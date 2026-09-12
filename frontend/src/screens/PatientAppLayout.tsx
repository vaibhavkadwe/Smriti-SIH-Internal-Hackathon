import { NavLink, Outlet } from 'react-router-dom';

const tabs = [
  { to: '/patient', label: 'Home', icon: '⌂', end: true },
  { to: '/patient/match-it', label: 'Games', icon: '◫' },
  { to: '/patient/voice', label: 'Voice', icon: '◉' },
  { to: '/patient/profile', label: 'Profile', icon: '◍' },
] as const;

export default function PatientAppLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-parchment">
      <main className="flex-1 overflow-y-auto pb-24">
        <div className="mx-auto max-w-[1432px] px-6 py-10">
          <Outlet />
        </div>
      </main>
      {/* Bottom nav — 72px tall + safe-area inset, 56px min tap targets,
          parchment background, 1px ash top border. */}
      <nav className="no-select safe-bottom fixed bottom-0 left-0 right-0 z-40 flex flex-col border-t border-ash bg-parchment">
        <div className="flex h-[72px]">
          {tabs.map((t) => (
            <NavLink
              key={t.to}
              to={t.to}
              end={'end' in t ? t.end : false}
              className={({ isActive }) =>
                `flex flex-1 flex-col items-center justify-center gap-1 font-mono text-caption uppercase tracking-caption transition-colors ${
                  isActive ? 'text-off-black' : 'text-smoke'
                }`
              }
            >
              <span className="text-body-lg">{t.icon}</span>
              {t.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
