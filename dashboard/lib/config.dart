/// Centralised config — kept small on purpose.
/// _baseUrl must be importable from widgets (was private to main.dart).
library;

const String apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000',
);
