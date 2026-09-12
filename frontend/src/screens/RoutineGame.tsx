import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { DndContext, closestCenter, type DragEndEvent } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { PillButton, PillTag } from '../components';
import { api } from '../lib/api';
import { enqueue, isNetworkError } from '../lib/offlineQueue';

const TINTS = ['bg-coral/25', 'bg-mint/25', 'bg-gold/25', 'bg-sky-blue/25'];

interface RoutineBoardItem {
  step_id: string;
  title_en: string;
  title_as?: string;
  approx_time?: string;
  icon?: string | null;
  hint?: string | null;
}

interface RoutineBoard {
  difficulty_level: number;
  step_count: number;
  has_hints: boolean;
  has_icons: boolean;
  shuffled_items: RoutineBoardItem[];
  correct_sequence: string[];
}

function SortableCard({ step, tint, wrong }: { step: RoutineBoardItem; tint: string; wrong: boolean }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: step.step_id });
  const style = { transform: CSS.Transform.toString(transform), transition };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-4 rounded-cards border p-6 min-h-14 ${
        wrong ? 'border-coral outline outline-2 outline-coral/50' : `border-ash ${tint}`
      }`}
    >
      {step.icon && (
        <span className="text-[64px] leading-none" aria-hidden="true">{step.icon}</span>
      )}
      <div className="flex-1">
        <p className="font-mono text-body-lg text-off-black">{step.title_en}</p>
        {step.approx_time && <p className="font-mono text-body-sm text-smoke mt-1">{step.approx_time}</p>}
      </div>
      {step.hint && <span className="font-mono text-body-sm text-graphite mr-2">{step.hint}</span>}
      <button
        type="button"
        {...attributes}
        {...listeners}
        aria-label={`Drag ${step.title_en}`}
        className="cursor-grab font-mono text-body-lg text-smoke p-2 min-h-14"
      >
        ☰
      </button>
    </div>
  );
}

export default function RoutineGame() {
  const navigate = useNavigate();
  const [difficulty, setDifficulty] = useState(1);
  const [steps, setSteps] = useState<RoutineBoardItem[]>([]);
  const [correctSequence, setCorrectSequence] = useState<string[]>([]);
  const [wrongIds, setWrongIds] = useState<Set<string>>(new Set());
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [summary, setSummary] = useState<{ accuracy_pct: number } | null>(null);
  const [offline, setOffline] = useState(false);
  const [loadError, setLoadError] = useState('');

  // Resolve the patient profile bound to this account (needed for the board).
  const { data: profile } = useQuery({
    queryKey: ['my-profile'],
    queryFn: async () => (await api.get('/patients/me')).data as { id: string; name: string },
  });

  // Load board + start session once the profile resolves.
  useEffect(() => {
    if (!profile?.id) return;
    let cancelled = false;
    setSteps([]); setWrongIds(new Set()); setSummary(null); setLoadError(''); setOffline(false);

    api.get(`/games/routine/board`, { params: { patient_id: profile.id, difficulty_level: difficulty } })
      .then((res) => {
        if (cancelled) return;
        const board = res.data as RoutineBoard;
        setSteps(board.shuffled_items);
        setCorrectSequence(board.correct_sequence);
        return api.post('/games/sessions', { game_type: 'routine_sequencing', difficulty_level: difficulty });
      })
      .then((res) => { if (res && !cancelled) setSessionId(res.data.session_id); })
      .catch((err) => {
        if (cancelled) return;
        if (isNetworkError(err)) {
          setOffline(true);
          // Offline fallback — the caregiver-personalized routine may not be
          // reachable, so show a plain shuffled deck the elder can still play.
          const fallback = [
            { step_id: 'wake_up', title_en: 'Wake up', icon: '🌅', approx_time: '06:00' },
            { step_id: 'brush_teeth', title_en: 'Brush teeth', icon: '🪥', approx_time: '06:30' },
            { step_id: 'take_medicine', title_en: 'Take medicine', icon: '💊', approx_time: '07:00' },
            { step_id: 'breakfast', title_en: 'Eat breakfast', icon: '🍚', approx_time: '07:30' },
          ] as RoutineBoardItem[];
          setSteps(fallback);
          setCorrectSequence(fallback.map((s) => s.step_id));
        } else {
          setLoadError('Could not load your routine. Please try again.');
        }
      });
    return () => { cancelled = true; };
  }, [profile?.id, difficulty]);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    setSteps((prev) => {
      const oldIdx = prev.findIndex((s) => s.step_id === active.id);
      const newIdx = prev.findIndex((s) => s.step_id === over.id);
      const next = [...prev];
      const [moved] = next.splice(oldIdx, 1);
      next.splice(newIdx, 0, moved);
      return next;
    });
    // Each placement is an action the backend understands.
    const position = steps.findIndex((s) => s.step_id === over.id);
    if (sessionId) {
      api.post(`/games/sessions/${sessionId}/actions`, {
        action_type: 'place_step',
        action_data: { position, step_id: active.id },
      }).catch((err) => {
        if (isNetworkError(err)) enqueue({ kind: 'game-action', sessionId: sessionId!, body: {
          action_type: 'place_step', action_data: { position, step_id: active.id },
        } });
      });
    }
  };

  const handleSubmit = async () => {
    const currentOrder = steps.map((s) => s.step_id);
    const wrong = new Set<string>();
    currentOrder.forEach((id, i) => { if (id !== correctSequence[i]) wrong.add(id); });
    setWrongIds(wrong);

    if (sessionId) {
      const body = {
        action_type: 'place_step',
        action_data: { order: currentOrder, submitted: true },
        is_correct: wrong.size === 0,
      };
      try {
        await api.post(`/games/sessions/${sessionId}/actions`, body);
        const { data } = await api.post(`/games/sessions/${sessionId}/complete`);
        setSummary(data);
      } catch (err) {
        if (isNetworkError(err)) {
          enqueue({ kind: 'game-action', sessionId, body });
          enqueue({ kind: 'game-complete', sessionId });
        }
      }
    }
  };

  const allCorrect = wrongIds.size === 0 && steps.length > 0 && summary !== null;

  if (loadError) {
    return (
      <div className="flex flex-col items-center gap-8 py-20 text-center">
        <h1 className="font-heading text-heading tracking-heading leading-heading text-off-black">Daily Routine</h1>
        <p className="font-mono text-body-lg text-graphite">{loadError}</p>
        <PillButton variant="secondary" onClick={() => setDifficulty(difficulty)}>TRY AGAIN</PillButton>
        <Link to="/patient" className="font-mono text-body-sm uppercase text-off-black underline">Back home</Link>
      </div>
    );
  }

  if (allCorrect) {
    return (
      <div className="flex flex-col items-center gap-8 py-20 text-center">
        <h1 className="font-heading text-heading-lg tracking-heading-lg leading-heading-lg text-off-black">Well done!</h1>
        <p className="font-mono text-body-lg text-graphite">Your routine is in the right order.</p>
        {summary && (
          <p className="font-mono text-body-lg text-graphite">Accuracy {summary.accuracy_pct}%</p>
        )}
        {offline && <PillTag icon="⌁">SAVED FOR SYNC</PillTag>}
        <div className="flex gap-4">
          <PillButton variant="primary" arrow onClick={() => { setSummary(null); setWrongIds(new Set()); setDifficulty(difficulty); }}>PLAY AGAIN</PillButton>
          <PillButton variant="ghost" onClick={() => navigate('/patient')}>HOME</PillButton>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="font-heading text-subheading tracking-subheading leading-subheading text-off-black mb-8">Daily Routine</h1>
      {offline && (
        <p className="mb-6 font-mono text-body-sm text-crimson">Offline — this round will sync when you reconnect.</p>
      )}
      <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={steps.map((s) => s.step_id)} strategy={verticalListSortingStrategy}>
          <div className="flex flex-col gap-4">
            {steps.map((step, i) => (
              <div key={step.step_id} className={wrongIds.has(step.step_id) ? 'rounded-cards outline outline-2 outline-coral/50' : ''}>
                <SortableCard step={step} tint={TINTS[i % TINTS.length]} wrong={wrongIds.has(step.step_id)} />
              </div>
            ))}
          </div>
        </SortableContext>
      </DndContext>
      <div className="mt-10 flex justify-center">
        <PillButton variant="primary" arrow onClick={handleSubmit} disabled={steps.length === 0}>CHECK MY ORDER</PillButton>
      </div>
    </div>
  );
}
