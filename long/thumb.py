import sys; sys.path.insert(0,'/home/claude/long')
import longvid as L, wd, cairo, math
from pz import hexc
c = L.cases.CASES[0]
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080); ctx = cairo.Context(surf)
L.stage(ctx, 1.0, cone=(380, 960, 1540))
for x, q in zip((380, 960, 1540), L.cases.CASES[8]['sus']):
    wd.suspect(ctx, x, 1000, 0.95, q[4], 1.0, cap=q[5], mood='sus', stache=True)
    wd.text(ctx, '?', x, 470, 200, '#ffd23f')
def big(s, x, y, size, col):
    ctx.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
    e = ctx.text_extents(s); x0 = x - e[2]/2 - e[0]
    ctx.move_to(x0, y); ctx.text_path(s); ctx.set_source_rgb(0.05,0.05,0.08); ctx.set_line_width(size*0.16); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*hexc(col)); ctx.fill()
big('WHO DID IT?', 960, 260, 230, '#ffd23f')
ctx.save(); ctx.translate(560, 820); ctx.rotate(-0.06); wd.pill(ctx, 0, 0, 760, 190, '#e8283c', '99% FAIL', size=130); ctx.restore()
big('9 MYSTERIES', 560, 1020, 110, '#ffffff')
surf.write_to_png('out/thumb.png')
