import { api } from './api';

/**
 * Offline sync queue — game actions, completions, and reminder acks that
 * failed on a network error are stored in sessionStorage and replayed in
 * order when connectivity returns. (Per the brief: no service worker needed.)
 */

export type QueuedItem =
  | { kind: 'game-action'; sessionId: string; body: Record<string, unknown> }
  | { kind: 'game-complete'; sessionId: string }
  | { kind: 'reminder-ack'; eventId: string; body: Record<string, unknown> };

const KEY = 'smriti.offline-queue';
const listeners = new Set<() => void>();

function read(): QueuedItem[] {
  try {
    return JSON.parse(sessionStorage.getItem(KEY) || '[]') as QueuedItem[];
  } catch {
    return [];
  }
}

function write(items: QueuedItem[]) {
  sessionStorage.setItem(KEY, JSON.stringify(items));
  listeners.forEach((l) => l());
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  listener();
  return () => listeners.delete(listener);
}

export function queueSize(): number {
  return read().length;
}

export function enqueue(item: QueuedItem) {
  write([...read(), item]);
}

/** True when an Axios error is a connectivity failure (no response at all). */
export function isNetworkError(err: unknown): boolean {
  return (
    typeof err === 'object' &&
    err !== null &&
    'response' in err &&
    (err as { response?: unknown }).response === undefined
  );
}

async function replay(item: QueuedItem): Promise<boolean> {
  // Returns true when the item was consumed (succeeded or permanently
  // redundant — e.g. 404/409 on replay). Returns false to retry next flush.
  try {
    if (item.kind === 'game-action') {
      await api.post(`/games/sessions/${item.sessionId}/actions`, item.body);
    } else if (item.kind === 'game-complete') {
      await api.post(`/games/sessions/${item.sessionId}/complete`);
    } else {
      await api.post(`/reminders/events/${item.eventId}/acknowledge`, item.body);
    }
    return true;
  } catch (err) {
    if (isNetworkError(err)) return false;
    const status = (err as { response?: { status?: number } }).response?.status;
    // 401 lets the refresh interceptor handle it; everything else (403/404/409)
    // means the server already has or rejects this item — drop it.
    return status !== 401;
  }
}

/** Drain the queue; keeps entries that still fail on the network. */
export async function flush(): Promise<void> {
  const items = read();
  if (items.length === 0) return;

  const remaining: QueuedItem[] = [];
  for (const item of items) {
    // Sequential: order matters (actions before complete).
    if (!(await replay(item))) remaining.push(item);
  }
  write(remaining);
}
