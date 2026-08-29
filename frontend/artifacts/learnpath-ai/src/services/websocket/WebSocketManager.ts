import { fallbackProvider } from '../fallbackProvider';

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
  action: string;
  payload: Record<string, unknown>;
};

type EventListener = (data: unknown) => void;
type ConnectionListener = (status: 'connected' | 'disconnected' | 'reconnecting') => void;

const DEFAULT_TIMEOUT_MS = 15_000;
const FALLBACK_CONNECT_GRACE_MS = 1_500;
const BASE_RECONNECT_MS = 1_000;
const MAX_RECONNECT_MS = 30_000;
const MAX_RECONNECT_ATTEMPTS = 5;

function getBackendWsUrl(token?: string | null): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const host = import.meta.env.VITE_BACKEND_HOST ?? 'localhost:8000';
  const path = '/ws/';
  const base = `${proto}://${host}${path}`;
  return token ? `${base}?token=${encodeURIComponent(token)}` : base;
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
  private currentStatus: 'connected' | 'disconnected' | 'reconnecting' = 'disconnected';

  /** Open the connection. Call with a token to authenticate. */
  connect(token?: string | null): void {
    this.token = token ?? null;
    this.intentionallyClosed = false;
    this._openSocket();
  }

  /** Disconnect and stop auto-reconnect. */
  disconnect(): void {
    this.intentionallyClosed = true;
    this._clearReconnect();
    this.ws?.close(1000, 'Client logout');
    this.ws = null;
    this.pending.forEach(({ resolve, timer, action, payload }) => {
      clearTimeout(timer);
      try {
        const fallback = fallbackProvider.handleAction(action, payload);
        resolve(fallback);
      } catch (err) {
        // Safe fallback
      }
    });
    this.pending.clear();
    this._notifyConnectionListeners('disconnected');
  }

  /** Update the token (e.g. after refresh) without reconnecting. */
  updateToken(token: string): void {
    this.token = token;
  }

  /** True when the socket is OPEN. */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /** Get the current connection status. */
  get status(): 'connected' | 'disconnected' | 'reconnecting' {
    return this.currentStatus;
  }

  /**
   * Send an action and wait for the matching response.
   * If the WebSocket is unavailable or times out, gracefully returns high-fidelity fallback data.
   */
  request<T = unknown>(
    action: string,
    payload: Record<string, unknown> = {},
    timeoutMs = DEFAULT_TIMEOUT_MS,
  ): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      // If WebSocket is already connected, send over socket
      if (this.isConnected) {
        const request_id = uuidv4();
        const timer = setTimeout(() => {
          this.pending.delete(request_id);
          console.warn(`[WS] Request '${action}' timed out. Falling back to localized provider.`);
          try {
            const fallback = fallbackProvider.handleAction(action, payload) as T;
            resolve(fallback);
          } catch (e) {
            reject(new Error(`Request '${action}' timed out after ${timeoutMs}ms`));
          }
        }, timeoutMs);

        this.pending.set(request_id, {
          resolve: (data) => resolve(data as T),
          reject: (err) => {
            console.warn(`[WS] Request '${action}' failed (${err.message}). Using fallback.`);
            try {
              const fallback = fallbackProvider.handleAction(action, payload) as T;
              resolve(fallback);
            } catch {
              reject(err);
            }
          },
          timer,
          action,
          payload,
        });

        this._send({ action, request_id, payload });
        return;
      }

      // If disconnected, try opening socket in background, but immediately provide fallback if not connected quickly
      if (this.ws === null && !this.intentionallyClosed) {
        this._openSocket();
      }

      // Allow a brief grace period to connect; if not connected, resolve via fallback
      const graceTimer = setTimeout(() => {
        if (!this.isConnected) {
          try {
            const fallback = fallbackProvider.handleAction(action, payload) as T;
            resolve(fallback);
          } catch (err) {
            reject(err instanceof Error ? err : new Error('Fallback failed'));
          }
        } else {
          // If connected within grace period, dispatch request
          this.request<T>(action, payload, timeoutMs).then(resolve).catch(reject);
        }
      }, FALLBACK_CONNECT_GRACE_MS);

      // If connected before graceTimer finishes, onopen handles queue
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
    // Immediately inform the listener of current state
    listener(this.currentStatus);
    return () => this.connectionListeners.delete(listener);
  }

  // ─── private helpers ──────────────────────────────────────────────────────

  private _openSocket(): void {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) return;

    try {
      const url = getBackendWsUrl(this.token);
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this._notifyConnectionListeners('connected');
        this._flushQueue();
      };

      this.ws.onmessage = (evt) => {
        let msg: WSIncoming;
        try {
          msg = JSON.parse(evt.data as string) as WSIncoming;
        } catch {
          console.warn('[WS] Could not parse message:', evt.data);
          return;
        }
        this._handleMessage(msg);
      };

      this.ws.onclose = (evt) => {
        this.ws = null;
        if (!this.intentionallyClosed) {
          this._scheduleReconnect();
        } else {
          this._notifyConnectionListeners('disconnected');
        }
        // Fulfill pending requests with fallback instead of hard failing
        this.pending.forEach(({ resolve, timer, action, payload }) => {
          clearTimeout(timer);
          try {
            const fallback = fallbackProvider.handleAction(action, payload);
            resolve(fallback);
          } catch {
            // Ignored
          }
        });
        this.pending.clear();
      };

      this.ws.onerror = () => {
        // Handled in onclose
      };
    } catch (e) {
      this.ws = null;
      this._notifyConnectionListeners('disconnected');
    }
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
    this.currentStatus = status;
    this.connectionListeners.forEach((fn) => fn(status));
  }
}

// Singleton instance used throughout the app
export const wsManager = new WebSocketManager();
