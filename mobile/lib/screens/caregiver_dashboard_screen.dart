/// Caregiver Dashboard (mobile/web responsive) — patient roster, 7-day
/// analytics, active risk alerts with acknowledgment, reminder adherence.
library;

import 'package:flutter/material.dart';

import '../services/api_service.dart';

class CaregiverDashboardScreen extends StatefulWidget {
  final String caregiverId;

  const CaregiverDashboardScreen({super.key, required this.caregiverId});

  @override
  State<CaregiverDashboardScreen> createState() => _CaregiverDashboardScreenState();
}

class _CaregiverDashboardScreenState extends State<CaregiverDashboardScreen> {
  final ApiService _api = ApiService.instance;

  List<Map<String, dynamic>>? _patients;
  String? _selectedPatientId;
  Map<String, dynamic>? _summary;
  bool _loading = true;
  String? _error;

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
        await _fetchSummary(patients.first['patient_id'] as String);
      }
    } on Exception catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Could not load your patient list. $e';
      });
    }
  }

  Future<void> _fetchSummary(String patientId) async {
    setState(() => _loading = true);
    try {
      final summary = await _api.patientSummary(patientId);
      if (!mounted) return;
      setState(() {
        _selectedPatientId = patientId;
        _summary = summary;
        _loading = false;
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
      if (_selectedPatientId != null) await _fetchSummary(_selectedPatientId!);
    } on Exception catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not acknowledge: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Caregiver Dashboard / তত্ত্বাৱধায়ক', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _selectedPatientId != null
                ? () => _fetchSummary(_selectedPatientId!)
                : _fetchPatients,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off, size: 64, color: Colors.grey),
              const SizedBox(height: 12),
              Text(_error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 17)),
              const SizedBox(height: 16),
              ElevatedButton(onPressed: _fetchPatients, child: const Text('Retry')),
            ],
          ),
        ),
      );
    }
    final patients = _patients ?? const [];
    if (patients.isEmpty) {
      return const Center(
        child: Text('No patients assigned to this caregiver account yet.',
            style: TextStyle(fontSize: 18, color: Colors.grey)),
      );
    }
    final summary = _summary;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _patientSelector(patients),
        const SizedBox(height: 16),
        if (summary != null) ...[
          _alerts(summary),
          if ((summary['active_alerts'] as List? ?? []).isNotEmpty)
            const SizedBox(height: 16),
          _metrics(summary),
          const SizedBox(height: 16),
          _trajectory(summary),
          const SizedBox(height: 16),
          _adherence(summary),
        ],
      ],
    );
  }

  Widget _patientSelector(List<Map<String, dynamic>> patients) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: DropdownButtonHideUnderline(
          child: DropdownButton<String>(
            value: _selectedPatientId,
            isExpanded: true,
            hint: const Text('Select patient'),
            items: patients.map((p) {
              return DropdownMenuItem<String>(
                value: p['patient_id'] as String,
                child: Text(
                  '${p['name']} (${p['district'] ?? 'NER'}) — ${(p['relationship_type'] ?? '').toString().toUpperCase()}',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              );
            }).toList(),
            onChanged: (v) {
              if (v != null) _fetchSummary(v);
            },
          ),
        ),
      ),
    );
  }

  Widget _alerts(Map<String, dynamic> summary) {
    final alerts = summary['active_alerts'] as List? ?? const [];
    if (alerts.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Active Risk Alerts', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.red)),
        const SizedBox(height: 8),
        ...alerts.map((a) {
          final map = a as Map<String, dynamic>;
          final critical = map['severity'] == 'critical' || map['severity'] == 'warning';
          return Card(
            color: critical ? Colors.red.shade50 : Colors.amber.shade50,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              leading: Icon(
                critical ? Icons.warning_amber_rounded : Icons.info_outline,
                color: critical ? Colors.red : Colors.orange,
                size: 32,
              ),
              title: Text(map['summary'] as String? ?? 'Risk alert',
                  style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('Type: ${map['trigger_type']}'),
              trailing: ElevatedButton(
                onPressed: () => _acknowledge(map['id'] as String),
                child: const Text('Resolve'),
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _metrics(Map<String, dynamic> summary) {
    final accuracy = (summary['accuracy_pct'] as num? ?? 0).toDouble();
    final compliance = (summary['compliance_pct'] as num? ?? 0).toDouble();
    final games = summary['games_played'] as int? ?? 0;
    return Row(
      children: [
        Expanded(
          child: _tile(
            'Cognitive Accuracy',
            '${accuracy.toStringAsFixed(0)}%',
            '$games games (7d)',
            Icons.psychology,
            accuracy >= 70 ? Colors.teal : Colors.orange,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _tile(
            'Reminder Compliance',
            '${compliance.toStringAsFixed(0)}%',
            '${summary['reminders_acknowledged']}/${summary['reminders_total']} acked',
            Icons.alarm_on,
            compliance >= 75 ? Colors.green : Colors.red,
          ),
        ),
      ],
    );
  }

  Widget _tile(String title, String value, String subtitle, IconData icon, Color color) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(title, style: const TextStyle(fontSize: 13, color: Colors.grey, fontWeight: FontWeight.bold)),
                Icon(icon, color: color, size: 24),
              ],
            ),
            const SizedBox(height: 8),
            Text(value, style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: color)),
            const SizedBox(height: 4),
            Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.black54)),
          ],
        ),
      ),
    );
  }

  Widget _trajectory(Map<String, dynamic> summary) {
    final flags = summary['clinical_flags'] as Map<String, dynamic>? ?? const {};
    final drop = flags['cognitive_drop_detected'] == true;
    final speed = (summary['avg_response_time_ms'] as num? ?? 0).toDouble();
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ListTile(
        leading: Icon(drop ? Icons.trending_down : Icons.trending_up,
            color: drop ? Colors.red : Colors.green, size: 36),
        title: Text(drop ? 'Cognitive drop detected (<60%)' : 'Cognitive baseline stable',
            style: TextStyle(fontWeight: FontWeight.bold, color: drop ? Colors.red : Colors.green.shade800)),
        subtitle: Text(speed > 0 ? 'Avg decision speed: ${(speed / 1000).toStringAsFixed(1)}s' : 'No game data yet'),
      ),
    );
  }

  Widget _adherence(Map<String, dynamic> summary) {
    final total = summary['reminders_total'] as int? ?? 0;
    final ack = summary['reminders_acknowledged'] as int? ?? 0;
    final missed = summary['reminders_missed'] as int? ?? 0;
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Adherence (7 days)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _count('Completed', ack, Colors.green),
                _count('Missed', missed, Colors.red),
                _count('Scheduled', total, Colors.blueGrey),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _count(String label, int value, Color color) {
    return Column(
      children: [
        Text('$value', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: color)),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(fontSize: 13, color: Colors.black87)),
      ],
    );
  }
}
