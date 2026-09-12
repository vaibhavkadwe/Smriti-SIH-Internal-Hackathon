import { useState, useEffect, useRef } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

const LANGS = ['assamese', 'bengali', 'hindi', 'english'] as const;

interface Message {
  role: 'patient' | 'companion';
  text: string;
}

export default function VoiceCompanion() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [lang, setLang] = useState<string>('assamese');
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: profile } = useQuery({
    queryKey: ['my-profile'],
    queryFn: async () => (await api.get('/patients/me')).data as { id: string },
  });

  const send = useMutation({
    mutationFn: (message: string) =>
      api.post('/companion/chat/text', {
        patient_id: profile?.id,
        message,
        language: lang,
      }),
    onSuccess: (d, msg) => {
      setMessages((prev) => [
        ...prev,
        { role: 'patient', text: msg },
        { role: 'companion', text: d.data.reply_text || '…' },
      ]);
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        { role: 'companion', text: 'I could not hear you just now. Please try again.' },
      ]);
    },
  });

  // Companion greets first when the conversation starts.
  useEffect(() => {
    if (messages.length === 0 && profile) {
      setMessages([{ role: 'companion', text: 'Hello! I am Saathi, your companion. How are you feeling today?' }]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profile]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    setInput('');
    send.mutate(text);
  };

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-6">
      <h1 className="font-heading text-subheading tracking-subheading leading-subheading text-off-black text-center">
        Voice Companion
      </h1>

      {/* Language picker — ash borders; lake blue stays exclusive to the mic */}
      <div className="flex justify-center gap-2">
        {LANGS.map((l) => (
          <button
            key={l}
            type="button"
            onClick={() => setLang(l)}
            aria-pressed={lang === l}
            className={`rounded-tags border bg-parchment px-4 py-2 font-mono text-caption uppercase tracking-caption cursor-pointer transition-colors ${
              lang === l ? 'border-off-black text-off-black' : 'border-ash text-smoke'
            }`}
          >
            {l}
          </button>
        ))}
      </div>

      {/* Conversation — patient right (parchment/ash), companion left (periwinkle) */}
      <div ref={scrollRef} className="flex min-h-[320px] flex-col gap-4 overflow-y-auto rounded-cards border border-ash bg-parchment p-6">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'patient' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-cards px-6 py-4 font-mono text-body-lg leading-body-lg text-off-black ${
                m.role === 'patient' ? 'border border-ash bg-parchment' : 'bg-periwinkle-mist'
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {send.isPending && (
          <div className="flex justify-start">
            <div className="rounded-cards bg-periwinkle-mist px-6 py-4 font-mono text-body-lg text-off-black">…</div>
          </div>
        )}
      </div>

      {/* Text input + the single lake-blue mic CTA, centered */}
      <form onSubmit={handleSubmit} className="flex flex-col items-center gap-6">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message…"
          aria-label="Message"
          className="w-full rounded-cards border border-ash bg-parchment px-6 py-4 font-mono text-body-lg text-off-black outline-none min-h-14"
        />
        {/* Large circular mic button — 64px, lake blue (the ONLY lake-blue element) */}
        <button
          type="submit"
          disabled={send.isPending}
          aria-label="Send message"
          className="h-16 w-16 rounded-pills bg-lake-blue text-[28px] leading-none text-white cursor-pointer transition-colors hover:bg-[#1f49b3] disabled:opacity-50"
        >
          ◉
        </button>
      </form>
    </div>
  );
}
