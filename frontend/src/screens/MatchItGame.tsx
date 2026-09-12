import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { PillButton, PillTag } from '../components';
import { api } from '../lib/api';
import { enqueue, isNetworkError } from '../lib/offlineQueue';

const TINTS = ['bg-coral/25', 'bg-sky-blue/25', 'bg-mint/25', 'bg-gold/25'];
const FALLBACK_ICONS = ['🎪', '🍊', '🌿', '🏛️', '🎭', '🍇', '🌸', '🎵', '🐘', '💃', '🐅', '🌺'];

/** Board card as returned by GET /games/content-packs/{pack}/board. */
interface BoardCard {
  card_id: number;
  item_id: string;
  name_en: string;
  name_as?: string;
  image_url?: string;
}

interface Board {
  pack_id: string;
  pack_name: string;
  difficulty_level: number;
  pair_count: number;
  total_cards: number;
  cards: BoardCard[];
}

/** Client-side view of a card, keyed by its position in the shuffled deck. */
interface CardState {
  card: BoardCard;
  flipped: boolean;
  matched: boolean;
}

export default function MatchItGame() {
  const [difficulty, setDifficulty] = useState(() => {
    const saved = Number(sessionStorage.getItem('smriti.match-it.difficulty'));
    return saved >= 1 && saved <= 3 ? saved : 1;
  });
  const [board, setBoard] = useState<Board | null>(null);
  const [cards, setCards] = useState<CardState[]>([]);
  const [selected, setSelected] = useState<number[]>([]); // deck indices
  const [moves, setMoves] = useState(0);
  const [pairsFound, setPairsFound] = useState(0);
  const [summary, setSummary] = useState<{ accuracy_pct: number; avg_response_time_ms: number } | null>(null);
  const [loadError, setLoadError] = useState('');
  const flipStart = useRef<number>(0);
  const deckRef = useRef<HTMLDivElement>(null);

  // Adapt difficulty across sessions: ≥90% accuracy bumps up, <50% eases down
  // (mirrors the backend's rule-based engine for offline play).
  const adaptDifficulty = (accuracyPct: number) => {
    let next = difficulty;
    if (accuracyPct >= 90 && difficulty < 3) next = difficulty + 1;
    else if (accuracyPct < 50 && difficulty > 1) next = difficulty - 1;
    if (next !== difficulty) {
      sessionStorage.setItem('smriti.match-it.difficulty', String(next));
    }
    setDifficulty(next);
  };

  // Pack list (for a picker once the board loads poorly) — fetched once.
  const { data: packs } = useQuery({
    queryKey: ['content-packs'],
    queryFn: async () => (await api.get('/games/content-packs')).data as { id: string; name: string }[],
  });

  const startSession = useMutation({
    mutationFn: () => api.post('/games/sessions', {
      game_type: 'match_it',
      difficulty_level: difficulty,
      content_pack_id: board?.pack_id,
    }),
    onSuccess: (d) => {
      // Board cards were generated against this session's difficulty; queue
      // is not needed here — actions flow through recordAction below.
      setSessionId(d.data.session_id);
    },
    onError: (err) => {
      if (isNetworkError(err)) setOffline(true);
    },
  });

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [offline, setOffline] = useState(false);

  // Load board + start session when difficulty changes
  useEffect(() => {
    let cancelled = false;
    setBoard(null); setCards([]); setSelected([]); setMoves(0); setPairsFound(0);
    setSummary(null); setLoadError(''); setSessionId(null); setOffline(false);

    api.get(`/games/content-packs/festivals_ner/board`, { params: { difficulty_level: difficulty } })
      .then((res) => {
        if (cancelled) return;
        const b = res.data as Board;
        setBoard(b);
        setCards(b.cards.map((c) => ({ card: c, flipped: false, matched: false })));
        startSession.mutate();
      })
      .catch((err) => {
        if (cancelled) return;
        if (isNetworkError(err)) {
          setOffline(true);
          // Offline fallback: synthesize a local deck so the elder can still play.
          const local: Board = {
            pack_id: 'local', pack_name: 'Offline', difficulty_level: difficulty,
            pair_count: difficulty === 1 ? 2 : difficulty === 2 ? 4 : 6,
            total_cards: (difficulty === 1 ? 2 : difficulty === 2 ? 4 : 6) * 2,
            cards: Array.from({ length: (difficulty === 1 ? 2 : difficulty === 2 ? 4 : 6) * 2 }, (_, i) => ({
              card_id: i + 1, item_id: `local_${Math.floor(i / 2)}`,
              name_en: `Item ${Math.floor(i / 2) + 1}`,
            })),
          };
          setBoard(local);
          setCards(local.cards.map((c) => ({ card: c, flipped: false, matched: false })));
        } else {
          setLoadError('Could not load the game board. Please try again.');
        }
      });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [difficulty]);

  const recordAction = async (body: Record<string, unknown>) => {
    if (!sessionId) return;
    try {
      await api.post(`/games/sessions/${sessionId}/actions`, body);
    } catch (err) {
      if (isNetworkError(err)) enqueue({ kind: 'game-action', sessionId, body });
    }
  };

  const completeSession = async () => {
    if (!sessionId) return;
    try {
      const { data } = await api.post(`/games/sessions/${sessionId}/complete`);
      setSummary(data);
      // Server-computed accuracy drives the cross-session difficulty ladder.
      if (typeof data?.accuracy_pct === 'number') adaptDifficulty(data.accuracy_pct);
    } catch (err) {
      if (isNetworkError(err)) enqueue({ kind: 'game-complete', sessionId });
    }
  };

  const handleFlip = (idx: number) => {
    if (selected.length >= 2) return;
    const card = cards[idx];
    if (!card || card.flipped || card.matched) return;

    if (selected.length === 0) {
      flipStart.current = Date.now();
      setCards((prev) => prev.map((c, i) => (i === idx ? { ...c, flipped: true } : c)));
      setSelected([idx]);
      // First flip is informational — no is_correct flag.
      recordAction({ action_type: 'flip_card', action_data: { card_id: card.card.card_id, item_id: card.card.item_id } });
      return;
    }

    // Second flip — resolve the pair.
    const first = selected[0];
    setCards((prev) => prev.map((c, i) => (i === idx ? { ...c, flipped: true } : c)));
    setSelected([first, idx]);
    const isMatch = cards[first].card.item_id === card.card.item_id;
    const responseMs = Date.now() - flipStart.current;
    setMoves((m) => m + 1);

    void recordAction({
      action_type: 'flip_card',
      action_data: { card_id: card.card.card_id, item_id: card.card.item_id },
      is_correct: isMatch,
      response_time_ms: responseMs,
    });

    const delay = isMatch ? 450 : 900;
    setTimeout(() => {
      setCards((prev) => {
        const next = prev.map((c, i) =>
          i === first || i === idx
            ? { ...c, flipped: isMatch, matched: isMatch }
            : c,
        );
        if (next.every((c) => c.matched)) {
          // All pairs found — completion fires inside the state setter to
          // avoid a second render pass.
          setTimeout(() => void completeSession(), 50);
        }
        return next;
      });
      setSelected([]);
      if (isMatch) setPairsFound((p) => p + 1);
    }, delay);
  };

  // Keyboard play: arrow keys + Enter to flip (a11y for tremor/motor needs).
  useEffect(() => {
    const el = deckRef.current;
    if (!el) return;
    el.tabIndex = 0;
  }, [board]);

  const cols = difficulty === 1 ? 'grid-cols-2' : 'grid-cols-4';
  const done = cards.length > 0 && cards.every((c) => c.matched);

  /** Restart at a (possibly new) level without reloading the page — a reload
   *  would drop the in-memory auth tokens. Bumping difficulty re-runs the
   *  board effect, which resets all round state. */
  const playAgain = (level: number) => {
    setMoves(0); setPairsFound(0); setSelected([]); setSummary(null);
    setDifficulty(level);
    sessionStorage.setItem('smriti.match-it.difficulty', String(level));
  };

  if (loadError) {
    return (
      <div className="flex flex-col items-center gap-8 py-20 text-center">
        <h1 className="font-heading text-heading tracking-heading leading-heading text-off-black">Match It</h1>
        <p className="font-mono text-body-lg text-graphite">{loadError}</p>
        <PillButton variant="secondary" onClick={() => setDifficulty(difficulty)}>TRY AGAIN</PillButton>
        <Link to="/patient" className="font-mono text-body-sm uppercase text-off-black underline">Back home</Link>
      </div>
    );
  }

  if (done) {
    return (
      <div className="flex flex-col items-center gap-8 py-20 text-center">
        <h1 className="font-heading text-heading-lg tracking-heading-lg leading-heading-lg text-off-black">Well done!</h1>
        <p className="font-mono text-body-lg text-graphite">You matched all {cards.length / 2} pairs in {moves} moves.</p>
        {summary && (
          <p className="font-mono text-body-lg text-graphite">
            Accuracy {summary.accuracy_pct}% · Average time {Math.round(summary.avg_response_time_ms / 100) / 10}s
          </p>
        )}
        {offline && <PillTag icon="⌁">SAVED FOR SYNC</PillTag>}
        <div className="flex gap-4">
          <PillButton variant="primary" arrow onClick={() => playAgain(difficulty)}>PLAY AGAIN</PillButton>
          <PillButton variant="ghost" onClick={() => playAgain(difficulty === 3 ? 1 : difficulty + 1)}>
            {difficulty === 3 ? 'EASIER LEVEL' : 'HARDER LEVEL'}
          </PillButton>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-heading text-subheading tracking-subheading leading-subheading text-off-black">Match It</h1>
          {board && <p className="mt-1 font-mono text-body-lg tracking-body-lg text-graphite">{board.pack_name}</p>}
        </div>
        <span className="font-mono text-body-lg text-off-black">
          {pairsFound}/{board?.pair_count ?? '–'}
        </span>
      </div>

      {offline && (
        <p className="mb-6 font-mono text-body-sm text-crimson">Offline — this round will sync when you reconnect.</p>
      )}

      <div ref={deckRef} className={`no-select fit-viewport grid ${cols} gap-3 sm:gap-4`}>
        {cards.map((card, idx) => {
          const pairIdx = card.card.item_id.split('').reduce((a, ch) => a + ch.charCodeAt(0), 0) % TINTS.length;
          const tint = TINTS[pairIdx];
          const icon = FALLBACK_ICONS[pairIdx];
          return (
            <button
              key={`${card.card.card_id}-${idx}`}
              type="button"
              onClick={() => handleFlip(idx)}
              disabled={card.matched}
              aria-label={card.flipped || card.matched ? `Card ${card.card.name_en}` : 'Hidden card'}
              className={`match-card aspect-square min-h-14 rounded-cards border cursor-pointer flex flex-col items-center justify-center gap-2 transition-all ${
                card.matched
                  ? 'border-lake-blue bg-parchment'
                  : card.flipped
                    ? `${tint} border-ash shadow-md`
                    : 'border-ash bg-parchment'
              }`}
            >
              {(card.flipped || card.matched) && (
                <>
                  <span className="text-4xl" aria-hidden="true">{icon}</span>
                  <span className="font-mono text-body-lg text-off-black">{card.card.name_en}</span>
                </>
              )}
            </button>
          );
        })}
      </div>

      {packs && packs.length > 0 && cards.length === 0 && (
        <p className="mt-8 text-center font-mono text-body-sm text-graphite">Loading board…</p>
      )}
    </div>
  );
}
