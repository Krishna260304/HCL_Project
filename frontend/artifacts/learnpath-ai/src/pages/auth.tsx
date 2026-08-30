import React, { useState } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowRight, Compass, ShieldCheck, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

function Logo({ light = false }: { light?: boolean }) {
  return (
    <Link href="/" className={`flex items-center gap-2.5 font-bold tracking-tight ${light ? 'text-[#f8f5eb]' : 'text-[#20322f]'}`}>
      <span className="grid size-8 place-items-center rounded-[10px] bg-[#e9ae3d] text-[#20322f]">
        <Compass size={18} strokeWidth={2.5} />
      </span>
      <span className="text-[17px] font-extrabold tracking-tight">learnpath<span className="text-[#d69323]">.</span>ai</span>
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
      const msg = err instanceof Error ? err.message : 'Authentication failed. Please check your credentials.';
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
          <p className="font-mono text-xs uppercase tracking-[.2em] text-[#edbc55]">Your route, made visible</p>
          <h1 className="mt-5 max-w-md text-6xl font-bold leading-[.92] tracking-[-.06em]">
            Small steps. Serious <span className="text-[#edbc55]">momentum.</span>
          </h1>
          <p className="mt-6 max-w-md leading-7 text-[#bfd1c4]">
            LearnPath connects your skills, career goals, and realistic time commitments to generate an adaptive AI curriculum you can trust.
          </p>
        </div>
        <div className="flex items-center justify-between text-xs text-[#8da99b]">
          <span className="font-mono">LEARNPATH AI / PLATFORM</span>
          <span>Adaptive Skill Engine</span>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex flex-col bg-[#f7f5ed] px-6 py-8 md:px-16 justify-center">
        <div className="lg:hidden mb-6">
          <Logo />
        </div>

        <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center">
          <p className="font-mono text-xs uppercase tracking-[.18em] text-[#b17820]">
            {register ? 'Create your learner account' : 'Welcome back'}
          </p>
          <h1 className="mt-3 text-4xl font-bold tracking-[-.04em] text-[#20322f]">
            {register ? 'Build a path that fits.' : 'Pick up where you left off.'}
          </h1>
          <p className="mt-3 text-sm leading-6 text-[#718079]">
            {register
              ? 'Tell us a little more about yourself so your recommendations are tailored from day one.'
              : 'Sign in to access your active learning phases, checkpoints, and projects.'}
          </p>

          {error && (
            <div className="mt-6 flex items-start gap-3 rounded-xl border border-[#f5d5d0] bg-[#fdf5f4] p-4 text-xs font-semibold text-[#a04b3e]">
              <AlertCircle size={17} className="shrink-0 text-[#a04b3e]" />
              <div className="flex-1">{error}</div>
            </div>
          )}

          <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
            {register && (
              <label className="block text-sm font-bold text-[#36504a]">
                Your full name
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="Enter your full name"
                  className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-3.5 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10"
                  data-testid="input-name"
                />
              </label>
            )}

            <label className="block text-sm font-bold text-[#36504a]">
              Email address
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                type="email"
                required
                placeholder="Enter your email address"
                className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-3.5 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10"
                data-testid="input-email"
              />
            </label>

            <label className="block text-sm font-bold text-[#36504a]">
              Password
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                required
                placeholder="••••••••"
                className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-3.5 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10"
                data-testid="input-password"
              />
            </label>

            {register && (
              <>
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="block text-sm font-bold text-[#36504a]">
                    Current role
                    <input
                      value={currentRole}
                      onChange={(e) => setCurrentRole(e.target.value)}
                      placeholder="Enter your current role"
                      className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-3 text-sm outline-none focus:border-[#176b65]"
                      data-testid="input-role"
                    />
                  </label>
                  <label className="block text-sm font-bold text-[#36504a]">
                    Experience
                    <select
                      value={experience}
                      onChange={(e) => setExperience(e.target.value)}
                      required
                      className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-3 py-3 text-sm outline-none focus:border-[#176b65]"
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

                <label className="block text-sm font-bold text-[#36504a]">
                  Target career destination
                  <input
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    required
                    placeholder="Enter your target career role"
                    className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-3 text-sm outline-none focus:border-[#176b65]"
                    data-testid="input-registration-goal"
                  />
                </label>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#176b65] px-5 py-3.5 text-sm font-bold text-[#f7f5ed] shadow-[0_10px_22px_rgba(23,107,101,.18)] hover:bg-[#115a55] disabled:opacity-50 disabled:cursor-not-allowed transition"
              data-testid="button-auth-submit"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  {register ? 'Creating account…' : 'Signing in…'}
                </>
              ) : (
                <>
                  {register ? 'Create account & continue' : 'Sign in to LearnPath'}
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {!register && (
            <>
              <div className="my-5 flex items-center gap-3 text-xs text-[#a1ada7]">
                <span className="h-px flex-1 bg-[#dce4da]" />
                or
                <span className="h-px flex-1 bg-[#dce4da]" />
              </div>
              <Link
                href="/admin/login"
                className="flex w-full items-center justify-center gap-2 rounded-xl border border-[#ccd8ce] bg-[#f7f5ed] px-4 py-3 text-sm font-bold text-[#36504a] transition hover:border-[#176b65] hover:bg-[#eef5ef]"
                data-testid="link-admin-login"
              >
                <ShieldCheck size={16} className="text-[#176b65]" /> Platform Administrator Sign In
              </Link>
            </>
          )}

          <p className="mt-8 text-center text-sm text-[#718079]">
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
