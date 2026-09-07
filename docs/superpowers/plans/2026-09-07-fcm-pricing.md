# FCM Pricing (2026-09-07) — FCM is free; no paid tier, no billing required. Per-device caps: 4/min, 240/hr, 10,000/day; topic fanout 1,000 msg/sec (new projects). Needs Firebase project + server key/V1 API. [firebase.google.com/pricing] [firebase.google.com/docs/cloud-messaging]

Smriti: README:104 lists FCM; notification_service.py:8-10 and .env.example:58 use console (mock). Swap NOTIFICATION_PROVIDER=fcm when keys ready. [README.md:104] [notification_service.py:8] [.env.example:58]
