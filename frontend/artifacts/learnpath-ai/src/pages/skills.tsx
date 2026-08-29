import { useState, useEffect } from 'react';
import { Link } from 'wouter';
import {
  Gauge,
  ShieldCheck,
  Target,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ChevronDown,
  Sparkles,
  ArrowRight,
  BookOpen,
  Zap,
  HelpCircle,
  BarChart3,
  Layers,
  Filter,
} from 'lucide-react';
import { skillService, type Skill } from '@/services/index';
import { SkeletonCard, ErrorState, EmptyState } from '@/components/states';

function ProgressBar({
  value,
  threshold = 80,
  color = '#176b65',
}: {
  value: number;
  threshold?: number;
  color?: string;
}) {
  return (
    <div className="relative h-2.5 w-full overflow-visible rounded-full bg-[#e3e9e1]">
      {/* Progress Bar Fill */}
      <div
        className="h-full rounded-full transition-all duration-700 ease-out"
        style={{ width: `${Math.min(Math.max(value, 0), 100)}%`, background: color }}
      />
      {/* Role-ready Threshold Marker */}
      {threshold && (
        <span
          className="absolute -top-1 size-4 rounded-full border-2 border-white bg-[#20322f] shadow-sm z-10 transition-transform hover:scale-125"
          title={`Role-Ready Requirement: ${threshold}%`}
          style={{ left: `calc(${threshold}% - 8px)` }}
        />
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: 'Mastered' | 'Developing' | 'Priority Gap' | string }) {
  if (status === 'Mastered') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-[#dceee4] px-2.5 py-1 text-[11px] font-bold text-[#176b65] border border-[#bcdcc8]">
        <CheckCircle2 size={12} /> Mastered & Verified
      </span>
    );
  }
  if (status === 'Developing') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-[#fae9bb] px-2.5 py-1 text-[11px] font-bold text-[#93611a] border border-[#edd597]">
        <Clock size={12} /> Developing (Active Focus)
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-[#fbe9e5] px-2.5 py-1 text-[11px] font-bold text-[#a04b3e] border border-[#f2ccc5]">
      <Target size={12} /> Need to Learn (Target Gap)
    </span>
  );
}

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSkill, setExpandedSkill] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<'all' | 'mastered' | 'developing' | 'gaps'>('all');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await skillService.listSkills({});
      setSkills(data);
      // Auto-expand first developing skill
      const devSkill = data.find((s) => s.status === 'Developing');
      if (devSkill) setExpandedSkill(devSkill.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load skills.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid gap-5 md:grid-cols-4">
          <SkeletonCard rows={2} />
          <SkeletonCard rows={2} />
          <SkeletonCard rows={2} />
          <SkeletonCard rows={2} />
        </div>
        <SkeletonCard rows={4} />
      </div>
    );
  }

  if (error) return <ErrorState title="Skill intelligence unavailable" message={error} onRetry={load} />;
  if (skills.length === 0) return <EmptyState title="No skills data yet" description="Complete your onboarding to see your skill intelligence." />;

  // Categorize Skills into 3 Tiers
  const masteredSkills = skills.filter((s) => s.status === 'Mastered' || (s.gap === 0 && (s.verified_score ?? 0) >= (s.required_score ?? 70)));
  const developingSkills = skills.filter((s) => s.status === 'Developing' || ((s.gap ?? 0) > 0 && (s.gap ?? 0) <= 40));
  const gapSkills = skills.filter((s) => s.status === 'Priority Gap' || (s.gap ?? 0) > 40);

  // High-level Metrics
  const avgConfidence = skills.length
    ? Math.round(skills.reduce((a, s) => a + (s.verified_score ?? s.self_score ?? 0), 0) / skills.length)
    : 0;
  const totalVerified = masteredSkills.length;
  const totalDeveloping = developingSkills.length;
  const totalGaps = gapSkills.length;

  const filteredCategories = [
    {
      id: 'mastered',
      title: 'Tier 1: Mastered & Verified (Already Know)',
      description: 'Skills verified through diagnostic assessments and demonstrated project work.',
      badgeVariant: 'teal',
      badgeText: `${masteredSkills.length} Verified`,
      skills: masteredSkills,
    },
    {
      id: 'developing',
      title: 'Tier 2: Developing Competencies (In Progress)',
      description: 'Skills currently being practiced and deepened in active Phase 2 and Phase 3 roadmaps.',
      badgeVariant: 'gold',
      badgeText: `${developingSkills.length} Active Targets`,
      skills: developingSkills,
    },
    {
      id: 'gaps',
      title: 'Tier 3: Priority Skill Gaps (Need to Learn)',
      description: 'Critical knowledge domains required for role readiness scheduled for Phases 4 and 5.',
      badgeVariant: 'amber',
      badgeText: `${gapSkills.length} Priority Gaps`,
      skills: gapSkills,
    },
  ].filter((cat) => {
    if (activeFilter === 'all') return true;
    return cat.id === activeFilter;
  });

  const getCoachExplanation = (s: Skill) => {
    if (s.status === 'Mastered' || (s.gap ?? 0) === 0) {
      return `Your verified proficiency of ${s.verified_score ?? s.self_score}% is comfortably above the role threshold (${s.required_score}%). Keep this competency sharp by utilizing it in Phase 3 gateway projects.`;
    }
    if (s.status === 'Developing' || (s.gap ?? 0) <= 40) {
      return `Active focus area: You are currently ${s.gap}% points from role readiness. Completing the upcoming hands-on session will bridge this delta.`;
    }
    return `Critical prerequisite gap: Target role requires ${s.required_score}% proficiency (current baseline: ${s.verified_score ?? s.self_score}%). Scheduled for structured coverage in future roadmap phases.`;
  };

  return (
    <div className="space-y-8 animate-rise">
      {/* ─── Header & Value Proposition ────────────────────────────────────────── */}
      <div className="flex flex-wrap items-end justify-between gap-5 border-b border-[#dbe4da] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] font-bold uppercase tracking-[.2em] text-[#b17820]">
              Skill Intelligence & Gap Analysis
            </span>
            <span className="text-[#c5cdc5]">/</span>
            <span className="inline-flex items-center gap-1 text-xs font-bold text-[#176b65]">
              <ShieldCheck size={13} /> Evidence Over Guesswork
            </span>
          </div>

          <h1 className="display mt-2 text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">
            Skill-Gap Matrix
          </h1>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-[#718079]">
            Side-by-side verification: compare your self-reported confidence against verified diagnostic scores and target role thresholds.
          </p>
        </div>

        <Link
          href="/learning-path"
          className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-xs font-bold text-[#f7f5ed] shadow-sm hover:bg-[#115a55] transition"
        >
          View Connected Roadmap <ArrowRight size={14} />
        </Link>
      </div>

      {/* ─── Metric Summary Cards ────────────────────────────────────────────────── */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#718079] uppercase font-mono">Role Readiness</span>
            <Gauge className="text-[#176b65]" size={18} />
          </div>
          <p className="display mt-3 text-3xl font-bold text-[#20322f]">{avgConfidence}%</p>
          <p className="mt-1 text-xs text-[#718079]">Average across 9 core competencies</p>
        </section>

        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#718079] uppercase font-mono">Mastered Skills</span>
            <CheckCircle2 className="text-[#176b65]" size={18} />
          </div>
          <p className="display mt-3 text-3xl font-bold text-[#176b65]">{totalVerified}</p>
          <p className="mt-1 text-xs text-[#718079]">100% verified role-ready</p>
        </section>

        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#718079] uppercase font-mono">Developing</span>
            <Clock className="text-[#d89c2c]" size={18} />
          </div>
          <p className="display mt-3 text-3xl font-bold text-[#d89c2c]">{totalDeveloping}</p>
          <p className="mt-1 text-xs text-[#718079]">Active focus in Phases 2–3</p>
        </section>

        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#718079] uppercase font-mono">Priority Gaps</span>
            <Target className="text-[#a04b3e]" size={18} />
          </div>
          <p className="display mt-3 text-3xl font-bold text-[#a04b3e]">{totalGaps}</p>
          <p className="mt-1 text-xs text-[#718079]">Targeted in Phases 4–5</p>
        </section>
      </div>

      {/* ─── Filter Pills ───────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#e3e8e0] pb-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold text-[#718079] mr-1 flex items-center gap-1">
            <Filter size={13} /> Filter:
          </span>
          {[
            { id: 'all', label: `All Skills (${skills.length})` },
            { id: 'mastered', label: `Mastered (${totalVerified})` },
            { id: 'developing', label: `Developing (${totalDeveloping})` },
            { id: 'gaps', label: `Priority Gaps (${totalGaps})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id as typeof activeFilter)}
              className={`rounded-xl px-3.5 py-1.5 text-xs font-bold transition ${
                activeFilter === tab.id
                  ? 'bg-[#20322f] text-white shadow-sm'
                  : 'bg-[#eef2ea] text-[#61716c] hover:bg-[#e2e8dc] hover:text-[#20322f]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3 text-xs text-[#718079]">
          <span className="flex items-center gap-1.5">
            <span className="size-3 rounded-full bg-[#176b65]" /> Verified Score
          </span>
          <span className="flex items-center gap-1.5">
            <span className="size-3 rounded-full bg-[#20322f]" /> Role Threshold (80%)
          </span>
        </div>
      </div>

      {/* ─── 3-Tier Categorized Skill Breakdown ─────────────────────────────────── */}
      <div className="space-y-8">
        {filteredCategories.map((category) => (
          <div key={category.id} className="space-y-4">
            {/* Category Section Header */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="display text-xl font-bold text-[#20322f]">{category.title}</h2>
                  <span className="rounded-lg bg-[#e3eee7] px-2 py-0.5 text-xs font-bold text-[#176b65]">
                    {category.badgeText}
                  </span>
                </div>
                <p className="text-xs text-[#718079] mt-0.5">{category.description}</p>
              </div>
            </div>

            {/* Category Skill Cards */}
            <div className="space-y-3">
              {category.skills.map((s) => {
                const isExpanded = expandedSkill === s.id;
                const verifiedScore = s.verified_score ?? s.self_score ?? 0;
                const requiredScore = s.required_score ?? 80;
                const gap = s.gap ?? Math.max(requiredScore - verifiedScore, 0);

                return (
                  <section
                    key={s.id ?? s.name}
                    className={`rounded-2xl border bg-[#fbfaf5] shadow-sm transition-all duration-200 ${
                      isExpanded ? 'border-[#176b65] ring-1 ring-[#176b65]/20' : 'border-[#dbe4da] hover:border-[#ccd8ce]'
                    }`}
                  >
                    {/* Main Row Clickable Header */}
                    <button
                      onClick={() => setExpandedSkill(isExpanded ? null : s.id)}
                      className="w-full p-5 md:p-6 text-left flex flex-col md:flex-row md:items-center justify-between gap-4"
                    >
                      {/* Left: Skill Name, Category & Badges */}
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2.5">
                          <h3 className="display text-lg font-bold text-[#20322f] truncate">{s.name}</h3>
                          <StatusBadge status={s.status || (gap === 0 ? 'Mastered' : gap <= 40 ? 'Developing' : 'Priority Gap')} />
                          {s.category && (
                            <span className="font-mono text-[10px] uppercase tracking-wider text-[#88958e] bg-[#eef2ea] px-2 py-0.5 rounded-md">
                              {s.category}
                            </span>
                          )}
                        </div>
                        {s.description && <p className="mt-1 text-xs text-[#718079] line-clamp-1">{s.description}</p>}
                      </div>

                      {/* Middle: Visual Score vs Role-Ready Bar */}
                      <div className="w-full md:w-56 space-y-1.5 shrink-0">
                        <div className="flex justify-between text-xs font-mono font-bold">
                          <span className="text-[#176b65]">Current: {verifiedScore}%</span>
                          <span className="text-[#20322f]">Role: {requiredScore}%</span>
                        </div>
                        <ProgressBar
                          value={verifiedScore}
                          threshold={requiredScore}
                          color={gap === 0 ? '#176b65' : gap <= 40 ? '#d89c2c' : '#a04b3e'}
                        />
                        <div className="flex justify-between text-[10px] text-[#88958e]">
                          <span>Self: {s.self_score ?? verifiedScore}%</span>
                          <span>{gap > 0 ? `Gap: ${gap}%` : '✓ Role Ready'}</span>
                        </div>
                      </div>

                      {/* Right: Expand Chevron */}
                      <div className="hidden md:flex items-center pl-2">
                        <span className="grid size-8 place-items-center rounded-xl bg-[#eef2ea] text-[#61716c]">
                          <ChevronDown
                            size={16}
                            className={`transition-transform duration-200 ${isExpanded ? 'rotate-180 text-[#176b65]' : ''}`}
                          />
                        </span>
                      </div>
                    </button>

                    {/* Expandable AI Coach Insight Drawer */}
                    {isExpanded && (
                      <div className="border-t border-[#e4e9e2] bg-[#f6f8f4] p-5 md:px-7 md:py-6 rounded-b-2xl animate-fade">
                        <div className="grid gap-5 md:grid-cols-[1.3fr_.7fr]">
                          {/* Left: Coach Diagnostic Analysis */}
                          <div className="space-y-3">
                            <div className="flex items-center gap-2 font-bold text-xs text-[#176b65]">
                              <Sparkles size={14} className="text-[#d89c2c]" /> AI Coach Diagnostic Assessment
                            </div>
                            <p className="text-xs leading-relaxed text-[#40534d]">{getCoachExplanation(s)}</p>

                            <div className="flex flex-wrap items-center gap-4 text-xs text-[#718079] pt-2">
                              <span>
                                Last Assessed: <strong className="text-[#20322f]">{s.last_assessed || 'Diagnostic Benchmark'}</strong>
                              </span>
                              <span>•</span>
                              <span>
                                Confidence Level: <strong className="text-[#176b65]">{s.confidence || 'Verified'}</strong>
                              </span>
                            </div>
                          </div>

                          {/* Right: Actionable Next Step CTA */}
                          <div className="rounded-xl border border-[#dbe4da] bg-white p-4 flex flex-col justify-between gap-3 shadow-sm">
                            <div>
                              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#b17820]">
                                Recommended Action
                              </span>
                              <p className="text-xs font-bold text-[#20322f] mt-1">
                                {gap === 0
                                  ? 'Apply in Checkpoint Project'
                                  : `Close ${gap}% gap with targeted resource`}
                              </p>
                            </div>

                            <Link
                              href={gap === 0 ? '/projects' : '/resources'}
                              className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#176b65] px-3.5 py-2 text-xs font-bold text-white hover:bg-[#115a55] transition shadow-sm"
                            >
                              <BookOpen size={13} />
                              {gap === 0 ? 'Explore Projects' : 'Launch Closing Resource'}
                            </Link>
                          </div>
                        </div>
                      </div>
                    )}
                  </section>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
