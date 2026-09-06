/// Daily Reminders — gradient cards with cultural atmosphere.
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
    setState(() { _loading = true; _error = null; });
    try {
      final schedules = await _reminders.getSchedules(widget.patientId);
      final events = await _reminders.getTodaysEvents(widget.patientId);
      for (final schedule in schedules) {
        ReminderScheduler.instance.scheduleForSchedule(schedule).catchError((_) {});
      }
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
      setState(() { _loading = false; _error = 'Could not load reminders. $e'; });
    }
  }

  Future<void> _handleAcknowledge(ReminderScheduleModel schedule) async {
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

  // ---- Design helpers ----

  static LinearGradient _gradientFor(ReminderType type) {
    switch (type) {
      case ReminderType.medicine:
        return const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFFE8EEFF), Color(0xFFF3F6FF)]);
      case ReminderType.water:
        return const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFFE0EDFF), Color(0xFFF0F7FF)]);
      case ReminderType.food:
        return const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFFFFF3E0), Color(0xFFFFFBF5)]);
      case ReminderType.exercise:
        return const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFFE8FFF0), Color(0xFFF4FFFB)]);
    }
  }

  static IconData _iconFor(ReminderType type) {
    switch (type) {
      case ReminderType.medicine: return Icons.medication;
      case ReminderType.water: return Icons.water_drop;
      case ReminderType.food: return Icons.restaurant;
      case ReminderType.exercise: return Icons.directions_walk;
    }
  }

  static Color _accentFor(ReminderType type) {
    switch (type) {
      case ReminderType.medicine: return Monad.lakeBlue;
      case ReminderType.water: return Monad.skyBlue;
      case ReminderType.food: return const Color(0xFFD4A030);
      case ReminderType.exercise: return const Color(0xFF3CB371);
    }
  }

  static String _assameseFor(ReminderType type) {
    switch (type) {
      case ReminderType.medicine: return 'ঔষধ';
      case ReminderType.water: return 'পানী';
      case ReminderType.food: return 'খাদ্য';
      case ReminderType.exercise: return 'চলাচল';
    }
  }

  static String _descriptionFor(ReminderType type) {
    switch (type) {
      case ReminderType.medicine: return 'Time to take your medicine';
      case ReminderType.water: return 'Stay hydrated — drink water';
      case ReminderType.food: return 'Remember your meals';
      case ReminderType.exercise: return 'Light movement helps your mind';
    }
  }

  Widget _buildSectionHeader(String title, {String? subtitle}) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(4, 24, 4, 12),
      child: Row(
        children: [
          Container(width: 3, height: 24, decoration: BoxDecoration(
            color: Monad.lakeBlue, borderRadius: BorderRadius.circular(2))),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: Monad.subheading.copyWith(fontSize: 22)),
              if (subtitle != null) ...[
                const SizedBox(height: 2),
                Text(subtitle, style: Monad.monoCaption),
              ],
            ],
          ),
          const Spacer(),
        ],
      ),
    );
  }

  Widget _buildCard(ReminderScheduleModel schedule) {
    final done = _justAcked.contains(schedule.id);
    final hasOpenEvent = _openEventBySchedule.containsKey(schedule.id);
    final accent = _accentFor(schedule.reminderType);
    final gradient = _gradientFor(schedule.reminderType);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: done ? const Color(0xFFF8FFF8) : null,
        gradient: done ? null : gradient,
        borderRadius: BorderRadius.circular(Monad.radiusCard),
        border: Border.all(
          color: done ? const Color(0xFFD0EED0) : Monad.ash.withValues(alpha: 0.6),
          width: 1,
        ),
        boxShadow: Monad.cardShadow,
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          // Main row
          Padding(
            padding: const EdgeInsets.all(24),
            child: Row(
              children: [
                // Icon container
                Container(
                  width: 64, height: 64,
                  decoration: BoxDecoration(
                    color: done ? const Color(0xFFE8F5E8) : Monad.parchment,
                    borderRadius: BorderRadius.circular(Monad.radiusMin),
                    border: Border.all(
                      color: done ? const Color(0xFFB8D8B8) : accent.withValues(alpha: 0.4),
                      width: done ? 1 : 1.5,
                    ),
                    boxShadow: done ? null : [
                      BoxShadow(color: accent.withValues(alpha: 0.12), blurRadius: 8, offset: const Offset(0, 2)),
                    ],
                  ),
                  child: Icon(
                    done ? Icons.check_rounded : _iconFor(schedule.reminderType),
                    color: done ? const Color(0xFF4CAF50) : accent,
                    size: 30,
                  ),
                ),
                const SizedBox(width: 18),
                // Content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Type pill + assamese
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                            decoration: BoxDecoration(
                              color: accent.withValues(alpha: done ? 0.1 : 0.15),
                              borderRadius: BorderRadius.circular(Monad.radiusPill),
                              border: Border.all(color: accent.withValues(alpha: 0.3)),
                            ),
                            child: Text(
                              schedule.reminderType.name.toUpperCase(),
                              style: Monad.monoCaption.copyWith(
                                color: done ? const Color(0xFF4CAF50) : accent,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            _assameseFor(schedule.reminderType),
                            style: Monad.monoCaption.copyWith(
                              color: done ? const Color(0xFF4CAF50) : accent,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        done ? '✓ Done today' : _descriptionFor(schedule.reminderType),
                        style: Monad.monoLabel.copyWith(
                          color: done ? const Color(0xFF4CAF50) : Monad.offBlack,
                          fontSize: 17,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        done ? '' : schedule.cadence,
                        style: Monad.monoBody.copyWith(
                          color: done ? const Color(0xFF4CAF50) : Monad.smoke,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Action button
          if (!done)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: SizedBox(
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: !hasOpenEvent ? null : () => _handleAcknowledge(schedule),
                  icon: Icon(
                    hasOpenEvent ? Icons.check_circle : Icons.access_time,
                    size: 24,
                    color: Monad.white,
                  ),
                  label: Text(
                    hasOpenEvent ? 'I Did This  কৰিলোঁ' : 'Not Due Now',
                    style: Monad.monoLabel.copyWith(color: Monad.white, fontSize: 17),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: accent,
                    foregroundColor: Monad.white,
                    disabledBackgroundColor: Monad.parchment,
                    disabledForegroundColor: Monad.smoke,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(Monad.radiusMin),
                    ),
                    elevation: hasOpenEvent ? 2 : 0,
                    shadowColor: accent.withValues(alpha: 0.4),
                  ),
                ),
              ),
            ),
          if (done)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Container(
                height: 56,
                decoration: BoxDecoration(
                  color: const Color(0xFFE8F5E8),
                  borderRadius: BorderRadius.circular(Monad.radiusMin),
                  border: Border.all(color: const Color(0xFFD0EED0)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.check_circle, color: Color(0xFF4CAF50), size: 24),
                    const SizedBox(width: 10),
                    Text(
                      'Well done! — ধন্যবাদ',
                      style: Monad.monoLabel.copyWith(color: const Color(0xFF4CAF50), fontSize: 17),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Daily Reminders'),
        centerTitle: false,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _messageView(Icons.cloud_off, _error!, retry: _load)
              : _schedules == null || _schedules!.isEmpty
                  ? _messageView(Icons.alarm_on, 'No reminders yet — your caregiver will set them up.')
                  : RefreshIndicator(
                      onRefresh: _load,
                      color: Monad.lakeBlue,
                      child: ListView(
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                        children: [
                          _buildSectionHeader(
                            'Your Day',
                            subtitle: 'Tap when you complete each one',
                          ),
                          ...(_schedules!.map((s) => _buildCard(s))),
                          const SizedBox(height: 32),
                        ],
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
            Container(
              width: 80, height: 80,
              decoration: BoxDecoration(
                color: Monad.periwinkleMist,
                borderRadius: BorderRadius.circular(24),
              ),
              child: Icon(icon, size: 40, color: Monad.smoke),
            ),
            const SizedBox(height: 20),
            Text(text, textAlign: TextAlign.center, style: Monad.monoBodyLg),
            if (retry != null) ...[
              const SizedBox(height: 20),
              FilledButton(onPressed: retry, child: const Text('Try Again')),
            ],
          ],
        ),
      ),
    );
  }
}
