/// Local reminder scheduling with flutter_local_notifications — fires
/// notifications on-device without any network, per the offline-first design.
///
/// Cadences are stored as time strings (e.g. "08:00,14:00,20:00" or
/// "08:00 AM Daily"); each time becomes a daily zoned notification.
library;

import 'package:flutter/material.dart' show TimeOfDay;
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest_all.dart' as tzdata;
import 'package:timezone/timezone.dart' as tz;

import '../models/shared_models.dart';

class ReminderScheduler {
  ReminderScheduler._();

  static final ReminderScheduler instance = ReminderScheduler._();

  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();
  bool _initialized = false;

  /// Must be called once at startup (after `flutter create .` has added the
  /// platform folders). Uses a placeholder icon id for the demo; replace with
  /// your app's notification icon on Android.
  Future<void> initialize() async {
    if (_initialized) return;
    tzdata.initializeTimeZones();
    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const ios = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    await _plugin.initialize(
      settings: const InitializationSettings(android: android, iOS: ios),
    );
    _initialized = true;
  }

  /// Schedule one daily notification per time token found in the cadence.
  Future<void> scheduleForSchedule(ReminderScheduleModel schedule) async {
    await initialize();
    for (final time in _parseTimes(schedule.cadence)) {
      await _plugin.zonedSchedule(
        id: schedule.id.hashCode * 31 + time.minute + time.hour * 60,
        title: 'Reminder — ${schedule.reminderType.name.toUpperCase()}',
        body: 'Time for your ${schedule.reminderType.name} routine.',
        scheduledDate: _nextInstanceOf(time),
        notificationDetails: const NotificationDetails(
          android: AndroidNotificationDetails(
            'reminders',
            'Daily reminders',
            channelDescription: 'Medicine, water, food and exercise reminders',
            importance: Importance.high,
            priority: Priority.high,
          ),
          iOS: DarwinNotificationDetails(),
        ),
        androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
      );
    }
  }

  Future<void> cancelSchedule(ReminderScheduleModel schedule) async {
    await initialize();
    for (final time in _parseTimes(schedule.cadence)) {
      await _plugin.cancel(
          id: schedule.id.hashCode * 31 + time.minute + time.hour * 60);
    }
  }

  Future<void> cancelAll() async {
    if (!_initialized) return;
    await _plugin.cancelAll();
  }

  List<TimeOfDay> _parseTimes(String cadence) {
    final tokens = cadence
        .toLowerCase()
        .replaceAll('am', ' am')
        .replaceAll('pm', ' pm')
        .split(RegExp(r'[,;/\s]+'))
        .where((t) => t.isNotEmpty)
        .toList();
    final times = <TimeOfDay>[];
    for (final token in tokens) {
      final m = RegExp(r'^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$').firstMatch(token);
      if (m == null) continue;
      var hour = int.parse(m.group(1)!);
      final minute = int.parse(m.group(2) ?? '0');
      final meridiem = m.group(3);
      if (meridiem == 'pm' && hour < 12) hour += 12;
      if (meridiem == 'am' && hour == 12) hour = 0;
      times.add(TimeOfDay(hour: hour, minute: minute));
    }
    return times;
  }

  tz.TZDateTime _nextInstanceOf(TimeOfDay time) {
    final now = tz.TZDateTime.now(tz.local);
    var scheduled = tz.TZDateTime(
        tz.local, now.year, now.month, now.day, time.hour, time.minute);
    if (scheduled.isBefore(now)) {
      scheduled = scheduled.add(const Duration(days: 1));
    }
    return scheduled;
  }
}
