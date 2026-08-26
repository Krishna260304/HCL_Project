import React, { useState, useEffect } from 'react';
import {
  Activity, AlertTriangle, ArrowRight, Bell, BookOpen, Bot, Check, CheckCircle2, ChevronDown,
  Code2, Database, FileText, Flame, Gauge, LayoutDashboard, Lock, LogOut, Menu, MessageSquare,
  MoreHorizontal, Play, Plus, RefreshCw, Search, Settings, Shield, ShieldCheck, SlidersHorizontal,
  ToggleLeft, ToggleRight, Trash2, TrendingUp, Users, Workflow, X, Zap, Loader2, AlertCircle, Eye
} from 'lucide-react';
import { Link, useLocation } from 'wouter';
import { useAuth } from '@/context/AuthContext';
import {
  adminService,
  courseService,
  type AdminUser,
  type AdminAnalytics,
  type Skill,
  type Assessment,
  type Resource,
  type Notification,
} from '@/services/index';
import { SkeletonCard, SkeletonTable, ErrorState, EmptyState } from '@/components/states';

// ─── Admin Navigation Taxonomy ───────────────────────────────────────────────

const adminNav = [
  { slug: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { slug: 'users', label: 'Users', icon: Users },
  { slug: 'learning-paths', label: 'Learning paths', icon: Workflow },
  { slug: 'skills', label: 'Skills catalog', icon: Code2 },
  { slug: 'assessments', label: 'Assessments', icon: CheckCircle2 },
  { slug: 'resources', label: 'Resource curation', icon: Database },
  { slug: 'ai-controls', label: 'AI parameters', icon: Bot },
  { slug: 'analytics', label: 'Analytics', icon: Activity },
  { slug: 'notifications', label: 'Broadcasts', icon: Bell },
  { slug: 'audit', label: 'Audit logs', icon: Shield },
  { slug: 'settings', label: 'Settings', icon: Settings },
] as const;

type Slug = typeof adminNav[number]['slug'];

// ─── Shared UI Helpers ────────────────────────────────────────────────────────

const Badge = ({ children, green = false, yellow = false, red = false, blue = false }: { children: React.ReactNode; green?: boolean; yellow?: boolean; red?: boolean; blue?: boolean }) => {
  const cls = green ? 'bg-[#dceee4] text-[#176b65]' : yellow ? 'bg-[#fae9bb] text-[#93611a]' : red ? 'bg-[#fbe9e5] text-[#a04b3e]' : blue ? 'bg-[#dde8f7] text-[#2b5faa]' : 'bg-[#edf0eb] text-[#5a6b64]';
  return <span className={`inline-flex rounded-full px-2.5 py-0.5 text-[10px] font-bold ${cls}`}>{children}</span>;
};

const CardWrap = ({ title, sub, action, children }: { title: string; sub?: string; action?: React.ReactNode; children: React.ReactNode }) => (
  <section className="overflow-hidden rounded-2xl border border-[#dbe4da] bg-[#fafbf8] shadow-sm">
    {(title || action) && (
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#e4e9e2] px-6 py-4">
        <div>
          <h2 className="text-lg font-bold text-[#1f312e]">{title}</h2>
          {sub && <p className="mt-0.5 text-xs text-[#83918a]">{sub}</p>}
        </div>
        {action}
      </div>
    )}
    {children}
  </section>
);

// ─── Admin Login ──────────────────────────────────────────────────────────────

export function AdminLogin() {
  const [, setLocation] = useLocation();
  const { login, user, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && user?.role === 'admin') {
      setLocation('/admin/dashboard');
    }
  }, [isAuthenticated, user, setLocation]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const authUser = await login(email.trim(), password);
      if (authUser.role !== 'admin') {
        throw new Error('Access denied. This account does not have administrator privileges.');
      }
      setLocation('/admin/dashboard');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Invalid administrator credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-[100dvh] place-items-center bg-[#f4f6f1] px-5 py-10">
      <div className="w-full max-w-md rounded-3xl border border-[#dbe4da] bg-[#fafbf8] p-8 shadow-[0_20px_70px_rgba(42,67,57,.08)] md:p-10">
        <div className="flex items-center gap-3">
          <span className="grid size-11 place-items-center rounded-2xl bg-[#176b65] text-white">
            <ShieldCheck size={22} />
          </span>
          <div>
            <p className="font-bold text-[#1f312e]">LearnPath AI</p>
            <p className="font-mono text-[9px] uppercase tracking-widest text-[#89968f]">Admin control center</p>
          </div>
        </div>

        <p className="mt-8 font-mono text-[10px] uppercase tracking-[.18em] text-[#b17820]">Restricted access</p>
        <h1 className="mt-2 text-3xl font-bold tracking-[-.05em] text-[#1f312e]">Administrator sign in</h1>
        <p className="mt-2 text-xs leading-5 text-[#718079]">
          Platform governance, learner management, and AI pipeline configuration.
        </p>

        {error && (
          <div className="mt-5 flex items-start gap-2.5 rounded-xl border border-[#f5d5d0] bg-[#fdf5f4] p-3 text-xs font-semibold text-[#a04b3e]">
            <AlertCircle size={16} className="shrink-0 text-[#a04b3e]" />
            <div>{error}</div>
          </div>
        )}

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm font-bold text-[#36504a]">
            Administrator email
            <input
              value={email}
              onChange={e => setEmail(e.target.value)}
              type="email"
              required
              placeholder="admin@learnpath.ai"
              className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-3 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10"
              data-testid="input-admin-email"
            />
          </label>

          <label className="block text-sm font-bold text-[#36504a]">
            Password
            <input
              value={password}
              onChange={e => setPassword(e.target.value)}
              type="password"
              required
              placeholder="••••••••"
              autoComplete="current-password"
              className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-3 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10"
              data-testid="input-admin-password"
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-[#176b65] px-4 py-3 text-sm font-bold text-white hover:bg-[#115a55] disabled:opacity-50 transition"
            data-testid="button-admin-submit"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            {loading ? 'Authenticating…' : 'Sign in to Control Center'} <ArrowRight size={15} />
          </button>
        </form>

        <div className="mt-8 border-t border-[#e4e9e2] pt-5 text-center">
          <Link href="/login" className="text-xs font-bold text-[#176b65] hover:underline">
            ← Switch to Learner portal
          </Link>
        </div>
      </div>
    </div>
  );
}

// ─── Admin Shell ──────────────────────────────────────────────────────────────

export function AdminShell({ children, active }: { children: React.ReactNode; active: Slug | string }) {
  const [, setLocation] = useLocation();
  const { user, logout, isAdmin } = useAuth();
  const [drawer, setDrawer] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    // If not authenticated or not admin, redirect to admin login
    if (!user || user.role !== 'admin') {
      setLocation('/admin/login');
    }
  }, [user, setLocation]);

  const handleLogout = async () => {
    await logout();
    setLocation('/admin/login');
  };

  const Sidebar = () => (
    <aside className={`flex h-full flex-col bg-[#172e29] py-4 text-[#e7f0e8] transition-all ${collapsed ? 'w-[70px]' : 'w-[256px]'}`}>
      <div className={`flex items-center gap-3 px-4 py-2 ${collapsed ? 'justify-center' : ''}`}>
        <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-[#e8b044] text-[#172e29]">
          <ShieldCheck size={18} />
        </span>
        {!collapsed && (
          <span className="min-w-0 flex-1">
            <span className="block text-sm font-bold truncate">LearnPath AI</span>
            <span className="font-mono text-[9px] uppercase tracking-widest text-[#7fa898]">Control center</span>
          </span>
        )}
        {!collapsed && (
          <button onClick={() => setCollapsed(true)} className="ml-auto rounded-lg p-1 text-[#7fa898] hover:text-white">
            <X size={14} />
          </button>
        )}
      </div>

      {collapsed && (
        <button onClick={() => setCollapsed(false)} className="mx-auto mt-1 rounded-lg p-1.5 text-[#7fa898] hover:text-white">
          <Menu size={15} />
        </button>
      )}

      <nav className="mt-5 flex-1 space-y-0.5 px-2 overflow-y-auto">
        {adminNav.map(({ slug, label, icon: Icon }) => (
          <Link
            key={slug}
            href={`/admin/${slug}`}
            onClick={() => setDrawer(false)}
            className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-bold transition-colors ${
              active === slug ? 'bg-[#e8b044] text-[#172e29]' : 'text-[#a8c6b8] hover:bg-[#243f39] hover:text-white'
            } ${collapsed ? 'justify-center' : ''}`}
            title={collapsed ? label : ''}
          >
            <Icon size={16} className="shrink-0" />
            {!collapsed && label}
          </Link>
        ))}
      </nav>

      <div className="mt-auto px-2 pt-3 border-t border-[#243f39]">
        <button
          onClick={handleLogout}
          className={`flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-xs font-bold text-[#a8c6b8] hover:bg-[#243f39] hover:text-white transition ${collapsed ? 'justify-center' : ''}`}
        >
          <LogOut size={15} />
          {!collapsed && 'Log out'}
        </button>
      </div>
    </aside>
  );

  return (
    <div className="flex min-h-[100dvh] bg-[#f3f6f1] text-[#1f312e]">
      <div className="hidden lg:sticky lg:top-0 lg:flex lg:h-screen lg:shrink-0">
        <Sidebar />
      </div>

      {drawer && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setDrawer(false)} />
          <div className="relative h-full w-[256px] flex">
            <Sidebar />
          </div>
        </div>
      )}

      <div className="flex flex-1 flex-col min-w-0">
        <header className="sticky top-0 z-30 flex h-[68px] shrink-0 items-center justify-between border-b border-[#dbe4da] bg-[#f3f6f1]/90 px-5 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <button onClick={() => setDrawer(true)} className="rounded-lg p-2 lg:hidden">
              <Menu size={19} />
            </button>
            <div className="flex items-center gap-2 text-xs text-[#718079]">
              <span className="font-mono text-[10px] uppercase tracking-widest text-[#b17820]">Admin</span>
              <span>/</span>
              <span className="font-bold text-[#36504a]">
                {adminNav.find(n => n.slug === active)?.label || 'Control Center'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 rounded-xl border border-[#ccd8ce] bg-white px-3 py-1.5 text-xs font-bold text-[#36504a]">
              <span className="size-2 rounded-full bg-[#176b65]" /> Production
            </span>
            <span className="grid size-9 place-items-center rounded-xl bg-[#e8b044] text-xs font-bold text-[#172e29]">
              AD
            </span>
          </div>
        </header>

        <main className="flex-1 p-5 lg:p-8 max-w-[1440px] w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

// ─── Admin Dashboard ──────────────────────────────────────────────────────────

export function AdminDashboard() {
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.getAnalyticsOverview();
      setAnalytics(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not fetch admin overview.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <AdminShell active="dashboard">
        <div className="space-y-5">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[1, 2, 3, 4].map(i => <SkeletonCard key={i} rows={1} />)}
          </div>
          <SkeletonCard rows={4} />
        </div>
      </AdminShell>
    );
  }

  if (error) {
    return (
      <AdminShell active="dashboard">
        <ErrorState title="Dashboard error" message={error} onRetry={load} />
      </AdminShell>
    );
  }

  const stats = [
    { label: 'Total Learners', value: analytics?.total_learners ?? 0 },
    { label: 'Active This Week', value: analytics?.active_this_week ?? 0 },
    { label: 'Paths Generated', value: analytics?.paths_generated ?? 0 },
    { label: 'Live Resources', value: analytics?.resources_live ?? 0 },
    { label: 'Assessments Taken', value: analytics?.assessments_taken ?? 0 },
    { label: 'AI Conversations', value: analytics?.ai_conversations ?? 0 },
    { label: 'Catalog Skills', value: analytics?.skills_in_catalog ?? 0 },
    { label: 'Projects Shipped', value: analytics?.projects_shipped ?? 0 },
  ];

  const activities = analytics?.recent_activities || [];

  return (
    <AdminShell active="dashboard">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">System overview</p>
          <h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Platform Control Center</h1>
          <p className="mt-2 text-sm text-[#718079]">Live analytics and operations feed from the LearnPath backend.</p>
        </div>
        <span className="flex items-center gap-2 rounded-full bg-[#dceee4] px-4 py-2 text-xs font-bold text-[#176b65]">
          <span className="size-2 animate-pulse rounded-full bg-[#176b65]" /> Live telemetry
        </span>
      </div>

      <div className="mt-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map(({ label, value }) => (
          <div key={label} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5 shadow-sm">
            <p className="text-xs text-[#83918a]">{label}</p>
            <p className="mt-3 font-mono text-3xl font-bold text-[#1f312e]">{value.toLocaleString()}</p>
            <p className="mt-2 text-xs font-bold text-[#176b65]">Synchronized</p>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <CardWrap title="Platform Activity Stream" sub="Real-time events dispatched to the gateway">
          <div className="divide-y divide-[#e4e9e2] p-6">
            {activities.length > 0 ? (
              activities.map((act, i) => (
                <div key={i} className="flex items-center justify-between py-3">
                  <div>
                    <p className="text-sm font-bold text-[#1f312e]">{act.event}</p>
                    <p className="text-xs text-[#83918a]">By {act.actor}</p>
                  </div>
                  <span className="font-mono text-xs text-[#83918a]">{act.time}</span>
                </div>
              ))
            ) : (
              <p className="text-center py-6 text-xs text-[#83918a]">No recorded events in the recent window.</p>
            )}
          </div>
        </CardWrap>

        <CardWrap title="System Health & Controls" sub="Services state">
          <div className="p-6 space-y-4 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-[#eef2ea]">
              <span className="font-bold text-[#36504a]">WebSocket Gateway</span>
              <Badge green>Connected</Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-[#eef2ea]">
              <span className="font-bold text-[#36504a]">MongoDB Database</span>
              <Badge green>Healthy</Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-[#eef2ea]">
              <span className="font-bold text-[#36504a]">Channel Layer (Redis)</span>
              <Badge green>Active</Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-[#eef2ea]">
              <span className="font-bold text-[#36504a]">Authentication & JWT</span>
              <Badge green>Operational</Badge>
            </div>
          </div>
        </CardWrap>
      </div>
    </AdminShell>
  );
}

// ─── Admin Users Module ───────────────────────────────────────────────────────

function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.listUsers();
      setUsers(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not fetch users.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggleStatus = async (user: AdminUser) => {
    const nextStatus = user.status === 'active' ? 'suspended' : 'active';
    setActionLoading(user.id);
    try {
      await adminService.updateUserStatus(user.id, nextStatus);
      setUsers(prev => prev.map(u => u.id === user.id ? { ...u, status: nextStatus } : u));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update user status.');
    } finally {
      setActionLoading(null);
    }
  };

  const deleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to permanently delete this user?')) return;
    setActionLoading(userId);
    try {
      await adminService.deleteUser(userId);
      setUsers(prev => prev.filter(u => u.id !== userId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete user.');
    } finally {
      setActionLoading(null);
    }
  };

  const filtered = users.filter(u =>
    `${u.name || ''} ${u.email || ''} ${u.role || ''}`.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-sm text-[#718079]">Manage registered learners, roles, and account statuses.</p>
        </div>
        <div className="relative">
          <Search size={16} className="absolute left-3.5 top-3 text-[#89968f]" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search users…"
            className="rounded-xl border border-[#ccd8ce] bg-white py-2.5 pl-10 pr-4 text-xs outline-none focus:border-[#176b65]"
          />
        </div>
      </div>

      {loading && <SkeletonTable rows={5} cols={5} />}
      {error && <ErrorState title="User list unavailable" message={error} onRetry={load} />}

      {!loading && !error && (
        <CardWrap title={`All Accounts (${filtered.length})`}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#f0f3ed] text-[10px] uppercase font-bold text-[#83918a]">
                <tr>
                  <th className="p-4">User</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Joined</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e4e9e2]">
                {filtered.map(u => (
                  <tr key={u.id} className="hover:bg-[#f8faf6]">
                    <td className="p-4">
                      <p className="font-bold text-[#1f312e]">{u.name || u.email.split('@')[0]}</p>
                      <p className="text-[11px] text-[#83918a]">{u.email}</p>
                    </td>
                    <td className="p-4">
                      <Badge blue={u.role === 'admin'}>{u.role || 'learner'}</Badge>
                    </td>
                    <td className="p-4">
                      <Badge green={u.status === 'active'} red={u.status === 'suspended'}>
                        {u.status || 'active'}
                      </Badge>
                    </td>
                    <td className="p-4 text-[#83918a] font-mono">
                      {u.joined ? new Date(u.joined).toLocaleDateString() : '—'}
                    </td>
                    <td className="p-4 text-right space-x-2">
                      <button
                        onClick={() => toggleStatus(u)}
                        disabled={actionLoading === u.id}
                        className="rounded-lg border border-[#ccd8ce] px-2.5 py-1 text-[11px] font-bold text-[#36504a] hover:border-[#176b65]"
                      >
                        {u.status === 'active' ? 'Suspend' : 'Activate'}
                      </button>
                      <button
                        onClick={() => deleteUser(u.id)}
                        disabled={actionLoading === u.id}
                        className="rounded-lg border border-[#f5d5d0] bg-[#fdf5f4] px-2.5 py-1 text-[11px] font-bold text-[#a04b3e] hover:bg-[#fbe9e5]"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-[#83918a]">
                      No users match the search criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardWrap>
      )}
    </div>
  );
}

// ─── Admin Skills Module ──────────────────────────────────────────────────────

function AdminSkills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.adminListSkills();
      setSkills(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not fetch skills.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;
    try {
      const created = await adminService.createSkill({
        name: newSkillName.trim(),
        category: newSkillCategory.trim() || 'General',
      });
      setSkills(prev => [created, ...prev]);
      setNewSkillName('');
      setNewSkillCategory('');
      setShowAdd(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create skill.');
    }
  };

  const handleDelete = async (skillId: string) => {
    if (!confirm('Are you sure you want to remove this skill from the taxonomy?')) return;
    try {
      await adminService.deleteSkill(skillId);
      setSkills(prev => prev.filter(s => s.id !== skillId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete skill.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Skill Taxonomy Catalog</h1>
          <p className="text-sm text-[#718079]">Manage competency nodes, prerequisites, and evaluation benchmarks.</p>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="inline-flex items-center gap-1.5 rounded-xl bg-[#176b65] px-4 py-2.5 text-xs font-bold text-white hover:bg-[#115a55]"
        >
          <Plus size={15} /> Add Skill
        </button>
      </div>

      {showAdd && (
        <form onSubmit={handleCreate} className="rounded-2xl border border-[#dbe4da] bg-white p-6 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-[#1f312e]">Add New Skill Node</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <input
              value={newSkillName}
              onChange={e => setNewSkillName(e.target.value)}
              placeholder="Skill name (e.g. PyTorch)"
              required
              className="rounded-xl border border-[#ccd8ce] p-3 text-xs outline-none focus:border-[#176b65]"
            />
            <input
              value={newSkillCategory}
              onChange={e => setNewSkillCategory(e.target.value)}
              placeholder="Category (e.g. Deep Learning)"
              className="rounded-xl border border-[#ccd8ce] p-3 text-xs outline-none focus:border-[#176b65]"
            />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="rounded-xl bg-[#176b65] px-4 py-2 text-xs font-bold text-white">
              Save Skill
            </button>
            <button type="button" onClick={() => setShowAdd(false)} className="rounded-xl border px-4 py-2 text-xs font-bold">
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading && <SkeletonTable rows={6} cols={3} />}
      {error && <ErrorState title="Skills error" message={error} onRetry={load} />}

      {!loading && !error && (
        <CardWrap title={`Catalog Skills (${skills.length})`}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#f0f3ed] text-[10px] uppercase font-bold text-[#83918a]">
                <tr>
                  <th className="p-4">Skill</th>
                  <th className="p-4">Category</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e4e9e2]">
                {skills.map(s => (
                  <tr key={s.id || s.name} className="hover:bg-[#f8faf6]">
                    <td className="p-4 font-bold text-[#1f312e]">{s.name}</td>
                    <td className="p-4"><Badge>{s.category || 'General'}</Badge></td>
                    <td className="p-4 text-right">
                      {s.id && (
                        <button
                          onClick={() => handleDelete(s.id!)}
                          className="rounded-lg p-1.5 text-[#a04b3e] hover:bg-[#fbe9e5]"
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardWrap>
      )}
    </div>
  );
}

// ─── Admin Resources Module ───────────────────────────────────────────────────

function AdminResources() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.adminListResources();
      setResources(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not fetch resources.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const approve = async (id: string) => {
    try {
      await adminService.approveResource(id);
      load();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Approval failed.');
    }
  };

  const reject = async (id: string) => {
    try {
      await adminService.rejectResource(id);
      load();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Rejection failed.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Resource Curation & Moderation</h1>
          <p className="text-sm text-[#718079]">Review, approve, and assign learning resources.</p>
        </div>
      </div>

      {loading && <SkeletonCard rows={3} />}
      {error && <ErrorState title="Resource list unavailable" message={error} onRetry={load} />}

      {!loading && !error && (
        <CardWrap title={`Managed Resources (${resources.length})`}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#f0f3ed] text-[10px] uppercase font-bold text-[#83918a]">
                <tr>
                  <th className="p-4">Title</th>
                  <th className="p-4">Source</th>
                  <th className="p-4">Type</th>
                  <th className="p-4">Status</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e4e9e2]">
                {resources.map(r => (
                  <tr key={r.id} className="hover:bg-[#f8faf6]">
                    <td className="p-4 font-bold text-[#1f312e] max-w-xs truncate">{r.title}</td>
                    <td className="p-4 text-[#83918a]">{r.source || 'Curated'}</td>
                    <td className="p-4"><Badge>{r.type || 'Resource'}</Badge></td>
                    <td className="p-4"><Badge green>{r.status || 'Active'}</Badge></td>
                    <td className="p-4 text-right space-x-2">
                      <button onClick={() => approve(r.id)} className="rounded-lg bg-[#dceee4] px-2.5 py-1 font-bold text-[#176b65] hover:bg-[#c9e6d4]">
                        Approve
                      </button>
                      <button onClick={() => reject(r.id)} className="rounded-lg bg-[#fbe9e5] px-2.5 py-1 font-bold text-[#a04b3e] hover:bg-[#f5d0ca]">
                        Reject
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardWrap>
      )}
    </div>
  );
}

// ─── Admin Assessments Module ─────────────────────────────────────────────────

function AdminAssessments() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.adminListAssessments();
      setAssessments(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not fetch assessments.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Assessment Engine & Checkpoints</h1>
      <p className="text-sm text-[#718079]">View and configure automated checkpoint evaluations.</p>

      {loading && <SkeletonCard rows={3} />}
      {error && <ErrorState title="Assessments error" message={error} onRetry={load} />}

      {!loading && !error && (
        <CardWrap title={`Active Assessments (${assessments.length})`}>
          <div className="divide-y divide-[#e4e9e2] p-4">
            {assessments.map(a => (
              <div key={a.id} className="flex items-center justify-between py-3">
                <div>
                  <p className="text-sm font-bold text-[#1f312e]">{a.title || a.topic}</p>
                  <p className="text-xs text-[#83918a]">{a.questions_count ?? 10} questions · {a.difficulty || 'Core'}</p>
                </div>
                <Badge green>{a.status || 'Published'}</Badge>
              </div>
            ))}
          </div>
        </CardWrap>
      )}
    </div>
  );
}

// ─── Admin Generic Module Router ──────────────────────────────────────────────

export function AdminModule({ module }: { module: string }) {
  const [data, setData] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);

    const fetchModuleData = async () => {
      try {
        if (module === 'learning-paths') {
          const res = await adminService.listLearningPaths();
          if (mounted) setData(res);
        } else if (module === 'audit') {
          const res = await adminService.listAuditLogs();
          if (mounted) setData(res);
        } else if (module === 'notifications') {
          const res = await adminService.adminListNotifications();
          if (mounted) setData(res);
        } else if (module === 'settings' || module === 'ai-controls') {
          const res = await adminService.getSettings();
          if (mounted) setData(res);
        } else if (module === 'analytics') {
          const res = await adminService.getAnalyticsOverview();
          if (mounted) setData(res);
        }
      } catch (e) {
        if (mounted) setError(e instanceof Error ? e.message : 'Could not load data.');
      } finally {
        if (mounted) setLoading(false);
      }
    };

    fetchModuleData();
    return () => { mounted = false; };
  }, [module]);

  if (module === 'users') return <AdminShell active="users"><AdminUsers /></AdminShell>;
  if (module === 'skills') return <AdminShell active="skills"><AdminSkills /></AdminShell>;
  if (module === 'resources') return <AdminShell active="resources"><AdminResources /></AdminShell>;
  if (module === 'assessments') return <AdminShell active="assessments"><AdminAssessments /></AdminShell>;

  return (
    <AdminShell active={module}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold capitalize">{module.replace('-', ' ')}</h1>
        {loading && <SkeletonCard rows={3} />}
        {error && <ErrorState title="Error" message={error} />}

        {!loading && !error && (
          <CardWrap title={`Module: ${module}`}>
            <div className="p-6">
              <pre className="max-h-96 overflow-auto rounded-xl bg-[#1f312e] p-4 text-xs text-[#a8c6b8] font-mono">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </CardWrap>
        )}
      </div>
    </AdminShell>
  );
}
