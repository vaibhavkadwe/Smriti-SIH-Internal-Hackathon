/// Voice Companion — warm, calm conversation with the elder in their language.
library;

import 'package:flutter/material.dart';

import '../config/app_config.dart';
import '../services/api_service.dart';
import '../theme/monad_theme.dart';
import '../widgets/monad/monad_pill_button.dart';

class VoiceCompanionScreen extends StatefulWidget {
  final String patientId;

  const VoiceCompanionScreen({super.key, required this.patientId});

  @override
  State<VoiceCompanionScreen> createState() => _VoiceCompanionScreenState();
}

class _VoiceCompanionScreenState extends State<VoiceCompanionScreen> {
  final ApiService _api = ApiService.instance;

  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<_ChatMessage> _messages = [];

  String _selectedLanguage = 'assamese';
  bool _sending = false;
  bool _wasFallback = false;

  /// Languages the active backend provider actually covers (from
  /// /language/status). Null while loading or when the call fails —
  /// all ten picker entries stay enabled as before.
  Set<String>? _providerLanguages;

  static const Map<String, String> _languages = {
    'assamese': 'অসমীয়া',
    'bengali': 'বাংলা',
    'hindi': 'हिन्दी',
    'english': 'English',
    'mizo': 'Mizo',
    'meitei': 'Meitei (Manipuri)',
    'khasi': 'Khasi',
    'bodo': 'Bodo',
    'garo': 'Garo',
    'nepali': 'Nepali',
  };

  // Per-language input hint. Falls back to English if a language is added
  // without a hint here.
  static const Map<String, String> _hints = {
    'assamese': 'বার্তা লিখক…',
    'bengali': 'একটি বার্তা লিখুন…',
    'hindi': 'एक संदेश लिखें…',
    'english': 'Type a message…',
    'mizo': 'Message emai…',
    'meitei': 'Message ei chaba…',
    'khasi': 'Nongsain ka jingiew…',
    'bodo': 'Message jawabo…',
    'garo': 'Message gnaty e…',
    'nepali': 'Sandaitha…',
  };

  static const _greeting = 'নমস্কাৰ! মই আপোনাৰ লগত আছোঁ। আজি কেনে আছে?';

  @override
  void initState() {
    super.initState();
    _messages.add(_ChatMessage(
      content: _greeting,
      isCompanion: true,
      timestamp: DateTime.now(),
    ));
    _loadProviderLanguages();
  }

  Future<void> _loadProviderLanguages() async {
    // The active provider may not cover every picker language (AI4Bharat
    // models exclude Khasi + Mizo). The backend reports its supported set;
    // uncovered languages show "not yet available" and are disabled rather
    // than erroring at send time.
    try {
      final data = await _api
          .getJson('${AppConfig.apiV1}/language/status');
      final langs = (data['supported_languages'] as List?)
              ?.map((e) => e.toString().toLowerCase())
              .toSet();
      if (mounted) setState(() => _providerLanguages = langs);
    } on Exception {
      // Offline or backend down — keep all languages enabled (mock covers all).
      if (mounted) setState(() => _providerLanguages = null);
    }
  }

  bool _languageAvailable(String code) {
    final supported = _providerLanguages;
    return supported == null || supported.contains(code);
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _send(String rawMessage) async {
    final message = rawMessage.trim();
    if (message.isEmpty || _sending) return;
    _messageController.clear();

    final userMsg = _ChatMessage(content: message, isCompanion: false, timestamp: DateTime.now());
    setState(() {
      _messages.add(userMsg);
      _sending = true;
      _wasFallback = false;
    });
    _scrollToBottom();

    try {
      final result = await _api.companionTextChat(
        patientId: widget.patientId,
        message: message,
        language: _selectedLanguage,
        history: _messages
            .where((m) => !m.isCompanion || m.content != _greeting)
            .map((m) => {'role': m.isCompanion ? 'assistant' : 'user', 'content': m.content})
            .toList(),
      );
      if (!mounted) return;
      setState(() {
        _messages.add(_ChatMessage(
          content: result.replyText,
          isCompanion: true,
          timestamp: DateTime.now(),
        ));
        _wasFallback = result.fallback;
        _sending = false;
      });
    } on Exception catch (e) {
      if (!mounted) return;
      setState(() {
        _messages.add(_ChatMessage(
          content: 'I am here with you. Please try again.',
          isCompanion: true,
          timestamp: DateTime.now(),
          isFallback: true,
        ));
        _sending = false;
      });
      debugPrint('Companion chat failed: $e');
    }
    _scrollToBottom();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Aai Companion'),
        centerTitle: false,
        actions: [
          PopupMenuButton<String>(
            icon: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.language, color: Monad.offBlack, size: 20),
                const SizedBox(width: 4),
                Text(
                  _languages[_selectedLanguage] ?? _selectedLanguage,
                  style: Monad.monoCaption.copyWith(color: Monad.offBlack),
                ),
              ],
            ),
            onSelected: (v) => setState(() => _selectedLanguage = v),
            itemBuilder: (context) => _languages.entries
                .map((e) {
                  final available = _languageAvailable(e.key);
                  return PopupMenuItem(
                      value: available ? e.key : null,
                      enabled: available,
                      child: Row(
                        children: [
                          if (e.key == _selectedLanguage)
                            const Icon(Icons.check, size: 16, color: Monad.lakeBlue),
                          if (e.key != _selectedLanguage) const SizedBox(width: 16),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              available
                                  ? e.value
                                  : '${e.value} — not yet available',
                              style: Monad.monoBody.copyWith(
                                color: available
                                    ? Monad.offBlack
                                    : Monad.smoke,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                })
                .toList(),
          ),
          const SizedBox(width: 8),
        ],
      ),
      // Parchment canvas — no gradient washes on patient-facing chrome.
      body: SafeArea(
        child: Column(
          children: [
            if (_wasFallback)
              _offlineBanner(),
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                itemCount: _messages.length + (_sending ? 1 : 0),
                itemBuilder: (context, index) => index < _messages.length
                    ? _messageBubble(_messages[index])
                    : _typingBubble(),
              ),
            ),
            _inputBar(),
          ],
        ),
      ),
    );
  }

  Widget _offlineBanner() {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Center(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: ShapeDecoration(
            color: Monad.tintGold,
            shape: const StadiumBorder(side: BorderSide(color: Monad.ash, width: 1)),
          ),
          child: Text(
            'OFFLINE MODE — RESPONSES SIMPLIFIED',
            style: Monad.monoBodySm.copyWith(color: Monad.offBlack),
          ),
        ),
      ),
    );
  }

  Widget _messageBubble(_ChatMessage msg) {
    final isUser = !msg.isCompanion;
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            _companionAvatar(),
            const SizedBox(width: 10),
          ],
          Flexible(
            child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.72,
              ),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: isUser ? Monad.parchment : Monad.periwinkleMist,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(isUser ? 16 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 16),
                ),
                border: Border.all(color: Monad.ash, width: 1),
              ),
              child: Text(
                msg.content,
                style: Monad.patientBody.copyWith(
                  color: Monad.offBlack,
                ),
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 10),
            _userAvatar(),
          ],
        ],
      ),
    );
  }

  Widget _typingBubble() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          _companionAvatar(),
          const SizedBox(width: 10),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: Monad.periwinkleMist,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                  bottomLeft: Radius.circular(4),
                  bottomRight: Radius.circular(16),
                ),
                border: Border.all(color: Monad.ash, width: 1),
              ),
              child: Text('…', style: Monad.patientBody),
            ),
          ),
        ],
      ),
    );
  }

  Widget _companionAvatar() {
    return Container(
      width: 36,
      height: 36,
      decoration: const BoxDecoration(
        color: Monad.periwinkleMist,
        shape: BoxShape.circle,
        border: Border.fromBorderSide(BorderSide(color: Monad.ash, width: 1)),
      ),
      child: const Icon(Icons.favorite, color: Monad.offBlack, size: 18),
    );
  }

  Widget _userAvatar() {
    return Container(
      width: 36, height: 36,
      decoration: BoxDecoration(
        color: Monad.periwinkleMist,
        shape: BoxShape.circle,
        border: Border.all(color: Monad.ash, width: 1),
      ),
      child: const Icon(Icons.person, color: Monad.graphite, size: 18),
    );
  }

  Widget _inputBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      decoration: const BoxDecoration(
        color: Monad.parchment,
        border: Border(top: BorderSide(color: Monad.ash, width: 1)),
      ),
      child: Row(
        children: [
          Expanded(
            child: SizedBox(
              height: 50,
              child: TextField(
                controller: _messageController,
                textInputAction: TextInputAction.send,
                onSubmitted: _send,
                // Patient-facing input floor: 20px.
                style: Monad.patientBody,
                decoration: InputDecoration(
                  hintText: _hints[_selectedLanguage] ?? 'Type a message…',
                  hintStyle: Monad.monoBody.copyWith(color: Monad.smoke),
                  filled: true,
                  fillColor: Monad.parchment,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(Monad.radiusMin),
                    borderSide: const BorderSide(color: Monad.ash, width: 1),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(Monad.radiusMin),
                    borderSide: const BorderSide(color: Monad.ash, width: 1),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(Monad.radiusMin),
                    borderSide: const BorderSide(color: Monad.lakeBlue, width: 1),
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          MonadPillButton(
            label: 'Send',
            variant: MonadPillVariant.primary,
            busy: _sending,
            onPressed: () => _send(_messageController.text),
          ),
        ],
      ),
    );
  }
}

class _ChatMessage {
  final String content;
  final bool isCompanion;
  final DateTime timestamp;
  final bool isFallback;

  _ChatMessage({
    required this.content,
    required this.isCompanion,
    required this.timestamp,
    this.isFallback = false,
  });
}
