import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { profileService, userService, type LearnerProfile } from '@/services/index';
import { Check, Clock3, Bell, Sparkles, ShieldCheck, UserRound, ArrowRight, Loader2 } from 'lucide-react';
import { SkeletonCard, ErrorState } from '@/components/states';

export default function ProfilePage({ settings = false }: { settings?: boolean }) {
  const { user } = useAuth();
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form fields
  const [name, setName] = useState('');
  const [currentRole, setCurrentRole] = useState('');
  const [education, setEducation] = useState('');
  const [timeline, setTimeline] = useState('');
  const [availableHours, setAvailableHours] = useState(8);
  const [goal, setGoal] = useState('');
  const [motivation, setMotivation] = useState('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const p = await profileService.getProfile();
      setProfile(p);
      setName(p.name || user?.email?.split('@')[0] || '');
      setCurrentRole(p.current_role || '');
      setEducation(p.education || '');
      setTimeline(p.timeline || '');
      setAvailableHours(p.available_hours || 8);
      setGoal(p.goals?.[0] || '');
      setMotivation(p.motivation || '');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load your profile.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);

    try {
      const updated = await profileService.updateProfile({
        name,
        current_role: currentRole,
        education,
        timeline,
        available_hours: Number(availableHours),
        goals: goal ? [goal] : [],
        motivation,
      });
      setProfile(updated);
      setEditing(false);
      setMessage('Profile successfully updated.');
      setTimeout(() => setMessage(null), 4000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save changes.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-5">
        <SkeletonCard rows={3} />
      </div>
    );
  }

  if (error && !profile) {
    return <ErrorState title="Profile error" message={error} onRetry={load} />;
  }

  if (settings) {
    return (
      <>
        <div className="mb-8 animate-rise">
          <p className="font-mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Preferences & Settings</p>
          <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Settings</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[#718079]">Tune your pace, notification preferences, and adaptive recommendations.</p>
        </div>

        {message && (
          <div className="mb-5 rounded-xl bg-[#dceee4] p-4 text-xs font-bold text-[#176b65]">
            {message}
          </div>
        )}

        <div className="grid gap-5 lg:grid-cols-[1fr_280px]">
          <section className="divide-y divide-[#e4e9e2] rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] shadow-sm">
            <div className="flex items-center gap-4 p-6">
              <span className="grid size-10 place-items-center rounded-xl bg-[#e3eee7] text-[#176b65]">
                <Clock3 size={18} />
              </span>
              <div className="flex-1">
                <p className="text-sm font-bold">Weekly study target</p>
                <p className="mt-1 text-xs text-[#83918a]">Current: {profile?.available_hours ?? 8} hours per week</p>
              </div>
              <span className="rounded-lg border border-[#ccd8ce] px-3 py-2 text-xs font-bold text-[#40534d]">
                {profile?.available_hours ?? 8} hrs/wk
              </span>
            </div>

            <div className="flex items-center gap-4 p-6">
              <span className="grid size-10 place-items-center rounded-xl bg-[#e3eee7] text-[#176b65]">
                <Bell size={18} />
              </span>
              <div className="flex-1">
                <p className="text-sm font-bold">Real-time Push Notifications</p>
                <p className="mt-1 text-xs text-[#83918a]">Receive updates on recommendations and assessments</p>
              </div>
              <span className="rounded-full bg-[#dceee4] px-3 py-1 text-xs font-bold text-[#176b65]">
                Enabled
              </span>
            </div>

            <div className="flex items-center gap-4 p-6">
              <span className="grid size-10 place-items-center rounded-xl bg-[#e3eee7] text-[#176b65]">
                <Sparkles size={18} />
              </span>
              <div className="flex-1">
                <p className="text-sm font-bold">Adaptive AI Path Adjustments</p>
                <p className="mt-1 text-xs text-[#83918a]">Dynamically recalculate path milestones as you pass checkpoints</p>
              </div>
              <span className="rounded-full bg-[#dceee4] px-3 py-1 text-xs font-bold text-[#176b65]">
                Active
              </span>
            </div>
          </section>

          <section className="h-fit rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
            <ShieldCheck className="text-[#176b65]" size={20} />
            <h2 className="display mt-4 text-xl font-bold">Account Security</h2>
            <p className="mt-2 text-xs leading-5 text-[#718079]">
              Signed in as <strong>{user?.email}</strong> with role <strong>{user?.role}</strong>.
            </p>
          </section>
        </div>
      </>
    );
  }

  const initials = (profile?.name || user?.email || 'LP')
    .split(' ')
    .map(w => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-5 animate-rise">
        <div>
          <p className="font-mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Your learning identity</p>
          <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">{profile?.name || user?.email}</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[#718079]">The context behind your personalized AI path.</p>
        </div>
        {!editing && (
          <button
            onClick={() => setEditing(true)}
            className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-sm font-bold text-white hover:bg-[#115a55] transition"
            data-testid="button-edit-profile"
          >
            Edit profile <ArrowRight size={14} />
          </button>
        )}
      </div>

      {message && (
        <div className="mb-5 rounded-xl bg-[#dceee4] p-4 text-xs font-bold text-[#176b65]">
          {message}
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 text-center shadow-sm">
          <span className="mx-auto grid size-24 place-items-center rounded-[2rem] bg-[#edbc55] text-2xl font-bold text-[#20322f]">
            {initials}
          </span>
          <h2 className="display mt-5 text-2xl font-bold">{profile?.name || user?.email?.split('@')[0]}</h2>
          <p className="mt-1 text-sm text-[#718079]">{profile?.current_role || 'Active Learner'}</p>
          <p className="mt-0.5 text-xs text-[#8da99b]">{user?.email}</p>

          <div className="mt-6 flex justify-center gap-4 text-center border-t border-[#e4e9e2] pt-5">
            <div>
              <p className="font-mono text-lg font-bold text-[#176b65]">{profile?.available_hours || 8}h</p>
              <p className="text-[10px] text-[#83918a]">weekly time</p>
            </div>
            <div>
              <p className="font-mono text-lg font-bold text-[#176b65]">{profile?.experience_level || 'Active'}</p>
              <p className="text-[10px] text-[#83918a]">level</p>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-6 shadow-sm">
          {editing ? (
            <form onSubmit={handleSave} className="space-y-4">
              <p className="font-mono text-[10px] uppercase tracking-widest text-[#b17820]">Edit profile details</p>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm font-bold text-[#36504a]">
                  Full name
                  <input
                    value={name}
                    onChange={e => setName(e.target.value)}
                    required
                    className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#f9f9f3] px-4 py-3 text-sm outline-none focus:border-[#176b65]"
                    data-testid="input-profile-name"
                  />
                </label>

                <label className="block text-sm font-bold text-[#36504a]">
                  Current role
                  <input
                    value={currentRole}
                    onChange={e => setCurrentRole(e.target.value)}
                    placeholder="e.g. Developer, Student"
                    className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#f9f9f3] px-4 py-3 text-sm outline-none focus:border-[#176b65]"
                    data-testid="input-profile-role"
                  />
                </label>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm font-bold text-[#36504a]">
                  Target career destination
                  <input
                    value={goal}
                    onChange={e => setGoal(e.target.value)}
                    placeholder="e.g. AI Engineer"
                    className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#f9f9f3] px-4 py-3 text-sm outline-none focus:border-[#176b65]"
                    data-testid="input-profile-goal"
                  />
                </label>

                <label className="block text-sm font-bold text-[#36504a]">
                  Available hours / week
                  <input
                    type="number"
                    min="1"
                    max="80"
                    value={availableHours}
                    onChange={e => setAvailableHours(Number(e.target.value))}
                    className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-[#f9f9f3] px-4 py-3 text-sm outline-none focus:border-[#176b65]"
                  />
                </label>
              </div>

              <label className="block text-sm font-bold text-[#36504a]">
                Motivation & About you
                <textarea
                  value={motivation}
                  onChange={e => setMotivation(e.target.value)}
                  rows={4}
                  placeholder="Share what drives you to learn and any specific background."
                  className="mt-2 w-full resize-none rounded-xl border border-[#ccd8ce] bg-[#f9f9f3] px-4 py-3 text-sm outline-none focus:border-[#176b65]"
                  data-testid="textarea-profile-about"
                />
              </label>

              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-5 py-2.5 text-sm font-bold text-white hover:bg-[#115a55] disabled:opacity-50 transition"
                >
                  {saving ? <Loader2 size={16} className="animate-spin" /> : null}
                  {saving ? 'Saving…' : 'Save profile'}
                </button>
                <button
                  type="button"
                  onClick={() => setEditing(false)}
                  className="rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-4 py-2.5 text-sm font-bold text-[#36504a] hover:border-[#176b65] transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <>
              <p className="font-mono text-[10px] uppercase tracking-widest text-[#b17820]">Profile Summary</p>
              <div className="mt-5 grid gap-5 md:grid-cols-2">
                <div>
                  <p className="text-xs text-[#9aa7a0]">Destination</p>
                  <p className="mt-1 text-sm font-bold text-[#40534d]">{profile?.goals?.[0] || 'Not specified'}</p>
                </div>
                <div>
                  <p className="text-xs text-[#9aa7a0]">Current Role</p>
                  <p className="mt-1 text-sm font-bold text-[#40534d]">{profile?.current_role || 'Not specified'}</p>
                </div>
                <div>
                  <p className="text-xs text-[#9aa7a0]">Available Study Time</p>
                  <p className="mt-1 text-sm font-bold text-[#40534d]">{profile?.available_hours || 8} hours / week</p>
                </div>
                <div>
                  <p className="text-xs text-[#9aa7a0]">Experience Level</p>
                  <p className="mt-1 text-sm font-bold text-[#40534d] capitalize">{profile?.experience_level || 'Beginner'}</p>
                </div>
              </div>

              {profile?.motivation && (
                <div className="mt-6 rounded-xl bg-[#eef2ea] p-4">
                  <p className="text-xs font-bold text-[#40534d]">About & Motivation</p>
                  <p className="mt-1 text-sm leading-6 text-[#61716c]">{profile.motivation}</p>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </>
  );
}
