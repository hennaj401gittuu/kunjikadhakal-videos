import cairo, math, random
from gfx import *

# ---------------- helpers for static backdrops ----------------
def sky(ctx, w, h, day=False, seed=0):
    g = cairo.LinearGradient(0, 0, 0, h)
    if day:
        g.add_color_stop_rgb(0, 0.20, 0.24, 0.30); g.add_color_stop_rgb(0.7, 0.36, 0.38, 0.40); g.add_color_stop_rgb(1, 0.30, 0.30, 0.30)
    else:
        g.add_color_stop_rgb(0, 0.02, 0.03, 0.07); g.add_color_stop_rgb(0.65, 0.07, 0.09, 0.15); g.add_color_stop_rgb(1, 0.10, 0.10, 0.13)
    ctx.set_source(g); ctx.paint()
    if not day:
        noise_dots(ctx, 260, w, h * 0.55, (1, 1, 1), 0.15, 0.8, 1.6, seed)
        glow(ctx, w * 0.78, h * 0.2, 260, MOON, 0.25)
        ctx.set_source_rgb(0.86, 0.89, 0.93); ctx.arc(w * 0.78, h * 0.2, 62, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgba(0.6, 0.64, 0.7, 0.35); ctx.arc(w * 0.77, h * 0.19, 14, 0, 7); ctx.fill(); ctx.arc(w * 0.795, h * 0.22, 9, 0, 7); ctx.fill()

def tree_sil(ctx, x, base, hgt, col, rnd):
    ctx.set_source_rgb(*col)
    ctx.rectangle(x - 7, base - hgt * 0.35, 14, hgt * 0.35); ctx.fill()
    for _ in range(14):
        r = rnd.uniform(hgt * 0.15, hgt * 0.28)
        ctx.arc(x + rnd.uniform(-hgt * 0.22, hgt * 0.22), base - hgt * 0.35 - rnd.uniform(0, hgt * 0.5), r, 0, 7); ctx.fill()

def house_row(ctx, w, h, day=False, seed=3):
    rnd = random.Random(seed)
    ground = h * 0.80
    col = (0.05, 0.055, 0.07) if not day else (0.16, 0.17, 0.19)
    # far trees
    for i in range(18):
        tree_sil(ctx, rnd.uniform(0, w), ground - 40, rnd.uniform(160, 300), (0.04, 0.05, 0.07) if not day else (0.22, 0.24, 0.26), rnd)
    x = -80
    while x < w:
        hw = rnd.uniform(380, 520); hh = rnd.uniform(170, 230)
        ctx.set_source_rgb(*col)
        ctx.rectangle(x, ground - hh, hw, hh); ctx.fill()
        ctx.move_to(x - 30, ground - hh); ctx.line_to(x + hw * 0.5, ground - hh - rnd.uniform(110, 160)); ctx.line_to(x + hw + 30, ground - hh); ctx.close_path(); ctx.fill()
        # garage
        ctx.set_source_rgb(col[0] * 1.6, col[1] * 1.6, col[2] * 1.6)
        ctx.rectangle(x + hw * 0.55, ground - 110, hw * 0.36, 110); ctx.fill()
        # windows
        for k in range(2):
            wx = x + 40 + k * 110; wy = ground - hh + 50
            lit = rnd.random() < (0.55 if not day else 0.2)
            if lit:
                glow(ctx, wx + 35, wy + 30, 90, (1.0, 0.78, 0.45), 0.25 if not day else 0.1)
                ctx.set_source_rgb(0.95, 0.72, 0.38) if not day else ctx.set_source_rgb(0.55, 0.55, 0.5)
            else:
                ctx.set_source_rgb(0.08, 0.09, 0.12) if not day else ctx.set_source_rgb(0.12, 0.13, 0.15)
            ctx.rectangle(wx, wy, 70, 62); ctx.fill()
            ctx.set_source_rgb(*col); ctx.rectangle(wx + 33, wy, 4, 62); ctx.fill(); ctx.rectangle(wx, wy + 29, 70, 4); ctx.fill()
        x += hw + rnd.uniform(140, 240)
    # lawn
    g = cairo.LinearGradient(0, ground, 0, h)
    if day:
        g.add_color_stop_rgb(0, 0.14, 0.17, 0.13); g.add_color_stop_rgb(1, 0.06, 0.07, 0.06)
    else:
        g.add_color_stop_rgb(0, 0.04, 0.06, 0.05); g.add_color_stop_rgb(1, 0.01, 0.01, 0.015)
    ctx.set_source(g); ctx.rectangle(0, ground, w, h - ground); ctx.fill()
    # streetlight
    lx = w * 0.18
    if not day: glow(ctx, lx + 60, ground - 420, 320, (1.0, 0.8, 0.5), 0.35)
    ctx.set_source_rgb(0.02, 0.02, 0.03); ctx.rectangle(lx, ground - 420, 10, 420 + 40); ctx.fill()
    ctx.rectangle(lx, ground - 420, 80, 8); ctx.fill()
    ctx.set_source_rgb(1, 0.85, 0.6) if not day else ctx.set_source_rgb(0.4, 0.4, 0.4)
    ctx.rectangle(lx + 55, ground - 412, 34, 10); ctx.fill()
    # fence
    ctx.set_source_rgb(0.02, 0.02, 0.025)
    for fx in range(0, int(w), 26):
        ctx.rectangle(fx, h - 130, 18, 130); ctx.fill()
    ctx.rectangle(0, h - 110, w, 10); ctx.fill()

def man_sil(ctx, x, y, s, col=(0, 0, 0), a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_source_rgba(*col, a)
    ctx.arc(0, -170, 30, 0, 7); ctx.fill()                     # head (masked)
    ctx.move_to(-48, -135); ctx.curve_to(-60, -60, -55, 0, -40, 0); ctx.line_to(40, 0); ctx.curve_to(55, 0, 60, -60, 48, -135); ctx.close_path(); ctx.fill()
    ctx.rectangle(-36, 0, 28, 120); ctx.fill(); ctx.rectangle(8, 0, 28, 120); ctx.fill()
    ctx.restore()

# ---------------- scenes ----------------
class Scene:
    def __init__(self, p, D, idx): self.p, self.D, self.idx = p, D, idx; self.prep()
    def prep(self): pass

class House(Scene):
    def prep(self):
        s, c = surface(2200, 1238)
        sky(c, 2200, 1238, self.p.get("day", False), self.idx)
        house_row(c, 2200, 1238, self.p.get("day", False), self.idx + 7)
        self.bg = s
    def frame(self, ctx, t):
        u = t / self.D
        blit(ctx, self.bg, 1.0 + 0.07 * u, ox=-40 * u + (self.idx % 2) * 60, oy=10 * u)
        if self.p.get("figure"):
            man_sil(ctx, 1180, 930, 2.2, (0, 0, 0), ease((t - 1.0) / 2.0))
        if self.p.get("beam"):
            ang = -0.35 + 0.6 * math.sin(t * 0.6)
            ctx.save(); ctx.translate(980, 820); ctx.rotate(ang)
            g = cairo.LinearGradient(0, 0, 0, -700)
            g.add_color_stop_rgba(0, 1, 1, 0.9, 0.55); g.add_color_stop_rgba(1, 1, 1, 0.9, 0)
            ctx.set_source(g); ctx.move_to(-10, 0); ctx.line_to(-170, -700); ctx.line_to(170, -700); ctx.line_to(10, 0); ctx.fill(); ctx.restore()
        caption_bar(ctx, self.p.get("caption", ""), u)

class Surveil(Scene):
    def prep(self):
        s, c = surface(2200, 1238)
        sky(c, 2200, 1238, False, self.idx); house_row(c, 2200, 1238, False, self.idx + 11)
        # car silhouette
        c.set_source_rgb(0.01, 0.01, 0.015)
        c.move_to(300, 1100); c.line_to(330, 1010); c.line_to(470, 960); c.line_to(700, 960); c.line_to(820, 1010); c.line_to(900, 1030); c.line_to(900, 1100); c.close_path(); c.fill()
        self.bg = s
    def frame(self, ctx, t):
        u = t / self.D
        blit(ctx, self.bg, 1.25 + 0.05 * math.sin(t * 0.4), ox=60 * math.sin(t * 0.25), oy=20 * math.sin(t * 0.33))
        # green night-vision tint
        ctx.set_source_rgba(0.1, 0.35, 0.18, 0.28); ctx.set_operator(cairo.OPERATOR_OVERLAY); ctx.paint(); ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_rgba(0.85, 1, 0.85, 0.9); ctx.set_line_width(5)
        L = 70; m = 70
        for (x, y, dx, dy) in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
            ctx.move_to(x, y + dy * L); ctx.line_to(x, y); ctx.line_to(x + dx * L, y); ctx.stroke()
        ctx.set_line_width(2); ctx.move_to(W / 2 - 40, H / 2); ctx.line_to(W / 2 + 40, H / 2); ctx.move_to(W / 2, H / 2 - 40); ctx.line_to(W / 2, H / 2 + 40); ctx.stroke()
        if int(t * 2) % 2 == 0:
            ctx.set_source_rgb(*RED); ctx.arc(m + 40, m + 60, 13, 0, 7); ctx.fill()
        text(ctx, "REC", m + 64, m + 74, "Inter", 36, (0.9, 1, 0.9), bold=True)
        sec = int(t) % 60
        text(ctx, "CAM 02   00:%02d:%02d" % (int(t) // 60, sec), W - m - 30, m + 74, "Special Elite", 34, (0.9, 1, 0.9), align="r")
        st = self.p.get("stamp", "")
        if st:
            text(ctx, typed(st, u * 2.5), m + 30, H - m - 40, "Special Elite", 40, (0.9, 1, 0.9))

class Quote(Scene):
    def frame(self, ctx, t):
        u = t / self.D
        radial_bg(ctx, (0.09, 0.07, 0.08), (0.01, 0.01, 0.015))
        q = self.p.get("q", ""); who = self.p.get("who", "")
        size = 92 if len(q) < 30 else 76
        lines = wrap(ctx, q, 1250, "Bebas Neue", size)
        a = ease(t / 0.8)
        sc = 1.0 + 0.04 * u
        ctx.save(); ctx.translate(W / 2, H / 2 - 40); ctx.scale(sc, sc)
        y0 = -(len(lines) - 1) * size * 1.05 / 2
        for i, ln in enumerate(lines):
            text(ctx, ln, 0, y0 + i * size * 1.05 + size * 0.35, "Bebas Neue", size, PAPER, a, "c", spacing=3)
        ctx.restore()
        lw = 520 * ease((t - 0.4) / 1.0)
        ctx.set_source_rgba(*RED, a); ctx.rectangle(W / 2 - lw / 2, H / 2 + len(lines) * size * 0.55 + 10, lw, 6); ctx.fill()
        if who:
            text(ctx, who, W / 2, H / 2 + len(lines) * size * 0.55 + 80, "Inter", 30, (0.7, 0.7, 0.72), ease((t - 1.0) / 0.8), "c", spacing=4)

class Stats(Scene):
    def frame(self, ctx, t):
        radial_bg(ctx, (0.08, 0.06, 0.07), (0.01, 0.01, 0.015))
        items = self.p["items"]; n = len(items)
        for i, (num, lab) in enumerate(items):
            x = W / 2 + (i - (n - 1) / 2) * 560
            a = ease((t - i * 0.9) / 0.6)
            digits = "".join(ch for ch in num if ch.isdigit())
            suffix = num[len(digits):]
            val = int(int(digits) * ease((t - i * 0.9) / 1.4))
            text(ctx, f"{val}{suffix}", x, H / 2 + 40, "Bebas Neue", 230, RED, a, "c")
            text(ctx, lab, x, H / 2 + 130, "Inter", 40, PAPER, a, "c", bold=True, spacing=8)
            if i < n - 1:
                ctx.set_source_rgba(1, 1, 1, 0.15 * a); ctx.rectangle(x + 280, H / 2 - 160, 2, 320); ctx.fill()

class Sketch(Scene):
    def prep(self):
        s, c = surface(1920, 1080)
        radial_bg(c, (0.86, 0.83, 0.76), (0.55, 0.52, 0.46), 960, 540, 1200)
        rnd = random.Random(self.idx)
        c.set_line_width(1.6)
        # charcoal head with ski mask
        for k in range(900):
            ang = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(150, 230)
            x = 960 + math.cos(ang) * r * 0.86; y = 470 + math.sin(ang) * r * 1.12
            c.set_source_rgba(0.1, 0.1, 0.1, rnd.uniform(0.05, 0.25))
            c.move_to(x, y); c.line_to(x + rnd.uniform(-30, 30), y + rnd.uniform(-30, 30)); c.stroke()
        c.set_source_rgba(0.08, 0.08, 0.08, 0.92)
        c.save(); c.translate(960, 470); c.scale(0.86, 1.12); c.arc(0, 0, 200, 0, 7); c.restore(); c.fill()
        c.move_to(700, 1080); c.curve_to(720, 820, 820, 720, 960, 700); c.curve_to(1100, 720, 1200, 820, 1220, 1080); c.close_path(); c.fill()
        # eye holes
        for ex in (885, 1035):
            c.set_source_rgb(0.75, 0.72, 0.66); c.save(); c.translate(ex, 450); c.scale(1.6, 0.8); c.arc(0, 0, 34, 0, 7); c.restore(); c.fill()
            c.set_source_rgb(0.15, 0.15, 0.17); c.arc(ex, 450, 15, 0, 7); c.fill()
        c.set_source_rgb(0.75, 0.72, 0.66); c.save(); c.translate(960, 590); c.scale(1.4, 0.6); c.arc(0, 0, 36, 0, 7); c.restore(); c.fill()
        text(c, "COMPOSITE  •  SUSPECT UNKNOWN", 960, 150, "Special Elite", 44, (0.15, 0.13, 0.12), 1, "c")
        self.bg = s
    def frame(self, ctx, t):
        u = t / self.D
        blit(ctx, self.bg, 1.02 + 0.08 * u)
        stamp(ctx, "UNIDENTIFIED", 1420, 260, 84, -0.18, ease((t - 1.2) / 0.3), scale=1 + 0.4 * (1 - ease((t - 1.2) / 0.3)))

class DNA(Scene):
    def frame(self, ctx, t):
        radial_bg(ctx, (0.04, 0.08, 0.14), (0.0, 0.01, 0.03))
        noise_dots(ctx, 120, W, H, (0.5, 0.7, 1), 0.05, 0.25, 2.2, self.idx)
        cx = W / 2 + 300 * math.sin(self.idx)
        n = 46
        for strand_pass in (0, 1):
            for i in range(n):
                y = -60 + i * (H + 120) / n
                ph = i * 0.38 + t * 1.1
                x1 = cx + 230 * math.sin(ph); x2 = cx + 230 * math.sin(ph + math.pi)
                z1 = math.cos(ph); z2 = -z1
                if strand_pass == 0:
                    ctx.set_source_rgba(0.5, 0.75, 1, 0.25); ctx.set_line_width(4)
                    ctx.move_to(x1, y); ctx.line_to(x2, y); ctx.stroke()
                else:
                    for x, z, col in ((x1, z1, (0.45, 0.8, 1.0)), (x2, z2, RED)):
                        r = 9 + 6 * (z + 1) / 2
                        ctx.set_source_rgba(*col, 0.45 + 0.5 * (z + 1) / 2); ctx.arc(x, y, r, 0, 7); ctx.fill()

class Title(Scene):
    def frame(self, ctx, t):
        radial_bg(ctx, (0.10, 0.04, 0.05), (0.0, 0.0, 0.0))
        fl = 1.0 if t > 1.2 else (0.4 + 0.6 * (math.sin(t * 40) > 0)) * ease(t / 0.4)
        sc = 1.0 + 0.05 * t / self.D
        ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc)
        text(ctx, self.p.get("small", ""), 0, -150, "Inter", 34, (0.75, 0.75, 0.78), ease(t / 1.0), "c", bold=True, spacing=10)
        big = self.p.get("big", "")
        size = 200 if len(big) < 14 else 150
        text(ctx, big, 0, 60, "Bebas Neue", size, PAPER, fl, "c", spacing=6)
        lw = 900 * ease((t - 0.6) / 1.2)
        ctx.set_source_rgba(*RED, 1); ctx.rectangle(-lw / 2, 110, lw, 8); ctx.fill()
        ctx.restore()

class Chapter(Scene):
    def frame(self, ctx, t):
        ctx.set_source_rgb(0.01, 0.01, 0.012); ctx.paint()
        glow(ctx, W / 2, H / 2, 900, (0.4, 0.05, 0.07), 0.25)
        a = ease(t / 0.6) * (1 - ease((t - self.D + 0.6) / 0.6))
        text(ctx, self.p["title"].upper(), W / 2, H / 2 - 90, "Inter", 38, RED, a, "c", bold=True, spacing=14)
        text(ctx, self.p["sub"].upper(), W / 2, H / 2 + 70, "Bebas Neue", 170, PAPER, a, "c", spacing=8)
        lw = 300 * ease((t - 0.3) / 1.0)
        ctx.set_source_rgba(*RED, a); ctx.rectangle(W / 2 - lw / 2, H / 2 + 120, lw, 5); ctx.fill()

# ---- map ----
CA = [(-124.21, 41.99), (-120.0, 42.0), (-120.0, 39.0), (-114.63, 35.0), (-114.6, 34.3), (-114.72, 32.72), (-117.12, 32.53), (-117.25, 32.9), (-117.6, 33.4), (-118.1, 33.75), (-118.4, 33.78), (-118.5, 34.03), (-118.9, 34.03), (-119.2, 34.15), (-119.6, 34.41), (-120.45, 34.45), (-120.6, 34.6), (-120.65, 35.15), (-120.9, 35.45), (-121.3, 35.7), (-121.9, 36.3), (-121.95, 36.6), (-121.8, 36.85), (-122.0, 36.97), (-122.4, 37.2), (-122.5, 37.5), (-122.52, 37.78), (-122.6, 37.9), (-123.0, 38.0), (-123.0, 38.3), (-123.7, 38.9), (-123.8, 39.4), (-123.8, 39.8), (-124.4, 40.4), (-124.1, 40.9), (-124.1, 41.5)]
CITY = {"Visalia": (36.33, -119.29), "Exeter": (36.30, -119.14), "Auburn": (38.90, -121.08), "Rancho Cordova": (38.59, -121.30), "Carmichael": (38.62, -121.33), "Citrus Heights": (38.71, -121.28), "Sacramento": (38.58, -121.49), "Davis": (38.54, -121.74), "Stockton": (37.96, -121.29), "Modesto": (37.64, -121.00), "Walnut Creek": (37.91, -122.06), "Danville": (37.82, -121.99), "Fremont": (37.55, -121.99), "Goleta": (34.44, -119.83), "Santa Barbara": (34.42, -119.70), "Ventura": (34.27, -119.23), "Dana Point": (33.47, -117.70), "Irvine": (33.68, -117.83)}
FOCUS = {"visalia": (-122.0, -117.0, 34.6, 38.2), "valley": (-122.2, -118.6, 35.8, 39.3), "sac": (-122.4, -120.5, 38.1, 39.2), "norcal": (-122.6, -120.6, 37.3, 39.1), "socal": (-120.4, -117.3, 33.2, 34.9), "ca": (-124.8, -114.0, 32.3, 42.2)}
KX = 100.0; KY = 120.0
def proj(lat, lon): return ((lon + 125) * KX, (42.5 - lat) * KY)

class Map(Scene):
    def frame(self, ctx, t):
        u = t / self.D
        ctx.set_source_rgb(0.02, 0.03, 0.045); ctx.paint()
        fx0, fx1, fy0, fy1 = FOCUS[self.p.get("focus", "ca")]
        x0, y0 = proj(fy1, fx0); x1, y1 = proj(fy0, fx1)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        sc_end = min(W * 0.8 / (x1 - x0), H * 0.75 / (y1 - y0))
        sc = sc_end * (0.82 + 0.18 * ease(u * 1.3))
        ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc); ctx.translate(-cx, -cy)
        lw = 1.0 / sc
        # grid
        ctx.set_source_rgba(0.3, 0.45, 0.6, 0.12); ctx.set_line_width(lw * 1.2)
        for lon in range(-126, -112):
            a, b = proj(43, lon), proj(32, lon); ctx.move_to(*a); ctx.line_to(*b); ctx.stroke()
        for lat in range(32, 44):
            a, b = proj(lat, -126), proj(lat, -113); ctx.move_to(*a); ctx.line_to(*b); ctx.stroke()
        ctx.move_to(*proj(CA[0][1], CA[0][0]))
        for lo, la in CA[1:]: ctx.line_to(*proj(la, lo))
        ctx.close_path()
        ctx.set_source_rgb(0.07, 0.09, 0.12); ctx.fill_preserve()
        ctx.set_source_rgba(0.6, 0.75, 0.9, 0.6); ctx.set_line_width(lw * 3); ctx.stroke()
        for nm_, (la_, lo_) in CITY.items():
            x_, y_ = proj(la_, lo_); ctx.set_source_rgba(0.5, 0.6, 0.7, 0.35); ctx.arc(x_, y_, 5 * lw, 0, 7); ctx.fill()
        pins = self.p.get("pins", [])
        pts = []
        for i, (nm, hl) in enumerate(pins):
            la, lo = CITY[nm]; x, y = proj(la, lo)
            a = ease((t - 0.4 - i * 0.55) / 0.4)
            if a <= 0: continue
            pts.append((x, y))
            col = RED if hl else (0.7, 0.75, 0.8)
            pr = (12 if hl else 9) * lw
            if hl:
                pulse = (t * 1.2 + i * 0.3) % 1.0
                ctx.set_source_rgba(*RED, 0.6 * (1 - pulse) * a); ctx.set_line_width(lw * 3)
                ctx.arc(x, y, pr + pulse * 40 * lw, 0, 7); ctx.stroke()
            ctx.set_source_rgba(*col, a); ctx.arc(x, y, pr, 0, 7); ctx.fill()
            side = 1 if i % 2 == 0 else -1
            fs = 34 * lw
            text(ctx, nm.upper(), x + side * 22 * lw, y + (-14 if i % 4 < 2 else 40) * lw, "Inter", fs, (0.95, 0.95, 0.95), a, "l" if side > 0 else "r", bold=True)
        if len(pts) > 1 and len(pins) > 2:
            ctx.set_source_rgba(*RED, 0.35); ctx.set_line_width(lw * 2); ctx.set_dash([8 * lw, 8 * lw])
            ctx.move_to(*pts[0])
            for p in pts[1:]: ctx.line_to(*p)
            ctx.stroke(); ctx.set_dash([])
        ctx.restore()
        text(ctx, "CALIFORNIA", 90, 130, "Bebas Neue", 64, (0.6, 0.7, 0.8), 0.6, spacing=8)

class File(Scene):
    def prep(self):
        s, c = surface(1920, 1080)
        radial_bg(c, (0.16, 0.12, 0.09), (0.03, 0.025, 0.02))
        rnd = random.Random(self.idx)
        c.save(); c.translate(960, 560); c.rotate(rnd.uniform(-0.03, 0.03))
        c.set_source_rgba(0, 0, 0, 0.5); c.rectangle(-660, -410, 1340, 860); c.fill()
        c.set_source_rgb(0.80, 0.68, 0.45); rrect(c, -680, -440, 1340, 860, 10); c.fill()   # folder
        c.set_source_rgb(*PAPER); c.rectangle(-620, -400, 1220, 800); c.fill()
        noise_dots(c, 500, 1220, 800, (0.4, 0.35, 0.25), 0.02, 0.08, 3, self.idx)
        c.restore()
        self.bg = s; self.rot = rnd.uniform(-0.03, 0.03)
    def frame(self, ctx, t):
        u = t / self.D
        sc = 1.0 + 0.06 * u
        ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc); ctx.translate(-W / 2, -H / 2)
        ctx.set_source_surface(self.bg, 0, 0); ctx.paint()
        ctx.translate(960, 560); ctx.rotate(self.rot)
        head = self.p.get("head", "")
        text(ctx, head, -560, -310, "Special Elite", 44, INK, 1)
        ctx.set_source_rgba(*INK, 0.7); ctx.rectangle(-560, -285, 1100, 3); ctx.fill()
        lines = self.p.get("lines", [])
        per = min(1.8, (self.D * 0.6) / max(1, len(lines)))
        for i, ln in enumerate(lines):
            uu = (t - 0.5 - i * per) / (per * 0.8)
            if uu <= 0: continue
            text(ctx, "— " + typed(ln, uu), -560, -190 + i * 86, "Special Elite", 46, INK, 1)
        ctx.restore()
        tt = self.D * 0.55
        stamp(ctx, "CONFIDENTIAL", 1430, 860, 70, -0.15, 0.85 * ease((t - tt) / 0.2), scale=1 + 0.5 * (1 - ease((t - tt) / 0.2)))

class Board(Scene):
    def prep(self):
        s, c = surface(2200, 1238)
        c.set_source_rgb(0.20, 0.14, 0.09); c.paint()
        noise_dots(c, 6000, 2200, 1238, (0.05, 0.03, 0.02), 0.1, 0.4, 2.5, self.idx)
        noise_dots(c, 3000, 2200, 1238, (0.45, 0.32, 0.2), 0.1, 0.3, 2, self.idx + 1)
        g = cairo.RadialGradient(1100, 619, 200, 1100, 619, 1300); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.8)
        c.set_source(g); c.paint()
        self.bg = s
        rnd = random.Random(self.idx * 3)
        cards = self.p.get("cards", [])
        n = len(cards); cols = 3 if n > 4 else 2 if n > 1 else 1
        rows = math.ceil(n / cols)
        self.pos = []
        for i in range(n):
            r_, c_ = divmod(i, cols)
            x = W / 2 + (c_ - (cols - 1) / 2) * 560 + rnd.uniform(-40, 40)
            y = H / 2 + (r_ - (rows - 1) / 2) * 300 + rnd.uniform(-30, 30)
            self.pos.append((x, y, rnd.uniform(-0.06, 0.06)))
    def frame(self, ctx, t):
        u = t / self.D
        blit(ctx, self.bg, 1.0 + 0.06 * u, ox=-30 * u)
        cards = self.p.get("cards", [])
        shown = []
        for i, txt in enumerate(cards):
            a = ease((t - 0.3 - i * 0.7) / 0.35)
            if a <= 0: continue
            x, y, r = self.pos[i]; shown.append((x, y))
            ctx.save(); ctx.translate(x, y + 30 * (1 - a)); ctx.rotate(r)
            ctx.set_source_rgba(0, 0, 0, 0.45 * a); ctx.rectangle(-226, -106, 460, 220); ctx.fill()
            ctx.set_source_rgba(0.94, 0.92, 0.86, a); ctx.rectangle(-230, -110, 460, 220); ctx.fill()
            ctx.set_source_rgba(0.6, 0.75, 0.9, 0.5 * a); ctx.rectangle(-230, -70, 460, 2); ctx.fill()
            lines = wrap(ctx, txt, 400, "Bebas Neue", 58)
            for k, ln in enumerate(lines[:3]):
                text(ctx, ln, 0, 10 + (k - (len(lines) - 1) / 2) * 56 + 10, "Bebas Neue", 58, INK, a, "c")
            ctx.set_source_rgba(*RED, a); ctx.arc(0, -92, 12, 0, 7); ctx.fill()
            ctx.restore()
        if len(shown) > 1:
            ctx.set_source_rgba(0.75, 0.08, 0.1, 0.85); ctx.set_line_width(3)
            for a_, b_ in zip(shown, shown[1:]):
                ctx.move_to(a_[0], a_[1] - 92); mx = (a_[0] + b_[0]) / 2; my = (a_[1] + b_[1]) / 2 - 40
                ctx.curve_to(mx, my + 60, mx, my + 60, b_[0], b_[1] - 92); ctx.stroke()

class Phone(Scene):
    def frame(self, ctx, t):
        radial_bg(ctx, (0.10, 0.08, 0.08), (0.01, 0.01, 0.01))
        cx, cy = W / 2 - 300, H / 2 + 30
        sh = 6 * math.sin(t * 50) if (t % 1.6) < 0.7 else 0
        ctx.save(); ctx.translate(cx + sh, cy); ctx.rotate(-0.5)
        ctx.set_source_rgb(0.30, 0.29, 0.30); ctx.set_line_width(70); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(-200, 0); ctx.curve_to(-120, -90, 120, -90, 200, 0); ctx.stroke()
        for x in (-220, 220):
            ctx.save(); ctx.translate(x, 30); ctx.scale(1.3, 0.8); ctx.arc(0, 0, 70, 0, 7); ctx.restore(); ctx.fill()
        ctx.restore()
        ctx.set_source_rgba(0.30, 0.29, 0.30, 1); ctx.set_line_width(6)
        for k in range(14):
            ctx.arc(cx - 120 + k * 10, cy + 160 + k * 18, 22, 0, 7); ctx.stroke()
        if (t % 1.6) < 0.9:
            for k in range(3):
                r = 300 + k * 70 + (t % 0.5) * 60
                ctx.set_source_rgba(*RED, 0.6 - k * 0.18); ctx.set_line_width(8)
                ctx.arc(cx, cy - 20, r, -0.9, -0.3); ctx.stroke(); ctx.arc(cx, cy - 20, r, math.pi + 0.3, math.pi + 0.9); ctx.stroke()
        tx = self.p.get("txt", "")
        text(ctx, typed(tx, (t - 0.8) / 1.2), W / 2 + 120, H / 2 + 40, "Special Elite", 80, PAPER, 1)

class Newspaper(Scene):
    def prep(self):
        s, c = surface(1500, 1000)
        c.set_source_rgb(0.86, 0.83, 0.74); c.paint()
        noise_dots(c, 1500, 1500, 1000, (0.4, 0.35, 0.25), 0.03, 0.1, 3, self.idx)
        text(c, "—  ARCHIVE  —", 750, 90, "Special Elite", 46, INK, 1, "c")
        c.set_source_rgb(*INK); c.rectangle(60, 115, 1380, 4); c.fill(); c.rectangle(60, 125, 1380, 1.5); c.fill()
        lines = wrap(c, self.p.get("head", ""), 1360, "Bebas Neue", 150)
        y = 270
        for ln in lines[:2]:
            text(c, ln, 750, y, "Bebas Neue", 150, INK, 1, "c"); y += 140
        text(c, self.p.get("sub", ""), 750, y - 30, "Special Elite", 40, INK, 0.9, "c")
        rnd = random.Random(self.idx)
        top = y + 20
        for col in range(4):
            x = 70 + col * 345
            for k in range(int((960 - top) / 26)):
                ww = 310 if rnd.random() > 0.15 else rnd.uniform(120, 300)
                c.set_source_rgba(*INK, 0.35); c.rectangle(x, top + k * 26, ww, 9); c.fill()
        self.bg = s
    def frame(self, ctx, t):
        u = t / self.D
        radial_bg(ctx, (0.08, 0.07, 0.07), (0, 0, 0))
        sp = ease(t / 0.9)
        ctx.save(); ctx.translate(W / 2, H / 2 + 40)
        ctx.rotate((1 - sp) * 6.0 - 0.04); s = (0.2 + 0.8 * sp) * (0.95 + 0.12 * u)
        ctx.scale(s, s)
        ctx.set_source_rgba(0, 0, 0, 0.5); ctx.rectangle(-740, -480, 1500, 1000); ctx.fill()
        ctx.set_source_surface(self.bg, -750, -500); ctx.paint()
        ctx.restore()

class Badge(Scene):
    def frame(self, ctx, t):
        u = t / self.D
        radial_bg(ctx, (0.07, 0.08, 0.12), (0, 0, 0.01))
        ctx.save(); ctx.translate(W / 2, H / 2 - 20); s = 1.0 + 0.08 * u; ctx.scale(s, s)
        g = cairo.LinearGradient(-200, -260, 200, 260); g.add_color_stop_rgb(0, 0.85, 0.72, 0.4); g.add_color_stop_rgb(0.5, 0.55, 0.42, 0.18); g.add_color_stop_rgb(1, 0.8, 0.66, 0.35)
        ctx.move_to(0, -280); ctx.curve_to(120, -200, 220, -220, 230, -200); ctx.curve_to(240, 0, 180, 180, 0, 290); ctx.curve_to(-180, 180, -240, 0, -230, -200); ctx.curve_to(-220, -220, -120, -200, 0, -280); ctx.close_path()
        ctx.set_source(g); ctx.fill_preserve(); ctx.set_source_rgb(0.3, 0.22, 0.1); ctx.set_line_width(6); ctx.stroke()
        ctx.set_source_rgb(0.3, 0.22, 0.1); ctx.arc(0, -10, 120, 0, 7); ctx.set_line_width(8); ctx.stroke()
        text(ctx, "POLICE", 0, 0, "Bebas Neue", 90, (0.25, 0.18, 0.08), 1, "c", spacing=6)
        text(ctx, "OFFICER", 0, 70, "Bebas Neue", 46, (0.25, 0.18, 0.08), 1, "c", spacing=6)
        ctx.restore()
        glint = (t * 0.4) % 1.5
        ctx.set_source_rgba(1, 1, 1, 0.12); ctx.move_to(W / 2 - 300 + glint * 600, 200); ctx.line_to(W / 2 - 220 + glint * 600, 200); ctx.line_to(W / 2 - 420 + glint * 600, 900); ctx.line_to(W / 2 - 500 + glint * 600, 900); ctx.fill()
        text(ctx, "1973 – 1979", W / 2, H - 120, "Special Elite", 44, PAPER, ease((t - 1) / 0.8), "c")

class Timeline(Scene):
    def frame(self, ctx, t):
        radial_bg(ctx, (0.07, 0.06, 0.08), (0.0, 0.0, 0.01))
        marks = self.p["marks"]; n = len(marks)
        span = 1500; x0 = W / 2 - span / 2
        y = H / 2
        lw = span * ease(t / 1.0)
        ctx.set_source_rgba(*PAPER, 0.5); ctx.rectangle(x0, y - 2, lw, 4); ctx.fill()
        for i, (d, lab) in enumerate(marks):
            x = x0 + span * (i / (n - 1) if n > 1 else 0.5)
            a = ease((t - 0.6 - i * (self.D * 0.6 / n)) / 0.4)
            if a <= 0: continue
            ctx.set_source_rgba(*RED, a); ctx.arc(x, y, 14, 0, 7); ctx.fill()
            ctx.set_source_rgba(*RED, a * 0.4); ctx.arc(x, y, 26, 0, 7); ctx.fill()
            up = i % 2 == 0
            text(ctx, d, x, y - (60 if up else -90), "Bebas Neue", 64, PAPER, a, "c")
            for k, ln in enumerate(wrap(ctx, lab, 300, "Inter", 30)):
                text(ctx, ln, x, y + (-120 - 36 * k if up else 140 + 36 * k), "Inter", 34, (0.8, 0.8, 0.82), a, "c")

class Truck(Scene):
    def prep(self):
        s, c = surface(2200, 1238)
        sky(c, 2200, 1238, False, self.idx)
        c.set_source_rgb(0.05, 0.055, 0.07); c.rectangle(0, 500, 2200, 500); c.fill()
        for k in range(6):
            x = 200 + k * 330
            c.set_source_rgb(0.95, 0.85, 0.6); c.rectangle(x, 560, 180, 26); c.fill()
            glow(c, x + 90, 600, 200, (1, 0.8, 0.5), 0.2)
            c.set_source_rgb(0.12, 0.12, 0.14); c.rectangle(x - 20, 640, 240, 320); c.fill()
        text(c, "DISTRIBUTION CENTER", 1100, 470, "Bebas Neue", 80, (0.7, 0.7, 0.72), 0.7, "c", spacing=10)
        c.set_source_rgb(0.02, 0.02, 0.025)
        for x in (250, 1250):
            c.rectangle(x, 820, 640, 230); c.fill(); c.rectangle(x + 660, 880, 180, 170); c.fill()
            for wx in (x + 80, x + 520, x + 740): c.arc(wx, 1060, 42, 0, 7); c.fill()
        c.set_source_rgb(0.01, 0.01, 0.015); c.rectangle(0, 1080, 2200, 200); c.fill()
        self.bg = s
    def frame(self, ctx, t):
        u = t / self.D
        blit(ctx, self.bg, 1.0 + 0.07 * u, ox=50 * u)
        caption_bar(ctx, "ROSEVILLE, CA  •  27 YEARS", u)

class Lab(Scene):
    def frame(self, ctx, t):
        radial_bg(ctx, (0.05, 0.08, 0.12), (0.0, 0.01, 0.02))
        rnd = random.Random(42)
        bands = [rnd.uniform(0, 1) for _ in range(16)]
        for col, lab in enumerate((self.p.get("a", "SAMPLE A"), self.p.get("b", "SAMPLE B"))):
            x = W / 2 + (-260 if col == 0 else 260)
            ctx.set_source_rgba(0.1, 0.14, 0.2, 1); rrect(ctx, x - 150, 180, 300, 700, 12); ctx.fill()
            for i, b in enumerate(bands):
                a = ease((t - 0.3 - col * 0.8 - i * 0.08) / 0.3)
                y = 220 + b * 620
                ctx.set_source_rgba(0.45, 0.85, 1.0, 0.85 * a); ctx.rectangle(x - 110, y, 220, 14); ctx.fill()
            text(ctx, lab, x, 950, "Inter", 30, PAPER, 1, "c", bold=True)
        tt = 0.3 + 0.8 + 16 * 0.08 + 0.6
        a = ease((t - tt) / 0.25)
        if a > 0:
            for i, b in enumerate(bands):
                y = 227 + b * 620
                ctx.set_source_rgba(*RED, 0.5 * a); ctx.set_line_width(2); ctx.set_dash([10, 8]); ctx.move_to(W / 2 - 150, y); ctx.line_to(W / 2 + 150, y); ctx.stroke()
            ctx.set_dash([])
            stamp(ctx, "MATCH", W / 2, 140, 110, -0.05, a, scale=1 + 0.5 * (1 - a))

class Tree(Scene):
    def prep(self):
        rnd = random.Random(7)
        self.nodes = []; self.edges = []
        # generations: top ancestors (gen0) down to living (gen4)
        gens = [2, 6, 14, 30, 52]
        prev = []
        for g, n in enumerate(gens):
            cur = []
            for i in range(n):
                x = 140 + (i + 0.5) * (W - 280) / n + rnd.uniform(-10, 10)
                y = 170 + g * 190
                idx = len(self.nodes); self.nodes.append((x, y, g)); cur.append(idx)
                if prev:
                    par = prev[min(len(prev) - 1, int(i * len(prev) / n))]
                    self.edges.append((par, idx))
            prev = cur
        self.target = self.nodes.index(next(nd for nd in self.nodes if nd[2] == 4 and nd[0] > W * 0.62))
        # path to target
        path = {self.target}; cur = self.target
        par = {b: a for a, b in self.edges}
        while cur in par: cur = par[cur]; path.add(cur)
        self.path = path
        self.matches = [i for i, nd in enumerate(self.nodes) if nd[2] == 4 and rnd.random() < 0.35 and i != self.target]
    def frame(self, ctx, t):
        st = self.p.get("stage", 0); u = t / self.D
        radial_bg(ctx, (0.05, 0.07, 0.11), (0.0, 0.0, 0.01))
        if st == 0:
            rnd = random.Random(3)
            for i in range(140):
                a = ease((t - i * 0.03) / 0.3)
                x, y = rnd.uniform(120, W - 120), rnd.uniform(140, H - 140)
                ctx.set_source_rgba(0.45, 0.8, 1, 0.8 * a); ctx.arc(x, y, 9, 0, 7); ctx.fill()
            text(ctx, "PUBLIC DNA DATABASE", W / 2, 110, "Bebas Neue", 70, PAPER, ease(t), "c", spacing=8)
            text(ctx, "MILLIONS OF CONSUMER DNA TESTS", W / 2, H - 70, "Inter", 32, (0.7, 0.75, 0.8), ease(t - 1), "c", spacing=4)
            return
        if st == 1:
            cx, cy = W / 2, H / 2
            ctx.set_source_rgba(*RED, 1); ctx.arc(cx, cy, 60, 0, 7); ctx.fill()
            text(ctx, "?", cx, cy + 34, "Bebas Neue", 100, PAPER, 1, "c")
            rnd = random.Random(5)
            for i in range(24):
                a = ease((t - 0.8 - i * 0.12) / 0.3)
                ang = i / 24 * 2 * math.pi; r = rnd.uniform(260, 460)
                x, y = cx + math.cos(ang) * r * 1.5, cy + math.sin(ang) * r
                ctx.set_source_rgba(0.45, 0.8, 1, 0.4 * a); ctx.set_line_width(2); ctx.move_to(cx, cy); ctx.line_to(x, y); ctx.stroke()
                ctx.set_source_rgba(0.45, 0.8, 1, 0.9 * a); ctx.arc(x, y, 12, 0, 7); ctx.fill()
            text(ctx, "KILLER'S DNA  >>  RELATIVES", W / 2, 110, "Bebas Neue", 70, PAPER, 1, "c", spacing=6)
            return
        reveal = {2: 1.0, 3: 1.0, 4: 1.0}[st]
        grow = ease(u * 1.6) if st == 3 else 1.0
        for a_, b_ in self.edges:
            x1, y1, g1 = self.nodes[a_]; x2, y2, g2 = self.nodes[b_]
            if st == 2 and g2 < 4: continue
            vis = ease((grow * 5 - g2) ) if st == 3 else 1
            hl = st == 4 and b_ in self.path
            dim = 0.25 if (st == 4 and not hl) else 0.5
            ctx.set_source_rgba(*(RED if hl else (0.5, 0.7, 0.9)), (1 if hl else dim) * vis)
            ctx.set_line_width(5 if hl else 2); ctx.move_to(x1, y1); ctx.curve_to(x1, (y1 + y2) / 2, x2, (y1 + y2) / 2, x2, y2); ctx.stroke()
        for i, (x, y, g) in enumerate(self.nodes):
            if st == 2 and g < 4: continue
            vis = ease(grow * 5 - g) if st == 3 else 1
            if vis <= 0: continue
            if st == 4:
                if i == self.target:
                    pulse = 1 + 0.15 * math.sin(t * 5)
                    ctx.set_source_rgba(*RED, 1); ctx.arc(x, y, 20 * pulse, 0, 7); ctx.fill()
                    glow(ctx, x, y, 90, RED, 0.5)
                    continue
                fade = 1 - 0.75 * ease((t - 1.0 - (i % 9) * 0.25) / 0.5)
                col = RED if i in self.path else (0.45, 0.8, 1)
                ctx.set_source_rgba(*col, fade if i not in self.path else 1)
            else:
                m = i in self.matches
                ctx.set_source_rgba(*((0.45, 0.8, 1) if (m or st == 3) else (0.3, 0.4, 0.5)), vis)
            ctx.arc(x, y, 10, 0, 7); ctx.fill()
        if st == 2:
            text(ctx, "1,000+", W / 2, 520, "Bebas Neue", 260, RED, ease((t - 0.5) / 0.6), "c")
            text(ctx, "DISTANT RELATIVES FOUND", W / 2, 600, "Inter", 40, PAPER, ease((t - 0.9) / 0.6), "c", bold=True, spacing=8)
        lab = {2: "1,000+ GENETIC COUSINS", 3: "BUILDING THE FAMILY TREES", 4: "ONE MAN"}[st]
        text(ctx, lab, W / 2, 95, "Bebas Neue", 70, PAPER, ease(t), "c", spacing=8)
        if st == 3:
            gl = ["1800s", "", "", "", "TODAY"]
            text(ctx, "1800s", 60, 180, "Inter", 26, (0.6, 0.65, 0.7), 1)
            text(ctx, "TODAY", 60, 170 + 4 * 190 + 10, "Inter", 26, (0.6, 0.65, 0.7), 1)

class Reveal(Scene):
    def frame(self, ctx, t):
        radial_bg(ctx, (0.10, 0.09, 0.08), (0.01, 0.01, 0.01))
        ctx.set_source_rgb(*PAPER); ctx.rectangle(260, 250, 1400, 580); ctx.fill()
        text(ctx, "IDENTIFICATION  •  FILE 2018-0414", 320, 330, "Special Elite", 40, INK, 1)
        ctx.set_source_rgba(*INK, 0.7); ctx.rectangle(320, 352, 1280, 3); ctx.fill()
        name = self.p.get("name", ""); info = self.p.get("info", "")
        nw = twidth(ctx, name, "Bebas Neue", 130)
        text(ctx, name, W / 2, 560, "Bebas Neue", 130, INK, 1, "c")
        bar = 1 - ease((t - 1.2) / 1.2)
        ctx.set_source_rgb(0.02, 0.02, 0.02); ctx.rectangle(W / 2 - nw / 2 - 20 + (nw + 40) * (1 - bar), 450, (nw + 40) * bar, 140); ctx.fill()
        text(ctx, typed(info, (t - 2.6) / 1.5), W / 2, 700, "Special Elite", 40, INK, 1, "c")
        stamp(ctx, "IDENTIFIED", 1480, 860, 80, -0.12, ease((t - 4) / 0.25), scale=1 + 0.5 * (1 - ease((t - 4) / 0.25)))

class Interrogation(Scene):
    def prep(self):
        s, c = surface(1920, 1080)
        c.set_source_rgb(0.06, 0.065, 0.07); c.paint()
        c.set_source_rgb(0.09, 0.095, 0.1); c.rectangle(0, 0, 1920, 760); c.fill()
        c.set_source_rgb(0.03, 0.035, 0.045); c.rectangle(1260, 170, 520, 330); c.fill()  # one-way mirror
        c.set_source_rgba(0.5, 0.6, 0.7, 0.08); c.move_to(1300, 190); c.line_to(1400, 190); c.line_to(1320, 480); c.line_to(1280, 480); c.fill()
        g = cairo.LinearGradient(0, 0, 0, 1080)
        c.save(); c.move_to(860, 0); c.line_to(1060, 0); c.line_to(1500, 1080); c.line_to(420, 1080); c.close_path()
        g = cairo.RadialGradient(960, 0, 50, 960, 600, 900); g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.35); g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0.02)
        c.set_source(g); c.fill(); c.restore()
        c.set_source_rgb(0.12, 0.12, 0.13); c.rectangle(560, 700, 800, 40); c.fill()
        c.rectangle(600, 740, 30, 300); c.fill(); c.rectangle(1290, 740, 30, 300); c.fill()
        man_sil(c, 960, 700, 2.0, (0.01, 0.01, 0.015))
        c.set_source_rgb(0.12, 0.12, 0.13); c.rectangle(860, 700, 200, 40); c.fill()
        c.set_source_rgb(0.02, 0.02, 0.02); c.rectangle(950, 0, 20, 60); c.fill(); c.move_to(900, 60); c.line_to(1020, 60); c.line_to(990, 100); c.line_to(930, 100); c.fill()
        self.bg = s
    def frame(self, ctx, t):
        u = t / self.D
        fl = 0.85 + 0.15 * (math.sin(t * 13) * math.sin(t * 7.3) > 0.6)
        blit(ctx, self.bg, 1.03 + 0.07 * u, oy=-20 * u, alpha=1)
        ctx.set_source_rgba(0, 0, 0, 1 - fl); ctx.paint()
        text(ctx, "INTERVIEW ROOM 2  •  APRIL 24, 2018", 90, 120, "Special Elite", 36, (0.85, 0.85, 0.85), 0.8)

class Court(Scene):
    def prep(self):
        s, c = surface(2200, 1238)
        g = cairo.LinearGradient(0, 0, 0, 1238); g.add_color_stop_rgb(0, 0.10, 0.07, 0.05); g.add_color_stop_rgb(1, 0.03, 0.02, 0.015)
        c.set_source(g); c.paint()
        for x in range(0, 2200, 140):
            c.set_source_rgba(0.2, 0.14, 0.08, 0.5); c.rectangle(x, 0, 6, 700); c.fill()
        c.set_source_rgb(0.18, 0.12, 0.07); c.arc(1100, 300, 150, 0, 7); c.fill()
        c.set_source_rgb(0.55, 0.45, 0.25); c.set_line_width(8); c.arc(1100, 300, 150, 0, 7); c.stroke(); c.arc(1100, 300, 115, 0, 7); c.stroke()
        text(c, "SUPERIOR COURT", 1100, 312, "Bebas Neue", 46, (0.6, 0.5, 0.3), 1, "c", spacing=4)
        c.set_source_rgb(0.14, 0.09, 0.05); c.rectangle(500, 560, 1200, 380); c.fill()
        c.set_source_rgb(0.22, 0.15, 0.08); c.rectangle(480, 540, 1240, 40); c.fill()
        c.set_source_rgb(0.02, 0.02, 0.02); c.rectangle(0, 1000, 2200, 238); c.fill()
        for x in range(60, 2200, 170):
            c.arc(x, 1020, 60, math.pi, 2 * math.pi); c.fill(); c.rectangle(x - 60, 1020, 120, 220); c.fill()
        self.bg = s
    def frame(self, ctx, t):
        u = t / self.D
        blit(ctx, self.bg, 1.0 + 0.06 * u, oy=15 * u)
        # gavel
        hit = (t % 4.0)
        ang = -0.6 + 0.6 * ease(hit / 0.25) if hit < 0.5 else 0
        ctx.save(); ctx.translate(1350, 600); ctx.rotate(ang)
        ctx.set_source_rgb(0.25, 0.15, 0.07); ctx.rectangle(-10, -20, 160, 20); ctx.fill(); rrect(ctx, -50, -60, 60, 100, 10); ctx.fill(); ctx.restore()
        caption_bar(ctx, self.p.get("caption", ""), u)

class Cell(Scene):
    def frame(self, ctx, t):
        u = t / self.D
        radial_bg(ctx, (0.25, 0.25, 0.27), (0.02, 0.02, 0.03), W / 2, H / 2 - 100, 900)
        off = -40 * u
        for k in range(9):
            x = 120 + k * 215 + off
            g = cairo.LinearGradient(x, 0, x + 50, 0); g.add_color_stop_rgb(0, 0.02, 0.02, 0.02); g.add_color_stop_rgb(0.5, 0.18, 0.18, 0.2); g.add_color_stop_rgb(1, 0.02, 0.02, 0.02)
            ctx.set_source(g); ctx.rectangle(x, 0, 50, H); ctx.fill()
        ctx.set_source_rgb(0.05, 0.05, 0.06); ctx.rectangle(0, 120, W, 40); ctx.fill(); ctx.rectangle(0, H - 160, W, 40); ctx.fill()
        a = ease((t - 0.8) / 0.8)
        ctx.set_source_rgba(0, 0, 0, 0.75 * a); ctx.rectangle(0, H / 2 - 120, W, 210); ctx.fill()
        text(ctx, self.p.get("txt", ""), W / 2, H / 2 + 40, "Bebas Neue", 170, PAPER, a, "c", spacing=6)

class End(Scene):
    def frame(self, ctx, t):
        radial_bg(ctx, (0.10, 0.04, 0.05), (0, 0, 0))
        a = ease(t / 0.8)
        text(ctx, "MIDNIGHT WITNESS", W / 2, H / 2 - 60, "Bebas Neue", 170, PAPER, a, "c", spacing=10)
        text(ctx, "A NEW SOLVED CASE EVERY NIGHT", W / 2, H / 2 + 20, "Inter", 38, (0.8, 0.8, 0.82), a, "c", bold=True, spacing=8)
        pulse = 1 + 0.04 * math.sin(t * 4)
        ctx.save(); ctx.translate(W / 2, H / 2 + 170); ctx.scale(pulse, pulse)
        ctx.set_source_rgba(*RED, ease((t - 1) / 0.5)); rrect(ctx, -230, -55, 460, 110, 14); ctx.fill()
        text(ctx, "SUBSCRIBE", 0, 24, "Bebas Neue", 76, (1, 1, 1), ease((t - 1) / 0.5), "c", spacing=6)
        ctx.restore()
        text(ctx, "Which case should we cover next?  Tell us in the comments ↓", W / 2, H - 120, "Inter", 34, (0.75, 0.75, 0.78), ease((t - 2) / 0.6), "c")

def BookCards(p, D, idx, n):
    cards = [["MICHELLE McNAMARA", "TRUE CRIME WRITER", "COINED: 'GOLDEN STATE KILLER'"], ["2016: McNAMARA DIES", "2018: HER BOOK IS PUBLISHED", "THE WORLD IS WATCHING"]][min(n, 1)]
    return Board({"cards": cards}, D, idx)

def DogCards(p, D, idx):
    return Board({"cards": ["HAMMER", "DOG REPELLENT", "WHY?"]}, D, idx)

_book = [0]
def make(scene, p, D, idx):
    if scene == "quote" and not p.get("q"):
        return House({"day": False}, D, idx)
    if scene == "book":
        b = BookCards(p, D, idx, _book[0]); _book[0] += 1; return b
    if scene == "dog": return DogCards(p, D, idx)
    return {"house": House, "surveil": Surveil, "quote": Quote, "stats": Stats, "sketch": Sketch, "dna": DNA, "title": Title,
            "chapter": Chapter, "map": Map, "file": File, "board": Board, "phone": Phone, "newspaper": Newspaper, "badge": Badge,
            "timeline": Timeline, "truck": Truck, "lab": Lab, "tree": Tree, "reveal": Reveal, "interrogation": Interrogation,
            "court": Court, "cell": Cell, "end": End}[scene](p, D, idx)
