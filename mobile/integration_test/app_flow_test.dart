/// On-device end-to-end (emulator-5554, backend at 10.0.2.2:8000).
///
/// Run: flutter test integration_test/app_flow_test.dart
/// NOTE: pump() with fixed durations only — pumpAndSettle never settles
/// here (periodic stuck-timer + animations keep the scheduler busy).
library;

import 'package:eldercare_mobile/main.dart';
import 'package:eldercare_mobile/services/auth_session.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<void> _loginAs(WidgetTester tester, String phone) async {
  SharedPreferences.setMockInitialValues({});
  await AuthSession.instance.restore(); // pumpWidget skips main(), so drive restore here
  await tester.pumpWidget(const ElderCareApp());
  await tester.pump(const Duration(seconds: 2));
  await tester.enterText(
      find.widgetWithText(TextField, 'Phone number'), phone);
  await tester.enterText(
      find.widgetWithText(TextField, 'Password'), 'DemoPass123');
  await tester.pump(const Duration(milliseconds: 500));
  await tester.tap(find.widgetWithText(FilledButton, 'Sign In'));
  await tester.pump(const Duration(seconds: 6));
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('patient login, play Match It to a win', (tester) async {
    await _loginAs(tester, '919876543001');
    expect(find.text('Play Memory Match'), findsOneWidget);

    await tester.tap(find.text('Play Memory Match'));
    await tester.pump(const Duration(seconds: 4));
    expect(find.text('Choose a Game'), findsOneWidget);

    // First content pack, Easy (2 pairs = 4 cards).
    await tester.tap(find.byType(ListTile).first);
    await tester.pump(const Duration(seconds: 4));
    expect(find.text('?'), findsNWidgets(4));

    // Brute-force the 2 pairs: flip first, then try others until matched.
    Finder cards() => find.text('?');
    for (var round = 0; round < 8; round++) {
      if (find.text('Game completed').evaluate().isNotEmpty) break;
      if (cards().evaluate().isEmpty) break;
      await tester.tap(cards().first);
      await tester.pump(const Duration(milliseconds: 400));
      if (cards().evaluate().length > 1) {
        await tester.tap(cards().at(1));
        await tester.pump(const Duration(milliseconds: 1200));
      }
      await tester.pump(const Duration(milliseconds: 400));
    }
    await tester.pump(const Duration(seconds: 2));
    expect(find.text('Game completed'), findsOneWidget);
    expect(find.textContaining('Accuracy'), findsOneWidget);
  });

  testWidgets('family caregiver dashboard hides patient switcher',
      (tester) async {
    await _loginAs(tester, '919876543002');
    await tester.pump(const Duration(seconds: 4));
    expect(find.textContaining('Caregiver Dashboard'), findsWidgets);
    expect(find.byType(DropdownButton<String>), findsNothing);
  });

  testWidgets('ASHA dashboard shows patient switcher', (tester) async {
    await _loginAs(tester, '9100000001');
    await tester.pump(const Duration(seconds: 4));
    expect(find.textContaining('Caregiver Dashboard'), findsWidgets);
    expect(find.byType(DropdownButton<String>), findsOneWidget);
  });
}
