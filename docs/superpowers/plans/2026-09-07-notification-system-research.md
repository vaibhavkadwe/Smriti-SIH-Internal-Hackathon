# Notification System Research — 2026-09-07

## 1. Current Notification Provider Interface

**File:** `backend/app/services/notification_service.py`

The `NotificationProvider` ABC defines two abstract methods [source: `notification_service.py:38-61`]:

```python
class NotificationProvider(ABC):
    @abstractmethod
    async def send_alert(
        self,
        patient_id: UUID,
        alert_id: UUID,
        severity: str,
        trigger: str,
        summary: str,
        recipients: List[Dict[str, Any]],
    ) -> None: ...

    @abstractmethod
    async def send_reminder_reprompt(
        self,
        patient_id: UUID,
        event_id: UUID,
        reminder_type: str,
    ) -> None: ...
```

`send_alert` fans out AlertFlags to family/ASHA links. `send_reminder_reprompt` fires for unacknowledged reminders after 10 minutes. There is **no method for initial reminder delivery** — that is handled on-device by `flutter_local_notifications`.

The concrete `ConsoleNotificationProvider` stores each delivery in an in-memory `deliveries` list for testing [source: `notification_service.py:65-87`]. `get_notification_provider()` reads `NOTIFICATION_PROVIDER` from config (`"console"` default) and falls back to console on unknown names [source: `notification_service.py:100-107`]. Only `"console"` / `"log"` / `"logonly"` are accepted; others raise and fall back.

---

## 2. How Reminders and Alerts Route to Notifications

### Reminders
`ReminderService.parse_cadence()` parses cadence strings (e.g. `"08:00,14:00"`) into wall-clock times [source: `reminder_service.py:37-55`]. The generation job creates `ReminderEvent(PENDING)` rows; the escalation scan (every 60s, `REMINDER_ESCALATE_MINUTES=10`, `REMINDER_MISSED_MINUTES=60`) updates them:

```
PENDING (10 min unacked) → ESCALATED (reprompt via notify_reprompts)
ESCALATED (60 min total unacked) → MISSED
3+ unresolved same-type in 7 days → AlertFlag
```

`notify_reprompts()` sends `send_reminder_reprompt()` per ESCALATED event; `notify_escalation_results()` fans out new AlertFlags to family + ASHA via `send_alert()` [source: `notification_service.py:110-166`, `notification_service.py:169-195`].

Both swallow exceptions [source: `notification_service.py:164-165`, `notification_service.py:193-194`]. `AlertEngine.run_hourly_pass()` (3600s) also calls `evaluate_escalations()` plus a cognitive-drop rule (20%+ drop over 14 days) [source: `alert_engine.py:42-129`, `alert_engine.py:131-173`].

### Key gap: reprompt has no recipient
`notify_reprompts()` passes only `patient_id` to `send_reminder_reprompt()` [source: `notification_service.py:186-191`]. There is no recipient list; FCM or SMS implementations would need to resolve the device token / phone from DB inside the provider, not as a parameter.

---

## 3. Existing Notification Providers

**Only `ConsoleNotificationProvider`.** Config: `NOTIFICATION_PROVIDER=console` [source: `config.py:100`]. References to `sms`, `fcm`, `email` exist in comments and `.env.example` [source: `.env.example:57-58`, `notification_service.py:11`] but no implementations, dependencies, or routes exist. `requirements.txt` and `pubspec.yaml` have no FCM, Twilio, or SMTP packages.

---

## 4. Escalation Flow (Full)

```
ReminderSchedule.cadence → [generate job, 60s] ReminderEvent(PENDING)
    PENDING, unacked 10m → ESCALATED + notify_reprompts (reprompt)
    ESCALATED, unacked 60m → MISSED
    3+ unresolved (MISSED | ESCALATED) same-type in 7 days → AlertFlag
        → notify_escalation_results → send_alert
        → recipients: active CaregiverPatientLink (FAMILY_CAREGIVER | ASHA_WORKER)
```

Recipients for alerts are queried per call (DB query of `User` + `CaregiverPatientLink`) [source: `notification_service.py:126-136`]. Alert dedup: 1 per `(patient, trigger)` per 24h [source: `notification_service.py:308-314`, `alert_engine.py:54-64`].

---

## 5. Mobile Local Notification System

**Package:** `flutter_local_notifications: ^22.3.0` [source: `pubspec.yaml:21`], with `timezone: ^0.11.1` [source: `pubspec.yaml:22`]. `ReminderScheduler` (singleton, `reminder_scheduler.dart`) handles everything on-device [source: `reminder_scheduler.dart:15-109`]:

- `initialize()` — creates plugin; requests alert/badge/sound permissions on iOS [source: `reminder_scheduler.dart:27-39`]
- `scheduleForSchedule()` — parses cadence, creates one `zonedSchedule` per time token; notification ID computed as `hashCode * 31 + minute + hour * 60` [source: `reminder_scheduler.dart:43-63`]
- `cancelSchedule()` / `cancelAll()` — by computed ID [source: `reminder_scheduler.dart:66-77`]

Uses `AndroidScheduleMode.inexactAllowWhileIdle` (battery-friendly, high priority channel `"reminders"`) [source: `reminder_scheduler.dart:53-62`].

No FCM dependency. The mobile app is fully offline-first for reminders — no push from backend reaches it.

---

## 6. What Would Be Needed to Add FCM and SMS

### FCM

**New backend pieces:**
- `FCMNotificationProvider` implementing the ABC; add `"fcm"` to `_build_provider()`
- `FCM_PROJECT_ID`, `FCM_SERVICE_ACCOUNT_JSON` settings in `config.py`
- `UserDeviceToken` (or `PatientDeviceToken`) model: `user_id`, `fcm_token`, `platform`, `updated_at`
- `POST /api/v1/devices/register` endpoint (patient + caregiver versions)
- Mobile: add `firebase_core` + `firebase_messaging` to `pubspec.yaml`; POST token to register endpoint; listen to `onMessage` for push notifications (reprompt path needs this to replace the no-op push path)
- `_build_provider()` must accept `"fcm"`

Note: the `send_reminder_reprompt()` method takes `patient_id` but no recipient — FCM provider must resolve the patient's token from the DB inside the call [source: `notification_service.py:54-62`].

### SMS (Twilio)

**New backend pieces:**
- `SMSNotificationProvider`; add `"sms"` to `_build_provider()`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` in `config.py`
- `send_alert()` uses `client.messages.create()` per recipient; `send_reminder_reprompt()` uses patient phone from DB (same recipient gap as FCM)
- `twilio` package in `requirements.txt`
- No mobile dependency needed — SMS is pure backend-to-user

Both share the same audit gap described in Section 7.

---

## 7. Audit / Record-Keeping

**No delivery audit table exists.**

- `NotificationProvider` has no delivery-receipt method; `ConsoleNotificationProvider.deliveries` is in-memory only (test seam) [source: `notification_service.py:76`]
- `NotificationLog` or `NotificationDelivery` model: **absent** from `backend/app/models/`
- `ReminderEvent.status` (PENDING/ESCALATED/ACKNOWLEDGED/MISSED) tracks patient response state, not delivery state
- `AlertFlag` records that an alert was raised, not delivered
- `AuditLog` (compliance) tracks user data access, not notification delivery
- Delivery failures are caught, logged (`logger.error()`), and suppressed — never persisted [source: `notification_service.py:164-165`, `notification_service.py:193-194`]

**Compliance implication:** DPDP 2023 requires a record of notifications sent. The current in-memory-only `deliveries` list does not survive process restart or audit requests.

**Minimum viable fix:** new `NotificationDelivery` model (`id`, `provider`, `kind`={`reprompt`/`alert`}, `event_id`, `recipient_user_id`, `address`={phone/token}, `status`={sent/failed}, `created_at`), written inside each provider `send_*` method. FCM delivery receipts (`message.id` returned by Firebase) could be added later for delivery confirmation tracking.

---

## Changes Needed (Practical)

| Priority | Area | What | File impact |
|---|---|---|---|
| P0 | FCM push | `FCMNotificationProvider` + `fcm` factory entry | `notification_service.py` |
| P0 | SMS | `SMSNotificationProvider` + `sms` factory entry | `notification_service.py` |
| P0 | Mobile push | `firebase_core` / `firebase_messaging` in `pubspec.yaml`, token POST endpoint, notification-tap handler | `pubspec.yaml`, new mobile service, new backend route |
| P0 | Recipient DB | `UserDeviceToken` model + migration + register endpoint | `models/`, `routes/` |
| P1 | Audit | `NotificationDelivery` model + migration; write from each provider | new model + migration |
| P1 | Config | `FCM_*`, `TWILIO_*`, `NOTIFICATION_PROVIDER` expanded validation | `config.py`, `.env.example` |
| P2 | Retry / receipt | Retry queue or retry-on-failure in providers; FCM receipt callback | `notification_service.py` or new job |

The notification interface is clean and well-isolated; the main gap is not the interface design but the missing implementations (FCM, SMS) and the absence of a delivery audit trail.
