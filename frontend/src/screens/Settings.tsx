import { useState } from 'react';
import { FeatureCard, PillButton } from '../components';
import { useAuth } from '../lib/AuthContext';

const LANGS = ['assamese', 'bengali', 'hindi', 'english'] as const;

export default function Settings() {
  const { logout, user } = useAuth();
  const [lang, setLang] = useState(user?.preferred_language || 'english');
  const [notifications, setNotifications] = useState(true);

  return (
    <div>
      <h1 className="font-heading text-heading tracking-heading leading-heading text-off-black mb-16">Settings</h1>
      <div className="flex flex-col gap-10 max-w-md">
        <FeatureCard title="Language">
          <div className="flex flex-wrap gap-3 mt-4">
            {LANGS.map((l) => (
              <button
                key={l}
                type="button"
                onClick={() => setLang(l)}
                className={`rounded-tags border bg-parchment px-5 py-3 font-mono text-body-sm uppercase tracking-body-sm cursor-pointer transition-colors ${
                  lang === l ? 'border-lake-blue text-off-black' : 'border-ash text-smoke'
                }`}
              >
                {l}
              </button>
            ))}
          </div>
        </FeatureCard>

        <FeatureCard title="Notifications">
          <div className="mt-4 flex items-center justify-between gap-4">
            <p className="font-mono text-body text-graphite">
              Reminder alerts on this device
            </p>
            {/* Toggle — pill-shaped, 56px tap target, mono label */}
            <button
              type="button"
              role="switch"
              aria-checked={notifications}
              aria-label="Notifications"
              onClick={() => setNotifications(!notifications)}
              className={`relative h-14 w-24 rounded-pills border cursor-pointer transition-colors ${
                notifications ? 'border-mint bg-mint/25' : 'border-ash bg-parchment'
              }`}
            >
              <span
                className={`absolute top-1/2 h-10 w-10 -translate-y-1/2 rounded-pills bg-parchment border border-ash transition-all ${
                  notifications ? 'left-[calc(100%-44px)]' : 'left-1'
                }`}
              />
            </button>
          </div>
        </FeatureCard>

        <PillButton variant="ghost" onClick={logout} className="self-start">LOGOUT</PillButton>
      </div>
    </div>
  );
}
