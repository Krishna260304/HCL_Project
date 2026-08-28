import { useState, useEffect } from 'react';
import { Link, useRoute } from 'wouter';
import { ChevronLeft, Zap, Check, Clock3, ShieldCheck, ArrowRight, BookOpen, Star } from 'lucide-react';
import { learningPathService, resourceService, type LearningPath, type LearningPathPhase, type Resource } from '@/services/index';
import { SkeletonCard, ErrorState, EmptyState } from '@/components/states';

function Tag({ children, warm = false }: { children: React.ReactNode; warm?: boolean }) {
  return (
    <span className={`inline-flex rounded-lg px-2 py-1 text-[10px] font-bold ${warm ? 'bg-[#fae9bb] text-[#93611a]' : 'bg-[#e3eee7] text-[#176b65]'}`}>
      {children}
    </span>
  );
}

export default function PhaseDetail() {
  const [, params] = useRoute('/learning-path/:phaseId');
  const phaseId = params?.phaseId;

  const [path, setPath] = useState<LearningPath | null>(null);
  const [phase, setPhase] = useState<LearningPathPhase | null>(null);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [lp, allRes] = await Promise.all([
        learningPathService.getLearningPath(),
        resourceService.listResources({ limit: 6 }).catch(() => []),
      ]);
      setPath(lp);
      const found = lp.phases?.find(p => p.id === phaseId) || lp.phases?.[0];
      setPhase(found || null);
      setResources(allRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load phase details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [phaseId]);

  if (loading) {
    return (
      <div className="space-y-5 animate-pulse">
        <SkeletonCard rows={2} />
        <div className="grid gap-5 lg:grid-cols-2">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (error) return <ErrorState title="Phase unavailable" message={error} onRetry={load} />;
  if (!phase) {
    return (
      <EmptyState
        title="Phase not found"
        description="We couldn't locate this learning phase."
        action={<Link href="/learning-path" className="rounded-xl bg-[#176b65] px-4 py-2 text-sm font-bold text-white">Back to path</Link>}
      />
    );
  }

  const milestones = [
    `Study core concepts: ${phase.skills?.slice(0, 2).join(', ') || 'Foundation skills'}`,
    `Build checkpoint project: ${phase.project || 'Phase practice project'}`,
    `Complete evaluation: ${phase.assessment || 'Phase checkpoint assessment'}`,
  ];

  return (
    <>
      <Link href="/learning-path" className="mb-7 inline-flex items-center gap-2 text-sm font-bold text-[#61716c] hover:text-[#176b65] transition" data-testid="link-back-path">
        <ChevronLeft size={16} /> Learning path
      </Link>

      <div className="mb-8 flex flex-wrap items-end justify-between gap-5 animate-rise">
        <div>
          <p className="font-mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">
            Phase Detail {phase.estimated_time ? `· ${phase.estimated_time}` : ''}
          </p>
          <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">{phase.title}</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[#718079]">{phase.objective || 'Focus on your active milestones and resources.'}</p>
        </div>
        <Tag warm={phase.status === 'current'}>{phase.progress}% complete</Tag>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.2fr_.8fr]">
        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 shadow-sm md:p-8">
          <div className="flex items-center gap-3">
            <span className="grid size-10 place-items-center rounded-xl bg-[#fae9bb] text-[#a66c15]">
              <Zap size={18} />
            </span>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-[#83918a]">Key milestones</p>
              <h2 className="display text-2xl font-bold">{phase.project || 'Phase action plan'}</h2>
            </div>
          </div>

          <p className="mt-6 max-w-2xl text-sm leading-7 text-[#61716c]">
            Work through each milestone below to lock in the required skills and demonstrate verified competency.
          </p>

          <div className="mt-7 space-y-3">
            {milestones.map((item, i) => {
              const isComplete = completedSteps.includes(i);
              return (
                <button
                  key={item}
                  onClick={() => {
                    setCompletedSteps(prev =>
                      prev.includes(i) ? prev.filter(x => x !== i) : [...prev, i]
                    );
                  }}
                  className="flex w-full items-center gap-3 rounded-xl border border-[#dbe4da] bg-[#f8f8f2] p-4 text-left transition-colors hover:bg-[#eaf1e8]"
                  data-testid={`button-milestone-${i}`}
                >
                  <span className={`grid size-7 place-items-center rounded-full transition ${isComplete ? 'bg-[#176b65] text-[#f7f5ed]' : 'border border-[#bfcfc2] text-[#9aa7a0]'}`}>
                    {isComplete ? <Check size={14} /> : i + 1}
                  </span>
                  <span className="text-sm font-bold text-[#40534d] flex-1">{item}</span>
                  <span className="text-xs font-semibold text-[#176b65]">{isComplete ? 'Done' : 'Mark done'}</span>
                </button>
              );
            })}
          </div>

          <div className="mt-7 flex items-center gap-3">
            <Link href="/resources" className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-sm font-bold text-white hover:bg-[#115a55] transition">
              <BookOpen size={16} /> Explore phase resources
            </Link>
            <Link href="/assistant" className="inline-flex items-center gap-2 rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-2.5 text-sm font-bold text-[#36504a] hover:border-[#176b65] transition">
              Ask AI coach <ArrowRight size={14} />
            </Link>
          </div>
        </section>

        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 shadow-sm">
          <p className="font-mono text-[10px] uppercase tracking-widest text-[#b17820]">Target Skills</p>
          <h2 className="display mt-3 text-2xl font-bold">Skills in this phase</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {phase.skills?.map(s => <Tag key={s}>{s}</Tag>) || <p className="text-xs text-[#83918a]">No specific skills tagged.</p>}
          </div>

          <div className="mt-7 border-t border-[#e4e9e2] pt-5">
            <p className="text-xs font-bold text-[#40534d]">Assessment checkpoint</p>
            <div className="mt-4 flex items-center gap-3">
              <span className="grid size-9 place-items-center rounded-xl bg-[#dceee4] text-[#176b65]">
                <ShieldCheck size={17} />
              </span>
              <div>
                <p className="text-sm font-bold">{phase.assessment || 'Checkpoint evaluation'}</p>
                <p className="text-xs text-[#83918a]">{phase.estimated_time || 'Adaptive timing'}</p>
              </div>
            </div>
            <Link href="/assessments" className="mt-4 inline-flex items-center gap-1.5 text-xs font-bold text-[#176b65]">
              Go to assessments <ArrowRight size={13} />
            </Link>
          </div>
        </section>
      </div>

      {resources.length > 0 && (
        <section className="mt-5 rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="display text-xl font-bold">Recommended resources</h2>
              <p className="mt-1 text-xs text-[#83918a]">Curated from your active learning profile</p>
            </div>
            <Link href="/resources" className="text-xs font-bold text-[#176b65]" data-testid="link-all-resources">
              Browse all resources
            </Link>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {resources.slice(0, 3).map(r => (
              <div key={r.id} className="rounded-xl border border-[#dbe4da] p-4 bg-white">
                <div className="flex items-start justify-between">
                  <Tag>{r.type || 'Resource'}</Tag>
                  {r.rating && (
                    <span className="flex items-center gap-1 text-xs text-[#d89c2c]">
                      <Star size={13} fill="currentColor" /> {r.rating}
                    </span>
                  )}
                </div>
                <p className="mt-4 text-sm font-bold leading-5 text-[#40534d]">{r.title}</p>
                <p className="mt-1 text-xs text-[#83918a]">{r.source || 'Curated'} {r.duration ? `· ${r.duration}` : ''}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </>
  );
}
