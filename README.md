# Digi Royale v0.7a

A single-screen, portrait auto battle royale prototype: 35 Digimon fight automatically inside a shrinking zone until one is left. Tap the mode button to switch to ROOKIES (every Rookie at once), and the speed button for 1×/2×/4×.

**Play:** https://ccconih.github.io/digi-royale/

Add `?test` to the URL to run the combat-rule self-checks (results in the browser console).

## Run locally
```
python -m http.server 8765
```
Then open http://localhost:8765/.

## Credits
Fan-made, non-commercial test prototype. Digimon names and sprite art belong to Bandai (sprites via Wikimon). Technique effect art and data come from [digisurvivor.com](https://digisurvivor.com/), a fork of [PokéSurvivor](https://github.com/JPTER78/pokesurvivor). Not affiliated with or endorsed by any of them. The code in `index.html` and `tools/` is the only original work here.
