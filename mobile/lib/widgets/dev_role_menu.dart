/// Dev-only role switcher for testing/demo.
///
/// Visible only with `--dart-define=DEV_MENU=true`. Lets testers jump
/// between the seeded patient, family caregiver, and ASHA accounts without
/// re-typing credentials — so the patient-vs-caregiver routing never needs
/// re-diagnosing. Never compiled into release builds' UI (flag is false
/// unless explicitly passed).
library;

import 'package:flutter/material.dart';

import '../services/auth_session.dart';

class DevRoleMenu extends StatelessWidget {
  static const enabled = bool.fromEnvironment('DEV_MENU');

  const DevRoleMenu({super.key});

  static const _accounts = [
    ('Patient', '919876543001'),
    ('Family caregiver', '919876543002'),
    ('ASHA worker', '9100000001'),
  ];

  @override
  Widget build(BuildContext context) {
    if (!enabled) return const SizedBox.shrink();
    return Drawer(
      child: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text('DEV — view as',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            for (final (label, phone) in _accounts)
              ListTile(
                title: Text(label),
                subtitle: Text(phone,
                    style: const TextStyle(fontFamily: 'monospace')),
                onTap: () async {
                  Navigator.of(context).pop();
                  await AuthSession.instance.logout();
                  await AuthSession.instance.login(
                      phone: phone, password: 'DemoPass123');
                },
              ),
          ],
        ),
      ),
    );
  }
}
