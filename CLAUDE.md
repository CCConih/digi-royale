# Digi Royale v0.7a

Snapshot of the prototype built 2026-11-16/17 in `Downloads\digisurvivor-handoff\game`. Starting point for a rebuild as its own project.

A single-screen, portrait auto battle royale: 35 random Digimon (Rookie–Mega) fight automatically inside a shrinking zone until one is left. A HUD button switches to ROOKIES mode (every Rookie at once).

## Run
`python -m http.server 8765` in this folder, then open http://localhost:8765/ (it must be served; `file://` won't load the sheets). `?test` runs 10 self-checks (combat, EXP, evolution) and logs PASS/FAIL to the console.

## Files
- `index.html`: the whole game (one canvas, about 600 lines, no dependencies).
- `roster.js`: `window.ROSTER`, 436 Digimon `{id, n name, st stage, t type, a attribute, fly, sz, s sheet path, f frame rects [x,y,w,h,anchorX,anchorY] per pose, u signature technique}`. Built by `tools/mkroster.py <digisurvivor-sprites.zip> roster.js <app.min.js>`.
- `evo.js`: `window.EVO`, `{dex: [3 next-stage dex ids]}` for every Rookie, Champion and Ultimate. Built by `python -I tools/mkevo.py roster.js <app.min.js> evo.js` from a curated main-line table in the script, then Digimon not used yet (from the site's `G.DEX` `evo` lists first), then the rest, so every Champion, Ultimate and Mega is reachable from some Rookie. It's seeded, so rebuilds are identical.
- `sheets/`: 436 sprite sheets, one row of up to 4 poses (map, battle, attack, hit).
- `vfx/`: `atlas.png` + `atlas.json` (technique effect frames) and `techs.json` (per-Digimon kind, palette, proj/melee/beam/trail, variant). Captured from the site's `G.VFX` in the browser; no script reproduces it.

## How the game works
- Animation is procedural on static poses (idle bob, walk hop, attack lunge, shoot recoil, hurt knock-back, faint slump, charge, ult). Attack/shoot → `attack` pose, hurt/faint → `hit`, else `map`. `frameFor` shrinks big poses to map size, matching against `battle`, or `hit`/`attack` when a sheet has no battle pose.
- Size is set by stage (`STAGE_HEIGHT`), not sprite size.
- Data/Free/Unknown attribute can be ranged: 50% damage, no knockback, 5% faster.
- Zone shrinks nonstop over 70 s; damage rises from 1% to 10% max HP/s as it shrinks. Digimon walk back in.
- Ultimate: meter fills over time and from damage dealt/taken; fires the Digimon's signature technique in its archetype (projectile, melee, beam, dash, cone, chain, nova, aura, orbit, meteor, boomerang). Ult hits never refill the caster's meter. Fire burns, ice/water slow, electric pierces.
- Supply drops every 5 s: shield, heal, full ult, or EXP. An EXP crate gives 25 EXP at the full circle, rising to 100 as the zone closes (`DROP.expMin`/`expMax`).
- EXP: 100 EXP (`LEVEL_EXP`) = level up: max HP ×1.15, heal 40%, damage ×1.1, size ×1.05. A KO gives 100 EXP. A purple line under the HP and ult bars shows progress to the next level.
- ROOKIES mode only: at levels 3, 6 and 9 a Digimon digivolves into a random one of its 3 `EVO` options (Rookie → Champion → Ultimate → Mega). HP and damage scale by the stage formulas, size follows the new stage, and the technique and type switch to the new form. The ranged/melee role is kept.
- `KIND_DMG` and `MODES.rookie.kindDmg` are sim-tuned so each archetype wins 0.7–1.5× its fair share.

## Known gaps
- One-shot animation durations (`DUR`) are guesses; the real ones are in the `G.Sprites` `r` map of the site's app.min.js.
- No sound. Not tested on a real phone or with touch.

## IP
The Digimon art and names are Bandai's (sprites credited to Wikimon), and the VFX art and data come from digisurvivor.com (a fork of PokéSurvivor, MIT). Use this for reference and prototyping only. Do not publish or sell it. A public or commercial rebuild needs original art.
