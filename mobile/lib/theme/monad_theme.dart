/// Monad design-system tokens for Flutter — mirrors DESIGN.md exactly.
/// Newsreader substitutes Untitled Serif; JetBrains Mono substitutes ABC
/// Diatype Mono (both per DESIGN.md's listed substitutes).
library;

import 'package:flutter/material.dart';

class Monad {
  Monad._();

  // ===== Colors (DESIGN.md Tokens — Colors) =====
  static const Color parchment = Color(0xFFF6F3F1);
  static const Color lakeBlue = Color(0xFF2B59D1);
  static const Color periwinkleMist = Color(0xFFCFDAF5);
  static const Color skyBlue = Color(0xFFA0B5EB);
  static const Color mint = Color(0xFFA7FCCD);
  static const Color coral = Color(0xFFFF9473);
  static const Color gold = Color(0xFFECDA98);
  static const Color crimson = Color(0xFFF37A0A);
  static const Color offBlack = Color(0xFF242424);
  static const Color ink = Color(0xFF000000);
  static const Color graphite = Color(0xFF4E4D4D);
  static const Color smoke = Color(0xFF797776);
  static const Color ash = Color(0xFFCECAC8);
  static const Color white = Color(0xFFFFFFFF);

  // ===== Font families =====
  static const String serifFamily = 'Newsreader'; // Untitled Serif substitute
  static const String monoFamily = 'JetBrainsMono'; // ABC Diatype Mono substitute

  // ===== Spacing (DESIGN.md, 8px base) =====
  static const double spacing8 = 8;
  static const double spacing16 = 16;
  static const double spacing24 = 24;
  static const double spacing32 = 32;
  static const double spacing40 = 40;
  static const double spacing64 = 64;

  // ===== Radii =====
  static const double radiusButton = 100; // pill buttons
  static const double radiusCard = 40; // cards
  static const double radiusPill = 9999; // tags / pills
  static const double radiusMin = 16; // smallest allowed card radius

  // ===== Layout =====
  static const double pageMaxWidth = 1432;
  static const double cardPadding = 40;
  static const double elementGap = 16;

  // ===== Serif display text (weight locked at 400) =====
  static const TextStyle display = TextStyle(
      fontFamily: serifFamily, fontWeight: FontWeight.w400, height: 1.2, color: offBlack, letterSpacing: -1.6);
  static const TextStyle headingLg = TextStyle(
      fontFamily: serifFamily, fontWeight: FontWeight.w400, height: 1.2, color: offBlack, fontSize: 48, letterSpacing: -0.96);
  static const TextStyle heading = TextStyle(
      fontFamily: serifFamily, fontWeight: FontWeight.w400, height: 1.2, color: offBlack, fontSize: 40, letterSpacing: -0.8);
  static const TextStyle headingSm = TextStyle(
      fontFamily: serifFamily, fontWeight: FontWeight.w400, height: 1.2, color: offBlack, fontSize: 32, letterSpacing: -0.64);
  static const TextStyle subheading = TextStyle(
      fontFamily: serifFamily, fontWeight: FontWeight.w400, height: 1.2, color: offBlack, fontSize: 24, letterSpacing: -0.48);

  // ===== Mono UI text =====
  static const TextStyle monoCaption = TextStyle(
      fontFamily: monoFamily, fontSize: 12, height: 1.2, letterSpacing: -0.4, color: smoke);
  static const TextStyle monoBodySm = TextStyle(
      fontFamily: monoFamily, fontSize: 14, height: 1.35, letterSpacing: -0.28, color: graphite);
  static const TextStyle monoBody = TextStyle(
      fontFamily: monoFamily, fontSize: 16, height: 1.35, letterSpacing: -0.4, color: graphite);
  static const TextStyle monoLabel = TextStyle(
      fontFamily: monoFamily, fontSize: 18, height: 1.2, letterSpacing: -0.4, color: offBlack);
  static const TextStyle monoBodyLg = TextStyle(
      fontFamily: monoFamily, fontSize: 20, height: 1.35, letterSpacing: -0.4, color: graphite);

  /// Uppercase mono label for buttons / nav / tags.
  static const TextStyle monoButtonLabel = TextStyle(
      fontFamily: monoFamily, fontSize: 14, height: 1.0, letterSpacing: -0.02, color: white);

  // ===== Widget specs =====

  /// Pill button (100px radius, 48px min height, mono 14 uppercase).
  static ButtonStyle bluePill() => _pill(foreground: white, background: lakeBlue);
  static ButtonStyle blackPill() => _pill(foreground: white, background: offBlack);
  static ButtonStyle ghostPill() => _pill(
      foreground: offBlack, background: Colors.transparent, border: offBlack);

  static ButtonStyle _pill(
      {required Color foreground, required Color background, Color? border}) {
    return ButtonStyle(
      foregroundColor: WidgetStatePropertyAll(foreground),
      backgroundColor: WidgetStatePropertyAll(background),
      overlayColor: WidgetStatePropertyAll(foreground.withValues(alpha: 0.08)),
      minimumSize: const WidgetStatePropertyAll(Size(64, 48)),
      padding: const WidgetStatePropertyAll(
          EdgeInsets.symmetric(horizontal: 32, vertical: 16)),
      shape: WidgetStatePropertyAll(RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusButton),
          side: border != null ? BorderSide(color: border) : BorderSide.none)),
      textStyle: const WidgetStatePropertyAll(monoButtonLabel),
    );
  }

  /// Card shape: 40px radius, 1px ash hairline, no elevation.
  static RoundedRectangleBorder get cardShape =>
      RoundedRectangleBorder(borderRadius: BorderRadius.circular(radiusCard), side: const BorderSide(color: ash, width: 1));

  static RoundedRectangleBorder get softShape =>
      RoundedRectangleBorder(borderRadius: BorderRadius.circular(radiusMin), side: const BorderSide(color: ash, width: 1));

  // ===== Elder-care game extension (see DESIGN.md amendment) =====
  // Pastel face tints: illustration surfaces only, always paired with
  // distinct art + text label (never color-alone). All exceed 10:1 with
  // Off-Black text/icons on Parchment.
  static const double _faceTintOpacity = 0.22;
  static Color get tintCoral => Color.lerp(parchment, coral, _faceTintOpacity)!;
  static Color get tintSky => Color.lerp(parchment, skyBlue, _faceTintOpacity)!;
  static Color get tintMint => Color.lerp(parchment, mint, _faceTintOpacity)!;
  static Color get tintGold => Color.lerp(parchment, gold, _faceTintOpacity)!;

  // Stable order for cycling tints across cards.
  static List<Color> get faceTints => [tintMint, tintSky, tintCoral, tintGold];

  /// Reminder type color (icon + label + tint together; never color-alone).
  static Color reminderColor(String type) {
    switch (type.toLowerCase()) {
      case 'medicine':
        return lakeBlue;
      case 'water':
        return skyBlue;
      case 'food':
        return gold;
      case 'exercise':
        return mint;
      default:
        return graphite;
    }
  }

  /// Ambient shadow, permitted on game card faces and status chips only.
  static const List<BoxShadow> cardShadow = [
    BoxShadow(color: Color(0x1A000000), blurRadius: 10, offset: Offset.zero),
  ];

  /// Patient-facing body floor: 20px (DESIGN.md --text-body-lg).
  static TextStyle get patientBody => monoBodyLg.copyWith(color: offBlack);

  /// ThemeData for the whole app.
  static ThemeData theme() {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.light(
        primary: lakeBlue,
        onPrimary: white,
        secondary: offBlack,
        onSecondary: white,
        surface: parchment,
        onSurface: offBlack,
        surfaceContainerHighest: periwinkleMist,
        onSurfaceVariant: graphite,
        outline: ash,
        error: crimson,
        onError: white,
      ),
      scaffoldBackgroundColor: parchment,
    );
    return base.copyWith(
      textTheme: base.textTheme.copyWith(
        displayLarge: display.copyWith(fontSize: 80),
        displayMedium: headingLg,
        displaySmall: heading,
        headlineLarge: headingLg,
        headlineMedium: heading,
        headlineSmall: headingSm,
        titleLarge: subheading,
        titleMedium: subheading.copyWith(fontSize: 24),
        titleSmall: monoBody.copyWith(color: offBlack),
        bodyLarge: monoBodyLg,
        bodyMedium: monoBody,
        bodySmall: monoBodySm,
        labelLarge: monoLabel,
        labelMedium: monoBodySm.copyWith(color: offBlack),
        labelSmall: monoCaption,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: parchment,
        foregroundColor: offBlack,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
            fontFamily: serifFamily, fontWeight: FontWeight.w400, fontSize: 32, color: offBlack, letterSpacing: -0.64),
      ),
      dividerTheme: const DividerThemeData(color: ash, thickness: 1, space: 1),
      cardTheme: CardThemeData(
        color: parchment,
        elevation: 0,
        shape: cardShape,
        margin: EdgeInsets.zero,
        clipBehavior: Clip.antiAlias,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: parchment,
        border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(radiusMin), borderSide: const BorderSide(color: ash)),
        enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(radiusMin), borderSide: const BorderSide(color: ash)),
        focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(radiusMin), borderSide: const BorderSide(color: lakeBlue, width: 1)),
        labelStyle: monoCaption,
        hintStyle: monoCaption,
        contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      ),
      filledButtonTheme: FilledButtonThemeData(style: bluePill()),
      elevatedButtonTheme: ElevatedButtonThemeData(style: blackPill()),
      outlinedButtonTheme: OutlinedButtonThemeData(style: ghostPill()),
      textButtonTheme: TextButtonThemeData(
        style: ButtonStyle(
          foregroundColor: const WidgetStatePropertyAll(offBlack),
          textStyle: const WidgetStatePropertyAll(
              TextStyle(fontFamily: monoFamily, fontSize: 14, letterSpacing: -0.02)),
        ),
      ),
      dropdownMenuTheme: DropdownMenuThemeData(
        textStyle: monoBody.copyWith(color: offBlack),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: parchment,
          border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(radiusMin), borderSide: const BorderSide(color: ash)),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: offBlack,
        contentTextStyle: monoBody.copyWith(color: parchment),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(radiusMin)),
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(color: lakeBlue),
    );
  }
}
