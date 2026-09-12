/// MonadElevatedCard — the ONLY widget allowed a non-parchment surface fill.
/// Periwinkle mist fill, 40px radius, 40px padding, serif 24 title, mono 16
/// body. Use sparingly — one hero-style card per screen.
library;

import 'package:flutter/material.dart';

import '../../theme/monad_theme.dart';

class MonadElevatedCard extends StatelessWidget {
  final String title;
  final String body;
  final Widget? trailing;

  const MonadElevatedCard(
      {super.key, required this.title, required this.body, this.trailing});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Monad.cardPadding),
      decoration: BoxDecoration(
        color: Monad.periwinkleMist,
        borderRadius: BorderRadius.circular(Monad.radiusCard),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(title, style: Monad.subheading),
          const SizedBox(height: Monad.spacing16),
          Text(body, style: Monad.monoBody),
          if (trailing != null) ...[
            const SizedBox(height: Monad.spacing16),
            trailing!,
          ],
        ],
      ),
    );
  }
}
