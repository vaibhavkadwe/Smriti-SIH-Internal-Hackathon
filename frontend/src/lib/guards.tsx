import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

/** Redirect to /login if not authenticated. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { accessToken } = useAuth();
  if (!accessToken) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

/** Only caregiver/staff roles may pass. */
export function RequireCaregiver({ children }: { children: ReactNode }) {
  const { accessToken, isCaregiver } = useAuth();
  if (!accessToken) return <Navigate to="/login" replace />;
  if (!isCaregiver) return <Navigate to="/patient" replace />;
  return <>{children}</>;
}

/** Only patient role may pass. */
export function RequirePatient({ children }: { children: ReactNode }) {
  const { accessToken, isPatient } = useAuth();
  if (!accessToken) return <Navigate to="/login" replace />;
  if (!isPatient) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

/** Caregiver consent gate — must accept before seeing patient data. */
export function RequireConsent({ children }: { children: ReactNode }) {
  const { consentGiven } = useAuth();
  if (!consentGiven) return <Navigate to="/consent" replace />;
  return <>{children}</>;
}

