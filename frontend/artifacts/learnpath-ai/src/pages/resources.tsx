import { useState, useEffect } from 'react';
import { Link } from 'wouter';
import {
  Search,
  Star,
  Sparkles,
  ExternalLink,
  BookOpen,
  CheckCircle2,
  Clock,
  Filter,
  Bookmark,
  Layers,
  ArrowRight,
  Zap,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react';
import { resourceService, type Resource } from '@/services/index';
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

export default function Resources() {
  const { toast } = useToast();
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');
  const [difficultyFilter, setDifficultyFilter] = useState('All');
  const [savedIds, setSavedIds] = useState<string[]>(['res_01', 'res_03']);
  const [startedIds, setStartedIds] = useState<string[]>(['res_01']);
  const [ratings, setRatings] = useState<Record<string, 'up' | 'down'>>({});

  const handleRate = (id: string, type: 'up' | 'down') => {
    setRatings((prev) => ({ ...prev, [id]: type }));
    toast({
      title: type === 'up' ? 'Feedback Noted! 👍' : 'Feedback Recorded 💡',
      description:
        type === 'up'
          ? 'Marked as highly relevant to your active skill goals.'
          : 'We will de-prioritize similar modules in your future recommendations.',
    });
  };

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await resourceService.listResources({ limit: 50 });
      setResources(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load resources.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggleSave = (id: string, title: string) => {
    const isSaved = savedIds.includes(id);
    const updated = isSaved ? savedIds.filter((x) => x !== id) : [...savedIds, id];
    setSavedIds(updated);
    toast({
      title: isSaved ? 'Removed from Queue' : 'Saved to Learning Queue 📌',
      description: `"${title}" has been ${isSaved ? 'removed from' : 'added to'} your study queue.`,
    });
  };

  const handleStart = (id: string, title: string) => {
    if (!startedIds.includes(id)) {
      setStartedIds([...startedIds, id]);
    }
    toast({
      title: 'Session Started 🚀',
      description: `Now studying "${title}". Progress will be recorded against your active phase.`,
    });
  };

  const filtered = resources.filter((r) => {
    const matchesQuery =
      !query.trim() ||
      r.title.toLowerCase().includes(query.toLowerCase()) ||
      r.source?.toLowerCase().includes(query.toLowerCase()) ||
      r.skills?.some((s) => s.toLowerCase().includes(query.toLowerCase()));

    const matchesType = typeFilter === 'All' || r.type?.toLowerCase() === typeFilter.toLowerCase();
    const matchesDifficulty =
      difficultyFilter === 'All' || r.difficulty?.toLowerCase() === difficultyFilter.toLowerCase();

    return matchesQuery && matchesType && matchesDifficulty;
  });

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <SkeletonCard rows={2} />
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <SkeletonCard key={i} rows={3} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-rise">
      {/* ─── Top Header & Value Proposition ──────────────────────────────────────── */}
      <div className="flex flex-wrap items-end justify-between gap-5 border-b border-[#dbe4da] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] font-bold uppercase tracking-[.2em] text-[#b17820]">
              Personalized Recommendations
            </span>
            <span className="text-[#c5cdc5]">/</span>
            <span className="inline-flex items-center gap-1 text-xs font-bold text-[#176b65]">
              <Sparkles size={13} className="text-[#d89c2c]" /> AI Reasoned & Curated
            </span>
          </div>

          <h1 className="display mt-2 text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">
            Resource Shelf
          </h1>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-[#718079]">
            Less searching, more focused learning. Every item is curated specifically to bridge your active skill gaps in Phase 3.
          </p>
        </div>

        <Link
          href="/learning-path"
          className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-xs font-bold text-[#f7f5ed] shadow-sm hover:bg-[#115a55] transition"
        >
          View Connected Roadmap <ArrowRight size={14} />
        </Link>
      </div>

      {/* ─── Search & Multi-Faceted Filters ──────────────────────────────────────── */}
      <div className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row gap-3">
          <label className="relative flex-1">
            <Search size={17} className="absolute left-4 top-3.5 text-[#88958e]" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by topic, skill (e.g. REST, JWT, SQL), or publisher..."
              className="w-full rounded-xl border border-[#ccd8ce] bg-white py-3 pl-11 pr-4 text-sm outline-none focus:border-[#176b65] transition"
            />
          </label>

          <div className="flex flex-wrap gap-2.5">
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="rounded-xl border border-[#ccd8ce] bg-white px-3.5 py-3 text-xs font-bold text-[#40534d] outline-none cursor-pointer"
            >
              <option value="All">All Formats</option>
              <option value="Workshop">Interactive Workshop</option>
              <option value="Article">Deep-Dive Article</option>
              <option value="Video">Video Course</option>
              <option value="Interactive">Hands-on Lab</option>
            </select>

            <select
              value={difficultyFilter}
              onChange={(e) => setDifficultyFilter(e.target.value)}
              className="rounded-xl border border-[#ccd8ce] bg-white px-3.5 py-3 text-xs font-bold text-[#40534d] outline-none cursor-pointer"
            >
              <option value="All">All Difficulties</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>
        </div>

        {/* Quick Filter Tag Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span className="text-[#718079] font-bold flex items-center gap-1 mr-1">
            <Filter size={12} /> Quick Focus:
          </span>
          {['REST APIs', 'JWT Security', 'Database Design', 'WebSockets'].map((chip) => (
            <button
              key={chip}
              onClick={() => setQuery(query === chip ? '' : chip)}
              className={`rounded-lg px-2.5 py-1 font-bold text-[11px] transition ${
                query === chip
                  ? 'bg-[#176b65] text-white'
                  : 'bg-[#eef2ea] text-[#61716c] hover:bg-[#e2e8dc] hover:text-[#20322f]'
              }`}
            >
              #{chip}
            </button>
          ))}
          {query && (
            <button
              onClick={() => setQuery('')}
              className="text-[11px] font-bold text-[#b45309] hover:underline ml-2"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* ─── Resource Grid ──────────────────────────────────────────────────────── */}
      {error && <ErrorState title="Resources unavailable" message={error} onRetry={load} />}

      {!error && filtered.length === 0 && (
        <EmptyState
          title="No matching resources found"
          description="Try broadening your search query or switching category filters."
          action={
            <button
              onClick={() => {
                setQuery('');
                setTypeFilter('All');
                setDifficultyFilter('All');
              }}
              className="rounded-xl bg-[#176b65] px-4 py-2 text-xs font-bold text-white"
            >
              Reset all filters
            </button>
          }
        />
      )}

      {!error && filtered.length > 0 && (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((r) => {
            const isSaved = savedIds.includes(r.id);
            const isStarted = startedIds.includes(r.id);

            return (
              <section
                key={r.id}
                className="group rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between hover:border-[#176b65]"
              >
                <div>
                  {/* Card Header: Type, Difficulty, Star Rating */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <Tag variant="teal">{r.type ?? 'Resource'}</Tag>
                      {r.difficulty && <Tag variant="gold">{r.difficulty}</Tag>}
                    </div>

                    <div className="flex items-center gap-2">
                      {r.rating && (
                        <span className="flex items-center gap-1 text-xs font-bold text-[#d89c2c]">
                          <Star size={13} fill="currentColor" /> {r.rating}
                        </span>
                      )}
                      <button
                        onClick={() => toggleSave(r.id, r.title)}
                        className={`p-1 rounded-lg transition ${
                          isSaved ? 'text-[#176b65]' : 'text-[#8c9892] hover:text-[#20322f]'
                        }`}
                        title={isSaved ? 'Saved' : 'Save to queue'}
                      >
                        <Bookmark size={16} fill={isSaved ? 'currentColor' : 'none'} />
                      </button>
                    </div>
                  </div>

                  {/* Title & Publisher */}
                  <h2 className="display mt-4 text-xl font-bold leading-snug text-[#20322f] group-hover:text-[#176b65] transition">
                    {r.title}
                  </h2>
                  <p className="mt-1.5 text-xs text-[#83918a]">
                    Published by <strong>{r.source || 'Curated'}</strong>
                    {r.duration ? ` · ${r.duration}` : ''}
                  </p>

                  {/* AI "Why This Was Recommended" Reason Box with Rating Widget */}
                  {r.reason && (
                    <div className="mt-4 rounded-xl bg-[#eef2ea] p-3.5 border border-[#dce4da] text-xs leading-relaxed text-[#51635e]">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <div className="flex items-center gap-1.5 font-bold text-[#176b65]">
                          <Sparkles size={12} className="text-[#d89c2c]" /> AI Recommendation Reason:
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            type="button"
                            onClick={() => handleRate(r.id, 'up')}
                            aria-label="Mark recommendation as helpful"
                            className={`p-1 rounded-md transition ${
                              ratings[r.id] === 'up'
                                ? 'bg-[#176b65] text-white shadow-2xs'
                                : 'text-[#718079] hover:bg-[#dbe6dc] hover:text-[#176b65]'
                            }`}
                          >
                            <ThumbsUp size={12} />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleRate(r.id, 'down')}
                            aria-label="Mark recommendation as not helpful"
                            className={`p-1 rounded-md transition ${
                              ratings[r.id] === 'down'
                                ? 'bg-[#a04b3e] text-white shadow-2xs'
                                : 'text-[#718079] hover:bg-[#fae2df] hover:text-[#a04b3e]'
                            }`}
                          >
                            <ThumbsDown size={12} />
                          </button>
                        </div>
                      </div>
                      <p className="mt-1">{r.reason}</p>
                    </div>
                  )}

                  {/* Skill Badges */}
                  {r.skills && r.skills.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-1.5">
                      {r.skills.map((s) => (
                        <span
                          key={s}
                          className="rounded-md bg-[#e3eee7] px-2 py-0.5 text-[10px] font-bold text-[#176b65]"
                        >
                          #{s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Card Actions Footer */}
                <div className="mt-6 pt-4 border-t border-[#e4e9e2] flex items-center justify-between gap-3">
                  <span className="text-[11px] text-[#88958e] font-mono">
                    {r.url ? 'Interactive Module' : 'Guided Reading'}
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleStart(r.id, r.title)}
                      className={`inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-xs font-bold transition shadow-sm ${
                        isStarted
                          ? 'bg-[#e3eee7] text-[#176b65] border border-[#bcdcc8]'
                          : 'bg-[#176b65] text-white hover:bg-[#115a55]'
                      }`}
                    >
                      {isStarted ? (
                        <>
                          <CheckCircle2 size={13} /> In Progress
                        </>
                      ) : (
                        <>
                          <Zap size={13} className="text-[#edbc55]" /> Start Learning
                        </>
                      )}
                    </button>

                    {r.url && (
                      <a
                        href={r.url}
                        target="_blank"
                        rel="noreferrer"
                        className="grid size-8 place-items-center rounded-xl border border-[#ccd8ce] text-[#61716c] hover:border-[#176b65] hover:text-[#176b65] transition"
                        title="Open external source"
                      >
                        <ExternalLink size={14} />
                      </a>
                    )}
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
