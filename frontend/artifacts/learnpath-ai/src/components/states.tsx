import { AlertTriangle, RefreshCw, Inbox } from 'lucide-react';

// ─── Skeleton ─────────────────────────────────────────────────────────────────

export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-xl bg-[#e4e9e2] ${className}`}
      aria-hidden="true"
    />
  );
}

export function SkeletonCard({ rows = 3 }: { rows?: number }) {
  return (
    <div className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 space-y-4">
      <Skeleton className="h-5 w-2/5" />
      <Skeleton className="h-3 w-3/5" />
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full" />
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-[#dbe4da] bg-[#fbfaf5]">
      <div className="grid gap-px bg-[#dbe4da]">
        {Array.from({ length: rows + 1 }).map((_, ri) => (
          <div
            key={ri}
            className={`grid gap-4 bg-[#fbfaf5] px-5 py-3.5 ${ri === 0 ? 'bg-[#f0f3ed]' : ''}`}
            style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
          >
            {Array.from({ length: cols }).map((_, ci) => (
              <Skeleton key={ci} className={`h-3.5 ${ri === 0 ? 'w-3/4' : ci === 0 ? 'w-full' : 'w-4/5'}`} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Error state ──────────────────────────────────────────────────────────────

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Unable to load data',
  message = 'Something went wrong. Please try again.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-[#f5d5d0] bg-[#fdf5f4] p-12 text-center">
      <span className="grid size-14 place-items-center rounded-2xl bg-[#fbe9e5] text-[#a04b3e]">
        <AlertTriangle size={24} />
      </span>
      <h3 className="mt-5 text-lg font-bold text-[#1f312e]">{title}</h3>
      <p className="mt-2 max-w-sm text-sm leading-6 text-[#718079]">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-6 inline-flex items-center gap-2 rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-2.5 text-sm font-bold text-[#36504a] hover:border-[#176b65]"
        >
          <RefreshCw size={15} /> Try again
        </button>
      )}
    </div>
  );
}

// ─── Empty state ──────────────────────────────────────────────────────────────

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-12 text-center">
      <span className="grid size-14 place-items-center rounded-2xl bg-[#e3eee7] text-[#176b65]">
        <Inbox size={24} />
      </span>
      <h3 className="mt-5 text-lg font-bold text-[#1f312e]">{title}</h3>
      {description && (
        <p className="mt-2 max-w-sm text-sm leading-6 text-[#718079]">{description}</p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

// ─── Connection banner ────────────────────────────────────────────────────────

export function ConnectionBanner({ status }: { status: 'connected' | 'disconnected' | 'reconnecting' }) {
  if (status === 'connected') return null;

  return (
    <div
      className={`fixed bottom-4 left-1/2 z-50 -translate-x-1/2 rounded-full px-5 py-2.5 text-xs font-bold shadow-lg ${
        status === 'reconnecting'
          ? 'bg-[#fae9bb] text-[#93611a]'
          : 'bg-[#fbe9e5] text-[#a04b3e]'
      }`}
    >
      {status === 'reconnecting' ? '⟳ Reconnecting to server…' : '✕ Disconnected from server'}
    </div>
  );
}
