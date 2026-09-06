/// String-key lookup for every on-screen label in the cognitive games.
///
/// All game UI text resolves through [GameLabels.of] so Indian-language
/// translation is a lookup swap (add a map entry), never a rewrite.
/// Card/step content labels live in the content packs / routine models;
/// this file covers chrome: titles, buttons, hints, dialogs, results.
library;

class GameLabels {
  GameLabels._();

  /// Supported language codes. 'en' is the fallback for any missing key.
  static const String fallbackLanguage = 'en';

  static const Map<String, Map<String, String>> _labels = {
    'en': {
      // Match It
      'matchit.title': 'Match It',
      'matchit.pairs': 'Pairs matched',
      'matchit.moves': 'Moves',
      'matchit.hint.pair': 'Try this one',
      'matchit.complete.title': 'Well done!',
      'matchit.complete.playAgain': 'Play again',
      'matchit.offlineNote': 'Result will sync when you are back online.',
      // Routine sequencing
      'routine.title': 'Daily Routine',
      'routine.tapNext': 'Tap what you do next',
      'routine.tapToReorder': 'Tap to reorder your morning',
      'routine.placed': 'Placed',
      'routine.hint.step': 'Maybe this one?',
      'routine.complete.title': 'Nicely done!',
      'routine.results.correct': 'steps placed correctly',
      'routine.results.accuracy': 'Accuracy',
      // Shared
      'common.home': 'Home',
      'common.exit': 'Exit game',
      'common.back': 'Back',
      'common.retry': 'Try again',
      'common.loading': 'Getting your game ready…',
      'common.error.offline': 'Playing offline — progress is saved.',
      'common.easy': 'Easy',
      'common.medium': 'Medium',
      'common.hard': 'Hard',
    },
    'as': {
      // Match It
      'matchit.title': 'মিলাওক',
      'matchit.pairs': 'মিলা যোৰা',
      'matchit.moves': 'চেষ্টা',
      'matchit.hint.pair': 'এইটো চাওক',
      'matchit.complete.title': 'বৰ ভাল!',
      'matchit.complete.playAgain': 'আকৌ খেলক',
      'matchit.offlineNote': 'নেটৱৰ্ক আহিলে ফলাফল পঠিয়াই দিয়া হ\'ব।',
      // Routine sequencing
      'routine.title': 'দৈনিক অভ্যাস',
      'routine.tapNext': 'ইয়াৰ পাছত কি কৰে টিপ কৰক',
      'routine.tapToReorder': 'আপোনাৰ পুৱাৰ কাম সজাওক',
      'routine.placed': 'স্থাপন কৰা',
      'routine.hint.step': 'নহয় এইটো?',
      'routine.complete.title': 'বৰ ভাল কৰিলে!',
      'routine.results.correct': 'টো পদক্ষেপ শুদ্ধকৈ সজোৱা হ\'ল',
      'routine.results.accuracy': 'শুদ্ধতা',
      // Shared
      'common.home': 'ঘৰ',
      'common.exit': 'খেল এৰক',
      'common.back': 'উভতি যাওক',
      'common.retry': 'আকৌ চেষ্টা কৰক',
      'common.loading': 'খেল সাজু কৰি আছোঁ…',
      'common.error.offline': 'অফলাইনত খেলা হৈছে — ফলাফল ৰাখি থকা হ\'ল।',
      'common.easy': 'সহজ',
      'common.medium': 'মজলীয়া',
      'common.hard': 'কঠিন',
    },
  };

  /// Resolve [key] for [languageCode], falling back to English, then key.
  static String of(String languageCode, String key) {
    final lang = _labels[languageCode] ?? _labels[fallbackLanguage]!;
    return lang[key] ?? _labels[fallbackLanguage]![key] ?? key;
  }
}
