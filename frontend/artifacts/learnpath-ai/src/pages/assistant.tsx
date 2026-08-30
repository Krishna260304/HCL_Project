import { useState, useEffect, useRef } from 'react';
import { Link } from 'wouter';
import {
  ArrowRight,
  Bot,
  Send,
  Sparkles,
  Zap,
  RefreshCw,
  Compass,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Target,
  Layers,
  HelpCircle,
  Code2,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import {
  chatService,
  profileService,
  learningPathService,
  skillService,
  type ChatMessage,
  type ChatConversation,
  type LearnerProfile,
  type LearningPath,
  type Skill,
} from '@/services/index';
import { SkeletonCard } from '@/components/states';
import { useToast } from '@/hooks/use-toast';

export default function Assistant() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [conversation, setConversation] = useState<ChatConversation | null>(null);
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [path, setPath] = useState<LearningPath | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  const init = async () => {
    setLoading(true);
    try {
      const [conv, prof, lp, sk] = await Promise.all([
        chatService.createConversation('Active Learning Coaching Session'),
        profileService.getProfile().catch(() => null),
        learningPathService.getLearningPath().catch(() => null),
        skillService.listSkills({ limit: 4 }).catch(() => []),
      ]);
      setConversation(conv);
      setProfile(prof);
      setPath(lp);
      setSkills(sk);

      const name = prof?.name || user?.email?.split('@')[0] || 'Alex';
      setMessages([
        {
          from: 'assistant',
          text: `Hello ${name}! I'm your AI Learning Coach, grounded in your active journey toward **${
            prof?.goals?.[0] || 'Full-Stack Web & AI Application Architect'
          }**.\n\nYou are currently in **Phase 3: Backend API Architecture & Security** (42% total path complete). How can I help you accelerate your progress today?`,
        },
      ]);
    } catch {
      setMessages([
        {
          from: 'assistant',
          text: "Hi! I'm your AI Learning Coach. Ask me anything about your active roadmap, skill gaps, or checkpoint projects.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    init();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const send = async (textToSend?: string) => {
    const text = textToSend ?? input;
    if (!text.trim() || sending) return;

    setInput('');
    setMessages((prev) => [...prev, { from: 'user', text }]);
    setSending(true);

    try {
      let convId = conversation?.id || (conversation as any)?._id;
      if (!convId || convId === 'default') {
        try {
          const newConv = await chatService.createConversation('Learning session');
          setConversation(newConv);
          convId = newConv.id || (newConv as any)._id;
        } catch {
          convId = '';
        }
      }
      const res = await chatService.sendMessage(convId || '', text);
      const reply =
        typeof res === 'object' && res !== null && 'reply' in res
          ? (res as { reply: string }).reply
          : String(res);

      setMessages((prev) => [...prev, { from: 'assistant', text: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          from: 'assistant',
          text: 'I apologize, but I encountered a temporary connection glitch. Please feel free to try your question again.',
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleReset = () => {
    const name = profile?.name || 'Alex';
    setMessages([
      {
        from: 'assistant',
        text: `Session reset. Ready for a new topic, ${name}! Ask me anything about your roadmap, architecture concepts, or checkpoint reviews.`,
      },
    ]);
    toast({
      title: 'Chat Session Reset 🔄',
      description: 'Conversation context has been cleared.',
    });
  };

  const quickPrompts = [
    {
      label: 'Why this sequence?',
      prompt: 'Why am I learning RESTful APIs and Security before Distributed Systems and Caching?',
    },
    {
      label: 'Explain Checkpoint',
      prompt: 'Explain the requirements for the Phase 3 REST & WebSocket Gateway checkpoint project.',
    },
    {
      label: 'My Skill Gaps',
      prompt: 'Summarize my top 3 active skill gaps and what resources will help me close them.',
    },
    {
      label: 'Quiz Me',
      prompt: 'Give me a diagnostic quiz question on JWT authentication security and token rotation.',
    },
  ];

  const currentPhase = path?.phases?.find((p) => p.status === 'current') || path?.phases?.[2];
  const priorityGaps = skills.filter((s) => (s.gap ?? 0) > 0).slice(0, 3);

  return (
    <div className="space-y-8 animate-rise">
      {/* ─── Top Header ────────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-end justify-between gap-5 border-b border-[#dbe4da] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] font-bold uppercase tracking-[.2em] text-[#b17820]">
              Curriculum Grounded Assistant
            </span>
            <span className="text-[#c5cdc5]">/</span>
            <span className="inline-flex items-center gap-1 text-xs font-bold text-[#176b65]">
              <Sparkles size={13} className="text-[#d89c2c]" /> Phase 3 Context Active
            </span>
          </div>

          <h1 className="display mt-2 text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">
            AI Learning Coach
          </h1>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-[#718079]">
            A personalized sounding board to untangle architecture concepts, choose optimal study paths, and prepare for diagnostic assessments.
          </p>
        </div>

        <button
          onClick={handleReset}
          className="inline-flex items-center gap-1.5 rounded-xl border border-[#ccd8ce] bg-[#fbfaf5] px-3.5 py-2 text-xs font-bold text-[#36504a] shadow-sm hover:border-[#176b65] hover:text-[#176b65] transition"
        >
          <RefreshCw size={13} /> Reset Chat
        </button>
      </div>

      {/* ─── Main Chat + Context Sidebar ────────────────────────────────────────── */}
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        {/* Chat Window */}
        <section className="flex min-h-[620px] flex-col overflow-hidden rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] shadow-sm">
          {/* Coach Window Top Bar */}
          <div className="flex items-center justify-between border-b border-[#e4e9e2] bg-[#f6f8f4] px-6 py-4">
            <div className="flex items-center gap-3">
              <span className="grid size-9 place-items-center rounded-xl bg-[#dceee4] text-[#176b65] shadow-sm">
                <Bot size={18} />
              </span>
              <div>
                <p className="text-sm font-bold text-[#20322f]">Adaptive Path Coach</p>
                <p className="text-[11px] text-[#83918a]">
                  Grounded in your 5-phase roadmap & verified assessment scores
                </p>
              </div>
            </div>

            <span className="inline-flex items-center gap-1.5 rounded-full bg-[#dceee4] px-2.5 py-1 text-[11px] font-bold text-[#176b65]">
              <span className="size-2 rounded-full bg-[#176b65] animate-pulse" /> Live Grounding
            </span>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 space-y-5 overflow-auto p-6 md:p-7">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${
                    m.from === 'user'
                      ? 'rounded-br-sm bg-[#176b65] text-[#f7f5ed] shadow-sm'
                      : 'rounded-bl-sm border border-[#dbe4da] bg-white text-[#36504a] shadow-sm space-y-2'
                  }`}
                >
                  {m.from === 'assistant' && (
                    <div className="flex items-center gap-1.5 font-mono text-[10px] font-bold uppercase tracking-wider text-[#b17820] mb-1">
                      <Sparkles size={11} /> AI Coach Response
                    </div>
                  )}

                  <div className="whitespace-pre-wrap">{m.text}</div>

                  {m.from === 'assistant' && (
                    <div className="pt-2 border-t border-[#e8ede4] flex items-center justify-between text-[10px] text-[#88958e] font-mono">
                      <span>Ref: Phase 3 Architecture & Skill Matrix</span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {sending && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-sm border border-[#dbe4da] bg-white px-5 py-4 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#718079]">
                    <Sparkles size={14} className="text-[#edbc55] animate-spin" />
                    <span>Analyzing your roadmap context...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Quick-Prompt Chips & Input Box */}
          <div className="border-t border-[#e4e9e2] bg-[#f9faf7] p-4 md:p-5 space-y-3">
            {/* Quick Prompt Chips */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] font-bold text-[#718079] flex items-center gap-1 mr-1 font-mono">
                <Zap size={12} className="text-[#d89c2c]" /> Suggested:
              </span>
              {quickPrompts.map((qp) => (
                <button
                  key={qp.label}
                  onClick={() => send(qp.prompt)}
                  disabled={sending}
                  className="rounded-lg border border-[#ccd8ce] bg-white px-2.5 py-1 text-[11px] font-bold text-[#40534d] hover:border-[#176b65] hover:text-[#176b65] transition shadow-xs disabled:opacity-50"
                >
                  {qp.label}
                </button>
              ))}
            </div>

            {/* Input Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                send();
              }}
              className="flex gap-2.5"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={sending}
                placeholder="Ask about your roadmap, explain an architecture concept, or quiz a skill..."
                className="min-w-0 flex-1 rounded-xl border border-[#ccd8ce] bg-white px-4 py-3 text-sm outline-none focus:border-[#176b65] transition disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={sending || !input.trim()}
                aria-label="Send message to AI coach"
                className="grid size-12 shrink-0 place-items-center rounded-xl bg-[#176b65] text-white hover:bg-[#115a55] transition disabled:opacity-50 shadow-sm"
              >
                <Send size={17} />
              </button>
            </form>
          </div>
        </section>

        {/* Learner Context Sidebar */}
        <aside className="space-y-5">
          {/* Active Context Card */}
          <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-[#e4e9e2] pb-3">
              <Compass size={16} className="text-[#176b65]" />
              <h2 className="display text-lg font-bold text-[#20322f]">Active Context</h2>
            </div>

            <div className="space-y-3.5 text-xs">
              <div>
                <p className="font-mono text-[10px] uppercase font-bold text-[#88958e]">Destination Goal</p>
                <p className="font-bold text-[#20322f] mt-0.5 leading-snug">
                  {profile?.goals?.[0] || path?.goal || 'Full-Stack Web & AI Architect'}
                </p>
              </div>

              <div>
                <p className="font-mono text-[10px] uppercase font-bold text-[#88958e]">Current Phase</p>
                <p className="font-bold text-[#176b65] mt-0.5">
                  {currentPhase?.title || 'Phase 3: Backend API Architecture'}
                </p>
              </div>

              <div>
                <p className="font-mono text-[10px] uppercase font-bold text-[#88958e]">Weekly Study Pace</p>
                <p className="font-bold text-[#40534d] mt-0.5">
                  {profile?.available_hours || 10} hours / week
                </p>
              </div>
            </div>

            <Link
              href="/profile"
              className="mt-2 flex items-center justify-between text-xs font-bold text-[#176b65] hover:underline pt-2 border-t border-[#e4e9e2]"
            >
              <span>Edit learner profile</span>
              <ArrowRight size={13} />
            </Link>
          </section>

          {/* Active Priority Gaps Card */}
          <section className="rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-2 border-b border-[#e4e9e2] pb-3">
              <Target size={16} className="text-[#d89c2c]" />
              <h3 className="display text-base font-bold text-[#20322f]">Coach Focus Gaps</h3>
            </div>

            <div className="space-y-2.5">
              {priorityGaps.map((s) => (
                <div
                  key={s.id ?? s.name}
                  className="rounded-xl border border-[#e3e8e0] bg-white p-3 space-y-1"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-[#36504a]">{s.name}</span>
                    <span className="text-[10px] font-mono font-bold text-[#a04b3e]">
                      Gap: {s.gap}%
                    </span>
                  </div>
                  <div className="h-1.5 rounded-full bg-[#e3e9e1] overflow-hidden">
                    <div
                      className="h-full bg-[#d89c2c] rounded-full"
                      style={{ width: `${s.verified_score ?? s.self_score ?? 40}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <Link
              href="/skills"
              className="flex items-center justify-between text-xs font-bold text-[#176b65] hover:underline pt-2"
            >
              <span>View full skill matrix</span>
              <ArrowRight size={13} />
            </Link>
          </section>
        </aside>
      </div>
    </div>
  );
}
