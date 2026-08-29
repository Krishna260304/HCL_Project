import { useState, useEffect } from 'react';
import { Link } from 'wouter';
import {
  ArrowRight,
  Check,
  Clock3,
  Sparkles,
  BriefcaseBusiness,
  ShieldCheck,
  CheckCircle2,
  FolderGit2,
  Play,
  Layers,
  Code2,
} from 'lucide-react';
import { projectService, type Project } from '@/services/index';
import { SkeletonCard, ErrorState, EmptyState } from '@/components/states';
import { useToast } from '@/hooks/use-toast';

function Tag({
  children,
  variant = 'teal',
}: {
  children: React.ReactNode;
  variant?: 'teal' | 'gold' | 'amber' | 'emerald' | 'subtle';
}) {
  const styles = {
    teal: 'bg-[#e3eee7] text-[#176b65] border border-[#cbe0d3]',
    gold: 'bg-[#fae9bb] text-[#93611a] border border-[#edd597]',
    amber: 'bg-[#fef3c7] text-[#b45309] border border-[#fde68a]',
    emerald: 'bg-[#294b44] text-[#deebe0] border border-[#3b635a]',
    subtle: 'bg-[#eef2ea] text-[#61716c] border border-[#dce4da]',
  };
  return (
    <span className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-bold ${styles[variant]}`}>
      {children}
    </span>
  );
}

export default function Projects() {
  const { toast } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'all' | 'current' | 'completed'>('all');
  const [completedIds, setCompletedIds] = useState<string[]>(['proj_01', 'proj_02']);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await projectService.listProjects({});
      setProjects(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load projects.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggleComplete = (id: string, title: string) => {
    const isDone = completedIds.includes(id);
    const updated = isDone ? completedIds.filter((x) => x !== id) : [...completedIds, id];
    setCompletedIds(updated);
    toast({
      title: isDone ? 'Project Status Reverted' : 'Project Shipped! 🚀',
      description: `"${title}" has been ${isDone ? 'marked in progress' : 'verified and added to your portfolio'}.`,
    });
  };

  const filtered = projects.filter((p) => {
    const isDone = completedIds.includes(p.id) || p.status === 'completed';
    if (tab === 'completed') return isDone;
    if (tab === 'current') return !isDone;
    return true;
  });

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <SkeletonCard rows={2} />
        <div className="grid gap-6 lg:grid-cols-2">
          <SkeletonCard rows={3} />
          <SkeletonCard rows={3} />
        </div>
      </div>
    );
  }

  if (error) return <ErrorState title="Projects unavailable" message={error} onRetry={load} />;

  return (
    <div className="space-y-8 animate-rise">
      {/* ─── Top Header & Value Proposition ──────────────────────────────────────── */}
      <div className="flex flex-wrap items-end justify-between gap-5 border-b border-[#dbe4da] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] font-bold uppercase tracking-[.2em] text-[#b17820]">
              Applied Portfolio Checkpoints
            </span>
            <span className="text-[#c5cdc5]">/</span>
            <span className="inline-flex items-center gap-1 text-xs font-bold text-[#176b65]">
              <FolderGit2 size={13} /> Verifiable Proof of Competence
            </span>
          </div>

          <h1 className="display mt-2 text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">
            Project Studio
          </h1>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-[#718079]">
            Hands-on checkpoint projects turning conceptual learning into tangible portfolio evidence with automated diagnostic verification.
          </p>
        </div>

        <Link
          href="/learning-path"
          className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-xs font-bold text-[#f7f5ed] shadow-sm hover:bg-[#115a55] transition"
        >
          View Connected Roadmap <ArrowRight size={14} />
        </Link>
      </div>

      {/* ─── Filter Tabs ───────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#e3e8e0] pb-4">
        <div className="flex gap-1.5 rounded-xl bg-[#e6ebe4] p-1">
          {[
            { id: 'all', label: `All Checkpoints (${projects.length})` },
            { id: 'current', label: `In Progress (${projects.length - completedIds.length})` },
            { id: 'completed', label: `Shipped (${completedIds.length})` },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id as typeof tab)}
              className={`rounded-lg px-4 py-2 text-xs font-bold transition ${
                tab === t.id ? 'bg-[#fbfaf5] text-[#20322f] shadow-sm' : 'text-[#7b8882] hover:text-[#20322f]'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <span className="text-xs text-[#718079] font-mono">
          Demonstrated mastery unlocks subsequent architecture phases
        </span>
      </div>

      {/* ─── Projects Grid ─────────────────────────────────────────────────────── */}
      {filtered.length === 0 ? (
        <EmptyState
          title={tab === 'completed' ? 'No completed projects yet' : 'No active projects'}
          description="Complete current phase assignments to unlock new portfolio checkpoints."
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {filtered.map((p) => {
            const isCompleted = completedIds.includes(p.id) || p.status === 'completed';

            return (
              <section
                key={p.id}
                className={`rounded-2xl border bg-[#fbfaf5] p-6 shadow-sm flex flex-col justify-between transition-all duration-200 ${
                  isCompleted ? 'border-[#dbe4da] opacity-95' : 'border-[#176b65] ring-1 ring-[#176b65]/20'
                }`}
              >
                <div>
                  {/* Top Badges */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <Tag variant={isCompleted ? 'teal' : 'amber'}>
                        {isCompleted ? '✓ Shipped & Verified' : '● Active Checkpoint'}
                      </Tag>
                      <span className="font-mono text-[10px] font-bold uppercase text-[#88958e] bg-[#eef2ea] px-2 py-0.5 rounded-md">
                        Phase {p.phase_order || 3}
                      </span>
                    </div>

                    {p.estimated_time && (
                      <span className="flex items-center gap-1.5 text-xs text-[#83918a] font-mono">
                        <Clock3 size={13} /> {p.estimated_time}
                      </span>
                    )}
                  </div>

                  {/* Title & Description */}
                  <h2 className="display mt-4 text-2xl font-bold leading-snug text-[#20322f]">{p.title}</h2>

                  {/* AI "Why This Project" Reasoning */}
                  {p.reason && (
                    <div className="mt-4 rounded-xl bg-[#eef2ea] p-3.5 border border-[#dce4da] text-xs leading-relaxed text-[#51635e]">
                      <div className="flex items-center gap-1.5 font-bold text-[#176b65] mb-1">
                        <Sparkles size={12} className="text-[#d89c2c]" /> AI Architecture Rationale:
                      </div>
                      {p.reason}
                    </div>
                  )}

                  {p.description && !p.reason && (
                    <p className="mt-3 text-xs leading-relaxed text-[#718079]">{p.description}</p>
                  )}

                  {/* Skills Targeted */}
                  {p.skills && p.skills.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-1.5">
                      {p.skills.map((s) => (
                        <span key={s} className="rounded-md bg-[#e3eee7] px-2 py-0.5 text-[10px] font-bold text-[#176b65]">
                          #{s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Bottom Actions */}
                <div className="mt-6 pt-5 border-t border-[#e4e9e2] flex items-center justify-between gap-4">
                  <span className="text-xs text-[#718079] flex items-center gap-1.5 font-mono">
                    <Code2 size={14} className="text-[#176b65]" /> Checkpoint Deliverable
                  </span>

                  <div className="flex items-center gap-2.5">
                    <button
                      onClick={() => toggleComplete(p.id, p.title)}
                      className={`inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-xs font-bold transition shadow-sm ${
                        isCompleted
                          ? 'bg-[#e3eee7] text-[#176b65] border border-[#bcdcc8]'
                          : 'bg-[#176b65] text-white hover:bg-[#115a55]'
                      }`}
                    >
                      {isCompleted ? (
                        <>
                          <CheckCircle2 size={14} /> Shipped
                        </>
                      ) : (
                        <>
                          <Play size={13} fill="currentColor" /> Submit / Verify Checkpoint
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}
