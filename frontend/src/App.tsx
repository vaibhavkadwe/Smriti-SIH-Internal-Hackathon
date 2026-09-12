import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './lib/AuthContext';
import { RequireAuth, RequireCaregiver, RequirePatient, RequireConsent } from './lib/guards';
import CaregiverLogin from './screens/CaregiverLogin';
import PatientLogin from './screens/PatientLogin';
import ConsentGate from './screens/ConsentGate';
import DashboardLayout from './screens/DashboardLayout';
import PatientList from './screens/PatientList';
import PatientDetail from './screens/PatientDetail';
import Settings from './screens/Settings';
import AuditLog from './screens/AuditLog';
import PatientAppLayout from './screens/PatientAppLayout';
import PatientHome from './screens/PatientHome';
import MatchItGame from './screens/MatchItGame';
import RoutineGame from './screens/RoutineGame';
import VoiceCompanion from './screens/VoiceCompanion';
import ReminderAck from './screens/ReminderAck';
import PatientProfile from './screens/PatientProfile';
import OfflineBanner from './components/OfflineBanner';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <OfflineBanner />
          <Routes>
            {/* Public */}
            <Route path="/login" element={<CaregiverLogin />} />
            <Route path="/patient/login" element={<PatientLogin />} />

            {/* Consent gate */}
            <Route
              path="/consent"
              element={
                <RequireAuth>
                  <RequireCaregiver>
                    <ConsentGate />
                  </RequireCaregiver>
                </RequireAuth>
              }
            />

            {/* Caregiver dashboard */}
            <Route
              path="/dashboard"
              element={
                <RequireAuth>
                  <RequireCaregiver>
                    <RequireConsent>
                      <DashboardLayout />
                    </RequireConsent>
                  </RequireCaregiver>
                </RequireAuth>
              }
            >
              <Route index element={<PatientList />} />
              <Route path="patients/:patientId" element={<PatientDetail />} />
              <Route path="settings" element={<Settings />} />
              <Route path="audit" element={<AuditLog />} />
            </Route>

            {/* Patient app */}
            <Route
              path="/patient"
              element={
                <RequireAuth>
                  <RequirePatient>
                    <PatientAppLayout />
                  </RequirePatient>
                </RequireAuth>
              }
            >
              <Route index element={<PatientHome />} />
              <Route path="match-it" element={<MatchItGame />} />
              <Route path="routine" element={<RoutineGame />} />
              <Route path="voice" element={<VoiceCompanion />} />
              <Route path="profile" element={<PatientProfile />} />
              <Route path="reminder/:eventId" element={<ReminderAck />} />
            </Route>

            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

