import { useQuery } from '@tanstack/react-query';
import { FeatureCard, FAQRow } from '../components';
import { api } from '../lib/api';
import { useAuth } from '../lib/AuthContext';

export default function AuditLog() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const { data } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: async () => (await api.get('/compliance/audit-logs', { params: { limit: 100 } })).data,
    enabled: isAdmin,
  });

  return (
    <div>
      <h1 className="font-heading text-heading tracking-heading leading-heading text-off-black mb-16">Audit Log</h1>
      {!isAdmin ? (
        <FeatureCard body="Audit log access is restricted to administrators." />
      ) : (
        <div className="flex flex-col">
          {(data || []).map((log: any) => (
            <FAQRow
              key={log.id}
              question={
                <span className="font-mono text-body-sm uppercase tracking-body-sm text-off-black">
                  {log.timestamp ? new Date(log.timestamp).toLocaleString() : '—'} · {log.action} · {log.resource_type}
                </span>
              }
            >
              <p>User: {log.user_id}</p>
              <p>Resource: {log.resource_id}</p>
              {log.ip_address && <p>IP: {log.ip_address}</p>}
            </FAQRow>
          ))}
          {(!data || data.length === 0) && <FeatureCard body="No audit entries yet." />}
        </div>
      )}
    </div>
  );
}

