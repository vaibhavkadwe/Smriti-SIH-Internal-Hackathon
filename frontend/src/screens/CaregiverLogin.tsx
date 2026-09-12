import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { FeatureCard, PillButton } from '../components';
import { useAuth } from '../lib/AuthContext';

/** Caregiver login — phone + password inside a FeatureCard. */
export default function CaregiverLogin() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(phone, password);
      navigate('/consent');
    } catch {
      setError('Invalid credentials. Check your phone number and password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-parchment px-6">
      <FeatureCard className="w-full max-w-md">
        <h1 className="font-heading text-heading-sm tracking-heading-sm leading-heading-sm text-off-black mb-8">
          Sign in
        </h1>
        {error && (
          <p className="mb-4 font-mono text-body-sm text-crimson">{error}</p>
        )}
        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <div>
            <label className="mb-2 block font-mono text-body-sm uppercase tracking-body-sm text-graphite">
              Phone
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
              className="w-full rounded-cards border border-ash bg-parchment px-6 py-4 font-mono text-body text-off-black outline-none focus:border-lake-blue"
              placeholder="+91 98765 43210"
            />
          </div>
          <div>
            <label className="mb-2 block font-mono text-body-sm uppercase tracking-body-sm text-graphite">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-cards border border-ash bg-parchment px-6 py-4 font-mono text-body text-off-black outline-none focus:border-lake-blue"
            />
          </div>
          <PillButton variant="primary" arrow type="submit" disabled={loading} className="w-full justify-center mt-4">
            {loading ? 'SIGNING IN' : 'LOGIN'}
          </PillButton>
        </form>
        <p className="mt-6 text-center font-mono text-caption uppercase tracking-caption text-smoke">
          Caregiver or clinician access only
        </p>
      </FeatureCard>
    </main>
  );
}

