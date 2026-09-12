/// MonadFeatureCard — default card everywhere.
/// Parchment fill, 1px ash border, 40px radius, 40px padding, optional 20px
/// mono icon top-left, serif 24 title, mono 16 body. NO shadow.
library;

import 'package:flutter/material.dart';

import '../../theme/monad_theme.dart';

class MonadFeatureCard extends StatelessWidget {
  final String title;
  final String body;
  final IconData? icon;
  final Widget? trailing;

  const MonadFeatureCard(
      {super.key, required this.title, required this.body, this.icon, this.trailing});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Monad.cardPadding),
      decoration: BoxDecoration(
        color: Monad.parchment,
        border: Border.all(color: Monad.ash, width: 1),
        borderRadius: BorderRadius.circular(Monad.radiusCard),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null)
            Padding(
              padding: const EdgeInsets.only(bottom: Monad.spacing16),
              child: Icon(icon, size: 20, color: Monad.offBlack),
            ),
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
