"""Stick-figure explainer drawing kit (hand-drawn look, pycairo).
Coordinates are in a 1920x1080 world. Everything is drawn with slightly wobbly lines for a hand-made feel."""
import cairo, math, random

INK = (0.08, 0.07, 0.07)
SKIN = (0.99, 0.98, 0.96)

def wob(rnd, a=1.6):
    return rnd.uniform(-a, a)

def sline(c, pts, width=6, col=INK, seed=0, close=False, wobble=1.4):
    """sketchy polyline through pts (list of (x,y)), subdivided with jitter"""
    rnd = random.Random(seed)
    c.set_source_rgb(*col); c.set_line_width(width); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    P = pts + ([pts[0]] if close else [])
    c.move_to(*P[0])
    for (x0, y0), (x1, y1) in zip(P, P[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 40))
        for k in range(1, n + 1):
            t = k / n
            c.line_to(x0 + (x1 - x0) * t + (wob(rnd, wobble) if k < n else 0), y0 + (y1 - y0) * t + (wob(rnd, wobble) if k < n else 0))
    c.stroke()

def sbox(c, x, y, w, h, fill, line=INK, lw=4, seed=0):
    c.new_path(); c.set_source_rgb(*fill); c.rectangle(x, y, w, h); c.fill()
    sline(c, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], lw, line, seed, True)

def spoly(c, pts, fill, line=INK, lw=4, seed=0):
    c.new_path(); c.set_source_rgb(*fill); c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.close_path(); c.fill()
    sline(c, pts, lw, line, seed, True)

def scircle(c, x, y, r, fill, line=INK, lw=4, seed=0):
    c.new_path(); c.set_source_rgb(*fill); c.arc(x, y, r, 0, 7); c.fill()
    rnd = random.Random(seed); n = 28
    pts = [(x + (r + wob(rnd, 1.2)) * math.cos(2 * math.pi * k / n), y + (r + wob(rnd, 1.2)) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    sline(c, pts, lw, line, seed, True, 0)

def label(c, txt, x, y, size, col=INK, fam="Bebas Neue", align="c", ang=0):
    c.save(); c.translate(x, y); c.rotate(ang)
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    w = c.text_extents(txt).x_advance
    c.move_to(-w / 2 if align == "c" else (-w if align == "r" else 0), size * 0.35); c.set_source_rgb(*col); c.show_text(txt); c.restore()

def sign(c, txt, x, y, w, h, bg=(0.25, 0.16, 0.1), fg=(0.98, 0.9, 0.7), size=None, seed=0, ang=0):
    c.save(); c.translate(x, y); c.rotate(ang)
    sbox(c, -w / 2, -h / 2, w, h, bg, seed=seed)
    label(c, txt, 0, 0, size or h * 0.62, fg)
    c.restore()

# ---------------------------------------------------------------- the mascot
POSES = {
    # (left arm angle, right arm angle, left elbow bend, right elbow bend) in degrees, 0 = down
    "stand": (15, -15, 0, 0), "point": (15, -110, 0, 0), "wave": (15, -150, 0, -40), "cheer": (150, -150, 10, -10),
    "think": (15, -140, 0, -120), "shrug": (70, -70, 60, -60), "hold": (40, -40, 50, -50), "sad": (8, -8, 0, 0),
    "shock": (130, -130, 30, -30), "walk": (35, -35, 0, 0), "present": (15, -80, 0, -20), "cross": (0, 0, 0, 0),
}

HAIRC = {"blonde": (0.93, 0.78, 0.42), "brown": (0.42, 0.28, 0.16), "dark": (0.12, 0.1, 0.09), "grey": (0.72, 0.72, 0.72),
         "white": (0.95, 0.95, 0.95), "red": (0.85, 0.42, 0.18), "ginger": (0.85, 0.42, 0.18), "silver": (0.82, 0.82, 0.85)}
# Famous-person caricature kit: signature looks only (hair, outfit, accessories). Drawn by us, never photos.
LOOKS = {
    "diana":       {"hair": "feather_blonde", "outfit": (0.2, 0.42, 0.78), "extras": ["dress", "pearls", "earrings"]},
    "diana_royal": {"hair": "feather_blonde", "outfit": (0.97, 0.97, 0.98), "extras": ["dress", "pearls", "earrings", "tiara", "sash"], "sash_col": (0.25, 0.45, 0.8)},
    "charles":     {"hair": "side_brown", "outfit": (0.16, 0.2, 0.33), "extras": ["big_ears", "tie"], "tie_col": (0.3, 0.45, 0.35)},
    "charles_old": {"hair": "side_grey", "outfit": (0.16, 0.2, 0.33), "extras": ["big_ears", "tie"], "tie_col": (0.5, 0.15, 0.2)},
    "king":        {"hair": "side_grey", "outfit": (0.55, 0.1, 0.15), "hat": "crown", "extras": ["big_ears", "sash", "medals"], "sash_col": (0.2, 0.35, 0.7)},
    "queen":       {"hair": "curls_grey", "outfit": (0.62, 0.78, 0.92), "hat": "royal_hat", "extras": ["coat", "pearls", "handbag"]},
    "queen_young": {"hair": "curls_brown", "outfit": (0.97, 0.97, 0.98), "extras": ["dress", "pearls", "tiara", "sash"], "sash_col": (0.25, 0.45, 0.8)},
    "philip":      {"hair": "slick_grey", "outfit": (0.12, 0.14, 0.22), "extras": ["tie", "medals"]},
    "camilla":     {"hair": "bob_blonde", "outfit": (0.45, 0.6, 0.5), "extras": ["coat", "pearls"]},
    "william":     {"hair": "receding_brown", "outfit": (0.16, 0.2, 0.33), "extras": ["tie"], "tie_col": (0.2, 0.3, 0.6)},
    "harry":       {"hair": "ginger", "outfit": (0.16, 0.2, 0.33), "beard": True, "extras": ["tie"], "tie_col": (0.35, 0.35, 0.4)},
    "einstein":    {"hair": "wild_white", "outfit": (0.4, 0.37, 0.35), "mustache": True},
    "napoleon":    {"hair": "dark", "outfit": (0.15, 0.2, 0.45), "hat": "bicorne", "extras": ["medals", "sash"], "sash_col": (0.85, 0.85, 0.85)},
    "lincoln":     {"hair": "dark", "outfit": (0.1, 0.1, 0.1), "hat": "top", "beard": True},
    "tycoon":      {"hair": "slick_grey", "outfit": (0.12, 0.12, 0.13), "hat": "top", "mustache": True, "extras": ["tie"]},
}

def figure(c, x, y, s=1.0, pose="stand", face="smile", hat=None, outfit=None, mustache=False, glasses=False, hair=None,
           facing=1, t=0.0, seed=0, prop=None, apron=False, beard=False, body_col=None, look=None):
    """stick figure standing with feet at (x, y). s=1 -> ~300 px tall.
    look: name in LOOKS (famous-person caricature kit) -> overrides hair/outfit/hat/etc. and adds extras."""
    LK = LOOKS.get(look, {}) if isinstance(look, str) else (look or {})
    if LK:
        outfit = LK.get("outfit", outfit); hat = LK.get("hat", hat); hair = LK.get("hair", hair)
        mustache = LK.get("mustache", mustache); beard = LK.get("beard", beard); glasses = LK.get("glasses", glasses)
    X = set(LK.get("extras", ()))
    rnd = random.Random(seed)
    c.save(); c.translate(x, y); c.scale(s * facing, s)
    bob = math.sin(t * 2.2 + seed) * 2
    lw = 7
    hip = (0, -120 + bob); neck = (0, -215 + bob); head = (0, -262 + bob)
    walk = pose == "walk"
    sw = math.sin(t * 6) * 18 if walk else 0
    # legs
    sline(c, [hip, (-22 + sw, -60), (-26 + sw, 0)], lw, INK, seed + 1)
    sline(c, [hip, (22 - sw, -60), (26 - sw, 0)], lw, INK, seed + 2)
    c.set_source_rgb(*INK); c.save(); c.translate(-26 + sw, 0); c.scale(1.5, 0.7); c.arc(-6, -4, 10, 0, 7); c.restore(); c.fill()
    c.save(); c.translate(26 - sw, 0); c.scale(1.5, 0.7); c.arc(6, -4, 10, 0, 7); c.restore(); c.fill()
    # torso / outfit
    if outfit:
        col = outfit
        spoly(c, [(-34, -218 + bob), (34, -218 + bob), (40, -112 + bob), (-40, -112 + bob)], col, seed=seed + 3)
        if apron: spoly(c, [(-26, -190 + bob), (26, -190 + bob), (30, -95 + bob), (-30, -95 + bob)], (0.97, 0.96, 0.92), seed=seed + 4)
    else:
        sline(c, [neck, hip], lw, INK, seed + 5)
    if "dress" in X and outfit:
        spoly(c, [(-40, -125 + bob), (40, -125 + bob), (62, -48 + bob), (-62, -48 + bob)], outfit, seed=seed + 31)
    if "coat" in X and outfit:
        spoly(c, [(-40, -125 + bob), (40, -125 + bob), (48, -70 + bob), (-48, -70 + bob)], outfit, seed=seed + 32)
        c.set_source_rgb(*INK)
        for k in range(3): c.arc(0, -195 + bob + k * 32, 4, 0, 7); c.fill()
    if "tie" in X:
        spoly(c, [(-6, -214 + bob), (6, -214 + bob), (9, -150 + bob), (0, -138 + bob), (-9, -150 + bob)], LK.get("tie_col", (0.55, 0.12, 0.15)), seed=seed + 33)
        spoly(c, [(-22, -218 + bob), (0, -196 + bob), (22, -218 + bob)], (0.97, 0.97, 0.97), seed=seed + 34)
    if "sash" in X:
        spoly(c, [(-34, -214 + bob), (-18, -218 + bob), (40, -128 + bob), (24, -116 + bob)], LK.get("sash_col", (0.2, 0.35, 0.7)), seed=seed + 35)
    if "medals" in X:
        for k, col in enumerate(((0.9, 0.75, 0.2), (0.8, 0.2, 0.2), (0.9, 0.75, 0.2))):
            c.set_source_rgb(*col); c.arc(-20 + k * 11, -180 + bob, 5, 0, 7); c.fill()
    # arms
    la, ra, lb, rb = POSES.get(pose, POSES["stand"])
    if pose == "wave": rb += math.sin(t * 8) * 18
    if pose == "cheer": la += math.sin(t * 7) * 10; ra -= math.sin(t * 7) * 10
    if walk: la += sw; ra += sw
    sh = (0, -205 + bob)
    hands = []
    if pose == "cross":
        for side in (-1, 1):
            pts = [(side * 8, sh[1]), (side * 46, sh[1] + 48), (-side * 34, sh[1] + 62 + (6 if side > 0 else 0))]
            sline(c, pts, lw + 2, INK, seed + 6 + side)
            hx, hy = pts[-1]
            c.set_source_rgb(*SKIN); c.arc(hx, hy, 9, 0, 7); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
            hands.append((hx, hy))
    for side, ang, bend in (() if pose == "cross" else ((-1, la, lb), (1, ra, rb))):
        a1 = math.radians(ang); L = 62
        ex, ey = sh[0] + side * 8 + math.sin(a1) * L * (-1 if side < 0 else 1) * -1, sh[1] + math.cos(a1) * L
        # simpler: angle measured from down, positive = outward
        ex = sh[0] + side * (8 + math.sin(abs(a1)) * L); ey = sh[1] + math.cos(a1) * L
        a2 = a1 + math.radians(bend)
        hx = ex + side * math.sin(abs(a2)) * L; hy = ey + math.cos(a2) * L
        sline(c, [(sh[0] + side * 6, sh[1]), (ex, ey), (hx, hy)], lw, INK, seed + 6 + side)
        c.set_source_rgb(*SKIN); c.arc(hx, hy, 9, 0, 7); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
        hands.append((hx, hy))
    # head
    if "big_ears" in X:
        for dx in (-50, 46):
            scircle(c, head[0] + dx, head[1] + 4, 16, SKIN, INK, 5, seed + 40)
    if hair in ("long_blonde", "long_dark", "long_red"):
        hc = HAIRC[hair.split("_")[1]]
        c.set_source_rgb(*hc); c.move_to(head[0] - 52, head[1] - 10); c.curve_to(head[0] - 60, head[1] + 60, head[0] - 40, head[1] + 90, head[0] - 20, head[1] + 80)
        c.line_to(head[0] + 40, head[1] + 80); c.curve_to(head[0] + 60, head[1] + 60, head[0] + 56, head[1], head[0] + 50, head[1] - 10); c.close_path(); c.fill()
    scircle(c, head[0], head[1], 46, SKIN, INK, 6, seed + 9)
    hx0, hy0 = head
    if hair in HAIRC or (isinstance(hair, str) and hair.split("_")[0] in ("feather", "side", "curls", "bob", "wild", "slick", "receding", "long", "ginger")):
        style, _, colname = hair.partition("_")
        hc = HAIRC.get(colname, HAIRC.get(style, INK))
        c.set_source_rgb(*hc)
        if style == "feather":   # Diana: short, voluminous, feathered with a side fringe
            c.move_to(hx0 - 52, hy0 + 14); c.curve_to(hx0 - 70, hy0 - 40, hx0 - 40, hy0 - 78, hx0 + 4, hy0 - 70)
            c.curve_to(hx0 + 50, hy0 - 74, hx0 + 70, hy0 - 30, hx0 + 52, hy0 + 6); c.curve_to(hx0 + 40, hy0 - 30, hx0 + 20, hy0 - 34, hx0 - 6, hy0 - 22)
            c.curve_to(hx0 - 26, hy0 - 26, hx0 - 40, hy0 - 10, hx0 - 52, hy0 + 14); c.fill()
            c.set_source_rgba(0.75, 0.55, 0.2, 0.7); c.set_line_width(3)
            for k in range(4): c.move_to(hx0 - 30 + k * 18, hy0 - 60); c.curve_to(hx0 - 20 + k * 18, hy0 - 46, hx0 - 10 + k * 18, hy0 - 36, hx0 + k * 18, hy0 - 30); c.stroke()
        elif style == "side":    # neat side parting (Charles, William)
            c.move_to(hx0 - 48, hy0 - 2); c.curve_to(hx0 - 52, hy0 - 52, hx0 - 10, hy0 - 66, hx0 + 30, hy0 - 52)
            c.curve_to(hx0 + 46, hy0 - 44, hx0 + 50, hy0 - 26, hx0 + 48, hy0 - 12); c.curve_to(hx0 + 20, hy0 - 36, hx0 - 10, hy0 - 40, hx0 - 22, hy0 - 34)
            c.curve_to(hx0 - 34, hy0 - 26, hx0 - 42, hy0 - 14, hx0 - 48, hy0 - 2); c.fill()
            c.set_source_rgb(*SKIN); c.set_line_width(3); c.move_to(hx0 - 18, hy0 - 58); c.line_to(hx0 - 22, hy0 - 36); c.stroke()
        elif style == "receding":
            c.arc(hx0 - 42, hy0 - 6, 14, 0, 7); c.fill(); c.arc(hx0 + 42, hy0 - 6, 14, 0, 7); c.fill()
            c.arc(hx0 - 36, hy0 - 26, 12, 0, 7); c.fill(); c.arc(hx0 + 36, hy0 - 26, 12, 0, 7); c.fill()
        elif style == "curls":   # tight curls around the head (the Queen)
            for k in range(11):
                a_ = math.pi * (0.95 + k * 0.11); r_ = 46
                c.arc(hx0 + math.cos(a_) * r_, hy0 + math.sin(a_) * r_ + 2, 14, 0, 7); c.fill()
            c.set_source_rgb(*INK); c.set_line_width(2)
            for k in range(11):
                a_ = math.pi * (0.95 + k * 0.11); c.arc(hx0 + math.cos(a_) * 46, hy0 + math.sin(a_) * 46 + 2, 7, 0, 5); c.stroke()
        elif style == "bob":     # rounded bob (Camilla)
            c.move_to(hx0 - 56, hy0 + 30); c.curve_to(hx0 - 70, hy0 - 60, hx0 + 70, hy0 - 80, hx0 + 56, hy0 + 30)
            c.curve_to(hx0 + 44, hy0 - 20, hx0 + 10, hy0 - 40, hx0 - 10, hy0 - 26); c.curve_to(hx0 - 30, hy0 - 10, hx0 - 44, hy0 + 10, hx0 - 56, hy0 + 30); c.fill()
        elif style == "wild":    # Einstein-style wild hair
            for k in range(14):
                a_ = math.pi * (0.85 + k * 0.095); r_ = 50 + (k % 3) * 10
                c.move_to(hx0 + math.cos(a_) * 40, hy0 + math.sin(a_) * 40); c.line_to(hx0 + math.cos(a_ + 0.08) * r_ * 1.3, hy0 + math.sin(a_ + 0.08) * r_ * 1.3)
                c.line_to(hx0 + math.cos(a_ + 0.2) * 40, hy0 + math.sin(a_ + 0.2) * 40); c.close_path()
                c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(2.5); c.stroke(); c.set_source_rgb(*hc)
        elif style == "slick":   # slicked back
            c.arc(hx0, hy0 - 6, 48, math.pi * 1.02, math.pi * 1.98); c.fill()
        elif style == "ginger":  # short ginger crop
            c.arc(hx0, hy0 - 8, 48, math.pi * 1.05, math.pi * 1.95); c.fill()
        elif style == "long":
            c.arc(hx0, hy0 - 6, 50, math.pi * 1.0, math.pi * 2.0); c.fill()
    if hair == "bald" or (isinstance(hair, str) and "_" in hair): pass
    elif hair == "dark":
        c.set_source_rgb(*INK); c.arc(head[0] - 6, head[1] - 8, 44, math.pi * 1.1, math.pi * 1.75); c.fill()
    elif hair == "grey":
        c.set_source_rgb(0.75, 0.75, 0.75); c.arc(head[0] - 30, head[1] - 10, 18, 0, 7); c.fill(); c.arc(head[0] + 30, head[1] - 10, 18, 0, 7); c.fill()
    # face (looks to the right)
    ex_, ey_ = head[0] + 12, head[1] - 6
    blink = (t * 0.7 + seed * 0.13) % 3 < 0.08
    for dx in (-14, 14):
        if blink:
            sline(c, [(ex_ + dx - 6, ey_), (ex_ + dx + 6, ey_)], 4, INK, seed)
        else:
            c.set_source_rgb(*INK); c.arc(ex_ + dx, ey_, 5.5 if face != "shock" else 7, 0, 7); c.fill()
    if glasses:
        c.set_source_rgb(*INK); c.set_line_width(3.5)
        for dx in (-14, 14): c.arc(ex_ + dx, ey_, 12, 0, 7); c.stroke()
        c.move_to(ex_ - 2, ey_); c.line_to(ex_ + 2, ey_); c.stroke()
    my = head[1] + 20
    c.set_source_rgb(*INK); c.set_line_width(4)
    if face == "smile": c.arc(head[0] + 12, my - 8, 14, 0.2, math.pi - 0.2); c.stroke()
    elif face == "grin":
        c.move_to(head[0] - 6, my - 4); c.arc(head[0] + 12, my - 4, 18, 0, math.pi); c.close_path(); c.fill()
    elif face == "sad": c.arc_negative(head[0] + 12, my + 8, 12, -0.3, math.pi + 0.3); c.stroke()
    elif face == "shock": c.arc(head[0] + 12, my, 9, 0, 7); c.fill()
    elif face == "smirk": c.move_to(head[0], my); c.curve_to(head[0] + 10, my + 4, head[0] + 20, my, head[0] + 28, my - 8); c.stroke()
    else: c.move_to(head[0] + 2, my); c.line_to(head[0] + 22, my); c.stroke()
    if face in ("angry", "think"):
        sline(c, [(ex_ - 22, ey_ - 18), (ex_ - 6, ey_ - 12)], 4, INK, seed); sline(c, [(ex_ + 6, ey_ - 12), (ex_ + 22, ey_ - 18)], 4, INK, seed)
    if mustache:
        c.set_source_rgb(*INK); c.save(); c.translate(head[0] + 12, my - 14)
        c.move_to(0, 0); c.curve_to(-10, -8, -26, -2, -28, 6); c.curve_to(-16, 2, -6, 6, 0, 2); c.curve_to(6, 6, 16, 2, 28, 6); c.curve_to(26, -2, 10, -8, 0, 0); c.fill(); c.restore()
    if beard:
        c.set_source_rgb(*INK); c.move_to(head[0] - 30, head[1] + 18); c.curve_to(head[0] - 10, head[1] + 70, head[0] + 34, head[1] + 70, head[0] + 42, head[1] + 18); c.curve_to(head[0] + 20, head[1] + 40, head[0] - 10, head[1] + 40, head[0] - 30, head[1] + 18); c.fill()
    if hat == "top":
        sbox(c, head[0] - 34, head[1] - 118, 68, 78, INK, seed=seed); sbox(c, head[0] - 54, head[1] - 46, 108, 10, INK, seed=seed)
    elif hat == "bowler":
        c.set_source_rgb(*INK); c.arc(head[0], head[1] - 36, 38, math.pi, 2 * math.pi); c.fill(); c.rectangle(head[0] - 52, head[1] - 40, 104, 9); c.fill()
    elif hat == "cap":
        c.set_source_rgb(0.2, 0.35, 0.6); c.arc(head[0], head[1] - 22, 46, math.pi, 2 * math.pi); c.fill(); c.rectangle(head[0], head[1] - 26, 70, 10); c.fill()
    elif hat == "hard":
        c.set_source_rgb(1, 0.8, 0.1); c.arc(head[0], head[1] - 24, 48, math.pi, 2 * math.pi); c.fill(); c.rectangle(head[0] - 58, head[1] - 28, 116, 10); c.fill()
    elif hat == "crown":
        spoly(c, [(head[0] - 40, head[1] - 40), (head[0] - 40, head[1] - 90), (head[0] - 20, head[1] - 65), (head[0], head[1] - 95), (head[0] + 20, head[1] - 65), (head[0] + 40, head[1] - 90), (head[0] + 40, head[1] - 40)], (1, 0.8, 0.15), seed=seed)
    elif hat == "royal_hat":   # the Queen's pastel hat with a flower
        hc = LK.get("hat_col", (0.62, 0.78, 0.92))
        c.set_source_rgb(*hc); c.save(); c.translate(head[0], head[1] - 44); c.scale(1.5, 0.35); c.arc(0, 0, 44, 0, 7); c.restore(); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
        spoly(c, [(head[0] - 40, head[1] - 46), (head[0] - 34, head[1] - 92), (head[0] + 34, head[1] - 92), (head[0] + 40, head[1] - 46)], hc, seed=seed)
        for k in range(5):
            c.set_source_rgb(0.95, 0.6, 0.7); c.arc(head[0] + 22 + math.cos(k * 1.26) * 9, head[1] - 66 + math.sin(k * 1.26) * 9, 7, 0, 7); c.fill()
        c.set_source_rgb(1, 0.85, 0.3); c.arc(head[0] + 22, head[1] - 66, 5, 0, 7); c.fill()
    elif hat == "bicorne":
        c.set_source_rgb(*INK); c.move_to(head[0] - 80, head[1] - 34); c.curve_to(head[0] - 40, head[1] - 110, head[0] + 40, head[1] - 110, head[0] + 80, head[1] - 34); c.close_path(); c.fill()
        c.set_source_rgb(0.75, 0.15, 0.15); c.arc(head[0] + 10, head[1] - 70, 8, 0, 7); c.fill()
    if "tiara" in X:
        pts = [(head[0] - 34, head[1] - 52)]
        for k in range(7):
            xx = head[0] - 30 + k * 10; pts += [(xx, head[1] - (78 if k == 3 else 66 if k % 2 else 58)), (xx + 5, head[1] - 56)]
        pts += [(head[0] + 36, head[1] - 52)]
        spoly(c, pts, (0.86, 0.88, 0.95), seed=seed)
        for k in (-20, 0, 20): c.set_source_rgb(0.4, 0.6, 0.95); c.arc(head[0] + k, head[1] - 58, 4, 0, 7); c.fill()
    if "pearls" in X:
        for k in range(9):
            a_ = math.pi * (0.15 + k * 0.0875)
            scircle(c, head[0] + math.cos(a_) * 30, head[1] + 44 + math.sin(a_) * 10, 6, (0.98, 0.97, 0.94), INK, 2, seed + k)
    if "earrings" in X:
        for dx in (-44, 44): c.set_source_rgb(0.98, 0.97, 0.94); c.arc(head[0] + dx, head[1] + 22, 6, 0, 7); c.fill()
    if "handbag" in X:
        bx, by = (hands[0] if hands else (-60, -110))
        c.set_source_rgb(*INK); c.set_line_width(4); c.arc(bx, by + 18, 16, math.pi, 2 * math.pi); c.stroke()
        sbox(c, bx - 24, by + 16, 48, 36, LK.get("bag_col", (0.12, 0.12, 0.13)), seed=seed)
    c.restore()
    # world hand positions
    return [(x + hx * s * facing, y + hy * s) for hx, hy in hands]

# ---------------------------------------------------------------- environments
def paper(c, W, H, base=(0.96, 0.92, 0.84), seed=0):
    c.set_source_rgb(*base); c.paint()
    rnd = random.Random(seed)
    for _ in range(2500):
        c.set_source_rgba(0.4, 0.3, 0.2, rnd.uniform(0.01, 0.05)); c.arc(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.5, 2.5), 0, 7); c.fill()

def hatch(c, x, y, w, h, col=(0.2, 0.15, 0.1), a=0.12, step=14, seed=0):
    c.save(); c.rectangle(x, y, w, h); c.clip(); c.set_source_rgba(*col, a); c.set_line_width(2)
    for k in range(-int(h), int(w), step): c.move_to(x + k, y + h); c.line_to(x + k + h, y); c.stroke()
    c.restore()

def wood_floor(c, W, y0, H, col=(0.62, 0.42, 0.25), seed=0):
    sbox(c, -10, y0, W + 20, H - y0 + 10, col, seed=seed)
    rnd = random.Random(seed)
    for k in range(int(y0) + 30, H, 38): sline(c, [(0, k), (W, k + rnd.uniform(-3, 3))], 2, (0.35, 0.22, 0.12), seed + k)

def shelves(c, x, y, w, rows, items_fn, seed=0, col=(0.5, 0.32, 0.18)):
    for r in range(rows):
        yy = y + r * 150
        sbox(c, x, yy + 110, w, 16, col, seed=seed + r)
        items_fn(c, x, yy, w, r)

def window(c, x, y, w, h, sky=(0.65, 0.82, 0.95), seed=0):
    sbox(c, x, y, w, h, sky, seed=seed); sline(c, [(x + w / 2, y), (x + w / 2, y + h)], 5, INK, seed); sline(c, [(x, y + h / 2), (x + w, y + h / 2)], 5, INK, seed)

def building(c, x, ground, w, h, col, seed=0, sign_txt=None, windows=True, roof=True):
    sbox(c, x, ground - h, w, h, col, seed=seed)
    hatch(c, x, ground - h, w, h, a=0.06, seed=seed)
    if roof: spoly(c, [(x - 12, ground - h), (x + w / 2, ground - h - h * 0.3), (x + w + 12, ground - h)], (0.45, 0.2, 0.15), seed=seed)
    if windows:
        for i in range(max(1, int(w / 110))):
            for j in range(max(1, int(h / 140))):
                window(c, x + 25 + i * 110, ground - h + 30 + j * 130, 60, 70, (0.98, 0.85, 0.5), seed + i + j)
    if sign_txt: sign(c, sign_txt, x + w / 2, ground - h + 16 if not roof else ground - h - 10, min(w - 20, 40 + 22 * len(sign_txt)), 50, seed=seed)

def crowd(c, x0, x1, ground, rows=3, seed=0, t=0.0, cheer=False, scale=0.45):
    rnd = random.Random(seed)
    for r in range(rows):
        s = scale * (0.8 + 0.12 * r)
        y = ground - 30 * (rows - 1 - r)
        n = int((x1 - x0) / (90 * s))
        for i in range(n):
            x = x0 + (i + 0.5) * (x1 - x0) / n + rnd.uniform(-12, 12)
            figure(c, x, y, s, "cheer" if (cheer and rnd.random() < 0.6) else "stand", "grin" if cheer else "smile", t=t, seed=seed + r * 100 + i,
                   hat=rnd.choice([None, None, "bowler", "cap"]), outfit=rnd.choice([None, (0.3, 0.4, 0.6), (0.6, 0.3, 0.3), (0.35, 0.5, 0.35)]))

# ---------------------------------------------------------------- props
def lego_brick(c, x, y, w, col, seed=0, studs=4):
    h = w * 0.45
    sbox(c, x, y, w, h, col, seed=seed)
    for k in range(studs):
        sx = x + (k + 0.5) * w / studs
        sbox(c, sx - w / studs * 0.3, y - h * 0.28, w / studs * 0.6, h * 0.28, col, seed=seed + k)
    c.set_source_rgba(1, 1, 1, 0.25); c.rectangle(x + 6, y + 6, w - 12, 8); c.fill()

def wooden_duck(c, x, y, s=1.0, seed=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    spoly(c, [(-60, 0), (60, 0), (70, -40), (30, -50), (20, -90), (-10, -100), (-25, -80), (-20, -50), (-70, -40)], (0.85, 0.65, 0.35), seed=seed)
    spoly(c, [(-25, -85), (-50, -80), (-25, -72)], (0.95, 0.55, 0.15), seed=seed)
    c.set_source_rgb(*INK); c.arc(-8, -82, 4, 0, 7); c.fill()
    for wx in (-35, 35): scircle(c, wx, 8, 16, (0.55, 0.35, 0.2), seed=seed)
    c.restore()

def fire(c, x, y, w, h, t, seed=0):
    rnd = random.Random(seed)
    for k in range(int(w / 40)):
        fx = x + k * 40 + rnd.uniform(-10, 10); fh = h * (0.6 + 0.4 * math.sin(t * 7 + k))
        for col, sc in (((0.95, 0.35, 0.1), 1.0), ((1, 0.75, 0.2), 0.65), ((1, 0.95, 0.6), 0.3)):
            c.set_source_rgba(*col, 0.92); c.move_to(fx - 30 * sc, y); c.curve_to(fx - 30 * sc, y - fh * sc * 0.6, fx + rnd.uniform(-10, 10), y - fh * sc, fx, y - fh * sc)
            c.curve_to(fx, y - fh * sc, fx + 30 * sc, y - fh * sc * 0.6, fx + 30 * sc, y); c.close_path(); c.fill()

def big_calendar(c, x, y, txt, sub, seed=0):
    sbox(c, x - 220, y - 200, 440, 400, (0.98, 0.97, 0.93), seed=seed)
    sbox(c, x - 220, y - 200, 440, 110, (0.85, 0.15, 0.15), seed=seed)
    for k in range(5): scircle(c, x - 170 + k * 85, y - 200, 14, (0.6, 0.6, 0.6), seed=seed + k)
    label(c, sub, x, y - 145, 70, (1, 1, 1))
    label(c, txt, x, y + 40, 200, INK)

def chart(c, x, y, w, h, vals, col=(0.2, 0.6, 0.3), seed=0, title=None, t=1.0):
    sbox(c, x, y, w, h, (0.99, 0.98, 0.95), seed=seed)
    n = len(vals); mx = max(vals)
    pts = [(x + 40 + i * (w - 80) / (n - 1), y + h - 40 - (v / mx) * (h - 120)) for i, v in enumerate(vals)]
    k = max(2, int(len(pts) * min(1, t)))
    sline(c, pts[:k], 9, col, seed, wobble=0.6)
    if title: label(c, title, x + w / 2, y + 40, 48)
