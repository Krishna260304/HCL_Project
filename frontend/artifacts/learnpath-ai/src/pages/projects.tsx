import { useState, useEffect } from 'react';
import { ArrowRight, Check, Clock3, MoreHorizontal, Plus } from 'lucide-react';
import { projectService, type Project } from '@/services/index';
import { SkeletonCard, ErrorState, EmptyState } from '@/components/states';

function Tag({ children, warm = false }: { children: React.ReactNode; warm?: boolean }) {
  return <span className={`inline-flex rounded-lg px-2 py-1 text-[10px] font-bold ${warm ? 'bg-[#fae9bb] text-[#93611a]' : 'bg-[#e3eee7] text-[#176b65]'}`}>{children}</span>;
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'all' | 'current' | 'completed'>('all');

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const data = await projectService.listProjects({});
      setProjects(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load projects.');
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const filtered = tab === 'all' ? projects : projects.filter(p =>
    tab === 'current' ? p.status === 'current' || p.status === 'in_progress' :
    p.status === 'completed'
  );

  if (loading) return <div className="space-y-4"><SkeletonCard rows={2} /><SkeletonCard rows={2} /></div>;
  if (error) return <ErrorState title="Projects unavailable" message={error} onRetry={load} />;

  return (
    <>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-5 animate-rise">
        <div>
          <p className="mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Proof, not just progress</p>
          <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Project studio</h1>
          <p className="mt-3 text-sm leading-6 text-[#718079]">Projects turn a concept into evidence.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-xl border border-[#cbd5ce] bg-[#fbfaf5] px-4 py-2.5 text-sm font-bold text-[#27403b]"><Plus size={15} /> Add project</button>
      </div>

      <div className="mb-6 flex gap-1 rounded-xl bg-[#e6ebe4] p-1 md:w-fit">
        {(['all', 'current', 'completed'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} className={`rounded-lg px-4 py-2 text-xs font-bold capitalize ${tab === t ? 'bg-[#fbfaf5] text-[#20322f] shadow-sm' : 'text-[#7b8882]'}`}>{t}</button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title={tab === 'completed' ? 'No completed projects yet' : 'No projects assigned yet'}
          description="Projects will appear here once your learning path is generated."
        />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {filtered.map(p => (
            <section key={p.id} className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <Tag warm={p.status === 'recommended'}>{p.type ?? 'Project'}</Tag>
                  <h2 className="display mt-4 text-2xl font-bold leading-tight">{p.title}</h2>
                </div>
                <button className="rounded-lg p-1 text-[#8c9892]"><MoreHorizontal size={18} /></button>
              </div>
              {p.reason && <p className="mt-4 text-sm leading-6 text-[#718079]"><span className="font-bold text-[#40534d]">Why this project: </span>{p.reason}</p>}
              {p.description && !p.reason && <p className="mt-4 text-sm leading-6 text-[#718079]">{p.description}</p>}
              {p.skills && p.skills.length > 0 && (
                <div className="mt-5 flex flex-wrap gap-2">{p.skills.map(s => <Tag key={s}>{s}</Tag>)}</div>
              )}
              <div className="mt-6 flex items-center justify-between border-t border-[#e4e9e2] pt-4">
                {p.estimated_time && <span className="flex items-center gap-1.5 text-xs text-[#83918a]"><Clock3 size={14} /> {p.estimated_time}</span>}
                {p.status === 'completed' ? (
                  <span className="flex items-center gap-1.5 text-xs font-bold text-[#176b65]"><Check size={14} /> Shipped</span>
                ) : (
                  <button className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-sm font-bold text-[#f7f5ed] hover:bg-[#115a55]">
                    {p.status === 'in_progress' || p.status === 'current' ? 'Continue' : 'Start'} <ArrowRight size={14} />
                  </button>
                )}
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  );
}
