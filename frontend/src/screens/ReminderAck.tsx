import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PillButton } from '../components';
import { api } from '../lib/api';
import { enqueue, isNetworkError } from '../lib/offlineQueue';

const TYPE_HEADINGS: Record<string, string> = {
  medicine: 'Time for your medicine',
  water: 'Time for a glass of water',
  food: 'Time to eat',
  exercise: 'Time for some exercise',
};

const TYPE_ICONS: Record<string, string> = {
  medicine: '💊',
  water: '💧',
  food: '🍚',
  exercise: '🏃',
};

/** Resolve the reminder type for an event (events carry schedule_id only). */
async function loadType(eventId: string): Promise<string> {
  try {
    const { data: profile } = await api.get('/patients/me');
    const { data: events } = await api.get(`/reminders/patients/${profile.id}/events`, { params: { limit: 100 } });
    const match = (events as { id: string; schedule_id: string }[]).find((e) => e.id === eventId);
    if (!match) return 'medicine';
    const { data: schedules } = await api.get(`/reminders/schedules/${profile.id}`);
    const sched = (schedules as { id: string; reminder_type: string }[]).find((s) => s.id === match.schedule_id);
    return sched?.reminder_type ?? 'medicine';
  } catch {
    return 'medicine';
  }
}

export default function ReminderAck() {
  const { eventId } = useParams<{ eventId: string }>();
  const navigate = useNavigate();
  const [type, setType] = useState('medicine');

  useEffect(() => {
    if (eventId) void loadType(eventId).then(setType);
  }, [eventId]);

  const acknowledge = async () => {
    const body = { method: 'button' };
    try {
      await api.post(`/reminders/events/${eventId}/acknowledge`, body);
    } catch (err) {
      if (isNetworkError(err)) enqueue({ kind: 'reminder-ack', eventId: eventId!, body });
    }
    navigate('/patient');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-parchment safe-top">
      {/* Blurred gradient wash — coral to sky-blue, 60-75px blur */}
      <div
        className="absolute inset-0 -z-10"
        style={{
          background: 'linear-gradient(135deg, rgba(255,148,115,0.4) 0%, rgba(160,181,235,0.4) 100%)',
          filter: 'blur(70px)',
        }}
      />

      <div className="flex flex-col items-center gap-10 px-6 text-center max-w-md">
        {/* Lake blue icon — the single lake-blue element on this screen */}
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-lake-blue text-[40px]">
          {TYPE_ICONS[type]}
        </div>

        <h1 className="font-heading text-heading-lg tracking-heading-lg leading-heading-lg text-off-black">
          {TYPE_HEADINGS[type] ?? 'Time for your medicine'}
        </h1>

        <PillButton
          variant="primary"
          arrow
          onClick={acknowledge}
          className="w-full justify-center min-h-16 text-body-lg py-5"
        >
          DONE
        </PillButton>

        <PillButton variant="ghost" onClick={() => navigate('/patient')} className="w-full justify-center">
          REMIND ME IN 10 MIN
        </PillButton>

        <p className="font-mono text-caption uppercase tracking-caption text-smoke mt-4">
          Or say "done" to your voice companion
        </p>
      </div>
    </div>
  );
}
