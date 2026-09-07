# Fix-All — 5 Broken Frontend / Pipeline Wiring

GOAL: Dashboard buttons work; RAG upload visible; games show real art; adaptive engines reconciled.

PHASES (lazy order, smallest first):
1. Reconcile adaptive_engine.zip vs difficulty_engine.py → keep existing, archive zip (Done: existing is rule-based with DB audit; zip is standalone ML — different, both stay; zip archived).
2. Wire risk-screening card to POST endpoint → use feature_names.json input (32 fields) → card feeds endpoint.
3. Add RAG upload button in dashboard → calls /documents/upload → results to summary.
4. Fix reminder add/remove 404 → _Api.deleteSchedule sends correct schedule_id; check route.
5. Game art — fill availableImages with real PNG keys, or leave as CustomPainter (already working — not broken, just unfunded).
