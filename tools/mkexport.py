# Exports every Digimon's sprite poses + ultimate info into a working folder, plus a data spreadsheet.
# Usage: python -I tools/mkexport.py <out dir>      (run from the repo root)
# Out:   <out>/sprites/<N_Stage>/<dex>_<Name>/{map,battle,attack,hit}.png, sheet.png, info.txt
#        <out>/Digimon_Data.xlsx   (sheet "Digimon": one row per Digimon with a thumbnail; sheet "Legend")
# Mirrors the game's rules in index.html: STAGE_HEIGHT sizing, skillOf() effect choice, Omnimon's All Delete.
import json, os, re, sys
from PIL import Image
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

OUT = sys.argv[1]
roster = json.loads(re.search(r'window\.ROSTER=(\[.*\]);', open('roster.js', encoding='utf-8').read(), re.S)[1])
techs = json.load(open('vfx/techs.json', encoding='utf-8'))
src = open('index.html', encoding='utf-8').read()
STAGE_HEIGHT = {int(k): int(v) for k, v in re.findall(r'(\d+):\s*(\d+)', re.search(r'STAGE_HEIGHT\s*=\s*\{([^}]*)\}', src)[1])}
STAGES = {0: 'Baby', 1: 'In-Training', 2: 'Rookie', 3: 'Champion', 4: 'Ultimate', 5: 'Mega'}
POSES = ['map', 'battle', 'attack', 'hit']
CLOSE = {'melee', 'dash', 'cone', 'aura', 'orbit', 'nova'}
SKILL_NAMES = {'fireball': 'Fireball', 'fist': 'Burning Fist', 'ice': 'Ice Shards', 'bolt': 'Lightning Bolt',
               'vine': 'Thorn Vine', 'portal': 'Dark Portal'}

def skill_of(t, kind):  # same rule as skillOf() in index.html
    if t == 'fire': return 'fist' if kind in CLOSE else 'fireball'
    return {'ice': 'ice', 'water': 'ice', 'electric': 'bolt', 'grass': 'vine', 'ground': 'vine', 'dark': 'portal', 'poison': 'portal'}.get(t)

def role(a):
    return 'Ranged' if a == 'Data' else 'Ranged or melee (50/50 per round)' if a in ('Free', 'Unknown') else 'Melee'

rows = []
for d in sorted(roster, key=lambda d: (d['st'], d['id'])):
    t = techs[str(d['id'])]
    omni = d['n'] == 'Omnimon'
    ult = 'All Delete' if omni else d['u']
    kind = 'alldelete' if omni else t['kind']
    sk = None if omni else skill_of(d['t'], kind)
    if omni: effect, source = 'All Delete: charge, slash, ALL DELETE burst, code cascade (+ 8 custom poses)', 'Custom (vfx/alldelete.png, vfx/omnimon-poses.png)'
    elif sk: effect, source = SKILL_NAMES[sk], 'Skill sheet (vfx/skills.png)'
    else:
        shapes = ', '.join(dict.fromkeys(s for s in (t.get('proj'), t.get('melee'), t.get('beam')) if s))
        effect, source = f"{shapes} ({t['pal']} palette)", 'Site VFX (vfx/atlas.png)'
    stage_dir = f"{d['st']}_{STAGES[d['st']]}"
    folder = f"{d['id']:04d}_{re.sub(r'[^A-Za-z0-9()\-]+', '_', d['n']).strip('_')}"
    rel = f"sprites/{stage_dir}/{folder}"
    os.makedirs(os.path.join(OUT, rel), exist_ok=True)
    sheet = Image.open(d['s']).convert('RGBA')
    sheet.save(os.path.join(OUT, rel, 'sheet.png'))
    sizes = {}
    for p in POSES:
        if p in d['f']:
            x, y, w, h = d['f'][p][:4]
            sheet.crop((x, y, x + w, y + h)).save(os.path.join(OUT, rel, f'{p}.png'))
            sizes[p] = (w, h)
    base = d['f'].get('map') or d['f']['battle']
    info = [f"Name: {d['n']}", f"Dex: {d['id']}", f"Stage: {STAGES[d['st']]}", f"Element: {d['t']}", f"Attribute: {d['a']}",
            f"Ultimate attack: {ult}", f"Archetype: {kind}", f"Attack effect: {effect}", f"Effect source: {source}",
            f"Role: {role(d['a'])}", f"Flying: {'yes' if d['fly'] else 'no'}"]
    info += [f"{p} pose: {sizes[p][0]}x{sizes[p][1]} px, feet anchor ({d['f'][p][4]}, {d['f'][p][5]})" for p in POSES if p in sizes]
    info += [f"{p} pose: missing" for p in POSES if p not in sizes]
    open(os.path.join(OUT, rel, 'info.txt'), 'w', encoding='utf-8').write('\n'.join(info) + '\n')
    rows.append(dict(d=d, ult=ult, kind=kind, effect=effect, source=source, sizes=sizes, base=base, rel=rel))

# ---- spreadsheet ----
wb = Workbook()
ws = wb.active; ws.title = 'Digimon'
lg = wb.create_sheet('Legend')
F = Font(name='Arial', size=10); FB = Font(name='Arial', size=10, bold=True, color='FFFFFF'); HEAD = PatternFill('solid', start_color='1F2A37')
cols = ['Sprite', 'Dex', 'Name', 'Stage', 'Element', 'Attribute', 'Ultimate Attack', 'Archetype', 'Attack Effect', 'Effect Source',
        'Role', 'Flying', 'Map W (px)', 'Map H (px)', 'Battle (px)', 'Attack (px)', 'Hit (px)', 'Missing Poses',
        'In-game H (px)', 'In-game W (px)', 'Folder']
widths = [9, 6, 26, 11, 10, 10, 28, 11, 44, 30, 18, 7, 9, 9, 11, 11, 11, 13, 11, 11, 44]
for i, (c, w) in enumerate(zip(cols, widths), 1):
    cell = ws.cell(1, i, c); cell.font = FB; cell.fill = HEAD; cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[1].height = 30
thumbs = os.path.join(OUT, '_thumbs'); os.makedirs(thumbs, exist_ok=True)
for r, row in enumerate(rows, 2):
    d, s = row['d'], row['sizes']
    fmt = lambda p: f'{s[p][0]}x{s[p][1]}' if p in s else '-'
    vals = [None, d['id'], d['n'], STAGES[d['st']], d['t'], d['a'], row['ult'], row['kind'], row['effect'], row['source'],
            role(d['a']), 'yes' if d['fly'] else 'no', row['base'][2], row['base'][3], fmt('battle'), fmt('attack'), fmt('hit'),
            ', '.join(p for p in POSES if p not in s) or '-',
            f'=IFERROR(INDEX(Legend!$B$4:$B$7,MATCH(D{r},Legend!$A$4:$A$7,0)),"-")',
            f'=IF(ISNUMBER(S{r}),ROUND(M{r}*S{r}/N{r},0),"-")', row['rel']]
    for c, v in enumerate(vals, 1):
        cell = ws.cell(r, c, v); cell.font = F; cell.alignment = Alignment(vertical='center', wrap_text=c in (9, 10))
    ws.cell(r, 21).hyperlink = row['rel'].replace('/', '\\'); ws.cell(r, 21).font = Font(name='Arial', size=10, color='0563C1', underline='single')
    ws.row_dimensions[r].height = 44
    # thumbnail: the map pose (or battle) scaled to fit ~52 px tall, crisp
    x, y, w, h = row['base'][:4]
    im = Image.open(d['s']).convert('RGBA').crop((x, y, x + w, y + h))
    k = max(1, 52 // h) if h <= 52 else 52 / h
    im = im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.NEAREST)
    tp = os.path.join(thumbs, f"{d['id']:04d}.png"); im.save(tp)
    xi = XLImage(tp); ws.add_image(xi, f'A{r}')
ws.freeze_panes = 'D2'
ws.auto_filter.ref = f'A1:{get_column_letter(len(cols))}{len(rows) + 1}'

lg.column_dimensions['A'].width = 22; lg.column_dimensions['B'].width = 100
L = [('Digi Royale: Digimon data', None), (None, None), ('Stage', 'In-game height (px), STAGE_HEIGHT in index.html: edit here to try other sizes; the Digimon sheet recalculates')]
L += [(STAGES[k], STAGE_HEIGHT[k]) for k in (2, 3, 4, 5)]
L += [(None, None), ('Column', 'Meaning'),
      ('Ultimate Attack', "Signature technique from digisurvivor.com's G.DEX (roster.js field u). Omnimon is overridden to All Delete."),
      ('Archetype', 'How the ultimate behaves: projectile, melee, beam, dash, cone, chain, nova, aura, orbit, meteor, boomerang (alldelete = Omnimon only).'),
      ('Attack Effect', 'What the game draws. Skill sheet: fire = Fireball (Burning Fist for melee/dash/cone/aura/orbit/nova), ice & water = Ice Shards, electric = Lightning Bolt, grass & ground = Thorn Vine, dark & poison = Dark Portal. Other elements: the site VFX shapes and palette.'),
      ('Role', 'Normal attacks: Data attribute = ranged, Free/Unknown = 50% chance each round, others melee.'),
      ('Map/Battle/Attack/Hit (px)', 'Native size of each pose in the sprite sheet. Map is the small pose used on the field; the game shrinks the others to map size.'),
      ('In-game H / W (px)', 'Formula: height from the Stage table above; width = Map W x In-game H / Map H. Baby and In-Training never fight, so "-".'),
      ('Folder', 'sprites/<stage>/<dex>_<name>/ holds sheet.png (all poses in one row), map/battle/attack/hit.png, and info.txt.'),
      (None, None), ('Note', 'Sprites are Bandai Digimon art (via Wikimon) from digisurvivor.com: reference and prototyping only, do not publish or sell.')]
for r, (a, b) in enumerate(L, 1):
    if a is not None: lg.cell(r, 1, a).font = Font(name='Arial', size=10, bold=r in (1, 3, 9))
    if b is not None:
        c = lg.cell(r, 2, b); c.font = Font(name='Arial', size=10, bold=r in (3, 9), color='0000FF' if isinstance(b, int) else None)
        c.alignment = Alignment(wrap_text=True, vertical='top')
lg.cell(1, 1).font = Font(name='Arial', size=13, bold=True)
wb.calculation.fullCalcOnLoad = True
xlsx = os.path.join(OUT, 'Digimon_Data.xlsx'); wb.save(xlsx)
import shutil; shutil.rmtree(thumbs)  # thumbnails are embedded in the xlsx now
print(len(rows), 'Digimon exported to', OUT)
