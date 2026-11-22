import cairo, math, random, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
TX = json.load(open("thumb.json")) if os.path.exists("thumb.json") else {"l1": "CAUGHT", "l2": "42 YEARS", "l3": "LATER", "tag": "DNA MATCH"}
TW, TH = 1280, 720
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, TW, TH); c = cairo.Context(s)
g = cairo.RadialGradient(360, 380, 40, 360, 380, 900)
g.add_color_stop_rgb(0, 0.32, 0.04, 0.06); g.add_color_stop_rgb(0.45, 0.08, 0.02, 0.03); g.add_color_stop_rgb(1, 0.01, 0.01, 0.01)
c.set_source(g); c.paint()
# faint DNA on right
for i in range(30):
    y = i * 26; ph = i * 0.45
    x1 = 1080 + 70 * math.sin(ph); x2 = 1080 + 70 * math.sin(ph + math.pi)
    c.set_source_rgba(0.5, 0.75, 1, 0.12); c.set_line_width(2); c.move_to(x1, y); c.line_to(x2, y); c.stroke()
    c.set_source_rgba(0.5, 0.75, 1, 0.25); c.arc(x1, y, 5, 0, 7); c.fill(); c.set_source_rgba(*RED, 0.3); c.arc(x2, y, 5, 0, 7); c.fill()
# masked head, big
c.save(); c.translate(330, 400)
glow(c, 0, -40, 380, (0.9, 0.1, 0.12), 0.35)
c.set_source_rgb(0.02, 0.02, 0.025)
c.save(); c.scale(0.86, 1.1); c.arc(0, -60, 210, 0, 7); c.restore(); c.fill()
c.move_to(-330, 330); c.curve_to(-300, 160, -150, 120, 0, 115); c.curve_to(150, 120, 300, 160, 330, 330); c.close_path(); c.fill()
# rim light
c.set_source_rgba(0.9, 0.2, 0.2, 0.6); c.set_line_width(4)
c.save(); c.scale(0.86, 1.1); c.arc(0, -60, 210, -2.6, -1.2); c.restore(); c.stroke()
for ex in (-70, 70):
    c.set_source_rgb(0.75, 0.72, 0.66); c.save(); c.translate(ex, -90); c.scale(1.6, 0.75); c.arc(0, 0, 36, 0, 7); c.restore(); c.fill()
    glow(c, ex, -90, 34, (1, 0.2, 0.2), 0.8)
    c.set_source_rgb(0.05, 0.02, 0.02); c.arc(ex, -90, 17, 0, 7); c.fill()
c.set_source_rgb(0.6, 0.56, 0.5); c.save(); c.translate(0, 45); c.scale(1.4, 0.6); c.arc(0, 0, 38, 0, 7); c.restore(); c.fill()
c.restore()
def big(txt, x, y, size, col, ang=0):
    c.save(); c.translate(x, y); c.rotate(ang)
    font(c, "Bebas Neue", size)
    c.move_to(0, 0); c.text_path(txt)
    c.set_source_rgb(0, 0, 0); c.set_line_width(16); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgb(*col); c.fill(); c.restore()
def fit(txt, size, maxw=600):
    font(c, "Bebas Neue", size)
    w_ = c.text_extents(txt).x_advance
    return size if w_ <= maxw else size * maxw / w_
big(TX["l1"], 650, 300, fit(TX["l1"], 230), (0.95, 0.15, 0.17))
big(TX["l2"], 655, 470, fit(TX["l2"], 170), (1, 1, 1))
big(TX["l3"], 660, 610, fit(TX["l3"], 150), (1, 1, 1))
# DNA match tag
c.save(); c.translate(1120, 70); c.rotate(0.08)
c.set_source_rgb(0.95, 0.15, 0.17); rrect(c, -150, -48, 300, 96, 10); c.fill()
font(c, "Bebas Neue", 70); tw = c.text_extents(TX["tag"]).x_advance
c.set_source_rgb(1, 1, 1); c.move_to(-tw / 2, 24); c.show_text(TX["tag"]); c.restore()
s.write_to_png("thumb.png")
