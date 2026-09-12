/// MonadPillTag — pipeline node tag.
/// Parchment fill, 1px ash border, StadiumBorder, 12/20 padding, optional
/// 12px icon + 14px mono uppercase text.
library;

import 'package:flutter/material.dart';

import '../../theme/monad_theme.dart';

class MonadPillTag extends StatelessWidget {
  final String label;
  final IconData? icon;

  const MonadPillTag({super.key, required this.label, this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: const ShapeDecoration(
        color: Monad.parchment,
        shape: StadiumBorder(side: BorderSide(color: Monad.ash, width: 1)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 12, color: Monad.offBlack),
            const SizedBox(width: 8),
          ],
          Text(
            label.toUpperCase(),
            style: Monad.monoBodySm.copyWith(color: Monad.offBlack),
          ),
        ],
      ),
    );
  }
}
