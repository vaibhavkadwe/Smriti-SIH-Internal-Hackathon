import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../lib/AuthContext';
import { PillButton } from '../components';

const navItems = [
  { to: '/dashboard', label: 'Patients', end: true },
  { to: '/dashboard/settings', label: 'Settings' },
  { to: '/dashboard/audit', label: 'Audit Log' },
] as const;

export default function DashboardLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-parchment">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r border-ash bg-parchment px-6 py-10">
        <h1 className="font-heading text-subheading tracking-subheading leading-subheading text-off-black mb-16">
          Smriti
        </h1>
        <nav className="flex flex-1 flex-col gap-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={'end' in item ? item.end : false}
              className={({ isActive }) =>
                `block font-mono text-label uppercase tracking-label leading-label transition-opacity ${
                  isActive ? 'text-off-black' : 'text-smoke hover:text-off-black'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto flex flex-col gap-4">
          <p className="font-mono text-body-sm text-graphite truncate">
            {user?.phone}
          </p>
          <PillButton variant="ghost" onClick={logout} className="w-full justify-center text-xs">
            LOGOUT
          </PillButton>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-[1432px] px-16 py-16">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

