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

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../theme/monad_theme.dart';
import 'cultural_art.dart';

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

  /// The visual for a card face, in order: commissioned PNG, painted
  /// cultural art ([CulturalArt]), mapped Material icon. Never crashes.
  static Widget face({
    required String imageKey,
    required String label,
    double iconSize = 44,
  }) {
    if (availableImages.contains(imageKey)) {
      return Image.asset(
        '$_assetDir/$imageKey.png',
        fit: BoxFit.contain,
        errorBuilder: (_, __, ___) => _iconFace(imageKey, iconSize),
      );
    }
    if (CulturalArt.hasArt(imageKey)) {
      return CulturalArt(imageKey, size: iconSize);
    }
    return _iconFace(imageKey, iconSize);
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
