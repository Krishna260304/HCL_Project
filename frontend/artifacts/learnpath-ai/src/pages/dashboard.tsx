import { useState, useEffect } from 'react';
import { Link } from 'wouter';
import {
  ArrowRight,
  Check,
  Clock3,
  Flame,
  Play,
  Target,
  Sparkles,
  Zap,
  Bot,
  Compass,
  CheckCircle2,
  Circle,
  AlertCircle,
  TrendingUp,
  BookOpen,
  BriefcaseBusiness,
  Award,
  Layers,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import {
  progressService,
  learningPathService,
  skillService,
  profileService,
  type ProgressData,
  type LearningPath,
  type Skill,
  type LearnerProfile,
} from '@/services/index';
import { SkeletonCard, ErrorState } from '@/components/states';
import { useToast } from '@/hooks/use-toast';

function ProgressBar({ value, color = '#176b65' }: { value: number; color?: string }) {
  return (
    <div className="h-2 overflow-hidden rounded-full bg-[#e3e9e1]">
      <div
        className="h-full rounded-full transition-all duration-700 ease-out"
        style={{ width: `${Math.min(Math.max(value, 0), 100)}%`, background: color }}
      />
    </div>
  );
}

function Tag({
  children,
  variant = 'teal',
}: {
  children: React.ReactNode;
  variant?: 'teal' | 'gold' | 'emerald' | 'amber' | 'subtle';
}) {
  const styles = {
    teal: 'bg-[#e3eee7] text-[#176b65]',
    gold: 'bg-[#fae9bb] text-[#93611a]',
    emerald: 'bg-[#294b44] text-[#deebe0]',
    amber: 'bg-[#fef3c7] text-[#b45309]',
    subtle: 'bg-[#eef2ea] text-[#61716c]',
  };
  return (
    <span className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-bold ${styles[variant]}`}>
      {children}
    </span>
  );
}

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <section className={`rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] shadow-sm transition-all duration-200 ${className}`}>
      {children}
    </section>
  );
}

interface MilestoneItem {
  id: string;
  title: string;
  type: 'concept' | 'project' | 'assessment';
  duration: string;
  completed: boolean;
}

export default function Dashboard() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [path, setPath] = useState<LearningPath | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completedMilestones, setCompletedMilestones] = useState<string[]>(['ms_01']);
  const [nextActionCompleted, setNextActionCompleted] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [prof, p, lp, sk] = await Promise.all([
        profileService.getProfile().catch(() => null),
        progressService.getProgress().catch(() => null),
        learningPathService.getLearningPath().catch(() => null),
        skillService.listSkills({ limit: 4 }).catch(() => []),
      ]);
      setProfile(prof);
      setProgress(p);
      setPath(lp);
      setSkills(sk as Skill[]);
    } catch {
      setError('Unable to load your dashboard. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggleMilestone = (milestoneId: string, title: string) => {
    const isNowDone = !completedMilestones.includes(milestoneId);
    const updated = isNowDone
      ? [...completedMilestones, milestoneId]
      : completedMilestones.filter((id) => id !== milestoneId);

    setCompletedMilestones(updated);

    if (isNowDone) {
      toast({
        title: 'Milestone Completed! 🎉',
        description: `Great progress! "${title}" has been verified in your active phase.`,
      });
    }
  };

  const handleCompleteNextAction = () => {
    setNextActionCompleted(!nextActionCompleted);
    if (!nextActionCompleted) {
      toast({
        title: 'Session Goal Shipped! 🚀',
        description: 'Your project checkpoint has been registered. Roadmap progress updated by +8%.',
      });
    }
  };

  if (loading) {
    return (
      <div className="space-y-5 animate-pulse">
        <SkeletonCard rows={2} />
        <div className="grid gap-5 lg:grid-cols-2">
          <SkeletonCard rows={3} />
          <SkeletonCard rows={3} />
        </div>
      </div>
    );
  }

  if (error) return <ErrorState title="Dashboard unavailable" message={error} onRetry={load} />;

  const displayName = profile?.name || user?.email?.split('@')[0] || 'Alex';
  const targetGoal = profile?.goals?.[0] || path?.goal || 'Full-Stack Web & AI Application Architect';
  const currentPhase = path?.phases?.find((p) => p.status === 'current') || path?.phases?.[2];
  
  // Calculate dynamic progress with interactive milestone additions
  const baseProgress = path?.total_progress ?? progress?.overall_progress ?? 42;
  const milestoneBonus = (completedMilestones.length - 1) * 4 + (nextActionCompleted ? 8 : 0);
  const overallProgress = Math.min(baseProgress + milestoneBonus, 100);
  
  const streak = progress?.learning_streak ?? 12;
  const totalHours = (progress?.total_hours ?? 46.5) + (nextActionCompleted ? 2.5 : 0);
  const prioritySkills = skills.filter((s) => s.gap && s.gap > 0).slice(0, 3);
  const activities = progress?.activity || [];

  const phaseMilestones: MilestoneItem[] = [
    {
      id: 'ms_01',
      title: 'Study RESTful HTTP Semantics & Clean Service Architecture',
      type: 'concept',
      duration: '2.5 hrs',
      completed: completedMilestones.includes('ms_01'),
    },
    {
      id: 'ms_02',
      title: 'Implement JWT Token Rotation & Session Invalidation Middleware',
      type: 'concept',
      duration: '3.0 hrs',
      completed: completedMilestones.includes('ms_02'),
    },
    {
      id: 'ms_03',
      title: 'Build Production-Grade REST & WebSocket Gateway Checkpoint',
      type: 'project',
      duration: '18 hrs',
      completed: completedMilestones.includes('ms_03') || nextActionCompleted,
    },
    {
      id: 'ms_04',
      title: 'Pass API Security & Gateway Diagnostic Evaluation',
      type: 'assessment',
      duration: '30 mins',
      completed: completedMilestones.includes('ms_04'),
    },
  ];

  return (
    <div className="space-y-8 animate-rise">
      {/* ─── Top Greeting & Destination Header ──────────────────────────────────────── */}
      <div className="flex flex-wrap items-end justify-between gap-5 border-b border-[#dbe4da] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] font-bold uppercase tracking-[.2em] text-[#b17820]">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
            </span>
            <span className="text-[#c5cdc5]">/</span>
            <span className="inline-flex items-center gap-1 text-xs font-bold text-[#176b65]">
              <Sparkles size={13} className="text-[#d89c2c]" /> Adaptive Track Active
            </span>
          </div>

          <h1 className="display mt-2 text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">
            Welcome back, {displayName}.
          </h1>

          <div className="mt-3.5 flex flex-wrap items-center gap-3 text-sm text-[#718079]">
            <span className="text-xs font-bold text-[#51645e]">Target Goal:</span>
            <div className="relative inline-block">
              <select
                value={targetGoal}
                onChange={(e) => {
                  const newGoal = e.target.value;
                  setProfile((prev) => prev ? { ...prev, goals: [newGoal] } : null);
                  toast({
                    title: 'Career Track Recalibrated! 🎯',
                    description: `Active curriculum and recommendations adjusted for "${newGoal}".`,
                  });
                }}
                className="rounded-xl border border-[#c6d7cb] bg-[#eef6f0] px-3 py-1.5 text-xs font-bold text-[#176b65] outline-none hover:border-[#176b65] transition cursor-pointer shadow-2xs"
                data-testid="select-track-switcher"
              >
                <option value="Full-Stack Web & AI Application Architect">🚀 Full-Stack Web & AI Architect</option>
                <option value="Machine Learning & LLM Systems Engineer">🎓 ML & LLM Systems Engineer</option>
                <option value="Cloud Infrastructure & DevOps Architect">☁️ Cloud Infrastructure & DevOps</option>
              </select>
            </div>
            {currentPhase && (
              <>
                <span className="text-[#c5cdc5]">·</span>
                <span className="text-xs">Active Phase: <strong className="text-[#176b65]">{currentPhase.title}</strong></span>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/assistant"
            className="inline-flex items-center gap-2 rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-2.5 text-xs font-bold text-[#36504a] shadow-sm hover:border-[#176b65] hover:text-[#176b65] transition"
          >
            <Bot size={15} className="text-[#176b65]" /> Ask Coach
          </Link>
          <Link
            href="/learning-path"
            className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-xs font-bold text-[#f7f5ed] shadow-sm hover:bg-[#115a55] transition"
          >
            Full Roadmap <ArrowRight size={14} />
          </Link>
        </div>
      </div>

      {/* ─── Hero Section: Next Best Action + Path Momentum ────────────────────────── */}
      <div className="grid gap-6 xl:grid-cols-[1.35fr_.65fr]">
        {/* HERO: Next Best Action Decision Card */}
        <Card className="!bg-[#203d38] overflow-hidden text-[#f8f5eb] shadow-[0_20px_50px_rgba(32,61,56,0.18)]">
          <div className="p-6 md:p-8 flex flex-col justify-between h-full">
            <div>
              {/* Badge & Context Header */}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="inline-flex items-center gap-2 rounded-full bg-[#294b44] px-3 py-1 text-[11px] font-bold text-[#edbc55] border border-[#3b635a]">
                  <Zap size={13} className="text-[#edbc55] animate-pulse" /> AI RECOMMENDED NEXT BEST ACTION
                </div>
                <span className="font-mono text-xs font-bold text-[#a6c4b2]">Phase 3 Checkpoint</span>
              </div>

              {/* Title & Core Problem Addressed */}
              <h2 className="display mt-5 text-2xl md:text-3xl font-bold leading-tight tracking-[-.03em] text-[#f8f5eb]">
                Build your Production-Grade REST & WebSocket Gateway
              </h2>

              {/* AI "Why This Action Now?" Context Box */}
              <div className="mt-4 rounded-xl bg-[#294b44]/90 p-4 border border-[#40685e] text-xs leading-relaxed text-[#d7e7dc]">
                <div className="flex items-center gap-1.5 font-bold text-[#edbc55] mb-1">
                  <Sparkles size={13} /> Why this action now?
                </div>
                Addresses your <strong>27% gap in REST API design</strong> and <strong>40% gap in security protocols</strong>. Completing this checkpoint provides verified proof required before advancing to Distributed Systems in Phase 4.
              </div>

              {/* Metadata Badges */}
              <div className="mt-5 flex flex-wrap items-center gap-3">
                <span className="flex items-center gap-1.5 text-xs text-[#b9d1c1] bg-[#1a332f] px-3 py-1.5 rounded-lg border border-[#2e5047]">
                  <Clock3 size={13} className="text-[#edbc55]" /> ~18 hours estimated
                </span>
                <span className="flex items-center gap-1.5 text-xs text-[#b9d1c1] bg-[#1a332f] px-3 py-1.5 rounded-lg border border-[#2e5047]">
                  <Target size={13} className="text-[#edbc55]" /> Intermediate–Advanced
                </span>
                <span className="flex items-center gap-1.5 text-xs text-[#b9d1c1] bg-[#1a332f] px-3 py-1.5 rounded-lg border border-[#2e5047]">
                  <BriefcaseBusiness size={13} className="text-[#edbc55]" /> REST & Auth Project
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 pt-6 border-t border-[#31574e] flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-3">
                <Link
                  href="/projects"
                  className="inline-flex items-center gap-2 rounded-xl bg-[#edbc55] px-5 py-3 text-sm font-bold text-[#20322f] hover:bg-[#e7a93b] transition shadow-md hover:shadow-lg"
                >
                  <Play size={15} fill="currentColor" /> Continue Project Checkpoint
                </Link>

                <button
                  onClick={handleCompleteNextAction}
                  className={`inline-flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-bold border transition ${
                    nextActionCompleted
                      ? 'bg-[#176b65] text-[#f7f5ed] border-[#176b65]'
                      : 'bg-[#294b44] text-[#deebe0] border-[#40685e] hover:border-[#edbc55]'
                  }`}
                >
                  <Check size={16} />
                  {nextActionCompleted ? 'Checkpoint Verified' : 'Mark Completed'}
                </button>
              </div>

              <Link
                href="/assistant"
                className="text-xs font-bold text-[#b9d1c1] hover:text-[#edbc55] transition flex items-center gap-1"
              >
                Why this recommendation? <ChevronRight size={13} />
              </Link>
            </div>
          </div>
        </Card>

        {/* Path Momentum & Streak Card */}
        <Card className="p-6 md:p-7 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-mono text-[10px] font-bold uppercase tracking-[.18em] text-[#82918a]">
                  Path Momentum
                </p>
                <h3 className="display mt-1 text-3xl font-bold text-[#20322f]">{overallProgress}%</h3>
              </div>
              <span className="grid size-12 place-items-center rounded-2xl bg-[#fae9bb] text-[#a66c15] shadow-sm">
                <Flame size={22} />
              </span>
            </div>

            {/* Circular Conic Ring + Bar */}
            <div className="mt-6 flex items-center gap-5">
              <div
                className="grid shrink-0 size-24 place-items-center rounded-full border-[8px] border-[#e4eee6] transition-all duration-700"
                style={{
                  background: `conic-gradient(#176b65 ${overallProgress}%, transparent 0)`,
                }}
              >
                <div className="grid size-[64px] place-items-center rounded-full bg-[#fbfaf5]">
                  <span className="display text-xl font-bold text-[#20322f]">{overallProgress}%</span>
                </div>
              </div>

              <div className="flex-1 space-y-2">
                <div className="flex justify-between text-xs font-bold text-[#40534d]">
                  <span>Total Hours</span>
                  <span>{totalHours.toFixed(1)} hrs</span>
                </div>
                <div className="flex justify-between text-xs font-bold text-[#40534d]">
                  <span>Learning Streak</span>
                  <span className="text-[#a66c15] flex items-center gap-1">
                    <Flame size={13} fill="currentColor" /> {streak} Days
                  </span>
                </div>
                <div className="flex justify-between text-xs font-bold text-[#40534d]">
                  <span>Phases Complete</span>
                  <span className="text-[#176b65]">2 of 5</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-5 border-t border-[#e4e9e2] space-y-3">
            <div className="rounded-xl bg-[#eef2ea] p-3 text-xs leading-5 text-[#61716c]">
              <span className="font-bold text-[#20322f]">Adaptive Coach Read: </span>
              Your momentum is in the top 10% of active cohorts. Complete the Phase 3 project to unlock Phase 4 Distributed Caching.
            </div>

            <Link
              href="/progress"
              className="flex items-center justify-between text-xs font-bold text-[#176b65] hover:underline"
            >
              <span>View full progress analytics</span>
              <ArrowRight size={13} />
            </Link>
          </div>
        </Card>
      </div>

      {/* ─── Second Row: Active Phase Milestones + Skill Signal Matrix ──────────────── */}
      <div className="grid gap-6 lg:grid-cols-[1.1fr_.9fr]">
        {/* Active Phase Milestone Checklist */}
        <Card>
          <div className="flex items-center justify-between border-b border-[#e4e9e2] px-6 py-5">
            <div>
              <div className="flex items-center gap-2">
                <Tag variant="gold">Phase 3 Milestone Tracker</Tag>
                <span className="text-xs font-bold text-[#83918a]">In Motion</span>
              </div>
              <h2 className="display mt-2 text-xl font-bold text-[#20322f]">
                Backend API Architecture & Security
              </h2>
            </div>
            <Link href="/learning-path" className="text-xs font-bold text-[#176b65] hover:underline">
              View All Phases
            </Link>
          </div>

          <div className="p-6 space-y-3">
            {phaseMilestones.map((ms, index) => (
              <button
                key={ms.id}
                onClick={() => toggleMilestone(ms.id, ms.title)}
                className={`w-full flex items-start gap-3.5 p-3.5 rounded-xl border text-left transition-all ${
                  ms.completed
                    ? 'bg-[#edf5f0] border-[#ccd8ce] text-[#176b65]'
                    : 'bg-[#fafbf8] border-[#e3e8e0] hover:border-[#176b65] text-[#40534d]'
                }`}
              >
                <span className="mt-0.5 shrink-0">
                  {ms.completed ? (
                    <CheckCircle2 size={18} className="text-[#176b65]" />
                  ) : (
                    <Circle size={18} className="text-[#9aa7a0]" />
                  )}
                </span>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className={`text-sm font-bold truncate ${ms.completed ? 'line-through opacity-80' : ''}`}>
                      {index + 1}. {ms.title}
                    </p>
                    <span className="font-mono text-[11px] text-[#83918a] shrink-0">{ms.duration}</span>
                  </div>
                  <div className="mt-1 flex items-center gap-2">
                    <Tag variant={ms.type === 'project' ? 'amber' : ms.type === 'assessment' ? 'teal' : 'subtle'}>
                      {ms.type === 'project' ? 'Checkpoint Project' : ms.type === 'assessment' ? 'Diagnostic Evaluation' : 'Core Concept'}
                    </Tag>
                    {ms.completed && <span className="text-[11px] font-bold text-[#176b65]">✓ Verified Complete</span>}
                  </div>
                </div>
              </button>
            ))}
          </div>

          <div className="border-t border-[#e4e9e2] bg-[#f6f8f4] px-6 py-4 rounded-b-2xl flex items-center justify-between text-xs text-[#718079]">
            <span>Click any milestone to simulate completion and dynamic roadmap adaptation.</span>
          </div>
        </Card>

        {/* Skill Gap & Role-Readiness Signals */}
        <Card>
          <div className="flex items-center justify-between border-b border-[#e4e9e2] px-6 py-5">
            <div>
              <Tag variant="teal">Skill Intelligence</Tag>
              <h2 className="display mt-2 text-xl font-bold text-[#20322f]">
                Active Gaps vs Role Threshold
              </h2>
            </div>
            <Link href="/skills" className="text-xs font-bold text-[#176b65] hover:underline">
              Full Matrix
            </Link>
          </div>

          <div className="p-6 space-y-5">
            {prioritySkills.map((s) => (
              <div key={s.id ?? s.name} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-[#36504a]">{s.name}</span>
                  <Tag variant={(s.gap ?? 0) > 30 ? 'gold' : 'teal'}>
                    {(s.gap ?? 0) > 0 ? `Gap: ${s.gap}%` : 'Role Ready'}
                  </Tag>
                </div>

                <div className="relative">
                  <ProgressBar
                    value={s.verified_score ?? s.self_score ?? 0}
                    color={(s.gap ?? 0) > 30 ? '#d89c2c' : '#176b65'}
                  />
                  {s.required_score && (
                    <span
                      className="absolute -top-1 size-3.5 rounded-full border-2 border-white bg-[#20322f] shadow-sm"
                      title={`Target Requirement: ${s.required_score}%`}
                      style={{ left: `calc(${s.required_score}% - 7px)` }}
                    />
                  )}
                </div>

                <div className="flex justify-between text-[10px] font-mono text-[#88958e]">
                  <span>Current: {s.verified_score ?? s.self_score ?? 0}%</span>
                  <span>Role Threshold: {s.required_score ?? 80}%</span>
                </div>
              </div>
            ))}
          </div>

          <div className="px-6 pb-6">
            <Link
              href="/skills"
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-[#cbd5ce] bg-[#fbfaf5] py-2.5 text-xs font-bold text-[#36504a] hover:border-[#176b65] hover:text-[#176b65] transition"
            >
              <ShieldCheck size={14} className="text-[#176b65]" /> Explore All 300+ Verified Skills
            </Link>
          </div>
        </Card>
      </div>

      {/* ─── Third Row: Recent Activity & Evidence Timeline ────────────────────────── */}
      <Card className="p-6 md:p-7">
        <div className="flex items-center justify-between border-b border-[#e4e9e2] pb-4 mb-5">
          <div>
            <h3 className="display text-xl font-bold text-[#20322f]">Recent Verified Learning Activity</h3>
            <p className="text-xs text-[#718079] mt-0.5">Live audit trail of completed checkpoints and session submissions</p>
          </div>
          <Link href="/progress" className="text-xs font-bold text-[#176b65] hover:underline">
            View Analytics
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {activities.slice(0, 4).map((act, idx) => (
            <div
              key={idx}
              className="rounded-xl border border-[#e3e8e0] bg-[#fafbf8] p-4 flex flex-col justify-between gap-3 hover:border-[#176b65] transition"
            >
              <div className="flex items-center justify-between">
                <span className="grid size-7 place-items-center rounded-lg bg-[#dceee4] text-[#176b65]">
                  <Check size={13} />
                </span>
                <span className="font-mono text-[10px] text-[#88958e]">{act.day || 'Recent'}</span>
              </div>
              <p className="text-xs font-bold text-[#36504a] leading-snug line-clamp-2">
                {act.title}
              </p>
              <span className="text-[11px] font-mono text-[#176b65]">{act.duration}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
