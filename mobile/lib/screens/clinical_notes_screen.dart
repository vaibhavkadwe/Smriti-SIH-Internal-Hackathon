/// ASHA worker clinical notes entry — lightweight on-device form for
/// field observations during a patient visit. Notes are stored locally
/// in the offline outbox (drift) and replayed to the backend when the
/// mobile reconnects. Backend ingestion target: /api/v1/sync (offline outbox).
library;

import 'package:flutter/material.dart';
import '../models/shared_models.dart';
import '../services/api_service.dart';
import '../theme/monad_theme.dart';

class ClinicalNotesScreen extends StatefulWidget {
  final String patientId;
  const ClinicalNotesScreen({super.key, required this.patientId});

  @override
  State<ClinicalNotesScreen> createState() => _ClinicalNotesScreenState();
}

class _ClinicalNotesScreenState extends State<ClinicalNotesScreen> {
  final _notes = TextEditingController();
  final _observation = TextEditingController();
  String _severity = 'low';
  bool _saving = false;
  String? _result;

  @override
  void dispose() {
    _notes.dispose();
    _observation.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (_notes.text.trim().isEmpty) {
      setState(() => _result = 'Please enter notes.');
      return;
    }
    setState(() { _saving = true; _result = null; });
    try {
      // POST to /api/v1/sync — clinical observation; offline-safe queue path
      // is the same one used by symptom logs. The backend categorizes on its end.
      await ApiService.instance.postJson(
        '/api/v1/sync',
        body: {
          'patient_id': widget.patientId,
          'kind': 'clinical_observation',
          'severity': _severity,
          'notes': _notes.text.trim(),
          'observation': _observation.text.trim(),
        },
      );
      if (!mounted) return;
      setState(() {
        _saving = false;
        _result = 'Saved successfully.';
        _notes.clear();
        _observation.clear();
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _saving = false;
        _result = 'Error: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Clinical Notes'),
        backgroundColor: Monad.parchment,
        elevation: 0,
      ),
      body: Container(
        color: Monad.parchment,
        padding: const EdgeInsets.all(20),
        child: ListView(
          children: [
            Text('Field visit observation', style: Monad.subheading.copyWith(fontSize: 20)),
            const SizedBox(height: 8),
            Text('ASHA worker — add clinical notes from today\'s visit.', style: Monad.monoCaption),
            const SizedBox(height: 24),
            _label('Severity'),
            Row(children: [
              for (final s in const ['low', 'medium', 'high'])
                Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(s),
                    selected: _severity == s,
                    onSelected: (_) => setState(() => _severity = s),
                  ),
                ),
            ]),
            const SizedBox(height: 16),
            _label('Observation (brief)'),
            TextField(
              controller: _observation,
              maxLines: 2,
              decoration: const InputDecoration(border: OutlineInputBorder(), hintText: 'e.g. walking slower than usual'),
            ),
            const SizedBox(height: 16),
            _label('Notes (detailed)'),
            TextField(
              controller: _notes,
              maxLines: 6,
              decoration: const InputDecoration(border: OutlineInputBorder(), hintText: 'Detailed clinical observation'),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: _saving ? null : _save,
              icon: _saving
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.save),
              label: Text(_saving ? 'Saving…' : 'Save Notes'),
            ),
            if (_result != null) ...[
              const SizedBox(height: 16),
              Text(_result!, style: Monad.monoBodySm.copyWith(
                color: _result!.contains('successfully') || _result!.contains('Saved') ? Colors.green.shade700 : Monad.terracotta,
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _label(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: Text(text, style: Monad.monoLabel),
  );
}
