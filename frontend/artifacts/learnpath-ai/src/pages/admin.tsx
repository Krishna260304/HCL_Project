import { useEffect, useState } from 'react';
import {
  Activity, AlertTriangle, ArrowRight, Bell, BookOpen, Bot, Check, CheckCircle2, ChevronDown,
  Code2, Database, FileText, Flame, Gauge, LayoutDashboard, Lock, LogOut, Menu, MessageSquare,
  MoreHorizontal, Play, Plus, RefreshCw, Search, Settings, Shield, ShieldCheck, SlidersHorizontal,
  ToggleLeft, ToggleRight, Trash2, TrendingUp, Users, Workflow, X, Zap,
} from 'lucide-react';
import { Link, useLocation } from 'wouter';
import { useAuth } from '@/context/AuthContext';
import { adminService } from '@/services';

const adminNav = [
  { slug: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { slug: 'users', label: 'Users', icon: Users },
  { slug: 'learning', label: 'Learning content', icon: BookOpen },
  { slug: 'learning-paths', label: 'Learning paths', icon: Workflow },
  { slug: 'skills', label: 'Skills', icon: Code2 },
  { slug: 'assessments', label: 'Assessments', icon: CheckCircle2 },
  { slug: 'resources', label: 'Resources', icon: Database },
  { slug: 'recommendations', label: 'Recommendations', icon: SlidersHorizontal },
  { slug: 'ai-controls', label: 'AI controls', icon: Bot },
  { slug: 'analytics', label: 'Analytics', icon: Activity },
  { slug: 'notifications', label: 'Notifications', icon: Bell },
  { slug: 'audit', label: 'Audit logs', icon: Shield },
  { slug: 'settings', label: 'Settings', icon: Settings },
] as const;
type Slug = typeof adminNav[number]['slug'];

const displayMetric = (value: unknown): string => value === undefined || value === null || value === '' ? '—' : typeof value === 'number' ? value.toLocaleString() : String(value);

const dashStats: Array<{ label: string; value: string; delta: string; color: string }> = [];

// ─── Shared UI ────────────────────────────────────────────────────────────────

const Badge = ({ children, green = false, yellow = false, red = false, blue = false }: { children: React.ReactNode; green?: boolean; yellow?: boolean; red?: boolean; blue?: boolean }) => {
  const cls = green ? 'bg-[#dceee4] text-[#176b65]' : yellow ? 'bg-[#fae9bb] text-[#93611a]' : red ? 'bg-[#fbe9e5] text-[#a04b3e]' : blue ? 'bg-[#dde8f7] text-[#2b5faa]' : 'bg-[#edf0eb] text-[#5a6b64]';
  return <span className={`inline-flex rounded-full px-2.5 py-0.5 text-[10px] font-bold ${cls}`}>{children}</span>;
};
const Btn = ({ children, small = false, outline = false, danger = false, onClick }: { children: React.ReactNode; small?: boolean; outline?: boolean; danger?: boolean; onClick?: () => void }) => (
  <button onClick={onClick} className={`inline-flex items-center gap-1.5 rounded-xl font-bold transition ${small ? 'px-3 py-1.5 text-xs' : 'px-4 py-2.5 text-sm'} ${danger ? 'bg-[#fbe9e5] text-[#a04b3e] hover:bg-[#f5d0ca]' : outline ? 'border border-[#ccd8ce] bg-[#fafbf8] text-[#36504a] hover:border-[#176b65]' : 'bg-[#176b65] text-[#f7f5ed] hover:bg-[#115a55]'}`}>{children}</button>
);
const THead = ({ cols }: { cols: string[] }) => <thead className="bg-[#f3f6f1] text-[10px] uppercase tracking-wider text-[#83918a]"><tr>{cols.map(c => <th key={c} className="px-4 py-3 text-left font-bold">{c}</th>)}</tr></thead>;
const CardWrap = ({ title, sub, action, className = '', children }: { title: string; sub?: string; action?: React.ReactNode; className?: string; children: React.ReactNode }) => (
  <section className={`overflow-hidden rounded-2xl border border-[#dbe4da] bg-[#fafbf8] shadow-sm ${className}`}>
    {(title || action) && <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#e4e9e2] px-6 py-4"><div><h2 className="text-lg font-bold text-[#1f312e]">{title}</h2>{sub && <p className="mt-0.5 text-xs text-[#83918a]">{sub}</p>}</div>{action}</div>}
    {children}
  </section>
);

// ─── Admin login ──────────────────────────────────────────────────────────────

function AdminLogin() {
  const [, setLocation] = useLocation();
  const { login, logout, isAdmin, loading: authLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => { if (!authLoading && isAdmin) setLocation('/admin/dashboard'); }, [authLoading, isAdmin, setLocation]);
  return (
    <div className="grid min-h-[100dvh] place-items-center bg-[#f4f6f1] px-5">
      <div className="w-full max-w-md rounded-3xl border border-[#dbe4da] bg-[#fafbf8] p-8 shadow-[0_20px_70px_rgba(42,67,57,.08)] md:p-10">
        <div className="flex items-center gap-3">
          <span className="grid size-11 place-items-center rounded-2xl bg-[#176b65] text-white"><ShieldCheck size={22} /></span>
          <div><p className="font-bold text-[#1f312e]">LearnPath AI</p><p className="font-mono text-[9px] uppercase tracking-widest text-[#89968f]">Admin control center</p></div>
        </div>
        <p className="mt-10 font-mono text-[10px] uppercase tracking-[.18em] text-[#b17820]">Restricted access</p>
        <h1 className="mt-3 text-4xl font-bold tracking-[-.05em] text-[#1f312e]">Administrator sign in</h1>
        <p className="mt-3 text-sm leading-6 text-[#718079]">This area is reserved for platform administrators only. There is no public admin registration.</p>
        <form className="mt-8 space-y-4" onSubmit={async e => { e.preventDefault(); setError(''); setSubmitting(true); try { const user = await login(email, password); if (user.role !== 'admin') { await logout(); throw new Error('This account does not have administrator access.'); } setLocation('/admin/dashboard'); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to sign in.'); } finally { setSubmitting(false); } }}>
          <label className="block text-sm font-bold text-[#36504a]">Email<input value={email} onChange={e => setEmail(e.target.value)} type="email" className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-3 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10" /></label>
          <label className="block text-sm font-bold text-[#36504a]">Password<input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="••••••••" autoComplete="current-password" className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-3 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10" /></label>
          <label className="flex items-center gap-2 text-xs text-[#718079]"><input type="checkbox" className="accent-[#176b65]" /> Remember me</label>
          {error && <p className="rounded-xl bg-[#fbe9e5] px-4 py-3 text-xs font-bold text-[#a04b3e]">{error}</p>}
          <button disabled={submitting} className="w-full rounded-xl bg-[#176b65] px-4 py-3 text-sm font-bold text-white hover:bg-[#115a55] disabled:cursor-wait disabled:opacity-60">{submitting ? 'Signing in…' : 'Sign in'} <ArrowRight size={15} className="ml-1 inline" /></button>
        </form>
        <button className="mt-5 w-full text-center text-xs font-bold text-[#176b65]">Forgot password?</button>
        <Link href="/" className="mt-8 block text-center text-xs font-bold text-[#83918a] hover:text-[#36504a]">← Return to learner site</Link>
      </div>
    </div>
  );
}

// ─── Admin shell ──────────────────────────────────────────────────────────────

function AdminShell({ children, active }: { children: React.ReactNode; active: Slug | string }) {
  const [, setLocation] = useLocation();
  const { isAdmin, loading: authLoading, logout } = useAuth();
  const [drawer, setDrawer] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => { if (!authLoading && !isAdmin) setLocation('/admin/login'); }, [authLoading, isAdmin, setLocation]);
  if (authLoading || !isAdmin) return <div className="grid min-h-[100dvh] place-items-center bg-[#f3f6f1] text-sm text-[#60746d]">Checking administrator session…</div>;

  const Sidebar = () => (
    <aside className={`flex h-full flex-col bg-[#172e29] py-4 text-[#e7f0e8] transition-all ${collapsed ? 'w-[70px]' : 'w-[256px]'}`}>
      <div className={`flex items-center gap-3 px-4 py-2 ${collapsed ? 'justify-center' : ''}`}>
        <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-[#e8b044] text-[#172e29]"><ShieldCheck size={18} /></span>
        {!collapsed && <span><span className="block text-sm font-bold">LearnPath AI</span><span className="font-mono text-[9px] uppercase tracking-widest text-[#7fa898]">Control center</span></span>}
        {!collapsed && <button onClick={() => setCollapsed(true)} className="ml-auto rounded-lg p-1 text-[#7fa898] hover:text-white"><X size={14} /></button>}
      </div>
      {collapsed && <button onClick={() => setCollapsed(false)} className="mx-auto mt-1 rounded-lg p-1.5 text-[#7fa898] hover:text-white"><Menu size={15} /></button>}
      <nav className="mt-5 flex-1 space-y-0.5 px-2">
        {adminNav.map(({ slug, label, icon: Icon }) => (
          <Link key={slug} href={`/admin/${slug}`} onClick={() => setDrawer(false)}
            className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-bold transition-colors ${active === slug ? 'bg-[#e8b044] text-[#172e29]' : 'text-[#a8c6b8] hover:bg-[#243f39] hover:text-white'} ${collapsed ? 'justify-center' : ''}`}
            title={collapsed ? label : ''}>
            <Icon size={16} className="shrink-0" />
            {!collapsed && label}
          </Link>
        ))}
      </nav>
      <button onClick={async () => { await logout(); setLocation('/admin/login'); }} className={`mx-2 mt-2 flex items-center gap-2 rounded-xl px-3 py-2.5 text-xs font-bold text-[#a8c6b8] hover:bg-[#243f39] hover:text-white ${collapsed ? 'justify-center' : ''}`}>
        <LogOut size={15} />{!collapsed && 'Log out'}
      </button>
    </aside>
  );

  return (
    <div className="flex min-h-[100dvh] bg-[#f3f6f1] text-[#1f312e]">
      <div className="hidden lg:sticky lg:top-0 lg:flex lg:h-screen lg:shrink-0"><Sidebar /></div>
      {drawer && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setDrawer(false)} />
          <div className="relative h-full w-[256px] flex"><Sidebar /></div>
        </div>
      )}
      <div className="flex flex-1 flex-col min-w-0">
        <header className="sticky top-0 z-30 flex h-[68px] shrink-0 items-center gap-4 border-b border-[#dbe4da] bg-[#f3f6f1]/90 px-5 backdrop-blur-md">
          <button onClick={() => setDrawer(true)} className="rounded-lg p-2 lg:hidden"><Menu size={19} /></button>
          <div className="hidden items-center gap-2 text-xs text-[#718079] sm:flex">
            <span className="font-mono text-[10px] uppercase tracking-widest text-[#b17820]">Admin</span>
            <span>/</span>
            <span className="font-bold text-[#36504a]">{adminNav.find(n => n.slug === active)?.label || 'Control Center'}</span>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <label className="hidden items-center gap-2 rounded-xl border border-[#ccd8ce] bg-white px-3 py-2 md:flex">
              <Search size={15} className="text-[#89968f]" /><input placeholder="Search platform…" className="w-44 bg-transparent text-xs outline-none" />
            </label>
            <button className="relative rounded-xl p-2.5 text-[#60746d] hover:bg-[#e4ebe2]"><Bell size={18} /><span className="absolute right-2 top-2 size-1.5 rounded-full bg-[#e8b044]" /></button>
            <span className="flex items-center gap-1.5 rounded-xl border border-[#ccd8ce] bg-white px-3 py-2 text-xs font-bold text-[#36504a]"><span className="size-2 rounded-full bg-[#176b65]" />Operational</span>
            <span className="grid size-9 place-items-center rounded-xl bg-[#e8b044] text-xs font-bold text-[#172e29]">AD</span>
          </div>
        </header>
        <main className="flex-1 p-5 lg:p-8 max-w-[1440px] w-full mx-auto">{children}</main>
      </div>
    </div>
  );
}

// ─── Admin dashboard ──────────────────────────────────────────────────────────

function AdminDashboard() {
  const [analytics, setAnalytics] = useState<any | null>(null);
  const [analyticsError, setAnalyticsError] = useState('');
  useEffect(() => {
    adminService.getAnalyticsOverview().then(setAnalytics).catch(err => setAnalyticsError(err instanceof Error ? err.message : 'Live analytics unavailable.'));
  }, []);
  const users = analytics?.users ?? {};
  const catalog = analytics?.catalog ?? {};
  const assessments = analytics?.assessments ?? {};
  const pathsMetrics = analytics?.learning_paths ?? {};
  const stats = analytics ? [
    ['Total learners', users.learners ?? 0, '#176b65'],
    ['Active users', users.active ?? 0, '#176b65'],
    ['Paths generated', pathsMetrics.total ?? 0, '#176b65'],
    ['Resources live', catalog.resources ?? 0, '#176b65'],
    ['Assessments taken', assessments.attempts ?? 0, '#176b65'],
    ['AI conversations', analytics.ai_conversations ?? '—', '#d89c2c'],
    ['Skills in catalog', catalog.skills ?? 0, '#176b65'],
    ['Projects shipped', catalog.projects ?? 0, '#176b65'],
  ].map(([label, value, color]) => ({ label, value: displayMetric(value), delta: 'Live', color })) : dashStats;
  const activities = analytics?.recent_activities ?? [];
  return (
    <AdminShell active="dashboard">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">System overview</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Platform Control Center</h1><p className="mt-2 text-sm text-[#718079]">Monitor and control the LearnPath AI platform.</p></div>
        <span className="flex items-center gap-2 rounded-full bg-[#dceee4] px-4 py-2 text-xs font-bold text-[#176b65]"><span className="size-2 animate-pulse rounded-full bg-[#176b65]" />All systems operational</span>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map(({ label, value, delta }) => (
          <div key={label} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5 shadow-sm">
            <p className="text-xs text-[#83918a]">{label}</p>
            <p className="mt-3 font-mono text-3xl font-medium text-[#1f312e]">{value}</p>
            <p className="mt-2 text-xs font-bold text-[#176b65]">{delta} this month</p>
          </div>
        ))}
      </div>
      {analyticsError && <p className="mt-4 rounded-xl bg-[#fae9bb] px-4 py-3 text-xs font-bold text-[#93611a]">{analyticsError} Showing a safe empty state until the API is available.</p>}
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.35fr_.65fr]">
        <CardWrap title="Platform activity" sub="Real-time control plane events">
          <div className="divide-y divide-[#edf0eb]">
            {activities.length === 0 && <p className="px-6 py-8 text-sm text-[#83918a]">No recent activity recorded.</p>}
            {activities.map((a: any, i: number) => (
              <div key={`${a.event}-${i}`} className="flex items-center gap-4 px-6 py-4">
                <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-[#e8f1ec] text-[#176b65]"><CheckCircle2 size={16} /></span>
                <div className="flex-1 min-w-0"><p className="truncate text-sm font-bold">{a.event}</p><p className="mt-0.5 text-[10px] text-[#89968f]">{a.time} · {a.actor}</p></div>
                <ArrowRight size={14} className="shrink-0 text-[#c0ccbf]" />
              </div>
            ))}
          </div>
        </CardWrap>
        <CardWrap title="System health" sub="Frontend service monitor">
          <div className="divide-y divide-[#edf0eb]">
            {['Frontend UI', 'API gateway', 'AI service', 'Vector DB', 'Recommendation engine', 'Resource discovery'].map((svc, i) => (
              <div key={svc} className="flex items-center justify-between px-6 py-3.5">
                <span className="text-sm font-bold">{svc}</span>
                <Badge green={i < 4} yellow={i === 4}>{i === 4 ? 'Degraded' : 'Operational'}</Badge>
              </div>
            ))}
          </div>
        </CardWrap>
      </div>
    </AdminShell>
  );
}

// ─── Admin modules ────────────────────────────────────────────────────────────

function UsersModule() {
  const [query, setQuery] = useState('');
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [selected, setSelected] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    adminService.listUsers({ page_size: 100 }).then(users => {
      if (cancelled) return;
      setItems(users.map((u: any) => ({
        ...u,
        name: u.name || u.email,
        status: String(u.status || 'active').replace('_', ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
        goal: u.goal || 'Not set',
        experience: u.experience || 'Not set',
        progress: u.progress || 0,
        joined: u.created_at ? new Date(u.created_at).toLocaleDateString() : '—',
        lastActive: u.last_login_at ? new Date(u.last_login_at).toLocaleDateString() : '—',
      })));
    }).catch(err => { if (!cancelled) setLoadError(err instanceof Error ? err.message : 'Unable to load users.'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);
  const toggle = async (id: string) => {
    const current = items.find(u => u.id === id);
    if (!current) return;
    const next = current.status === 'Active' ? 'suspended' : 'active';
    try {
      await adminService.updateUserStatus(id, next);
      setItems(c => c.map(u => u.id === id ? { ...u, status: next === 'active' ? 'Active' : 'Suspended' } : u));
    } catch (err) { setLoadError(err instanceof Error ? err.message : 'Unable to update user.'); }
  };
  const rows = items.filter(u => `${u.name} ${u.email} ${u.goal}`.toLowerCase().includes(query.toLowerCase()));
  const user = items.find(u => u.id === selected);
  return (
    <AdminShell active="users">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">User management</h1><p className="mt-2 text-sm text-[#718079]">View, search, filter and manage all learner accounts.</p></div>
        <Btn><Plus size={14} />Add learner</Btn>
      </div>
      {selected && user ? (
        <div className="mt-7">
          <button onClick={() => setSelected(null)} className="mb-5 flex items-center gap-2 text-sm font-bold text-[#176b65]">← Back to all users</button>
          <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
            <CardWrap title={user.name}>
              <div className="p-5 space-y-3 text-sm">
                <div><p className="text-xs text-[#83918a]">Email</p><p className="font-bold">{user.email}</p></div>
                <div><p className="text-xs text-[#83918a]">Goal</p><p className="font-bold">{user.goal}</p></div>
                <div><p className="text-xs text-[#83918a]">Experience</p><p className="font-bold">{user.experience}</p></div>
                <div><p className="text-xs text-[#83918a]">Status</p><Badge green={user.status === 'Active'} red={user.status === 'Suspended'}>{user.status}</Badge></div>
                <div><p className="text-xs text-[#83918a]">Progress</p><div className="mt-1.5 h-2 rounded-full bg-[#e3e9e1]"><div className="h-full rounded-full bg-[#176b65]" style={{ width: `${user.progress}%` }} /></div><p className="mt-1 text-xs text-[#718079]">{user.progress}%</p></div>
                <div><p className="text-xs text-[#83918a]">Joined</p><p className="font-bold">{user.joined}</p></div>
                <div><p className="text-xs text-[#83918a]">Last active</p><p className="font-bold">{user.lastActive}</p></div>
              </div>
              <div className="border-t border-[#e4e9e2] p-5 space-y-2">
                <Btn outline small onClick={() => toggle(user.id)}>{user.status === 'Active' ? 'Suspend account' : 'Reactivate account'}</Btn>
                <Btn danger small><Trash2 size={13} />Delete account</Btn>
              </div>
            </CardWrap>
            <div className="space-y-5">
              <CardWrap title="Learning path" sub="Current progress across all phases">
                <div className="divide-y divide-[#edf0eb]">
                  {([] as Array<[string, number, string]>).map(([ph, pct, st]) => (
                    <div key={ph as string} className="flex items-center gap-4 px-6 py-3.5">
                      <span className="flex-1 text-sm font-bold text-[#40534d]">{ph as string}</span>
                      <div className="w-28 h-1.5 rounded-full bg-[#e3e9e1]"><div className="h-full rounded-full bg-[#176b65]" style={{ width: `${pct}%` }} /></div>
                      <Badge green={st === 'Complete'} yellow={st === 'Current'}>{st as string}</Badge>
                    </div>
                  ))}
                </div>
              </CardWrap>
              <CardWrap title="Assessment history">
                <div className="divide-y divide-[#edf0eb]">
                  {([] as Array<[string, number | null, string]>).map(([t, s, st]) => (
                    <div key={t as string} className="flex items-center gap-4 px-6 py-3.5">
                      <span className="flex-1 text-sm font-bold text-[#40534d]">{t as string}</span>
                      <span className="font-mono text-sm">{s ? `${s}%` : '—'}</span>
                      <Badge green={st === 'Passed'}>{st as string}</Badge>
                    </div>
                  ))}
                </div>
              </CardWrap>
            </div>
          </div>
        </div>
      ) : (
        <CardWrap title="" action={
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 rounded-xl border border-[#ccd8ce] bg-white px-3 py-2"><Search size={14} className="text-[#89968f]" /><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search learners" className="bg-transparent text-sm outline-none w-44" /></label>
            <span className="text-xs text-[#83918a]">{rows.length} learner{rows.length !== 1 ? 's' : ''}</span>
          </div>
        } className="mt-7">
          {loadError && <p className="m-4 rounded-xl bg-[#fbe9e5] px-4 py-3 text-xs font-bold text-[#a04b3e]">{loadError}</p>}
          {loading && <p className="px-6 py-10 text-sm text-[#83918a]">Loading users…</p>}
          {!loading && !loadError && rows.length === 0 && <p className="px-6 py-10 text-sm text-[#83918a]">No users found.</p>}
          <div className="overflow-auto">
            <table className="w-full min-w-[820px] text-left text-sm">
              <THead cols={['Learner', 'Goal', 'Experience', 'Status', 'Progress', 'Joined', 'Last active', 'Actions']} />
              <tbody className="divide-y divide-[#edf0eb]">
                {rows.map(u => (
                  <tr key={u.id} className="hover:bg-[#f5f7f3]">
                    <td className="px-4 py-3.5"><p className="font-bold">{u.name}</p><p className="mt-0.5 text-[10px] text-[#83918a]">{u.email}</p></td>
                    <td className="px-4 py-3.5 text-[#53665f]">{u.goal}</td>
                    <td className="px-4 py-3.5 text-[#53665f]">{u.experience}</td>
                    <td className="px-4 py-3.5"><Badge green={u.status === 'Active'} red={u.status === 'Suspended'} yellow={u.status === 'Inactive'}>{u.status}</Badge></td>
                    <td className="px-4 py-3.5 font-mono text-xs">{u.progress}%</td>
                    <td className="px-4 py-3.5 text-xs text-[#83918a]">{u.joined}</td>
                    <td className="px-4 py-3.5 text-xs text-[#83918a]">{u.lastActive}</td>
                    <td className="px-4 py-3.5">
                      <div className="flex gap-2">
                        <Btn small outline onClick={() => setSelected(u.id)}>View</Btn>
                        <Btn small danger onClick={() => toggle(u.id)}>{u.status === 'Active' ? 'Suspend' : 'Activate'}</Btn>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardWrap>
      )}
    </AdminShell>
  );
}

function LearningModule() {
  const [courses, setCourses] = useState<any[]>([]);
  useEffect(() => { adminService.adminListCourses().then(rows => setCourses(rows.map((c: any) => ({ ...c, skills: c.skills || [], category: c.category || '—', difficulty: c.difficulty || '—', duration: c.duration || '—', resources: c.resources || 0, updated: c.updated_at ? new Date(c.updated_at).toLocaleDateString() : '—', status: c.status === 'published' ? 'Published' : 'Draft' })))).catch(() => setCourses([])); }, []);
  const toggle = (id: string) => setCourses(c => c.map(x => x.id === id ? { ...x, status: x.status === 'Published' ? 'Draft' : 'Published' } : x));
  return (
    <AdminShell active="learning">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Learning content</h1><p className="mt-2 text-sm text-[#718079]">Create, publish, and manage all learning content types.</p></div>
        <Btn><Plus size={14} />New course</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Courses', courses.length.toLocaleString()], ['Videos', '—'], ['Articles', '—'], ['Projects', '—']].map(([l, v]) => (
          <div key={l} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5"><p className="text-xs text-[#83918a]">{l}</p><p className="mt-2 font-mono text-3xl text-[#1f312e]">{v}</p></div>
        ))}
      </div>
      <CardWrap title="Course catalog" sub="All courses — published, draft, and archived" action={<Btn outline small><RefreshCw size={13} />Refresh</Btn>} className="mt-5">
        <div className="overflow-auto">
          <table className="w-full min-w-[860px] text-left text-sm">
            <THead cols={['Course', 'Category', 'Difficulty', 'Skills', 'Duration', 'Resources', 'Status', 'Actions']} />
            <tbody className="divide-y divide-[#edf0eb]">
              {courses.map(c => (
                <tr key={c.id} className="hover:bg-[#f5f7f3]">
                  <td className="px-4 py-3.5"><p className="font-bold">{c.title}</p><p className="mt-0.5 text-[10px] text-[#83918a]">Updated {c.updated}</p></td>
                  <td className="px-4 py-3.5 text-[#53665f]">{c.category}</td>
                  <td className="px-4 py-3.5"><Badge blue={c.difficulty === 'Advanced'} green={c.difficulty === 'Beginner'} yellow={c.difficulty === 'Intermediate'}>{c.difficulty}</Badge></td>
                  <td className="px-4 py-3.5"><div className="flex flex-wrap gap-1">{c.skills.map((s: string) => <Badge key={s}>{s}</Badge>)}</div></td>
                  <td className="px-4 py-3.5 text-xs text-[#718079]">{c.duration}</td>
                  <td className="px-4 py-3.5 font-mono text-xs">{c.resources}</td>
                  <td className="px-4 py-3.5"><Badge green={c.status === 'Published'} yellow={c.status === 'Draft'}>{c.status}</Badge></td>
                  <td className="px-4 py-3.5"><div className="flex gap-2"><Btn small outline onClick={() => toggle(c.id)}>{c.status === 'Published' ? 'Unpublish' : 'Publish'}</Btn></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardWrap>
    </AdminShell>
  );
}

function LearningPathsModule() {
  const [paths, setPaths] = useState<any[]>([]);
  useEffect(() => { adminService.listLearningPaths().then(rows => setPaths(rows.map((p: any) => ({ ...p, id: p.id || p._id, goal: p.goal || p.title || '—', learner: p.learner || p.user_id || '—', progress: p.progress || 0, phases: p.phases?.length || 0, status: p.status || '—', created: p.created_at ? new Date(p.created_at).toLocaleDateString() : '—' })))).catch(() => setPaths([])); }, []);
  return (
    <AdminShell active="learning-paths">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Learning paths</h1><p className="mt-2 text-sm text-[#718079]">View, edit, and manage all AI-generated learning paths.</p></div>
        <Btn><Plus size={14} />Build path</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Total paths', paths.length.toLocaleString()], ['Active', paths.filter(p => p.status === 'active').length.toLocaleString()], ['Completed', paths.filter(p => p.status === 'completed').length.toLocaleString()], ['Archived', paths.filter(p => p.status === 'archived').length.toLocaleString()]].map(([l, v]) => (
          <div key={l} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5"><p className="text-xs text-[#83918a]">{l}</p><p className="mt-2 font-mono text-3xl text-[#1f312e]">{v}</p></div>
        ))}
      </div>
      <CardWrap title="All learning paths" sub="Learner paths — generated and manual" action={<Btn outline small>Export CSV</Btn>} className="mt-5">
        <div className="overflow-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <THead cols={['Goal', 'Learner', 'Progress', 'Phases', 'Status', 'Created', 'Actions']} />
            <tbody className="divide-y divide-[#edf0eb]">
              {paths.map(p => (
                <tr key={p.id} className="hover:bg-[#f5f7f3]">
                  <td className="px-4 py-3.5 font-bold">{p.goal}</td>
                  <td className="px-4 py-3.5 text-[#53665f]">{p.learner}</td>
                  <td className="px-4 py-3.5">
                    <div className="flex items-center gap-2"><div className="w-16 h-1.5 rounded-full bg-[#e3e9e1]"><div className="h-full rounded-full bg-[#176b65]" style={{ width: `${p.progress}%` }} /></div><span className="font-mono text-xs">{p.progress}%</span></div>
                  </td>
                  <td className="px-4 py-3.5 font-mono text-xs">{p.phases}</td>
                  <td className="px-4 py-3.5"><Badge green={p.status === 'Active'} red={p.status === 'Suspended'}>{p.status}</Badge></td>
                  <td className="px-4 py-3.5 text-xs text-[#83918a]">{p.created}</td>
                  <td className="px-4 py-3.5"><div className="flex gap-2"><Btn small outline>View</Btn><Btn small outline><RefreshCw size={12} />Regen</Btn></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardWrap>
    </AdminShell>
  );
}

function SkillsModule() {
  const [skills, setSkills] = useState<any[]>([]);
  useEffect(() => { adminService.adminListSkills({}).then(rows => setSkills(rows.map((s: any) => ({ ...s, name: s.name || s.title || s.id, learners: s.learners || 0, related: s.related || [], status: s.status === 'disabled' ? 'Disabled' : 'Active' })))).catch(() => setSkills([])); }, []);
  const toggleSkill = (name: string) => setSkills(c => c.map(s => s.name === name ? { ...s, status: s.status === 'Active' ? 'Disabled' : 'Active' } : s));
  return (
    <AdminShell active="skills">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Skill management</h1><p className="mt-2 text-sm text-[#718079]">Control the complete CS skill taxonomy powering recommendations and assessments.</p></div>
        <Btn><Plus size={14} />New skill</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Total skills', skills.length.toLocaleString()], ['Active', skills.filter(s => s.status === 'Active').length.toLocaleString()], ['Disabled', skills.filter(s => s.status === 'Disabled').length.toLocaleString()], ['Categories', new Set(skills.map(s => s.category).filter(Boolean)).size.toLocaleString()]].map(([l, v]) => (
          <div key={l} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5"><p className="text-xs text-[#83918a]">{l}</p><p className="mt-2 font-mono text-3xl text-[#1f312e]">{v}</p></div>
        ))}
      </div>
      <CardWrap title="Skill catalog" sub="Full taxonomy — searchable, editable" action={<Btn outline small>Export taxonomy</Btn>} className="mt-5">
        <div className="overflow-auto">
          <table className="w-full min-w-[700px] text-left text-sm">
            <THead cols={['Skill', 'Category', 'Difficulty', 'Learners using', 'Related skills', 'Status', 'Actions']} />
            <tbody className="divide-y divide-[#edf0eb]">
              {skills.map(s => (
                <tr key={s.name} className="hover:bg-[#f5f7f3]">
                  <td className="px-4 py-3.5 font-bold">{s.name}</td>
                  <td className="px-4 py-3.5 text-[#53665f]">{s.category}</td>
                  <td className="px-4 py-3.5"><Badge blue={s.difficulty === 'Advanced'} green={s.difficulty === 'Beginner'} yellow={s.difficulty === 'Intermediate'}>{s.difficulty}</Badge></td>
                  <td className="px-4 py-3.5 font-mono text-xs">{s.learners.toLocaleString()}</td>
                  <td className="px-4 py-3.5"><div className="flex flex-wrap gap-1">{s.related.map((r: string) => <Badge key={r}>{r}</Badge>)}</div></td>
                  <td className="px-4 py-3.5"><Badge green={s.status === 'Active'} red={s.status === 'Disabled'}>{s.status}</Badge></td>
                  <td className="px-4 py-3.5"><div className="flex gap-2"><Btn small outline>Edit</Btn><button onClick={() => toggleSkill(s.name)} className="rounded-lg p-1.5 text-[#83918a] hover:text-[#1f312e]">{s.status === 'Active' ? <ToggleRight size={16} className="text-[#176b65]" /> : <ToggleLeft size={16} />}</button></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardWrap>
    </AdminShell>
  );
}

function AssessmentsModule() {
  const [items, setItems] = useState<any[]>([]);
  useEffect(() => { adminService.adminListAssessments({}).then(rows => setItems(rows.map((a: any) => ({ ...a, name: a.name || a.title || a.id, questions: a.questions || a.questions_count || 0, avgScore: a.avgScore || a.average_score || 0, attempts: a.attempts || 0, status: a.status === 'published' ? 'Published' : 'Draft' })))).catch(() => setItems([])); }, []);
  const toggle = (id: string) => setItems(c => c.map(a => a.id === id ? { ...a, status: a.status === 'Published' ? 'Draft' : 'Published' } : a));
  return (
    <AdminShell active="assessments">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Assessment management</h1><p className="mt-2 text-sm text-[#718079]">Build, publish, and track all platform assessments and question banks.</p></div>
        <Btn><Plus size={14} />New assessment</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Total assessments', items.length.toLocaleString()], ['Published', items.filter(a => a.status === 'Published').length.toLocaleString()], ['Average score', items.length ? `${Math.round(items.reduce((sum, a) => sum + Number(a.avgScore || 0), 0) / items.length)}%` : '—'], ['Total attempts', items.reduce((sum, a) => sum + Number(a.attempts || 0), 0).toLocaleString()]].map(([l, v]) => (
          <div key={l} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5"><p className="text-xs text-[#83918a]">{l}</p><p className="mt-2 font-mono text-3xl text-[#1f312e]">{v}</p></div>
        ))}
      </div>
      <CardWrap title="Assessment library" sub="All checkpoints and practice assessments" action={<Btn outline small>Export results</Btn>} className="mt-5">
        <div className="overflow-auto">
          <table className="w-full min-w-[700px] text-left text-sm">
            <THead cols={['Assessment', 'Skill', 'Difficulty', 'Questions', 'Avg score', 'Attempts', 'Status', 'Actions']} />
            <tbody className="divide-y divide-[#edf0eb]">
              {items.map(a => (
                <tr key={a.id} className="hover:bg-[#f5f7f3]">
                  <td className="px-4 py-3.5 font-bold">{a.name}</td>
                  <td className="px-4 py-3.5 text-[#53665f]">{a.skill}</td>
                  <td className="px-4 py-3.5"><Badge yellow={a.difficulty === 'Stretch'} green={a.difficulty === 'Core'}>{a.difficulty}</Badge></td>
                  <td className="px-4 py-3.5 font-mono text-xs">{a.questions}</td>
                  <td className="px-4 py-3.5 font-mono text-xs">{a.avgScore}%</td>
                  <td className="px-4 py-3.5 font-mono text-xs">{a.attempts.toLocaleString()}</td>
                  <td className="px-4 py-3.5"><Badge green={a.status === 'Published'} yellow={a.status === 'Draft'}>{a.status}</Badge></td>
                  <td className="px-4 py-3.5"><div className="flex gap-2"><Btn small outline>Edit</Btn><Btn small outline onClick={() => toggle(a.id)}>{a.status === 'Published' ? 'Unpublish' : 'Publish'}</Btn></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardWrap>
    </AdminShell>
  );
}

function ResourcesModule() {
  const [items, setItems] = useState<any[]>([]);
  useEffect(() => { adminService.adminListResources({}).then(rows => setItems(rows.map((r: any) => ({ ...r, source: r.source || r.provider || '—', type: r.type || '—', skill: r.skill || r.skills?.join(', ') || '—', quality: r.quality || r.quality_score || 0, status: r.status === 'pending_review' ? 'Pending' : 'Approved' })))).catch(() => setItems([])); }, []);
  const approve = (id: string) => setItems(c => c.map(r => r.id === id ? { ...r, status: 'Approved' } : r));
  const reject = (id: string) => setItems(c => c.filter(r => r.id !== id));
  return (
    <AdminShell active="resources">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Resource management</h1><p className="mt-2 text-sm text-[#718079]">Approve, reject, and curate all external learning resources.</p></div>
        <Btn><Plus size={14} />Add resource</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Total resources', items.length.toLocaleString()], ['Approved', items.filter(r => r.status === 'Approved').length.toLocaleString()], ['Pending review', items.filter(r => r.status === 'Pending').length.toLocaleString()], ['Quality avg', items.length ? `${Math.round(items.reduce((sum, r) => sum + Number(r.quality || 0), 0) / items.length)}%` : '—']].map(([l, v]) => (
          <div key={l} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5"><p className="text-xs text-[#83918a]">{l}</p><p className="mt-2 font-mono text-3xl text-[#1f312e]">{v}</p></div>
        ))}
      </div>
      {items.some(r => r.status === 'Pending') && (
        <div className="mt-5 rounded-2xl border border-[#f7d9a0] bg-[#fdf6e7] p-5">
          <div className="flex items-center gap-2 mb-4"><AlertTriangle size={16} className="text-[#b17820]" /><p className="text-sm font-bold text-[#7a5618]">Resources awaiting approval</p></div>
          {items.filter(r => r.status === 'Pending').map(r => (
            <div key={r.id} className="flex flex-wrap items-center gap-3 rounded-xl border border-[#f0d090] bg-white p-4 mb-2 last:mb-0">
              <div className="flex-1 min-w-0"><p className="font-bold text-sm text-[#1f312e]">{r.title}</p><p className="mt-0.5 text-xs text-[#83918a]">{r.source} · {r.type} · Skill: {r.skill} · Quality score: {r.quality}</p></div>
              <div className="flex gap-2"><Btn small onClick={() => approve(r.id)}><Check size={13} />Approve</Btn><Btn small danger onClick={() => reject(r.id)}><X size={13} />Reject</Btn></div>
            </div>
          ))}
        </div>
      )}
      <CardWrap title="Resource library" sub="All curated and approved resources" action={<Btn outline small>Export list</Btn>} className="mt-5">
        <div className="overflow-auto">
          <table className="w-full min-w-[700px] text-left text-sm">
            <THead cols={['Resource', 'Source', 'Type', 'Skill', 'Quality', 'Status', 'Actions']} />
            <tbody className="divide-y divide-[#edf0eb]">
              {items.map(r => (
                <tr key={r.id} className="hover:bg-[#f5f7f3]">
                  <td className="px-4 py-3.5 font-bold">{r.title}</td>
                  <td className="px-4 py-3.5 text-[#53665f]">{r.source}</td>
                  <td className="px-4 py-3.5"><Badge>{r.type}</Badge></td>
                  <td className="px-4 py-3.5 text-[#53665f]">{r.skill}</td>
                  <td className="px-4 py-3.5 font-mono text-xs">{r.quality}</td>
                  <td className="px-4 py-3.5"><Badge green={r.status === 'Approved'} yellow={r.status === 'Pending'}>{r.status}</Badge></td>
                  <td className="px-4 py-3.5"><div className="flex gap-2"><Btn small outline>Edit</Btn><Btn small danger onClick={() => reject(r.id)}><Trash2 size={12} /></Btn></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardWrap>
    </AdminShell>
  );
}

function RecommendationsModule() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  useEffect(() => { adminService.listRecommendations({}).then(setRecommendations).catch(() => setRecommendations([])); }, []);
  const weights = [
    { label: 'Skill gap match', key: 'gap', value: 30 }, { label: 'Semantic similarity', key: 'sem', value: 20 },
    { label: 'Prerequisite match', key: 'pre', value: 15 }, { label: 'Difficulty match', key: 'dif', value: 10 },
    { label: 'Goal alignment', key: 'goal', value: 10 }, { label: 'Learning preference', key: 'pref', value: 5 },
    { label: 'Resource quality', key: 'qual', value: 5 }, { label: 'Historical feedback', key: 'hist', value: 5 },
  ];
  const [saved, setSaved] = useState(false);
  return (
    <AdminShell active="recommendations">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Recommendations</h1><p className="mt-2 text-sm text-[#718079]">Configure recommendation engine weights and monitor delivery.</p></div>
      </div>
      <div className="mt-7 grid gap-5 xl:grid-cols-[1.4fr_.6fr]">
        <CardWrap title="Recent recommendations" sub="Last 48 hours across all learners">
          <div className="overflow-auto">
            <table className="w-full min-w-[600px] text-left text-sm">
              <THead cols={['Learner', 'Resource', 'Skill', 'Reason', 'Score', 'Status']} />
              <tbody className="divide-y divide-[#edf0eb]">
                {recommendations.map(r => (
                  <tr key={r.learner + r.resource} className="hover:bg-[#f5f7f3]">
                    <td className="px-4 py-3.5 font-bold">{r.learner}</td>
                    <td className="px-4 py-3.5 text-[#53665f]">{r.resource}</td>
                    <td className="px-4 py-3.5"><Badge>{r.skill}</Badge></td>
                    <td className="px-4 py-3.5 text-xs text-[#718079]">{r.reason}</td>
                    <td className="px-4 py-3.5 font-mono text-xs">{r.score}%</td>
                    <td className="px-4 py-3.5"><Badge green={r.status === 'Accepted'} yellow={r.status === 'Skipped'}>{r.status}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardWrap>
        <CardWrap title="Engine weights" sub="Must total 100%">
          <div className="p-5 space-y-3">
            {weights.map(w => (
              <div key={w.key}>
                <div className="flex justify-between text-xs mb-1"><span className="font-bold text-[#40534d]">{w.label}</span><span className="font-mono text-[#83918a]">{w.value}%</span></div>
                <div className="h-2 rounded-full bg-[#e3e9e1]"><div className="h-full rounded-full bg-[#176b65]" style={{ width: `${w.value * 3}%` }} /></div>
              </div>
            ))}
            <div className="flex items-center justify-between pt-3 border-t border-[#e4e9e2]">
              <span className="text-xs font-bold text-[#83918a]">Total: <span className="text-[#176b65]">100%</span></span>
              <Btn small onClick={() => setSaved(true)}>{saved ? <><Check size={12} />Saved</> : 'Save weights'}</Btn>
            </div>
          </div>
        </CardWrap>
      </div>
    </AdminShell>
  );
}

function AIControlsModule() {
  const [enabled, setEnabled] = useState({ assistant: true, pathGen: true, assessment: true, resAnalysis: true });
  const [aiStats, setAiStats] = useState<any | null>(null);
  useEffect(() => { Promise.all([adminService.getAnalyticsOverview(), adminService.listFeatureFlags()]).then(([metrics, flags]) => { setAiStats(metrics); if (Array.isArray(flags)) setEnabled(current => ({ ...current, ...Object.fromEntries(flags.map((f: any) => [f.name || f.key, Boolean(f.enabled)])) })); }).catch(() => undefined); }, []);
  const [temp, setTemp] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [saved, setSaved] = useState(false);
  return (
    <AdminShell active="ai-controls">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">AI control center</h1><p className="mt-2 text-sm text-[#718079]">Configure AI model, prompts, and safety settings for the entire platform.</p></div>
      </div>
      <div className="mt-7 grid gap-5 xl:grid-cols-2">
        <CardWrap title="AI model configuration" sub="Platform-wide AI model settings">
          <div className="p-5 space-y-5">
            <div className="flex items-center justify-between rounded-xl bg-[#f0f4ee] px-5 py-4">
              <div><p className="text-xs text-[#83918a]">Current model</p><p className="font-bold text-[#1f312e]">Qwen 2.5-72B</p></div>
              <Badge green>Operational</Badge>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2"><label className="font-bold text-[#36504a]">Temperature</label><span className="font-mono text-[#83918a]">{temp}</span></div>
              <input type="range" min={0} max={1} step={0.1} value={temp} onChange={e => setTemp(parseFloat(e.target.value))} className="w-full accent-[#176b65]" />
              <div className="flex justify-between text-xs text-[#83918a] mt-1"><span>Conservative (0)</span><span>Creative (1)</span></div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2"><label className="font-bold text-[#36504a]">Max tokens</label><span className="font-mono text-[#83918a]">{maxTokens}</span></div>
              <input type="range" min={512} max={8192} step={256} value={maxTokens} onChange={e => setMaxTokens(parseInt(e.target.value))} className="w-full accent-[#176b65]" />
            </div>
            <Btn onClick={() => setSaved(true)}>{saved ? <><Check size={14} />Settings saved</> : 'Save configuration'}</Btn>
          </div>
        </CardWrap>
        <CardWrap title="AI feature toggles" sub="Enable or disable AI capabilities platform-wide">
          <div className="divide-y divide-[#edf0eb]">
            {([['assistant', 'AI Learning assistant', 'Path coach and Q&A'], ['pathGen', 'AI Path generation', 'Personalized learning paths'], ['assessment', 'AI Assessment generation', 'Dynamic question creation'], ['resAnalysis', 'Resource analysis', 'AI content curation']] as const).map(([key, label, sub]) => (
              <div key={key} className="flex items-center justify-between px-6 py-4">
                <div><p className="text-sm font-bold">{label}</p><p className="mt-0.5 text-xs text-[#83918a]">{sub}</p></div>
                <button onClick={() => setEnabled(e => ({ ...e, [key]: !e[key] }))} className={`relative h-6 w-11 rounded-full transition-colors ${enabled[key] ? 'bg-[#176b65]' : 'bg-[#d4dbd1]'}`}>
                  <span className={`absolute top-1 size-4 rounded-full bg-white shadow transition-transform ${enabled[key] ? 'left-6' : 'left-1'}`} />
                </button>
              </div>
            ))}
          </div>
        </CardWrap>
      </div>
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.2fr_.8fr]">
        <CardWrap title="Prompt library" sub="Active prompt templates for all AI features">
          <div className="divide-y divide-[#edf0eb]">
            {['Goal analysis', 'Assessment generation', 'Resource analysis', 'Path generation', 'AI assistant system'].map((p, i) => (
              <div key={p} className="flex items-center justify-between px-6 py-4">
                <div><p className="text-sm font-bold">{p}</p><p className="mt-0.5 text-xs text-[#83918a]">v1.{i + 2} · Active</p></div>
                <div className="flex gap-2"><Btn small outline>Edit</Btn><Btn small outline>History</Btn></div>
              </div>
            ))}
          </div>
        </CardWrap>
        <CardWrap title="RAG configuration" sub="Vector database and retrieval settings">
          <div className="divide-y divide-[#edf0eb]">
            {[['Documents indexed', aiStats?.catalog?.resources?.toLocaleString() ?? '—'], ['Embeddings', '—'], ['Vector DB status', aiStats ? 'Operational' : '—'], ['Last indexed', '—'], ['Search quality', '—']].map(([label, val]) => (
              <div key={label} className="flex justify-between px-6 py-3.5">
                <span className="text-sm text-[#83918a]">{label}</span>
                <span className="text-sm font-bold">{val}</span>
              </div>
            ))}
            <div className="px-6 py-4"><Btn small outline><RefreshCw size={13} />Re-index now</Btn></div>
          </div>
        </CardWrap>
      </div>
    </AdminShell>
  );
}

function AnalyticsModule() {
  const [analytics, setAnalytics] = useState<any | null>(null);
  useEffect(() => { adminService.getAnalyticsOverview().then(setAnalytics).catch(() => setAnalytics(null)); }, []);
  const weeks: string[] = analytics?.weeks ?? [];
  const signups: number[] = analytics?.weekly_signups ?? [];
  const active: number[] = analytics?.weekly_active ?? [];
  const maxVal = Math.max(...signups);
  return (
    <AdminShell active="analytics">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Platform analytics</h1><p className="mt-2 text-sm text-[#718079]">Understand learner engagement, path completion, and platform usage.</p></div>
        <Btn outline><TrendingUp size={14} />Export report</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Learners', analytics?.users?.learners ?? '—', 'Live'], ['Active users', analytics?.users?.active ?? '—', 'Live'], ['Completed paths', analytics?.learning_paths?.completed ?? '—', 'Live'], ['Average assessment score', analytics?.assessments?.average_score != null ? `${analytics.assessments.average_score}%` : '—', 'Live']].map(([l, v, d]) => (
          <div key={l} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5"><p className="text-xs text-[#83918a]">{l}</p><p className="mt-2 font-mono text-3xl text-[#1f312e]">{v}</p><p className="mt-2 text-xs font-bold text-[#176b65]">{d} vs last period</p></div>
        ))}
      </div>
      <CardWrap title="Learner signups and active users" sub="Weekly trend · last 8 weeks" className="mt-5">
        <div className="p-6">
          <div className="flex gap-4 mb-5 text-xs"><span className="flex items-center gap-1.5"><i className="size-2 rounded-full bg-[#176b65]" />Signups</span><span className="flex items-center gap-1.5"><i className="size-2 rounded-full bg-[#e8b044]" />Active</span></div>
          <div className="flex items-end gap-2 h-44 border-b border-l border-[#dbe4da]">
            {weeks.length === 0 && <p className="p-8 text-sm text-[#83918a]">No analytics data recorded yet.</p>}
            {weeks.map((w, i) => (
              <div key={w} className="flex flex-1 flex-col items-center gap-1">
                <div className="flex items-end gap-1 flex-1">
                  <div className="w-4 rounded-t bg-[#176b65] opacity-80" style={{ height: `${(signups[i] / maxVal) * 140}px` }} />
                  <div className="w-4 rounded-t bg-[#e8b044] opacity-80" style={{ height: `${(active[i] / maxVal) * 140}px` }} />
                </div>
                <span className="text-[9px] text-[#9aa7a0] rotate-[-35deg] origin-top-right mt-1">{w.slice(4)}</span>
              </div>
            ))}
          </div>
        </div>
      </CardWrap>
      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <CardWrap title="Top learning goals" sub="Most selected learner destinations">
          <div className="divide-y divide-[#edf0eb]">
            {(analytics?.top_goals ?? []).map((item: any) => [item.goal, item.percentage] as const).map(([g, pct]: readonly [string, number]) => (
              <div key={g} className="flex items-center gap-4 px-6 py-3.5">
                <span className="flex-1 text-sm font-bold text-[#40534d]">{g}</span>
                <div className="w-32 h-1.5 rounded-full bg-[#e3e9e1]"><div className="h-full rounded-full bg-[#176b65]" style={{ width: `${Number(pct) * 2.5}%` }} /></div>
                <span className="font-mono text-xs text-[#83918a]">{pct}%</span>
              </div>
            ))}
          </div>
        </CardWrap>
        <CardWrap title="Most practiced skills" sub="Skills with highest assessment activity">
          <div className="divide-y divide-[#edf0eb]">
            {(analytics?.top_skills ?? []).map((item: any) => [item.skill, item.learners] as const).map(([s, n]: readonly [string, number]) => (
              <div key={s} className="flex items-center gap-4 px-6 py-3.5">
                <span className="flex-1 text-sm font-bold text-[#40534d]">{s}</span>
                <span className="font-mono text-xs text-[#83918a]">{(n as number).toLocaleString()} learners</span>
              </div>
            ))}
          </div>
        </CardWrap>
      </div>
    </AdminShell>
  );
}

function NotificationsModule() {
  const [items, setItems] = useState<any[]>([]);
  useEffect(() => { adminService.adminListNotifications({}).then(rows => setItems(rows.map((n: any) => ({ ...n, type: n.type || '—', target: n.target || '—', priority: n.priority || '—', date: n.created_at ? new Date(n.created_at).toLocaleDateString() : '—', status: n.status || 'Published' })))).catch(() => setItems([])); }, []);
  const [form, setForm] = useState(false);
  const publish = (id: string) => setItems(c => c.map(n => n.id === id ? { ...n, status: 'Published' } : n));
  return (
    <AdminShell active="notifications">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Notification center</h1><p className="mt-2 text-sm text-[#718079]">Create and send platform announcements, reminders, and system notices to learners.</p></div>
        <Btn onClick={() => setForm(!form)}><Plus size={14} />New notification</Btn>
      </div>
      {form && (
        <div className="mt-5 rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-6">
          <h2 className="mb-5 text-lg font-bold">Create notification</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm font-bold text-[#36504a]">Title<input className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-sm outline-none focus:border-[#176b65]" placeholder="Notification title…" /></label>
            <label className="block text-sm font-bold text-[#36504a]">Target audience<select className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-sm outline-none focus:border-[#176b65]"><option>All Learners</option><option>New Learners</option><option>Advanced</option><option>Inactive</option></select></label>
            <label className="block text-sm font-bold text-[#36504a] col-span-full">Message<textarea rows={3} className="mt-2 w-full resize-none rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-sm outline-none focus:border-[#176b65]" placeholder="Notification message…" /></label>
          </div>
          <div className="mt-4 flex gap-3"><Btn>Publish now</Btn><Btn outline>Save draft</Btn><Btn outline onClick={() => setForm(false)}>Cancel</Btn></div>
        </div>
      )}
      <CardWrap title="All notifications" sub="Platform-wide announcements and reminders" className="mt-5">
        <div className="divide-y divide-[#edf0eb]">
          {items.map(n => (
            <div key={n.id} className="flex flex-wrap items-center gap-4 px-6 py-5">
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2"><p className="text-sm font-bold">{n.title}</p><Badge blue>{n.type}</Badge><Badge green={n.priority === 'High'} yellow={n.priority === 'Medium'}>{n.priority}</Badge></div>
                <p className="mt-1 text-xs text-[#83918a]">Target: {n.target} · {n.date}</p>
              </div>
              <Badge green={n.status === 'Published'} yellow={n.status === 'Scheduled'}>{n.status}</Badge>
              {n.status === 'Draft' && <Btn small onClick={() => publish(n.id)}><Play size={12} />Publish</Btn>}
              <Btn small danger><Trash2 size={12} /></Btn>
            </div>
          ))}
        </div>
      </CardWrap>
    </AdminShell>
  );
}

function AuditModule() {
  const [logs, setLogs] = useState<any[]>([]);
  useEffect(() => { adminService.listAuditLogs({}).then(rows => setLogs(rows.map((a: any) => ({ ...a, time: a.created_at ? new Date(a.created_at).toLocaleString() : '—', event: a.action || '—', admin: a.admin_id || '—', action: a.module || '—', severity: a.severity || 'low' })))).catch(() => setLogs([])); }, []);
  return (
    <AdminShell active="audit">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Audit logs</h1><p className="mt-2 text-sm text-[#718079]">Complete record of all admin actions and system events for compliance and review.</p></div>
        <Btn outline><TrendingUp size={14} />Export logs</Btn>
      </div>
      <CardWrap title="Event log" sub="Today's admin and system activity" action={<Btn small outline><RefreshCw size={12} />Live</Btn>} className="mt-7">
        <div className="overflow-auto">
          <table className="w-full min-w-[680px] text-left text-sm">
            <THead cols={['Time', 'Event', 'Administrator', 'Action type', 'Severity']} />
            <tbody className="divide-y divide-[#edf0eb]">
              {logs.map((a, i) => (
                <tr key={i} className="hover:bg-[#f5f7f3]">
                  <td className="px-4 py-3.5 font-mono text-xs text-[#83918a]">{a.time}</td>
                  <td className="px-4 py-3.5 font-bold">{a.event}</td>
                  <td className="px-4 py-3.5 text-xs text-[#53665f]">{a.admin}</td>
                  <td className="px-4 py-3.5"><Badge>{a.action}</Badge></td>
                  <td className="px-4 py-3.5"><Badge red={a.severity === 'high'} yellow={a.severity === 'medium'} green={a.severity === 'low'}>{a.severity}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardWrap>
    </AdminShell>
  );
}

function SettingsModule() {
  const [reg, setReg] = useState(true);
  const [ai, setAi] = useState(true);
  const [maint, setMaint] = useState(false);
  const Toggle = ({ on, set }: { on: boolean; set: (v: boolean) => void }) => (
    <button onClick={() => set(!on)} className={`relative h-6 w-11 rounded-full transition-colors ${on ? 'bg-[#176b65]' : 'bg-[#d4dbd1]'}`}>
      <span className={`absolute top-1 size-4 rounded-full bg-white shadow transition-transform ${on ? 'left-6' : 'left-1'}`} />
    </button>
  );
  return (
    <AdminShell active="settings">
      <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Platform settings</h1><p className="mt-2 text-sm text-[#718079]">Control global platform behavior, registration, and system configuration.</p></div>
      <div className="mt-7 grid gap-5 xl:grid-cols-2">
        <CardWrap title="Platform controls" sub="Global on/off switches">
          <div className="divide-y divide-[#edf0eb]">
            {[['Learner registration', 'Allow new learners to sign up', reg, setReg], ['AI features', 'Enable all AI capabilities platform-wide', ai, setAi], ['Maintenance mode', 'Take the platform offline for learners', maint, setMaint]].map(([label, sub, on, set]) => (
              <div key={label as string} className="flex items-center justify-between px-6 py-5">
                <div><p className="text-sm font-bold">{label as string}</p><p className="mt-0.5 text-xs text-[#83918a]">{sub as string}</p></div>
                <Toggle on={on as boolean} set={set as (v: boolean) => void} />
              </div>
            ))}
          </div>
        </CardWrap>
        <CardWrap title="Platform identity">
          <div className="p-5 space-y-4">
            <label className="block text-sm font-bold text-[#36504a]">Platform name<input defaultValue="LearnPath AI" className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-sm outline-none focus:border-[#176b65]" /></label>
            <label className="block text-sm font-bold text-[#36504a]">Tagline<input defaultValue="AI-powered personalized learning" className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-sm outline-none focus:border-[#176b65]" /></label>
            <label className="block text-sm font-bold text-[#36504a]">Default language<select className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-sm outline-none focus:border-[#176b65]"><option>English (US)</option><option>Hindi</option><option>Spanish</option><option>French</option></select></label>
            <label className="block text-sm font-bold text-[#36504a]">Timezone<select className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-2.5 text-sm outline-none focus:border-[#176b65]"><option>UTC</option><option>Asia/Calcutta</option><option>America/New_York</option></select></label>
            <Btn><Check size={14} />Save settings</Btn>
          </div>
        </CardWrap>
      </div>
      <CardWrap title="Security & access" sub="Admin account and session settings" className="mt-5">
        <div className="divide-y divide-[#edf0eb]">
          {[['Two-factor authentication', 'Require 2FA for all admin logins', 'Disabled'], ['Session timeout', 'Auto-logout after inactivity', '30 minutes'], ['IP whitelist', 'Restrict admin access to trusted IPs', 'Not configured'], ['Admin audit trail', 'Log all admin actions', 'Enabled']].map(([l, s, v]) => (
            <div key={l} className="flex items-center justify-between px-6 py-4">
              <div><p className="text-sm font-bold">{l}</p><p className="mt-0.5 text-xs text-[#83918a]">{s}</p></div>
              <div className="flex items-center gap-3"><Badge green={v === 'Enabled'} yellow={v === 'Disabled'}>{v}</Badge><Btn small outline>Configure</Btn></div>
            </div>
          ))}
        </div>
      </CardWrap>
    </AdminShell>
  );
}

// ─── Dispatcher ───────────────────────────────────────────────────────────────

function AdminModule({ module }: { module: string }) {
  switch (module) {
    case 'users': return <UsersModule />;
    case 'learning': return <LearningModule />;
    case 'learning-paths': return <LearningPathsModule />;
    case 'skills': return <SkillsModule />;
    case 'assessments': return <AssessmentsModule />;
    case 'resources': return <ResourcesModule />;
    case 'recommendations': return <RecommendationsModule />;
    case 'ai-controls': return <AIControlsModule />;
    case 'analytics': return <AnalyticsModule />;
    case 'notifications': return <NotificationsModule />;
    case 'audit': return <AuditModule />;
    case 'settings': return <SettingsModule />;
    default: return <AdminDashboard />;
  }
}

export { AdminLogin, AdminDashboard, AdminModule };
