/// Voice Companion — warm, calm conversation with the elder in their language.
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
  final ScrollController _scrollController = ScrollController();
  final List<_ChatMessage> _messages = [];

  String _selectedLanguage = 'assamese';
  bool _sending = false;
  bool _wasFallback = false;

  static const Map<String, String> _languages = {
    'assamese': 'অসমীয়া',
    'bengali': 'বাংলা',
    'hindi': 'हिन्दी',
    'english': 'English',
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
                .map((e) => PopupMenuItem(
                      value: e.key,
                      child: Row(
                        children: [
                          if (e.key == _selectedLanguage)
                            const Icon(Icons.check, size: 16, color: Monad.lakeBlue),
                          if (e.key != _selectedLanguage) const SizedBox(width: 16),
                          const SizedBox(width: 8),
                          Text(e.value, style: Monad.monoBody),
                        ],
                      ),
                    ))
                .toList(),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFF0F6FF), Monad.parchment],
            stops: [0.0, 0.35],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              if (_wasFallback)
                _offlineBanner(),
              Expanded(
                child: ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) => _messageBubble(_messages[index]),
                ),
              ),
              _inputBar(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _offlineBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: const Color(0xFFFFF3E0),
      child: Row(
        children: [
          const Icon(Icons.wifi_off, size: 14, color: Color(0xFFD4A030)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Offline mode — some responses are simplified.',
              style: Monad.monoCaption.copyWith(color: const Color(0xFFD4A030)),
            ),
          ),
        ],
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
                color: isUser ? Monad.lakeBlue : Monad.white,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(20),
                  topRight: const Radius.circular(20),
                  bottomLeft: Radius.circular(isUser ? 20 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 20),
                ),
                border: isUser
                    ? null
                    : Border.all(color: Monad.ash.withValues(alpha: 0.5)),
                boxShadow: [
                  BoxShadow(
                    color: (isUser ? Monad.lakeBlue : Colors.black).withValues(alpha: 0.06),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Text(
                msg.content,
                style: Monad.monoBody.copyWith(
                  color: isUser ? Monad.white : Monad.offBlack,
                  height: 1.35,
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

  Widget _companionAvatar() {
    return Container(
      width: 36, height: 36,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF6B9DFC), Monad.lakeBlue],
        ),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Monad.lakeBlue.withValues(alpha: 0.3),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Icon(Icons.favorite, color: Monad.white, size: 18),
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
      decoration: BoxDecoration(
        color: Monad.white,
        border: Border(top: BorderSide(color: Monad.ash.withValues(alpha: 0.5))),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 4, offset: const Offset(0, -2))],
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
                style: Monad.monoLabel.copyWith(fontSize: 16),
                decoration: InputDecoration(
                  hintText: _selectedLanguage == 'assamese'
                      ? 'বার্তা লিখুন…'
                      : 'Type a message…',
                  hintStyle: Monad.monoBody.copyWith(color: Monad.smoke),
                  filled: true,
                  fillColor: Monad.parchment,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(25),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Container(
            width: 50, height: 50,
            decoration: BoxDecoration(
              color: Monad.lakeBlue,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: Monad.lakeBlue.withValues(alpha: 0.4),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: IconButton(
              onPressed: _sending ? null : () => _send(_messageController.text),
              icon: _sending
                  ? const SizedBox(width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Monad.white))
                  : const Icon(Icons.send, color: Monad.white, size: 22),
            ),
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
