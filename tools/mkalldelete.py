# Cuts the user's "Omegamon All Delete skill FX" sheet into 8 transparent frames for Omnimon's ultimate.
# Usage: python -I tools/mkalldelete.py tools/src/alldelete-fx.jpg vfx/alldelete.png [preview.png]
# Output: one row of 8 frames, FW x FH px: F1 charge, F2 vortex, F3 slash, F4 data impact,
# F5 trigger, F6 cascade, F7 void collapse, F8 dissolution. The dark-blue grid background is keyed
# out by brightness (grid lines stay under ~85, effects are bright).
import sys
from PIL import Image

FW, FH = 160, 112
BOXES = [(62, 140, 490, 458), (515, 140, 965, 458), (1010, 140, 1490, 458), (1505, 140, 1938, 458),  # panel art, labels excluded
         (90, 632, 530, 912), (535, 632, 985, 912), (1005, 632, 1455, 912), (1470, 632, 1910, 912)]

src = Image.open(sys.argv[1]).convert('RGB')
out = Image.new('RGBA', (FW * len(BOXES), FH), (0, 0, 0, 0))
for i, box in enumerate(BOXES):
    cell = src.crop(box)
    k = min(FW / cell.width, FH / cell.height)
    cell = cell.resize((round(cell.width * k), round(cell.height * k)), Image.LANCZOS).convert('RGBA')
    cp = cell.load()
    for y in range(cell.height):
        for x in range(cell.width):
            p = cp[x, y]
            v = max(p[:3])
            a = max(0, min(255, (v - 85) * 255 // 60))
            cp[x, y] = (p[0], p[1], p[2], a)
    out.paste(cell, (i * FW + (FW - cell.width) // 2, (FH - cell.height) // 2))
out.save(sys.argv[2])
if len(sys.argv) > 3:
    bg = Image.new('RGBA', out.size, (60, 122, 58, 255)); bg.alpha_composite(out)
    bg.resize((out.width * 2, out.height * 2), Image.NEAREST).save(sys.argv[3])
print('saved', out.size)
