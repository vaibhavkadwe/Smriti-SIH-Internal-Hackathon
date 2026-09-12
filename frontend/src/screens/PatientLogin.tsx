import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { PillButton } from '../components';
import { useAuth } from '../lib/AuthContext';

/** Patient login — phone + 4-digit PIN with large tap targets. */
export default function PatientLogin() {
  const [phone, setPhone] = useState('');
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (pin.length !== 4) { setError('Enter your 4-digit PIN'); return; }
    setError('');
    setLoading(true);
    try {
      await login(phone, pin);
      navigate('/patient');
    } catch {
      setError('Invalid phone or PIN.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-parchment px-6">
      <div className="w-full max-w-md">
        <h1 className="font-heading text-heading tracking-heading leading-heading text-off-black mb-10 text-center">
          Welcome back
        </h1>
        {error && (
          <p className="mb-4 font-mono text-body-lg text-crimson text-center">{error}</p>
        )}
        <form onSubmit={handleSubmit} className="flex flex-col gap-8">
          <div>
            <label className="mb-3 block font-mono text-body-lg uppercase tracking-body-lg text-graphite">
              Phone number
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
              className="w-full rounded-cards border border-ash bg-parchment px-6 py-5 font-mono text-subheading text-off-black outline-none focus:border-lake-blue"
              placeholder="+91 98765 43210"
            />
          </div>
          <div>
            <label className="mb-3 block font-mono text-body-lg uppercase tracking-body-lg text-graphite">
              4-digit PIN
            </label>
            <input
              type="password"
              inputMode="numeric"
              maxLength={4}
              pattern="[0-9]{4}"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
              required
              className="w-full rounded-cards border border-ash bg-parchment px-6 py-5 text-center font-mono text-subheading tracking-[1em] text-off-black outline-none focus:border-lake-blue"
            />
          </div>
          <PillButton variant="primary" arrow type="submit" disabled={loading} className="w-full justify-center mt-4 min-h-14">
            {loading ? 'SIGNING IN' : 'ENTER'}
          </PillButton>
        </form>
      </div>
    </main>
  );
}

