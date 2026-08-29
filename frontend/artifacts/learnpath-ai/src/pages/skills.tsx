import { useState, useEffect } from 'react';
import { Gauge, ShieldCheck, Target } from 'lucide-react';
import { skillService, type Skill } from '@/services/index';
import { SkeletonTable, ErrorState, EmptyState } from '@/components/states';

function ProgressBar({ value, color = '#176b65' }: { value: number; color?: string }) {
  return <div className="h-2 overflow-hidden rounded-full bg-[#e3e9e1]"><div className="h-full rounded-full" style={{ width: `${Math.min(value, 100)}%`, background: color }} /></div>;
}
function Tag({ children, warm = false }: { children: React.ReactNode; warm?: boolean }) {
  return <span className={`inline-flex rounded-lg px-2 py-1 text-[10px] font-bold ${warm ? 'bg-[#fae9bb] text-[#93611a]' : 'bg-[#e3eee7] text-[#176b65]'}`}>{children}</span>;
}

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const data = await skillService.listSkills({});
      setSkills(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load skills.');
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const verified = skills.filter(s => s.verified_score && s.verified_score > 0 && (s.required_score ?? 0) <= s.verified_score);
  const gaps = skills.filter(s => (s.gap ?? 0) > 0);
  const avgConfidence = skills.length ? Math.round(skills.reduce((a, s) => a + (s.self_score ?? 0), 0) / skills.length) : 0;

  if (loading) return <div className="space-y-4"><SkeletonTable rows={5} cols={4} /></div>;
  if (error) return <ErrorState title="Skills unavailable" message={error} onRetry={load} />;
  if (skills.length === 0) return <EmptyState title="No skills data yet" description="Complete your onboarding to see your skill intelligence." />;

  return (
    <>
      <div className="mb-8 animate-rise">
        <p className="mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Evidence over guesswork</p>
        <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Skill intelligence</h1>
        <p className="mt-3 text-sm leading-6 text-[#718079]">Side-by-side: where you are, what the role needs, and how confident we are.</p>
      </div>

      <section className="overflow-hidden rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] shadow-sm">
        <div className="grid grid-cols-[1.3fr_.7fr_.7fr_.7fr] border-b border-[#e4e9e2] bg-[#f0f3ed] px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-[#84918a] md:grid-cols-[1.5fr_.7fr_.7fr_.7fr_.7fr]">
          <span>Skill</span><span>Current</span><span>Role-ready</span><span className="hidden md:block">Confidence</span><span>Status</span>
        </div>
        {skills.map((s, i) => (
          <button key={s.id ?? s.name} onClick={() => setInfo(info === (s.name) ? null : s.name)}
            className="grid w-full grid-cols-[1.3fr_.7fr_.7fr_.7fr] items-center border-b border-[#e8ece6] px-5 py-5 text-left last:border-0 hover:bg-[#f8f8f2] md:grid-cols-[1.5fr_.7fr_.7fr_.7fr_.7fr]">
            <div>
              <p className="text-sm font-bold text-[#40534d]">{s.name}</p>
              <div className="mt-2 max-w-[160px]">
                <ProgressBar value={s.verified_score ?? s.self_score ?? 0} color={(s.gap ?? 0) > 0 ? '#d89c2c' : '#176b65'} />
              </div>
              {info === s.name && (
                <div className="col-span-full mt-4 rounded-xl bg-[#eef2ea] p-3 text-xs leading-5 text-[#61716c]">
                  <span className="font-bold text-[#36504a]">Coach read: </span>
                  {(s.gap ?? 0) > 0
                    ? `This is ${s.gap} points from role-ready. It's the reason your current phase emphasizes practice.`
                    : 'Your verified signal is comfortably above the role threshold. Keep this warm through project work.'}
                </div>
              )}
            </div>
            <span className="mono text-sm text-[#61716c]">{s.verified_score ?? s.self_score ?? 0}</span>
            <span className="mono text-sm text-[#20322f]">{s.required_score ?? '—'}</span>
            <span className="hidden text-xs text-[#718079] md:block">{s.confidence ?? 'Unknown'}</span>
            <span><Tag warm={(s.gap ?? 0) > 0}>{s.status ?? ((s.gap ?? 0) > 0 ? 'Focus next' : 'On track')}</Tag></span>
          </button>
        ))}
      </section>

      <div className="mt-5 grid gap-5 md:grid-cols-3">
        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
          <Gauge className="text-[#176b65]" size={20} />
          <p className="mono mt-5 text-3xl text-[#20322f]">{avgConfidence}%</p>
          <p className="mt-1 text-xs text-[#718079]">path confidence</p>
        </section>
        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
          <ShieldCheck className="text-[#176b65]" size={20} />
          <p className="mono mt-5 text-3xl text-[#20322f]">{verified.length}</p>
          <p className="mt-1 text-xs text-[#718079]">verified strengths</p>
        </section>
        <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
          <Target className="text-[#d89c2c]" size={20} />
          <p className="mono mt-5 text-3xl text-[#20322f]">{gaps.length}</p>
          <p className="mt-1 text-xs text-[#718079]">priority gaps</p>
        </section>
      </div>
    </>
  );
}
