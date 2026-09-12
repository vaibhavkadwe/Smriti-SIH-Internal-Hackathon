import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FeatureCard, ElevatedCard, PillButton, PillTag } from '../components';
import { api } from '../lib/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

type Tab = 'overview' | 'trends' | 'reminders' | 'alerts' | 'documents' | 'reports' | 'screening';
const TABS: { key: Tab; label: string }[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'trends', label: 'Trends' },
  { key: 'reminders', label: 'Reminders' },
  { key: 'alerts', label: 'Risk Flags' },
  { key: 'documents', label: 'Documents' },
  { key: 'reports', label: 'Reports' },
  { key: 'screening', label: 'Screening' },
];

interface DailyTrend { date: string; games: number; accuracy_pct: number | null; avg_response_time_ms: number | null }
interface ActiveAlert { id: string; trigger_type: string; severity: string; summary: string; created_at: string }

/** Basic tier strips clinical fields — make every clinical field optional. */
interface Summary {
  patient_id: string;
  games_played?: number;
  accuracy_pct?: number;
  avg_response_time_ms?: number;
  reminders_total: number;
  reminders_acknowledged: number;
  reminders_missed: number;
  compliance_pct: number;
  active_alerts?: ActiveAlert[];
  daily_trends?: DailyTrend[];
  accuracy_drop_pct?: number | null;
  clinical_flags?: Record<string, boolean>;
  view?: string;
}

/** Overview stat tile — big serif 48px number, mono 12px uppercase label below. */
function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <FeatureCard>
      <span className="font-heading text-heading-lg tracking-heading-lg leading-heading-lg text-off-black">{value}</span>
      <p className="mt-4 font-mono text-caption uppercase tracking-caption text-smoke">{label}</p>
    </FeatureCard>
  );
}

/** Today's games — the latest day in the 14-day trend with sessions. */
function todayGames(s: Summary): string {
  const t = s.daily_trends || [];
  const last = [...t].reverse().find((d) => d.games > 0);
  return String(last?.games ?? 0);
}

/** Consecutive days with ≥1 game, counting back from the most recent active day. */
function streakDays(s: Summary): number {
  const t = (s.daily_trends || []).filter((d) => d.games > 0);
  if (t.length === 0) return 0;
  const dates = new Set(t.map((d) => d.date));
  const last = new Date(t[t.length - 1].date);
  let streak = 0;
  for (let d = new Date(last); dates.has(d.toISOString().slice(0, 10)); d.setDate(d.getDate() - 1)) {
    streak += 1;
  }
  return streak;
}

/** Estimated engaged minutes: games × ~3.5 min average session length. */
function timeEngaged(s: Summary): string {
  const total = (s.daily_trends || []).reduce((acc, d) => acc + d.games, 0);
  return `${Math.round(total * 3.5)} min`;
}

const SEVERITY_STYLE: Record<string, string> = {
  info: 'bg-periwinkle-mist/40 border-sky-blue',
  warning: 'bg-gold/25 border-gold',
  critical: 'bg-coral/25 border-coral',
};

export default function PatientDetail() {
  const { patientId } = useParams<{ patientId: string }>();
  const [tab, setTab] = useState<Tab>('overview');
  const qc = useQueryClient();

  const { data: summary } = useQuery<Summary>({
    queryKey: ['patient-summary', patientId],
    queryFn: async () => (await api.get(`/dashboard/patients/${patientId}/summary`)).data,
    enabled: !!patientId,
  });

  const acknowledgeAlert = useMutation({
    mutationFn: (alertId: string) => api.post(`/dashboard/alerts/${alertId}/acknowledge`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['patient-summary', patientId] }),
  });

  const isClinical = summary?.view === 'clinical';

  return (
    <div>
      {/* Tabs — PillTag row: active = lake-blue border, inactive = ash */}
      <div className="flex flex-wrap gap-3 mb-16">
        {TABS.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={`rounded-tags border bg-parchment px-5 py-3 font-mono text-body-sm uppercase tracking-body-sm cursor-pointer transition-colors ${
              tab === t.key ? 'border-lake-blue text-off-black' : 'border-ash text-smoke'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && summary && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <StatTile label="Games Today" value={todayGames(summary)} />
          <StatTile label="Streak" value={`${streakDays(summary)} days`} />
          <StatTile label="Time Engaged" value={timeEngaged(summary)} />
        </div>
      )}

      {tab === 'trends' && (
        isClinical ? (
          <div className="flex flex-col gap-8">
            <FeatureCard title="Accuracy (14 days)">
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={summary?.daily_trends || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#cecac8" />
                    <XAxis dataKey="date" tick={{ fontSize: 12, fontFamily: 'JetBrains Mono', fill: '#797776' }} />
                    <YAxis tick={{ fontSize: 12, fontFamily: 'JetBrains Mono', fill: '#797776' }} domain={[0, 100]} />
                    <Tooltip contentStyle={{ background: '#f6f3f1', border: '1px solid #cecac8', borderRadius: 8, fontFamily: 'JetBrains Mono', fontSize: 12 }} />
                    <Line type="monotone" dataKey="accuracy_pct" stroke="#2b59d1" strokeWidth={2} dot={false} connectNulls />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </FeatureCard>
            <FeatureCard title="Response Time (14 days)">
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={summary?.daily_trends || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#cecac8" />
                    <XAxis dataKey="date" tick={{ fontSize: 12, fontFamily: 'JetBrains Mono', fill: '#797776' }} />
                    <YAxis tick={{ fontSize: 12, fontFamily: 'JetBrains Mono', fill: '#797776' }} />
                    <Tooltip contentStyle={{ background: '#f6f3f1', border: '1px solid #cecac8', borderRadius: 8, fontFamily: 'JetBrains Mono', fontSize: 12 }} />
                    <Line type="monotone" dataKey="avg_response_time_ms" stroke="#2b59d1" strokeWidth={2} dot={false} connectNulls />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </FeatureCard>
          </div>
        ) : (
          <FeatureCard title="Trends" body="Detailed accuracy and response-time trends are available to clinical staff (ASHA, clinician, admin) only." />
        )
      )}

      {tab === 'reminders' && <RemindersTab patientId={patientId!} />}

      {tab === 'alerts' && (
        <div className="flex flex-col gap-4">
          {(summary?.active_alerts || []).length === 0 && <FeatureCard body="No active alerts." />}
          {(summary?.active_alerts || []).map((a) => (
            <ElevatedCard key={a.id} title={a.trigger_type.replace(/_/g, ' ')} body={a.summary}>
              <div className="mt-4 flex items-center gap-4">
                <PillTag className={SEVERITY_STYLE[a.severity] || SEVERITY_STYLE.info}>{a.severity}</PillTag>
                <PillButton variant="ghost" onClick={() => acknowledgeAlert.mutate(a.id)}>ACKNOWLEDGE</PillButton>
              </div>
            </ElevatedCard>
          ))}
        </div>
      )}

      {tab === 'documents' && <DocumentsTab patientId={patientId!} />}

      {tab === 'reports' && <ReportsTab patientId={patientId!} />}

      {tab === 'screening' && <ScreeningTab patientId={patientId!} />}
    </div>
  );
}

/* ============ Reminders tab ============ */

function RemindersTab({ patientId }: { patientId: string }) {
  const qc = useQueryClient();
  const [editing, setEditing] = useState<string | null>(null);

  const { data: schedules } = useQuery({
    queryKey: ['schedules', patientId],
    queryFn: async () => (await api.get(`/reminders/schedules/${patientId}`)).data as Schedule[],
  });

  // Compliance pills come from the 7-day summary (ack = mint, missed = coral).
  const { data: summary } = useQuery<Summary>({
    queryKey: ['patient-summary', patientId],
    queryFn: async () => (await api.get(`/dashboard/patients/${patientId}/summary`)).data,
    enabled: !!patientId,
  });

  const del = useMutation({
    mutationFn: (id: string) => api.delete(`/reminders/schedules/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['schedules', patientId] }),
  });

  const add = useMutation({
    mutationFn: (body: { reminder_type: string; cadence: string }) =>
      api.post('/reminders/schedules', { patient_id: patientId, ...body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['schedules', patientId] }),
  });

  const saveEdit = useMutation({
    mutationFn: (s: Schedule) => api.post('/reminders/schedules', { patient_id: patientId, reminder_type: s.reminder_type, cadence: s.cadence }),
    onSuccess: () => { setEditing(null); qc.invalidateQueries({ queryKey: ['schedules', patientId] }); },
  });

  return (
    <div className="flex flex-col gap-6">
      <AddScheduleForm onAdd={(body) => add.mutate(body)} />

      {/* Compliance pills (7-day window from the summary) */}
      {summary && (
        <div className="flex flex-wrap gap-3">
          <PillTag className="bg-mint/25 border-mint">ACKNOWLEDGED {summary.reminders_acknowledged}</PillTag>
          <PillTag className="bg-coral/25 border-coral">MISSED {summary.reminders_missed}</PillTag>
          <PillTag>COMPLIANCE {summary.compliance_pct}%</PillTag>
        </div>
      )}

      {schedules?.map((s) => (
        <div key={s.id} className="border-b border-ash">
          <div className="flex flex-wrap items-center gap-4 py-10">
            <span className="font-heading text-subheading tracking-subheading leading-subheading text-off-black flex-1">
              {s.reminder_type} — {s.cadence}
            </span>
            <PillTag className={s.is_active ? 'bg-mint/25 border-mint' : ''}>{s.is_active ? 'ACTIVE' : 'INACTIVE'}</PillTag>
            <button type="button" onClick={() => setEditing(editing === s.id ? null : s.id)} className="font-mono text-body-sm uppercase text-off-black underline cursor-pointer bg-transparent border-none">EDIT</button>
            <button type="button" onClick={() => del.mutate(s.id)} className="font-mono text-body-sm uppercase text-crimson underline cursor-pointer bg-transparent border-none">DELETE</button>
          </div>
          {editing === s.id && (
            <EditScheduleForm schedule={s} onSave={(next) => saveEdit.mutate({ ...s, ...next })} onCancel={() => setEditing(null)} />
          )}
        </div>
      ))}
      {(!schedules || schedules.length === 0) && <FeatureCard body="No reminder schedules yet. Add one above." />}
    </div>
  );
}

interface Schedule { id: string; reminder_type: string; cadence: string; is_active: boolean }

function AddScheduleForm({ onAdd }: { onAdd: (b: { reminder_type: string; cadence: string }) => void }) {
  const [rType, setRType] = useState('medicine');
  const [cadence, setCadence] = useState('daily@08:00');
  return (
    <div className="flex flex-wrap gap-4 items-end">
      <select value={rType} onChange={(e) => setRType(e.target.value)} aria-label="Reminder type" className="rounded-cards border border-ash bg-parchment px-4 py-3 font-mono text-body-sm text-off-black">
        <option value="medicine">Medicine</option><option value="water">Water</option><option value="food">Food</option><option value="exercise">Exercise</option>
      </select>
      <input value={cadence} onChange={(e) => setCadence(e.target.value)} aria-label="Cadence" className="flex-1 min-w-64 rounded-cards border border-ash bg-parchment px-4 py-3 font-mono text-body-sm text-off-black" placeholder="daily@08:00,20:00" />
      <PillButton variant="secondary" onClick={() => onAdd({ reminder_type: rType, cadence })}>ADD REMINDER</PillButton>
    </div>
  );
}

function EditScheduleForm({ schedule, onSave, onCancel }: {
  schedule: Schedule;
  onSave: (next: { reminder_type: string; cadence: string }) => void;
  onCancel: () => void;
}) {
  const [rType, setRType] = useState(schedule.reminder_type);
  const [cadence, setCadence] = useState(schedule.cadence);
  return (
    <div className="flex flex-wrap gap-4 items-end pb-10">
      <select value={rType} onChange={(e) => setRType(e.target.value)} aria-label="Reminder type" className="rounded-cards border border-ash bg-parchment px-4 py-3 font-mono text-body-sm text-off-black">
        <option value="medicine">Medicine</option><option value="water">Water</option><option value="food">Food</option><option value="exercise">Exercise</option>
      </select>
      <input value={cadence} onChange={(e) => setCadence(e.target.value)} aria-label="Cadence" className="flex-1 min-w-64 rounded-cards border border-ash bg-parchment px-4 py-3 font-mono text-body-sm text-off-black" />
      <PillButton variant="secondary" onClick={() => onSave({ reminder_type: rType, cadence })}>SAVE</PillButton>
      <PillButton variant="ghost" onClick={onCancel}>CANCEL</PillButton>
    </div>
  );
}

/* ============ Documents tab ============ */

interface UploadedDoc { document_id: string; file_name?: string; chars_extracted?: number }

function DocumentsTab({ patientId }: { patientId: string }) {
  const [query, setQuery] = useState('');
  const [docs, setDocs] = useState<UploadedDoc[]>([]);
  const [answer, setAnswer] = useState<{ answer?: string; sources?: { document_id: string; chunk_text: string }[] } | null>(null);
  const ask = useMutation({
    mutationFn: () => api.post('/reports/documents/answer', { patient_id: patientId, question: query, top_k: 3 }),
    onSuccess: (d) => setAnswer(d.data),
  });
  const upload = useMutation({
    mutationFn: (file: File) => {
      const fd = new FormData();
      fd.append('file', file);
      return api.post(`/reports/documents/upload?patient_id=${patientId}&doc_type=prescription`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
    },
    onSuccess: (d) => setDocs((prev) => [...prev, d.data as UploadedDoc]),
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Drag-drop upload zone — dashed ash, 40px radius */}
      <div
        className="rounded-cards border border-dashed border-ash p-10 text-center cursor-pointer hover:bg-[#f0edeb] transition-colors"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) upload.mutate(f); }}
      >
        <p className="font-mono text-body text-graphite">Drop a medical document here, or browse to upload</p>
        <input type="file" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) upload.mutate(f); }} id="doc-upload" />
        <label htmlFor="doc-upload" className="mt-4 inline-block cursor-pointer font-mono text-body-sm uppercase text-off-black underline">BROWSE</label>
        {upload.isPending && <p className="mt-4 font-mono text-body-sm text-smoke">Extracting text…</p>}
        {upload.isError && <p className="mt-4 font-mono text-body-sm text-crimson">Upload failed. Check the file type (PDF or text).</p>}
      </div>

      {/* Uploaded docs as chips */}
      {docs.length > 0 && (
        <div className="flex flex-wrap gap-3">
          {docs.map((d) => (
            <PillTag key={d.document_id} icon="✓">{d.file_name || 'Document'}</PillTag>
          ))}
        </div>
      )}

      {/* RAG query — the single primary CTA on this tab */}
      <div className="flex gap-4">
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask about the patient's documents…" className="flex-1 rounded-cards border border-ash bg-parchment px-6 py-4 font-mono text-body text-off-black outline-none" />
        <PillButton variant="primary" arrow onClick={() => ask.mutate()} disabled={!query || ask.isPending}>{ask.isPending ? 'ASKING' : 'ASK'}</PillButton>
      </div>

      {ask.isError && <FeatureCard body="The query failed. Check you are linked to this patient with clinical access." />}

      {answer && (
        <FeatureCard title="Answer" body={answer.answer || 'No answer returned.'}>
          {answer.sources && answer.sources.length > 0 && (
            <div className="mt-6 flex flex-col gap-3">
              <p className="font-mono text-caption uppercase tracking-caption text-smoke">Sources</p>
              {answer.sources.map((s, i) => (
                <p key={i} className="font-mono text-body-sm text-graphite border-l-2 border-ash pl-4">{s.chunk_text.slice(0, 160)}…</p>
              ))}
            </div>
          )}
        </FeatureCard>
      )}
    </div>
  );
}

/* ============ Reports tab ============ */

interface WeeklyReportData {
  report_id: string;
  patient_id: string;
  week_start: string;
  generated_at: string;
  report: {
    patient_name?: string;
    cognitive_metrics?: { total_sessions: number; overall_accuracy_pct: number; trend: string };
    adherence_metrics?: { total_scheduled: number; acknowledged: number; missed_or_late: number; compliance_pct: number };
    symptom_observations?: string[];
    clinical_recommendations?: string[];
  };
}

function ReportsTab({ patientId }: { patientId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['latest-report', patientId],
    queryFn: async () => (await api.get(`/reports/patients/${patientId}/latest`)).data as WeeklyReportData,
  });

  const download = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data.report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weekly-report-${data.report_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) return <FeatureCard body="Loading latest report…" />;

  if (!data?.report) return <FeatureCard body="No reports available yet." />;

  const r = data.report;
  return (
    <FeatureCard title={`Weekly summary — week of ${new Date(data.week_start).toLocaleDateString()}`}>
      {r.patient_name && <p className="font-mono text-body text-graphite">{r.patient_name}</p>}

      {r.cognitive_metrics && (
        <div className="mt-6 flex flex-wrap gap-3">
          <PillTag>SESSIONS {r.cognitive_metrics.total_sessions}</PillTag>
          <PillTag>ACCURACY {r.cognitive_metrics.overall_accuracy_pct}%</PillTag>
          <PillTag>TREND {r.cognitive_metrics.trend}</PillTag>
        </div>
      )}

      {r.adherence_metrics && (
        <div className="mt-4 flex flex-wrap gap-3">
          <PillTag>ACKNOWLEDGED {r.adherence_metrics.acknowledged}/{r.adherence_metrics.total_scheduled}</PillTag>
          <PillTag className="bg-coral/25 border-coral">MISSED {r.adherence_metrics.missed_or_late}</PillTag>
          <PillTag>COMPLIANCE {r.adherence_metrics.compliance_pct}%</PillTag>
        </div>
      )}

      {r.symptom_observations && r.symptom_observations.length > 0 && (
        <div className="mt-6">
          <p className="font-mono text-caption uppercase tracking-caption text-smoke mb-2">Observations</p>
          {r.symptom_observations.map((o, i) => <p key={i} className="font-mono text-body text-graphite">• {o}</p>)}
        </div>
      )}

      {r.clinical_recommendations && r.clinical_recommendations.length > 0 && (
        <div className="mt-6">
          <p className="font-mono text-caption uppercase tracking-caption text-smoke mb-2">Recommendations</p>
          {r.clinical_recommendations.map((c, i) => <p key={i} className="font-mono text-body text-graphite">• {c}</p>)}
        </div>
      )}

      <div className="mt-8">
        <PillButton variant="secondary" onClick={download}>DOWNLOAD</PillButton>
      </div>
    </FeatureCard>
  );
}

/* ============ Screening tab ============ */

const SCREENING_FIELDS = ['Age','Gender','Ethnicity','EducationLevel','BMI','Smoking','AlcoholConsumption','PhysicalActivity','DietQuality','SleepQuality','FamilyHistoryAlzheimers','CardiovascularDisease','Diabetes','Depression','HeadInjury','Hypertension','SystolicBP','DiastolicBP','CholesterolTotal','CholesterolLDL','CholesterolHDL','CholesterolTriglycerides','MMSE','FunctionalAssessment','MemoryComplaints','BehavioralProblems','ADL','Confusion','Disorientation','PersonalityChanges','DifficultyCompletingTasks','Forgetfulness'];

function ScreeningTab({ patientId }: { patientId: string }) {
  const [form, setForm] = useState<Record<string, string>>({});
  const [result, setResult] = useState<{
    status: string; risk_score?: number | null; tier?: string | null; note?: string; errors?: string[];
  } | null>(null);

  const run = useMutation({
    // extra="forbid" on the backend: send only filled fields.
    mutationFn: () => {
      const body: Record<string, number> = {};
      for (const [k, v] of Object.entries(form)) if (v !== '') body[k] = Number(v);
      return api.post(`/patients/${patientId}/risk-screening`, body);
    },
    onSuccess: (d) => setResult(d.data),
    onError: (e: unknown) => {
      const detail = (e as { response?: { data?: { detail?: string[] } } })?.response?.data?.detail;
      if (detail) setResult({ status: 'validation_failed', errors: detail as unknown as string[] });
    },
  });

  const tierStyle = result?.tier === 'low_risk'
    ? 'bg-mint/25 border-mint'
    : result?.tier === 'moderate_risk'
      ? 'bg-gold/25 border-gold'
      : 'bg-coral/25 border-coral';

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {SCREENING_FIELDS.map((f) => (
          <div key={f}>
            <label htmlFor={`sf-${f}`} className="mb-1 block font-mono text-caption uppercase tracking-caption text-graphite">{f}</label>
            <input id={`sf-${f}`} value={form[f] || ''} onChange={(e) => setForm({ ...form, [f]: e.target.value })} inputMode="decimal" className="w-full rounded-cards border border-ash bg-parchment px-3 py-2 font-mono text-body-sm text-off-black outline-none" />
          </div>
        ))}
      </div>
      <PillButton variant="primary" arrow onClick={() => run.mutate()} disabled={run.isPending}>{run.isPending ? 'RUNNING' : 'RUN SCREENING'}</PillButton>

      {result && result.status === 'ok' && (
        <div className={`rounded-tags border p-6 ${tierStyle}`}>
          <p className="font-mono text-body uppercase text-off-black">
            {result.tier?.replace('_', ' ')} — Score {result.risk_score ?? 'N/A'}
          </p>
          {result.note && <p className="mt-2 font-mono text-body-sm text-graphite">{result.note}</p>}
        </div>
      )}
      {result && result.status === 'validation_failed' && (
        <div className="rounded-tags border border-coral bg-coral/25 p-6">
          <p className="font-mono text-body uppercase text-off-black">Validation failed</p>
          <ul className="mt-2 list-inside list-disc font-mono text-body-sm text-graphite">
            {(result.errors || []).map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
