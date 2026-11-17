# Cuts the 8 Omnimon poses (with their baked-in effects) out of the user's All Delete pose guide.
# Usage: python -I tools/mkomniposes.py tools/src/alldelete-poses.jpg vfx/omnimon-poses.png [preview.png]
# Output: one row of 8 frames, PW x PH px, Omnimon facing right, feet at (PW/2, FEET) in every frame.
# The flat green panel, its darker shadow ellipse and the dashed guide line are keyed out
# (green-dominant and not bright). Bright greens (eyes, code rain) stay.
import sys
from PIL import Image

K = 0.3                                   # panel px -> frame px
XS = [(89, 531), (566, 1008), (1042, 1484), (1518, 1960)]
YS = [(70, 545), (822, 1295)]
PANEL_FEET = 0.93                         # feet line as a fraction of panel height (shadow centre)
PW, PH = round(442 * K), round(475 * K)
FEET = round(475 * PANEL_FEET * K)

src = Image.open(sys.argv[1]).convert('RGB')
out = Image.new('RGBA', (PW * 8, PH), (0, 0, 0, 0))
for i in range(8):
    (x0, x1), (y0, y1) = XS[i % 4], YS[i // 4]
    cell = src.crop((x0, y0, x1, y1))
    if i < 4:  # top-row panels have their "F1".."F4" label painted inside the top-left corner
        cell.paste((65, 115, 60), (0, 0, 75, 60))
    cell = cell.resize((PW, PH), Image.LANCZOS).convert('RGBA')
    cp = cell.load()
    for y in range(PH):
        for x in range(PW):
            r, g, b, _ = cp[x, y]
            bg = g > r + 18 and g > b + 18 and g < 165
            if i == 4 and y > PH * 0.8:  # F5's black "DELETE 101" strip along the bottom: drop its black and green
                bg = bg or max(r, g, b) < 70 or (g > r + 18 and g > b + 18)
            cp[x, y] = (r, g, b, 0 if bg else 255)
    out.paste(cell, (i * PW, 0))
out.save(sys.argv[2])
if len(sys.argv) > 3:
    pv = Image.new('RGBA', out.size, (90, 90, 110, 255)); pv.alpha_composite(out)
    pv.resize((out.width * 2, out.height * 2), Image.NEAREST).save(sys.argv[3])
print('saved', out.size, 'frame', PW, PH, 'feet y', FEET)
