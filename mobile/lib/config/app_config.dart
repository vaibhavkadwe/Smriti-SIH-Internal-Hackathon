/// App-wide configuration for the patient mobile app.
///
/// The backend base URL can be overridden at build time:
///   flutter run --dart-define=API_BASE_URL=https://api.example.com
///
/// Defaults:
///   - Web: http://localhost:8000
///   - Android emulator: http://10.0.2.2:8000 (host loopback)
///   - iOS simulator / desktop: http://localhost:8000
library;

import 'package:flutter/foundation.dart';

class AppConfig {
  AppConfig._();

  static const String _defined = String.fromEnvironment('API_BASE_URL');

  static String get apiBaseUrl {
    if (_defined.isNotEmpty) return _defined;
    if (kIsWeb) return 'http://localhost:8000';
    if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }

  static const String apiV1 = '/api/v1';
}
