import { useState, useEffect } from 'react';
import { TrendingUp, Lightbulb, Flame, Bell, Check, Sparkles } from 'lucide-react';
import { notificationService, type Notification } from '@/services/index';
import { SkeletonCard, ErrorState, EmptyState } from '@/components/states';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await notificationService.listNotifications({});
      setNotifications(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load notifications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const unsub = notificationService.onNew((notif) => {
      setNotifications(prev => [notif, ...prev]);
    });
    return unsub;
  }, []);

  const handleMarkRead = async (id: string) => {
    try {
      await notificationService.markRead(id);
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      );
    } catch {}
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllRead();
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch {}
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map(i => (
          <SkeletonCard key={i} rows={1} />
        ))}
      </div>
    );
  }

  if (error) {
    return <ErrorState title="Notifications unavailable" message={error} onRetry={load} />;
  }

  return (
    <>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-5 animate-rise">
        <div>
          <p className="font-mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Real-time system feed</p>
          <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Notifications</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[#718079]">Adaptive updates and reminders from your path engine.</p>
        </div>
        {notifications.some(n => !n.read) && (
          <button
            onClick={handleMarkAllRead}
            className="inline-flex items-center gap-1.5 rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-2 text-xs font-bold text-[#36504a] hover:border-[#176b65] transition"
          >
            <Check size={14} /> Mark all read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <EmptyState
          title="No notifications yet"
          description="You are all caught up! New checkpoint reminders and recommendations will appear here."
        />
      ) : (
        <div className="space-y-3">
          {notifications.map(n => (
            <section
              key={n.id}
              className={`flex gap-4 rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm transition-opacity ${
                n.read ? 'opacity-65' : ''
              }`}
            >
              <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-[#e3eee7] text-[#176b65]">
                {n.type === 'achievement' ? <Flame size={18} /> : n.type === 'recommendation' ? <Lightbulb size={18} /> : <Sparkles size={18} />}
              </span>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-bold text-[#20322f]">{n.title}</p>
                  {!n.read && (
                    <button
                      onClick={() => handleMarkRead(n.id)}
                      className="size-2 shrink-0 rounded-full bg-[#d89c2c]"
                      title="Mark as read"
                    />
                  )}
                </div>
                {n.body && <p className="mt-1 text-sm leading-6 text-[#718079]">{n.body}</p>}
                {n.created_at && (
                  <p className="font-mono mt-3 text-[10px] text-[#9aa7a0]">
                    {new Date(n.created_at).toLocaleString()}
                  </p>
                )}
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  );
}
