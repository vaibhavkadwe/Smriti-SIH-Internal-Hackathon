/// Daily Reminders — large accessible cards for medicine/water/food/exercise.
library;

import 'package:flutter/material.dart';

import '../models/shared_models.dart';
import '../services/reminder_scheduler.dart';
import '../services/reminder_service.dart';
import '../theme/monad_theme.dart';

class RemindersScreen extends StatefulWidget {
  final String patientId;

  const RemindersScreen({super.key, required this.patientId});

  @override
  State<RemindersScreen> createState() => _RemindersScreenState();
}

class _RemindersScreenState extends State<RemindersScreen> {
  final MobileReminderService _reminders = MobileReminderService();

  List<ReminderScheduleModel>? _schedules;
  // schedule id -> latest still-open (pending/escalated) event for that schedule.
  Map<String, ReminderEventModel> _openEventBySchedule = {};
  bool _loading = true;
  String? _error;
  final Set<String> _justAcked = {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final schedules = await _reminders.getSchedules(widget.patientId);
      final events = await _reminders.getTodaysEvents(widget.patientId);
      // Schedule local daily notifications so reminders fire without network.
      for (final schedule in schedules) {
        ReminderScheduler.instance.scheduleForSchedule(schedule).catchError((_) {});
      }
      // Resolve the latest OPEN event per schedule (real id to acknowledge).
      final open = <String, ReminderEventModel>{};
      for (final e in events) {
        if (e.status == ReminderStatus.pending || e.status == ReminderStatus.escalated) {
          final existing = open[e.scheduleId];
          if (existing == null || e.scheduledAt.isAfter(existing.scheduledAt)) {
            open[e.scheduleId] = e;
          }
        }
      }
      if (!mounted) return;
      setState(() {
        _schedules = schedules;
        _openEventBySchedule = open;
        _loading = false;
      });
    } on Exception catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Could not load reminders. $e';
      });
    }
  }

  Future<void> _handleAcknowledge(ReminderScheduleModel schedule) async {
    // Acknowledge the REAL open event for this schedule (not the schedule id).
    // Offline acks are queued by the service and replayed on reconnect.
    final openEvent = _openEventBySchedule[schedule.id];
    if (openEvent == null) return;
    final reachedServer = await _reminders.acknowledgeReminder(
      patientId: widget.patientId,
      eventId: openEvent.id,
      method: 'button',
    );
    if (!mounted) return;
    setState(() {
      _justAcked.add(schedule.id);
      _openEventBySchedule.remove(schedule.id);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '${schedule.reminderType.name.toUpperCase()} done — well done! '
          '${reachedServer ? '' : '(offline — will sync)'}',
        ),
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Daily Reminders / দৈনিক সোঁৱৰণী'),
        centerTitle: false,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _messageView(Icons.cloud_off, _error!, retry: _load)
              : _schedules == null || _schedules!.isEmpty
                  ? _messageView(Icons.alarm_on, 'All caught up — no scheduled reminders yet.')
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _schedules!.length,
                        itemBuilder: (context, index) =>
                            _scheduleCard(_schedules![index]),
                      ),
                    ),
    );
  }

  Widget _messageView(IconData icon, String text, {VoidCallback? retry}) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 80, color: Monad.smoke),
            const SizedBox(height: 16),
            Text(text, textAlign: TextAlign.center, style: Monad.monoBodyLg),
            if (retry != null) ...[
              const SizedBox(height: 16),
              ElevatedButton(onPressed: retry, child: const Text('Retry')),
            ],
          ],
        ),
      ),
    );
  }

  Widget _scheduleCard(ReminderScheduleModel schedule) {
    final done = _justAcked.contains(schedule.id);
    final hasOpenEvent = _openEventBySchedule.containsKey(schedule.id);
    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 16),
      shape: Monad.cardShape,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: Monad.parchment,
                    border: Border.all(color: Monad.ash),
                    borderRadius: BorderRadius.circular(Monad.radiusMin),
                  ),
                  child:
                      Icon(_iconFor(schedule.reminderType), color: Monad.offBlack, size: 20),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        schedule.reminderType.name.toUpperCase(),
                        style: Monad.monoLabel.copyWith(
                          color: done ? Monad.smoke : Monad.offBlack,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Time: ${schedule.cadence}',
                        style: Monad.monoBodySm,
                      ),
                    ],
                  ),
                ),
                if (done) const Icon(Icons.check_circle, color: Monad.offBlack, size: 32),
              ],
            ),
            const SizedBox(height: 18),
            SizedBox(
              width: double.infinity,
              height: 58,
              child: ElevatedButton.icon(
                onPressed: (done || !hasOpenEvent) ? null : () => _handleAcknowledge(schedule),
                icon: const Icon(Icons.check_circle, size: 28, color: Monad.white),
                label: Text(
                  done
                      ? 'Done / সম্পন্ন'
                      : hasOpenEvent
                          ? 'I Did This / কৰিলোঁ'
                          : 'No reminder due now / এতিয়া নাই',
                  style: Monad.monoLabel.copyWith(color: Monad.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _iconFor(ReminderType type) {
    switch (type) {
      case ReminderType.medicine:
        return Icons.medication;
      case ReminderType.water:
        return Icons.water_drop;
      case ReminderType.food:
        return Icons.restaurant;
      case ReminderType.exercise:
        return Icons.directions_walk;
    }
  }
}
