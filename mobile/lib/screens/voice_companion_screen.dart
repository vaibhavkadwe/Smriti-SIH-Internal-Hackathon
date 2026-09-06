/// Voice Companion — warm conversation with the elder in their language.
///
/// MVP wiring uses text chat against POST /companion/chat/text. Real audio
/// capture/TTS playback requires the speech plugins (see pubspec TODO) — the
/// backend voice pipeline (Bhashini ASR -> Claude -> TTS) is fully ready.
library;

import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../theme/monad_theme.dart';

class VoiceCompanionScreen extends StatefulWidget {
  final String patientId;

  const VoiceCompanionScreen({super.key, required this.patientId});

  @override
  State<VoiceCompanionScreen> createState() => _VoiceCompanionScreenState();
}

class _VoiceCompanionScreenState extends State<VoiceCompanionScreen> {
  final ApiService _api = ApiService.instance;

  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, String>> _history = [];

  String _selectedLanguage = 'assamese';
  bool _sending = false;
  String _reply = 'নমস্কাৰ! মই আপোনাৰ লগত আছোঁ। আপুনি আজি কেনে আছে?';
  bool _wasFallback = false;

  static const Map<String, String> _languages = {
    'assamese': 'অসমীয়া (Assamese)',
    'bengali': 'বাংলা (Bengali)',
    'hindi': 'हिन्दी (Hindi)',
    'english': 'English',
  };

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _send(String rawMessage) async {
    final message = rawMessage.trim();
    if (message.isEmpty || _sending) return;
    _messageController.clear();

    setState(() {
      _sending = true;
      _history.add({'role': 'user', 'content': message});
    });

    try {
      final result = await _api.companionTextChat(
        patientId: widget.patientId,
        message: message,
        language: _selectedLanguage,
        history: _history.take(_history.length - 1).toList(),
      );
      if (!mounted) return;
      setState(() {
        _reply = result.replyText;
        _wasFallback = result.fallback;
        _history.add({'role': 'assistant', 'content': result.replyText});
      });
    } on Exception catch (e) {
      if (!mounted) return;
      setState(() {
        _reply = 'I am here with you. Please try again in a moment.';
        _wasFallback = true;
        _history.removeLast();
      });
      debugPrint('Companion chat failed: $e');
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Aai Companion / মৰমৰ সংগী'),
        centerTitle: false,
        actions: [
          DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: _selectedLanguage,
              icon: const Icon(Icons.language, color: Monad.offBlack),
              items: _languages.entries
                  .map((e) => DropdownMenuItem(
                      value: e.key,
                      child: Text(e.value, style: Monad.monoBodySm)))
                  .toList(),
              onChanged: (v) {
                if (v != null) setState(() => _selectedLanguage = v);
              },
            ),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  _companionCard(),
                  if (_wasFallback) ...[
                    const SizedBox(height: 8),
                    Center(
                      child: Text(
                        'Companion is in offline mode — connect to enable full conversation.',
                        style: Monad.monoCaption.copyWith(color: Monad.crimson),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            _inputBar(),
          ],
        ),
      ),
    );
  }

  Widget _companionCard() {
    return Card(
      elevation: 0,
      shape: Monad.cardShape,
      color: Monad.periwinkleMist,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Container(
              width: 16,
              height: 16,
              margin: const EdgeInsets.only(bottom: 14),
              decoration: const BoxDecoration(
                color: Monad.lakeBlue,
                shape: BoxShape.circle,
              ),
            ),
            Text(
              _reply,
              textAlign: TextAlign.center,
              style: Monad.monoBodyLg.copyWith(color: Monad.offBlack, height: 1.4),
            ),
          ],
        ),
      ),
    );
  }

  Widget _inputBar() {
    return Container(
      padding: const EdgeInsets.all(12),
      color: Monad.parchment,
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _messageController,
              textInputAction: TextInputAction.send,
              onSubmitted: _send,
              style: Monad.monoLabel,
              decoration: InputDecoration(
                hintText: 'Type a message…',
                filled: true,
                fillColor: Monad.parchment,
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(Monad.radiusMin),
                    borderSide: const BorderSide(color: Monad.ash)),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
              ),
            ),
          ),
          const SizedBox(width: 10),
          IconButton.filled(
            onPressed: _sending ? null : () => _send(_messageController.text),
            iconSize: 30,
            icon: _sending
                ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.send),
          ),
        ],
      ),
    );
  }
}
