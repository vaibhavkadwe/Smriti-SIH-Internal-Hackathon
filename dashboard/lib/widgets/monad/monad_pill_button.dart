/// MonadPillButton — primary / secondary / ghost.
///
/// Primary (lakeBlue, trailing "▸") is the single primary action per screen
/// (hard rule from DESIGN.md Do's/Don'ts). Secondary is offBlack, ghost is
/// transparent with a 1px offBlack border. All: mono 14 uppercase, 100px
/// radius, 16/32 padding, min height 48.
library;

import 'package:flutter/material.dart';

import '../../theme/monad_theme.dart';

enum MonadPillVariant { primary, secondary, ghost }

class MonadPillButton extends StatelessWidget {
  final String label;
  final MonadPillVariant variant;
  final VoidCallback? onPressed;
  final bool expanded;

  final bool busy;

  const MonadPillButton(
      {super.key,
      required this.label,
      this.variant = MonadPillVariant.primary,
      this.onPressed,
      this.expanded = false,
      this.busy = false});

  @override
  Widget build(BuildContext context) {
    final upper = label.toUpperCase();
    final suffix = variant == MonadPillVariant.primary ? ' ▸' : '';
    final style = switch (variant) {
      MonadPillVariant.primary => Monad.bluePill(),
      MonadPillVariant.secondary => Monad.blackPill(),
      MonadPillVariant.ghost => Monad.ghostPill(),
    };
    final button = FilledButton(
      onPressed: busy ? null : onPressed,
      style: style,
      child: busy
          ? SizedBox(
              width: 22,
              height: 22,
              child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: variant == MonadPillVariant.ghost
                      ? Monad.offBlack
                      : Monad.white))
          : Text('$upper$suffix', style: Monad.monoButtonLabel),
    );
    if (!expanded) return button;
    return SizedBox(width: double.infinity, child: button);
  }
}
