import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'wouter';
import {
  Compass,
  LayoutDashboard,
  BookOpen,
  BriefcaseBusiness,
  Radar,
  TrendingUp,
  ListChecks,
  Bot,
  Bell,
  Menu,
  X,
  ChevronRight,
  LogOut,
  UserRound,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { profileService, notificationService, type LearnerProfile, type Notification } from '@/services/index';

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

const navItems = [
  { href: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  { href: '/learning-path', label: 'Learning path', icon: Compass },
  { href: '/resources', label: 'Resources', icon: BookOpen },
  { href: '/projects', label: 'Projects', icon: BriefcaseBusiness },
  { href: '/skills', label: 'Skills', icon: Radar },
  { href: '/progress', label: 'Progress', icon: TrendingUp },
];

const moreItems = [
  { href: '/assessments', label: 'Assessments', icon: ListChecks },
  { href: '/assistant', label: 'AI assistant', icon: Bot },
  { href: '/notifications', label: 'Notifications', icon: Bell },
];

function SideLink({
  href,
  label,
  icon: Icon,
  active,
  hasUnread = false,
  onClick,
}: {
  href: string;
  label: string;
  icon: React.ComponentType<{ size?: number }>;
  active: boolean;
  hasUnread?: boolean;
  onClick?: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={`mb-1 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition-colors ${
        active ? 'bg-[#edbc55] text-[#20322f]' : 'text-[#abc1b3] hover:bg-[#294b44] hover:text-[#f8f5eb]'
      }`}
      data-testid={`link-nav-${label.toLowerCase().replaceAll(' ', '-')}`}
    >
      <Icon size={17} />
      <span>{label}</span>
      {hasUnread && <span className="ml-auto size-2 rounded-full bg-[#edbc55] animate-pulse" />}
    </Link>
  );
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [location, setLocation] = useLocation();
  const { user, logout, connectionStatus } = useAuth();
  const [mobile, setMobile] = useState(false);
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    let mounted = true;
    profileService.getProfile()
      .then(p => { if (mounted) setProfile(p); })
      .catch(() => {});

    notificationService.listNotifications()
      .then(list => {
        if (mounted) {
          const unread = list.filter(n => !n.read).length;
          setUnreadCount(unread);
        }
      })
      .catch(() => {});

    const unsub = notificationService.onNew(() => {
      setUnreadCount(c => c + 1);
    });

    return () => {
      mounted = false;
      unsub();
    };
  }, []);

  const handleLogout = async () => {
    await logout();
    setLocation('/');
  };

  const displayName = profile?.name || user?.email?.split('@')[0] || 'Learner';
  const displayInitials = displayName
    .split(' ')
    .map((s: string) => s[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
  const targetTrack = profile?.goals?.[0] || 'Learner Track';

  return (
    <div className="min-h-[100dvh] bg-[#f3f4ed] text-[#20322f]">
      {/* Connection warning banner if disconnected */}
      {connectionStatus !== 'connected' && (
        <div className="bg-[#fae9bb] px-4 py-1.5 text-center text-xs font-bold text-[#93611a] border-b border-[#e3ce9c] flex items-center justify-center gap-2">
          <span className="size-2 rounded-full bg-[#e6a933] animate-ping" />
          {connectionStatus === 'reconnecting' ? 'Reconnecting to backend…' : 'Disconnected from backend server.'}
        </div>
      )}

      {/* Desktop Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[254px] flex-col border-r border-[#dbe4da] bg-[#203d38] text-[#deebe0] lg:flex">
        <div className="px-6 py-6">
          <Logo light />
        </div>

        <div className="px-3">
          <p className="font-mono mb-3 px-3 text-[10px] uppercase tracking-[.18em] text-[#88a99b]">Workspace</p>
          {navItems.map(item => (
            <SideLink key={item.href} {...item} active={location === item.href} />
          ))}

          <p className="font-mono mb-3 mt-8 px-3 text-[10px] uppercase tracking-[.18em] text-[#88a99b]">Keep learning</p>
          {moreItems.map(item => (
            <SideLink
              key={item.href}
              {...item}
              active={location === item.href}
              hasUnread={item.href === '/notifications' && unreadCount > 0}
            />
          ))}
        </div>

        <div className="mt-auto space-y-2 p-4">
          <Link
            href="/profile"
            className="flex items-center gap-3 rounded-2xl border border-[#47675e] bg-[#294b44] p-3 transition hover:bg-[#325a52]"
            data-testid="link-sidebar-profile"
          >
            <span className="grid size-9 place-items-center rounded-xl bg-[#edbc55] text-xs font-bold text-[#20322f]">
              {displayInitials || 'LP'}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-bold text-[#f8f5eb]">{displayName}</span>
              <span className="block truncate text-xs text-[#9eb8aa]">{targetTrack}</span>
            </span>
            <ChevronRight size={15} className="text-[#8da99b]" />
          </Link>

          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold text-[#abc1b3] hover:bg-[#294b44] hover:text-[#f8f5eb] transition"
            data-testid="button-logout"
          >
            <LogOut size={16} />
            Log out
          </button>
        </div>
      </aside>

      {/* Main content wrapper */}
      <div className="lg:pl-[254px]">
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex h-[70px] items-center justify-between border-b border-[#dbe4da] bg-[#f3f4ed]/90 px-5 backdrop-blur-md lg:px-9">
          <div className="flex items-center gap-3">
            <button onClick={() => setMobile(!mobile)} className="rounded-lg p-2 lg:hidden" data-testid="button-open-sidebar">
              <Menu size={20} />
            </button>
            <div className="lg:hidden">
              <Logo />
            </div>
            <div className="hidden items-center gap-2 text-sm text-[#7b8882] md:flex">
              <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</span>
              <span className="text-[#c5cdc5]">/</span>
              <span className="font-bold text-[#36504a]">Active Session</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/notifications"
              className="relative rounded-xl p-2.5 text-[#61716c] hover:bg-[#e4ebe2] transition"
              data-testid="link-header-notifications"
            >
              <Bell size={18} />
              {unreadCount > 0 && <span className="absolute right-2 top-2 size-2 rounded-full bg-[#e6a933]" />}
            </Link>
            <Link
              href="/assistant"
              className="hidden items-center gap-2 rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-3 py-2 text-xs font-bold text-[#36504a] sm:flex hover:border-[#176b65] transition"
              data-testid="link-header-assistant"
            >
              <Bot size={15} className="text-[#176b65]" /> Ask your AI coach
            </Link>
          </div>
        </header>

        {/* Mobile menu overlay */}
        {mobile && (
          <div className="fixed inset-0 z-50 bg-[#203d38] p-6 text-[#deebe0] lg:hidden flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <Logo light />
                <button onClick={() => setMobile(false)} data-testid="button-close-sidebar">
                  <X />
                </button>
              </div>
              <div className="mt-10 flex flex-col gap-1">
                {[...navItems, ...moreItems].map(item => (
                  <SideLink
                    key={item.href}
                    {...item}
                    active={location === item.href}
                    onClick={() => setMobile(false)}
                    hasUnread={item.href === '/notifications' && unreadCount > 0}
                  />
                ))}
              </div>
            </div>

            <div className="space-y-3 pt-6 border-t border-[#31574e]">
              <Link
                href="/profile"
                onClick={() => setMobile(false)}
                className="flex items-center gap-3 rounded-2xl bg-[#294b44] p-3 text-white"
              >
                <span className="grid size-9 place-items-center rounded-xl bg-[#edbc55] text-xs font-bold text-[#20322f]">
                  {displayInitials || 'LP'}
                </span>
                <span className="min-w-0">
                  <span className="block truncate text-sm font-bold">{displayName}</span>
                  <span className="block text-xs text-[#9eb8aa]">{targetTrack}</span>
                </span>
              </Link>

              <button
                onClick={() => { setMobile(false); handleLogout(); }}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold text-[#abc1b3]"
                data-testid="button-mobile-logout"
              >
                <LogOut size={16} />
                Log out
              </button>
            </div>
          </div>
        )}

        <main className="mx-auto max-w-[1440px] px-5 py-7 lg:px-9 lg:py-10">
          {children}
        </main>
      </div>
    </div>
  );
}
