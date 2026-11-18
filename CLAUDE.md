# Digi Royale v0.7a

Snapshot of the prototype built 2026-11-16/17 in `Downloads\digisurvivor-handoff\game`. Starting point for a rebuild as its own project.

A single-screen, portrait auto battle royale: 35 random Digimon (Rookie–Mega) fight automatically inside a shrinking zone until one is left. A HUD button switches to ROOKIES mode: 40 random Rookies out of the 60 each round, at 2× HP (`hpMul`), with ranged cooldown 0.75. The sims behind those numbers: 60 Rookies at 1× HP lost 60% of the field in 10 s and rounds lasted 36 s; this setup loses about 19% and rounds last about 53 s, and ranged Rookies' share of wins matches their share of the field (38%).

Spectating: tap a Digimon to cheer for it (`fav`). It gets a cyan ring and an arrow, its name, level and KOs show in the header, and banners announce its evolutions and its fall; if it wins, the winner card says "YOUR PICK WINS!". When 2 are left, "FINAL BATTLE · A vs B" shows and time runs at 0.35× for 2.5 real seconds (`DUEL`, applied in `frame()`, so sims that call `update()` directly are unaffected). The "+ OMNIMON" button in the bottom bar spawns Omnimon mid-round, or starts a new round with it if the last one ended.

Omnimon is special (`OMNIMON`, `isOmni`). It has an additive gold/cyan aura, a ring at its feet, rising data sparkles, and its own ultimate, "All Delete" (`allDelete`). While charging and through the ult Omnimon is drawn with the 8 poses from the user's pose guide (`vfx/omnimon-poses.png`, built by `python -I tools/mkomniposes.py tools/src/alldelete-poses.jpg vfx/omnimon-poses.png`), and he holds the ult state until the sequence ends. F3 slashes from Omnimon to the target, dealing 0.6× damage along the line, and F4–F8 play on the target. At F5 a 75 px blast deals 1.4× damage and shakes the screen. Frames: `vfx/alldelete.png`, built by `python -I tools/mkalldelete.py tools/src/alldelete-fx.jpg vfx/alldelete.png` from the user's FX sheet; timing follows the user's pose guide.

Basic attacks use the user's "Basic Elemental VFX" sheet (`vfx/basic-vfx.png`: 10 element rows × [projectile, melee], built by `python -I tools/mkguide.py basic-vfx tools/src/basic-vfx.jpg vfx/basic-vfx.png`). Ranged shots fly the projectile, about 31 px, pointed along their path. Melee hits flash the slash on the target for 0.22 s. `BASIC_ROW` maps game types to the sheet: fire and dragon = fire, water, ice, electric, grass and bug = grass, ground = earth, flying = wind, steel and normal = steel, fairy and psychic = light, dark and poison = dark.

Custom attack animations (`ANIM` in index.html) work per Digimon. Each entry is a strip of poses facing right, with a foot anchor, the body height in frame px, `charge` (the pose frames spread over the charge) and `seq` (`[pose, until s]` after the ult fires; the ult state lasts until the last one). `customPose` picks the frame, and drawUnit draws it in place of the sprite, scaled so the body matches the normal sprite height. Digimon with an `ANIM` entry skip the skill-sheet effects. So far:
- Omnimon: see above.
- Gabumon "Petit Fire" (cone): poses F1–F3 while charging and F4–F8 after firing (`vfx/gabumon-poses.png`). The effect frames F4–F8 of row 1 of `vfx/special-fx.png` grow out of his `mouth` toward the target, about 70 px long; the cone still hits out to 150 px. Built by `python -I tools/mkguide.py gabumon-poses tools/src/gabumon-poses.jpg vfx/gabumon-poses.png` and `python -I tools/mkguide.py special-fx tools/src/special-fx.jpg vfx/special-fx.png`. Rows 0 and 2 of special-fx.png (Scissors Execution = Crabmon, Lullaby Bubble = Otamamon) are cut but not used yet.

## Run
`python -m http.server 8765` in this folder, then open http://localhost:8765/ (it must be served; `file://` won't load the sheets). `?test` runs 18 self-checks (combat, EXP, bounty, evolution, Omnimon, Gabumon poses, final duel, zone events and a live Gabumon scene) and logs PASS/FAIL to the console.

## Files
- `index.html`: the whole game (one canvas, about 600 lines, no dependencies).
- `roster.js`: `window.ROSTER`, 436 Digimon `{id, n name, st stage, t type, a attribute, fly, sz, s sheet path, f frame rects [x,y,w,h,anchorX,anchorY] per pose, u signature technique}`. Built by `tools/mkroster.py <digisurvivor-sprites.zip> roster.js <app.min.js>`.
- `evo.js`: `window.EVO`, `{dex: [3 next-stage dex ids]}` for every Rookie, Champion and Ultimate. Built by `python -I tools/mkevo.py roster.js <app.min.js> evo.js` from a curated main-line table in the script, then Digimon not used yet (from the site's `G.DEX` `evo` lists first), then the rest, so every Champion, Ultimate and Mega is reachable from some Rookie. It's seeded, so rebuilds are identical.
- `sheets/`: 436 sprite sheets, one row of up to 4 poses (map, battle, attack, hit).
- `vfx/`: `atlas.png` + `atlas.json` (technique effect frames) and `techs.json` (per-Digimon kind, palette, proj/melee/beam/trail, variant). Captured from the site's `G.VFX` in the browser; no script reproduces it.
- `vfx/skills.png`: the user's "Digital Skills" sheet as 7 rows (fireball, fist, ice, bolt, vine, portal, barrier) × 7 frames of 64×52, transparent. Built by `python -I tools/mkskills.py tools/src/skills-sheet.jpg vfx/skills.png`. In game (`SKILL`, `skillOf`), ultimates use it by element type: fire uses fireball, or fist for close-range archetypes; ice and water use ice; electric bolt; grass and ground vine; dark and poison portal. Projectiles, dashes, punches and meteors fly the travel frames, and every ultimate plays the impact frames. Picking up a shield plays barrier. Other types keep the `G.VFX` effects.

## How the game works
- Animation is procedural on static poses (idle bob, walk hop, attack lunge, shoot recoil, hurt knock-back, faint slump, charge, ult). Attack/shoot → `attack` pose, hurt/faint → `hit`, else `map`. `frameFor` shrinks big poses to map size, matching against `battle`, or `hit`/`attack` when a sheet has no battle pose.
- Size is set by stage (`STAGE_HEIGHT`), not sprite size. `SIZE_MUL` scales single Digimon on top of that (Apocalymon 1.6×, about 93 px); the body radius, and so the hit and reach, scale with it.
- The arena (`ground`) is painted once in code at half resolution from a fixed seed, as original pixel art in a Digimon World 1–style meadow. Inside the zone: grass patches, a winding dirt path, flowers, tufts and small rocks. Outside it: puffy trees (some with red fruit), pines, boulders and a pond. It is decoration only: nothing collides with it. The storm outside the zone is a light purple tint (0.26) so the scenery keeps its colour.
- Data/Free/Unknown attribute can be ranged: 50% damage, no knockback, 5% faster.
- Zone shrinks nonstop over 70 s; damage rises from 1% to 10% max HP/s as it shrinks. Digimon walk back in.
- Ultimate: meter fills over time and from damage dealt/taken; fires the Digimon's signature technique in its archetype (projectile, melee, beam, dash, cone, chain, nova, aura, orbit, meteor, boomerang). Ult hits never refill the caster's meter. Fire burns, ice/water slow, electric pierces.
- Supply drops every 5 s: shield, heal, full ult, or EXP. An EXP crate gives 25 EXP at the full circle, rising to 100 as the zone closes (`DROP.expMin`/`expMax`).
- Zone events (`ZEV`, `updateEvent`): once a round, at 25 s or when 30% of the field is left (about 40% into a round in sims, 10–12 left), one random event hits, with a title over the arena. Meteor shower: for 4 s rocks fall, half on a Digimon, half anywhere; each shows a red circle for 0.8 s, then hits everyone inside it for 15% max HP with a knock-back. The rocks are the skill-sheet fireball (fly frames, with the ember frame as a trail) and land with its explosion frames (no KO credit, feed says "fell to a meteor"); about 0.3–0.9 meteor KOs a round. Data storm: 5 s with everyone's movement and attacks slowed 40%. EXP rain: 6 EXP crates drop at once.
- EXP: 100 EXP (`LEVEL_EXP`) = level up: max HP ×1.15, heal 40%, damage ×1.1, size ×1.05. A KO gives 100 EXP plus a bounty of 50 per level the victim had over the killer (`BOUNTY`), so knocking out an evolved Digimon lets an underdog catch up. A purple line under the HP and ult bars shows progress to the next level.
- ROOKIES mode only: at levels 3, 6 and 9 a Digimon digivolves into a random one of its 3 `EVO` options (Rookie → Champion → Ultimate → Mega). HP and damage scale by the stage formulas, size follows the new stage, and the technique and type switch to the new form. The ranged/melee role is kept.
- `KIND_DMG` and `MODES.rookie.kindDmg` are sim-tuned so each archetype wins 0.7–1.5× its fair share.

## Known gaps
- One-shot animation durations (`DUR`) are guesses; the real ones are in the `G.Sprites` `r` map of the site's app.min.js.
- No sound. Not tested on a real phone or with touch.

## IP
The Digimon art and names are Bandai's (sprites credited to Wikimon), and the VFX art and data come from digisurvivor.com (a fork of PokéSurvivor, MIT). Use this for reference and prototyping only. Do not publish or sell it. A public or commercial rebuild needs original art.
