/// MonadFAQRow — full width, 40px vertical padding, 1px ash BOTTOM border
/// only, serif 24 question, trailing "↓" 20px right-aligned. No hover/fill.
library;

import 'package:flutter/material.dart';

import '../../theme/monad_theme.dart';

class MonadFAQRow extends StatelessWidget {
  final String question;
  final String? answer;
  final bool expanded;
  final VoidCallback? onTap;

  const MonadFAQRow(
      {super.key,
      required this.question,
      this.answer,
      this.expanded = false,
      this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 40),
        decoration: const BoxDecoration(
          border: Border(bottom: BorderSide(color: Monad.ash, width: 1)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(question, style: Monad.subheading)),
                const Text('↓',
                    style: TextStyle(
                        fontSize: 20, color: Monad.offBlack, height: 1.0)),
              ],
            ),
            if (expanded && answer != null) ...[
              const SizedBox(height: Monad.spacing16),
              Text(answer!, style: Monad.monoBody),
            ],
          ],
        ),
      ),
    );
  }
}
