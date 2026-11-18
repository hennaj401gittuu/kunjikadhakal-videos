"""Tiny Meadow Tales recurring heroes: Bramble (little bunny) and Dot (ladybug).

Shared pycairo drawing code so every video draws the two heroes the same way.

    import cairo, meadow_heroes as mh
    mh.draw_bramble(ctx, x, y, scale=1.0, facing=1, mouth=0.0, blink=False,
                    expression="happy", t=0.0, arms="down")
    mh.draw_dot(ctx, x, y, scale=1.0, facing=1, mouth=0.0, blink=False,
                expression="happy", t=0.0, flying=False)

(x, y) is the point on the ground under the feet (for Dot flying=True it is the
point she hovers above; she floats ~40 px higher and her wings buzz). At scale 1.0
Bramble is about 270 px tall to the ear tips and Dot about 120 px, so Dot often
sits on Bramble's head or flies beside his face (Dot scale 1 next to Bramble scale 1).
facing=1 looks right, -1 looks left. mouth 0..1 drives lip-sync.
expression: happy | sad | shocked | angry | sleepy | laugh.
t is time in seconds (idle bob, ear wiggle, wing buzz).
arms (Bramble): down | up | wave | point.
"""
import math

# ---- palette (fixed: the characters' identity) ----
OUTLINE = (0.24, 0.16, 0.12)
CHEEK = (1.0, 0.55, 0.60)
BR_FUR = (0.86, 0.66, 0.42)          # honey-caramel fur
BR_FUR_LIGHT = (0.95, 0.80, 0.58)
BR_FUR_DARK = (0.70, 0.50, 0.30)
BR_CREAM = (1.0, 0.95, 0.84)         # tummy, muzzle, tail
BR_EAR_IN = (0.98, 0.72, 0.74)
BR_SCARF = (0.20, 0.52, 0.90)        # blue scarf
BR_SCARF_DARK = (0.12, 0.38, 0.72)
BR_NOSE = (0.96, 0.46, 0.55)

DOT_SHELL = (0.92, 0.14, 0.16)       # bright red shell
DOT_SHELL_LIGHT = (1.0, 0.40, 0.36)
DOT_SPOT = (0.10, 0.07, 0.07)
DOT_HEAD = (0.16, 0.12, 0.13)
DOT_FACE = (1.0, 0.88, 0.76)         # peach face
DOT_BOW = (1.0, 0.62, 0.82)          # pink bow on her left antenna
DOT_WING = (0.85, 0.95, 1.0)


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


def _eye(ctx, cx, cy, r, expression, blink, look=0.3, line=OUTLINE):
    if blink or expression == "sleepy":
        ctx.set_source_rgb(*line); ctx.set_line_width(max(2.5, r * 0.25))
        ctx.move_to(cx - r, cy); ctx.curve_to(cx - r * 0.4, cy + r * 0.6, cx + r * 0.4, cy + r * 0.6, cx + r, cy)
        ctx.stroke(); return
    if expression == "laugh":
        ctx.set_source_rgb(*line); ctx.set_line_width(max(3, r * 0.3))
        ctx.move_to(cx - r, cy + r * 0.2); ctx.curve_to(cx - r * 0.4, cy - r * 0.8, cx + r * 0.4, cy - r * 0.8, cx + r, cy + r * 0.2)
        ctx.stroke(); return
    big = 1.25 if expression == "shocked" else 1.0
    _ell(ctx, cx, cy, r * 0.85 * big, r * big); _fill_stroke(ctx, (1, 1, 1), max(2, r * 0.18))
    pr = r * (0.42 if expression == "shocked" else 0.62)
    _ell(ctx, cx + look * r * 0.5, cy + r * 0.12, pr * 0.9, pr); ctx.set_source_rgb(0.12, 0.08, 0.06); ctx.fill()
    _ell(ctx, cx + look * r * 0.5 - pr * 0.35, cy - pr * 0.3, pr * 0.32, pr * 0.32); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    _ell(ctx, cx + look * r * 0.5 + pr * 0.3, cy + pr * 0.35, pr * 0.14, pr * 0.14); ctx.set_source_rgb(1, 1, 1); ctx.fill()


def _brow(ctx, cx, cy, w, expression, side, line=OUTLINE, lw=5):
    ctx.set_source_rgb(*line); ctx.set_line_width(lw); ctx.set_line_cap(1)
    if expression == "angry":
        ctx.move_to(cx - w * side, cy - w * 0.4); ctx.line_to(cx + w * side, cy + w * 0.4)
    elif expression in ("sad", "sleepy"):
        ctx.move_to(cx - w * side, cy + w * 0.35); ctx.line_to(cx + w * side, cy - w * 0.4)
    elif expression == "shocked":
        ctx.move_to(cx - w, cy - w * 0.7); ctx.curve_to(cx - w * 0.3, cy - w * 1.5, cx + w * 0.3, cy - w * 1.5, cx + w, cy - w * 0.7)
    else:
        ctx.move_to(cx - w, cy); ctx.curve_to(cx - w * 0.3, cy - w * 0.55, cx + w * 0.3, cy - w * 0.55, cx + w, cy)
    ctx.stroke()


def _mouth(ctx, cx, cy, w, expression, mouth, line=OUTLINE):
    ctx.set_line_width(max(2.5, w * 0.16)); ctx.set_line_cap(1)
    if expression == "shocked":
        _ell(ctx, cx, cy + 4, w * 0.35, w * (0.35 + 0.25 * mouth)); _fill_stroke(ctx, (0.45, 0.10, 0.12), 2.5); return
    if mouth > 0.08 or expression == "laugh":
        o = max(mouth, 0.7 if expression == "laugh" else 0)
        ctx.move_to(cx - w * 0.55, cy)
        if expression in ("sad", "angry"):
            ctx.curve_to(cx - w * 0.3, cy - 4, cx + w * 0.3, cy - 4, cx + w * 0.55, cy)
            ctx.curve_to(cx + w * 0.3, cy + w * 0.5 * o, cx - w * 0.3, cy + w * 0.5 * o, cx - w * 0.55, cy)
        else:
            ctx.curve_to(cx - w * 0.3, cy + 3, cx + w * 0.3, cy + 3, cx + w * 0.55, cy)
            ctx.curve_to(cx + w * 0.35, cy + w * 0.75 * o + 5, cx - w * 0.35, cy + w * 0.75 * o + 5, cx - w * 0.55, cy)
        ctx.close_path(); _fill_stroke(ctx, (0.50, 0.12, 0.14), 2.5)
        _ell(ctx, cx, cy + w * 0.35 * o + 2, w * 0.22, w * 0.12 * o + 1); ctx.set_source_rgb(0.95, 0.45, 0.50); ctx.fill()
        return
    ctx.set_source_rgb(*line)
    if expression == "sad":
        ctx.move_to(cx - w * 0.4, cy + 5); ctx.curve_to(cx - w * 0.1, cy - 5, cx + w * 0.1, cy - 5, cx + w * 0.4, cy + 5)
    elif expression == "angry":
        ctx.move_to(cx - w * 0.35, cy + 2); ctx.line_to(cx + w * 0.35, cy + 2)
    elif expression == "sleepy":
        _ell(ctx, cx, cy + 2, w * 0.12, w * 0.1); ctx.stroke(); return
    else:
        ctx.move_to(cx - w * 0.5, cy - 2); ctx.curve_to(cx - w * 0.2, cy + w * 0.5, cx + w * 0.2, cy + w * 0.5, cx + w * 0.5, cy - 2)
    ctx.stroke()


# --------------------------------------------------------------------------
def draw_bramble(ctx, x, y, scale=1.0, facing=1, mouth=0.0, blink=False,
                 expression="happy", t=0.0, arms="down"):
    """Bramble: a curious, bouncy, slightly clumsy little bunny boy.
    Honey-caramel fur, cream tummy and muzzle, long ears with the right ear
    flopped over at the tip, pink nose, buck teeth, a blue scarf."""
    bob = abs(math.sin(t * 2.4)) * -4
    wig = math.sin(t * 3.0) * 0.06
    ctx.save()
    ctx.translate(x, y + bob); ctx.scale(scale * facing, scale)
    # big back foot + feet
    for fx in (-30, 22):
        _ell(ctx, fx, -10, 30, 12); _fill_stroke(ctx, BR_FUR_LIGHT, 3.5)
        _ell(ctx, fx + 6, -8, 12, 6); ctx.set_source_rgb(*BR_EAR_IN); ctx.fill()
    # tail (behind)
    for k in range(5):
        a = k * 2 * math.pi / 5
        _ell(ctx, -58 + math.cos(a) * 9, -62 + math.sin(a) * 9, 13, 13)
    ctx.set_source_rgb(*BR_CREAM); ctx.fill()
    _ell(ctx, -58, -62, 18, 18); _fill_stroke(ctx, BR_CREAM, 3)
    # body (pear shape)
    ctx.move_to(-42, -120); ctx.curve_to(-70, -80, -62, -18, 0, -16)
    ctx.curve_to(62, -18, 70, -80, 42, -120); ctx.close_path()
    _grad_fill_stroke(ctx, -125, -15, BR_FUR_LIGHT, BR_FUR)
    _ell(ctx, 4, -62, 32, 38); ctx.set_source_rgb(*BR_CREAM); ctx.fill()
    # arms
    def arm(sx, dirn):
        ctx.save(); ctx.translate(sx, -108)
        if arms == "up":
            ang = -2.4 * dirn
        elif arms == "wave" and dirn > 0:
            ang = -2.3 + math.sin(t * 9) * 0.35
        elif arms == "point" and dirn > 0:
            ang = -1.45
        else:
            ang = 0.35 * dirn
        ctx.rotate(ang)
        ctx.move_to(-10, 0); ctx.curve_to(-12, 30, -10, 46, 0, 50); ctx.curve_to(10, 46, 12, 30, 10, 0)
        ctx.close_path(); _fill_stroke(ctx, BR_FUR, 3)
        _ell(ctx, 0, 50, 11, 10); _fill_stroke(ctx, BR_FUR_LIGHT, 3)
        ctx.restore()
    arm(-38, -1); arm(38, 1)
    # scarf
    ctx.move_to(-40, -128); ctx.curve_to(-20, -112, 20, -112, 40, -128)
    ctx.line_to(40, -142); ctx.curve_to(20, -128, -20, -128, -40, -142); ctx.close_path()
    _fill_stroke(ctx, BR_SCARF, 3)
    ctx.move_to(-28, -124); ctx.line_to(-40, -86 + math.sin(t * 3) * 4); ctx.line_to(-22, -90); ctx.line_to(-16, -120)
    ctx.close_path(); _fill_stroke(ctx, BR_SCARF_DARK, 3)
    # ears
    def ear(ex, ang, flop):
        ctx.save(); ctx.translate(ex, -200); ctx.rotate(ang)
        ctx.move_to(-14, 0); ctx.curve_to(-22, -40, -18, -78, 0, -92)
        ctx.curve_to(18, -78, 22, -40, 14, 0); ctx.close_path()
        _grad_fill_stroke(ctx, -92, 0, BR_FUR_LIGHT, BR_FUR, 3.5)
        ctx.move_to(-7, -6); ctx.curve_to(-12, -38, -9, -68, 0, -80)
        ctx.curve_to(9, -68, 12, -38, 7, -6); ctx.close_path(); ctx.set_source_rgb(*BR_EAR_IN); ctx.fill()
        if flop:
            ctx.save(); ctx.translate(0, -78); ctx.rotate(1.9)
            ctx.move_to(-11, 0); ctx.curve_to(-14, -16, -8, -30, 0, -34); ctx.curve_to(8, -30, 14, -16, 11, 0)
            ctx.close_path(); _fill_stroke(ctx, BR_FUR, 3.5)
            ctx.restore()
        ctx.restore()
    ear(-22, -0.18 - wig, False)
    ear(24, 0.20 + wig, True)
    # head
    _ell(ctx, 4, -176, 62, 54); _grad_fill_stroke(ctx, -230, -122, BR_FUR_LIGHT, BR_FUR)
    # muzzle
    _ell(ctx, 16, -152, 30, 20); ctx.set_source_rgb(*BR_CREAM); ctx.fill()
    # face
    _eye(ctx, -12, -184, 15, expression, blink)
    _eye(ctx, 30, -186, 14, expression, blink)
    _brow(ctx, -12, -206, 11, expression, -1, lw=4)
    _brow(ctx, 30, -206, 10, expression, 1, lw=4)
    _ell(ctx, -36, -158, 11, 7); ctx.set_source_rgba(*CHEEK, 0.75); ctx.fill()
    _ell(ctx, 50, -160, 9, 6); ctx.set_source_rgba(*CHEEK, 0.75); ctx.fill()
    # nose + whiskers
    ctx.move_to(10, -164); ctx.line_to(26, -164); ctx.line_to(18, -155); ctx.close_path(); _fill_stroke(ctx, BR_NOSE, 2.5)
    ctx.set_source_rgba(*OUTLINE, 0.6); ctx.set_line_width(2)
    for dy in (-4, 3):
        ctx.move_to(40, -156 + dy); ctx.line_to(62, -160 + dy * 2); ctx.stroke()
        ctx.move_to(-4, -156 + dy); ctx.line_to(-24, -160 + dy * 2); ctx.stroke()
    # buck teeth (shown when mouth closed and happy)
    if mouth < 0.08 and expression in ("happy",):
        ctx.rectangle(13, -146, 10, 9); _fill_stroke(ctx, (1, 1, 1), 2)
        ctx.move_to(18, -146); ctx.line_to(18, -137); ctx.set_line_width(1.5); ctx.stroke()
    _mouth(ctx, 18, -146, 20, expression, mouth)
    ctx.restore()


# --------------------------------------------------------------------------
def draw_dot(ctx, x, y, scale=1.0, facing=1, mouth=0.0, blink=False,
             expression="happy", t=0.0, flying=False):
    """Dot: a clever, kind, cheerful little ladybug girl, Bramble's best friend.
    Shiny red shell with seven black spots, dark head with a round peach face,
    two curly antennae (a pink bow on one), little black legs; wings buzz when flying."""
    hover = (-40 + math.sin(t * 5.0) * 6) if flying else math.sin(t * 2.6) * 1.5
    ctx.save()
    ctx.translate(x, y + hover); ctx.scale(scale * facing, scale)
    # legs
    ctx.set_source_rgb(*DOT_SPOT); ctx.set_line_width(5); ctx.set_line_cap(1)
    for lx in (-22, 0, 20):
        ctx.move_to(lx, -22); ctx.line_to(lx - 4, -2 if not flying else -10); ctx.stroke()
    # wings (only when flying)
    if flying:
        buzz = math.sin(t * 40) * 0.25
        for side in (-1, 1):
            ctx.save(); ctx.translate(-8, -60); ctx.rotate(-0.9 * side + buzz * side - 0.5)
            _ell(ctx, 0, -36, 18, 40); ctx.set_source_rgba(*DOT_WING, 0.7); ctx.fill_preserve()
            ctx.set_source_rgba(*OUTLINE, 0.6); ctx.set_line_width(2.5); ctx.stroke(); ctx.restore()
    # shell
    _ell(ctx, -6, -48, 46, 38)
    import cairo
    g = cairo.RadialGradient(-20, -66, 4, -6, -48, 50)
    g.add_color_stop_rgb(0, *DOT_SHELL_LIGHT); g.add_color_stop_rgb(1, DOT_SHELL[0] * 0.85, DOT_SHELL[1], DOT_SHELL[2])
    ctx.set_source(g); ctx.fill_preserve(); ctx.set_source_rgb(*OUTLINE); ctx.set_line_width(3.5); ctx.stroke()
    ctx.set_source_rgb(*OUTLINE); ctx.set_line_width(3)
    ctx.move_to(-2, -86); ctx.line_to(-6, -12); ctx.stroke()
    for (sx, sy, r) in ((-28, -62, 8), (-30, -34, 7), (-14, -24, 6), (16, -62, 8), (20, -36, 7), (6, -24, 5), (-4, -74, 6)):
        _ell(ctx, sx, sy, r, r); ctx.set_source_rgb(*DOT_SPOT); ctx.fill()
    _ell(ctx, -22, -72, 10, 5); ctx.set_source_rgba(1, 1, 1, 0.55); ctx.fill()
    # head
    _ell(ctx, 40, -72, 30, 28); _fill_stroke(ctx, DOT_HEAD, 3.5)
    # antennae
    ctx.set_source_rgb(*DOT_HEAD); ctx.set_line_width(4)
    sw = math.sin(t * 3.3) * 3
    for (ax, tip) in ((30, (18 + sw, -122)), (50, (62 + sw, -124))):
        ctx.move_to(ax, -96); ctx.curve_to(ax - 4, -110, tip[0], -112, tip[0], tip[1]); ctx.stroke()
        _ell(ctx, tip[0], tip[1], 6, 6); _fill_stroke(ctx, DOT_HEAD, 2)
    # pink bow on the left antenna
    bx, by = 24 + sw * 0.5, -110
    for side in (-1, 1):
        ctx.move_to(bx, by); ctx.line_to(bx + side * 11, by - 7); ctx.line_to(bx + side * 11, by + 7); ctx.close_path()
        _fill_stroke(ctx, DOT_BOW, 2)
    _ell(ctx, bx, by, 3.5, 3.5); _fill_stroke(ctx, DOT_BOW, 1.5)
    # face
    _ell(ctx, 44, -70, 23, 21); ctx.set_source_rgb(*DOT_FACE); ctx.fill()
    _eye(ctx, 36, -74, 8, expression, blink, look=0.4)
    _eye(ctx, 54, -75, 7.5, expression, blink, look=0.4)
    _brow(ctx, 36, -86, 6, expression, -1, lw=2.5)
    _brow(ctx, 54, -86, 5.5, expression, 1, lw=2.5)
    _ell(ctx, 28, -62, 5, 3.5); ctx.set_source_rgba(*CHEEK, 0.8); ctx.fill()
    _ell(ctx, 60, -62, 4.5, 3.2); ctx.set_source_rgba(*CHEEK, 0.8); ctx.fill()
    _mouth(ctx, 46, -60, 13, expression, mouth)
    ctx.restore()


if __name__ == "__main__":
    import cairo
    W, H = 1920, 1080
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    c.set_source(_vgrad(c, 0, H, (0.68, 0.86, 0.98), (0.95, 0.98, 1.0))); c.paint()
    c.rectangle(0, 640, W, H - 640); c.set_source(_vgrad(c, 640, H, (0.60, 0.84, 0.40), (0.38, 0.64, 0.28))); c.fill()
    for i in range(40):  # buttercups
        fx, fy = (i * 211) % W, 660 + (i * 97) % 120
        _ell(c, fx, fy, 7, 7); c.set_source_rgb(1.0, 0.86, 0.15); c.fill()
    draw_bramble(c, 640, 840, 1.85, 1, 0.0, False, "happy", 0.3, arms="wave")
    draw_dot(c, 1250, 620, 2.4, -1, 0.0, False, "happy", 0.3, flying=True)
    exprs = ["happy", "laugh", "shocked", "sad", "angry", "sleepy"]
    for i, e in enumerate(exprs):
        draw_bramble(c, 120 + i * 300, 1065, 0.5, 1, 0.5 if e == "happy" else 0, False, e, 0)
        draw_dot(c, 235 + i * 300, 1062, 0.75, -1, 0, False, e, 0)
    surf.write_to_png("meadow_heroes_sheet.png")
    print("ok")
