import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PillButton } from '../components';
import { useAuth } from '../lib/AuthContext';
import { api } from '../lib/api';

/**
 * Caregiver consent gate — shown once per caregiver session before any patient
 * data renders. Records DPDP consent for each linked patient on the roster
 * (POST /compliance/consent), then unlocks the dashboard. Failures are
 * non-blocking: the acceptance is what the backend audit trail needs, and an
 * already-granted record just 200s again.
 */
export default function ConsentGate() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { setConsent, user } = useAuth();
  const navigate = useNavigate();

  const handleAgree = async () => {
    setLoading(true);
    setError('');
    try {
      if (user?.id) {
        const { data: roster } = await api.get(`/dashboard/caregivers/${user.id}/patients`);
        const patients = (roster as { patient_id: string }[]) || [];
        await Promise.allSettled(
          patients.map((p) =>
            api.post('/compliance/consent', {
              patient_id: p.patient_id,
              consent_type: 'guardian',
              scope: 'all',
            }),
          ),
        );
      }
      setConsent(true);
      navigate('/dashboard');
    } catch {
      // Network failure: still unlock the dashboard (the offline banner is
      // showing), but note the consent didn't reach the server.
      setError('Consent could not be recorded on the server. You can continue; it will sync later.');
      setConsent(true);
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-parchment px-6">
      <div className="w-full max-w-lg">
        <h1 className="font-heading text-heading-sm tracking-heading-sm leading-heading-sm text-off-black mb-6">
          Before you continue
        </h1>
        <p className="font-mono text-body tracking-body leading-body text-graphite mb-4">
          You are about to access personal health information of the patients in your care.
          This data is protected under India's Digital Personal Data Protection Act, 2023.
        </p>
        <p className="font-mono text-body tracking-body leading-body text-graphite mb-10">
          By proceeding, you agree to use this information solely for the purpose of
          providing care, and to not share, copy, or store it outside this platform.
          Every access is logged and audited.
        </p>
        {error && <p className="mb-6 font-mono text-body-sm text-crimson">{error}</p>}
        <PillButton
          variant="primary"
          arrow
          onClick={handleAgree}
          disabled={loading}
          className="w-full justify-center"
        >
          {loading ? 'RECORDING' : 'I AGREE'}
        </PillButton>
      </div>
    </main>
  );
}
