import sys; sys.path.insert(0,'/home/claude/money')
import money as M, cairo, math
from wd import text_w
W,H=1920,1080
surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
st=M.SL[-1]
ctx.set_source_surface(M.street_bg(st['shops'],8)); ctx.paint(); M.clouds(ctx,0)
ctx.set_source_rgba(0.05,0.03,0.1,0.35); ctx.paint()
M.person(ctx,300,1040,1.35,'#34495e','#f4f1e8',False,0.6,0.0,1,None,0)
M.person(ctx,1400,1040,1.35,'#27ae60','#f4f1e8',False,0.0,0.8,-1,None,0)
M.note(ctx,980,760,'₹100',2.2,-0.15)
for qx,qy in ((760,700),(1210,720)): 
    ctx.save(); ctx.translate(qx,qy); M.text(ctx,'?',0,0,200,'#ffd23f'); ctx.restore()
def big(s,x,y,size,col):
    ctx.select_font_face('Poppins',0,1); ctx.set_font_size(size)
    xb,yb,w,h,xa,ya=ctx.text_extents(s); ctx.move_to(x-w/2-xb,y); ctx.text_path(s)
    ctx.set_source_rgba(0.08,0.05,0.12,1); ctx.set_line_width(size*0.16); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*M.hexc(col)); ctx.fill()
big('WHERE IS ₹100?',W/2,260,190,'#ffd23f')
big('99% FAIL',W/2,500,170,'#ffffff')
surf.write_to_png('out/thumb.png')
