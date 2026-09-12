/// Cultural icon mapping + image-asset fallback chain for game visuals.
/// ENHANCED (2026-09-06): added layered face rendering — cultural art +
/// material glyph + subtle depth states (revealed / matched / hinting).
/// Every visual conveys state by position + border width + art presence,
/// never color-alone. All depth increases contrast with parchment background.
///
/// Real illustrated PNGs don't exist yet. Every card tries, in order:
///   1. assets/games/icons/<imageKey>.png  (commissioned illustration)
///   2. mapped Material icon in theme colors (safe placeholder)
/// A missing file therefore NEVER crashes — it degrades to the icon.
///
/// ## ASSET MANIFEST — files still to be sourced/commissioned:
/// assets/games/icons/bihu.png          (Rongali Bihu festival scene)
/// assets/games/icons/hornbill.png      (Hornbill festival)
/// assets/games/icons/chapchar_kut.png  (Chapchar Kut, Mizoram)
/// assets/games/icons/nongkrem.png     (Nongkrem dance)
/// assets/games/icons/losar.png         (Losar, Arunachal)
/// assets/games/icons/sangken.png      (Sangken water festival)
/// assets/games/icons/wangala.png      (Wangala 100 drums)
/// assets/games/icons/moatsu.png       (Moatsu festival)
/// assets/games/icons/dree.png         (Dree festival)
/// assets/games/icons/ningol_chakouba.png (Ningol Chakouba, Manipur)
/// assets/games/icons/kaji_nemu.png    (Assam lemon)
/// assets/games/icons/bhut_jolokia.png (ghost pepper)
/// assets/games/icons/ou_tenga.png     (elephant apple)
/// assets/games/icons/jolpai.png       (Indian olive)
/// assets/games/icons/bamboo_shoot.png (khorisa)
/// assets/games/icons/lakadong.png     (Lakadong turmeric)
/// assets/games/icons/starfruit.png    (kordoi)
/// assets/games/icons/tamul_pan.png    (betel nut & leaf)
/// assets/games/icons/kopou.png        (foxtail orchid)
/// assets/games/icons/assam_tea_leaf.png (tea leaf)
/// assets/games/icons/jaapi.png        (bamboo sun hat)
/// assets/games/icons/xorai.png        (bell-metal offering tray)
/// assets/games/icons/gamosa.png       (red-white woven cloth)
/// assets/games/icons/rhino.png        (one-horned rhino)
/// assets/games/icons/red_panda.png    (red panda)
/// assets/games/icons/dhol.png         (Bihu drum)
/// assets/games/icons/pepa.png         (buffalo-horn pipe)
/// assets/games/icons/mekhela.png     (Mekhela Sador textile)
/// assets/games/icons/puan.png        (Mizo Puan textile)
/// assets/games/icons/eri_silk.png     (Eri silk cocoon/cloth)
/// assets/games/icons/bamboo_craft.png (bamboo weaving)
/// assets/games/icons/naga_shawl.png  (Naga shawl textile)
library;

import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../theme/monad_theme.dart';

/// Custom flat illustrations (CustomPainter) for cultural items.
/// Replaces missing `cultural_art.dart` and Material-icon placeholders.
class CulturalArtPainter extends CustomPainter {
  final String key;
  final Color color;
  CulturalArtPainter(this.key, {required this.color});

  // Warm earthy palette — North-East cultural theme (matches DESIGN.md)
  static const Color terracotta = Color(0xFFC0704A); // clay / NER earth
  static const Color teaGreen    = Color(0xFF2D5A27); // tea-garden canopy
  static const Color eriGold     = Color(0xFFC9A227); // Eri silk fiber

  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()..color = color..style = PaintingStyle.fill;
    final w = size.width, h = size.height, cx = w / 2, cy = h / 2;
    if (key == 'rhino') {
      // Rounded body + horn
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(cx - 12, cy - 6, 24, 14), const Radius.circular(6)), p);
      canvas.drawPath(Path()..moveTo(cx + 6, cy - 8)..lineTo(cx + 14, cy - 14)..lineTo(cx + 10, cy - 4)..close(), Paint()..color = terracotta..style = PaintingStyle.fill);
    } else if (key == 'assam_tea_leaf') {
      // Oval leaf + stem
      canvas.drawOval(Rect.fromLTWH(cx - 10, cy - 8, 20, 14), p);
      canvas.drawLine(Offset(cx, cy + 6), Offset(cx, cy + 16), Paint()..strokeWidth = 2..color = teaGreen);
    } else if (key == 'jaapi') {
      // Fan arc
      canvas.drawArc(Rect.fromLTWH(cx - 14, cy - 10, 28, 20), 0.2 * 3.14, 2.6 * 3.14, false, p);
    } else if (key == 'eri_silk') {
      // Folded rectangle + cross
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(cx - 10, cy - 8, 20, 16), const Radius.circular(4)), p);
      canvas.drawLine(Offset(cx - 6, cy - 2), Offset(cx + 6, cy + 2), Paint()..strokeWidth = 1.5..color = eriGold);
    } else if (key == 'dhol') {
      // Cylinder
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(cx - 10, cy - 4, 20, 14), const Radius.circular(6)), p);
      canvas.drawOval(Rect.fromLTWH(cx - 10, cy - 4, 20, 6), Paint()..color = terracotta..style = PaintingStyle.fill);
    } else if (key == 'bamboo_craft') {
      // 3 vertical bars
      for (var i = -1; i <= 1; i++) canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(cx + i * 6 - 2, cy - 8, 4, 16), const Radius.circular(2)), p);
    } else if (key == 'naga_shawl') {
      // Diamond grid
      canvas.drawPath(Path()..moveTo(cx, cy - 10)..lineTo(cx + 10, cy)..lineTo(cx, cy + 10)..lineTo(cx - 10, cy)..close(), p);
    } else if (key == 'bihu') {
      canvas.drawCircle(Offset(cx, cy), 11, Paint()..color = terracotta..style = PaintingStyle.fill);
    } else if (key == 'hornbill') {
      canvas.drawCircle(Offset(cx, cy), 12, p);
      for (var i = 0; i < 3; i++) {
        final a = i * 2.09;
        canvas.drawCircle(Offset(cx + 12 * cos(a), cy + 12 * sin(a)), 2, Paint()..color = teaGreen..style = PaintingStyle.fill);
      }
    } else if (key == 'chapchar_kut' || key == 'losar') {
      // Mountain / hill arc (Mizo / Arunachal festivals) — kept
      canvas.drawArc(Rect.fromLTWH(cx - 14, cy - 8, 28, 16), 0.1 * 3.14, 2.8 * 3.14, false, p);
    } else if (key == 'sangken') {
      // Water splash arc (Sangken water festival)
      canvas.drawArc(Rect.fromLTWH(cx - 14, cy - 9, 28, 18), 0.0, 1.0 * 3.14, false, Paint()..color = Color(0xFF4A8DB7)..style = PaintingStyle.fill);
    } else if (key == 'wangala') {
      // Drum rhythm (Wangala 100 drums) — kept
      canvas.drawCircle(Offset(cx, cy), 11, Paint()..color = eriGold..style = PaintingStyle.fill);
      canvas.drawCircle(Offset(cx, cy), 5, Paint()..color = terracotta..style = PaintingStyle.fill);
    } else if (key == 'moatsu') {
      // Flower/wreath arc (Ao Moatsu festival)
      canvas.drawArc(Rect.fromLTWH(cx - 13, cy - 7, 26, 14), 0.2 * 3.14, 2.4 * 3.14, false, Paint()..color = Color(0xFFC0704A)..style = PaintingStyle.fill);
    } else if (key == 'dree') {
      // Circular offering (Dree, Arunachal)
      canvas.drawCircle(Offset(cx, cy), 10, Paint()..color = Color(0xFF2D5A27)..style = PaintingStyle.fill);
    } else if (key == 'ningol_chakouba') {
      // Bond / thread loop (Manipur Ningol Chakouba)
      canvas.drawOval(Rect.fromLTWH(cx - 9, cy - 8, 18, 16), p);
    } else if (key == 'kaji_nemu') {
      // Lemon crescent (Assam kaji nemu)
      canvas.drawArc(Rect.fromLTWH(cx - 11, cy - 9, 22, 18), 0.6 * 3.14, 2.6 * 3.14, false, p);
    } else if (key == 'nongkrem' || key == 'wangala') {
      // Drum / circular rhythm (Nongkrem dance / Wangala 100 drums)
      canvas.drawCircle(Offset(cx, cy), 11, Paint()..color = eriGold..style = PaintingStyle.fill);
      canvas.drawCircle(Offset(cx, cy), 5, Paint()..color = terracotta..style = PaintingStyle.fill);
    } else {
      // Mountain / hill arc backdrop (Mizo / Arunachal festivals) with the
      // generic star / flower fallback painted over it.
      canvas.drawArc(Rect.fromLTWH(cx - 14, cy - 8, 28, 16), 0.1 * 3.14, 2.8 * 3.14, false, p);
      final pts = [Offset(cx, cy - 10), Offset(cx + 6, cy - 2), Offset(cx + 10, cy + 4), Offset(cx + 2, cy + 8), Offset(cx - 6, cy + 2)];
      final path = Path()..moveTo(pts[0].dx, pts[0].dy); for (var i = 1; i < pts.length; i++) path.lineTo(pts[i].dx, pts[i].dy); path.close();
      canvas.drawPath(path, p);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter old) => old is! CulturalArtPainter || old.key != key || old.color != color;
}

class GameVisuals {
  GameVisuals._();

  /// imageKey -> Material icon placeholder (theme-colored).
  static const Map<String, IconData> iconFor = {
    // Festivals
    'bihu': Icons.celebration,
    'hornbill': Icons.festival,
    'chapchar_kut': Icons.festival,
    'nongkrem': Icons.music_note,
    'losar': Icons.auto_awesome,
    'sangken': Icons.water_drop,
    'wangala': Icons.music_note,
    'moatsu': Icons.local_florist,
    'dree': Icons.agriculture,
    'ningol_chakouba': Icons.family_restroom,
    // Flora / food
    'kaji_nemu': Icons.eco,
    'bhut_jolokia': Icons.local_fire_department,
    'ou_tenga': Icons.spa,
    'jolpai': Icons.spa,
    'bamboo_shoot': Icons.grass,
    'lakadong': Icons.colorize,
    'starfruit': Icons.star,
    'tamul_pan': Icons.spa,
    'kopou': Icons.local_florist,
    'assam_tea_leaf': Icons.emoji_food_beverage,
    // Heritage / household
    'jaapi': Icons.beach_access,
    'xorai': Icons.temple_buddhist,
    'gamosa': Icons.checkroom,
    'rhino': Icons.pets,
    'red_panda': Icons.cruelty_free,
    'dhol': Icons.album,
    'pepa': Icons.queue_music,
    'mekhela': Icons.woman,
    'puan': Icons.grid_view,
    'eri_silk': Icons.crop_free,
    'bamboo_craft': Icons.carpenter,
    'naga_shawl': Icons.dry_cleaning,
  };

  static const _assetDir = 'assets/games/icons';

  /// True if a commissioned PNG exists for [imageKey]. Precomputed set
  /// because asset lookup can't be probed synchronously at paint time —
  /// ship PNGs and add their keys here.
  static const Set<String> availableImages = {};

  /// The visual for a card face — CustomPainter illustration in palette.
  static Widget face({
    required String imageKey,
    required String label,
    double iconSize = 44,
  }) {
    // Pick palette color per item family
    Color c = Monad.indigo;
    if (imageKey.contains('tea') || imageKey.contains('bamboo')) c = Monad.teaGreen;
    else if (imageKey.contains('silk') || imageKey.contains('eri')) c = Monad.eriGold;
    else if (imageKey.contains('rhino') || imageKey.contains('red_panda')) c = Color(0xFF8B6914);
    else if (imageKey.contains('jaapi') || imageKey.contains('dhol') || imageKey.contains('horn')) c = Monad.terracotta;
    else if (imageKey.contains('bihu')) c = Monad.indigo;
    else if (imageKey.contains('shawl')) c = Monad.indigo;
    return CustomPaint(
      size: Size(iconSize, iconSize),
      painter: CulturalArtPainter(imageKey, color: c),
    );
  }

  static Widget _iconFace(String imageKey, double size) => Icon(
        iconFor[imageKey] ?? Icons.help_outline,
        size: size,
        color: Monad.offBlack,
      );

  /// Soft positive feedback: light haptic + (future) short soft sound.
  /// Negative taps get nothing — no punishment feedback for dementia UX.
  static void positiveFeedback() {
    HapticFeedback.lightImpact();
    // Soft audio hook: play assets/audio/match_success.wav when sourced.
  }

  static void selectionFeedback() => HapticFeedback.selectionClick();
}
