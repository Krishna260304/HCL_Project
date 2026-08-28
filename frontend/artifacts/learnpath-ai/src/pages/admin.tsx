import { useState } from 'react';
import {
  Activity, AlertTriangle, ArrowRight, Bell, BookOpen, Bot, Check, CheckCircle2, ChevronDown,
  Code2, Database, FileText, Flame, Gauge, LayoutDashboard, Lock, LogOut, Menu, MessageSquare,
  MoreHorizontal, Play, Plus, RefreshCw, Search, Settings, Shield, ShieldCheck, SlidersHorizontal,
  ToggleLeft, ToggleRight, Trash2, TrendingUp, Users, Workflow, X, Zap,
} from 'lucide-react';
import { Link, useLocation } from 'wouter';

// ─── Mock data ───────────────────────────────────────────────────────────────

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

const learnersMock = [
  { id: '1', name: 'Maya Chen', email: 'maya.chen@example.com', goal: 'AI Engineer', status: 'Active', progress: 74, joined: 'Apr 12, 2025', lastActive: '2h ago', experience: '3–5 years' },
  { id: '2', name: 'Arjun Mehta', email: 'arjun.mehta@example.com', goal: 'Data Scientist', status: 'Active', progress: 48, joined: 'Apr 10, 2025', lastActive: '1d ago', experience: '1–2 years' },
  { id: '3', name: 'Sofia Alvarez', email: 'sofia.a@example.com', goal: 'Frontend Developer', status: 'Suspended', progress: 31, joined: 'Apr 08, 2025', lastActive: '5d ago', experience: 'Just starting' },
  { id: '4', name: 'Noah Williams', email: 'noah.w@example.com', goal: 'Cloud Engineer', status: 'Active', progress: 62, joined: 'Apr 06, 2025', lastActive: '3h ago', experience: '1–2 years' },
  { id: '5', name: 'Priya Sharma', email: 'priya.s@example.com', goal: 'ML Engineer', status: 'Active', progress: 88, joined: 'Mar 28, 2025', lastActive: '1h ago', experience: '3–5 years' },
  { id: '6', name: 'Lucas Costa', email: 'lucas.c@example.com', goal: 'Full-Stack Developer', status: 'Inactive', progress: 12, joined: 'Apr 15, 2025', lastActive: '10d ago', experience: 'Just starting' },
];

const coursesMock = [
  { id: '1', title: 'ML Foundations Bootcamp', category: 'Machine Learning', difficulty: 'Beginner', skills: ['Python', 'Scikit-learn'], duration: '3 weeks', status: 'Published', resources: 12, updated: 'Apr 18, 2025' },
  { id: '2', title: 'Deep Learning Mastery', category: 'Deep Learning', difficulty: 'Intermediate', skills: ['PyTorch', 'Neural networks'], duration: '5 weeks', status: 'Published', resources: 18, updated: 'Apr 20, 2025' },
  { id: '3', title: 'Transformers Explained', category: 'NLP', difficulty: 'Advanced', skills: ['Transformers', 'Hugging Face'], duration: '4 weeks', status: 'Draft', resources: 9, updated: 'Apr 22, 2025' },
  { id: '4', title: 'AI Systems in Production', category: 'MLOps', difficulty: 'Advanced', skills: ['RAG', 'Deployment'], duration: '5 weeks', status: 'Published', resources: 15, updated: 'Apr 17, 2025' },
];

const skillsMock = [
  { name: 'Python', category: 'Programming', difficulty: 'Beginner', learners: 18420, related: ['NumPy', 'Pandas'], status: 'Active' },
  { name: 'Machine Learning', category: 'AI/ML', difficulty: 'Intermediate', learners: 12380, related: ['Scikit-learn', 'Statistics'], status: 'Active' },
  { name: 'PyTorch', category: 'Deep Learning', difficulty: 'Intermediate', learners: 8210, related: ['Neural networks', 'CUDA'], status: 'Active' },
  { name: 'Transformers', category: 'NLP', difficulty: 'Advanced', learners: 5640, related: ['Attention', 'Hugging Face'], status: 'Active' },
  { name: 'RAG', category: 'Generative AI', difficulty: 'Advanced', learners: 3820, related: ['Embeddings', 'Vector DB'], status: 'Active' },
  { name: 'Docker', category: 'DevOps', difficulty: 'Intermediate', learners: 7190, related: ['Kubernetes', 'CI/CD'], status: 'Active' },
];

const assessmentsMock = [
  { id: '1', name: 'ML Foundations', skill: 'Machine Learning', difficulty: 'Core', questions: 18, avgScore: 81, attempts: 4230, status: 'Published' },
  { id: '2', name: 'Python for ML', skill: 'Python', difficulty: 'Core', questions: 12, avgScore: 87, attempts: 6100, status: 'Published' },
  { id: '3', name: 'Neural Networks Deep Dive', skill: 'Deep Learning', difficulty: 'Stretch', questions: 20, avgScore: 68, attempts: 1820, status: 'Published' },
  { id: '4', name: 'Transformer Architecture', skill: 'Transformers', difficulty: 'Stretch', questions: 15, avgScore: 59, attempts: 890, status: 'Draft' },
];

const resourcesMock = [
  { id: '1', title: 'Neural Networks: Zero to Hero', source: 'YouTube', type: 'Video', skill: 'Neural networks', quality: 98, status: 'Approved' },
  { id: '2', title: 'The Illustrated Transformer', source: 'Blog', type: 'Article', skill: 'Transformers', quality: 95, status: 'Approved' },
  { id: '3', title: 'PyTorch 60-min Blitz', source: 'Documentation', type: 'Interactive', skill: 'PyTorch', quality: 91, status: 'Approved' },
  { id: '4', title: 'Intro to Backpropagation', source: 'YouTube', type: 'Video', skill: 'Deep learning', quality: 74, status: 'Pending' },
  { id: '5', title: 'RAG Systems at Scale', source: 'GitHub', type: 'Code', skill: 'RAG', quality: 88, status: 'Pending' },
];

const recsMock = [
  { learner: 'Maya Chen', resource: 'Transformers Explained', skill: 'Transformers', reason: 'Matches next phase skill gap', score: 94, status: 'Accepted' },
  { learner: 'Arjun Mehta', resource: 'Statistics for DS', skill: 'Statistics', reason: 'Prerequisite gap detected', score: 89, status: 'Skipped' },
  { learner: 'Noah Williams', resource: 'AWS Cloud Practitioner', skill: 'AWS', reason: 'Goal alignment — Cloud Engineer', score: 91, status: 'Accepted' },
  { learner: 'Priya Sharma', resource: 'Hugging Face Course', skill: 'Fine-tuning', reason: 'Advanced path milestone', score: 96, status: 'Accepted' },
];

const pathsMock = [
  { id: '1', goal: 'Become an AI Engineer', learner: 'Maya Chen', progress: 74, phases: 4, status: 'Active', created: 'Feb 12, 2025' },
  { id: '2', goal: 'Become a Data Scientist', learner: 'Arjun Mehta', progress: 48, phases: 4, status: 'Active', created: 'Feb 10, 2025' },
  { id: '3', goal: 'Frontend Developer', learner: 'Sofia Alvarez', progress: 31, phases: 3, status: 'Suspended', created: 'Feb 08, 2025' },
  { id: '4', goal: 'Cloud Engineer', learner: 'Noah Williams', progress: 62, phases: 5, status: 'Active', created: 'Feb 06, 2025' },
];

const auditMock = [
  { time: '09:14', event: 'Admin modified skill taxonomy', admin: 'admin@example.com', action: 'Edit', severity: 'medium' },
  { time: '09:02', event: 'User account suspended', admin: 'admin@example.com', action: 'Suspend', severity: 'high' },
  { time: '08:48', event: 'Resource approved', admin: 'admin@example.com', action: 'Approve', severity: 'low' },
  { time: '08:31', event: 'Assessment published', admin: 'admin@example.com', action: 'Publish', severity: 'low' },
  { time: '08:15', event: 'AI model temperature updated', admin: 'admin@example.com', action: 'Config', severity: 'medium' },
  { time: '07:58', event: 'Recommendation weights saved', admin: 'admin@example.com', action: 'Config', severity: 'medium' },
  { time: '07:40', event: 'New learner registered', admin: 'System', action: 'Register', severity: 'low' },
  { time: '07:28', event: 'Learning path generated via AI', admin: 'System', action: 'Generate', severity: 'low' },
];

const notifMock = [
  { id: '1', title: 'New feature: AI path adjustments', type: 'Announcement', target: 'All Learners', status: 'Published', priority: 'High', date: 'Apr 22, 2025' },
  { id: '2', title: 'Scheduled maintenance — Apr 28', type: 'System', target: 'All Learners', status: 'Scheduled', priority: 'Medium', date: 'Apr 28, 2025' },
  { id: '3', title: 'Complete your baseline assessment', type: 'Reminder', target: 'New Learners', status: 'Draft', priority: 'Low', date: 'Apr 22, 2025' },
];

const dashStats = [
  { label: 'Total learners', value: '24,832', delta: '+12.4%', color: '#176b65' },
  { label: 'Active this week', value: '8,421', delta: '+8.7%', color: '#176b65' },
  { label: 'Paths generated', value: '14,320', delta: '+16.2%', color: '#176b65' },
  { label: 'Resources live', value: '18,492', delta: '+4.3%', color: '#176b65' },
  { label: 'Assessments taken', value: '7,320', delta: '+11.1%', color: '#176b65' },
  { label: 'AI conversations', value: '42,931', delta: '+22.8%', color: '#d89c2c' },
  { label: 'Skills in catalog', value: '486', delta: '+3.0%', color: '#176b65' },
  { label: 'Projects shipped', value: '2,180', delta: '+9.5%', color: '#176b65' },
];

const activities = [
  { event: 'New learner registered', time: '1 hour ago', actor: 'System', tag: 'register' },
  { event: 'Assessment generated for Arjun Mehta', time: '2 hours ago', actor: 'AI system', tag: 'assess' },
  { event: 'Resource approved: RAG Systems at Scale', time: '3 hours ago', actor: 'admin@example.com', tag: 'approve' },
  { event: 'Recommendation weights updated', time: '4 hours ago', actor: 'admin@example.com', tag: 'config' },
  { event: 'New project published by Maya Chen', time: '5 hours ago', actor: 'Maya Chen', tag: 'publish' },
  { event: 'AI model temperature adjusted (0.7→0.5)', time: '6 hours ago', actor: 'admin@example.com', tag: 'config' },
];

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
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
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
        <form className="mt-8 space-y-4" onSubmit={e => { e.preventDefault(); if (email === 'admin@example.com' && password === 'admin123') setLocation('/admin/dashboard'); else setError('Demo credentials: admin@example.com / admin123'); }}>
          <label className="block text-sm font-bold text-[#36504a]">Email<input value={email} onChange={e => setEmail(e.target.value)} type="email" className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-3 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10" /></label>
          <label className="block text-sm font-bold text-[#36504a]">Password<input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="••••••••" autoComplete="current-password" className="mt-2 w-full rounded-xl border border-[#ccd8ce] bg-white px-4 py-3 text-sm outline-none focus:border-[#176b65] focus:ring-2 focus:ring-[#176b65]/10" /></label>
          <label className="flex items-center gap-2 text-xs text-[#718079]"><input type="checkbox" className="accent-[#176b65]" /> Remember me</label>
          {error && <p className="rounded-xl bg-[#fbe9e5] px-4 py-3 text-xs font-bold text-[#a04b3e]">{error}</p>}
          <button className="w-full rounded-xl bg-[#176b65] px-4 py-3 text-sm font-bold text-white hover:bg-[#115a55]">Sign in <ArrowRight size={15} className="ml-1 inline" /></button>
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
  const [drawer, setDrawer] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

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
      <button onClick={() => setLocation('/')} className={`mx-2 mt-2 flex items-center gap-2 rounded-xl px-3 py-2.5 text-xs font-bold text-[#a8c6b8] hover:bg-[#243f39] hover:text-white ${collapsed ? 'justify-center' : ''}`}>
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
  return (
    <AdminShell active="dashboard">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">System overview</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Platform Control Center</h1><p className="mt-2 text-sm text-[#718079]">Monitor and control the LearnPath AI platform.</p></div>
        <span className="flex items-center gap-2 rounded-full bg-[#dceee4] px-4 py-2 text-xs font-bold text-[#176b65]"><span className="size-2 animate-pulse rounded-full bg-[#176b65]" />All systems operational</span>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {dashStats.map(({ label, value, delta }) => (
          <div key={label} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5 shadow-sm">
            <p className="text-xs text-[#83918a]">{label}</p>
            <p className="mt-3 font-mono text-3xl font-medium text-[#1f312e]">{value}</p>
            <p className="mt-2 text-xs font-bold text-[#176b65]">{delta} this month</p>
          </div>
        ))}
      </div>
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.35fr_.65fr]">
        <CardWrap title="Platform activity" sub="Real-time control plane events">
          <div className="divide-y divide-[#edf0eb]">
            {activities.map(a => (
              <div key={a.event} className="flex items-center gap-4 px-6 py-4">
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
  const [items, setItems] = useState(learnersMock);
  const [selected, setSelected] = useState<string | null>(null);
  const toggle = (id: string) => setItems(c => c.map(u => u.id === id ? { ...u, status: u.status === 'Active' ? 'Suspended' : 'Active' } : u));
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
                  {[['ML Foundations', 100, 'Complete'], ['Deep Learning', 62, 'Current'], ['Transformers', 0, 'Upcoming'], ['AI Systems', 0, 'Upcoming']].map(([ph, pct, st]) => (
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
                  {[['ML Foundations', 84, 'Passed'], ['Python for ML', 92, 'Passed'], ['Neural Networks', null, 'Not started']].map(([t, s, st]) => (
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
  const [courses, setCourses] = useState(coursesMock);
  const toggle = (id: string) => setCourses(c => c.map(x => x.id === id ? { ...x, status: x.status === 'Published' ? 'Draft' : 'Published' } : x));
  return (
    <AdminShell active="learning">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Learning content</h1><p className="mt-2 text-sm text-[#718079]">Create, publish, and manage all learning content types.</p></div>
        <Btn><Plus size={14} />New course</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Courses', '24'], ['Videos', '312'], ['Articles', '198'], ['Projects', '48']].map(([l, v]) => (
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
                  <td className="px-4 py-3.5"><div className="flex flex-wrap gap-1">{c.skills.map(s => <Badge key={s}>{s}</Badge>)}</div></td>
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
  return (
    <AdminShell active="learning-paths">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Learning paths</h1><p className="mt-2 text-sm text-[#718079]">View, edit, and manage all AI-generated learning paths.</p></div>
        <Btn><Plus size={14} />Build path</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Total paths', '14,320'], ['Active', '8,421'], ['Completed', '4,291'], ['Archived', '1,608']].map(([l, v]) => (
          <div key={l} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5"><p className="text-xs text-[#83918a]">{l}</p><p className="mt-2 font-mono text-3xl text-[#1f312e]">{v}</p></div>
        ))}
      </div>
      <CardWrap title="All learning paths" sub="Learner paths — generated and manual" action={<Btn outline small>Export CSV</Btn>} className="mt-5">
        <div className="overflow-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <THead cols={['Goal', 'Learner', 'Progress', 'Phases', 'Status', 'Created', 'Actions']} />
            <tbody className="divide-y divide-[#edf0eb]">
              {pathsMock.map(p => (
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
  const [skills, setSkills] = useState(skillsMock);
  const toggleSkill = (name: string) => setSkills(c => c.map(s => s.name === name ? { ...s, status: s.status === 'Active' ? 'Disabled' : 'Active' } : s));
  return (
    <AdminShell active="skills">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Skill management</h1><p className="mt-2 text-sm text-[#718079]">Control the complete CS skill taxonomy powering recommendations and assessments.</p></div>
        <Btn><Plus size={14} />New skill</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Total skills', '486'], ['Active', '472'], ['Disabled', '14'], ['Categories', '9']].map(([l, v]) => (
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
                  <td className="px-4 py-3.5"><div className="flex flex-wrap gap-1">{s.related.map(r => <Badge key={r}>{r}</Badge>)}</div></td>
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
  const [items, setItems] = useState(assessmentsMock);
  const toggle = (id: string) => setItems(c => c.map(a => a.id === id ? { ...a, status: a.status === 'Published' ? 'Draft' : 'Published' } : a));
  return (
    <AdminShell active="assessments">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Assessment management</h1><p className="mt-2 text-sm text-[#718079]">Build, publish, and track all platform assessments and question banks.</p></div>
        <Btn><Plus size={14} />New assessment</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Total assessments', '312'], ['Published', '284'], ['Average score', '78%'], ['Total attempts', '42,931']].map(([l, v]) => (
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
  const [items, setItems] = useState(resourcesMock);
  const approve = (id: string) => setItems(c => c.map(r => r.id === id ? { ...r, status: 'Approved' } : r));
  const reject = (id: string) => setItems(c => c.filter(r => r.id !== id));
  return (
    <AdminShell active="resources">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Resource management</h1><p className="mt-2 text-sm text-[#718079]">Approve, reject, and curate all external learning resources.</p></div>
        <Btn><Plus size={14} />Add resource</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['Total resources', '18,492'], ['Approved', '18,241'], ['Pending review', '2'], ['Quality avg', '91%']].map(([l, v]) => (
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
                {recsMock.map(r => (
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
            {[['Documents indexed', '18,492'], ['Embeddings', '312,481'], ['Vector DB status', 'Operational'], ['Last indexed', '1 hour ago'], ['Search quality', '94%']].map(([label, val]) => (
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
  const weeks = ['Mar 04', 'Mar 11', 'Mar 18', 'Mar 25', 'Apr 01', 'Apr 08', 'Apr 15', 'Apr 22'];
  const signups = [210, 340, 280, 410, 390, 520, 480, 610];
  const active = [180, 290, 250, 370, 340, 460, 420, 560];
  const maxVal = Math.max(...signups);
  return (
    <AdminShell active="analytics">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[.2em] text-[#b17820]">Admin module</p><h1 className="mt-2 text-4xl font-bold tracking-[-.05em]">Platform analytics</h1><p className="mt-2 text-sm text-[#718079]">Understand learner engagement, path completion, and platform usage.</p></div>
        <Btn outline><TrendingUp size={14} />Export report</Btn>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-4">
        {[['New learners (month)', '1,284', '+18%'], ['Avg sessions/week', '4.2', '+0.8'], ['Path completion rate', '62%', '+4%'], ['Avg assessment score', '78%', '+5pts']].map(([l, v, d]) => (
          <div key={l} className="rounded-2xl border border-[#dbe4da] bg-[#fafbf8] p-5"><p className="text-xs text-[#83918a]">{l}</p><p className="mt-2 font-mono text-3xl text-[#1f312e]">{v}</p><p className="mt-2 text-xs font-bold text-[#176b65]">{d} vs last period</p></div>
        ))}
      </div>
      <CardWrap title="Learner signups and active users" sub="Weekly trend · last 8 weeks" className="mt-5">
        <div className="p-6">
          <div className="flex gap-4 mb-5 text-xs"><span className="flex items-center gap-1.5"><i className="size-2 rounded-full bg-[#176b65]" />Signups</span><span className="flex items-center gap-1.5"><i className="size-2 rounded-full bg-[#e8b044]" />Active</span></div>
          <div className="flex items-end gap-2 h-44 border-b border-l border-[#dbe4da]">
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
            {[['AI Engineer', 34], ['Data Scientist', 28], ['Frontend Developer', 18], ['Cloud Engineer', 11], ['ML Engineer', 9] as const].map(([g, pct]) => (
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
            {[['Python', 18420], ['Machine Learning', 12380], ['PyTorch', 8210], ['Docker', 7190], ['Transformers', 5640]].map(([s, n]) => (
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
  const [items, setItems] = useState(notifMock);
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
              {auditMock.map((a, i) => (
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
