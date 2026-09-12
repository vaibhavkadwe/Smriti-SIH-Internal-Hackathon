// Smoke test: with no persisted session the app shows the login screen.
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:eldercare_dashboard/main.dart';

void main() {
  testWidgets('shows login screen when no session is persisted', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const CaregiverDashboardApp());
    await tester.pumpAndSettle();

    expect(find.text('Caregiver Dashboard'), findsOneWidget);
    // MonadPillButton uppercases + appends the ▸ primary-action glyph.
    expect(find.text('SIGN IN ▸'), findsOneWidget);
  });
}
