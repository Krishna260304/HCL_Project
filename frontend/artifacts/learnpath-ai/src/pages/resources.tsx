import { useState, useEffect } from 'react';
import { Search, Star } from 'lucide-react';
import { resourceService, type Resource } from '@/services/index';
import { SkeletonCard, ErrorState, EmptyState } from '@/components/states';

function Tag({ children, warm = false }: { children: React.ReactNode; warm?: boolean }) {
  return <span className={`inline-flex rounded-lg px-2 py-1 text-[10px] font-bold ${warm ? 'bg-[#fae9bb] text-[#93611a]' : 'bg-[#e3eee7] text-[#176b65]'}`}>{children}</span>;
}

export default function Resources() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('All');
  const [searching, setSearching] = useState(false);

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const data = await resourceService.listResources({ limit: 50 });
      setResources(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load resources.');
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleSearch = async () => {
    if (!query.trim()) { load(); return; }
    setSearching(true);
    try {
      const data = await resourceService.searchResources(query, filter !== 'All' ? { type: filter } : {});
      setResources(data);
    } catch { /* keep previous */ }
    finally { setSearching(false); }
  };

  useEffect(() => {
    if (!query.trim()) { load(); return; }
    const t = setTimeout(handleSearch, 500);
    return () => clearTimeout(t);
  }, [query, filter]);

  const filtered = filter === 'All' ? resources : resources.filter(r => r.type === filter);

  if (loading) return <div className="space-y-4"><SkeletonCard /><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{[1,2,3].map(i => <SkeletonCard key={i} rows={2} />)}</div></div>;

  return (
    <>
      <div className="mb-8 animate-rise">
        <p className="mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Curated for your route</p>
        <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Resource shelf</h1>
        <p className="mt-3 text-sm leading-6 text-[#718079]">Less browsing, more learning. These are here because they help with the next skill on your path.</p>
      </div>

      <div className="mb-6 flex flex-col gap-3 md:flex-row">
        <label className="relative flex-1">
          <Search size={17} className="absolute left-4 top-3.5 text-[#88958e]" />
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search titles, skills, or sources"
            className="w-full rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] py-3 pl-11 pr-4 text-sm outline-none focus:border-[#176b65]" />
        </label>
        <select value={filter} onChange={e => setFilter(e.target.value)}
          className="rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-3 text-sm font-bold text-[#40534d] outline-none">
          <option>All</option><option>Article</option><option>Video</option><option>Video series</option><option>Interactive</option><option>Workshop</option><option>Book chapter</option>
        </select>
      </div>

      {error && <ErrorState title="Resources unavailable" message={error} onRetry={load} />}
      {!error && filtered.length === 0 && !searching && (
        <EmptyState title="No resources available yet" description="Your personalized resources will appear here once your learning path is generated." />
      )}
      {searching && <div className="text-center py-8 text-sm text-[#718079]">Searching…</div>}

      {!error && filtered.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map(r => (
            <section key={r.id} className="group rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm transition-transform duration-200 hover:-translate-y-1">
              <div className="flex items-start justify-between">
                <div className="flex gap-2"><Tag>{r.type ?? 'Resource'}</Tag>{r.difficulty && <Tag warm>{r.difficulty}</Tag>}</div>
                {r.rating && <span className="flex items-center gap-1 text-xs text-[#d89c2c]"><Star size={13} fill="currentColor" />{r.rating}</span>}
              </div>
              <h2 className="display mt-6 text-xl font-bold leading-tight text-[#20322f]">{r.title}</h2>
              <p className="mt-2 text-xs text-[#83918a]">{r.source}{r.duration ? ` · ${r.duration}` : ''}</p>
              {r.reason && (
                <p className="mt-4 rounded-xl bg-[#eef2ea] p-3 text-xs leading-5 text-[#61716c]">
                  <span className="font-bold text-[#36504a]">Why it's here: </span>{r.reason}
                </p>
              )}
              {r.skills && r.skills.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-1">
                  {r.skills.map(s => <span key={s} className="text-[10px] font-bold text-[#176b65]">#{s.replaceAll(' ', '')}</span>)}
                </div>
              )}
            </section>
          ))}
        </div>
      )}
    </>
  );
}
