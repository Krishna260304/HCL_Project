import { useState, useEffect } from 'react';
import { Clock3, TrendingUp, BriefcaseBusiness, Check, Download, Flame } from 'lucide-react';
import { progressService, type ProgressData, type Skill } from '@/services/index';
import { SkeletonCard, ErrorState } from '@/components/states';

function Metric({ label, value, delta, icon }: { label: string; value: string | number; delta?: string; icon: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
      <span className="text-[#176b65] [&>svg]:size-5">{icon}</span>
      <p className="font-mono mt-5 text-3xl text-[#20322f]">{value}</p>
      <p className="mt-1 text-sm font-bold text-[#40534d]">{label}</p>
      {delta && <p className="mt-2 text-xs text-[#176b65] font-semibold">{delta}</p>}
    </section>
  );
}

export default function ProgressPage() {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [prog, sk, activity] = await Promise.all([
        progressService.getProgress().catch(() => null),
        progressService.getSkillProgress().catch(() => []),
        progressService.getActivity().catch(() => []),
      ]);
      setProgress(prog ? { ...prog, activity } : null);
      setSkills(sk);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load your progress analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div className="space-y-5">
        <div className="grid gap-5 md:grid-cols-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
        <SkeletonCard rows={3} />
      </div>
    );
  }

  if (error) {
    return <ErrorState title="Progress insights unavailable" message={error} onRetry={load} />;
  }

  const hours = progress?.total_hours ?? 0;
  const streak = progress?.learning_streak ?? 0;
  const overall = progress?.overall_progress ?? 0;
  const activities = progress?.activity || [];

  return (
    <>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-5 animate-rise">
        <div>
          <p className="font-mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Your learning signal</p>
          <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Progress with context</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[#718079]">Live metrics from your backend activity, hours studied, and checkpoint completions.</p>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-3">
        <Metric label="Total learning hours" value={hours.toFixed(1)} delta={`${hours > 0 ? 'Active learning track' : 'Ready to start'}`} icon={<Clock3 />} />
        <Metric label="Learning streak" value={`${streak} days`} delta={streak > 0 ? 'Consistent momentum' : 'Start today'} icon={<Flame />} />
        <Metric label="Path progress" value={`${overall}%`} delta="Verified milestone completions" icon={<TrendingUp />} />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 shadow-sm">
          <h2 className="display text-xl font-bold">Recent activity</h2>
          <p className="mt-1 text-xs text-[#83918a]">Events captured across your learning session</p>

          <div className="mt-5 space-y-4">
            {activities.length > 0 ? (
              activities.map((act, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="grid size-7 place-items-center rounded-full bg-[#dceee4] text-[#176b65]">
                    <Check size={14} />
                  </span>
                  <span className="flex-1 text-sm font-bold text-[#40534d]">{act.action || act.item_id || 'Study Session'}</span>
                  <span className="text-xs text-[#83918a] font-mono">{act.timestamp ? new Date(act.timestamp).toLocaleDateString() : 'Recent'}</span>
                </div>
              ))
            ) : (
              <div className="py-8 text-center text-xs text-[#83918a]">
                No recorded activity yet. Complete a lesson, project, or checkpoint to populate your timeline.
              </div>
            )}
          </div>
        </section>

        <section className="rounded-2xl border border-[#dbe4da] bg-[#203d38] p-6 text-[#f8f5eb] shadow-sm flex flex-col justify-between">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-widest text-[#edbc55]">Adaptive Learning Feedback</p>
            <h3 className="display mt-4 text-2xl font-bold leading-tight">
              “Consistent small sessions beat intense sprints.”
            </h3>
            <p className="mt-4 text-sm leading-6 text-[#bcd0c2]">
              Your personalized curriculum automatically reprioritizes concepts when you complete projects and submit checkpoint assessments.
            </p>
          </div>

          <div className="mt-6 rounded-xl bg-[#294b44] p-4 text-xs text-[#deebe0] border border-[#47675e]">
            <span className="font-bold text-[#edbc55]">Status:</span> Live synchronized with backend learning analytics.
          </div>
        </section>
      </div>
    </>
  );
}
