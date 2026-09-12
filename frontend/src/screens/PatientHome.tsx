import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { PillButton, PillTag } from '../components';
import { api } from '../lib/api';

/** Fixed reminder-type mapping (DESIGN.md elder-care extension). */
const REMINDER_TINT: Record<string, string> = {
  medicine: 'bg-lake-blue/10 border-lake-blue',
  water: 'bg-sky-blue/10 border-sky-blue',
  food: 'bg-gold/10 border-gold',
  exercise: 'bg-mint/10 border-mint',
};
const REMINDER_ICON: Record<string, string> = {
  medicine: '💊',
  water: '💧',
  food: '🍚',
  exercise: '🏃',
};

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

interface Schedule {
  id: string;
  reminder_type: string;
  cadence: string;
}

interface ReminderEvent {
  id: string;
  schedule_id: string;
  scheduled_at: string;
  status: string;
}

export default function PatientHome() {
  const { data: profile } = useQuery({
    queryKey: ['my-profile'],
    queryFn: async () => (await api.get('/patients/me')).data as { id: string; name: string },
  });

  // Reminder events don't carry the type — join against schedules client-side.
  const { data: events } = useQuery({
    queryKey: ['pending-events', profile?.id],
    queryFn: async () => {
      const [ev, sch] = await Promise.all([
        api.get(`/reminders/patients/${profile!.id}/events`, { params: { status_filter: 'pending', limit: 8 } }),
        api.get(`/reminders/schedules/${profile!.id}`),
      ]);
      const byId = new Map<string, Schedule>(
        ((sch.data as Schedule[]) || []).map((s) => [s.id, s]),
      );
      return ((ev.data as ReminderEvent[]) || []).map((e) => ({
        ...e,
        reminder_type: byId.get(e.schedule_id)?.reminder_type ?? 'medicine',
      }));
    },
    enabled: !!profile?.id,
  });

  const name = profile?.name || 'friend';

  return (
    <div className="flex flex-col gap-10">
      <h1 className="font-heading text-heading tracking-heading leading-heading text-off-black">
        {greeting()}, {name.split(' ')[0]}
      </h1>

      {/* Reminder pills — always icon + label + tint, never color alone */}
      <div className="flex flex-wrap gap-3">
        {(events || []).map((ev) => {
          const tint = REMINDER_TINT[ev.reminder_type] ?? REMINDER_TINT.medicine;
          const icon = REMINDER_ICON[ev.reminder_type] ?? '💊';
          return (
            <Link key={ev.id} to={`/patient/reminder/${ev.id}`} className="min-h-14 inline-flex items-center">
              <PillTag icon={icon} className={`${tint} shadow-md`}>{ev.reminder_type}</PillTag>
            </Link>
          );
        })}
        {(!events || events.length === 0) && (
          <p className="font-mono text-body-lg text-graphite">No pending reminders right now.</p>
        )}
      </div>

      {/* One large primary CTA — the only lake-blue element on the screen */}
      <div className="flex flex-col items-center gap-6 mt-6">
        <Link to="/patient/match-it">
          <PillButton variant="primary" arrow className="text-body-lg px-12 py-5 min-h-16">
            PLAY TODAY'S GAME
          </PillButton>
        </Link>
        <Link to="/patient/routine" className="font-mono text-body-lg uppercase text-off-black underline">
          Practice daily routine →
        </Link>
      </div>
    </div>
  );
}
