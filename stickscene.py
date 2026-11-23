"""Midnight Witness v3: illustrated stick-figure story scenes + documentary text/portrait scenes.
Scene types added: stick, words, portrait, money, versus, bigdate, chartx.  See README for params."""
import cairo, math, random
from gfx import W, H, ease, glow, noise_dots, rrect, surface
import scenes as v1
from stick import *

COLORS = {"grey": (0.45, 0.42, 0.4), "navy": (0.18, 0.22, 0.35), "black": (0.12, 0.12, 0.13), "red": (0.75, 0.2, 0.18), "green": (0.3, 0.5, 0.32),
          "brown": (0.5, 0.35, 0.22), "blue": (0.25, 0.42, 0.7), "white": (0.95, 0.95, 0.93), "yellow": (0.95, 0.78, 0.2), "purple": (0.45, 0.3, 0.6),
          "khaki": (0.6, 0.55, 0.35), "orange": (0.9, 0.5, 0.15), None: None}

# ---------------------------------------------------------------- props
def prop(c, kind, x, y, s=1.0, seed=0, t=0.0, txt=None):
    c.save(); c.translate(x, y); c.scale(s, s)
    if kind == "bottle":
        spoly(c, [(-22, 0), (22, 0), (22, -90), (10, -120), (10, -160), (-10, -160), (-10, -120), (-22, -90)], (0.45, 0.25, 0.15), seed=seed)
        sbox(c, -20, -80, 40, 40, (0.95, 0.9, 0.8), seed=seed);
        if txt: label(c, txt[:6], 0, -60, 22)
    elif kind == "moneybag":
        spoly(c, [(-60, 0), (60, 0), (70, -60), (30, -110), (40, -130), (-40, -130), (-30, -110), (-70, -60)], (0.75, 0.62, 0.35), seed=seed)
        label(c, "$", 0, -50, 80, (0.25, 0.45, 0.2))
    elif kind == "cash":
        for k in range(5): sbox(c, -70 + k * 4, -20 - k * 16, 140, 16, (0.55, 0.75, 0.5), seed=seed + k)
    elif kind == "trophy":
        spoly(c, [(-50, -150), (50, -150), (35, -80), (10, -60), (10, -30), (35, -20), (35, 0), (-35, 0), (-35, -20), (-10, -30), (-10, -60), (-35, -80)], (0.95, 0.75, 0.2), seed=seed)
    elif kind == "lightbulb":
        glow(c, 0, -90, 90 + 10 * math.sin(t * 5), (1, 0.95, 0.5), 0.6)
        scircle(c, 0, -100, 45, (1, 0.95, 0.6), seed=seed); sbox(c, -20, -60, 40, 40, (0.6, 0.6, 0.62), seed=seed)
    elif kind == "box":
        sbox(c, -70, -110, 140, 110, (0.8, 0.62, 0.4), seed=seed); sline(c, [(-70, -80), (70, -80)], 4, INK, seed)
    elif kind == "laptop":
        sbox(c, -90, -130, 180, 115, (0.2, 0.22, 0.25), seed=seed); sbox(c, -80, -120, 160, 95, (0.55, 0.75, 0.95), seed=seed)
        spoly(c, [(-110, 0), (110, 0), (90, -15), (-90, -15)], (0.6, 0.6, 0.62), seed=seed)
    elif kind == "tv":
        sbox(c, -110, -170, 220, 160, (0.45, 0.3, 0.2), seed=seed); sbox(c, -90, -150, 150, 120, (0.6, 0.7, 0.75), seed=seed)
        for k in range(2): scircle(c, 85, -130 + k * 40, 10, (0.2, 0.2, 0.2), seed=seed)
        sline(c, [(-30, -10), (-50, 0)], 5, INK, seed); sline(c, [(30, -10), (50, 0)], 5, INK, seed)
    elif kind == "car":
        spoly(c, [(-170, -30), (-150, -80), (-80, -120), (60, -120), (120, -80), (170, -70), (170, -30)], (0.75, 0.2, 0.18), seed=seed)
        window(c, -70, -110, 120, 30, (0.7, 0.85, 0.95), seed)
        for wx in (-100, 100): scircle(c, wx, -25, 30, (0.12, 0.12, 0.12), seed=seed); scircle(c, wx, -25, 12, (0.7, 0.7, 0.7), seed=seed)
    elif kind == "document":
        sbox(c, -80, -200, 160, 200, (0.97, 0.96, 0.9), seed=seed)
        for k in range(7): sline(c, [(-60, -170 + k * 22), (random.Random(k).uniform(10, 60), -170 + k * 22)], 3, (0.4, 0.4, 0.45), seed + k)
        if txt: label(c, txt[:10], 0, -185, 26)
    elif kind == "gear":
        c.set_source_rgb(0.55, 0.55, 0.58)
        for k in range(10):
            a = k * math.pi / 5 + t * 0.5
            c.save(); c.rotate(a); c.rectangle(-12, -90, 24, 30); c.fill(); c.restore()
        scircle(c, 0, 0, 65, (0.55, 0.55, 0.58), seed=seed); scircle(c, 0, 0, 20, (0.95, 0.92, 0.85), seed=seed)
    elif kind == "brick":
        lego_brick(c, -80, -70, 160, (0.9, 0.15, 0.15), seed)
    elif kind == "duck":
        wooden_duck(c, 0, 0, 1.0, seed)
    elif kind == "phone":
        sbox(c, -40, -150, 80, 150, (0.15, 0.15, 0.17), seed=seed); sbox(c, -32, -140, 64, 120, (0.5, 0.75, 0.95), seed=seed)
    elif kind == "rocket":
        spoly(c, [(0, -260), (40, -180), (40, -40), (-40, -40), (-40, -180)], (0.92, 0.92, 0.95), seed=seed)
        spoly(c, [(-40, -90), (-80, -20), (-40, -40)], (0.8, 0.2, 0.2), seed=seed); spoly(c, [(40, -90), (80, -20), (40, -40)], (0.8, 0.2, 0.2), seed=seed)
        fire(c, -30, 0, 60, 60 + 20 * math.sin(t * 9), t, seed)
    elif kind == "ship":
        spoly(c, [(-260, -60), (260, -60), (200, 0), (-220, 0)], (0.25, 0.25, 0.3), seed=seed)
        sbox(c, -120, -140, 200, 80, (0.9, 0.9, 0.88), seed=seed)
        for k in range(2): sbox(c, -80 + k * 90, -220, 40, 80, (0.75, 0.2, 0.18), seed=seed + k)
    elif kind == "crown":
        spoly(c, [(-70, 0), (-70, -80), (-35, -40), (0, -100), (35, -40), (70, -80), (70, 0)], (1, 0.8, 0.15), seed=seed)
    elif kind == "sign":
        sign(c, txt or "?", 0, -60, max(160, 30 * len(txt or "?")), 70, seed=seed)
    elif kind == "warning":
        spoly(c, [(0, -170), (95, 0), (-95, 0)], (1, 0.65, 0.1), seed=seed); label(c, "!", 0, -55, 120)
    elif kind == "cloud":
        for dx, dy, r in ((-60, 0, 50), (0, -30, 65), (60, 0, 50), (0, 10, 55)): scircle(c, dx, dy, r, (0.4, 0.42, 0.48), seed=seed)
        c.set_source_rgba(0.4, 0.55, 0.8, 0.8)
        for k in range(6): c.rectangle(-70 + k * 28, 50 + (t * 120 + k * 30) % 80, 4, 20); c.fill()
    elif kind == "fire":
        fire(c, -150, 0, 300, 220, t, seed)
    c.restore()

# ---------------------------------------------------------------- backgrounds (static, cached)
def bg_draw(c, kind, seed, sign_txt=None, year=None, trend="up"):
    rnd = random.Random(seed)
    if kind in ("workshop", "shop", "lab", "office", "home", "boardroom", "bank"):
        wall = {"workshop": (0.80, 0.66, 0.48), "shop": (0.86, 0.74, 0.55), "lab": (0.82, 0.86, 0.86), "office": (0.84, 0.86, 0.9),
                "home": (0.9, 0.8, 0.62), "boardroom": (0.78, 0.8, 0.85), "bank": (0.7, 0.68, 0.62)}[kind]
        paper(c, W, H, wall, seed); hatch(c, 0, 0, W, 760, a=0.06)
        window(c, 1420, 110, 330, 250, (0.72, 0.86, 0.96) if kind != "home" else (0.3, 0.35, 0.55), seed)
        if kind in ("workshop", "shop", "lab"):
            def items(c, x, y, w, r):
                for k in range(6):
                    xx = x + 50 + k * (w - 80) / 6
                    if kind == "lab": spoly(c, [(xx - 18, y + 110), (xx + 18, y + 110), (xx + 8, y + 60), (xx + 8, y + 30), (xx - 8, y + 30), (xx - 8, y + 60)], [(0.5, 0.8, 0.6), (0.6, 0.7, 0.95), (0.95, 0.6, 0.6)][(k + r) % 3], seed=k)
                    elif kind == "shop": prop(c, "bottle", xx, y + 110, 0.55, seed=k + r)
                    else: sbox(c, xx - 35, y + 50, 70, 60, [(0.85, 0.2, 0.2), (0.2, 0.4, 0.8), (0.95, 0.75, 0.15), (0.6, 0.45, 0.3)][(k + r) % 4], seed=k)
            shelves(c, 90, 150, 900, 3, items, seed=seed)
        if kind in ("office", "boardroom"):
            sbox(c, 120, 170, 520, 330, (0.99, 0.98, 0.95), seed=seed)
            down = trend == "down"
            pts = [(160 + i * 60, (230 + i * 30 + rnd.uniform(-20, 20)) if down else (450 - i * 28 + rnd.uniform(-20, 20))) for i in range(8)]
            sline(c, pts, 7, (0.85, 0.15, 0.15) if down else (0.2, 0.55, 0.3), seed)
        if kind == "bank":
            scircle(c, 500, 400, 260, (0.55, 0.56, 0.6), seed=seed); scircle(c, 500, 400, 200, (0.45, 0.46, 0.5), seed=seed)
            for k in range(6): c.save(); c.translate(500, 400); c.rotate(k * math.pi / 3); sline(c, [(0, 0), (0, -150)], 8, INK, seed); c.restore()
        if kind == "home":
            sbox(c, 150, 520, 520, 200, (0.55, 0.3, 0.25), seed=seed); sbox(c, 130, 470, 40, 250, (0.5, 0.28, 0.22), seed=seed); sbox(c, 650, 470, 40, 250, (0.5, 0.28, 0.22), seed=seed)
        wood_floor(c, W, 760, H, (0.62, 0.42, 0.25) if kind != "lab" else (0.7, 0.72, 0.74), seed)
        if kind in ("workshop", "shop", "lab", "boardroom"):
            sbox(c, 1050, 600, 680, 40, (0.55, 0.36, 0.2), seed=seed); sbox(c, 1080, 640, 30, 160, (0.45, 0.28, 0.15), seed=seed); sbox(c, 1670, 640, 30, 160, (0.45, 0.28, 0.15), seed=seed)
    elif kind in ("street", "town", "city"):
        paper(c, W, H, (0.72, 0.84, 0.94) if kind != "city" else (0.55, 0.65, 0.8), seed)
        if kind == "city":
            for k in range(14):
                hh = rnd.uniform(250, 600); sbox(c, k * 140 - 20, 760 - hh, 130, hh, (0.45, 0.5, 0.6), seed=seed + k)
                for j in range(int(hh / 60)): c.set_source_rgba(1, 0.9, 0.6, 0.7); c.rectangle(k * 140 + 10, 760 - hh + 20 + j * 60, 20, 25); c.fill(); c.rectangle(k * 140 + 60, 760 - hh + 20 + j * 60, 20, 25); c.fill()
        else:
            x = -40; names = ["BANK", "HOTEL", "GENERAL STORE", "PHARMACY", "SALOON", "BAKERY", "DRY GOODS"]
            k = 0
            while x < W:
                w = rnd.uniform(280, 420); h = rnd.uniform(380, 520)
                building(c, x, 760, w, h, [(0.75, 0.45, 0.32), (0.85, 0.72, 0.5), (0.6, 0.55, 0.5), (0.7, 0.35, 0.3)][k % 4], seed=seed + k,
                         sign_txt=(sign_txt if (sign_txt and k == 2) else names[(seed + k) % len(names)]), roof=False)
                x += w + 10; k += 1
        sbox(c, -10, 760, W + 20, 330, (0.6, 0.55, 0.5), seed=seed); sline(c, [(0, 820), (W, 820)], 3, INK, seed)
        for k in range(4):
            lx = 150 + k * 520; sbox(c, lx, 520, 12, 250, INK, seed=seed); scircle(c, lx + 6, 515, 20, (1, 0.9, 0.6), seed=seed)
    elif kind in ("factory", "field", "farm", "war", "sea", "space"):
        sky = {"factory": (0.75, 0.82, 0.9), "field": (0.7, 0.86, 0.96), "farm": (0.75, 0.88, 0.96), "war": (0.7, 0.68, 0.62), "sea": (0.65, 0.82, 0.95), "space": (0.04, 0.05, 0.12)}[kind]
        paper(c, W, H, sky, seed)
        if kind == "space":
            noise_dots(c, 500, W, H, (1, 1, 1), 0.3, 0.9, 2.0, seed); scircle(c, 1500, 260, 140, (0.85, 0.85, 0.8), seed=seed)
            sbox(c, -10, 820, W + 20, 280, (0.6, 0.6, 0.62), seed=seed)
        elif kind == "sea":
            sbox(c, -10, 620, W + 20, 470, (0.25, 0.45, 0.7), seed=seed)
            for k in range(30): sline(c, [(rnd.uniform(0, W), 650 + k * 14), (rnd.uniform(0, W), 650 + k * 14)], 2, (0.85, 0.92, 1), seed + k)
        else:
            if kind == "factory":
                building(c, 250, 760, 1400, 420, (0.72, 0.36, 0.28), seed=seed, sign_txt=sign_txt or "FACTORY", roof=False)
                for k, x in enumerate((330, 1450)):
                    sbox(c, x, 180, 70, 160, (0.5, 0.3, 0.25), seed=seed + k)
            if kind == "war":
                for k in range(5): spoly(c, [(150 + k * 360, 760), (300 + k * 360, 560), (450 + k * 360, 760)], (0.55, 0.52, 0.38), seed=seed + k)
                c.set_source_rgba(0.35, 0.35, 0.35, 0.35)
                for k in range(8): c.arc(rnd.uniform(0, W), rnd.uniform(100, 450), rnd.uniform(60, 140), 0, 7); c.fill()
            if kind == "farm":
                building(c, 1250, 760, 420, 320, (0.75, 0.2, 0.18), seed=seed, windows=False)
            for k in range(6): tree_x = rnd.uniform(0, W);
            sbox(c, -10, 760, W + 20, 330, (0.55, 0.7, 0.42) if kind != "war" else (0.5, 0.45, 0.35), seed=seed)
    elif kind == "stage":
        paper(c, W, H, (0.25, 0.08, 0.08), seed)
        for k in range(16): sbox(c, k * 125 - 10, -10, 70, 720, (0.65, 0.12, 0.12), seed=seed + k)
        sbox(c, -10, 700, W + 20, 120, (0.55, 0.36, 0.2), seed=seed)
        glow(c, W / 2, 400, 600, (1, 0.9, 0.6), 0.25)
        sbox(c, -10, 820, W + 20, 270, (0.15, 0.08, 0.08), seed=seed)
    elif kind == "court":
        paper(c, W, H, (0.55, 0.42, 0.3), seed)
        for x in range(0, W, 140): sbox(c, x, 0, 8, 700, (0.42, 0.3, 0.2), seed=seed + x)
        scircle(c, W / 2, 230, 120, (0.4, 0.28, 0.18), seed=seed); label(c, "COURT", W / 2, 230, 50, (0.85, 0.75, 0.5))
        sbox(c, 560, 470, 800, 330, (0.42, 0.27, 0.16), seed=seed)
        wood_floor(c, W, 800, H, (0.5, 0.34, 0.22), seed)
    else:
        paper(c, W, H, (0.93, 0.88, 0.78), seed)
        sbox(c, -10, 760, W + 20, 330, (0.75, 0.65, 0.5), seed=seed)
    if year:
        sbox(c, 70, 70, 250, 110, (0.98, 0.97, 0.93), seed=seed); label(c, str(year), 195, 125, 84)

class Stick(v1.Scene):
    """p: bg, sign, year, chars=[{x(0-1), pose, face, hat, outfit, mustache, glasses, hair, beard, apron, facing, s, name, prop}],
          props=[[kind, x(0-1), y(px ground), scale, txt]], crowd (bool/'cheer'), caption, fx ('fire','rain','money','confetti')"""
    def prep(self):
        p = self.p
        self.bg, c = surface(W, H)
        bg_draw(c, p.get("bg", "plain"), self.idx * 7 + 3, p.get("sign"), p.get("year"), p.get("trend", "up"))
        self.dir = 1 if self.idx % 2 else -1
    def frame(self, ctx, t):
        p = self.p; u = t / self.D
        z = 1.03 + 0.06 * u
        ctx.save(); ctx.translate(W / 2 + self.dir * 25 * u, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2)
        ctx.set_source_surface(self.bg, 0, 0); ctx.paint()
        for pr in p.get("props", []):
            kind = pr[0]; x = pr[1] * W if len(pr) > 1 else W * 0.7; y = pr[2] if len(pr) > 2 else 800; s = pr[3] if len(pr) > 3 else 1.0
            txt = pr[4] if len(pr) > 4 else None
            a = ease((t - 0.2) / 0.4)
            ctx.push_group(); prop(ctx, kind, x, y + 30 * (1 - a), s, seed=self.idx, t=t, txt=txt); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
        if p.get("crowd"):
            crowd(ctx, 80, W - 80, 1060, 2, seed=self.idx, t=t, cheer=p.get("crowd") == "cheer", scale=0.7)
        chars = p.get("chars", [])
        for i, ch in enumerate(chars):
            x = ch.get("x", (i + 1) / (len(chars) + 1)) * W
            a = ease((t - 0.1 - i * 0.25) / 0.35)
            yy = ch.get("y", 900 if p.get("bg") not in ("stage",) else 760)
            ctx.push_group()
            hands = figure(ctx, x, yy + 20 * (1 - a), ch.get("s", 1.5), ch.get("pose", "stand"), ch.get("face", "smile"), hat=ch.get("hat"),
                           outfit=COLORS.get(ch.get("outfit")), mustache=ch.get("mustache", False), glasses=ch.get("glasses", False),
                           hair=ch.get("hair"), facing=ch.get("facing", 1), t=t, seed=self.idx * 10 + i, apron=ch.get("apron", False), beard=ch.get("beard", False))
            if ch.get("prop"):
                hx, hy = hands[1]
                prop(ctx, ch["prop"], hx, hy + 30, 0.6 * ch.get("s", 1.5) / 1.5, seed=i, t=t)
            if ch.get("name"):
                s_ = ch.get("s", 1.5); ty = yy - 330 * s_ - 40
                ctx.select_font_face("Special Elite"); ctx.set_font_size(34); tw = ctx.text_extents(ch["name"]).x_advance
                sbox(ctx, x - tw / 2 - 14, ty - 34, tw + 28, 48, (0.98, 0.97, 0.92), seed=i)
                ctx.set_source_rgb(*INK); ctx.move_to(x - tw / 2, ty + 2); ctx.show_text(ch["name"])
            if ch.get("bubble"):
                s_ = ch.get("s", 1.5); bx, by = x + 120 * s_, yy - 420 * s_
                ctx.select_font_face("Bebas Neue"); ctx.set_font_size(46); tw = ctx.text_extents(ch["bubble"]).x_advance
                scircle(ctx, bx + tw / 2, by, max(70, tw / 2 + 40), (1, 1, 1), seed=i)
                ctx.set_source_rgb(*INK); ctx.move_to(bx, by + 16); ctx.show_text(ch["bubble"])
            ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
        fx = p.get("fx")
        if fx == "fire": fire(ctx, 0, 1080, W, 260, t, self.idx)
        if fx in ("money", "confetti"):
            rnd = random.Random(self.idx)
            for k in range(60):
                xx = rnd.uniform(0, W); yy = (rnd.uniform(-H, 0) + t * rnd.uniform(150, 300)) % (H + 100) - 50
                ctx.save(); ctx.translate(xx, yy); ctx.rotate(t * rnd.uniform(-2, 2))
                if fx == "money": sbox(ctx, -30, -14, 60, 28, (0.55, 0.78, 0.5), seed=k)
                else: ctx.set_source_rgb(*[(0.9, 0.2, 0.2), (0.2, 0.5, 0.9), (1, 0.8, 0.1), (0.3, 0.75, 0.4)][k % 4]); ctx.rectangle(-8, -5, 16, 10); ctx.fill()
                ctx.restore()
        if fx == "rain":
            rnd = random.Random(int(t * 24)); ctx.set_source_rgba(0.5, 0.6, 0.8, 0.5); ctx.set_line_width(2)
            for _ in range(140): x_, y_ = rnd.uniform(0, W), rnd.uniform(0, H); ctx.move_to(x_, y_); ctx.line_to(x_ - 6, y_ + 30)
            ctx.stroke()
        ctx.restore()
        if p.get("caption"):
            cap = p["caption"]; ctx.select_font_face("Bebas Neue"); ctx.set_font_size(58); tw = ctx.text_extents(cap).x_advance
            a = ease((t - 0.3) / 0.4)
            ctx.save(); ctx.translate(W / 2, 90); ctx.rotate(-0.015)
            ctx.push_group(); sbox(ctx, -tw / 2 - 26, -42, tw + 52, 80, (0.98, 0.96, 0.88), seed=self.idx)
            ctx.set_source_rgb(0.75, 0.1, 0.1); ctx.move_to(-tw / 2, 20); ctx.show_text(cap); ctx.pop_group_to_source(); ctx.paint_with_alpha(a); ctx.restore()

class Words(v1.Scene):
    """dramatic serif text reveal. p: lines=["NOT JUST A MURDER.", "A SPARK."], strike=0 (index of a line to strike through), small (kicker)"""
    def frame(self, ctx, t):
        v1.radial_bg(ctx, (0.10, 0.13, 0.16), (0.01, 0.015, 0.02))
        noise_dots(ctx, 600, W, H, (1, 1, 1), 0.01, 0.05, 1.5, 3)
        lines = self.p.get("lines", []); n = len(lines)
        strike = self.p.get("strike", -1)
        if self.p.get("small"):
            v1.text(ctx, self.p["small"], W / 2, 300, "Special Elite", 40, (0.75, 0.78, 0.8), ease(t / 0.5), "c")
        for i, ln in enumerate(lines):
            t0 = 0.3 + i * 1.3
            size = 110 if i == n - 1 and n > 1 else 84
            y = H / 2 - (n - 1) * 75 + i * 150
            words = ln.split(); shown = []
            for k, w_ in enumerate(words):
                if t > t0 + k * 0.22: shown.append(w_)
            txt = " ".join(shown)
            ctx.select_font_face("DM Serif Display"); ctx.set_font_size(size)
            full_w = ctx.text_extents(ln).x_advance
            x0 = W / 2 - full_w / 2
            col = (0.95, 0.93, 0.88) if i != strike else (0.6, 0.6, 0.62)
            dot = i == n - 1 and n > 1 and ln.endswith(".")
            if dot and txt.endswith("."): txt = txt[:-1]
            ctx.set_source_rgb(*col); ctx.move_to(x0, y); ctx.show_text(txt)
            if dot and len(shown) == len(words):
                ctx.new_path(); ctx.set_source_rgb(0.85, 0.15, 0.15); ctx.arc(x0 + full_w - size * 0.12, y - 10, 11, 0, 7); ctx.fill()
            if i == strike and t > t0 + len(words) * 0.22 + 0.4:
                sw = full_w * ease((t - (t0 + len(words) * 0.22 + 0.4)) / 0.4)
                sline(ctx, [(x0 - 10, y - size * 0.3), (x0 - 10 + sw, y - size * 0.32)], 7, (0.85, 0.15, 0.15), 5, wobble=1.0)

class Portrait(v1.Scene):
    """framed sepia portrait of a stick character with typed name tags + optional red circle. p: name, role, char={...}, year, circle (bool)"""
    def frame(self, ctx, t):
        u = t / self.D
        v1.radial_bg(ctx, (0.12, 0.16, 0.17), (0.02, 0.03, 0.03))
        noise_dots(ctx, 900, W, H, (0.6, 0.7, 0.7), 0.02, 0.06, 2, 9)
        sc = 1.0 + 0.06 * u
        ctx.save(); ctx.translate(W / 2 - 120, H / 2 + 20); ctx.rotate(-0.04); ctx.scale(sc, sc)
        ctx.set_source_rgba(0, 0, 0, 0.5); ctx.rectangle(-286, -366, 590, 740); ctx.fill()
        ctx.set_source_rgb(0.93, 0.89, 0.8); ctx.rectangle(-300, -380, 600, 740); ctx.fill()
        ctx.set_source_rgb(0.72, 0.62, 0.48); ctx.rectangle(-260, -340, 520, 600); ctx.fill()
        g = cairo.RadialGradient(0, -60, 50, 0, -60, 420); g.add_color_stop_rgba(0, 1, 0.95, 0.85, 0.35); g.add_color_stop_rgba(1, 0.3, 0.2, 0.1, 0.4)
        ctx.set_source(g); ctx.rectangle(-260, -340, 520, 600); ctx.fill()
        ctx.save(); ctx.rectangle(-260, -340, 520, 600); ctx.clip()
        ch = self.p.get("char", {})
        figure(ctx, 0, 520, 2.6, ch.get("pose", "stand"), ch.get("face", "smile"), hat=ch.get("hat"), outfit=COLORS.get(ch.get("outfit", "navy")),
               mustache=ch.get("mustache", False), glasses=ch.get("glasses", False), hair=ch.get("hair"), beard=ch.get("beard", False), t=t, seed=self.idx)
        ctx.restore()
        if self.p.get("year"): v1.text(ctx, str(self.p["year"]), 0, 320, "Special Elite", 34, (0.3, 0.25, 0.2), 1, "c")
        if self.p.get("circle") and t > 1.6:
            k = ease((t - 1.6) / 0.6)
            ctx.set_source_rgba(0.85, 0.12, 0.12, 0.9); ctx.set_line_width(6)
            ctx.new_path(); ctx.save(); ctx.translate(20, -170); ctx.scale(1.5, 1.0); ctx.arc(0, 0, 110, 0, 2 * math.pi * k); ctx.restore(); ctx.stroke()
        ctx.restore()
        for k, (txt, size) in enumerate(((self.p.get("name", ""), 46), (self.p.get("role", ""), 34))):
            if not txt: continue
            a = t - 0.6 - k * 0.5
            if a <= 0: continue
            shown = txt[:int(len(txt) * min(1, a / 0.8))]
            ctx.select_font_face("Special Elite"); ctx.set_font_size(size); tw = ctx.text_extents(txt).x_advance
            x, y = W / 2 + 230, H / 2 - 200 + k * 80
            ctx.set_source_rgb(0.97, 0.96, 0.9); ctx.rectangle(x - 16, y - size, tw + 32, size * 1.35); ctx.fill()
            ctx.set_source_rgb(*INK); ctx.move_to(x, y); ctx.show_text(shown)

class BigDate(v1.Scene):
    """p: date (big), small (above), place"""
    def frame(self, ctx, t):
        v1.radial_bg(ctx, (0.10, 0.12, 0.14), (0.01, 0.01, 0.02))
        a = ease(t / 0.6)
        v1.text(ctx, self.p.get("small", ""), W / 2, H / 2 - 110, "Special Elite", 40, (0.8, 0.8, 0.8), a, "c")
        ctx.set_source_rgba(0.8, 0.8, 0.8, a); ctx.rectangle(W / 2 - 520, H / 2 - 30, 300 * a, 2); ctx.fill(); ctx.rectangle(W / 2 + 520 - 300 * a, H / 2 - 30, 300 * a, 2); ctx.fill()
        sc = 1 + 0.05 * t / self.D
        ctx.save(); ctx.translate(W / 2, H / 2 + 40); ctx.scale(sc, sc)
        v1.text(ctx, str(self.p.get("date", "")), 0, 0, "DM Serif Display", 170, (0.95, 0.93, 0.88), a, "c"); ctx.restore()
        v1.text(ctx, self.p.get("place", ""), W / 2, H / 2 + 160, "Special Elite", 38, (0.85, 0.3, 0.3), ease((t - 0.8) / 0.6), "c")

class Versus(v1.Scene):
    """two characters/brands face off. p: left={name, char}, right={name, char}, mid ('VS')"""
    def frame(self, ctx, t):
        ctx.set_source_rgb(0.85, 0.2, 0.2); ctx.rectangle(0, 0, W / 2, H); ctx.fill()
        ctx.set_source_rgb(0.2, 0.4, 0.8); ctx.rectangle(W / 2, 0, W / 2, H); ctx.fill()
        hatch(ctx, 0, 0, W, H, (0, 0, 0), 0.08)
        for side, key in ((-1, "left"), (1, "right")):
            d = self.p.get(key, {}); ch = d.get("char", {})
            x = W / 2 + side * 480
            a = ease((t - (0.1 if side < 0 else 0.5)) / 0.4)
            ctx.push_group()
            figure(ctx, x, 950, 2.0, ch.get("pose", "point"), ch.get("face", "angry"), hat=ch.get("hat"), outfit=COLORS.get(ch.get("outfit", "black")),
                   mustache=ch.get("mustache", False), glasses=ch.get("glasses", False), hair=ch.get("hair"), facing=-side, t=t, seed=side + 5)
            label(ctx, d.get("name", ""), x, 140, 100, (1, 1, 1))
            ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
        s = 1 + 0.15 * math.sin(t * 4)
        ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(s, s); scircle(ctx, 0, 0, 110, (1, 0.85, 0.1), seed=2); label(ctx, self.p.get("mid", "VS"), 0, 0, 110); ctx.restore()

REG3 = {"stick": Stick, "words": Words, "portrait": Portrait, "bigdate": BigDate, "versus": Versus}
