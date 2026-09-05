/// Match It — memory card-flip game backed by the backend content packs.
///
/// Flow: start session -> fetch board from server -> play locally ->
/// complete session (reports accuracy / response time to the backend).
///
/// Telemetry: every flip is buffered and POSTed fire-and-forget to
/// /games/sessions/{id}/actions; a 10s idle "stuck" event fires once per
/// episode while playing. On offline/failure the buffered actions ride the
/// existing sync queue via OfflineSyncService.
///
/// Accessibility: 4-column grid keeps touch targets >=60dp, large type,
/// semantic labels on every card, soft (silent) feedback hooks, and zero
/// punishment animation on wrong answers (cards simply flip back).
library;

import 'dart:async';

import 'package:flutter/material.dart';

import '../data/local_content_packs.dart';
import '../models/game_models.dart';
import '../models/shared_models.dart';
import '../services/api_service.dart';
import '../services/auth_session.dart';
import '../services/match_it_service.dart';
import '../services/offline_sync_service.dart';

/// Warm, calm, high-contrast palette for elderly eyes (NER tones).
class _NERPalette {
  static const cardBack = Color(0xFFB45309); // warm terracotta
  static const cardFace = Color(0xFFFFFBF5); // warm cream
  static const matchedBg = Color(0xFFE8F5E9); // soft success green
  static const matchedBorder = Color(0xFF2E7D32);
  static const faceBorder = Color(0xFFD6A456); // soft gold
  static const faceText = Color(0xFF3E2723); // deep warm brown
}

class MatchItScreen extends StatefulWidget {
  final String packId;
  final String packName;
  final int difficultyLevel;

  const MatchItScreen({
    super.key,
    required this.packId,
    required this.packName,
    required this.difficultyLevel,
  });

  @override
  State<MatchItScreen> createState() => _MatchItScreenState();
}

class _MatchItScreenState extends State<MatchItScreen> {
  final ApiService _api = ApiService.instance;
  final MatchItService _logic = MatchItService();

  MatchItGameState? _game;
  String? _sessionId;
  String? _error;
  Timer? _flipReset;
  Timer? _stuckTimer;
  bool _offline = false;

  /// Buffered actions for this session (drives the offline sync path).
  final List<GameAction> _bufferedActions = [];

  static const _stuckThreshold = Duration(seconds: 10);

  @override
  void initState() {
    super.initState();
    _startGame();
  }

  @override
  void dispose() {
    _flipReset?.cancel();
    _stuckTimer?.cancel();
    super.dispose();
  }

  Future<void> _startGame() async {
    setState(() {
      _error = null;
      _offline = false;
    });
    try {
      final sessionId = await _api.startGame(
        gameType: 'match_it',
        difficultyLevel: widget.difficultyLevel,
        contentPackId: widget.packId,
      );
      final board = await _api.matchItBoard(
        packId: widget.packId,
        difficultyLevel: widget.difficultyLevel,
      );
      if (!mounted) return;
      setState(() {
        _sessionId = sessionId;
        _game = _logic.initializeGame(sessionId, board);
      });
      _armStuckTimer();
    } on Exception {
      // Offline-first: play from the local NER pack and queue the session later.
      final board = LocalContentPacks.board(
        widget.packId,
        widget.difficultyLevel,
        widget.packName,
      );
      final sessionId = 'offline_${DateTime.now().millisecondsSinceEpoch}';
      if (!mounted) return;
      setState(() {
        _offline = true;
        _sessionId = sessionId;
        _game = _logic.initializeGame(sessionId, board);
      });
      _armStuckTimer();
    }
  }

  // ------------------------------------------------------------------
  // Telemetry
  // ------------------------------------------------------------------

  void _bufferAndSend(GameAction action) {
    _bufferedActions.add(action);
    if (_offline) return; // stays buffered; flushed via sync queue on complete
    // ponytail: fire-and-forget, accept per-move undercount on flaky networks;
    // full replay only when the session itself must be queued offline.
    unawaited(
      _api
          .recordGameAction(
            sessionId: action.sessionId,
            actionType: action.actionType,
            actionData: action.actionData,
            isCorrect: action.isCorrect,
            responseTimeMs: action.responseTimeMs,
          )
          .catchError((_) => false),
    );
  }

  void _armStuckTimer() {
    _stuckTimer?.cancel();
    final game = _game;
    if (game == null || game.state != MatchItState.playing) return;
    _stuckTimer = Timer(_stuckThreshold, () {
      final current = _game;
      if (current == null || current.state != MatchItState.playing) return;
      final sessionId = _sessionId;
      if (sessionId == null) return;
      // One shot per idle episode; rearmed by the next tap.
      _bufferAndSend(GameAction(
        id: 'stuck_${DateTime.now().millisecondsSinceEpoch}',
        sessionId: sessionId,
        actionType: 'stuck',
        actionData: const {'stuck_duration_ms': 10000},
        timestamp: DateTime.now(),
      ));
    });
  }

  // ------------------------------------------------------------------
  // Gameplay
  // ------------------------------------------------------------------

  void _onCardTap(MatchItCard card) {
    final game = _game;
    if (game == null || game.state != MatchItState.playing) return;

    final wasSecondFlip = game.flippedCards[0] != null;
    final previousCorrect = game.correctMatches;
    final next = _logic.handleCardTap(game, card.id);
    if (next == null) return;

    setState(() => _game = next);

    final sessionId = _sessionId;
    if (sessionId != null) {
      final resolved = wasSecondFlip; // second flip resolves the attempt
      final isCorrect = resolved ? next.correctMatches > previousCorrect : null;
      _bufferAndSend(GameAction(
        id: 'act_${DateTime.now().millisecondsSinceEpoch}_${card.id}',
        sessionId: sessionId,
        actionType: 'flip_card',
        actionData:
            _logic.getCardFlipActionData(card.id, card, resolved ? isCorrect : null),
        isCorrect: isCorrect,
        responseTimeMs: resolved ? next.responseTimesMs.last : null,
        timestamp: DateTime.now(),
      ));
    }
    _softFeedback(next.state == MatchItState.checking ? false : true);

    if (next.state == MatchItState.checking) {
      _stuckTimer?.cancel();
      _flipReset?.cancel();
      _flipReset = Timer(const Duration(milliseconds: 900), () {
        if (!mounted) return;
        final reset = _logic.resetFlippedCards(_game!);
        setState(() => _game = reset);
        _armStuckTimer();
      });
    } else if (next.isComplete) {
      _stuckTimer?.cancel();
      _completeAndShowResults(next);
    } else {
      _armStuckTimer();
    }
  }

  Future<void> _completeAndShowResults(MatchItGameState finalState) async {
    final sessionId = _sessionId;
    if (sessionId == null) return;

    GameSessionSummary? summary;
    try {
      if (!_offline) {
        summary = await _api.completeGame(sessionId);
        _bufferedActions.clear(); // server holds the authoritative record
      } else {
        throw ApiException('offline session');
      }
    } on Exception catch (e) {
      debugPrint('Could not complete session online: $e');
      await OfflineSyncService.instance.enqueueGameSession(
        patientId: AuthSession.instance.user?.id ?? '',
        session: GameSessionModel(
          id: sessionId,
          patientId: AuthSession.instance.user?.id ?? '',
          gameType: GameType.matchIt,
          difficultyLevel: widget.difficultyLevel,
          attempts: finalState.attempts,
          correctCount: finalState.correctMatches,
          incorrectCount: finalState.incorrectMatches,
          avgResponseTimeMs: finalState.avgResponseTimeMs,
          startedAt: finalState.gameStartedAt,
          completedAt: DateTime.now(),
        ),
        actions: List<GameAction>.from(_bufferedActions),
      );
    }

    if (!mounted) return;
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Game Completed! 🎉', style: TextStyle(fontSize: 24)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _resultRow('Accuracy', '${finalState.accuracyPct.toStringAsFixed(1)}%'),
            _resultRow('Pairs matched', '${finalState.matchedPairs}/${finalState.totalPairs}'),
            _resultRow('Average response', '${finalState.avgResponseTimeMs.toStringAsFixed(0)} ms'),
            if (summary == null) ...[
              const SizedBox(height: 12),
              const Text(
                'Offline: result will sync when you reconnect.',
                style: TextStyle(color: Colors.orange, fontSize: 14),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Back', style: TextStyle(fontSize: 18)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              _restart();
            },
            child: const Text('Play Again', style: TextStyle(fontSize: 18)),
          ),
        ],
      ),
    );
  }

  /// Soft auditory feedback hook — silent no-op until audio assets land.
  // ponytail: wire SystemSound.play or a localized asset here when the
  // audio pack is added; never called on wrong answers (no punishment).
  void _softFeedback(bool positive) {}

  Widget _resultRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 16, color: Colors.grey)),
          Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  void _restart() {
    _flipReset?.cancel();
    _stuckTimer?.cancel();
    _bufferedActions.clear();
    setState(() {
      _game = null;
      _sessionId = null;
    });
    _startGame();
  }

  @override
  Widget build(BuildContext context) {
    final game = _game;
    return Scaffold(
      appBar: AppBar(
        title: Text('Match It: ${widget.packName}', style: const TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        actions: [
          if (game != null)
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Center(
                child: Text(
                  '${game.matchedPairs}/${game.totalPairs}',
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
              ),
            ),
        ],
      ),
      body: _error != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.cloud_off, size: 64, color: Colors.grey),
                  const SizedBox(height: 12),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: Text(
                      _error!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 18),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _startGame,
                    child: const Text('Try Again', style: TextStyle(fontSize: 18)),
                  ),
                ],
              ),
            )
          : game == null
              ? const Center(child: CircularProgressIndicator())
              : GridView.builder(
                  padding: const EdgeInsets.all(16),
                  // 4 columns keeps every touch target >=60dp on 360dp phones
                  // (level-3's 6 columns gave ~46dp cells — below the
                  // 60dp elderly-accessibility floor).
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 4,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                    childAspectRatio: 0.8,
                  ),
                  itemCount: game.cards.length,
                  itemBuilder: (context, index) => _CardView(
                    card: game.cards[index],
                    onTap: () => _onCardTap(game.cards[index]),
                  ),
                ),
    );
  }
}

class _CardView extends StatelessWidget {
  final MatchItCard card;
  final VoidCallback onTap;

  const _CardView({required this.card, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final revealed = card.isFlipped || card.isMatched;
    return Semantics(
      button: true,
      label: revealed
          ? card.labelLocal
          : 'Card ${card.id}',
      child: GestureDetector(
        onTap: card.isMatched ? null : onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          decoration: BoxDecoration(
            color: card.isMatched
                ? _NERPalette.matchedBg
                : revealed
                    ? _NERPalette.cardFace
                    : _NERPalette.cardBack,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: card.isMatched
                  ? _NERPalette.matchedBorder
                  : revealed
                      ? _NERPalette.faceBorder
                      : _NERPalette.cardBack,
              width: 2,
            ),
          ),
          child: Center(
            child: revealed
                ? Padding(
                    padding: const EdgeInsets.all(4),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (card.isMatched)
                          const Icon(Icons.check_circle,
                              color: Color(0xFF2E7D32), size: 28),
                        const SizedBox(height: 2),
                        Text(
                          card.labelLocal,
                          textAlign: TextAlign.center,
                          maxLines: 3,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: _NERPalette.faceText,
                          ),
                        ),
                      ],
                    ),
                  )
                : const Icon(Icons.self_improvement,
                    color: Colors.white, size: 40),
          ),
        ),
      ),
    );
  }
}
