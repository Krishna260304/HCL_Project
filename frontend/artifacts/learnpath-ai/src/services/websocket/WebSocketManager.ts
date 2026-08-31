function uuidv4(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export type WSMessage = {
  action: string;
  request_id?: string;
  payload?: Record<string, unknown>;
};

export type WSResponse = {
  type: 'response';
  action: string;
  request_id?: string;
  success: boolean;
  data?: unknown;
};

export type WSError = {
  type: 'error';
  action: string;
  request_id?: string;
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
};

export type WSEvent = {
  type: 'event';
  event: string;
  data: unknown;
};

export type WSIncoming = WSResponse | WSError | WSEvent;

type PendingRequest = {
  resolve: (data: unknown) => void;
  reject: (err: Error) => void;
  timer: ReturnType<typeof setTimeout>;
};

type EventListener = (data: unknown) => void;
type ConnectionListener = (status: 'connected' | 'disconnected' | 'reconnecting') => void;

const DEFAULT_TIMEOUT_MS = 30_000;
const BASE_RECONNECT_MS = 1_000;
const MAX_RECONNECT_MS = 30_000;
const MAX_RECONNECT_ATTEMPTS = 10;
const MAX_QUEUED_REQUESTS = 100;

function getBackendWsUrl(token?: string | null): string {
  const secureProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const configuredUrl = import.meta.env.VITE_BACKEND_WS_URL?.trim();
  const configuredHost = import.meta.env.VITE_BACKEND_HOST?.trim();

  // Use the same host the browser is on, but point at the exposed backend port.
  // In the Compose setup the backend is published on 8086 and the frontend on 8084.
  let rawUrl = configuredUrl || configuredHost;
  if (!rawUrl && import.meta.env.DEV) {
    rawUrl = `${window.location.hostname}:8086`;
  }
  if (!rawUrl) {
    rawUrl = `${window.location.hostname}:8086`;
    console.warn('[WS] VITE_BACKEND_WS_URL is not configured; using the current host on port 8086.');
  }

  const hasProtocol = /^[a-z][a-z\d+.-]*:\/\//i.test(rawUrl);
  const url = new URL(hasProtocol ? rawUrl : `${secureProto}//${rawUrl}`, window.location.origin);
  if (url.protocol === 'http:') url.protocol = 'ws:';
  if (url.protocol === 'https:') url.protocol = 'wss:';
  if (url.protocol !== 'ws:' && url.protocol !== 'wss:') {
    throw new Error('VITE_BACKEND_WS_URL must use ws:// or wss://.');
  }

  const pathname = url.pathname.replace(/\/+$/, '');
  if (!pathname.endsWith('/ws')) url.pathname = `${pathname}/ws/`;
  else url.pathname = `${pathname}/`;
  if (token) url.searchParams.set('token', token);
  return url.toString();
}

class WebSocketManager {
  private ws: WebSocket | null = null;
  private pending = new Map<string, PendingRequest>();
  private eventListeners = new Map<string, Set<EventListener>>();
  private connectionListeners = new Set<ConnectionListener>();
  private token: string | null = null;
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private intentionallyClosed = false;
  private messageQueue: WSMessage[] = [];

  /** Open the connection. Call with a token to authenticate. */
  connect(token?: string | null): void {
    const nextToken = token ?? null;
    const tokenChanged = this.token !== nextToken;
    this.token = nextToken;
    this.intentionallyClosed = false;

    // If socket is already OPEN, authenticate over the active socket without tearing it down
    if (this.isConnected) {
      if (tokenChanged && nextToken) {
        this.authenticate(nextToken).catch((e) => {
          console.warn('[WS] In-line authentication failed, falling back to reconnect:', e);
          this._reconnectWithToken(nextToken);
        });
      }
      return;
    }

    try {
      this._openSocket();
    } catch (error) {
      this.ws = null;
      this._notifyConnectionListeners('disconnected');
      console.error('[WS] Could not open backend connection:', error);
    }
  }

  /** Explicitly authenticate the current open connection with a JWT token */
  async authenticate(token: string): Promise<boolean> {
    this.token = token;
    if (this.isConnected) {
      try {
        await this.request('auth.authenticate', { token }, 10_000);
        return true;
      } catch (err) {
        console.warn('[WS] auth.authenticate request failed:', err);
        return false;
      }
    }
    return false;
  }

  private _reconnectWithToken(token: string): void {
    if (this.ws) {
      const prev = this.ws;
      this.ws = null;
      prev.close(1000, 'Re-authenticating connection');
    }
    this.token = token;
    this._openSocket();
  }

  /** Disconnect and stop auto-reconnect. */
  disconnect(): void {
    this.intentionallyClosed = true;
    this._clearReconnect();
    this.ws?.close(1000, 'Client logout');
    this.ws = null;
    this.pending.forEach(({ reject, timer }) => {
      clearTimeout(timer);
      reject(new Error('WebSocket disconnected'));
    });
    this.pending.clear();
    this.messageQueue = [];
    this._notifyConnectionListeners('disconnected');
  }

  /** Update the token (e.g. after refresh) without reconnecting. */
  updateToken(token: string): void {
    this.token = token;
    if (this.isConnected) {
      this.authenticate(token).catch(() => {});
    }
  }

  /** True when the socket is OPEN. */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Send an action and wait for the matching response.
   * Rejects on timeout or backend error.
   */
  request<T = unknown>(
    action: string,
    payload: Record<string, unknown> = {},
    timeoutMs = DEFAULT_TIMEOUT_MS,
  ): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      const request_id = uuidv4();

      const timer = setTimeout(() => {
        this.pending.delete(request_id);
        this.messageQueue = this.messageQueue.filter((queued) => queued.request_id !== request_id);
        reject(new Error(`Request '${action}' timed out after ${timeoutMs}ms`));
      }, timeoutMs);

      this.pending.set(request_id, {
        resolve: (data) => resolve(data as T),
        reject,
        timer,
      });

      const msg: WSMessage = { action, request_id, payload };

      if (this.isConnected) {
        this._send(msg);
      } else {
        if (this.messageQueue.length >= MAX_QUEUED_REQUESTS) {
          clearTimeout(timer);
          this.pending.delete(request_id);
          reject(new Error('WebSocket request queue is full; please retry shortly.'));
          return;
        }
        // Queue the message; it will be flushed on connect.
        this.messageQueue.push(msg);
        if (this.ws === null && !this.intentionallyClosed) {
          try {
            this._openSocket();
          } catch (error) {
            clearTimeout(timer);
            this.pending.delete(request_id);
            this.messageQueue = this.messageQueue.filter((queued) => queued.request_id !== request_id);
            reject(error instanceof Error ? error : new Error('Could not open backend connection.'));
          }
        }
      }
    });
  }

  /** Subscribe to backend push events (type: "event"). */
  on(event: string, listener: EventListener): () => void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(listener);
    return () => this.eventListeners.get(event)?.delete(listener);
  }

  /** Subscribe to connection status changes. */
  onConnectionChange(listener: ConnectionListener): () => void {
    this.connectionListeners.add(listener);
    return () => this.connectionListeners.delete(listener);
  }

  // ─── private helpers ──────────────────────────────────────────────────────

  private _openSocket(): void {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) return;

    const url = getBackendWsUrl(this.token);
    const socket = new WebSocket(url);
    this.ws = socket;

    socket.onopen = () => {
      if (this.ws !== socket) return;
      this.reconnectAttempts = 0;
      this._notifyConnectionListeners('connected');
      this._flushQueue();
    };

    socket.onmessage = (evt) => {
      if (this.ws !== socket) return;
      let msg: WSIncoming;
      try {
        msg = JSON.parse(evt.data as string) as WSIncoming;
      } catch {
        console.warn('[WS] Could not parse message:', evt.data);
        return;
      }
      this._handleMessage(msg);
    };

    socket.onclose = (evt) => {
      // A superseded socket must not clear or reconnect over its replacement.
      if (this.ws !== socket) return;
      this.ws = null;
      if (!this.intentionallyClosed) {
        this._scheduleReconnect();
      } else {
        this._notifyConnectionListeners('disconnected');
      }
      // Reject all pending requests that will not be answered
      const message = evt.code === 1000
        ? 'WebSocket disconnected.'
        : 'Unable to reach the LearnPath backend. Check that the backend is running and reachable.';
      this.pending.forEach(({ reject, timer }) => {
        clearTimeout(timer);
        reject(new Error(message));
      });
      this.pending.clear();
      // Requests are rejected above, so never replay stale messages after a
      // reconnect. This prevents duplicate actions and unbounded queue growth.
      this.messageQueue = [];
    };

    socket.onerror = () => {
      // onerror is always followed by onclose, so let onclose handle reconnect.
    };
  }

  private _handleMessage(msg: WSIncoming): void {
    if (msg.type === 'event') {
      const listeners = this.eventListeners.get((msg as WSEvent).event);
      if (listeners) {
        listeners.forEach((fn) => fn((msg as WSEvent).data));
      }
      return;
    }

    const requestId = (msg as WSResponse | WSError).request_id;
    if (!requestId) return;

    const pending = this.pending.get(requestId);
    if (!pending) return;

    clearTimeout(pending.timer);
    this.pending.delete(requestId);

    if (msg.type === 'error') {
      const err = (msg as WSError).error;
      const error = new Error(err.message);
      (error as Error & { code?: string; details?: unknown }).code = err.code;
      (error as Error & { details?: unknown }).details = err.details;
      pending.reject(error);
    } else {
      pending.resolve((msg as WSResponse).data);
    }
  }

  private _send(msg: WSMessage): void {
    try {
      this.ws!.send(JSON.stringify(msg));
    } catch (e) {
      console.error('[WS] Send failed:', e);
    }
  }

  private _flushQueue(): void {
    while (this.messageQueue.length > 0) {
      const msg = this.messageQueue.shift()!;
      this._send(msg);
    }
  }

  private _scheduleReconnect(): void {
    if (this.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      this._notifyConnectionListeners('disconnected');
      return;
    }

    this._notifyConnectionListeners('reconnecting');
    const delay = Math.min(BASE_RECONNECT_MS * 2 ** this.reconnectAttempts, MAX_RECONNECT_MS);
    this.reconnectAttempts += 1;

    this.reconnectTimer = setTimeout(() => {
      if (!this.intentionallyClosed) this._openSocket();
    }, delay);
  }

  private _clearReconnect(): void {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private _notifyConnectionListeners(status: 'connected' | 'disconnected' | 'reconnecting'): void {
    this.connectionListeners.forEach((fn) => fn(status));
  }
}

// Singleton instance used throughout the app
export const wsManager = new WebSocketManager();
