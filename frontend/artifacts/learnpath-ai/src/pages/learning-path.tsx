import { useState, useEffect } from 'react';
import { Link } from 'wouter';
import { ArrowRight, Check, ChevronDown, Download } from 'lucide-react';
import { learningPathService, type LearningPath, type LearningPathPhase } from '@/services/index';
import { SkeletonCard, ErrorState, EmptyState } from '@/components/states';

function ProgressBar({ value, color = '#176b65' }: { value: number; color?: string }) {
  return <div className="h-2 overflow-hidden rounded-full bg-[#e3e9e1]"><div className="h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(value, 100)}%`, background: color }} /></div>;
}
function Tag({ children, warm = false }: { children: React.ReactNode; warm?: boolean }) {
  return <span className={`inline-flex rounded-lg px-2 py-1 text-[10px] font-bold ${warm ? 'bg-[#fae9bb] text-[#93611a]' : 'bg-[#e3eee7] text-[#176b65]'}`}>{children}</span>;
}

export default function LearningPath() {
  const [lp, setLp] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string>('');

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const data = await learningPathService.getLearningPath();
      setLp(data);
      const cur = data.phases?.find(p => p.status === 'current');
      if (cur) setExpanded(cur.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load your learning path.');
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <div className="space-y-3"><SkeletonCard /><SkeletonCard rows={2} /></div>;
  if (error) return <ErrorState title="Learning path unavailable" message={error} onRetry={load} />;
  if (!lp) return <EmptyState title="No learning path yet" description="Complete your onboarding to generate a personalized path." action={<Link href="/onboarding" className="rounded-xl bg-[#176b65] px-4 py-2 text-sm font-bold text-white">Start onboarding</Link>} />;

  return (
    <>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-5 animate-rise">
        <div>
          <p className="mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Your personalized route</p>
          <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">The path to {lp.goal}</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[#718079]">Your phases, skills, and milestones — all from your backend profile.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-xl border border-[#cbd5ce] bg-[#fbfaf5] px-4 py-2.5 text-sm font-bold text-[#27403b] hover:border-[#176b65]"><Download size={15} /> Export path</button>
      </div>

      <section className="mb-5 flex flex-wrap items-center justify-between gap-5 rounded-2xl border border-[#dbe4da] bg-[#e4eee6] p-6">
        <div className="flex items-center gap-4">
          <span className="grid size-12 place-items-center rounded-2xl bg-[#176b65] text-[#f7f5ed]"><ArrowRight size={22} /></span>
          <div><p className="text-xs font-bold uppercase tracking-wider text-[#718079]">Destination</p><p className="display text-2xl font-bold text-[#20322f]">{lp.goal}</p></div>
        </div>
        <div className="flex gap-8 text-right">
          {lp.duration && <div><p className="mono text-xl font-medium text-[#176b65]">{lp.duration}</p><p className="text-[10px] uppercase tracking-wider text-[#7c8b84]">estimated</p></div>}
          <div><p className="mono text-xl font-medium text-[#176b65]">{lp.total_progress ?? 0}%</p><p className="text-[10px] uppercase tracking-wider text-[#7c8b84]">complete</p></div>
        </div>
      </section>

      <div className="space-y-3">
        {lp.phases.map((phase: LearningPathPhase, i: number) => (
          <section key={phase.id} className={`overflow-hidden rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] shadow-sm ${phase.status === 'current' ? 'border-[#d9a43d]' : ''}`}>
            <button onClick={() => setExpanded(expanded === phase.id ? '' : phase.id)} className="flex w-full items-center gap-4 p-5 text-left md:p-6">
              <span className={`grid size-10 shrink-0 place-items-center rounded-xl text-sm font-bold ${phase.status === 'complete' ? 'bg-[#dceee4] text-[#176b65]' : phase.status === 'current' ? 'bg-[#fae9bb] text-[#a66c15]' : 'bg-[#edf0eb] text-[#8b9891]'}`}>
                {phase.status === 'complete' ? <Check size={18} /> : `0${i + 1}`}
              </span>
              <span className="min-w-0 flex-1">
                <span className="flex flex-wrap items-center gap-2">
                  <span className="display text-xl font-bold text-[#20322f]">{phase.title}</span>
                  {phase.status === 'current' && <Tag warm>Current phase</Tag>}
                </span>
                {phase.objective && <span className="mt-1 block text-sm text-[#718079]">{phase.objective}</span>}
              </span>
              <span className="hidden min-w-[120px] md:block">
                <ProgressBar value={phase.progress} color={phase.status === 'current' ? '#d89c2c' : '#176b65'} />
                <span className="mt-1 block text-right text-[10px] text-[#83918a]">{phase.progress}% complete</span>
              </span>
              <ChevronDown size={18} className={`text-[#86938c] transition-transform ${expanded === phase.id ? 'rotate-180' : ''}`} />
            </button>
            {expanded === phase.id && (
              <div className="border-t border-[#e4e9e2] bg-[#f6f7f1] px-5 pb-6 pt-5 md:px-20">
                <div className="grid gap-6 md:grid-cols-2">
                  {phase.skills && phase.skills.length > 0 && (
                    <div>
                      <p className="mono text-[10px] uppercase tracking-widest text-[#b17820]">Skills in this phase</p>
                      <div className="mt-3 flex flex-wrap gap-2">{phase.skills.map(s => <Tag key={s}>{s}</Tag>)}</div>
                    </div>
                  )}
                  {(phase.project || phase.assessment) && (
                    <div>
                      <p className="mono text-[10px] uppercase tracking-widest text-[#b17820]">Proof of progress</p>
                      {phase.project && <p className="mt-3 text-sm font-bold text-[#40534d]">{phase.project}</p>}
                      {phase.assessment && <p className="mt-1 text-xs text-[#83918a]">{phase.assessment} · {phase.estimated_time}</p>}
                    </div>
                  )}
                </div>
                <Link href="/resources" className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-[#176b65]">
                  {phase.status === 'current' ? 'Browse phase resources' : 'Preview this phase'} <ArrowRight size={15} />
                </Link>
              </div>
            )}
          </section>
        ))}
      </div>
    </>
  );
}
