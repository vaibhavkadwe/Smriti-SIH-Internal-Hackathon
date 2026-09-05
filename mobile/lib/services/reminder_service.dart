/// Mobile Reminder Service — fetches reminder schedules + today's events from
/// the backend and acknowledges events by their REAL event id. Acknowledgments
/// that can't reach the server are queued (drift outbox) and replayed later, so
/// an offline "I Did This" is never lost.
library;

import 'package:flutter/foundation.dart';

import '../models/shared_models.dart';
import 'api_service.dart';
import 'offline_sync_service.dart';

class MobileReminderService {
  final ApiService apiService;
  final OfflineSyncService sync;

  MobileReminderService({ApiService? apiService, OfflineSyncService? sync})
      : apiService = apiService ?? ApiService.instance,
        sync = sync ?? OfflineSyncService.instance;

  Future<List<ReminderScheduleModel>> getSchedules(String patientId) async {
    try {
      return await apiService.reminderSchedules(patientId);
    } catch (e) {
      debugPrint('Reminder fetch failed (offline?): $e');
      rethrow;
    }
  }

  /// Today's reminder events (real ids + status). Returns [] when offline so the
  /// screen still renders the schedule cards.
  Future<List<ReminderEventModel>> getTodaysEvents(String patientId) async {
    try {
      return await apiService.reminderEvents(patientId);
    } catch (e) {
      debugPrint('Reminder events fetch failed (offline?): $e');
      return const [];
    }
  }

  /// Acknowledge a reminder event by its real id. Returns true when the server
  /// confirmed; false when offline — in which case the ack is queued for replay
  /// (never dropped).
  Future<bool> acknowledgeReminder({
    required String patientId,
    required String eventId,
    required String method,
  }) async {
    try {
      await apiService.acknowledgeReminder(eventId, method: method);
      return true;
    } catch (e) {
      debugPrint('Ack could not reach server (offline?), queueing for sync: $e');
      try {
        await sync.enqueueReminderAck(
          patientId: patientId,
          eventId: eventId,
          method: method,
        );
      } catch (qe) {
        debugPrint('Failed to enqueue offline ack: $qe');
      }
      return false;
    }
  }
}
