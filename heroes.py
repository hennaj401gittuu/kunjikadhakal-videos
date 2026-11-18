"""Kunjikadhakal recurring heroes: Ambadi (baby elephant) and Nila (little girl).

Shared pycairo drawing code so every video draws the two heroes the same way.

    import cairo, heroes
    heroes.draw_ambadi(ctx, x, y, scale=1.0, facing=1, mouth=0.0, blink=False,
                       expression="happy", t=0.0, trunk="down")
    heroes.draw_nila(ctx, x, y, scale=1.0, facing=1, mouth=0.0, blink=False,
                     expression="happy", t=0.0, arms="down")

(x, y) is the point on the ground between the feet. At scale 1.0 Ambadi is about
300 px tall and Nila about 260 px tall, so Nila's head is a little lower than
Ambadi's. facing=1 looks right, -1 looks left. mouth 0..1 drives lip-sync.
expression: happy | sad | shocked | angry | sleepy | laugh.
t is time in seconds (idle bob, ear flap, pigtail sway).
trunk: down | up (trumpeting) | curl (holding something). arms: down | up | wave | point.
"""
import math

# ---- palette (keep these fixed: they are the characters' identity) ----
AMB_SKIN = (0.56, 0.62, 0.72)        # soft blue-grey
AMB_SKIN_DARK = (0.42, 0.47, 0.57)
AMB_SKIN_LIGHT = (0.70, 0.76, 0.85)
AMB_EAR_IN = (0.97, 0.72, 0.76)      # pink inner ear
AMB_CAP = (0.82, 0.12, 0.16)         # red forehead cap
AMB_GOLD = (0.98, 0.78, 0.18)
OUTLINE = (0.24, 0.16, 0.12)         # dark brown outlines
CHEEK = (1.0, 0.55, 0.60)

NILA_SKIN = (0.80, 0.56, 0.40)
NILA_SKIN_DARK = (0.66, 0.43, 0.30)
NILA_HAIR = (0.10, 0.07, 0.07)
NILA_SKIRT = (0.99, 0.80, 0.16)      # yellow pavada
NILA_BORDER = (0.12, 0.62, 0.30)     # green border
NILA_BLOUSE = (0.16, 0.66, 0.36)     # green blouse
JASMINE = (1.0, 1.0, 0.96)


def _ell(ctx, cx, cy, rx, ry):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()


def _fill_stroke(ctx, fill, lw=4, stroke=OUTLINE):
    ctx.set_source_rgb(*fill); ctx.fill_preserve()
    ctx.set_source_rgb(*stroke); ctx.set_line_width(lw); ctx.stroke()


def _vgrad(ctx, y0, y1, top, bottom):
    import cairo
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bottom)
    return g


def _grad_fill_stroke(ctx, y0, y1, top, bottom, lw=4):
    ctx.set_source(_vgrad(ctx, y0, y1, top, bottom)); ctx.fill_preserve()
    ctx.set_source_rgb(*OUTLINE); ctx.set_line_width(lw); ctx.stroke()


def _eye(ctx, cx, cy, r, expression, blink, look=0.25):
    """Big glossy eye. look shifts the pupil towards the facing side."""
    if blink or expression == "sleepy":
        ctx.set_source_rgb(*OUTLINE); ctx.set_line_width(4)
        ctx.move_to(cx - r, cy); ctx.curve_to(cx - r * 0.4, cy + r * 0.6, cx + r * 0.4, cy + r * 0.6, cx + r, cy)
        ctx.stroke(); return
    if expression == "laugh":
        ctx.set_source_rgb(*OUTLINE); ctx.set_line_width(5)
        ctx.move_to(cx - r, cy + r * 0.2); ctx.curve_to(cx - r * 0.4, cy - r * 0.8, cx + r * 0.4, cy - r * 0.8, cx + r, cy + r * 0.2)
        ctx.stroke(); return
    big = 1.25 if expression == "shocked" else 1.0
    _ell(ctx, cx, cy, r * 0.85 * big, r * big); _fill_stroke(ctx, (1, 1, 1), 3)
    pr = r * (0.42 if expression == "shocked" else 0.62)
    _ell(ctx, cx + look * r * 0.5, cy + r * 0.12, pr * 0.9, pr); ctx.set_source_rgb(0.12, 0.08, 0.06); ctx.fill()
    _ell(ctx, cx + look * r * 0.5 - pr * 0.35, cy - pr * 0.3, pr * 0.32, pr * 0.32); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    _ell(ctx, cx + look * r * 0.5 + pr * 0.3, cy + pr * 0.35, pr * 0.14, pr * 0.14); ctx.set_source_rgb(1, 1, 1); ctx.fill()


def _brow(ctx, cx, cy, w, expression, side):
    ctx.set_source_rgb(*OUTLINE); ctx.set_line_width(5); ctx.set_line_cap(1)
    inner = side  # +1: inner end towards +x
    if expression == "angry":
        ctx.move_to(cx - w * inner, cy - 6); ctx.line_to(cx + w * inner, cy + 6)
    elif expression in ("sad", "sleepy"):
        ctx.move_to(cx - w * inner, cy + 5); ctx.line_to(cx + w * inner, cy - 6)
    elif expression == "shocked":
        ctx.move_to(cx - w, cy - 10); ctx.curve_to(cx - w * 0.3, cy - 22, cx + w * 0.3, cy - 22, cx + w, cy - 10)
    else:
        ctx.move_to(cx - w, cy); ctx.curve_to(cx - w * 0.3, cy - 8, cx + w * 0.3, cy - 8, cx + w, cy)
    ctx.stroke()


def _mouth(ctx, cx, cy, w, expression, mouth):
    """mouth 0..1 opens the mouth for lip-sync on top of the expression."""
    ctx.set_line_width(4); ctx.set_line_cap(1)
    if expression == "shocked":
        _ell(ctx, cx, cy + 4, w * 0.35, w * (0.35 + 0.25 * mouth)); _fill_stroke(ctx, (0.45, 0.10, 0.12), 3); return
    if mouth > 0.08 or expression == "laugh":
        o = max(mouth, 0.7 if expression == "laugh" else 0)
        ctx.move_to(cx - w * 0.55, cy)
        if expression in ("sad", "angry"):
            ctx.curve_to(cx - w * 0.3, cy - 4, cx + w * 0.3, cy - 4, cx + w * 0.55, cy)
            ctx.curve_to(cx + w * 0.3, cy + w * 0.5 * o, cx - w * 0.3, cy + w * 0.5 * o, cx - w * 0.55, cy)
        else:
            ctx.curve_to(cx - w * 0.3, cy + 4, cx + w * 0.3, cy + 4, cx + w * 0.55, cy)
            ctx.curve_to(cx + w * 0.35, cy + w * 0.75 * o + 6, cx - w * 0.35, cy + w * 0.75 * o + 6, cx - w * 0.55, cy)
        ctx.close_path(); _fill_stroke(ctx, (0.50, 0.12, 0.14), 3)
        _ell(ctx, cx, cy + w * 0.35 * o + 2, w * 0.22, w * 0.12 * o + 1); ctx.set_source_rgb(0.95, 0.45, 0.50); ctx.fill()
        return
    ctx.set_source_rgb(*OUTLINE)
    if expression in ("sad",):
        ctx.move_to(cx - w * 0.4, cy + 6); ctx.curve_to(cx - w * 0.1, cy - 6, cx + w * 0.1, cy - 6, cx + w * 0.4, cy + 6)
    elif expression == "angry":
        ctx.move_to(cx - w * 0.35, cy + 2); ctx.line_to(cx + w * 0.35, cy + 2)
    elif expression == "sleepy":
        _ell(ctx, cx, cy + 2, w * 0.12, w * 0.1); ctx.stroke(); return
    else:
        ctx.move_to(cx - w * 0.5, cy - 2); ctx.curve_to(cx - w * 0.2, cy + 14, cx + w * 0.2, cy + 14, cx + w * 0.5, cy - 2)
    ctx.stroke()


# --------------------------------------------------------------------------
def draw_ambadi(ctx, x, y, scale=1.0, facing=1, mouth=0.0, blink=False,
                expression="happy", t=0.0, trunk="down"):
    """Ambadi (അമ്പാടി): a small, cheerful baby elephant from Pachakkunnu village.
    Blue-grey, pink inner ears, big glossy eyes, tiny tusk nubs, a red forehead cap
    with gold dots (a mini nettipattam) and a little brass bell on a red cord."""
    bob = math.sin(t * 2.2) * 3
    flap = math.sin(t * 3.1) * 0.08
    ctx.save()
    ctx.translate(x, y + bob); ctx.scale(scale * facing, scale)
    # legs (back)
    for lx in (-70, 40):
        ctx.rectangle(lx - 4, -95, 46, 95); _fill_stroke(ctx, AMB_SKIN_DARK)
    # body
    _ell(ctx, -10, -125, 120, 85); _grad_fill_stroke(ctx, -210, -40, AMB_SKIN_LIGHT, AMB_SKIN_DARK)
    # tail
    ctx.set_source_rgb(*OUTLINE); ctx.set_line_width(5)
    ctx.move_to(-128, -140); ctx.curve_to(-150, -130, -150, -105, -140, -95 + math.sin(t * 4) * 6); ctx.stroke()
    _ell(ctx, -140, -92 + math.sin(t * 4) * 6, 7, 10); ctx.set_source_rgb(*OUTLINE); ctx.fill()
    # legs (front)
    for lx in (-40, 70):
        ctx.rectangle(lx - 4, -90, 48, 90); _grad_fill_stroke(ctx, -90, 0, AMB_SKIN, AMB_SKIN_DARK)
        for k in range(3):
            _ell(ctx, lx + 8 + k * 14, -6, 6, 4); ctx.set_source_rgb(0.93, 0.92, 0.88); ctx.fill()
    # back ear
    ctx.save(); ctx.translate(40, -215); ctx.rotate(-0.15 - flap)
    _ell(ctx, -30, 20, 55, 65); _fill_stroke(ctx, AMB_SKIN_DARK); ctx.restore()
    # head
    _ell(ctx, 95, -215, 92, 85); _grad_fill_stroke(ctx, -300, -130, AMB_SKIN_LIGHT, AMB_SKIN)
    # front ear
    ctx.save(); ctx.translate(30, -225); ctx.rotate(0.12 + flap)
    _ell(ctx, -20, 20, 62, 72); _grad_fill_stroke(ctx, -50, 90, AMB_SKIN_LIGHT, AMB_SKIN_DARK)
    _ell(ctx, -16, 22, 42, 52); ctx.set_source_rgb(*AMB_EAR_IN); ctx.fill()
    ctx.restore()
    # forehead cap (mini nettipattam)
    ctx.move_to(70, -292); ctx.curve_to(95, -305, 135, -305, 155, -288)
    ctx.line_to(140, -245); ctx.curve_to(125, -232, 105, -232, 92, -245); ctx.close_path()
    _fill_stroke(ctx, AMB_CAP, 3)
    for (dx, dy) in ((88, -285), (112, -290), (136, -284), (100, -265), (126, -265), (114, -246)):
        _ell(ctx, dx, dy, 5, 5); _fill_stroke(ctx, AMB_GOLD, 1.5)
    # trunk: a thick tube drawn as two strokes (outline, then skin)
    sway = math.sin(t * 2.6) * 5
    if trunk == "up":
        path = [(150, -200), (205, -205), (230, -250), (215, -295 + sway)]
    elif trunk == "curl":
        path = [(150, -195), (205, -175), (220, -130), (190, -118 + sway)]
    else:
        path = [(150, -195), (198, -175), (205, -125), (232 + sway, -98)]
    for w, col in ((44, OUTLINE), (36, AMB_SKIN)):
        ctx.set_line_width(w); ctx.set_line_cap(1); ctx.set_line_join(1); ctx.set_source_rgb(*col)
        ctx.move_to(*path[0]); ctx.curve_to(*path[1], *path[2], *path[3]); ctx.stroke()
    tx, ty = path[3]
    _ell(ctx, tx, ty, 17, 14); _fill_stroke(ctx, AMB_SKIN_LIGHT, 3)
    _ell(ctx, tx + 3, ty + 1, 4, 3); ctx.set_source_rgb(*OUTLINE); ctx.fill()
    ctx.set_source_rgba(*OUTLINE, 0.45); ctx.set_line_width(2.5)
    for k in (0.35, 0.55, 0.75):
        px = (1-k)**3*path[0][0] + 3*(1-k)**2*k*path[1][0] + 3*(1-k)*k*k*path[2][0] + k**3*path[3][0]
        py = (1-k)**3*path[0][1] + 3*(1-k)**2*k*path[1][1] + 3*(1-k)*k*k*path[2][1] + k**3*path[3][1]
        ctx.move_to(px - 12, py - 4); ctx.line_to(px + 12, py + 4); ctx.stroke()
    # tusk nubs
    for (tx2, ty2) in ((150, -168), (132, -165)):
        ctx.move_to(tx2, ty2); ctx.curve_to(tx2 + 4, ty2 + 10, tx2 + 10, ty2 + 13, tx2 + 16, ty2 + 10)
        ctx.line_to(tx2 + 10, ty2 - 2); ctx.close_path(); _fill_stroke(ctx, (0.99, 0.97, 0.90), 2.5)
    # red collar with a little brass bell (identity detail)
    ctx.set_source_rgb(*AMB_CAP); ctx.set_line_width(7); ctx.set_line_cap(1)
    ctx.move_to(38, -150); ctx.curve_to(60, -128, 120, -124, 150, -142); ctx.stroke()
    ctx.move_to(84, -128); ctx.curve_to(84, -112, 106, -112, 106, -128); ctx.line_to(110, -106)
    ctx.line_to(80, -106); ctx.close_path(); _fill_stroke(ctx, AMB_GOLD, 2.5)
    _ell(ctx, 95, -102, 4, 4); ctx.set_source_rgb(*OUTLINE); ctx.fill()
    # face
    _eye(ctx, 92, -225, 20, expression, blink)
    _eye(ctx, 140, -228, 17, expression, blink)
    _brow(ctx, 92, -258, 15, expression, -1)
    _brow(ctx, 140, -258, 13, expression, 1)
    _ell(ctx, 70, -192, 15, 9); ctx.set_source_rgba(*CHEEK, 0.75); ctx.fill()
    _mouth(ctx, 104, -176, 26, expression, mouth)
    ctx.restore()


# --------------------------------------------------------------------------
def draw_nila(ctx, x, y, scale=1.0, facing=1, mouth=0.0, blink=False,
              expression="happy", t=0.0, arms="down"):
    """Nila (നില): a curious, kind 6-year-old Malayali girl, Ambadi's best friend.
    Warm brown skin, black hair in two pigtails with jasmine, small black bindi,
    green blouse, yellow pavada (long skirt) with a green border, bare feet."""
    bob = math.sin(t * 2.4 + 1.0) * 2.5
    sway = math.sin(t * 2.0) * 0.12
    ctx.save()
    ctx.translate(x, y + bob); ctx.scale(scale * facing, scale)
    # feet
    for fx in (-22, 14):
        _ell(ctx, fx, -6, 15, 7); _fill_stroke(ctx, NILA_SKIN_DARK, 3)
    # pavada (skirt)
    ctx.move_to(-38, -118); ctx.line_to(38, -118); ctx.line_to(58, -12); ctx.line_to(-58, -12); ctx.close_path()
    _grad_fill_stroke(ctx, -118, -12, NILA_SKIRT, (0.95, 0.68, 0.10))
    ctx.rectangle(-58, -30, 116, 18); _fill_stroke(ctx, NILA_BORDER, 3)
    ctx.set_source_rgb(*AMB_GOLD)
    for k in range(-50, 56, 14):
        _ell(ctx, k, -21, 3, 3); ctx.fill()
    # arms
    def arm(sx, dirn):
        ctx.save(); ctx.translate(sx, -150)
        if arms == "up":
            ang = -2.5 * dirn
        elif arms == "wave" and dirn > 0:
            ang = -2.3 + math.sin(t * 9) * 0.35
        elif arms == "point" and dirn > 0:
            ang = -1.4
        else:
            ang = 0.25 * dirn
        ctx.rotate(ang if dirn > 0 else ang)
        ctx.rectangle(-8, 0, 16, 62); _fill_stroke(ctx, NILA_SKIN, 3)
        _ell(ctx, 0, 66, 10, 10); _fill_stroke(ctx, NILA_SKIN, 3)
        ctx.restore()
    arm(-34, -1); arm(34, 1)
    # blouse
    ctx.move_to(-36, -162); ctx.curve_to(-20, -172, 20, -172, 36, -162); ctx.line_to(40, -112)
    ctx.line_to(-40, -112); ctx.close_path(); _grad_fill_stroke(ctx, -172, -112, NILA_BLOUSE, (0.10, 0.52, 0.28))
    # neck
    ctx.rectangle(-9, -180, 18, 14); _fill_stroke(ctx, NILA_SKIN, 3)
    # pigtails (behind head)
    for side in (-1, 1):
        ctx.save(); ctx.translate(side * 56, -222); ctx.rotate(-side * (0.55 + sway))
        _ell(ctx, 0, 34, 15, 38); _fill_stroke(ctx, NILA_HAIR, 3)
        for j in range(4):
            _ell(ctx, side * -2 + (j % 2) * 6 - 3, 2 + j * 6, 5, 5); _fill_stroke(ctx, JASMINE, 1.5)
        ctx.restore()
    # head
    _ell(ctx, 0, -228, 54, 52); _grad_fill_stroke(ctx, -280, -176, (0.86, 0.62, 0.46), NILA_SKIN)
    # hair cap with centre parting and fringe
    ctx.move_to(-56, -226); ctx.curve_to(-60, -300, 60, -300, 56, -226)
    ctx.curve_to(40, -248, 20, -258, 0, -262); ctx.curve_to(-20, -258, -40, -248, -56, -226)
    ctx.close_path(); _fill_stroke(ctx, NILA_HAIR, 3)
    # ears
    for side in (-1, 1):
        _ell(ctx, side * 54, -222, 8, 12); _fill_stroke(ctx, NILA_SKIN, 3)
        _ell(ctx, side * 54, -208, 3.5, 3.5); ctx.set_source_rgb(*AMB_GOLD); ctx.fill()
    # bindi
    _ell(ctx, 6, -252, 3.5, 3.5); ctx.set_source_rgb(0.08, 0.05, 0.05); ctx.fill()
    # face (shifted a little towards facing side)
    _eye(ctx, -14, -228, 12, expression, blink, look=0.4)
    _eye(ctx, 24, -228, 12, expression, blink, look=0.4)
    _brow(ctx, -14, -246, 10, expression, -1)
    _brow(ctx, 24, -246, 10, expression, 1)
    _ell(ctx, -30, -210, 9, 6); ctx.set_source_rgba(*CHEEK, 0.7); ctx.fill()
    _ell(ctx, 40, -210, 9, 6); ctx.set_source_rgba(*CHEEK, 0.7); ctx.fill()
    ctx.set_source_rgb(*NILA_SKIN_DARK); ctx.set_line_width(2.5)
    ctx.move_to(8, -220); ctx.curve_to(10, -214, 12, -212, 8, -210); ctx.stroke()
    _mouth(ctx, 6, -198, 22, expression, mouth)
    ctx.restore()


if __name__ == "__main__":
    # character sheet for approval / reference
    import cairo
    W, H = 1920, 1080
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    c.set_source(_vgrad(c, 0, H, (0.68, 0.86, 0.98), (0.93, 0.97, 1.0))); c.paint()
    c.rectangle(0, 620, W, H - 620); c.set_source(_vgrad(c, 620, H, (0.55, 0.80, 0.38), (0.36, 0.62, 0.26))); c.fill()
    draw_ambadi(c, 600, 820, 1.55, 1, 0.0, False, "happy", 0.3)
    draw_nila(c, 1250, 820, 1.55, -1, 0.0, False, "happy", 0.3, arms="wave")
    exprs = ["happy", "laugh", "shocked", "sad", "angry", "sleepy"]
    for i, e in enumerate(exprs):
        draw_ambadi(c, 130 + i * 300, 1060, 0.42, 1, 0.5 if e == "happy" else 0, False, e, 0, trunk="up" if e == "laugh" else "down")
        draw_nila(c, 250 + i * 300, 1060, 0.42, -1, 0, False, e, 0)
    surf.write_to_png("heroes_sheet.png")
    print("ok")
