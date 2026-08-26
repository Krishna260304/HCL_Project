import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import {
  ArrowRight, BrainCircuit, Check, Compass,
  Lightbulb, ListChecks, Menu, Radar, Target, TrendingUp, Zap, Sparkles, BookOpen, Bot, ShieldCheck, LockKeyhole,
} from 'lucide-react';
import { Link, Route, Switch, Router as WouterRouter } from 'wouter';
import { ErrorBoundary } from '@/components/error-boundary';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import { AuthProvider } from '@/context/AuthContext';
import AppShell from '@/components/AppShell';

// Dynamic Pages
import NotFound from '@/pages/not-found';
import AuthPage from '@/pages/auth';
import OnboardingSkills from '@/pages/onboarding-skills';
import Dashboard from '@/pages/dashboard';
import LearningPath from '@/pages/learning-path';
import PhaseDetail from '@/pages/phase-detail';
import Resources from '@/pages/resources';
import Projects from '@/pages/projects';
import Skills from '@/pages/skills';
import Assessments from '@/pages/assessments';
import Assistant from '@/pages/assistant';
import ProfilePage from '@/pages/profile';
import ProgressPage from '@/pages/progress';
import NotificationsPage from '@/pages/notifications';
import { AdminLogin, AdminDashboard, AdminModule } from '@/pages/admin';

const queryClient = new QueryClient();

// ─── Public Landing Components ────────────────────────────────────────────────

function Logo({ light = false }: { light?: boolean }) {
  return (
    <Link href="/" className={`flex items-center gap-2.5 font-bold tracking-tight ${light ? 'text-[#f8f5eb]' : 'text-[#20322f]'}`} data-testid="link-logo">
      <span className="grid size-8 place-items-center rounded-[10px] bg-[#e9ae3d] text-[#20322f]">
        <Compass size={18} strokeWidth={2.5} />
      </span>
      <span className="text-[17px] font-extrabold tracking-tight">learnpath<span className="text-[#d69323]">.</span>ai</span>
    </Link>
  );
}

function PublicNav() {
  const [open, setOpen] = useState(false);
  return (
    <header className="sticky top-0 z-40 border-b border-[#dfe5dc]/80 bg-[#f7f5ed]/90 backdrop-blur-md">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 lg:px-10">
        <Logo />
        <nav className="hidden items-center gap-7 text-sm font-semibold text-[#61716c] md:flex">
          <Link href="/how-it-works" className="hover:text-[#176b65]" data-testid="link-how-it-works">How it works</Link>
          <Link href="/features" className="hover:text-[#176b65]" data-testid="link-features">Features</Link>
          <Link href="/about" className="hover:text-[#176b65]" data-testid="link-about">About</Link>
        </nav>
        <div className="hidden items-center gap-3 md:flex">
          <Link href="/login" className="px-3 py-2 text-sm font-bold text-[#47605a] hover:text-[#176b65]" data-testid="link-login">
            Sign in
          </Link>
          <Link href="/register" className="inline-flex items-center gap-1.5 whitespace-nowrap rounded-xl bg-[#176b65] px-4 py-2.5 text-sm font-bold text-[#f7f5ed] hover:bg-[#115a55]" data-testid="link-register">
            Build my path <ArrowRight size={15} />
          </Link>
        </div>
        <button className="rounded-lg p-2 md:hidden" onClick={() => setOpen(!open)} data-testid="button-mobile-menu">
          <Menu size={21} />
        </button>
      </div>
      {open && (
        <div className="border-t border-[#dfe5dc] bg-[#f7f5ed] p-5 md:hidden">
          <div className="flex flex-col gap-4 text-sm font-bold">
            <Link href="/how-it-works">How it works</Link>
            <Link href="/features">Features</Link>
            <Link href="/about">About</Link>
            <Link href="/login">Sign in</Link>
            <Link href="/register" className="text-[#176b65]">Build my path <ArrowRight size={14} className="inline" /></Link>
          </div>
        </div>
      )}
    </header>
  );
}

function PublicPage({ title, eyebrow, children, action = true }: { title: React.ReactNode; eyebrow: string; children: React.ReactNode; action?: boolean }) {
  return (
    <>
      <PublicNav />
      <main className="mx-auto max-w-7xl px-5 pb-24 pt-16 lg:px-10 lg:pt-24">
        <div className="max-w-3xl animate-rise">
          <p className="font-mono mb-5 text-xs uppercase tracking-[.2em] text-[#b17820]">{eyebrow}</p>
          <h1 className="display text-5xl font-bold leading-[.98] tracking-[-.055em] text-[#20322f] md:text-7xl">{title}</h1>
        </div>
        {children}
        {action && (
          <div className="mt-16 rounded-3xl bg-[#203d38] p-8 text-[#f8f5eb] md:p-12">
            <p className="font-mono text-xs uppercase tracking-[.18em] text-[#edbc55]">Your next clear step</p>
            <h2 className="display mt-4 max-w-xl text-3xl font-bold tracking-tight">Start with a path built around the way you actually learn.</h2>
            <Link href="/register" className="mt-7 inline-flex items-center gap-2 rounded-xl bg-[#edbc55] px-5 py-3 text-sm font-bold text-[#20322f]" data-testid="link-public-cta">
              Create my learning path <ArrowRight size={16} />
            </Link>
          </div>
        )}
      </main>
    </>
  );
}

function Landing() {
  return (
    <>
      <PublicNav />
      <main className="overflow-hidden">
        <section className="relative mx-auto grid max-w-7xl items-center gap-14 px-5 pb-20 pt-16 lg:grid-cols-[1.05fr_.95fr] lg:px-10 lg:pb-28 lg:pt-24">
          <div className="relative z-10 animate-rise">
            <p className="font-mono mb-6 text-xs uppercase tracking-[.2em] text-[#b17820]">A clearer way forward</p>
            <h1 className="display max-w-3xl text-[clamp(3.6rem,8vw,7.7rem)] font-bold leading-[.86] tracking-[-.075em] text-[#20322f]">
              Learn with a <span className="text-[#176b65]">direction.</span>
            </h1>
            <p className="mt-8 max-w-lg text-lg leading-8 text-[#61716c]">
              LearnPath AI turns your current skills, your career destination, and your available time into an adaptive route you can trust.
            </p>
            <div className="mt-9 flex items-center gap-3">
              <Link href="/register" className="inline-flex items-center gap-2 whitespace-nowrap rounded-xl bg-[#176b65] px-5 py-3.5 text-sm font-bold text-[#f7f5ed] shadow-[0_10px_22px_rgba(23,107,101,.18)]" data-testid="link-hero-start">
                Build my learning path <ArrowRight size={16} />
              </Link>
              <Link href="/how-it-works" className="inline-flex items-center gap-2 rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-5 py-3.5 text-sm font-bold text-[#36504a]" data-testid="link-hero-learn">
                See how it works
              </Link>
            </div>
          </div>

          <div className="relative animate-rise-delay">
            <div className="absolute -right-10 -top-12 size-48 rounded-full bg-[#e9ae3d]/15 blur-3xl" />
            <div className="relative overflow-hidden rounded-[2rem] border border-[#dce6d6] bg-white shadow-[0_24px_64px_rgba(30,55,45,.10)]">
              <div className="border-b border-[#edf0ea] bg-[#f6f8f4] px-5 py-4 flex items-center gap-3">
                <span className="grid size-9 place-items-center rounded-xl bg-[#176b65] text-[#f7f5ed]">
                  <BrainCircuit size={17} />
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-[#8c9c94]">AI path generator</p>
                  <p className="text-sm font-bold text-[#1f312e] truncate">Adaptive Career Mapping</p>
                </div>
                <span className="shrink-0 rounded-full bg-[#dceee4] px-2.5 py-1 text-[10px] font-bold text-[#176b65]">
                  Dynamic
                </span>
              </div>
              <div className="p-6">
                <p className="mb-3 text-[10px] font-bold uppercase tracking-widest text-[#8c9c94]">Personalized roadmap</p>
                <div className="space-y-2.5">
                  <div className="flex items-center gap-3 rounded-xl bg-[#edf5f0] p-3 text-sm font-bold text-[#176b65]">
                    <span className="font-mono text-xs">01</span>
                    <span className="flex-1">Foundations & Prerequisites</span>
                    <Check size={14} />
                  </div>
                  <div className="flex items-center gap-3 rounded-xl bg-[#1f312e] p-3 text-white text-sm font-bold">
                    <span className="font-mono text-xs text-[#e9ae3d]">02</span>
                    <span className="flex-1">Applied Core Concepts</span>
                    <span className="size-1.5 animate-pulse rounded-full bg-[#e9ae3d]" />
                  </div>
                  <div className="flex items-center gap-3 rounded-xl border border-[#e8ede4] bg-[#fafbf8] p-3 text-sm font-bold text-[#40534d]">
                    <span className="font-mono text-xs text-[#8c9c94]">03</span>
                    <span className="flex-1">Advanced Architecture & Checkpoints</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-10">
          <div className="grid gap-12 md:grid-cols-[.75fr_1.25fr]">
            <div>
              <p className="font-mono text-xs uppercase tracking-[.2em] text-[#b17820]">The right focus</p>
              <h2 className="display mt-4 text-4xl font-bold leading-tight tracking-[-.04em] text-[#20322f] md:text-5xl">
                The next right milestone, not everything at once.
              </h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <Feature icon={<Target />} number="01" title="Start with your destination" text="Name the role you want and the time you can give. We map the rest." />
              <Feature icon={<Radar />} number="02" title="See the real gaps" text="A lightweight assessment separates what you know from what matters next." />
              <Feature icon={<Zap />} number="03" title="Keep the route moving" text="Your plan adapts when you complete a project, miss a week, or move faster." />
              <Feature icon={<Lightbulb />} number="04" title="Know why it matters" text="Every recommendation comes with context, so learning feels connected." />
            </div>
          </div>
        </section>
      </main>
    </>
  );
}

function Feature({ icon, number, title, text }: { icon: React.ReactNode; number: string; title: string; text: string }) {
  return (
    <div className="rounded-2xl border border-[#dce4da] bg-[#fbfaf5] p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-[#176b65] [&>svg]:size-5">{icon}</span>
        <span className="font-mono text-[10px] text-[#a6b0aa]">{number}</span>
      </div>
      <h3 className="mt-8 font-bold text-[#20322f]">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-[#718079]">{text}</p>
    </div>
  );
}

function HowItWorks() {
  return (
    <PublicPage eyebrow="The adaptive loop" title={<>A path that pays attention to <span className="text-[#176b65]">you.</span></>}>
      <div className="mt-16 space-y-5">
        {[
          ['01', 'Tell us where you are going', 'Choose a career destination, a realistic timeline, and the hours you can protect.', Target],
          ['02', 'Make the invisible visible', 'Surfaces your strengths and the concepts between today and the work you want to do.', Radar],
          ['03', 'Follow a small next step', 'Each day has a clear action, a reason it was chosen, and a way to prove you have it.', ListChecks],
          ['04', 'Let progress reshape the route', 'Complete a project or take a checkpoint. LearnPath adjusts the emphasis without losing the destination.', TrendingUp],
        ].map(([num, head, body, Icon]) => (
          <div key={num as string} className="grid gap-5 rounded-2xl border border-[#dce4da] bg-[#fbfaf5] p-6 md:grid-cols-[70px_1fr_48px] md:items-center">
            <span className="font-mono text-sm text-[#b17820]">{num as string}</span>
            <div>
              <h2 className="display text-2xl font-bold text-[#20322f]">{head as string}</h2>
              <p className="mt-2 max-w-2xl text-sm leading-7 text-[#718079]">{body as string}</p>
            </div>
            <span className="grid size-11 place-items-center rounded-xl bg-[#e3eee7] text-[#176b65]">
              <Icon size={20} />
            </span>
          </div>
        ))}
      </div>
    </PublicPage>
  );
}

function Features() {
  return (
    <PublicPage eyebrow="Built around momentum" title={<>A quieter kind of <span className="text-[#176b65]">intelligence.</span></>}>
      <div className="mt-16 grid gap-5 md:grid-cols-2">
        {[
          ['Adaptive roadmap', 'A living sequence of phases, projects, and checkpoints tied to your goal.', Compass],
          ['Skill intelligence', 'See self-reported confidence beside verified evidence.', ShieldCheck],
          ['Resource context', 'Every resource earns its place with an explanation of why it is here.', BookOpen],
          ['AI Assistant Coach', 'Ask for a simpler explanation, a hint, or a different example.', Bot],
          ['Progress signals', 'Weekly hours, confidence, and completed work in one honest picture.', TrendingUp],
          ['Secure and Private', 'Your learning profile belongs to you. Fully synchronized with your backend.', LockKeyhole],
        ].map(([head, body, Icon], i) => (
          <div key={head as string} className={`rounded-2xl border border-[#dce4da] p-7 ${i === 0 ? 'bg-[#203d38] text-[#f8f5eb]' : 'bg-[#fbfaf5]'}`}>
            <span className={`grid size-11 place-items-center rounded-xl ${i === 0 ? 'bg-[#edbc55] text-[#20322f]' : 'bg-[#e3eee7] text-[#176b65]'}`}>
              <Icon size={21} />
            </span>
            <h2 className={`display mt-8 text-2xl font-bold ${i === 0 ? 'text-[#f8f5eb]' : 'text-[#20322f]'}`}>{head as string}</h2>
            <p className={`mt-3 text-sm leading-7 ${i === 0 ? 'text-[#c6d7cc]' : 'text-[#718079]'}`}>{body as string}</p>
          </div>
        ))}
      </div>
    </PublicPage>
  );
}

function About() {
  return (
    <PublicPage eyebrow="Why we made this" title={<>Less noise. More <span className="text-[#176b65]">becoming.</span></>}>
      <div className="mt-16 grid gap-10 md:grid-cols-[1fr_1.3fr]">
        <div className="rounded-3xl bg-[#edbc55] p-8">
          <Sparkles className="text-[#20322f]" />
          <p className="display mt-24 text-3xl font-bold leading-tight text-[#20322f]">
            The hard part of learning is rarely finding one more thing to read.
          </p>
        </div>
        <div className="space-y-6 text-lg leading-9 text-[#61716c]">
          <p>LearnPath started with a simple frustration: learners spend too much energy deciding what to learn and too little energy practicing the work they care about.</p>
          <p>We believe a good learning product should feel like a thoughtful coach. It should remember your context, point to the next challenge, and explain its reasoning.</p>
          <p className="font-bold text-[#20322f]">The goal is not to finish a catalog. It is to become capable.</p>
        </div>
      </div>
    </PublicPage>
  );
}

// ─── App Router ───────────────────────────────────────────────────────────────

function AppRouter() {
  return (
    <Switch>
      {/* Public Marketing */}
      <Route path="/" component={Landing} />
      <Route path="/how-it-works" component={HowItWorks} />
      <Route path="/features" component={Features} />
      <Route path="/about" component={About} />

      {/* Authentication */}
      <Route path="/login"><AuthPage /></Route>
      <Route path="/register"><AuthPage register /></Route>
      <Route path="/onboarding" component={OnboardingSkills} />

      {/* Administrator Control Center */}
      <Route path="/admin/login" component={AdminLogin} />
      <Route path="/admin/dashboard" component={AdminDashboard} />
      <Route path="/admin/users"><AdminModule module="users" /></Route>
      <Route path="/admin/learning-paths"><AdminModule module="learning-paths" /></Route>
      <Route path="/admin/skills"><AdminModule module="skills" /></Route>
      <Route path="/admin/assessments"><AdminModule module="assessments" /></Route>
      <Route path="/admin/resources"><AdminModule module="resources" /></Route>
      <Route path="/admin/ai-controls"><AdminModule module="ai-controls" /></Route>
      <Route path="/admin/analytics"><AdminModule module="analytics" /></Route>
      <Route path="/admin/notifications"><AdminModule module="notifications" /></Route>
      <Route path="/admin/audit"><AdminModule module="audit" /></Route>
      <Route path="/admin/settings"><AdminModule module="settings" /></Route>

      {/* Authenticated Learner Portal */}
      <Route path="/dashboard"><AppShell><Dashboard /></AppShell></Route>
      <Route path="/learning-path"><AppShell><LearningPath /></AppShell></Route>
      <Route path="/learning-path/:phaseId"><AppShell><PhaseDetail /></AppShell></Route>
      <Route path="/resources"><AppShell><Resources /></AppShell></Route>
      <Route path="/projects"><AppShell><Projects /></AppShell></Route>
      <Route path="/skills"><AppShell><Skills /></AppShell></Route>
      <Route path="/progress"><AppShell><ProgressPage /></AppShell></Route>
      <Route path="/assessments"><AppShell><Assessments /></AppShell></Route>
      <Route path="/assistant"><AppShell><Assistant /></AppShell></Route>
      <Route path="/profile"><AppShell><ProfilePage /></AppShell></Route>
      <Route path="/settings"><AppShell><ProfilePage settings /></AppShell></Route>
      <Route path="/notifications"><AppShell><NotificationsPage /></AppShell></Route>

      {/* Catch-all 404 */}
      <Route component={NotFound} />
    </Switch>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
            <ErrorBoundary>
              <AppRouter />
            </ErrorBoundary>
          </WouterRouter>
          <Toaster />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
