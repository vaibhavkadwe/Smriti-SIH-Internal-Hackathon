/// Match It — memory card-flip game backed by the backend content packs.
///
/// Flow: start session -> fetch board from server -> play locally ->
/// complete session (reports accuracy / response time to the backend).
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
  bool _offline = false;

  @override
  void initState() {
    super.initState();
    _startGame();
  }

  @override
  void dispose() {
    _flipReset?.cancel();
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
    }
  }

  void _onCardTap(MatchItCard card) {
    final game = _game;
    if (game == null || game.state != MatchItState.playing) return;

    final next = _logic.handleCardTap(game, card.id);
    if (next == null) return;

    setState(() => _game = next);

    if (next.state == MatchItState.checking) {
      _flipReset?.cancel();
      _flipReset = Timer(const Duration(milliseconds: 900), () {
        if (!mounted) return;
        final reset = _logic.resetFlippedCards(_game!);
        setState(() => _game = reset);
      });
    } else if (next.isComplete) {
      _completeAndShowResults(next);
    }
  }

  Future<void> _completeAndShowResults(MatchItGameState finalState) async {
    final sessionId = _sessionId;
    if (sessionId == null) return;

    GameSessionSummary? summary;
    try {
      if (!_offline) {
        summary = await _api.completeGame(sessionId);
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
        actions: const [],
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
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: game.totalPairs == 9 ? 6 : (game.totalPairs == 6 ? 4 : 4),
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
    return GestureDetector(
      onTap: card.isMatched ? null : onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        decoration: BoxDecoration(
          color: revealed
              ? (card.isMatched ? Colors.green.shade100 : Colors.teal.shade50)
              : Colors.teal.shade400,
          borderRadius: BorderRadius.circular(14),
          border: revealed ? Border.all(color: Colors.teal.shade300, width: 2) : null,
        ),
        child: Center(
          child: revealed
              ? Padding(
                  padding: const EdgeInsets.all(4),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (card.isMatched)
                        const Icon(Icons.check_circle, color: Colors.green, size: 28),
                      const SizedBox(height: 2),
                      Text(
                        card.labelLocal,
                        textAlign: TextAlign.center,
                        maxLines: 3,
                        style: TextStyle(
                          fontSize: card.labelLocal.length > 12 ? 12 : 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                )
              : const Icon(Icons.self_improvement, color: Colors.white, size: 40),
        ),
      ),
    );
  }
}
