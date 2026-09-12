import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { FeatureCard } from '../components';
import { api } from '../lib/api';
import { useAuth } from '../lib/AuthContext';

interface PatientRosterItem {
  patient_id: string;
  name: string;
  cognitive_baseline: string;
  region: string | null;
  district: string | null;
  relationship_type: string;
  permission_tier: string;
}

/** Card metadata: last active, today's score, missed reminders (7d). */
interface CardStats {
  last_active: string | null;
  today_score: string | null;
  missed: number | null;
}

function usePatientCardStats(patientId: string | undefined) {
  return useQuery<CardStats>({
    queryKey: ['card-stats', patientId],
    queryFn: async () => {
      const { data: s } = await api.get(`/dashboard/patients/${patientId}/summary`);
      const trends = (s.daily_trends || []) as { date: string; games: number; accuracy_pct: number | null }[];
      const lastActive = [...trends].reverse().find((d) => d.games > 0);
      return {
        last_active: lastActive?.date ?? null,
        today_score: s.accuracy_pct != null ? `${s.accuracy_pct}%` : null,
        missed: s.reminders_missed ?? null,
      };
    },
    enabled: !!patientId,
    staleTime: 60_000,
  });
}

function PatientCard({ p }: { p: PatientRosterItem }) {
  const { data: stats } = usePatientCardStats(p.patient_id);
  return (
    <Link to={`/dashboard/patients/${p.patient_id}`} className="block">
      <FeatureCard
        title={p.name}
        className="transition-colors hover:bg-[#f0edeb] cursor-pointer h-full"
      >
        <div className="mt-2 flex flex-col gap-1 font-mono text-body-sm tracking-body-sm text-graphite">
          <span>{stats?.last_active ? `Last active ${stats.last_active}` : 'No activity yet'}</span>
          <span>{stats?.today_score ? `Today's score ${stats.today_score}` : 'No score today'}</span>
          <span>{stats?.missed != null ? `${stats.missed} missed reminders (7d)` : ''}</span>
        </div>
      </FeatureCard>
    </Link>
  );
}

export default function PatientList() {
  const { user } = useAuth();

  const { data, isLoading } = useQuery({
    queryKey: ['caregiver-patients', user?.id],
    queryFn: async () => (await api.get(`/dashboard/caregivers/${user!.id}/patients`)).data as PatientRosterItem[],
    enabled: !!user?.id,
  });

  return (
    <div>
      <h1 className="font-heading text-heading tracking-heading leading-heading text-off-black mb-16">
        Patients
      </h1>

      {isLoading && <p className="font-mono text-body text-graphite">Loading roster…</p>}

      {!isLoading && (!data || data.length === 0) && (
        <FeatureCard body="No patients linked to your account yet. Ask the patient's family or your ASHA coordinator to link you." />
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {data?.map((p) => <PatientCard key={p.patient_id} p={p} />)}
      </div>
    </div>
  );
}
