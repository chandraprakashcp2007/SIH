import React, { useEffect, useRef, useState } from 'react';
import { Bot, Clipboard, ExternalLink, History, Plus, Send, Square, Trash2, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { createCopilotSession, deleteCopilotSession, fetchCopilotMessages, fetchCopilotSessions, streamCopilotChat } from '../../services/api';

type Message = { role: 'user' | 'assistant'; text: string; timestamp: string; sources?: string[]; mode?: string; dataMode?: string };
const welcome: Message = { role: 'assistant', text: 'PRAHARI Copilot is ready. Ask about live risk, alerts, gateway health, evidence, or system operation.', timestamp: new Date().toISOString(), mode: 'LOCAL_ASSISTANT', dataMode: 'SIMULATION' };

export const CopilotDrawer: React.FC = () => {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([welcome]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState('');
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const refreshSessions = () => fetchCopilotSessions().then(setSessions).catch(() => setSessions([]));
  useEffect(() => { if (open) refreshSessions(); }, [open]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, status]);

  const newChat = async () => {
    const session = await createCopilotSession('Operational Inquiry');
    setSessionId(session.id); setMessages([welcome]); refreshSessions();
  };
  const clearChat = async () => {
    if (sessionId) await deleteCopilotSession(sessionId);
    setSessionId(null); setMessages([welcome]); refreshSessions();
  };
  const loadSession = async (id: string) => {
    const history = await fetchCopilotMessages(id);
    setSessionId(id);
    setMessages(history.map((item: any) => ({ role: item.role, text: item.content, timestamp: item.created_at, sources: item.sources, mode: item.provider, dataMode: item.data_mode })));
  };

  const send = async (suggestion?: string) => {
    const query = (suggestion || input).trim();
    if (!query || streaming) return;
    setInput(''); setStreaming(true); setStatus('Checking live telemetry…');
    setMessages((old) => [...old, { role: 'user', text: query, timestamp: new Date().toISOString() }, { role: 'assistant', text: '', timestamp: new Date().toISOString(), sources: [] }]);
    const controller = new AbortController(); abortRef.current = controller;
    try {
      await streamCopilotChat(query, sessionId, controller.signal, (event, data) => {
        if (event === 'status') setStatus(data.message);
        if (event === 'source') setMessages((old) => old.map((m, i) => i === old.length - 1 ? { ...m, sources: [...(m.sources || []), data.source] } : m));
        if (event === 'token') setMessages((old) => old.map((m, i) => i === old.length - 1 ? { ...m, text: m.text + data.text } : m));
        if (event === 'complete') {
          setSessionId(data.session_id); setStatus('');
          setMessages((old) => old.map((m, i) => i === old.length - 1 ? { ...m, mode: data.mode, dataMode: data.data_mode } : m));
        }
      });
      refreshSessions();
    } catch (error: any) {
      if (error?.name !== 'AbortError') setMessages((old) => old.map((m, i) => i === old.length - 1 ? { ...m, text: 'Local Assistant is temporarily unavailable. Retry when the backend is reachable.' } : m));
    } finally { setStreaming(false); setStatus(''); abortRef.current = null; }
  };

  const deepLinks = (text: string) => [
    text.includes('JALA-01') && ['/nodes/JALA-01', 'Open JALA'],
    text.includes('AGNI-02') && ['/nodes/AGNI-02', 'Open AGNI'],
    text.includes('BHUMI-03') && ['/nodes/BHUMI-03', 'Open BHUMI'],
  ].filter(Boolean) as string[][];

  return <>
    <button onClick={() => setOpen(!open)} aria-label="Open PRAHARI Copilot" className="fixed bottom-4 right-4 z-40 w-14 h-14 rounded-full bg-accent-ai text-white shadow-2xl grid place-items-center transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-white"><Bot className="w-7 h-7"/><span className="absolute top-0 right-0 w-3 h-3 rounded-full bg-hazard-normal border-2 border-bg-primary"/></button>
    {open && <aside aria-label="PRAHARI Copilot" className="fixed inset-x-0 bottom-0 sm:inset-x-auto sm:right-4 sm:bottom-20 z-50 w-full sm:w-[440px] h-[85vh] sm:h-[620px] sm:max-h-[calc(100vh-110px)] bg-bg-secondary border border-border-subtle sm:rounded-lg shadow-2xl flex flex-col overflow-hidden">
      <header className="p-3 bg-bg-surface border-b border-border-subtle flex items-center justify-between">
        <div><div className="flex items-center gap-2 font-bold text-xs"><Bot className="w-5 h-5 text-accent-ai"/>PRAHARI COPILOT</div><div className="text-[10px] text-text-muted">Grounded operational assistant</div></div>
        <div className="flex gap-1"><button onClick={newChat} title="New chat" aria-label="New chat" className="p-2 hover:bg-bg-elevated"><Plus className="w-4 h-4"/></button><button onClick={clearChat} title="Clear chat" aria-label="Clear chat" className="p-2 hover:bg-bg-elevated"><Trash2 className="w-4 h-4"/></button><button onClick={() => setOpen(false)} aria-label="Close Copilot" className="p-2 hover:bg-bg-elevated"><X className="w-4 h-4"/></button></div>
      </header>
      {sessions.length > 0 && <div className="border-b border-border-subtle px-3 py-2 flex gap-2 overflow-x-auto"><History className="w-4 h-4 shrink-0 text-text-muted"/>{sessions.slice(0,5).map((s) => <button key={s.id} onClick={() => loadSession(s.id)} className="text-[10px] whitespace-nowrap px-2 py-1 border border-border-subtle hover:border-accent-ai">{s.title}</button>)}</div>}
      <div className="flex-1 overflow-y-auto p-3 space-y-3" aria-live="polite">
        {messages.map((m, i) => <article key={i} className={m.role === 'user' ? 'ml-auto max-w-[85%]' : 'mr-auto max-w-[92%]'}>
          <div className={m.role === 'user' ? 'bg-accent-info text-bg-primary p-3 text-xs' : 'bg-bg-surface border border-border-subtle p-3 text-xs whitespace-pre-wrap leading-relaxed'}>{m.text || (streaming && i === messages.length - 1 ? '…' : '')}</div>
          {m.role === 'assistant' && <div className="mt-1 flex flex-wrap items-center gap-1 text-[9px] text-text-muted"><span>{new Date(m.timestamp).toLocaleTimeString()}</span>{m.mode && <span className="border border-border-subtle px-1">{m.mode}</span>}{m.dataMode && <span className="border border-border-subtle px-1">{m.dataMode}</span>}<button aria-label="Copy response" onClick={() => navigator.clipboard.writeText(m.text)} className="p-1 hover:text-text-primary"><Clipboard className="w-3 h-3"/></button></div>}
          {m.sources?.length ? <div className="mt-1 flex flex-wrap gap-1">{m.sources.map((s) => <span key={s} className="text-[9px] bg-accent-ai/10 text-accent-ai border border-accent-ai/30 px-1.5 py-0.5">{s}</span>)}</div> : null}
          {deepLinks(m.text).map(([path,label]) => <button key={path} onClick={() => {navigate(path); setOpen(false);}} className="mt-1 mr-1 text-[10px] text-accent-info inline-flex items-center gap-1">{label}<ExternalLink className="w-3 h-3"/></button>)}
        </article>)}
        {status && <div className="text-[11px] text-accent-ai animate-pulse">{status}</div>}<div ref={endRef}/>
      </div>
      <div className="px-3 py-2 border-t border-border-subtle flex gap-2 overflow-x-auto">{['How is the system?','Any active alerts?','gateway okay ah','Why is JALA critical?'].map((q) => <button key={q} onClick={() => send(q)} className="text-[10px] whitespace-nowrap border border-border-subtle px-2 py-1 hover:border-accent-ai">{q}</button>)}</div>
      <div className="p-3 bg-bg-surface border-t border-border-subtle flex gap-2"><label className="sr-only" htmlFor="copilot-input">Ask PRAHARI Copilot</label><input id="copilot-input" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && send()} placeholder="Ask about risk, alerts, nodes, or network…" className="flex-1 bg-bg-secondary border border-border-subtle px-3 py-2 text-xs focus:outline-none focus:border-accent-info"/>{streaming ? <button onClick={() => abortRef.current?.abort()} aria-label="Stop generation" className="p-2 bg-hazard-critical text-white"><Square className="w-4 h-4"/></button> : <button onClick={() => send()} disabled={!input.trim()} aria-label="Send message" className="p-2 bg-accent-ai text-white disabled:opacity-40"><Send className="w-4 h-4"/></button>}</div>
    </aside>}
  </>;
};
