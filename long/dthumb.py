import sys; sys.path.insert(0,'/home/claude/long')
import doors as D, wd, cairo, math
from pz import hexc
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080); ctx = cairo.Context(surf)
D.corridor(ctx, 1.0, states=('closed','open','closed'), host=False)
ctx.set_source_rgba(0,0,0,0.25); ctx.paint()
for k,x in enumerate(D.DX):
    if k!=1: D.flame(ctx, x-60, 860, 0.9, 1.0, k); D.flame(ctx, x+60, 860, 0.8, 1.0, k+2)
D.quad(ctx, 960, 880, 0.55, 1.0, '#d9a441', head_r=52, mane='#8a4a18', skinny=True)
D.detective(ctx, 230, 1060, 0.85, 1.0, pose='chest')
def big(s, x, y, size, col):
    ctx.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
    e = ctx.text_extents(s); ctx.move_to(x - e[2]/2 - e[0], y); ctx.text_path(s)
    ctx.set_source_rgb(0.04,0.04,0.07); ctx.set_line_width(size*0.17); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*hexc(col)); ctx.fill()
big('WHICH DOOR?', 960, 250, 250, '#ffd23f')
ctx.save(); ctx.translate(1560, 560); ctx.rotate(0.08); wd.pill(ctx, 0, 0, 520, 150, '#e8283c', '99% FAIL', size=100); ctx.restore()
big('10 DEADLY DOORS', 760, 1010, 100, '#ffffff')
surf.write_to_png('out/thumb.png')
from PIL import Image
im = Image.open('out/thumb.png').convert('RGB').resize((1280,720), Image.LANCZOS); im.save('out/ML_Which_Door_Marathon_thumb.jpg', quality=90)
im.resize((320,180)).save('out/thumb_small.png')
