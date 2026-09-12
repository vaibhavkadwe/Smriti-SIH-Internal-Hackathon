import { useQuery } from '@tanstack/react-query';
import { FeatureCard, PillButton, PillTag } from '../components';
import { api } from '../lib/api';
import { useAuth } from '../lib/AuthContext';
import { queueSize } from '../lib/offlineQueue';

const LANGS = ['assamese', 'bengali', 'hindi', 'english'] as const;

export default function PatientProfile() {
  const { user, logout } = useAuth();
  const { data: profile } = useQuery({
    queryKey: ['my-profile'],
    queryFn: async () => (await api.get('/patients/me')).data as {
      id: string; name: string; region?: string | null; district?: string | null;
    },
  });

  const pending = queueSize();

  return (
    <div className="flex flex-col gap-10 max-w-lg mx-auto">
      <h1 className="font-heading text-heading tracking-heading leading-heading text-off-black">
        {profile?.name || 'My profile'}
      </h1>

      <FeatureCard title="Account" body={
        <span className="flex flex-col gap-2">
          <span>Phone: {user?.phone}</span>
          {profile?.region && <span>Region: {profile.region}{profile.district ? `, ${profile.district}` : ''}</span>}
        </span>
      } />

      <FeatureCard title="Language" body={
        <span className="flex flex-wrap gap-3 mt-2">
          {LANGS.map((l) => (
            <PillTag key={l}>{l}</PillTag>
          ))}
        </span>
      } />

      {pending > 0 && (
        <FeatureCard title="Pending sync" body={`${pending} change${pending === 1 ? '' : 's'} will upload when you're back online.`} />
      )}

      <PillButton variant="ghost" onClick={logout}>LOGOUT</PillButton>
    </div>
  );
}
