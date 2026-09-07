# UI Visual Redesign — Care Dashboard + Games + Reminders

> **Plan mode:** Confirmed exit — redesign needed; Phase 0 done (dev_role_menu.dart exists).
> **Skills used:** /graphify query (graph.json oriented); /ponytail full; /superpowers:writing-plans.

**Goal:** Real visual identity — NE-inspir palette, card elevation, custom game illustrations, reminder color-weight.

**Tech Stack:** Flutter (mobile + dashboard), CustomPainter.

---

## Verdict (before plan)
- **Needs improvement?** YES. Design tokens generic (warm tones, no named hex); games use `Material Icons`; dashboard is single-file flat list; reminders decent but flat.
- **Already done?** Phase 0 role switcher (`dev_role_menu.dart`) confirmed; reminder cards have partial styling; `DESIGN.md` exists.
- **Not done:** Phase 1 concrete hex + shadow/spacing; Phase 2 dashboard cards + chart styling; Phase 3 CustomPainter illustrations; Phase 4 reminder per-type color; Phase 5 screenshots + a11y check.

---

## Phase 0 — Confirm (done)
`mobile/lib/widgets/dev_role_menu.dart` exists; `main.dart` references role-aware routing (`caregiver_dashboard_screen.dart`). Confirm only.

## Phase 1 — Design Tokens
Files: `DESIGN.md`, `mobile/lib/theme/monad_theme.dart`, `dashboard/lib/theme/monad_theme.dart`.
Add hex palette: tea `#2D5A27`, gold `#C9A227`, terracotta `#C0704A`, indigo `#3D2B7A`, parchment `#FAF3DC`, ash `#EAE6DC`.
Shadow: `blurRadius 8, opacity 0.12`; radius: 16/8; spacing: 8/16/24/32.
Sync both theme files.

## Phase 2 — Dashboard (`dashboard/lib/main.dart`)
Card layout (`Card`, `elevation 2`, `RoundedRectangleBorder(radius 16)`) per metric.
Trend charts (`CustomPaint`) use palette colors; add soft background oval.
Hierarchy: overview → compliance → risk (spacing 24).
Accessibility: text ≥14sp, contrast AA (check green-on-parchment).

## Phase 3 — Games (`mobile/lib/games/game_visuals.dart` + screens)
Replace `iconFor` `Material Icons` with `CustomPainter` flat geometric shapes per culture item (rhino, tea, silk, jaapi, dhol, bamboo, shawl, festivals).
Each card: distinct `backgroundColor` (palette), `borderRadius 20`, `BoxShadow`, padding 12.
Routine cards: same container style, simplified.

## Phase 4 — Reminders (`mobile/lib/screens/reminders_screen.dart`)
Per-type accent: medication=terracotta, routine=tea, appointment=indigo.
Keep existing `done` green (`#E8F5E8`) + icon; pending = white + left bar (existing — keep, update hex to palette).
Spacing: card padding 16, gap 12.

## Phase 5 — Report
Screenshots (emulator) to `docs/superpowers/plans/2026-09-07-ui-redesign-screenshots/`.
Confirm touch targets ≥60dp, contrast AA, no color-only (icon+text always).
No backend/file changes needed.

---

## Verification
- `flutter analyze` green; `pytest` unchanged (UI only).
- Visual: load screens, confirm cards/shadow/colors; CustomPainter shapes visible; reminder types distinguishable by icon+color.
