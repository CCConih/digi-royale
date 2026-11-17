# Cuts the user's per-Digimon animation sheets into transparent strips for the game.
# Usage: python -I tools/mkguide.py <job> <src.jpg> <out.png> [preview.png]
#   gabumon-poses  tools/src/gabumon-poses.jpg -> vfx/gabumon-poses.png   8 poses, facing right, feet at FEET
#   special-fx     tools/src/special-fx.jpg    -> vfx/special-fx.png      3 rows x 8 frames:
#                  row 0 Scissors Execution, row 1 Petit Fire (cone), row 2 Lullaby Bubble
#   basic-vfx      tools/src/basic-vfx.jpg     -> vfx/basic-vfx.png       10 element rows x [projectile, melee]
# Both sheets sit on a dark navy grid. Poses keep black outlines (bg = dark AND bluish), and drop
# the khaki ground shadow; effects are keyed by brightness (they are all bright).
import sys
from PIL import Image

job, src_path, out_path = sys.argv[1:4]
src = Image.open(src_path).convert('RGB')

def key_pose(p, low):
    r, g, b = p[:3]; mx, mn = max(r, g, b), min(r, g, b)
    bg = mx <= 130 and b > r + 15                                    # navy panel + grid lines, not black outlines
    shadow = low and r >= b and mx - mn < 55 and 60 <= mx <= 175      # khaki ground ellipse under the feet
    return 0 if bg or shadow else 255

def key_fx(p, low):
    return max(0, min(255, (max(p[:3]) - 85) * 255 // 60))

def key_near_bg(p, low):  # by distance from the navy and its grid lines: keeps near-black (dark slash) and browns
    d = min(max(abs(p[0] - c[0]), abs(p[1] - c[1]), abs(p[2] - c[2])) for c in ((25, 35, 55), (50, 60, 82)))
    return max(0, min(255, (d - 14) * 255 // 22))

if job == 'gabumon-poses':
    XS = [(62, 488), (545, 971), (1029, 1455), (1512, 1938)]        # inside each panel's border
    YS = [(150, 508), (608, 966)]
    K, key, rows = 0.3, key_pose, [[(x, y) for y in YS for x in XS]]
    LABEL = (110, 66)                                                # "F1".."F8" tab in the top-left corner
elif job == 'special-fx':
    XS = [(204, 396), (427, 619), (650, 842), (873, 1066), (1097, 1291), (1322, 1516), (1547, 1741), (1772, 1964)]
    YS = [(156, 357), (466, 667), (778, 979)]
    K, key, rows = 0.5, key_fx, [[(x, y) for x in XS] for y in YS]
    LABEL = None
elif job == 'basic-vfx':  # 10 rows (fire, water, ice, electric, grass, earth, wind, steel, light, dark) x [projectile, melee]
    XS = [(660, 990), (1415, 1745)]
    YS = [(round(180 + i * 82.8) + 3, round(180 + i * 82.8) + 80) for i in range(10)]  # inside the row separators
    K, key, rows = 0.34, key_near_bg, [[(x, y) for x in XS] for y in YS]
    LABEL = None
else:
    sys.exit('unknown job ' + job)

cw = round((rows[0][0][0][1] - rows[0][0][0][0]) * K); ch = round((rows[0][0][1][1] - rows[0][0][1][0]) * K)
out = Image.new('RGBA', (cw * len(rows[0]), ch * len(rows)), (0, 0, 0, 0))
for ri, row in enumerate(rows):
    for ci, ((x0, x1), (y0, y1)) in enumerate(row):
        cell = src.crop((x0, y0, x1, y1))
        if LABEL: cell.paste(cell.getpixel((LABEL[0] + 20, 8)), (0, 0) + LABEL)
        cell = cell.resize((cw, ch), Image.LANCZOS).convert('RGBA')
        cp = cell.load()
        for y in range(ch):
            for x in range(cw):
                p = cp[x, y]; cp[x, y] = p[:3] + (key(p, y > ch * 0.78),)
        out.paste(cell, (ci * cw, ri * ch))
out.save(out_path)
if len(sys.argv) > 4:
    pv = Image.new('RGBA', out.size, (60, 122, 58, 255)); pv.alpha_composite(out)
    pv.resize((out.width * 2, out.height * 2), Image.NEAREST).save(sys.argv[4])
print(job, 'saved', out.size, 'cell', cw, ch)
