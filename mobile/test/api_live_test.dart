/// Live client->server integration check through the real ApiService.
///
/// Skipped by default (needs a running backend); run with:
///   flutter test --dart-define=LIVE_API=true --dart-define=API_BASE_URL=http://localhost:8000
/// (the extra define matters: flutter test reports an Android platform,
/// so AppConfig would otherwise point at the emulator-only 10.0.2.2).
library;

import 'package:eldercare_mobile/models/shared_models.dart';
import 'package:eldercare_mobile/services/api_service.dart';
import 'package:eldercare_mobile/services/auth_session.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _live = bool.fromEnvironment('LIVE_API');

/// Mirror the app's real auth flow: AuthSession wires tokens onto the
/// ApiService singleton (see auth_session.dart).
Future<UserModel> _loginAs(String phone) async {
  await AuthSession.instance.login(phone: phone, password: 'DemoPass123');
  return AuthSession.instance.user!;
}

void main() {
  SharedPreferences.setMockInitialValues({});
  group('live backend via ApiService', () {
    test('patient login routes to patient role', () async {
      final user = await _loginAs('919876543001');
      expect(user.role, Role.patient);
    });

    test('caregiver login routes to staff role', () async {
      final user = await _loginAs('919876543002');
      expect(user.role, isNot(Role.patient));
    });

    test('caregiver dashboard summary reflects real data', () async {
      final api = ApiService.instance;
      final user = await _loginAs('919876543002');
      final patients = await api.caregiverPatients(user.id);
      expect(patients, isNotEmpty);
      final summary = await api.patientSummary(
          patients.first['patient_id'] as String);
      expect(summary['patient_id'], isNotNull);
      expect(summary['view'], isIn(['basic', 'clinical']));
    });

    test('games session round-trip persists', () async {
      final api = ApiService.instance;
      await _loginAs('919876543001');
      final sessionId = await api.startGame(
          gameType: 'match_it', difficultyLevel: 1);
      expect(sessionId, isNotEmpty);
      await api.recordGameAction(
        sessionId: sessionId,
        actionType: 'flip_card',
        actionData: const {'card': 'a'},
        isCorrect: true,
        responseTimeMs: 900,
      );
      final summary = await api.completeGame(sessionId);
      expect(summary.accuracyPct, 100.0);
    });

    test('companions chat returns a real reply', () async {
      final api = ApiService.instance;
      await _loginAs('919876543001');
      final patient = await api.myPatient();
      final reply = await api.companionTextChat(
        patientId: patient!.id,
        message: 'hello',
        language: 'english',
      );
      expect(reply.replyText, isNotEmpty);
    });
  }, skip: !_live ? 'needs LIVE_API=true and a running backend' : false);
}
