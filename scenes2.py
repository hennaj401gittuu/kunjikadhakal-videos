"""Midnight Witness engine v2: cinematic upgrades on top of scenes.py"""
import cairo, math, random
from gfx import *
import scenes as v1
import geomap

# ---------------------------------------------------------------- overlays
class Atmos:
    """fog + dust + flicker drawn on top of every frame"""
    def __init__(self, seed=0):
        rnd = random.Random(seed)
        self.fog, c = surface(2600, 1100)
        for _ in range(70):
            x, y, r = rnd.uniform(0, 2600), rnd.uniform(0, 1100), rnd.uniform(150, 420)
            g = cairo.RadialGradient(x, y, 0, x, y, r)
            g.add_color_stop_rgba(0, 0.75, 0.8, 0.9, rnd.uniform(0.03, 0.07)); g.add_color_stop_rgba(1, 0.75, 0.8, 0.9, 0)
            c.set_source(g); c.arc(x, y, r, 0, 7); c.fill()
        self.dust = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.6, 2.4), rnd.uniform(4, 18), rnd.uniform(0, 6.28)) for _ in range(70)]
    def draw(self, ctx, t, fog=1.0, dust=1.0):
        if fog > 0:
            ox = -(t * 22) % 1300
            ctx.save(); ctx.translate(ox, H - 1100 + 120); ctx.set_source_surface(self.fog, 0, 0); ctx.paint_with_alpha(fog); ctx.restore()
        if dust > 0:
            for (x, y, r, sp, ph) in self.dust:
                xx = (x + t * sp) % W; yy = (y + math.sin(t * 0.5 + ph) * 30 - t * sp * 0.4) % H
                ctx.set_source_rgba(1, 0.95, 0.85, 0.25 * dust * (0.5 + 0.5 * math.sin(t * 2 + ph)))
                ctx.arc(xx, yy, r, 0, 7); ctx.fill()

ATM = Atmos(3)

# ---------------------------------------------------------------- parallax night street
def layer_trees(w, h, seed, col, n, hmin, hmax, base):
    s, c = surface(w, h); rnd = random.Random(seed)
    for _ in range(n): v1.tree_sil(c, rnd.uniform(0, w), base, rnd.uniform(hmin, hmax), col, rnd)
    return s

class House2(v1.Scene):
    def prep(self):
        day = self.p.get("day", False); rnd = random.Random(self.idx)
        self.sky, c = surface(2300, 1300); v1.sky(c, 2300, 1300, day, self.idx)
        self.far = layer_trees(2600, 1300, self.idx, (0.035, 0.045, 0.065) if not day else (0.2, 0.22, 0.24), 14, 200, 340, 1060)
        self.mid, c = surface(2600, 1300)
        # houses only (no sky) on mid layer
        c.save(); c.translate(0, 40); v1.house_row(c, 2600, 1300, day, self.idx + 7); c.restore()
        # cut sky region of mid to transparent: redraw by masking top part
        m, mc = surface(2600, 1300)
        mc.set_source_surface(self.mid, 0, 0); mc.rectangle(0, 560, 2600, 740); mc.fill()
        self.mid = m
        self.fg, c = surface(2800, 1300)
        c.set_source_rgb(0.008, 0.008, 0.012)
        for x in (rnd.uniform(0, 150), 2800 - rnd.uniform(0, 150)):
            v1.tree_sil(c, x, 1400, 650, (0.008, 0.008, 0.012), rnd)
        c.rectangle(0, 1220, 2800, 80); c.fill()
        self.rain = self.p.get("rain", False)
    def frame(self, ctx, t):
        u = t / self.D; dirn = 1 if self.idx % 2 else -1
        z = 1.0 + 0.06 * u
        def lay(s, speed, oy=0):
            ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z)
            ctx.translate(-s.get_width() / 2 + dirn * speed * u, -H / 2 - (s.get_height() - H) / 2 + oy)
            ctx.set_source_surface(s, 0, 0); ctx.paint(); ctx.restore()
        lay(self.sky, 15); lay(self.far, 45, 20); lay(self.mid, 90, -40)
        if self.p.get("figure"): v1.man_sil(ctx, 1180 + dirn * 30 * u, 930, 2.2, (0, 0, 0), ease((t - 1.0) / 2.0))
        if self.p.get("beam"):
            ang = -0.35 + 0.6 * math.sin(t * 0.6)
            ctx.save(); ctx.translate(980, 840); ctx.rotate(ang)
            g = cairo.LinearGradient(0, 0, 0, -700); g.add_color_stop_rgba(0, 1, 1, 0.9, 0.5); g.add_color_stop_rgba(1, 1, 1, 0.9, 0)
            ctx.set_source(g); ctx.move_to(-10, 0); ctx.line_to(-170, -700); ctx.line_to(170, -700); ctx.line_to(10, 0); ctx.fill(); ctx.restore()
        lay(self.fg, 260, 60)
        ATM.draw(ctx, t + self.idx * 7, 1.0, 0.6)
        if self.rain:
            rnd = random.Random(int(t * 30))
            ctx.set_source_rgba(0.8, 0.85, 0.95, 0.25); ctx.set_line_width(1.5)
            for _ in range(160):
                x, y = rnd.uniform(0, W), rnd.uniform(0, H); ctx.move_to(x, y); ctx.line_to(x - 8, y + 40)
            ctx.stroke()
        v1.caption_bar(ctx, self.p.get("caption", ""), u)

# ---------------------------------------------------------------- real map
class Map2(v1.Scene):
    LEG = {"visalia": (-120.5, 35.6, -118.2, 37.0), "valley": (-122.6, 35.6, -118.4, 39.4), "sac": (-122.0, 38.3, -120.8, 39.1),
           "norcal": (-122.8, 37.2, -120.4, 39.2), "socal": (-120.5, 33.1, -117.2, 34.9), "ca": (-125.0, 32.2, -113.8, 42.3)}
    def prep(self):
        p = self.p
        self.pins = []
        for pin in p.get("pins", []):
            if len(pin) >= 4: nm, la, lo, hl = pin[0], pin[1], pin[2], pin[3]
            else:
                nm, hl = pin[0], pin[1]
                ll = v1.CITY.get(nm) or geomap.find_place(nm, p.get("state_name"))
                if not ll: continue
                la, lo = ll
            self.pins.append((nm, la, lo, hl))
        f = p.get("focus", "auto")
        if isinstance(f, (list, tuple)): fb = tuple(f)
        elif f in self.LEG: fb = self.LEG[f]
        elif isinstance(f, str) and len(f) == 2 and geomap.state_bbox(f): fb = geomap.state_bbox(f)
        else:
            lats = [x[1] for x in self.pins] or [37]; lons = [x[2] for x in self.pins] or [-120]
            padx = max(0.6, (max(lons) - min(lons)) * 0.35); pady = max(0.4, (max(lats) - min(lats)) * 0.35)
            fb = (min(lons) - padx, min(lats) - pady, max(lons) + padx, max(lats) + pady)
        # keep 16:9 in projected space
        k = math.cos(math.radians((fb[1] + fb[3]) / 2)); w = (fb[2] - fb[0]) * k; h = fb[3] - fb[1]
        if w / h < 16 / 9: dw = (h * 16 / 9 / k - (fb[2] - fb[0])) / 2; fb = (fb[0] - dw, fb[1], fb[2] + dw, fb[3])
        else: dh = (w * 9 / 16 - h) / 2; fb = (fb[0], fb[1] - dh, fb[2], fb[3] + dh)
        self.focus = fb
        cx, cy = (fb[0] + fb[2]) / 2, (fb[1] + fb[3]) / 2; ww, hh = fb[2] - fb[0], fb[3] - fb[1]
        zf = p.get("zoom_from", 2.6)
        self.start = (cx - ww * zf / 2, cy - hh * zf / 2, cx + ww * zf / 2, cy + hh * zf / 2)
        self.hi = tuple(p.get("hi", ["CA"]))
    def frame(self, ctx, t):
        u = t / self.D
        view = geomap.lerp_bb(self.start, self.focus, ease(min(1, t / max(2.5, self.D * 0.45))))
        P = geomap.draw_base(ctx, view, W, H, self.hi)
        def lab(s, x, y): text(ctx, s, x, y, "Inter", 26, (0.75, 0.8, 0.9), 0.35, "c", bold=True, spacing=10)
        geomap.state_labels(ctx, P, view, lab)
        placed = []
        pts = []
        for i, (nm, la, lo, hl) in enumerate(self.pins):
            a = ease((t - 0.8 - i * 0.6) / 0.4)
            if a <= 0: continue
            x, y = P(lo, la); pts.append((x, y))
            col = RED if hl else (0.85, 0.88, 0.92)
            if hl:
                pulse = (t * 0.9 + i * 0.3) % 1.0
                ctx.set_source_rgba(*RED, 0.7 * (1 - pulse) * a); ctx.set_line_width(3); ctx.arc(x, y, 12 + pulse * 46, 0, 7); ctx.stroke()
                glow(ctx, x, y, 40, RED, 0.5 * a)
            ctx.set_source_rgba(0, 0, 0, a); ctx.arc(x, y, 12, 0, 7); ctx.fill()
            ctx.set_source_rgba(*col, a); ctx.arc(x, y, 8, 0, 7); ctx.fill()
            # label placement avoiding overlap
            font(ctx, "Inter", 30, True); tw = ctx.text_extents(nm.upper()).x_advance
            for dx, dy, al in ((22, 10, "l"), (-22, 10, "r"), (0, -26, "c"), (0, 50, "c"), (22, 40, "l"), (-22, 40, "r"), (22, -20, "l"), (-22, -20, "r")):
                lx = x + dx - (tw if al == "r" else tw / 2 if al == "c" else 0); ly = y + dy
                box = (lx - 10, ly - 30, lx + tw + 10, ly + 10)
                if all(box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3] for b in placed) and 20 < box[0] and box[2] < W - 20:
                    placed.append(box); break
            ctx.set_source_rgba(0, 0, 0, 0.55 * a); rrect(ctx, box[0], box[1], box[2] - box[0], box[3] - box[1], 6); ctx.fill()
            text(ctx, nm.upper(), box[0] + 10, box[3] - 10, "Inter", 30, (1, 1, 1), a, bold=True)
        if self.p.get("route", len(self.pins) > 2) and len(pts) > 1:
            ctx.set_source_rgba(*RED, 0.7); ctx.set_line_width(3); ctx.set_dash([12, 10], -t * 40)
            ctx.move_to(*pts[0]); [ctx.line_to(*q) for q in pts[1:]]; ctx.stroke(); ctx.set_dash([])
        # HUD
        ctx.set_source_rgba(0, 0, 0, 0.5); ctx.rectangle(0, 0, W, 90); ctx.fill()
        text(ctx, self.p.get("title", "CASE MAP"), 70, 60, "Bebas Neue", 52, PAPER, 1, spacing=8)
        cy_ = (view[1] + view[3]) / 2; cx_ = (view[0] + view[2]) / 2
        text(ctx, f"{abs(cy_):.3f}°{'N' if cy_ >= 0 else 'S'}  {abs(cx_):.3f}°{'W' if cx_ < 0 else 'E'}", W - 70, 58, "Special Elite", 30, (0.7, 0.75, 0.8), 1, "r")
        # scale bar
        km = (view[2] - view[0]) * 111 * math.cos(math.radians(cy_)) / 6
        nice = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000]; v = min(nice, key=lambda n: abs(n - km))
        px = v / ((view[2] - view[0]) * 111 * math.cos(math.radians(cy_))) * W
        ctx.set_source_rgba(1, 1, 1, 0.7); ctx.rectangle(70, H - 70, px, 4); ctx.fill()
        text(ctx, f"{int(v * 0.621)} MI", 70 + px + 14, H - 60, "Inter", 24, (0.85, 0.85, 0.85), 0.8, bold=True)
        ATM.draw(ctx, t, 0.35, 0.0)

# ---------------------------------------------------------------- realistic police report
class Report(v1.Scene):
    def prep(self):
        rnd = random.Random(self.idx)
        s, c = surface(1500, 1950)
        c.set_source_rgb(0.93, 0.91, 0.86); c.paint()
        noise_dots(c, 2500, 1500, 1950, (0.45, 0.4, 0.3), 0.02, 0.06, 2.5, self.idx)
        g = cairo.LinearGradient(0, 0, 1500, 0); g.add_color_stop_rgba(0, 0, 0, 0, 0.06); g.add_color_stop_rgba(0.5, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.08)
        c.set_source(g); c.paint()
        c.set_source_rgb(*INK); c.set_line_width(3); c.arc(160, 170, 80, 0, 7); c.stroke(); c.arc(160, 170, 62, 0, 7); c.set_line_width(1.5); c.stroke()
        text(c, "★", 160, 192, "DejaVu Sans", 64, INK, 1, "c")
        org = self.p.get("org", "")
        if not org:
            org = self.p.get("head", "CASE FILE").split("•")[0].strip()
        text(c, org.upper()[:38], 290, 150, "Special Elite", 52, INK, 1)
        text(c, self.p.get("form", "INVESTIGATION REPORT"), 290, 215, "Inter", 30, INK, 0.8, bold=True, spacing=6)
        c.set_source_rgb(*INK); c.rectangle(80, 280, 1340, 4); c.fill()
        head = self.p.get("head", "")
        sub = head.split("•")[1].strip() if "•" in head else head
        fields = self.p.get("fields") or [("CASE NO.", f"{rnd.randint(70, 99)}-{rnd.randint(10000, 99999)}"), ("SUBJECT", sub[:34]), ("STATUS", self.p.get("status", "CLOSED"))]
        y = 320
        for k, (a, b) in enumerate(fields):
            c.set_line_width(2); c.rectangle(80, y, 1340, 90); c.stroke()
            text(c, a, 100, y + 32, "Inter", 22, INK, 0.7, bold=True, spacing=4)
            text(c, str(b).upper(), 100, y + 74, "Special Elite", 38, INK, 1)
            y += 90
        text(c, "NARRATIVE", 80, y + 70, "Inter", 26, INK, 0.75, bold=True, spacing=6)
        c.rectangle(80, y + 85, 1340, 2); c.fill()
        self.narr_y = y + 160
        for k in range(14):
            c.set_source_rgba(0.5, 0.55, 0.7, 0.25); c.rectangle(80, self.narr_y + 30 + k * 82, 1340, 1.5); c.fill()
        self.paper = s; self.rot = rnd.uniform(-0.05, 0.05)
        self.bg, c = surface(W, H); v1.radial_bg(c, (0.13, 0.10, 0.08), (0.02, 0.015, 0.012))
        noise_dots(c, 1500, W, H, (0.3, 0.2, 0.12), 0.02, 0.08, 3, self.idx)
    def frame(self, ctx, t):
        u = t / self.D
        ctx.set_source_surface(self.bg, 0, 0); ctx.paint()
        lines = self.p.get("lines", [])
        per = min(1.8, (self.D * 0.6) / max(1, len(lines)))
        # camera: start on header, drift down to narrative
        sc = 0.72 + 0.1 * u
        focus_y = 520 + ease(u * 1.2) * (self.narr_y - 330)
        ctx.save(); ctx.translate(W / 2 + 80 * math.sin(self.idx), H / 2); ctx.rotate(self.rot); ctx.scale(sc, sc); ctx.translate(-750, -focus_y)
        ctx.set_source_rgba(0, 0, 0, 0.55)
        for k in range(6): rrect(ctx, -8 - k * 3, 14 + k * 3, 1500 + k * 6, 1950, 4); ctx.fill()
        ctx.set_source_surface(self.paper, 0, 0); ctx.paint()
        hl = self.p.get("hl", len(lines) - 1)
        for i, ln in enumerate(lines):
            uu = (t - 0.5 - i * per) / (per * 0.8)
            if uu <= 0: continue
            y = self.narr_y + 20 + i * 82
            if i == hl and uu > 1.2:
                tw = twidth(ctx, ln, "Special Elite", 44)
                hw = tw * ease((uu - 1.2) / 0.5)
                ctx.set_source_rgba(1.0, 0.9, 0.1, 0.45); ctx.rectangle(95, y - 38, hw + 20, 52); ctx.fill()
            text(ctx, typed(ln, uu), 105, y, "Special Elite", 44, INK, 1)
        for (ri, frac) in self.p.get("redact", [(len(lines) + 1, 0.6)]):
            if ri < 14:
                y = self.narr_y + 20 + ri * 82
                ra = ease((t - 0.5 - len(lines) * per) / 0.4)
                ctx.set_source_rgba(0.02, 0.02, 0.02, ra); ctx.rectangle(105, y - 36, 1260 * frac, 46); ctx.fill()
        ctx.restore()
        tt = self.D * 0.62
        v1.stamp(ctx, self.p.get("stamp", "CONFIDENTIAL"), 1450, 880, 72, -0.15, 0.85 * ease((t - tt) / 0.2), scale=1 + 0.5 * (1 - ease((t - tt) / 0.2)))
        ATM.draw(ctx, t, 0.0, 0.8)

# ---------------------------------------------------------------- evidence objects
def obj(c, kind, s=1.0):
    """draw an evidence object centred at 0,0 in ~300px box"""
    c.save(); c.scale(s, s)
    dark = (0.12, 0.12, 0.13); steel = (0.6, 0.62, 0.66); wood = (0.45, 0.3, 0.17)
    if kind == "hammer":
        c.set_source_rgb(*wood); rrect(c, -20, -60, 40, 200, 10); c.fill()
        c.set_source_rgb(*steel); rrect(c, -90, -110, 180, 60, 10); c.fill()
    elif kind == "can":
        g = cairo.LinearGradient(-60, 0, 60, 0); g.add_color_stop_rgb(0, 0.5, 0.1, 0.1); g.add_color_stop_rgb(0.5, 0.85, 0.25, 0.2); g.add_color_stop_rgb(1, 0.45, 0.08, 0.08)
        c.set_source(g); rrect(c, -60, -110, 120, 230, 14); c.fill(); c.set_source_rgb(*steel); c.rectangle(-30, -140, 60, 32); c.fill()
        c.set_source_rgb(0.95, 0.9, 0.8); c.rectangle(-60, -20, 120, 50); c.fill()
    elif kind == "swab":
        c.set_source_rgb(0.95, 0.95, 0.95); c.rectangle(-6, -120, 12, 220); c.fill(); c.save(); c.translate(0, -130); c.scale(1, 1.8); c.arc(0, 0, 18, 0, 7); c.restore(); c.fill()
    elif kind == "tissue":
        c.set_source_rgb(0.95, 0.95, 0.93); c.move_to(-90, 40); c.curve_to(-120, -60, -40, -120, 10, -80); c.curve_to(80, -110, 120, -20, 90, 50); c.curve_to(40, 90, -40, 90, -90, 40); c.fill()
        c.set_source_rgba(0.7, 0.7, 0.68, 0.6); c.set_line_width(2); c.move_to(-60, 0); c.curve_to(-20, -40, 20, 10, 60, -30); c.stroke()
    elif kind == "phone":
        c.set_source_rgb(*dark); rrect(c, -70, -120, 140, 240, 20); c.fill(); c.set_source_rgb(0.15, 0.2, 0.25); rrect(c, -58, -100, 116, 190, 8); c.fill()
    elif kind == "letter":
        c.set_source_rgb(0.92, 0.9, 0.82); c.rectangle(-110, -140, 220, 280); c.fill()
        c.set_source_rgba(0.1, 0.1, 0.3, 0.6)
        for k in range(10): c.rectangle(-90, -110 + k * 24, random.Random(k).uniform(120, 180), 3); c.fill()
    elif kind == "key":
        c.set_source_rgb(0.75, 0.65, 0.35); c.set_line_width(14); c.arc(-60, 0, 36, 0, 7); c.stroke(); c.rectangle(-24, -7, 140, 14); c.fill(); c.rectangle(80, 0, 14, 30); c.fill(); c.rectangle(105, 0, 14, 22); c.fill()
    elif kind == "shoe":
        c.set_source_rgb(0.25, 0.22, 0.2); c.move_to(-130, 40); c.line_to(-120, -60); c.line_to(-40, -60); c.curve_to(0, -10, 80, -10, 130, 10); c.line_to(130, 50); c.close_path(); c.fill()
    elif kind == "flashlight":
        c.set_source_rgb(*dark); rrect(c, -130, -22, 200, 44, 10); c.fill(); c.rectangle(60, -36, 60, 72); c.fill(); c.set_source_rgb(0.9, 0.9, 0.7); c.rectangle(118, -30, 6, 60); c.fill()
    elif kind == "mask":
        c.set_source_rgb(0.08, 0.08, 0.09); c.save(); c.scale(0.9, 1.15); c.arc(0, 0, 110, 0, 7); c.restore(); c.fill()
        c.set_source_rgb(0.7, 0.66, 0.6)
        for ex in (-40, 40): c.save(); c.translate(ex, -20); c.scale(1.6, 0.8); c.arc(0, 0, 18, 0, 7); c.restore(); c.fill()
    elif kind == "rope":
        c.set_source_rgb(0.7, 0.62, 0.45); c.set_line_width(10)
        for k in range(4): c.arc(0, 0, 40 + k * 18, 0.3, 5.9); c.stroke()
    elif kind == "photo":
        c.set_source_rgb(0.95, 0.95, 0.93); c.rectangle(-110, -130, 220, 260); c.fill(); c.set_source_rgb(0.2, 0.22, 0.26); c.rectangle(-95, -115, 190, 190); c.fill()
    elif kind == "car":
        c.set_source_rgb(0.2, 0.22, 0.26); c.move_to(-150, 40); c.line_to(-140, -10); c.line_to(-80, -60); c.line_to(60, -60); c.line_to(110, -10); c.line_to(150, 0); c.line_to(150, 40); c.close_path(); c.fill()
        c.set_source_rgb(0.05, 0.05, 0.05); c.arc(-90, 45, 28, 0, 7); c.fill(); c.arc(90, 45, 28, 0, 7); c.fill()
    else:  # generic box
        c.set_source_rgb(0.55, 0.42, 0.28); c.rectangle(-100, -80, 200, 160); c.fill()
    c.restore()

class Evidence(v1.Scene):
    """evidence bags on a dark table. p: items=[[kind, label], ...]"""
    def prep(self):
        self.bg, c = surface(2200, 1238)
        c.set_source_rgb(0.07, 0.07, 0.075); c.paint()
        noise_dots(c, 9000, 2200, 1238, (0.2, 0.2, 0.22), 0.03, 0.12, 2, self.idx)
        rnd = random.Random(self.idx); self.pos = []
        items = self.p.get("items", [])
        n = len(items)
        for i in range(n):
            x = W / 2 + (i - (n - 1) / 2) * (1500 / max(1, n)) if n > 1 else W / 2
            self.pos.append((x + rnd.uniform(-20, 20), H / 2 + rnd.uniform(-30, 30), rnd.uniform(-0.12, 0.12)))
    def frame(self, ctx, t):
        u = t / self.D
        blit(ctx, self.bg, 1.0 + 0.05 * u)
        g = cairo.RadialGradient(W / 2, H / 2 - 100, 100, W / 2, H / 2, 1000); g.add_color_stop_rgba(0, 1, 0.95, 0.85, 0.16); g.add_color_stop_rgba(1, 0, 0, 0, 0)
        ctx.set_source(g); ctx.paint()
        items = self.p.get("items", []); n = len(items)
        bw = min(420, 1500 / max(1, n) - 40)
        for i, (kind, label) in enumerate(items):
            a = ease((t - 0.3 - i * 0.8) / 0.4)
            if a <= 0: continue
            x, y, r = self.pos[i]
            ctx.save(); ctx.translate(x, y + 40 * (1 - a)); ctx.rotate(r)
            sc = bw / 420
            ctx.scale(sc, sc)
            ctx.set_source_rgba(0, 0, 0, 0.5 * a); rrect(ctx, -196, -246, 410, 560, 10); ctx.fill()
            ctx.set_source_rgba(0.82, 0.86, 0.9, 0.22 * a); rrect(ctx, -200, -250, 400, 550, 10); ctx.fill()
            ctx.push_group(); obj(ctx, kind, 1.0); ctx.pop_group_to_source(); ctx.paint_with_alpha(a * 0.92)
            ctx.set_source_rgba(1, 1, 1, 0.12 * a); ctx.move_to(-180, -230); ctx.line_to(-120, -230); ctx.line_to(-200, 200); ctx.line_to(-200, 0); ctx.fill()
            ctx.set_source_rgba(*RED, a); ctx.rectangle(-200, -250, 400, 46); ctx.fill()
            text(ctx, "EVIDENCE", 0, -215, "Bebas Neue", 40, (1, 1, 1), a, "c", spacing=8)
            ctx.set_source_rgba(0.96, 0.95, 0.9, a); ctx.rectangle(-180, 180, 360, 100); ctx.fill()
            text(ctx, f"ITEM #{i + 1}", -165, 212, "Inter", 22, INK, a, bold=True)
            for k, ln in enumerate(wrap(ctx, label.upper(), 330, "Special Elite", 30)[:2]):
                text(ctx, ln, -165, 248 + k * 28, "Special Elite", 30, INK, a)
            ctx.restore()
        ATM.draw(ctx, t, 0.0, 0.8)

class Polaroids(v1.Scene):
    """crime-scene style photos pinned/laid down. p: photos=[[kind, caption], ...] kind: house|street|car|door|window|road|field"""
    def prep(self):
        self.shots = []
        for i, (kind, cap) in enumerate(self.p.get("photos", [])):
            s, c = surface(600, 600)
            day = kind in ("field", "road")
            v1.sky(c, 600, 600, day, self.idx + i)
            if kind in ("house", "street", "window", "door"):
                c.save(); c.scale(0.55, 0.55); c.translate(-200 - i * 300, 0); v1.house_row(c, 2000, 1100, day, self.idx + i); c.restore()
            if kind == "window":
                c.set_source_rgb(0.03, 0.03, 0.04); c.rectangle(0, 0, 600, 600); c.fill()
                c.set_source_rgb(0.9, 0.7, 0.4); c.rectangle(150, 120, 300, 340); c.fill(); c.set_source_rgb(0.03, 0.03, 0.04); c.rectangle(292, 120, 16, 340); c.fill(); c.rectangle(150, 282, 300, 16); c.fill()
                v1.man_sil(c, 320, 470, 1.2, (0.02, 0.02, 0.02))
            if kind == "door":
                c.set_source_rgb(0.05, 0.05, 0.06); c.rectangle(0, 0, 600, 600); c.fill(); c.set_source_rgb(0.22, 0.17, 0.12); c.rectangle(180, 80, 240, 520); c.fill()
                c.set_source_rgb(0.75, 0.65, 0.35); c.arc(390, 340, 12, 0, 7); c.fill(); glow(c, 300, 40, 200, (1, 0.85, 0.6), 0.4)
            if kind == "car":
                c.set_source_rgb(0.05, 0.06, 0.07); c.rectangle(0, 380, 600, 220); c.fill(); c.save(); c.translate(300, 420); obj(c, "car", 1.6); c.restore()
            if kind in ("road", "field"):
                c.set_source_rgb(0.12, 0.13, 0.11); c.rectangle(0, 330, 600, 270); c.fill()
                if kind == "road":
                    c.set_source_rgb(0.08, 0.08, 0.09); c.move_to(260, 330); c.line_to(340, 330); c.line_to(560, 600); c.line_to(40, 600); c.fill()
                    c.set_source_rgb(0.85, 0.75, 0.3)
                    for k in range(5): c.rectangle(296 - k * 2, 350 + k * 50, 8 + k * 4, 28); c.fill()
            g = cairo.LinearGradient(0, 0, 600, 600); g.add_color_stop_rgba(0, 1, 0.9, 0.7, 0.12); g.add_color_stop_rgba(1, 0.1, 0.2, 0.3, 0.15)
            c.set_source(g); c.paint()
            self.shots.append((s, cap))
        rnd = random.Random(self.idx)
        n = len(self.shots)
        self.pos = [(W / 2 + (i - (n - 1) / 2) * min(620, 1700 / max(1, n)) + rnd.uniform(-30, 30), H / 2 + rnd.uniform(-50, 30), rnd.uniform(-0.1, 0.1)) for i in range(n)]
        self.bg, c = surface(W, H); v1.radial_bg(c, (0.14, 0.1, 0.07), (0.02, 0.015, 0.01)); noise_dots(c, 2000, W, H, (0.3, 0.2, 0.12), 0.02, 0.08, 3, self.idx)
    def frame(self, ctx, t):
        u = t / self.D
        sc0 = 1.0 + 0.06 * u
        ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc0, sc0); ctx.translate(-W / 2, -H / 2)
        ctx.set_source_surface(self.bg, 0, 0); ctx.paint()
        n = len(self.shots); s_ = min(1.0, 2.3 / max(1, n))
        for i, (shot, cap) in enumerate(self.shots):
            a = ease((t - 0.2 - i * 0.9) / 0.35)
            if a <= 0: continue
            x, y, r = self.pos[i]
            ctx.save(); ctx.translate(x, y); ctx.rotate(r); sc = s_ * (1 + 0.25 * (1 - a)); ctx.scale(sc, sc)
            ctx.set_source_rgba(0, 0, 0, 0.5 * a); ctx.rectangle(-232, -232, 480, 580); ctx.fill()
            ctx.set_source_rgba(0.95, 0.94, 0.9, a); ctx.rectangle(-240, -240, 480, 580); ctx.fill()
            ctx.save(); ctx.translate(-210, -210); ctx.scale(420 / 600, 420 / 600); ctx.set_source_surface(shot, 0, 0); ctx.paint_with_alpha(a); ctx.restore()
            text(ctx, cap.upper(), 0, 285, "Special Elite", 34, INK, a, "c")
            ctx.set_source_rgba(*RED, a); ctx.arc(0, -222, 11, 0, 7); ctx.fill()
            ctx.restore()
        ctx.restore()
        # flash at each photo arrival
        for i in range(n):
            ft = t - 0.2 - i * 0.9
            if 0 <= ft < 0.15:
                ctx.set_source_rgba(1, 1, 1, 0.35 * (1 - ft / 0.15)); ctx.paint()
        ATM.draw(ctx, t, 0.0, 0.8)

# ---------------------------------------------------------------- booking-style reveal
class Booking(v1.Scene):
    def frame(self, ctx, t):
        ctx.set_source_rgb(0.06, 0.065, 0.075); ctx.paint()
        for k in range(14):
            y = 120 + k * 60
            ctx.set_source_rgba(0.8, 0.85, 0.9, 0.35 if k % 2 == 0 else 0.15); ctx.rectangle(560, y, 800, 2); ctx.fill()
            if k % 2 == 0: text(ctx, f"{7 - k // 2}'", 520, y + 10, "Inter", 26, (0.8, 0.85, 0.9), 0.6, "r", bold=True)
        glow(ctx, W / 2, 420, 500, (0.9, 0.9, 1.0), 0.15)
        v1.man_sil(ctx, W / 2, 960, 3.4, (0.01, 0.01, 0.012))
        ctx.set_source_rgba(0, 0, 0, 0.8); ctx.rectangle(0, 800, W, 280); ctx.fill()
        name = self.p.get("name", ""); info = self.p.get("info", "")
        nw = twidth(ctx, name, "Bebas Neue", 120)
        text(ctx, name, W / 2, 930, "Bebas Neue", 120, PAPER, 1, "c", spacing=4)
        bar = 1 - ease((t - 1.2) / 1.2)
        ctx.set_source_rgb(0, 0, 0); ctx.rectangle(W / 2 - nw / 2 - 30 + (nw + 60) * (1 - bar), 820, (nw + 60) * bar, 140); ctx.fill()
        text(ctx, typed(info, (t - 2.6) / 1.5), W / 2, 1010, "Special Elite", 38, (0.85, 0.85, 0.85), 1, "c")
        v1.stamp(ctx, self.p.get("stamp", "IDENTIFIED"), 1560, 300, 84, -0.14, ease((t - 4) / 0.25), scale=1 + 0.5 * (1 - ease((t - 4) / 0.25)))
        if 4.0 <= t < 4.15:
            ctx.set_source_rgba(1, 1, 1, 0.5); ctx.paint()
        ATM.draw(ctx, t, 0.0, 0.6)

# ---------------------------------------------------------------- wrap v1 scenes with atmosphere
def with_atmos(cls, fog=0.6, dust=0.7):
    class X(cls):
        def frame(self, ctx, t):
            super().frame(ctx, t); ATM.draw(ctx, t + self.idx * 3.1, fog, dust)
    return X

REG = {
    "house": House2, "map": Map2, "file": Report, "evidence": Evidence, "photos": Polaroids, "reveal": Booking,
    "surveil": with_atmos(v1.Surveil, 0.5, 0.3), "interrogation": with_atmos(v1.Interrogation, 0.4, 0.9),
    "court": with_atmos(v1.Court, 0.3, 0.8), "sketch": v1.Sketch, "board": with_atmos(v1.Board, 0.0, 0.7),
    "newspaper": with_atmos(v1.Newspaper, 0.0, 0.6), "quote": with_atmos(v1.Quote, 0.5, 0.6), "stats": with_atmos(v1.Stats, 0.4, 0.5),
    "dna": v1.DNA, "title": with_atmos(v1.Title, 0.6, 0.6), "chapter": with_atmos(v1.Chapter, 0.4, 0.5), "phone": with_atmos(v1.Phone, 0.3, 0.6),
    "badge": with_atmos(v1.Badge, 0.3, 0.6), "timeline": with_atmos(v1.Timeline, 0.3, 0.5), "truck": with_atmos(v1.Truck, 0.6, 0.4),
    "lab": v1.Lab, "tree": v1.Tree, "cell": with_atmos(v1.Cell, 0.3, 0.8), "end": with_atmos(v1.End, 0.5, 0.6),
}

def make(scene, p, D, idx, book_n=0):
    import stickscene
    if scene in stickscene.REG3: return stickscene.REG3[scene](p, D, idx)
    if scene == "quote" and not p.get("q"): return House2({"day": False}, D, idx)
    if scene == "book":
        cards = [["MICHELLE McNAMARA", "TRUE CRIME WRITER", "COINED: 'GOLDEN STATE KILLER'"], ["2016: McNAMARA DIES", "2018: HER BOOK IS PUBLISHED", "THE WORLD IS WATCHING"]][min(book_n, 1)]
        return REG["board"]({"cards": cards}, D, idx)
    if scene == "dog": return Evidence({"items": [["hammer", "Hammer"], ["can", "Dog repellent"]]}, D, idx)
    return REG[scene](p, D, idx)
