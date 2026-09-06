# Game Assets — To Be Sourced/Commissioned

Nothing here is required for the games to run — every visual falls back to a
theme-colored Material icon (`lib/games/game_visuals.dart`), so a missing PNG
never crashes the UI. Ship files with these exact names, then add their keys
to `GameVisuals.availableImages` to activate them.

## Illustrated card icons — `assets/games/icons/` (32 PNGs)

Festivals: bihu, hornbill, chapchar_kut, nongkrem, losar, sangken, wangala,
moatsu, dree, ningol_chakouba

Flora/food: kaji_nemu, bhut_jolokia, ou_tenga, jolpai, bamboo_shoot, lakadong,
starfruit, tamul_pan, kopou, assam_tea_leaf

Heritage: jaapi, xorai, gamosa, rhino, red_panda, dhol, pepa, mekhela, puan,
eri_silk, bamboo_craft, naga_shawl

## Audio — `assets/audio/` (soft, <1s)

- match_success.wav — soft chime on a matched pair
- step_correct.wav — gentle click on a correct routine placement

(Both pair with a light haptic; wrong answers play nothing — no punishment.)
