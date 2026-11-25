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
figure(c, 360, 1060, 3.1, J.get("pose", "shock"), J.get("face", "shock"), hat=J.get("hat"), outfit=ss.COLORS.get(J.get("outfit", "navy")),
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
