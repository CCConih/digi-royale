# Cuts the "Digital Skills Animation Frames" sheet into a transparent atlas for the game.
# Usage: python -I tools/mkskills.py <sheet.jpg> vfx/skills.png [preview.png]
# Output: 7 rows (fireball, fist, ice, bolt, vine, portal, barrier) x 7 frames, each CW x CH px.
# Each cell's corner brackets are found from bright pixels, cropped away, and the dark grid
# background is keyed to transparent by colour distance (the sheet is a JPG, no alpha).
import sys
from PIL import Image

CW, CH = 64, 52
ROWS = [(168, 278), (293, 404), (421, 528), (546, 659), (677, 786), (801, 915), (929, 1056)]  # cell bands (y)
COLS = [(392, 540), (607, 770), (833, 1002), (1061, 1232), (1294, 1464), (1522, 1690), (1759, 1908)]  # generous x

src = Image.open(sys.argv[1]).convert('RGB')
px = src.load()
BG = px[580, 220]  # empty grid between cells

def bright(x, y):
    return max(px[x, y]) > 110

out = Image.new('RGBA', (CW * 7, CH * 7), (0, 0, 0, 0))
for r, (y0, y1) in enumerate(ROWS):
    for c, (x0, x1) in enumerate(COLS):
        xs = [x for x in range(x0, x1) if any(bright(x, y) for y in range(y0 - 6, y1 + 6, 2))]
        ys = [y for y in range(y0 - 6, y1 + 6) if any(bright(x, y) for x in range(x0, x1, 2))]
        bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)  # bracket box
        box = (bx0 + 12, by0 + 12, bx1 - 11, by1 - 11)               # inside the brackets
        cell = src.crop(box).resize((CW, CH), Image.LANCZOS).convert('RGBA')
        cp = cell.load()
        for y in range(CH):
            for x in range(CW):
                p = cp[x, y]
                v, s = max(p[:3]), max(p[:3]) - min(p[:3])
                score = max(v - 72, s * 3 // 2 - 42)  # bg/grid: dark and grey; effects: bright or saturated
                a = max(0, min(255, score * 255 // 40))
                cp[x, y] = (p[0], p[1], p[2], a)
        out.paste(cell, (c * CW, r * CH))
out.save(sys.argv[2])
if len(sys.argv) > 3:  # preview on arena-green, 3x
    bgc = Image.new('RGBA', out.size, (60, 122, 58, 255)); bgc.alpha_composite(out)
    bgc.resize((out.width * 3, out.height * 3), Image.NEAREST).save(sys.argv[3])
print('saved', out.size)
