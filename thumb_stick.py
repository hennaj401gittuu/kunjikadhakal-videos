"""Midnight Witness v3 long-video thumbnail (1280x720) in the stick-figure style.
Reads thumb.json in cwd: {"l1": "RED HOOK", "l2": "WHITE LINE", "l3": "optional", "tag": "<=10 chars",
 "face": "shock|grin|angry|sad|smirk", "pose": "shock|point|cheer|think|shrug", "outfit": "navy|red|...", "hat": null|"top"|"bowler"|"crown"|...,
 "mustache": false, "glasses": false, "hair": null|"dark"|"grey", "prop": "moneybag|bottle|trophy|brick|rocket|...", "bg": [r,g,b] (0-1, optional)}
Writes thumb.png (+ use ffmpeg to make thumb.jpg)."""
import cairo, json, math, os, sys
ENG = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ENG)
from stick import figure, sbox, scircle, label, hatch
from gfx import glow
import stickscene as ss
J = json.load(open("thumb.json"))
TW, TH = 1280, 720
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, TW, TH); c = cairo.Context(s)
bg = tuple(J.get("bg", (0.98, 0.78, 0.2)))
c.set_source_rgb(*bg); c.paint()
for k in range(24):  # sunburst
    a0 = k * math.pi / 12
    c.set_source_rgba(1, 1, 1, 0.18); c.move_to(380, 420); c.arc(380, 420, 1400, a0, a0 + math.pi / 24); c.close_path(); c.fill()
hatch(c, 0, 0, TW, TH, (0, 0, 0), 0.05)
glow(c, 380, 420, 380, (1, 1, 1), 0.35)
# big character, waist-up feel (huge scale, cropped by frame bottom)
figure(c, 360, 1060, 3.1, J.get("pose", "shock"), J.get("face", "shock"), look=J.get("look"), hat=J.get("hat"), outfit=ss.COLORS.get(J.get("outfit", "navy")),
       mustache=J.get("mustache", False), glasses=J.get("glasses", False), hair=J.get("hair"), t=0.5, seed=3)
if J.get("prop"):
    ss.prop(c, J["prop"], 650, 640, 1.5, seed=2, t=0.5)
def big(txt, x, y, size, col, maxw=560):
    c.select_font_face("Bebas Neue"); c.set_font_size(size); w = c.text_extents(txt).x_advance
    if w > maxw: size *= maxw / w; c.set_font_size(size); w = c.text_extents(txt).x_advance
    c.move_to(x - w / 2, y); c.text_path(txt)
    c.set_source_rgb(0, 0, 0); c.set_line_width(size * 0.14); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgb(*col); c.fill()
lines = [J.get("l1", ""), J.get("l2", ""), J.get("l3", "")]
if J.get("question"):  # huge "?" behind the text for mystery thumbnails
    c.select_font_face("Bebas Neue"); c.set_font_size(620); c.move_to(1010, 640); c.text_path("?")
    c.set_source_rgba(0.9, 0.1, 0.12, 0.85); c.fill()
lines = [l for l in lines if l]
y = 200 if len(lines) == 3 else 250
for i, ln in enumerate(lines):
    big(ln, 960, y, 150 if i == 0 else 120, (0.9, 0.1, 0.12) if i == 0 else (1, 1, 1)); y += 150 if i == 0 else 125
if J.get("tag"):
    c.save(); c.translate(1080, 640); c.rotate(-0.08)
    sbox(c, -130, -48, 260, 90, (0.9, 0.12, 0.14), seed=4); label(c, J["tag"], 0, -3, 64, (1, 1, 1)); c.restore()
s.write_to_png("thumb.png")
print("THUMB ok")

# ---------------------------------------------------------------- "history" style (like successful ENTIRE-History channels)
# thumb.json: {"style": "history", "name": "COCA-COLA", "years": "1886 - 2026", "scene": "factory|city|street|shop|town|sea|space|farm|...",
#              "sign": "shop sign text", "face": "smirk", "pose": "stand", "outfit": "black", "hat": ..., "mustache": ..., "hair": ..., "beard": ...,
#              "glasses": ..., "apron": ..., "icon": "bottle|brick|box|rocket|car|phone|moneybag|..."}
if J.get("style") == "history":
    import cairo as _c
    import stickscene as _ss
    from stick import paper as _paper
    W0, H0 = 1920, 1080
    bgs, bc = _c.ImageSurface(_c.FORMAT_ARGB32, W0, H0), None
    bc = _c.Context(bgs)
    _ss.bg_draw(bc, J.get("scene", "city"), 11, J.get("sign"), None)
    # extra busy detail: crowds / props in the background for a rich scene
    for k, kind in enumerate(J.get("scatter", [])[:6]):
        _ss.prop(bc, kind, 900 + (k % 3) * 300, 760 + (k // 3) * 140, 0.8, seed=k, t=0.3)
    out = _c.ImageSurface(_c.FORMAT_ARGB32, TW, TH); c2 = _c.Context(out)
    c2.save(); c2.scale(TW / W0 * 1.05, TH / H0 * 1.05); c2.translate(-40, -20); c2.set_source_surface(bgs, 0, 0); c2.paint(); c2.restore()
    # character on its own layer -> white sticker outline
    fig = _c.ImageSurface(_c.FORMAT_ARGB32, TW, TH); fc = _c.Context(fig)
    figure(fc, 250, 900, 2.35, J.get("pose", "stand"), J.get("face", "smirk"), look=J.get("look"), hat=J.get("hat"), outfit=_ss.COLORS.get(J.get("outfit", "black")),
           mustache=J.get("mustache", False), glasses=J.get("glasses", False), hair=J.get("hair"), beard=J.get("beard", False), t=0.5, seed=7,
           apron=J.get("apron", False))
    for k in range(24):
        a = k * math.pi / 12
        c2.save(); c2.translate(9 * math.cos(a), 9 * math.sin(a)); c2.set_source_rgb(1, 1, 1); c2.mask_surface(fig, 0, 0); c2.restore()
    c2.save(); c2.translate(6, 6); c2.set_source_rgba(0, 0, 0, 0.35); c2.mask_surface(fig, 0, 0); c2.restore()
    c2.set_source_surface(fig, 0, 0); c2.paint()
    def serif(txt, x, y, size, maxw):
        c2.select_font_face("DM Serif Display"); c2.set_font_size(size); w = c2.text_extents(txt).x_advance
        if w > maxw: size *= maxw / w; c2.set_font_size(size); w = c2.text_extents(txt).x_advance
        c2.move_to(x - w / 2, y); c2.text_path(txt)
        c2.set_source_rgb(1, 1, 1); c2.set_line_width(size * 0.2); c2.set_line_join(_c.LINE_JOIN_ROUND); c2.stroke_preserve()
        c2.set_source_rgb(0.07, 0.08, 0.12); c2.fill()
        return w
    w1 = serif(J.get("name", ""), 860, 165, 150, 640)
    serif(J.get("years", ""), 860, 290, 110, 600)
    if J.get("icon"):
        c2.save(); c2.translate(860 + w1 / 2 + 70, 120)
        sbox(c2, -55, -55, 110, 110, (1, 1, 1), seed=2)
        _ss.prop(c2, J["icon"], 0, 45, 0.45, seed=3, t=0.3); c2.restore()
    out.write_to_png("thumb.png")
    print("THUMB history ok")
