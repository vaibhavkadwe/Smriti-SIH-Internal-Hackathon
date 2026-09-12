/// Smoke tests for the Monad widget kit — verify each widget renders with
/// its DESIGN.md spec (fill, border, radius, type) so screens can rely on
/// them without visual inspection.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:eldercare_mobile/theme/monad_theme.dart';
import 'package:eldercare_mobile/widgets/monad/monad_pill_button.dart';
import 'package:eldercare_mobile/widgets/monad/monad_pill_tag.dart';
import 'package:eldercare_mobile/widgets/monad/monad_feature_card.dart';
import 'package:eldercare_mobile/widgets/monad/monad_elevated_card.dart';
import 'package:eldercare_mobile/widgets/monad/monad_game_card.dart';

void main() {
  group('Monad widget kit', () {
    testWidgets('MonadPillButton primary renders lakeBlue with ▸', (tester) async {
      await tester.pumpWidget(MaterialApp(
        theme: Monad.theme(),
        home: Scaffold(
          body: MonadPillButton(label: 'Sign In', onPressed: () {}),
        ),
      ));
      expect(find.text('SIGN IN ▸'), findsOneWidget);
      final fill = tester.widget<FilledButton>(find.byType(FilledButton));
      expect(fill.style?.backgroundColor?.resolve({}), equals(Monad.lakeBlue));
    });

    testWidgets('MonadPillButton secondary is offBlack, no arrow', (tester) async {
      await tester.pumpWidget(MaterialApp(
        theme: Monad.theme(),
        home: Scaffold(
          body: MonadPillButton(
              label: 'Save', variant: MonadPillVariant.secondary, onPressed: () {}),
        ),
      ));
      expect(find.text('SAVE'), findsOneWidget);
      final fill = tester.widget<FilledButton>(find.byType(FilledButton));
      expect(fill.style?.backgroundColor?.resolve({}), equals(Monad.offBlack));
    });

    testWidgets('MonadPillTag renders stadium, parchment, ash border', (tester) async {
      await tester.pumpWidget(MaterialApp(
        theme: Monad.theme(),
        home: const Scaffold(body: MonadPillTag(label: 'medicine', icon: Icons.medication)),
      ));
      expect(find.text('MEDICINE'), findsOneWidget);
      final container = tester.widget<Container>(find.descendant(
          of: find.byType(MonadPillTag), matching: find.byType(Container)));
      final decoration = container.decoration as ShapeDecoration;
      expect(decoration.shape, isA<StadiumBorder>());
      expect(decoration.color, equals(Monad.parchment));
    });

    testWidgets('MonadFeatureCard renders parchment + ash hairline, no shadow', (tester) async {
      await tester.pumpWidget(MaterialApp(
        theme: Monad.theme(),
        home: const Scaffold(
          body: MonadFeatureCard(title: 'Reminders', body: 'Medicine at 8', icon: Icons.alarm),
        ),
      ));
      expect(find.text('Reminders'), findsOneWidget);
      expect(find.text('Medicine at 8'), findsOneWidget);
      final container = tester.widget<Container>(find.descendant(
          of: find.byType(MonadFeatureCard), matching: find.byType(Container)));
      final deco = container.decoration as BoxDecoration;
      expect(deco.color, equals(Monad.parchment));
      expect(deco.border?.top.color, equals(Monad.ash));
      expect(deco.boxShadow, isNull);
    });

    testWidgets('MonadElevatedCard is the one periwinkle surface', (tester) async {
      await tester.pumpWidget(MaterialApp(
        theme: Monad.theme(),
        home: const Scaffold(
          body: MonadElevatedCard(title: 'Today', body: 'Everything acknowledged'),
        ),
      ));
      final container = tester.widget<Container>(find.descendant(
          of: find.byType(MonadElevatedCard), matching: find.byType(Container)));
      final deco = container.decoration as BoxDecoration;
      expect(deco.color, equals(Monad.periwinkleMist));
      expect(deco.boxShadow, isNull);
    });

    testWidgets('MonadGameCard is the only card with shadow', (tester) async {
      await tester.pumpWidget(MaterialApp(
        theme: Monad.theme(),
        home: const Scaffold(
          body: MonadGameCard(child: SizedBox(width: 80, height: 80)),
        ),
      ));
      final container = tester.widget<Container>(find.descendant(
          of: find.byType(MonadGameCard), matching: find.byType(Container)));
      final deco = container.decoration as BoxDecoration;
      expect(deco.boxShadow, isNotNull);
      expect(deco.boxShadow!.first.blurRadius, equals(10));
      expect(deco.boxShadow!.first.offset, equals(const Offset(0, 0)));
    });

    testWidgets('theme scaffold is parchment, never white', (tester) async {
      final theme = Monad.theme();
      // Screens set no explicit background — the global theme must be the
      // parchment canvas (DESIGN.md: never pure white).
      expect(theme.scaffoldBackgroundColor, equals(Monad.parchment));
      await tester.pumpWidget(MaterialApp(
        theme: theme,
        home: const Scaffold(body: SizedBox()),
      ));
      await tester.pump();
      // Scaffold falls back to the theme color when backgroundColor is null.
      expect(tester.widget<Scaffold>(find.byType(Scaffold)).backgroundColor,
          anyOf(isNull, Monad.parchment));
    });
  });
}
