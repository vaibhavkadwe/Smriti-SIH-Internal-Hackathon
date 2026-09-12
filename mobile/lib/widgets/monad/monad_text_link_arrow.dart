/// MonadTextLinkArrow — transparent link with trailing "→".
/// OffBlack mono 14px, uppercase tracking, no background/border.
library;

import 'package:flutter/material.dart';

import '../../theme/monad_theme.dart';

class MonadTextLinkArrow extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;

  const MonadTextLinkArrow({super.key, required this.label, this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Text(
        '${label.toUpperCase()} →',
        style: Monad.monoBodySm.copyWith(
            color: Monad.offBlack,
            fontWeight: FontWeight.w400,
            letterSpacing: -0.28),
      ),
    );
  }
}
