import { useState, useEffect } from 'react';
import { ArrowRight, Check, ListChecks } from 'lucide-react';
import { assessmentService, type Assessment, type AssessmentAttempt, type AssessmentResult } from '@/services/index';
import { SkeletonCard, ErrorState, EmptyState } from '@/components/states';

function questionKey(question: { id?: string; _id?: string }, index: number): string {
  return question.id ?? question._id ?? String(index);
}

function Tag({ children }: { children: React.ReactNode }) {
  return <span className="inline-flex rounded-lg px-2 py-1 text-[10px] font-bold bg-[#e3eee7] text-[#176b65]">{children}</span>;
}
function ProgressBar({ value }: { value: number }) {
  return <div className="h-2 overflow-hidden rounded-full bg-[#e3e9e1]"><div className="h-full rounded-full bg-[#176b65]" style={{ width: `${Math.min(value, 100)}%` }} /></div>;
}

export default function Assessments() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState<Assessment | null>(null);
  const [attempt, setAttempt] = useState<AssessmentAttempt | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [starting, setStarting] = useState(false);
  const [qIdx, setQIdx] = useState(0);

  const load = async () => {
    setLoading(true); setError(null);
    try { setAssessments(await assessmentService.listAssessments({})); }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to load assessments.'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const startAssessment = async (a: Assessment) => {
    setStarting(true);
    try {
      const att = await assessmentService.startAttempt(a.id);
      setActive(a); setAttempt(att); setAnswers({}); setResult(null); setQIdx(0);
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not start assessment.'); }
    finally { setStarting(false); }
  };

  const selectAnswer = (questionId: string, option: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: option }));
    const questions = attempt?.questions ?? [];
    if (qIdx < questions.length - 1) {
      setTimeout(() => setQIdx(q => q + 1), 300);
    }
  };

  const submit = async () => {
    if (!active || !attempt) return;
    setSubmitting(true);
    try {
      const res = await assessmentService.submitAttempt(active.id, attempt.attempt_id, answers);
      setResult(res);
    } catch (e) { setError(e instanceof Error ? e.message : 'Submission failed.'); }
    finally { setSubmitting(false); }
  };

  const reset = () => { setActive(null); setAttempt(null); setResult(null); setAnswers({}); setQIdx(0); load(); };

  if (loading) return <div className="space-y-3">{[1,2,3].map(i => <SkeletonCard key={i} rows={1} />)}</div>;
  if (error && !active) return <ErrorState title="Assessments unavailable" message={error} onRetry={load} />;

  // Result screen
  if (result && active) return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="w-full max-w-lg rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-8 text-center shadow-sm">
        <span className="mx-auto grid size-16 place-items-center rounded-full bg-[#dceee4] text-[#176b65]"><Check size={28} /></span>
        <p className="mono mt-6 text-xs uppercase tracking-widest text-[#b17820]">Assessment complete</p>
        <h2 className="display mt-3 text-4xl font-bold">Score: {result.score}%</h2>
        {result.passed !== undefined && <p className="mt-2 text-sm font-bold text-[#176b65]">{result.passed ? '✓ Passed' : 'Keep practicing'}</p>}
        {result.feedback && <p className="mt-4 text-sm leading-6 text-[#718079]">{result.feedback}</p>}
        {result.strengths && result.strengths.length > 0 && <div className="mt-4 text-left"><p className="text-xs font-bold text-[#176b65]">Strengths:</p><ul className="mt-1 list-inside list-disc text-xs text-[#718079]">{result.strengths.map(s => <li key={s}>{s}</li>)}</ul></div>}
        {result.weaknesses && result.weaknesses.length > 0 && <div className="mt-4 text-left"><p className="text-xs font-bold text-[#a04b3e]">Areas to improve:</p><ul className="mt-1 list-inside list-disc text-xs text-[#718079]">{result.weaknesses.map(w => <li key={w}>{w}</li>)}</ul></div>}
        <button onClick={reset} className="mt-7 inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-sm font-bold text-white">Back to assessments</button>
      </div>
    </div>
  );

  // Question screen
  if (active && attempt && attempt.questions.length > 0) {
    const q = attempt.questions[qIdx];
    const progress = (qIdx / attempt.questions.length) * 100;
    const allAnswered = attempt.questions.every((question, index) => answers[questionKey(question, index)]);
    const currentQuestionKey = questionKey(q, qIdx);
    return (
      <div className="mx-auto max-w-3xl">
        <div className="mb-4 flex items-center justify-between">
          <Tag>{active.topic ?? active.title}</Tag>
          <span className="text-xs text-[#83918a]">Question {qIdx + 1} of {attempt.questions.length}</span>
        </div>
        <ProgressBar value={progress} />
        <h2 className="display mt-10 text-3xl font-bold">{q.text}</h2>
        <div className="mt-7 space-y-3">
          {q.options.map((opt, i) => (
            <button key={opt} onClick={() => selectAnswer(currentQuestionKey, opt)}
              className={`flex w-full items-center gap-3 rounded-xl border p-4 text-left text-sm font-bold transition ${answers[currentQuestionKey] === opt ? 'border-[#176b65] bg-[#eef2ea] text-[#176b65]' : 'border-[#dbe4da] text-[#40534d] hover:border-[#176b65] hover:bg-[#eef2ea]'}`}>
              <span className="grid size-7 place-items-center rounded-lg bg-[#edf0eb] text-xs text-[#718079]">{String.fromCharCode(65 + i)}</span>
              {opt}
              {answers[currentQuestionKey] === opt && <Check size={14} className="ml-auto text-[#176b65]" />}
            </button>
          ))}
        </div>
        <div className="mt-8 flex items-center justify-between">
          {qIdx > 0 && <button onClick={() => setQIdx(q => q - 1)} className="text-sm font-bold text-[#718079]">← Back</button>}
          <div className="ml-auto flex gap-3">
            {qIdx < attempt.questions.length - 1 ? (
              <button onClick={() => setQIdx(q => q + 1)} disabled={!answers[currentQuestionKey]}
                className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-4 py-2.5 text-sm font-bold text-white disabled:opacity-50">
                Next <ArrowRight size={14} />
              </button>
            ) : (
              <button onClick={submit} disabled={submitting || !allAnswered}
                className="inline-flex items-center gap-2 rounded-xl bg-[#edbc55] px-4 py-2.5 text-sm font-bold text-[#20322f] disabled:opacity-50">
                {submitting ? 'Submitting…' : 'Submit answers'} <ArrowRight size={14} />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // List screen
  return (
    <>
      <div className="mb-8 animate-rise">
        <p className="mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Checkpoints, not judgments</p>
        <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Assessment history</h1>
        <p className="mt-3 text-sm leading-6 text-[#718079]">Use small assessments to turn confidence into evidence.</p>
      </div>
      {assessments.length === 0 ? (
        <EmptyState title="No assessments yet" description="Assessments will appear here once your learning path is generated." />
      ) : (
        <div className="grid gap-4">
          {assessments.map(a => (
            <section key={a.id} className="flex flex-wrap items-center gap-5 rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm md:p-6">
              <span className={`grid size-11 place-items-center rounded-xl ${a.latest_attempt?.status === 'passed' ? 'bg-[#dceee4] text-[#176b65]' : 'bg-[#fae9bb] text-[#a66c15]'}`}><ListChecks size={20} /></span>
              <div className="min-w-[180px] flex-1">
                <h2 className="font-bold text-[#40534d]">{a.title ?? a.topic}</h2>
                <p className="mt-1 text-xs text-[#83918a]">{a.questions_count ?? '?'} questions · {a.difficulty ?? 'Mixed'} · {a.latest_attempt?.date ?? 'Not started'}</p>
              </div>
              <div className="mr-4">
                <p className="mono text-xl text-[#20322f]">{a.latest_attempt?.score != null ? `${a.latest_attempt.score}%` : '—'}</p>
                <p className="text-[10px] uppercase tracking-wider text-[#9aa7a0]">{a.latest_attempt?.score != null ? 'latest score' : 'ready to take'}</p>
              </div>
              <button onClick={() => startAssessment(a)} disabled={starting}
                className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold ${a.latest_attempt?.status === 'passed' ? 'border border-[#cbd5ce] bg-[#fbfaf5] text-[#27403b]' : 'bg-[#edbc55] text-[#20322f]'} disabled:opacity-50`}>
                {starting ? 'Starting…' : a.latest_attempt?.status === 'passed' ? 'Retake' : 'Start checkpoint'} <ArrowRight size={14} />
              </button>
            </section>
          ))}
        </div>
      )}
    </>
  );
}
