import { useState, useEffect } from 'react';
import { Link } from 'wouter';
import { ArrowRight, Check, Clock3, Flame, Play, Target } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import {
  progressService,
  learningPathService,
  skillService,
  type ProgressData,
  type LearningPath,
  type Skill,
} from '@/services/index';
import { SkeletonCard, ErrorState } from '@/components/states';

function ProgressBar({ value, color = '#176b65' }: { value: number; color?: string }) {
  return (
    <div className="h-2 overflow-hidden rounded-full bg-[#e3e9e1]">
      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(value, 100)}%`, background: color }} />
    </div>
  );
}
function Tag({ children, warm = false }: { children: React.ReactNode; warm?: boolean }) {
  return <span className={`inline-flex rounded-lg px-2 py-1 text-[10px] font-bold ${warm ? 'bg-[#fae9bb] text-[#93611a]' : 'bg-[#e3eee7] text-[#176b65]'}`}>{children}</span>;
}
function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] shadow-sm ${className}`}>{children}</section>;
}

export default function Dashboard() {
  const { user } = useAuth();
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [path, setPath] = useState<LearningPath | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [todayDone, setTodayDone] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, lp, sk] = await Promise.all([
        progressService.getProgress().catch(() => null),
        learningPathService.getLearningPath().catch(() => null),
        skillService.listSkills({ limit: 3 }).catch(() => []),
      ]);
      // The gateway can legitimately return an empty/null payload while a
      // learner is being provisioned. Keep the dashboard renderable in that
      // state instead of allowing an unchecked response to crash the route.
      setProgress(p && typeof p === 'object' ? p : null);
      setPath(lp && typeof lp === 'object' ? lp : null);
      setSkills(Array.isArray(sk) ? sk : []);
    } catch {
      setError('Unable to load your dashboard. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="space-y-5 animate-pulse">
        <SkeletonCard rows={2} />
        <div className="grid gap-5 lg:grid-cols-2"><SkeletonCard /><SkeletonCard /></div>
      </div>
    );
  }
  if (error) return <ErrorState title="Dashboard unavailable" message={error} onRetry={load} />;

  const displayName = user?.email?.split('@')[0] ?? 'there';
  const phases = Array.isArray(path?.phases) ? path.phases : [];
  const currentPhase = phases.find(p => p.status === 'current');
  const overallProgress = Number(path?.total_progress ?? progress?.overall_progress ?? 0) || 0;
  const streak = Number(progress?.learning_streak ?? 0) || 0;
  const totalHours = Number(progress?.total_hours ?? 0) || 0;
  const prioritySkills = skills.filter(s => s.gap && s.gap > 0).slice(0, 3);

  return (
    <>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-5 animate-rise">
        <div>
          <p className="mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
          <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Good {new Date().getHours() < 12 ? 'morning' : 'afternoon'}, {displayName}.</h1>
          {currentPhase && <p className="mt-3 max-w-2xl text-sm leading-6 text-[#718079]">You're in the <strong>{currentPhase.title}</strong> phase. Keep the thread going.</p>}
        </div>
        <Link href="/learning-path" className="inline-flex items-center gap-2 text-sm font-bold text-[#176b65]">View full roadmap <ArrowRight size={15} /></Link>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.35fr_.65fr]">
        <Card className="!bg-[#203d38] overflow-hidden text-[#f8f5eb]">
          <div className="flex flex-col justify-between gap-8 p-6 md:flex-row md:p-8">
            <div>
              <div className="flex items-center gap-2">
                <span className="size-2 rounded-full bg-[#edbc55]" />
                <p className="mono text-[10px] uppercase tracking-[.18em] text-[#b9d1c1]">
                  {currentPhase ? `Today's focus · ${currentPhase.title}` : 'Your learning path'}
                </p>
              </div>
              <h2 className="display mt-5 max-w-xl text-3xl font-bold tracking-[-.04em] md:text-4xl">
                {currentPhase?.objective ?? 'Continue your learning journey'}
              </h2>
              <div className="mt-7 flex flex-wrap items-center gap-3">
                <button onClick={() => setTodayDone(!todayDone)} className="inline-flex items-center gap-2 rounded-xl bg-[#edbc55] px-4 py-2.5 text-sm font-bold text-[#20322f] hover:bg-[#e7a93b]">
                  {todayDone ? <><Check size={16} /> Completed for today</> : <><Play size={15} fill="currentColor" /> Start today's session</>}
                </button>
                <span className="flex items-center gap-1.5 text-xs text-[#b9d1c1]"><Clock3 size={14} /> {currentPhase?.estimated_time ?? 'At your own pace'}</span>
              </div>
            </div>
            <div className="grid shrink-0 size-28 place-items-center self-start rounded-full border-[10px] border-[#39645b] md:size-36"
              style={{ background: `conic-gradient(#edbc55 ${overallProgress}%, transparent 0)` }}>
              <div className="grid size-[78px] place-items-center rounded-full bg-[#203d38] md:size-[100px]">
                <span className="display text-2xl font-bold">{overallProgress}<small className="text-sm">%</small></span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="mono text-[10px] uppercase tracking-[.18em] text-[#82918a]">Path momentum</p>
              <p className="mt-2 display text-3xl font-bold text-[#20322f]">{overallProgress}%</p>
            </div>
            <span className="grid size-10 place-items-center rounded-xl bg-[#fae9bb] text-[#a66c15]"><Flame size={19} /></span>
          </div>
          <ProgressBar value={overallProgress} color="#d89c2c" />
          <div className="mt-4 flex justify-between text-xs text-[#718079]">
            <span>{streak} day streak</span>
            <span>{totalHours.toFixed(1)} total hours</span>
          </div>
          {path?.goal && (
            <div className="mt-6 rounded-xl bg-[#eef2ea] p-3 text-xs leading-5 text-[#61716c]">
              <span className="font-bold text-[#20322f]">Goal:</span> {path.goal}
            </div>
          )}
        </Card>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1.05fr_.95fr]">
        {path && (
          <Card>
            <div className="flex items-center justify-between border-b border-[#e4e9e2] px-6 py-5">
              <div><h2 className="display text-xl font-bold">Your route</h2><p className="mt-1 text-xs text-[#7b8882]">{currentPhase ? `${currentPhase.title} is in motion` : 'Your path'}</p></div>
              <Link href="/learning-path" className="text-xs font-bold text-[#176b65]">Details</Link>
            </div>
            <div className="p-6">
              {phases.slice(0, 4).map((phase, i) => (
                <div key={phase.id} className="relative flex gap-4 pb-6 last:pb-0">
                  <div className="relative flex flex-col items-center">
                    <span className={`z-10 grid size-8 place-items-center rounded-full ${phase.status === 'complete' ? 'bg-[#176b65] text-[#f7f5ed]' : phase.status === 'current' ? 'border-2 border-[#edbc55] bg-[#fae9bb] text-[#a66c15]' : 'border border-[#ccd8ce] bg-[#f2f4ed] text-[#9aa7a0]'}`}>
                      {phase.status === 'complete' ? <Check size={15} /> : <span className="text-xs font-bold">{i + 1}</span>}
                    </span>
                    {i !== phases.length - 1 && <span className="absolute top-8 h-full w-px bg-[#dbe4da]" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-3">
                      <div><p className={`text-sm font-bold ${phase.status === 'current' ? 'text-[#176b65]' : 'text-[#40534d]'}`}>{phase.title}</p><p className="mt-1 text-xs text-[#83918a]">{phase.estimated_time ?? ''}</p></div>
                      <span className="mono text-xs text-[#88958e]">{phase.progress}%</span>
                    </div>
                    <ProgressBar value={phase.progress} color={phase.status === 'current' ? '#d89c2c' : '#176b65'} />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {prioritySkills.length > 0 && (
          <Card>
            <div className="border-b border-[#e4e9e2] px-6 py-5">
              <h2 className="display text-xl font-bold">Skill signal</h2>
              <p className="mt-1 text-xs text-[#7b8882]">Where your next hour pays off</p>
            </div>
            <div className="space-y-5 p-6">
              {prioritySkills.map(s => (
                <div key={s.id ?? s.name}>
                  <div className="mb-2 flex items-center justify-between text-xs">
                    <span className="font-bold text-[#40534d]">{s.name}</span>
                    <Tag warm={(s.gap ?? 0) > 0}>{(s.gap ?? 0) > 0 ? 'Focus next' : 'On track'}</Tag>
                  </div>
                  <div className="relative">
                    <ProgressBar value={s.self_score ?? s.verified_score ?? 0} color={(s.gap ?? 0) > 0 ? '#d89c2c' : '#176b65'} />
                    {s.required_score && <span className="absolute -top-1 size-4 rounded-full border-2 border-[#fbfaf5] bg-[#203d38]" style={{ left: `calc(${s.required_score}% - 8px)` }} />}
                  </div>
                  <div className="mt-1 flex justify-between text-[10px] text-[#94a099]">
                    <span>Current {s.self_score ?? 0}</span>
                    <span>Role-ready {s.required_score ?? 0}</span>
                  </div>
                </div>
              ))}
            </div>
            <Link href="/skills" className="mx-6 mb-6 flex items-center justify-center gap-2 rounded-xl border border-[#ccd8ce] py-2.5 text-xs font-bold text-[#36504a]">See skill intelligence <ArrowRight size={14} /></Link>
          </Card>
        )}

        {!path && !loading && (
          <Card className="p-8 text-center">
            <Target size={32} className="mx-auto text-[#176b65]" />
            <h3 className="mt-4 text-lg font-bold">No learning path yet</h3>
            <p className="mt-2 text-sm text-[#718079]">Complete your onboarding to generate a personalized learning path.</p>
            <Link href="/onboarding" className="mt-4 inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-sm font-bold text-white">Get started <ArrowRight size={14} /></Link>
          </Card>
        )}
      </div>
    </>
  );
}
