import { AlertTriangle, RefreshCw, Inbox, Loader2 } from 'lucide-react';

// ─── Skeleton Loader ──────────────────────────────────────────────────────────

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
    <div className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 space-y-4 shadow-sm" aria-busy="true">
      <Skeleton className="h-5 w-2/5" />
      <Skeleton className="h-3.5 w-3/5" />
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full" />
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] shadow-sm" aria-busy="true">
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
  message = 'Something went wrong while synchronizing with the server. Please try again.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-[#f5d5d0] bg-[#fdf5f4] p-10 md:p-14 text-center shadow-sm" role="alert">
      <span className="grid size-14 place-items-center rounded-2xl bg-[#fbe9e5] text-[#a04b3e] shadow-sm">
        <AlertTriangle size={24} />
      </span>
      <h3 className="mt-5 display text-xl font-bold text-[#1f312e]">{title}</h3>
      <p className="mt-2 max-w-md text-xs md:text-sm leading-relaxed text-[#718079]">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-5 py-2.5 text-xs font-bold text-white hover:bg-[#115a55] transition shadow-sm"
        >
          <RefreshCw size={14} /> Retry Request
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
    <div className="flex flex-col items-center justify-center rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-10 md:p-14 text-center shadow-sm">
      <span className="grid size-14 place-items-center rounded-2xl bg-[#e3eee7] text-[#176b65] shadow-sm">
        <Inbox size={24} />
      </span>
      <h3 className="mt-5 display text-xl font-bold text-[#1f312e]">{title}</h3>
      {description && (
        <p className="mt-2 max-w-md text-xs md:text-sm leading-relaxed text-[#718079]">{description}</p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
