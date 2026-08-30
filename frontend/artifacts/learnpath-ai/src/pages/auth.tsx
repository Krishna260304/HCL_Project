import React, { useState } from 'react';
import { Link, useLocation } from 'wouter';
import {
  ArrowRight,
  Compass,
  ShieldCheck,
  AlertCircle,
  Loader2,
  Zap,
  Sparkles,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { authService } from '@/services/authService';

function Logo({ light = false }: { light?: boolean }) {
  return (
    <Link
      href="/"
      className={`flex items-center gap-2.5 font-bold tracking-tight ${
        light ? 'text-[#f8f5eb]' : 'text-[#20322f]'
      }`}
    >
      <span className="grid size-8 place-items-center rounded-[10px] bg-[#e9ae3d] text-[#20322f]">
        <Compass size={18} strokeWidth={2.5} />
      </span>
      <span className="text-[17px] font-extrabold tracking-tight font-[Space_Grotesk,sans-serif]">
        learnpath<span className="text-[#d69323]">.</span>ai
      </span>
    </Link>
  );
}

export default function AuthPage({ register = false }: { register?: boolean }) {
  const [, setLocation] = useLocation();
  const { login, register: registerUser, user, isAuthenticated } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [currentRole, setCurrentRole] = useState('');
  const [goal, setGoal] = useState('');
  const [experience, setExperience] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If already authenticated, redirect
  React.useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'admin') {
        setLocation('/admin/dashboard');
      } else {
        setLocation('/dashboard');
      }
    }
  }, [isAuthenticated, user, setLocation]);

  const handleDemoLogin = async (persona: 'alex' | 'maya') => {
    setLoading(true);
    setError(null);
    try {
      authService.loginAsDemoLearner();
      setLocation('/dashboard');
    } catch {
      setError('Unable to initialize demo persona session.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (register) {
        if (!name.trim()) {
          throw new Error('Please enter your full name.');
        }
        if (!currentRole.trim()) {
          throw new Error('Please enter your current role.');
        }
        if (!experience) {
          throw new Error('Please select your experience level.');
        }
        if (!goal.trim()) {
          throw new Error('Please enter your target career role.');
        }
        const experienceLevel = experience === 'beginner'
          ? 'beginner'
          : experience.startsWith('intermediate') ? 'intermediate' : 'advanced';
        const authUser = await registerUser({
          email: email.trim(),
          password,
          name: name.trim(),
          current_role: currentRole.trim(),
          experience_level: experienceLevel,
          target_outcome: goal.trim(),
        });
        if (authUser.role === 'admin') {
          setLocation('/admin/dashboard');
        } else {
          setLocation('/onboarding');
        }
      } else {
        const authUser = await login(email.trim(), password);
        if (authUser.role === 'admin') {
          setLocation('/admin/dashboard');
        } else {
          setLocation('/dashboard');
        }
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Authentication failed. Please check your credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-[100dvh] lg:grid-cols-[.9fr_1.1fr]">
      {/* Left branding panel */}
      <div className="hidden bg-[#203d38] p-10 text-[#f8f5eb] lg:flex lg:flex-col lg:justify-between">
        <Logo light />
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-[#294b44] px-3 py-1 text-xs font-bold text-[#edbc55] border border-[#3b635a]">
            <Sparkles size={13} /> Adaptive Curriculum Intelligence
          </div>
          <h1 className="mt-5 max-w-md text-5xl xl:text-6xl font-bold leading-[.95] tracking-[-.05em]">
            Small steps. Serious <span className="text-[#edbc55]">momentum.</span>
          </h1>
          <p className="mt-6 max-w-md leading-relaxed text-[#bfd1c4] text-sm">
            LearnPath connects your skills, career goals, and realistic time commitments to generate an adaptive AI curriculum with verifiable proof of competence.
          </p>
        </div>
        <div className="flex items-center justify-between text-xs text-[#8da99b] font-mono">
          <span>LEARNPATH AI / PLATFORM</span>
          <span>v2.0 MVP</span>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex flex-col bg-[#f7f5ed] px-6 py-8 md:px-16 justify-center">
        <div className="lg:hidden mb-6">
          <Logo />
        </div>

        <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center py-6">
          {/* Header */}
          <div>
            <p className="font-mono text-xs uppercase tracking-[.18em] text-[#b17820]">
              {register ? 'Create your learner account' : 'Welcome back'}
            </p>
            <h2 className="mt-2 text-3xl md:text-4xl font-bold tracking-[-.04em] text-[#20322f]">
              {register ? 'Build a path that fits.' : 'Sign in to your path.'}
            </h2>
            <p className="mt-2 text-xs leading-5 text-[#718079]">
              {register
                ? 'Tell us your background so recommendations are tailored from day one.'
                : 'Access your active phases, checkpoint projects, and diagnostic scores.'}
            </p>
          </div>

          {/* 1-Click Fast Evaluator Demo Presets Card */}
          <div className="mt-6 rounded-2xl border border-[#cbe0d3] bg-[#eef6f0] p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 font-bold text-xs text-[#176b65]">
                <Zap size={14} className="text-[#edbc55]" /> Evaluator 1-Click Demo Profiles:
              </span>
              <span className="font-mono text-[10px] text-[#718079]">Instant Login</span>
            </div>

            <div className="space-y-2">
              <button
                type="button"
                onClick={() => handleDemoLogin('alex')}
                disabled={loading}
                className="w-full flex items-center justify-between p-2.5 rounded-xl border border-[#cbd5ce] bg-white text-left hover:border-[#176b65] transition shadow-2xs group"
              >
                <div>
                  <p className="text-xs font-bold text-[#20322f] group-hover:text-[#176b65] transition">
                    🚀 Alex Rivera — Full-Stack & AI Architect
                  </p>
                  <p className="text-[10px] text-[#718079]">
                    Frontend background · Phase 3 Active · 10 hrs/week
                  </p>
                </div>
                <ChevronRight size={14} className="text-[#88958e] group-hover:text-[#176b65]" />
              </button>

              <button
                type="button"
                onClick={() => handleDemoLogin('maya')}
                disabled={loading}
                className="w-full flex items-center justify-between p-2.5 rounded-xl border border-[#cbd5ce] bg-white text-left hover:border-[#176b65] transition shadow-2xs group"
              >
                <div>
                  <p className="text-xs font-bold text-[#20322f] group-hover:text-[#176b65] transition">
                    🎓 Maya Chen — Machine Learning & LLMs
                  </p>
                  <p className="text-[10px] text-[#718079]">
                    CS graduate · Python & PyTorch · 15 hrs/week
                  </p>
                </div>
                <ChevronRight size={14} className="text-[#88958e] group-hover:text-[#176b65]" />
              </button>
            </div>
          </div>

          <div className="my-5 flex items-center gap-3 text-xs text-[#a1ada7]">
            <span className="h-px flex-1 bg-[#dce4da]" />
            or continue with credentials
            <span className="h-px flex-1 bg-[#dce4da]" />
          </div>

          {error && (
            <div className="mb-4 flex items-start gap-3 rounded-xl border border-[#f5d5d0] bg-[#fdf5f4] p-3 text-xs font-semibold text-[#a04b3e]">
              <AlertCircle size={16} className="shrink-0 text-[#a04b3e]" />
              <div className="flex-1">{error}</div>
            </div>
          )}

          {/* Form */}
          <form className="space-y-3.5" onSubmit={handleSubmit}>
            {register && (
              <label className="block text-xs font-bold text-[#36504a]">
                Full Name
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="e.g. Alex Rivera"
                  className="mt-1.5 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-xs outline-none focus:border-[#176b65]"
                  data-testid="input-name"
                />
              </label>
            )}

            <label className="block text-xs font-bold text-[#36504a]">
              Email address
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                type="email"
                required
                placeholder="you@example.com"
                className="mt-1.5 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-xs outline-none focus:border-[#176b65]"
                data-testid="input-email"
              />
            </label>

            <label className="block text-xs font-bold text-[#36504a]">
              Password
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                required
                placeholder="••••••••"
                className="mt-1.5 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-xs outline-none focus:border-[#176b65]"
                data-testid="input-password"
              />
            </label>

            {register && (
              <>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block text-xs font-bold text-[#36504a]">
                    Current role
                    <input
                      value={currentRole}
                      onChange={(e) => setCurrentRole(e.target.value)}
                      placeholder="e.g. Frontend Developer"
                      className="mt-1.5 w-full rounded-xl border border-[#ccd8ce] bg-white px-3 py-2.5 text-xs outline-none focus:border-[#176b65]"
                      data-testid="input-role"
                    />
                  </label>
                  <label className="block text-xs font-bold text-[#36504a]">
                    Experience
                    <select
                      value={experience}
                      onChange={(e) => setExperience(e.target.value)}
                      required
                      className="mt-1.5 w-full rounded-xl border border-[#ccd8ce] bg-white px-3 py-2.5 text-xs outline-none focus:border-[#176b65]"
                      data-testid="select-experience"
                    >
                      <option value="">Select experience</option>
                      <option value="beginner">Just starting</option>
                      <option value="intermediate_1_2">1–2 years</option>
                      <option value="intermediate_3_5">3–5 years</option>
                      <option value="advanced">5+ years</option>
                    </select>
                  </label>
                </div>

                <label className="block text-xs font-bold text-[#36504a]">
                  Target career destination
                  <input
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    required
                    placeholder="e.g. Full-Stack Web & AI Architect"
                    className="mt-1.5 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-xs outline-none focus:border-[#176b65]"
                    data-testid="input-registration-goal"
                  />
                </label>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#176b65] px-5 py-3 text-xs font-bold text-[#f7f5ed] shadow-sm hover:bg-[#115a55] disabled:opacity-50 transition"
              data-testid="button-auth-submit"
            >
              {loading ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  {register ? 'Creating account…' : 'Signing in…'}
                </>
              ) : (
                <>
                  {register ? 'Create account & start onboarding' : 'Sign in to LearnPath'}
                  <ArrowRight size={15} />
                </>
              )}
            </button>
          </form>

          {!register && (
            <div className="mt-4 text-center">
              <Link
                href="/admin/login"
                className="inline-flex items-center gap-1.5 text-xs font-bold text-[#61716c] hover:text-[#176b65] transition"
                data-testid="link-admin-login"
              >
                <ShieldCheck size={14} className="text-[#176b65]" /> Administrator Portal
              </Link>
            </div>
          )}

          <p className="mt-6 text-center text-xs text-[#718079]">
            {register ? 'Already have a path?' : 'New to LearnPath?'}{' '}
            <Link
              href={register ? '/login' : '/register'}
              className="font-bold text-[#176b65] hover:underline"
              data-testid="link-auth-switch"
            >
              {register ? 'Sign in' : 'Create an account'}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
