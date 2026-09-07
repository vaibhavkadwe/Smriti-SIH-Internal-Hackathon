/// Medical document upload for RAG pipeline — patient/family can upload a
/// prescription, discharge summary, or doctor's note. Uses existing `http`
/// package (multipart via multipart/form-data string); no new dependencies.
/// Backend endpoint: POST /api/v1/reports/documents/upload
library;

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../theme/monad_theme.dart';

class RagUploadScreen extends StatefulWidget {
  final String patientId;
  const RagUploadScreen({super.key, required this.patientId});

  @override
  State<RagUploadScreen> createState() => _RagUploadScreenState();
}

class _RagUploadScreenState extends State<RagUploadScreen> {
  bool _uploading = false;
  String? _result;
  String? _filePath;

  void _pickFile() {
    // Web/desktop: file picker via HTML input (not implemented fully here);
    // placeholder that guides the user to use the dashboard widget or provide
    // a file path via device picker. The real upload path uses http.MultipartRequest.
    setState(() {
      _result = 'Use file picker to select a PDF / text file, then tap Upload.';
    });
  }

  Future<void> _upload() async {
    if (_filePath == null || _filePath!.isEmpty) {
      setState(() => _result = 'Please select a file first.');
      return;
    }
    setState(() { _uploading = true; _result = null; });
    try {
      final file = File(_filePath!);
      final bytes = await file.readAsBytes();
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('${AppConfig.apiBaseUrl}/api/v1/reports/documents/upload'),
      );
      // The endpoint expects patient_id + file + doc_type + title
      request.fields['patient_id'] = widget.patientId;
      request.fields['doc_type'] = 'prescription';
      request.fields['title'] = 'Medical Document';
      request.files.add(http.MultipartFile.fromBytes('file', bytes,
          filename: file.path.split('/').last));
      final streamed = await request.send();
      final res = await http.Response.fromStream(streamed);
      setState(() {
        _uploading = false;
        _result = res.statusCode >= 200 && res.statusCode < 300
            ? 'Uploaded successfully (HTTP ${res.statusCode}).'
            : 'Failed: HTTP ${res.statusCode} — ${res.body}';
      });
    } catch (e) {
      setState(() { _uploading = false; _result = 'Error: $e'; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Medical Documents'),
        backgroundColor: Monad.parchment,
        elevation: 0,
      ),
      body: Container(
        color: Monad.parchment,
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Upload prescriptions, discharge summaries, or care plans.',
                style: Monad.subheading.copyWith(fontSize: 20)),
            const SizedBox(height: 8),
            Text('They become searchable in the clinical Q&A flow.',
                style: Monad.monoCaption),
            const SizedBox(height: 24),
            Card(
              elevation: 0,
              shape: Monad.cardShape,
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Monad.white,
                  borderRadius: BorderRadius.circular(Monad.radiusCard),
                  border: Border.all(color: Monad.ash.withValues(alpha: 0.4)),
                  boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 4, offset: const Offset(0, 2))],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Icon(Icons.upload_file, color: Monad.indigo, size: 28),
                      const SizedBox(width: 12),
                      Expanded(child: Text('Document File', style: Monad.monoLabel)),
                    ]),
                    const SizedBox(height: 12),
                    Text(_filePath ?? 'No file selected.', style: Monad.monoBodySm),
                    const SizedBox(height: 8),
                    FilledButton.icon(
                      onPressed: _uploading ? null : _pickFile,
                      icon: const Icon(Icons.attach_file),
                      label: const Text('Select File'),
                    ),
                    const SizedBox(height: 8),
                    FilledButton.icon(
                      onPressed: (_uploading || _filePath == null || _filePath!.isEmpty) ? null : _upload,
                      icon: _uploading ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.upload),
                      label: Text(_uploading ? 'Uploading…' : 'Upload'),
                    ),
                    if (_result != null) ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: _result!.contains('successfully') ? Colors.green.withValues(alpha: 0.08) : Colors.orange.withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(_result!, style: Monad.monoBodySm.copyWith(
                          color: _result!.contains('successfully') ? Colors.green.shade700 : Monad.terracotta,
                        )),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              elevation: 0,
              shape: Monad.cardShape,
              child: Container(
                padding: const EdgeInsets.all(16),
                color: Monad.periwinkleMist.withValues(alpha: 0.3),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('How it works', style: Monad.monoLabel),
                    const SizedBox(height: 6),
                    Text('Uploaded PDFs/text files are extracted, chunked, embedded, and made searchable through clinical questions in this app.', style: Monad.monoBodySm.copyWith(color: Monad.graphite)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
