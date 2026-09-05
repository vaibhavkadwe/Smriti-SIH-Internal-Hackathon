/// ElderCare Companion — patient mobile app (plus caregiver dashboard view).
///
/// Entry flow:
///   restore session -> AuthGate -> Login/Register
///                     -> HomeShell (role-aware) -> games / routine /
///                        reminders / voice companion / caregiver dashboard
library;

import 'package:flutter/material.dart';

import 'models/shared_models.dart';
import 'screens/caregiver_dashboard_screen.dart';
import 'screens/pack_picker_screen.dart';
import 'screens/reminders_screen.dart';
import 'screens/routine_screen.dart';
import 'screens/voice_companion_screen.dart';
import 'services/api_service.dart';
import 'services/auth_session.dart';
import 'services/offline_sync_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  AuthSession.instance.restore();
  runApp(const ElderCareApp());
}

class ElderCareApp extends StatelessWidget {
  const ElderCareApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ElderCare Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1B6B4A), // NER deep green
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        // High-contrast, large text for elderly users
        textTheme: const TextTheme(
          displayLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
          bodyLarge: TextStyle(fontSize: 20),
          labelLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
        ),
      ),
      home: const _AuthGate(),
    );
  }
}

class _AuthGate extends StatelessWidget {
  const _AuthGate();

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: AuthSession.instance,
      builder: (context, _) {
        switch (AuthSession.instance.status) {
          case AuthStatus.restoring:
            return const Scaffold(body: Center(child: CircularProgressIndicator()));
          case AuthStatus.unauthenticated:
            return const AuthScreen();
          case AuthStatus.authenticated:
            return const HomeShell();
        }
      },
    );
  }
}

// =====================================================================
// Auth (login / register)
// =====================================================================

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phone = TextEditingController();
  final _password = TextEditingController();
  final _name = TextEditingController();

  bool _registering = false;
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _phone.dispose();
    _password.dispose();
    _name.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      if (_registering) {
        await AuthSession.instance.register(
          phone: _phone.text.trim(),
          password: _password.text,
          name: _name.text.trim(),
        );
      } else {
        await AuthSession.instance.login(
          phone: _phone.text.trim(),
          password: _password.text,
        );
      }
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } on Exception catch (e) {
      if (mounted) setState(() => _error = 'Connection problem: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(Icons.volunteer_activism, size: 72, color: Colors.teal.shade400),
                  const SizedBox(height: 8),
                  Text(
                    'ElderCare Companion',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.displayLarge,
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'স্বাস্থ্য আৰু মনৰ চৰ্চা (Health & Mind Care)',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 16, color: Colors.grey),
                  ),
                  const SizedBox(height: 28),
                  if (_registering) ...[
                    TextFormField(
                      controller: _name,
                      style: const TextStyle(fontSize: 18),
                      decoration: const InputDecoration(labelText: 'Your name', border: OutlineInputBorder()),
                      validator: (v) => (v == null || v.trim().isEmpty) ? 'Name is required' : null,
                    ),
                    const SizedBox(height: 14),
                  ],
                  TextFormField(
                    controller: _phone,
                    keyboardType: TextInputType.phone,
                    style: const TextStyle(fontSize: 18),
                    decoration: const InputDecoration(labelText: 'Phone number', border: OutlineInputBorder()),
                    validator: (v) => (v == null || v.trim().length < 6) ? 'Enter a valid phone number' : null,
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _password,
                    obscureText: true,
                    style: const TextStyle(fontSize: 18),
                    decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
                    validator: (v) => (v == null || v.length < 6) ? 'At least 6 characters' : null,
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(_error!, textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.red, fontSize: 15)),
                  ],
                  const SizedBox(height: 22),
                  FilledButton(
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 18),
                      textStyle: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    onPressed: _busy ? null : _submit,
                    child: _busy
                        ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2))
                        : Text(_registering ? 'Create Account' : 'Sign In'),
                  ),
                  TextButton(
                    onPressed: _busy ? null : () => setState(() => _registering = !_registering),
                    child: Text(
                      _registering
                          ? 'Already have an account? Sign in'
                          : 'New patient? Register here',
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// =====================================================================
// Home shell — role-aware feature hub
// =====================================================================

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  final ApiService _api = ApiService.instance;

  String? _patientId;
  bool _resolvingProfile = true;

  @override
  void initState() {
    super.initState();
    OfflineSyncService.instance.start();
    OfflineSyncService.instance.syncNow();
    _resolveIdentity();
  }

  Future<void> _resolveIdentity() async {
    final user = AuthSession.instance.user;
    if (user != null && user.role == Role.patient) {
      try {
        final profile = await _api.myPatient();
        if (mounted) setState(() => _patientId = profile?.id);
      } on Exception catch (e) {
        debugPrint('Could not resolve patient profile: $e');
      }
    }
    if (mounted) setState(() => _resolvingProfile = false);
  }

  @override
  Widget build(BuildContext context) {
    final user = AuthSession.instance.user;
    final isStaff = user != null && user.role != Role.patient;

    if (_resolvingProfile) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    // Staff see the caregiver dashboard surface.
    if (isStaff) {
      return CaregiverDashboardScreen(caregiverId: user.id);
    }

    // Patient without a profile yet: prompt to create one.
    if (_patientId == null) {
      return _ProfileSetup(onCreated: (id) => setState(() => _patientId = id));
    }

    return _PatientHome(patientId: _patientId!);
  }
}

class _ProfileSetup extends StatefulWidget {
  final ValueChanged<String> onCreated;
  const _ProfileSetup({required this.onCreated});

  @override
  State<_ProfileSetup> createState() => _ProfileSetupState();
}

class _ProfileSetupState extends State<_ProfileSetup> {
  final _name = TextEditingController();
  bool _busy = false;

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  Future<void> _create() async {
    final name = _name.text.trim();
    if (name.isEmpty || _busy) return;
    setState(() => _busy = true);
    try {
      final patient = await ApiService.instance.createMyPatient(name: name);
      await ApiService.instance.grantConsent(patientId: patient.id);
      if (mounted) widget.onCreated(patient.id);
    } on Exception catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not create profile: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome!'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.face_retouching_natural, size: 80, color: Colors.teal),
            const SizedBox(height: 16),
            const Text('Tell us your name to get started', style: TextStyle(fontSize: 22)),
            const SizedBox(height: 20),
            TextField(
              controller: _name,
              style: const TextStyle(fontSize: 20),
              decoration: const InputDecoration(border: OutlineInputBorder(), labelText: 'Your name'),
            ),
            const SizedBox(height: 24),
            FilledButton(
              style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 40)),
              onPressed: _busy ? null : _create,
              child: const Text('Continue', style: TextStyle(fontSize: 20)),
            ),
          ],
        ),
      ),
    );
  }
}

class _PatientHome extends StatelessWidget {
  final String patientId;
  const _PatientHome({required this.patientId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ElderCare Companion'),
        centerTitle: true,
        actions: [
          IconButton(
            tooltip: 'Sign out',
            icon: const Icon(Icons.logout),
            onPressed: () => AuthSession.instance.logout(),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _homeButton(
            context,
            icon: Icons.extension,
            title: 'Play Memory Match',
            subtitle: 'Train your memory with NER themes',
            color: Colors.teal,
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute<void>(builder: (_) => const PackPickerScreen()),
            ),
          ),
          _homeButton(
            context,
            icon: Icons.event_note,
            title: 'Daily Routine Game',
            subtitle: 'Sequence your daily activities',
            color: Colors.indigo,
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => RoutineScreen(
                  patientId: patientId,
                  difficultyLevel: 1,
                  languageCode: AuthSession.instance.user?.preferredLanguage ?? 'english',
                ),
              ),
            ),
          ),
          _homeButton(
            context,
            icon: Icons.alarm,
            title: 'Reminders',
            subtitle: 'Medicine, water, food & exercise',
            color: Colors.orange,
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => RemindersScreen(patientId: patientId),
              ),
            ),
          ),
          _homeButton(
            context,
            icon: Icons.record_voice_over,
            title: 'Talk to Aai Companion',
            subtitle: 'A warm voice to talk with',
            color: Colors.pink,
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => VoiceCompanionScreen(patientId: patientId),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _homeButton(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 3,
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      child: ListTile(
        contentPadding: const EdgeInsets.all(18),
        minVerticalPadding: 12,
        leading: CircleAvatar(
          radius: 30,
          backgroundColor: color.withValues(alpha: 0.15),
          child: Icon(icon, color: color, size: 32),
        ),
        title: Text(title, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle, style: const TextStyle(fontSize: 15)),
        trailing: const Icon(Icons.chevron_right, size: 34),
        onTap: onTap,
      ),
    );
  }
}
