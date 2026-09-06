/// Native caregiver dashboard — family, ASHA worker, clinician.
///
/// Every view reads/writes the exact endpoints the web dashboard uses;
/// the server enforces roles and permission tiers — this screen only
/// reflects them (e.g. hides clinical charts when the summary says
/// view=basic, shows the audit panel only if the server allows it).
/// Dashboard views require a live connection; only reminder
/// acknowledgment is queued offline (by the existing patient app path).
library;

import 'package:flutter/material.dart';

import '../models/shared_models.dart';
import '../services/api_service.dart';
import '../services/auth_session.dart';
import '../theme/monad_theme.dart';
import '../widgets/trend_chart.dart';

class CaregiverDashboardScreen extends StatefulWidget {
  final String caregiverId;

  const CaregiverDashboardScreen({super.key, required this.caregiverId});

  @override
  State<CaregiverDashboardScreen> createState() =>
      _CaregiverDashboardScreenState();
}

class _CaregiverDashboardScreenState extends State<CaregiverDashboardScreen> {
  final ApiService _api = ApiService.instance;

  List<Map<String, dynamic>>? _patients;
  String? _selectedPatientId;
  Map<String, dynamic>? _summary;
  List<ReminderEventModel>? _events;
  List<ReminderScheduleModel>? _schedules;
  bool _loading = true;
  String? _error;

  /// Rate-limit / tier notice banner text (429 body or clinical-tier gate).
  String? _notice;

  @override
  void initState() {
    super.initState();
    _fetchPatients();
  }

  Future<void> _fetchPatients() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final patients = await _api.caregiverPatients(widget.caregiverId);
      if (!mounted) return;
      setState(() {
        _patients = patients;
        _loading = false;
      });
      if (patients.isNotEmpty) {
        await _select(patients.first['patient_id'] as String);
      }
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = e.statusCode == 429
            ? 'Too many requests — please wait a moment and retry.'
            : 'Could not load your patient list. ${e.message}';
        if (e.statusCode == 429) _notice = 'Rate limit reached (100 req/min).';
      });
    } on Exception catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Could not load your patient list. $e';
      });
    }
  }

  /// Loads everything the selected patient's views need. Live connection only.
  Future<void> _select(String patientId) async {
    setState(() => _loading = true);
    try {
      final summary = await _api.patientSummary(patientId);
      if (!mounted) return;
      setState(() {
        _selectedPatientId = patientId;
        _summary = summary;
        _loading = false;
      });
      // Secondary views degrade individually; the roster + summary stay.
      try {
        final events = await _api.reminderEvents(patientId);
        if (mounted) setState(() => _events = events);
      } on ApiException catch (e) {
        if (mounted && e.statusCode == 429) {
          setState(() => _notice = 'Rate limit reached (100 req/min).');
        }
      } on Exception {
        if (mounted) setState(() => _events = null);
      }
      try {
        final schedules = await _api.reminderSchedules(patientId);
        if (mounted) setState(() => _schedules = schedules);
      } on Exception {
        if (mounted) setState(() => _schedules = null);
      }
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = e.statusCode == 429
            ? 'Too many requests — please wait a moment and retry.'
            : 'Could not load the summary. ${e.message}';
        if (e.statusCode == 429) _notice = 'Rate limit reached (100 req/min).';
      });
    } on Exception catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Could not load the summary. $e';
      });
    }
  }

  Future<void> _acknowledge(String alertId) async {
    try {
      await _api.acknowledgeAlert(alertId);
      await _select(_selectedPatientId!);
    } on Exception catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not acknowledge: $e')),
      );
    }
  }

  Future<void> _addSchedule() async {
    const types = ['medicine', 'water', 'food', 'exercise'];
    var type = 'medicine';
    final timeCtl = TextEditingController(text: '08:00');
    final ok = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (context) => StatefulBuilder(
        builder: (context, setSheet) => Padding(
          padding: EdgeInsets.only(
            left: 24, right: 24, top: 24,
            bottom: MediaQuery.of(context).viewInsets.bottom + 24,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Add reminder schedule', style: Monad.subheading),
              const SizedBox(height: 16),
              DropdownButton<String>(
                value: type,
                isExpanded: true,
                items: [
                  for (final t in types)
                    DropdownMenuItem(value: t, child: Text(t.toUpperCase()))
                ],
                onChanged: (v) => setSheet(() => type = v ?? type),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: timeCtl,
                decoration: const InputDecoration(
                    labelText: 'Time (HH:MM, comma-separated)'),
              ),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Save'),
              ),
            ],
          ),
        ),
      ),
    );
    if (ok != true || !mounted) return;
    try {
      await _api.createSchedule(
        patientId: _selectedPatientId!,
        reminderType: type,
        cadence: 'daily@${timeCtl.text.trim()}',
      );
      await _select(_selectedPatientId!);
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(e.statusCode == 429
              ? 'Rate limit reached — try again shortly.'
              : 'Could not add schedule: ${e.message}')));
    } on Exception catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Could not add schedule: $e')));
    }
  }

  Future<void> _removeSchedule(String scheduleId) async {
    try {
      await _api.deleteSchedule(scheduleId);
      await _select(_selectedPatientId!);
    } on Exception catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Could not remove: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Caregiver Dashboard / তত্ত্বাৱধায়ক'),
        centerTitle: false,
        actions: [
          IconButton(
            tooltip: 'Sign out',
            icon: const Icon(Icons.logout),
            onPressed: () => AuthSession.instance.logout(),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _selectedPatientId != null
                ? () => _select(_selectedPatientId!)
                : _fetchPatients,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    final notice = _notice;
    return Column(
      children: [
        if (notice != null)
          Container(
            width: double.infinity,
            color: Monad.gold,
            padding: const EdgeInsets.all(12),
            child: Text(notice, style: Monad.monoBodySm.copyWith(color: Monad.offBlack)),
          ),
        Expanded(child: _buildMain()),
      ],
    );
  }

  Widget _buildMain() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off, size: 64, color: Monad.smoke),
              const SizedBox(height: 12),
              Text(_error!, textAlign: TextAlign.center, style: Monad.monoBodyLg),
              const SizedBox(height: 16),
              ElevatedButton(onPressed: _fetchPatients, child: const Text('Retry')),
            ],
          ),
        ),
      );
    }
    final patients = _patients ?? const [];
    if (patients.isEmpty) {
      return Center(
        child: Text('No patients assigned to this caregiver account yet.',
            style: Monad.monoBodyLg.copyWith(color: Monad.smoke)),
      );
    }
    final summary = _summary;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (_showPatientSwitcher) ...[
          _patientSelector(patients),
          const SizedBox(height: 16),
        ],
        if (summary != null) ...[
          _alerts(summary),
          if ((summary['active_alerts'] as List? ?? []).isNotEmpty)
            const SizedBox(height: 16),
          _metrics(summary),
          const SizedBox(height: 16),
          _trends(summary), // hidden server-side for view=basic
          const SizedBox(height: 16),
          _complianceLog(),
          const SizedBox(height: 16),
          _schedulesCard(),
          const SizedBox(height: 16),
          _auditCard(),
        ],
      ],
    );
  }

  /// Patient switcher — ASHA-worker tier only. Family accounts never see it
  /// (the server returns exactly their one linked patient anyway).
  bool get _showPatientSwitcher =>
      AuthSession.instance.user?.role == Role.ashaWorker;
  Widget _patientSelector(List<Map<String, dynamic>> patients) {
    return Card(
      elevation: 0,
      shape: Monad.softShape,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: DropdownButtonHideUnderline(
          child: DropdownButton<String>(
            value: _selectedPatientId,
            isExpanded: true,
            hint: Text('Select patient', style: Monad.monoBody),
            items: patients.map((p) {
              return DropdownMenuItem<String>(
                value: p['patient_id'] as String,
                child: Text(
                  '${p['name']} (${p['district'] ?? 'NER'}) — ${(p['relationship_type'] ?? '').toString().toUpperCase()}',
                  style: Monad.monoBody.copyWith(color: Monad.offBlack),
                ),
              );
            }).toList(),
            onChanged: (v) {
              if (v != null) _select(v);
            },
          ),
        ),
      ),
    );
  }

  /// Risk flags + active alerts, acknowledged via the same endpoint as web.
  Widget _alerts(Map<String, dynamic> summary) {
    final alerts = summary['active_alerts'] as List? ?? const [];
    final flags = summary['clinical_flags'] as Map<String, dynamic>? ?? const {};
    final drop = flags['cognitive_drop_detected'] == true;
    final missed = flags['high_missed_reminders'] == true;
    if (alerts.isEmpty && flags.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (alerts.isNotEmpty) ...[
          Text('ACTIVE RISK ALERTS', style: Monad.monoLabel.copyWith(color: Monad.crimson)),
          const SizedBox(height: 8),
          ...alerts.map((a) {
            final map = a as Map<String, dynamic>;
            final critical =
                map['severity'] == 'critical' || map['severity'] == 'warning';
            return Card(
              elevation: 0,
              color: critical
                  ? Monad.coral.withValues(alpha: 0.18)
                  : Monad.gold.withValues(alpha: 0.35),
              shape: Monad.softShape,
              child: ListTile(
                leading: Icon(
                  critical ? Icons.warning_amber_rounded : Icons.info_outline,
                  color: critical ? Monad.crimson : Monad.graphite,
                  size: 32,
                ),
                title: Text(map['summary'] as String? ?? 'Risk alert',
                    style: Monad.monoBody.copyWith(color: Monad.offBlack)),
                subtitle: Text('Type: ${map['trigger_type']}',
                    style: Monad.monoBodySm),
                trailing: ElevatedButton(
                  onPressed: () => _acknowledge(map['id'] as String),
                  child: const Text('Resolve'),
                ),
              ),
            );
          }),
          const SizedBox(height: 16),
        ],
        // Threshold flags — exactly as the backend computes them.
        if (drop || missed)
          Card(
            elevation: 0,
            shape: Monad.softShape,
            child: Column(
              children: [
                if (drop)
                  ListTile(
                    leading: const Icon(Icons.trending_down,
                        color: Monad.crimson, size: 32),
                    title: Text('Cognitive drop detected (<60% accuracy)',
                        style: Monad.monoBody.copyWith(color: Monad.offBlack)),
                  ),
                if (missed)
                  ListTile(
                    leading: const Icon(Icons.notifications_off,
                        color: Monad.crimson, size: 32),
                    title: Text('3+ missed reminders in 7 days',
                        style: Monad.monoBody.copyWith(color: Monad.offBlack)),
                  ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _metrics(Map<String, dynamic> summary) {
    final isClinical = summary['view'] == 'clinical';
    final compliance = (summary['compliance_pct'] as num? ?? 0).toDouble();
    final games = summary['games_played'] as int? ?? 0;
    final ack = summary['reminders_acknowledged'] as int? ?? 0;
    final total = summary['reminders_total'] as int? ?? 0;
    final missed = summary['reminders_missed'] as int? ?? 0;
    return Row(
      children: [
        if (isClinical)
          Expanded(
            child: _tile(
              'Cognitive accuracy',
              '${((summary['accuracy_pct'] as num? ?? 0) as double).toStringAsFixed(0)}%',
              '$games games (7d)',
              Icons.psychology,
            ),
          ),
        if (isClinical) const SizedBox(width: 12),
        Expanded(
          child: _tile('Compliance',
              '${compliance.toStringAsFixed(0)}%', '$ack/$total acknowledged',
              Icons.alarm_on),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _tile('Missed', '$missed', 'last 7 days', Icons.event_busy),
        ),
      ],
    );
  }

  /// 14-day sparklines — same daily_trends array the web charts render.
  /// Server strips it for basic tier, so basic caregivers see the note.
  Widget _trends(Map<String, dynamic> summary) {
    final trends = (summary['daily_trends'] as List? ?? const [])
        .cast<Map<String, dynamic>>();
    if (trends.isEmpty) {
      return Card(
        elevation: 0,
        color: Monad.gold.withValues(alpha: 0.35),
        shape: Monad.softShape,
        child: const Padding(
          padding: EdgeInsets.all(14),
          child: Row(children: [
            Icon(Icons.lock_outline, size: 22, color: Monad.graphite),
            SizedBox(width: 10),
            Expanded(
              child: Text(
                'Basic view — accuracy and response-time trends are visible '
                'to linked clinical staff only.',
                style: Monad.monoBodySm,
              ),
            ),
          ]),
        ),
      );
    }
    final acc = trends
        .map((t) => (t['accuracy_pct'] as num?)?.toDouble())
        .toList();
    final rt = trends
        .map((t) => (t['avg_response_time_ms'] as num?)?.toDouble())
        .toList();
    return Column(
      children: [
        TrendChart(
            values: acc,
            title: 'Accuracy trend (14d)',
            subtitle: '% per active day'),
        const SizedBox(height: 12),
        TrendChart(
            values: rt,
            title: 'Response time trend (14d)',
            subtitle: 'ms per active day'),
      ],
    );
  }

  /// Reminder compliance log — today's events with escalation status.
  Widget _complianceLog() {
    final events = _events;
    return Card(
      elevation: 0,
      shape: Monad.cardShape,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Today\'s reminders', style: Monad.subheading),
            const SizedBox(height: 12),
            if (events == null)
              Text('Reminder log unavailable right now.',
                  style: Monad.monoBodySm)
            else if (events.isEmpty)
              Text('No reminders scheduled for today.',
                  style: Monad.monoBodySm)
            else
              ...events.map((e) {
                final escalated = e.status == ReminderStatus.escalated;
                final missed = e.status == ReminderStatus.missed;
                final color = escalated || missed ? Monad.crimson : Monad.offBlack;
                return ListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(
                    escalated
                        ? Icons.notification_important
                        : missed
                            ? Icons.event_busy
                            : Icons.check_circle,
                    color: color,
                    size: 24,
                  ),
                  title: Text(
                    e.status.name.toUpperCase(),
                    style: Monad.monoBodySm.copyWith(color: color),
                  ),
                  subtitle: Text(
                    '${e.scheduledAt.toLocal()}'.substring(0, 16),
                    style: Monad.monoCaption,
                  ),
                );
              }),
          ],
        ),
      ),
    );
  }

  /// Schedule editing — same create/delete endpoints as the web dashboard.
  Widget _schedulesCard() {
    final schedules = _schedules;
    return Card(
      elevation: 0,
      shape: Monad.cardShape,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Schedules', style: Monad.subheading),
                TextButton.icon(
                  onPressed: _addSchedule,
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('ADD'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (schedules == null)
              Text('Schedules unavailable right now.', style: Monad.monoBodySm)
            else if (schedules.isEmpty)
              Text('No schedules yet.', style: Monad.monoBodySm)
            else
              ...schedules.map((s) => ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    leading: Icon(
                      s.reminderType == ReminderType.medicine
                          ? Icons.medication
                          : s.reminderType == ReminderType.water
                              ? Icons.water_drop
                              : s.reminderType == ReminderType.food
                                  ? Icons.restaurant
                                  : Icons.directions_walk,
                      color: Monad.offBlack,
                      size: 24,
                    ),
                    title: Text(s.reminderType.name.toUpperCase(),
                        style: Monad.monoLabel),
                    subtitle: Text('${s.cadence} · ${s.isActive ? 'active' : 'paused'}',
                        style: Monad.monoBodySm),
                    trailing: IconButton(
                      tooltip: 'Remove',
                      icon: const Icon(Icons.delete_outline, size: 20),
                      color: Monad.graphite,
                      onPressed: () => _removeSchedule(s.id),
                    ),
                  )),
          ],
        ),
      ),
    );
  }

  /// DPDP audit view — read-only; admin-only on the server. Other roles
  /// see the honest "admin-only" state rather than an error.
  Widget _auditCard() {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _api.auditLogs(limit: 50),
      builder: (context, snap) {
        Widget body;
        if (snap.hasError) {
          final e = snap.error;
          body = Text(
            e is ApiException && e.statusCode == 403
                ? 'Audit trail is admin-only — your role cannot view it.'
                : 'Could not load the audit trail right now.',
            style: Monad.monoBodySm,
          );
        } else if (!snap.hasData) {
          body = const SizedBox(
              height: 24,
              width: 24,
              child: CircularProgressIndicator(strokeWidth: 2));
        } else if (snap.data!.isEmpty) {
          body = Text('No audit entries yet.', style: Monad.monoBodySm);
        } else {
          body = Column(
            children: [
              for (final l in snap.data!.take(20))
                ListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  title: Text('${l['action']} · ${l['resource_type']}',
                      style: Monad.monoBodySm.copyWith(color: Monad.offBlack)),
                  subtitle: Text(
                      'by ${l['actor_id'] ?? 'system'} · ${(l['created_at'] ?? '')}'.substring(0, 60),
                      style: Monad.monoCaption),
                ),
            ],
          );
        }
        return Card(
          elevation: 0,
          color: Monad.periwinkleMist,
          shape: Monad.softShape,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('DPDP audit trail', style: Monad.subheading),
                const SizedBox(height: 12),
                body,
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _tile(String title, String value, String subtitle, IconData icon) {
    return Card(
      elevation: 0,
      shape: Monad.cardShape,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                    child: Text(title.toUpperCase(),
                        style: Monad.monoCaption,
                        overflow: TextOverflow.ellipsis)),
                Icon(icon, color: Monad.offBlack, size: 24),
              ],
            ),
            const SizedBox(height: 12),
            Text(value, style: Monad.headingSm.copyWith(fontSize: 32)),
            const SizedBox(height: 8),
            Text(subtitle, style: Monad.monoBodySm),
          ],
        ),
      ),
    );
  }
}
