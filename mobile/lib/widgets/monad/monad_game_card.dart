/// MonadGameCard — the ONLY card besides status chips allowed
/// [Monad.gameCardShadow]. 40px radius. Memory-match faces + routine cards.
/// Tint surfaces only (≤25% over parchment), always paired with icon + label.
library;

import 'package:flutter/material.dart';

import '../../theme/monad_theme.dart';

class MonadGameCard extends StatelessWidget {
  final Widget child;
  final Color? tint;
  final VoidCallback? onTap;
  final double? width;
  final double? height;

  const MonadGameCard(
      {super.key,
      required this.child,
      this.tint,
      this.onTap,
      this.width,
      this.height});

  @override
  Widget build(BuildContext context) {
    final card = Container(
      width: width,
      height: height,
      padding: const EdgeInsets.all(Monad.spacing24),
      decoration: BoxDecoration(
        color: tint ?? Monad.parchment,
        border: Border.all(color: Monad.ash, width: 1),
        borderRadius: BorderRadius.circular(Monad.radiusCard),
        boxShadow: Monad.gameCardShadow,
      ),
      child: child,
    );
    if (onTap == null) return card;
    return InkWell(
      borderRadius: BorderRadius.circular(Monad.radiusCard),
      onTap: onTap,
      child: card,
    );
  }
}
