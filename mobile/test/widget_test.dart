// Model + parsing unit tests (no widgets needed) — verifies the contract
// between the mobile layer and the backend JSON.
import 'package:flutter_test/flutter_test.dart';

import 'package:eldercare_mobile/models/game_models.dart';
import 'package:eldercare_mobile/models/shared_models.dart';

void main() {
  group('GameType helpers', () {
    test('api snake_case values map to enums', () {
      expect(gameTypeFromApi('match_it'), GameType.matchIt);
      expect(gameTypeFromApi('routine_sequencing'), GameType.routineSequencing);
      expect(gameTypeToApi(GameType.routineSequencing), 'routine_sequencing');
    });
  });

  group('RoutineStep', () {
    test('fromJson + copyWith round trip', () {
      final step = RoutineStep.fromJson(const {
        'step_id': 'meds',
        'order': 1,
        'time': '08:00',
        'title_en': 'Morning medicines',
      });
      expect(step.stepId, 'meds');
      expect(step.order, 1);

      final later = step.copyWith(isSelected: true);
      expect(later.isSelected, isTrue);
      expect(later.stepId, 'meds'); // unchanged
      expect(step.isSelected, isFalse); // original untouched
    });
  });

  group('Server JSON adapters', () {
    test('MatchItBoard.fromServerJson maps card payloads', () {
      final board = MatchItBoard.fromServerJson({
        'pack_id': 'bihu',
        'pack_name': 'Bihu Festival',
        'difficulty_level': 1,
        'pair_count': 2,
        'total_cards': 4,
        'cards': [
          {
            'card_id': 1,
            'item_id': 'jaapi',
            'name_en': 'Jaapi',
            'name_as': 'জাপি',
            'name_bn': 'জাপি',
            'name_hi': 'जापी',
            'image_url': null,
            'matched': false,
          },
          {
            'card_id': 2,
            'item_id': 'jaapi',
            'name_en': 'Jaapi',
            'name_as': 'জাপি',
            'name_bn': 'জাপি',
            'name_hi': 'जापी',
            'image_url': null,
            'matched': false,
          },
        ],
      });
      expect(board.totalCards, 4);
      expect(board.cards, hasLength(2));
      expect(board.cards.first.labelLocal, 'জাপি');
    });

    test('ReminderScheduleModel.fromJson maps schedule payload', () {
      final schedule = ReminderScheduleModel.fromJson({
        'id': 's1',
        'patient_id': 'p1',
        'reminder_type': 'medicine',
        'cadence': '08:00,14:00,20:00',
        'is_active': true,
        'created_at': '2026-09-05T00:00:00+05:30',
      });
      expect(schedule.reminderType, ReminderType.medicine);
      expect(schedule.cadence, contains('14:00'));
      expect(schedule.isActive, isTrue);
    });
  });
}
