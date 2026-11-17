# Builds evo.js: window.EVO = {dex: [3 next-stage dex ids]} for every Rookie, Champion and Ultimate.
# Usage: python -I tools/mkevo.py roster.js <app.min.js from digisurvivor.com> evo.js
# Options = curated main line first, then random picks from the site's G.DEX `evo` list (one stage up),
# then random Digimon of the next stage when that list runs short. Seeded, so rebuilds are identical.
import json, random, re, sys

# Well-known main lines (anime / V-pet). Only next-stage names that exist in roster.js.
MAIN = {
    # Rookie -> Champion
    'Agumon': ['Greymon', 'GeoGreymon'], 'Gabumon': ['Garurumon'], 'Palmon': ['Togemon'], 'Tentomon': ['Kabuterimon'],
    'Patamon': ['Angemon'], 'Biyomon': ['Birdramon'], 'Gomamon': ['Ikkakumon'], 'Salamon': ['Gatomon'],
    'Betamon': ['Seadramon'], 'Otamamon': ['Gekomon'], 'Toy Agumon': ['Greymon'], 'DemiDevimon': ['Devimon'],
    'Tsukaimon': ['Devimon'], 'Goblimon': ['Ogremon'], 'SnowGoblimon': ['Hyogamon'], 'Hagurumon': ['Guardromon'],
    'Armadillomon': ['Ankylomon'], 'Terriermon': ['Gargomon'], 'Veemon': ['ExVeemon', 'Veedramon'], 'Wormmon': ['Stingmon'],
    'Hawkmon': ['Aquilamon'], 'Keramon': ['Kurisarimon'], 'Monodramon': ['Strikedramon'], 'Renamon': ['Kyubimon'],
    'Guilmon': ['Growlmon'], 'Dorumon': ['Dorugamon'], 'Dracmon': ['Sangloupmon'], 'Gaomon': ['Gaogamon'],
    'Lalamon': ['Sunflowmon'], 'Coronamon': ['Firamon'], 'Lunamon': ['Lekismon'], 'Hyokomon': ['Peckmon'],
    'Bearmon': ['Grizzlymon'], 'Kunemon': ['Flymon'], 'Candlemon': ['Wizardmon'], 'Mushroomon': ['Woodmon'],
    'Shoutmon': ['Shoutmon X2 (Shoutmon Times Two)'],
    'Pawn Chessmon (Black)': ['Knight Chessmon (Black)'], 'PawnChessmon (White)': ['Knight Chessmon (White)'],
    # Champion -> Ultimate
    'Greymon': ['MetalGreymon (Vaccine)'], 'GeoGreymon': ['RizeGreymon'], 'Garurumon': ['WereGarurumon'],
    'Togemon': ['Lillymon'], 'Kabuterimon': ['MegaKabuterimon (Red)'], 'Angemon': ['MagnaAngemon'],
    'Birdramon': ['Garudamon'], 'Ikkakumon': ['Zudomon'], 'Gatomon': ['Angewomon'], 'Seadramon': ['Mega Seadramon'],
    'Gekomon': ['ShogunGekomon'], 'Guardromon': ['Andromon'], 'Gargomon': ['Rapidmon'], 'ExVeemon': ['Paildramon'],
    'Veedramon': ['AeroVeedramon'], 'Stingmon': ['Dinobeemon'], 'Aquilamon': ['Silphymon'], 'Kurisarimon': ['Infermon'],
    'Strikedramon': ['Cyberdramon'], 'Kyubimon': ['Taomon'], 'Growlmon': ['WarGrowlmon'], 'Dorugamon': ['DoruGreymon'],
    'Sangloupmon': ['Matadormon'], 'Gaogamon': ['MachGaogamon'], 'Sunflowmon': ['Lilamon'], 'Firamon': ['Flaremon'],
    'Lekismon': ['Crescemon'], 'Peckmon': ['Yatakaramon'], 'Grizzlymon': ['GrapLeomon'], 'Monochromon': ['Triceramon'],
    'Tyrannomon': ['MasterTyrannomon'], 'DarkTyrannomon': ['MetalTyrannomon'], 'Numemon': ['Monzaemon'],
    'Sukamon': ['Etemon'], 'Woodmon': ['Cherrymon'], 'Kuwagamon': ['Okuwamon'], 'Starmon': ['Superstarmon'],
    # Ultimate -> Mega
    'MetalGreymon (Vaccine)': ['WarGreymon'], 'RizeGreymon': ['Shine Greymon'], 'WereGarurumon': ['MetalGarurumon'],
    'Lillymon': ['Rosemon'], 'MegaKabuterimon (Red)': ['HerculesKabuterimon'], 'MagnaAngemon': ['Seraphimon'],
    'Garudamon': ['Phoenixmon'], 'Zudomon': ['Vikemon'], 'Angewomon': ['Ophanimon'], 'Mega Seadramon': ['Metal Seadramon'],
    'Andromon': ['HiAndromon'], 'Rapidmon': ['MegaGargomon'], 'Paildramon': ['Imperialdramon (Dragon Mode)'],
    'AeroVeedramon': ['UlforceVeedramon'], 'Silphymon': ['Valkyrimon'], 'Infermon': ['Diaboromon'],
    'Cyberdramon': ['Justimon (Accel Arm)'], 'Taomon': ['Sakuyamon'], 'WarGrowlmon': ['Gallantmon'],
    'DoruGreymon': ['Dorugoramon'], 'Matadormon': ['GranDracmon'], 'MachGaogamon': ['MirageGaogamon'],
    'Lilamon': ['Lotosmon'], 'Flaremon': ['Apollomon'], 'Crescemon': ['Dianamon'], 'Yatakaramon': ['Ravemon'],
    'GrapLeomon': ['BanchoLeomon'], 'Etemon': ['Metal Etemon'], 'Cherrymon': ['Puppetmon'], 'Okuwamon': ['Gran Kuwagamon'],
    'Myotismon': ['VenomMyotismon'], 'Mammothmon': ['SkullMammothmon'], 'Knightmon': ['LordKnightmon'],
}

roster = json.loads(re.search(r'window\.ROSTER=(\[.*\]);', open(sys.argv[1], encoding='utf-8').read(), re.S)[1])
js = open(sys.argv[2], encoding='utf-8').read()
site = {int(m[1]): [int(x) for x in m[2].split(',') if x] for m in re.finditer(r'\{dex:(\d+),name:"[^"]*"[^{}]*?evo:\[([\d,]*)\]', js)}
by_id = {d['id']: d for d in roster}
by_name = {}
for d in roster: by_name.setdefault(d['n'], d)  # roster has one duplicate name (Ghoulmon); first wins

rng = random.Random(7)
evo, stats = {}, {'main': 0, 'site': 0, 'random': 0}
for st in (2, 3, 4):  # stage by stage, so every Digimon of the next stage is some option (coverage)
    src = [d for d in roster if d['st'] == st]
    nxt_ids = [x['id'] for x in roster if x['st'] == st + 1]
    opts, pools = {}, {}
    for d in src:
        opts[d['id']] = [by_name[n]['id'] for n in MAIN.get(d['n'], [])][:3]
        assert all(by_id[i]['st'] == st + 1 for i in opts[d['id']]), (d['n'], opts[d['id']])
        pools[d['id']] = [i for i in site.get(d['id'], []) if i in by_id and by_id[i]['st'] == st + 1]
        rng.shuffle(pools[d['id']])
    stats['main'] += sum(len(v) for v in opts.values())
    used = {i for v in opts.values() for i in v}
    free = lambda k: len(opts[k]) < 3
    # 1) round-robin: each Digimon with a free slot takes one still-unused Digimon from its own site list
    order = [d['id'] for d in src]; rng.shuffle(order)
    while True:
        took = False
        for k in order:
            if not free(k): continue
            c = next((i for i in pools[k] if i not in used), None)
            if c is not None: opts[k].append(c); used.add(c); took = True; stats['site'] += 1
        if not took: break
    # 2) still-unused Digimon nobody's site list offers: hand each to a random free slot
    left = [i for i in nxt_ids if i not in used]; rng.shuffle(left)
    for i in left:
        k = rng.choice([k for k in order if free(k)]); opts[k].append(i); used.add(i); stats['random'] += 1
    # 3) fill remaining slots: own site list first, then any next-stage Digimon
    for k in order:
        for i in pools[k] + rng.sample(nxt_ids, len(nxt_ids)):
            if not free(k): break
            if i not in opts[k]: opts[k].append(i); stats['site' if i in pools[k] else 'random'] += 1
    evo.update(opts)
    assert set(nxt_ids) <= {i for v in opts.values() for i in v}, st

assert len(MAIN) == len([n for n in MAIN if n in by_name]), [n for n in MAIN if n not in by_name]
assert all(len(v) == 3 and len(set(v)) == 3 for v in evo.values())
open(sys.argv[3], 'w', encoding='utf-8').write('window.EVO=' + json.dumps(evo, separators=(',', ':')) + ';\n')
print(len(evo), 'Digimon with 3 options;', stats)
