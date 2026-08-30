import { useState, useEffect, useRef } from 'react';
import { ArrowRight, Bot, Send } from 'lucide-react';
import { Link } from 'wouter';
import { useAuth } from '@/context/AuthContext';
import { chatService, profileService, type ChatMessage, type ChatConversation, type LearnerProfile } from '@/services/index';

export default function Assistant() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [conversation, setConversation] = useState<ChatConversation | null>(null);
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const init = async () => {
      try {
        const [conv, prof] = await Promise.all([
          chatService.createConversation('Learning session'),
          profileService.getProfile().catch(() => null),
        ]);
        setConversation(conv);
        setProfile(prof);
        setMessages([{ from: 'assistant', text: `Hi ${prof?.name ?? user?.email?.split('@')[0] ?? 'there'}. I'm here to help with your learning path. What would you like to explore today?` }]);
      } catch {
        setMessages([{ from: 'assistant', text: "Hi! I'm your learning assistant. Ask me anything about your path." }]);
      }
    };
    init();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async (text = input) => {
    if (!text.trim() || sending) return;
    setInput('');
    setMessages(prev => [...prev, { from: 'user', text }]);
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
      const reply = typeof res === 'object' && res && 'reply' in res ? (res as { reply: string }).reply : String(res);
      setMessages(prev => [...prev, { from: 'assistant', text: reply }]);
    } catch (e) {
      setMessages(prev => [...prev, { from: 'assistant', text: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setSending(false);
    }
  };

  const prompts = ['Explain my current phase', 'What should I build next?', 'Quiz me on my weakest skill'];

  return (
    <>
      <div className="mb-8 animate-rise">
        <p className="mono mb-2 text-[10px] uppercase tracking-[.2em] text-[#b17820]">Your learning companion</p>
        <h1 className="display text-4xl font-bold tracking-[-.05em] text-[#20322f] md:text-5xl">Ask your coach</h1>
        <p className="mt-3 text-sm leading-6 text-[#718079]">A calm place to untangle concepts, choose a next step, or think out loud.</p>
      </div>
      <div className="grid gap-5 lg:grid-cols-[1fr_280px]">
        <section className="flex min-h-[570px] flex-col overflow-hidden rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] shadow-sm">
          <div className="flex items-center gap-3 border-b border-[#e4e9e2] px-6 py-4">
            <span className="grid size-9 place-items-center rounded-xl bg-[#dceee4] text-[#176b65]"><Bot size={18} /></span>
            <div>
              <p className="text-sm font-bold">Path coach</p>
              <p className="text-[10px] text-[#83918a]">Connected to your backend learning profile</p>
            </div>
            <span className="ml-auto flex items-center gap-1.5 text-[10px] font-bold text-[#176b65]">
              <span className="size-1.5 rounded-full bg-[#176b65]" /> Live
            </span>
          </div>
          <div className="flex-1 space-y-5 overflow-auto p-6">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-6 ${m.from === 'user' ? 'rounded-br-md bg-[#176b65] text-[#f7f5ed]' : 'rounded-bl-md bg-[#eef2ea] text-[#40534d]'}`}>
                  {m.text}
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-md bg-[#eef2ea] px-4 py-3">
                  <span className="flex gap-1">{[0,1,2].map(i => <span key={i} className="size-2 animate-bounce rounded-full bg-[#9aa7a0]" style={{ animationDelay: `${i * 150}ms` }} />)}</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <div className="border-t border-[#e4e9e2] p-4">
            <div className="mb-3 flex flex-wrap gap-2">
              {prompts.map(p => (
                <button key={p} onClick={() => send(p)} disabled={sending}
                  className="rounded-lg border border-[#dbe4da] px-3 py-1.5 text-[11px] font-bold text-[#61716c] hover:border-[#176b65] hover:text-[#176b65] disabled:opacity-50">
                  {p}
                </button>
              ))}
            </div>
            <form onSubmit={e => { e.preventDefault(); send(); }} className="flex gap-2">
              <input value={input} onChange={e => setInput(e.target.value)} disabled={sending}
                placeholder="Ask about your path…"
                className="min-w-0 flex-1 rounded-xl border border-[#ccd8ce] bg-[#f9f9f3] px-4 py-3 text-sm outline-none focus:border-[#176b65] disabled:opacity-50" />
              <button type="submit" disabled={sending || !input.trim()}
                className="grid size-11 shrink-0 place-items-center rounded-xl bg-[#176b65] text-white disabled:opacity-50">
                <Send size={16} />
              </button>
            </form>
          </div>
        </section>

        {profile && (
          <section className="h-fit rounded-2xl border border-[#dbe4da] bg-[#fbfaf5] p-5 shadow-sm">
            <p className="mono text-[10px] uppercase tracking-widest text-[#b17820]">Learner context</p>
            <h2 className="display mt-3 text-xl font-bold">{profile.name}'s profile</h2>
            <div className="mt-5 space-y-4 text-xs">
              {profile.target_outcome && <div><p className="text-[#9aa7a0]">Destination</p><p className="mt-1 font-bold text-[#40534d]">{profile.target_outcome}</p></div>}
              {profile.available_hours && <div><p className="text-[#9aa7a0]">Available time</p><p className="mt-1 font-bold text-[#40534d]">{profile.available_hours}h per week</p></div>}
              {profile.timeline && <div><p className="text-[#9aa7a0]">Timeline</p><p className="mt-1 font-bold text-[#40534d]">{profile.timeline}</p></div>}
              {profile.experience_level && <div><p className="text-[#9aa7a0]">Experience</p><p className="mt-1 font-bold text-[#40534d]">{profile.experience_level}</p></div>}
            </div>
            <Link href="/profile" className="mt-6 flex items-center gap-2 text-xs font-bold text-[#176b65]">Edit context <ArrowRight size={14} /></Link>
          </section>
        )}
      </div>
    </>
  );
}
