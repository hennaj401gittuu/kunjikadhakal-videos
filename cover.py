"""Midnight Witness Short/Reel cover (1080x1920 JPG).
Reads COVER from script.py in the cwd:
COVER = {"lines": ["HER FITBIT", "KEPT", "COUNTING"],   # 2-3 short lines, huge
         "kicker": "HE SAID SHE WAS DEAD",            # small line above (optional)
         "obj": "watch",                               # evidence object, see OBJS
         "tag": "SOLVED",                              # stamp text (<=10 chars)
         "accent": 0..5 (optional; default = hash of title)}
Writes cover.jpg. Keeps text inside the Instagram grid crop (y 285-1635) and away from the bottom 420 px."""
import cairo, math, os, sys, random, subprocess, hashlib
ENG = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ENG)
from gfx import font, glow, rrect, noise_dots
import scenes2 as s2
exec(open("script.py").read())
CW, CH = 1080, 1920
ACC = [(0.92, 0.12, 0.16), (0.10, 0.75, 0.85), (1.0, 0.68, 0.12), (0.62, 0.35, 0.95), (0.20, 0.85, 0.45), (0.95, 0.35, 0.65)]

def extra_obj(c, kind):
    """objects not in scenes2.obj"""
    if kind == "watch":
        c.set_source_rgb(0.1, 0.1, 0.11); rrect(c, -45, -190, 90, 380, 30); c.fill()
        c.set_source_rgb(0.05, 0.05, 0.06); rrect(c, -95, -110, 190, 220, 40); c.fill()
        c.set_source_rgb(0.15, 0.55, 0.8); rrect(c, -78, -92, 156, 184, 28); c.fill()
        c.set_source_rgb(1, 1, 1); font(c, "Bebas Neue", 70); c.move_to(-60, 10); c.show_text("10:05")
        c.set_line_width(5); c.set_source_rgb(1, 0.3, 0.3); c.move_to(-60, 45)
        for k in range(12): c.line_to(-60 + k * 11, 45 + (-18 if k % 3 == 1 else 0))
        c.stroke()
    elif kind == "ticket":
        c.set_source_rgb(0.97, 0.95, 0.7); c.rectangle(-140, -200, 280, 400); c.fill()
        c.set_source_rgb(0.8, 0.1, 0.1); c.rectangle(-140, -200, 280, 60); c.fill()
        c.set_source_rgb(1, 1, 1); font(c, "Bebas Neue", 46); c.move_to(-120, -155); c.show_text("PARKING VIOLATION")
        c.set_source_rgba(0.2, 0.2, 0.2, 0.7)
        for k in range(9): c.rectangle(-115, -110 + k * 32, random.Random(k).uniform(120, 230), 6); c.fill()
    elif kind == "floppy":
        c.set_source_rgb(0.45, 0.2, 0.6); rrect(c, -160, -160, 320, 320, 12); c.fill()
        c.set_source_rgb(0.75, 0.75, 0.78); c.rectangle(-80, -160, 160, 110); c.fill()
        c.set_source_rgb(0.45, 0.2, 0.6); c.rectangle(10, -145, 40, 80); c.fill()
        c.set_source_rgb(0.95, 0.95, 0.92); c.rectangle(-120, 10, 240, 140); c.fill()
    elif kind == "tattoo":
        c.set_source_rgb(0.72, 0.52, 0.4); c.save(); c.scale(1.2, 1); c.arc(0, 0, 170, 0, 7); c.restore(); c.fill()
        c.set_source_rgba(0.08, 0.1, 0.18, 0.9); c.set_line_width(7)
        c.rectangle(-110, -60, 220, 120); c.stroke(); c.move_to(-110, -60); c.line_to(0, -120); c.line_to(110, -60); c.stroke()
        c.rectangle(-30, 0, 50, 60); c.stroke()
    elif kind == "fingerprint":
        c.set_source_rgba(0.85, 0.85, 0.9, 0.9); c.set_line_width(8)
        for k in range(9):
            c.save(); c.scale(0.8, 1.05); c.arc(0, 10, 30 + k * 20, math.pi * 0.95 + k * 0.05, math.pi * 2.05 + k * 0.08); c.restore(); c.stroke()
    elif kind == "eye":
        c.set_source_rgb(0.92, 0.9, 0.86); c.move_to(-200, 0); c.curve_to(-100, -120, 100, -120, 200, 0); c.curve_to(100, 120, -100, 120, -200, 0); c.fill()
        c.set_source_rgb(0.75, 0.1, 0.12); c.arc(0, 0, 70, 0, 7); c.fill(); c.set_source_rgb(0, 0, 0); c.arc(0, 0, 30, 0, 7); c.fill()
    elif kind == "dna":
        for i in range(16):
            y = -220 + i * 29; ph = i * 0.5
            x1, x2 = 90 * math.sin(ph), 90 * math.sin(ph + math.pi)
            c.set_source_rgba(0.6, 0.85, 1, 0.5); c.set_line_width(4); c.move_to(x1, y); c.line_to(x2, y); c.stroke()
            c.set_source_rgb(0.5, 0.8, 1); c.arc(x1, y, 12, 0, 7); c.fill(); c.set_source_rgb(0.95, 0.2, 0.25); c.arc(x2, y, 12, 0, 7); c.fill()
    elif kind == "house":
        c.set_source_rgb(0.08, 0.08, 0.1); c.rectangle(-170, -40, 340, 220); c.fill(); c.move_to(-200, -40); c.line_to(0, -200); c.line_to(200, -40); c.fill()
        c.set_source_rgb(1, 0.78, 0.4); c.rectangle(-110, 10, 80, 70); c.fill(); c.rectangle(40, 10, 80, 70); c.fill()
    else:
        return False
    return True

OBJS = {"watch", "ticket", "floppy", "tattoo", "fingerprint", "eye", "dna", "house", "hammer", "can", "swab", "tissue", "phone", "letter", "key", "shoe", "flashlight", "mask", "rope", "photo", "car"}

def main():
    C = COVER
    seed = int(hashlib.md5("".join(C["lines"]).encode()).hexdigest(), 16)
    acc = ACC[C.get("accent", seed % len(ACC))]
    rnd = random.Random(seed)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, CW, CH); c = cairo.Context(s)
    # background: deep gradient + accent glow + grain + light rays
    g = cairo.LinearGradient(0, 0, 0, CH); g.add_color_stop_rgb(0, 0.02, 0.02, 0.03); g.add_color_stop_rgb(0.5, acc[0] * 0.18, acc[1] * 0.18, acc[2] * 0.18); g.add_color_stop_rgb(1, 0.01, 0.01, 0.015)
    c.set_source(g); c.paint()
    oy = 1200
    for k in range(14):
        a0 = -math.pi / 2 + (k - 7) * 0.22 + rnd.uniform(-0.05, 0.05)
        c.set_source_rgba(*acc, 0.07); c.move_to(CW / 2, oy); c.arc(CW / 2, oy, 1600, a0 - 0.05, a0 + 0.05); c.close_path(); c.fill()
    glow(c, CW / 2, oy, 520, acc, 0.55)
    noise_dots(c, 2500, CW, CH, (1, 1, 1), 0.02, 0.07, 1.6, seed % 999)
    # object
    obj = C.get("obj", "photo")
    c.save(); c.translate(CW / 2, oy); c.rotate(rnd.uniform(-0.18, 0.18)); c.scale(1.3, 1.3)
    c.push_group()
    if not extra_obj(c, obj): s2.obj(c, obj if obj in OBJS else "photo", 1.0)
    pat = c.pop_group()
    c.save(); c.translate(10, 14); c.set_source_rgba(0, 0, 0, 0.6); c.mask(pat); c.restore()
    c.set_source(pat); c.paint(); c.restore()
    # big question mark behind text? use evidence marker instead
    c.save(); c.translate(CW / 2 + 320, oy + 260); c.set_source_rgb(1, 0.8, 0.1); c.move_to(-60, 50); c.line_to(0, -60); c.line_to(60, 50); c.close_path(); c.fill()
    c.set_source_rgb(0, 0, 0); font(c, "Bebas Neue", 70); c.move_to(-14, 38); c.show_text(str(seed % 9 + 1)); c.restore()
    # text block
    def outlined(txt, y, size, col, maxw=980):
        font(c, "Bebas Neue", size); w = c.text_extents(txt).x_advance
        if w > maxw: size = size * maxw / w; font(c, "Bebas Neue", size); w = c.text_extents(txt).x_advance
        c.move_to(CW / 2 - w / 2, y); c.text_path(txt)
        c.set_source_rgb(0, 0, 0); c.set_line_width(size * 0.12); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
        c.set_source_rgb(*col); c.fill(); return size
    if C.get("kicker"):
        font(c, "Inter", 40, True); kw = c.text_extents(C["kicker"]).x_advance
        c.set_source_rgb(*acc); rrect(c, CW / 2 - kw / 2 - 28, 318, kw + 56, 70, 12); c.fill()
        c.set_source_rgb(1, 1, 1) if sum(acc) < 1.6 else c.set_source_rgb(0.05, 0.05, 0.05)
        c.move_to(CW / 2 - kw / 2, 366); c.show_text(C["kicker"])
    lines = C["lines"][:3]; y = 540
    for i, ln in enumerate(lines):
        col = acc if i == len(lines) - 1 else (1, 1, 1)
        sz = outlined(ln, y, 175 if len(lines) == 3 else 210, col)
        y += sz * 0.95
    # stamp
    tag = C.get("tag", "SOLVED")
    c.save(); c.translate(CW / 2 - 250, 1530); c.rotate(-0.16)
    font(c, "Bebas Neue", 96); tw = c.text_extents(tag).x_advance
    c.set_source_rgba(0.95, 0.15, 0.18, 0.95); c.set_line_width(9); rrect(c, -tw / 2 - 26, -86, tw + 52, 110, 10); c.stroke()
    c.move_to(-tw / 2, 0); c.show_text(tag); c.restore()
    font(c, "Inter", 30, True); t = "MIDNIGHT WITNESS"; w = c.text_extents(t).x_advance
    c.set_source_rgba(1, 1, 1, 0.75); c.move_to(CW / 2 - w / 2, 1625); c.show_text(t)
    s.write_to_png("cover.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "cover.png", "-q:v", "2", "cover.jpg"], check=True)
    print("COVER ok")

if __name__ == "__main__":
    main()
