import cairo, math, random

W, H = 1080, 1920
TAU = 2 * math.pi

# ---------- helpers ----------
def hexc(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

def setc(ctx, h, a=1.0):
    ctx.set_source_rgba(*hexc(h, a))

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def seg(t, a, b):
    return clamp((t - a) / (b - a))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def eob(x):
    x = clamp(x)
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def lerp(a, b, x):
    return a + (b - a) * x

def lerp2(p, q, x):
    return (lerp(p[0], q[0], x), lerp(p[1], q[1], x))

def ell(ctx, cx, cy, rx, ry):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.new_sub_path(); ctx.arc(0, 0, 1, 0, TAU); ctx.restore()

def rr(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()

def radial(cx, cy, r0, r1, stops, cx1=None, cy1=None):
    g = cairo.RadialGradient(cx, cy, r0, cx if cx1 is None else cx1, cy if cy1 is None else cy1, r1)
    for o, c, *a in stops:
        g.add_color_stop_rgba(o, *hexc(c, a[0] if a else 1))
    return g

def linear(x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, c, *a in stops:
        g.add_color_stop_rgba(o, *hexc(c, a[0] if a else 1))
    return g

def text(ctx, s, x, y, size, color='#5A2E12', font='Fredoka', weight=cairo.FONT_WEIGHT_BOLD,
         align='center', outline=None, ow=10, alpha=1.0):
    ctx.save()
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    if align == 'center':
        x -= ext.width / 2 + ext.x_bearing
    ctx.move_to(x, y)
    ctx.text_path(s)
    if outline:
        setc(ctx, outline, alpha); ctx.set_line_width(ow); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    setc(ctx, color, alpha); ctx.fill()
    ctx.restore()

_ging = {}
def gingham(col='#F27BA0', cell=16):
    key = (col, cell)
    if key not in _ging:
        n = cell * 2
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, n, n)
        c = cairo.Context(s)
        setc(c, '#FFF6F8'); c.paint()
        setc(c, col, 0.5); c.rectangle(0, 0, cell, n); c.fill()
        setc(c, col, 0.5); c.rectangle(0, 0, n, cell); c.fill()
        _ging[key] = s
    p = cairo.SurfacePattern(_ging[key]); p.set_extend(cairo.EXTEND_REPEAT); p.set_filter(cairo.FILTER_GOOD)
    return p

def blink_at(t, period=3.4, offset=0.0):
    ph = (t + offset) % period
    if ph < 0.16:
        return math.sin(ph / 0.16 * math.pi)
    return 0.0

def sparkle(ctx, x, y, r, a=1.0, col='#FFFFFF'):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(0, -r)
    for k in range(4):
        ang = -math.pi / 2 + k * math.pi / 2
        nx, ny = math.cos(ang + math.pi / 2) * r, math.sin(ang + math.pi / 2) * r
        mx, my = math.cos(ang + math.pi / 4) * r * 0.18, math.sin(ang + math.pi / 4) * r * 0.18
        ctx.line_to(mx, my); ctx.line_to(nx, ny)
    ctx.close_path(); setc(ctx, col, a); ctx.fill(); ctx.restore()

def heart(ctx, x, y, s, col='#FF5C8A', a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(0, 0.35)
    ctx.curve_to(-1.1, -0.35, -0.5, -1.15, 0, -0.55)
    ctx.curve_to(0.5, -1.15, 1.1, -0.35, 0, 0.35)
    ctx.close_path(); setc(ctx, col, a); ctx.fill_preserve()
    ctx.restore()
    ctx.new_path()

def steam(ctx, x, y, t, n=3, h=160, a=0.5, spread=60):
    ctx.save(); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        ph = (t * 0.6 + i / n) % 1.0
        xx = x + (i - (n - 1) / 2) * spread
        al = a * math.sin(ph * math.pi)
        ctx.set_line_width(14 * (1 - ph * 0.5))
        setc(ctx, '#FFFFFF', al)
        y0 = y - ph * h * 0.6
        ctx.move_to(xx, y0)
        for k in range(1, 9):
            yy = y0 - k * h / 8
            ctx.line_to(xx + math.sin(k * 0.9 + t * 3 + i) * 14, yy)
        ctx.stroke()
    ctx.restore()

# ---------- ant ----------
OR = '#F08A3A'; ORD = '#C35A1C'; ORL = '#FFC07A'; DARK = '#3A1A0A'; BROWN = '#5A2E12'

def chip_shape(ctx, x, y, s, rot=0.0, col='#5B2C12'):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.move_to(0, -1.15)
    ctx.curve_to(0.25, -0.6, 1.0, -0.05, 0.95, 0.45)
    ctx.curve_to(0.9, 0.95, -0.9, 0.95, -0.95, 0.45)
    ctx.curve_to(-1.0, -0.05, -0.25, -0.6, 0, -1.15)
    ctx.close_path()
    ctx.set_source(radial(-0.3, -0.2, 0.05, 1.3, [(0, '#8A4A22'), (0.6, col), (1, '#2E1407')]))
    ctx.fill()
    setc(ctx, '#FFFFFF', 0.35); ell(ctx, -0.35, -0.05, 0.12, 0.28); ctx.fill()
    ctx.restore()

def ant_abdomen(ctx, x=-100, y=95, rot=-0.4, rx=82, ry=64, t=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot + math.sin(t * 2) * 0.03)
    ell(ctx, 0, 0, rx, ry)
    ctx.set_source(radial(-rx * 0.3, -ry * 0.4, 5, rx * 1.3, [(0, ORL), (0.55, OR), (1, ORD)]))
    ctx.fill_preserve()
    ctx.save(); ctx.clip()
    for k in range(-3, 4):
        setc(ctx, '#7A3410', 0.55)
        ctx.save(); ctx.translate(k * 30, 0); ctx.scale(1, 1)
        ctx.move_to(-7, -ry - 5); ctx.curve_to(-14, -20, -14, 20, -7, ry + 5)
        ctx.line_to(5, ry + 5); ctx.curve_to(-2, 20, -2, -20, 5, -ry - 5); ctx.close_path(); ctx.fill()
        ctx.restore()
    ctx.restore(); ctx.new_path()
    ctx.restore()

def ant_legs(ctx, phase=0.0, walk=0.0, scale=1.0):
    ctx.save(); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for i, side in enumerate((-1, 1)):
        p = phase + i * math.pi
        hx, hy = side * 24, 120
        fx = side * 30 + math.sin(p) * 34 * walk
        fy = 262 - max(0.0, math.cos(p)) * 26 * walk
        kx, ky = (hx + fx) / 2 + side * 10, (hy + fy) / 2 - 4
        for wdt, col in ((18, ORD), (12, OR)):
            ctx.set_line_width(wdt); setc(ctx, col)
            ctx.move_to(hx, hy); ctx.line_to(kx, ky); ctx.line_to(fx, fy); ctx.stroke()
        setc(ctx, ORD); ell(ctx, kx, ky, 9, 9); ctx.fill()
        # shoe
        ctx.set_source(radial(fx + 8, fy - 2, 2, 26, [(0, '#FF8FB0'), (1, '#D9456F')]))
        ell(ctx, fx + 10, fy + 4, 24, 12); ctx.fill()
    ctx.restore()

def ant_torso(ctx, apron=True):
    setc(ctx, ORD); ell(ctx, 0, -95, 22, 30); ctx.fill()
    ell(ctx, 0, 15, 60, 84)
    ctx.set_source(radial(-20, -30, 5, 100, [(0, ORL), (0.6, OR), (1, ORD)])); ctx.fill()
    if not apron:
        return
    gp = gingham('#F2709A', 9)
    ctx.move_to(-50, 40); ctx.curve_to(-62, 90, -86, 130, -92, 160)
    ctx.line_to(92, 160); ctx.curve_to(86, 130, 62, 90, 50, 40); ctx.close_path()
    ctx.set_source(gp); ctx.fill()
    # scallop trim
    setc(ctx, '#FFFFFF')
    for k in range(9):
        x = -92 + k * 23 + 11.5
        ell(ctx, x, 162, 12, 9); ctx.fill()
    # bib
    rr(ctx, -42, -55, 84, 100, 16); ctx.set_source(gp); ctx.fill()
    ctx.save(); rr(ctx, -42, -55, 84, 100, 16); setc(ctx, '#FFFFFF', 0.9); ctx.set_line_width(4); ctx.stroke(); ctx.restore()
    # straps
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    setc(ctx, '#FFFFFF'); ctx.set_line_width(9)
    ctx.move_to(-34, -52); ctx.line_to(-46, -86); ctx.stroke()
    ctx.move_to(34, -52); ctx.line_to(46, -86); ctx.stroke()
    # waist band + bow
    rr(ctx, -60, 34, 120, 18, 9); setc(ctx, '#FFFFFF'); ctx.fill()
    # pocket heart
    heart(ctx, 0, 0, 13, '#FF5C8A', 0.9); ctx.fill()

def eye(ctx, ex, ey, rx, ry, look, blink, lashes=True, side=1, happy=False):
    if happy or blink > 0.8:
        ctx.save(); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(7); setc(ctx, DARK)
        if happy:
            ctx.arc(ex, ey + 8, rx * 0.8, math.pi * 1.15, math.pi * 1.85)
        else:
            ctx.arc(ex, ey - 6, rx * 0.85, math.pi * 0.15, math.pi * 0.85)
        ctx.stroke()
        if lashes:
            for k in range(3):
                a = (math.pi * 0.2 + k * 0.18) if not happy else (math.pi * 1.85 - k * 0.0)
            if not happy:
                for k in range(3):
                    a = math.pi * (0.75 - 0.0) if side < 0 else math.pi * 0.25
            pass
        ctx.restore()
        return
    ry2 = ry * (1 - blink)
    ctx.save()
    ell(ctx, ex, ey, rx, ry2); setc(ctx, '#FFFFFF'); ctx.fill_preserve()
    ctx.save(); ctx.clip()
    ix, iy = ex + look[0] * rx * 0.35, ey + 4 + look[1] * ry * 0.3
    ctx.set_source(radial(ix, iy + 6, 2, rx * 0.8, [(0, '#B5662C'), (0.6, '#6B3413'), (1, '#2A1205')]))
    ell(ctx, ix, iy, rx * 0.74, rx * 0.8); ctx.fill()
    setc(ctx, '#120803'); ell(ctx, ix, iy, rx * 0.42, rx * 0.46); ctx.fill()
    setc(ctx, '#FFFFFF'); ell(ctx, ix - rx * 0.28, iy - rx * 0.3, rx * 0.22, rx * 0.24); ctx.fill()
    ell(ctx, ix + rx * 0.25, iy + rx * 0.26, rx * 0.1, rx * 0.1); ctx.fill()
    # upper lid shade
    setc(ctx, '#C97E54', 0.25); ell(ctx, ex, ey - ry2 * 1.05, rx * 1.2, ry2 * 0.5); ctx.fill()
    ctx.restore()
    ell(ctx, ex, ey, rx, ry2); setc(ctx, DARK, 0.5); ctx.set_line_width(2.5); ctx.stroke()
    # upper lash line
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    setc(ctx, DARK); ctx.set_line_width(6)
    ctx.save(); ctx.translate(ex, ey); ctx.scale(rx, ry2)
    ctx.arc(0, 0, 1.02, math.pi * 1.08, math.pi * 1.92); ctx.restore(); ctx.stroke()
    if lashes:
        ctx.set_line_width(4.5)
        for k in range(3):
            a = (1.75 + k * 0.09) * math.pi if side > 0 else (1.25 - k * 0.09) * math.pi
            px, py = ex + math.cos(a) * rx, ey + math.sin(a) * ry2
            ctx.move_to(px, py); ctx.line_to(px + math.cos(a) * 14 + side * 4, py + math.sin(a) * 12 - 2); ctx.stroke()
    ctx.restore()

def ant_head(ctx, t=0.0, look=(0, 0), blink=0.0, mouth=0.0, flower=True, baby=False, happy=False,
             chew=0.0, tilt=0.0):
    hy = -200 if not baby else -170
    r = 108 if not baby else 100
    ctx.save(); ctx.translate(0, hy + r * 0.6); ctx.rotate(tilt); ctx.translate(0, -(hy + r * 0.6))
    # antennae
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for side in (-1, 1):
        sw = math.sin(t * 2.3 + side) * 6
        bx, by = side * 42, hy - r * 0.78
        tx, ty = side * (88 if not baby else 70) + sw, hy - r * (1.85 if not baby else 1.6)
        cx, cy = side * 50, hy - r * 1.65
        for wdt, col in ((13, ORD), (8, OR)):
            ctx.set_line_width(wdt); setc(ctx, col)
            ctx.move_to(bx, by); ctx.curve_to(cx, cy, tx - side * 30, ty - 30, tx, ty); ctx.stroke()
        ctx.set_source(radial(tx - 4, ty - 5, 1, 17, [(0, ORL), (1, ORD)])); ell(ctx, tx, ty, 15, 15); ctx.fill()
    # head
    ell(ctx, 0, hy, r, r * 0.97)
    ctx.set_source(radial(-r * 0.35, hy - r * 0.45, 8, r * 1.35, [(0, '#FFD39A'), (0.45, OR), (1, ORD)]))
    ctx.fill()
    # cheeks
    for side in (-1, 1):
        ctx.set_source(radial(side * r * 0.6, hy + r * 0.36, 2, 30, [(0, '#FF5C7A', 0.65), (1, '#FF5C7A', 0)]))
        ell(ctx, side * r * 0.6, hy + r * 0.36, 32, 24); ctx.fill()
    # eyes
    erx = 30 if not baby else 33
    ery = 38 if not baby else 40
    for side in (-1, 1):
        eye(ctx, side * r * 0.38, hy + 2, erx, ery, look, blink, lashes=not baby, side=side, happy=happy)
        # brow
        if not baby:
            ctx.save(); setc(ctx, '#7A3A16'); ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.arc(side * r * 0.4, hy - 18, 34, math.pi * (1.3 if side < 0 else 1.45), math.pi * (1.55 if side < 0 else 1.7))
            ctx.stroke(); ctx.restore()
    # nose
    setc(ctx, '#C9542A'); ell(ctx, 0, hy + r * 0.38, 8, 6); ctx.fill()
    # mouth
    my = hy + r * 0.52
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    m = max(mouth, chew)
    if m < 0.08:
        setc(ctx, '#7A2A10'); ctx.set_line_width(5)
        ctx.arc(0, my - 14, 20, math.pi * 0.2, math.pi * 0.8); ctx.stroke()
    else:
        h = 6 + m * 26
        ctx.move_to(-22, my); ctx.curve_to(-20, my + h * 1.2, 20, my + h * 1.2, 22, my)
        ctx.curve_to(10, my + 3, -10, my + 3, -22, my); ctx.close_path()
        setc(ctx, '#6E1A10'); ctx.fill_preserve()
        ctx.save(); ctx.clip(); setc(ctx, '#FF7F8E'); ell(ctx, 0, my + h, 15, h * 0.5); ctx.fill(); ctx.restore()
    # flower
    if flower:
        fx, fy = -r * 0.62, hy - r * 0.72
        for k in range(5):
            a = k * TAU / 5 + 0.3
            setc(ctx, '#FF86AE'); ell(ctx, fx + math.cos(a) * 13, fy + math.sin(a) * 13, 11, 11); ctx.fill()
        setc(ctx, '#FFD34E'); ell(ctx, fx, fy, 8, 8); ctx.fill()
    ctx.restore()

def arm_path(ctx, sx, sy, hx, hy, L1=78, L2=78, bend=1, mitt=False, hand_col=OR):
    dx, dy = hx - sx, hy - sy
    d = math.hypot(dx, dy) + 1e-6
    if d > (L1 + L2) * 0.98:
        k = d / ((L1 + L2) * 0.98); L1 *= k; L2 *= k
    a = math.atan2(dy, dx)
    cb = clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1)
    b = math.acos(cb)
    ang = a + bend * b
    ex, ey = sx + L1 * math.cos(ang), sy + L1 * math.sin(ang)
    ctx.save(); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for wdt, col in ((20, ORD), (14, OR)):
        ctx.set_line_width(wdt); setc(ctx, col)
        ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.line_to(hx, hy); ctx.stroke()
    setc(ctx, ORD); ell(ctx, ex, ey, 10, 10); ctx.fill()
    if mitt:
        ell(ctx, hx, hy, 26, 22); ctx.set_source(gingham('#F2709A', 7)); ctx.fill()
        ell(ctx, hx, hy, 26, 22); setc(ctx, '#E25A86'); ctx.set_line_width(3); ctx.stroke()
    else:
        ctx.set_source(radial(hx - 4, hy - 4, 1, 20, [(0, ORL), (1, OR)])); ell(ctx, hx, hy, 16, 16); ctx.fill()
        setc(ctx, ORD); ctx.set_line_width(2.5); ell(ctx, hx, hy, 16, 16); ctx.stroke()
    ctx.restore()

class Pose:
    def __init__(self, tx, ty, s, flip=False):
        self.tx, self.ty, self.s, self.flip = tx, ty, s, flip
    def apply(self, ctx):
        ctx.translate(self.tx, self.ty); ctx.scale(-self.s if self.flip else self.s, self.s)
    def local(self, p):
        f = -1 if self.flip else 1
        return ((p[0] - self.tx) / (self.s * f), (p[1] - self.ty) / self.s)
    def world(self, p):
        f = -1 if self.flip else 1
        return (self.tx + p[0] * self.s * f, self.ty + p[1] * self.s)

def draw_ant(ctx, pose, t, lh=None, rh=None, look=(0, 0), blink=None, mouth=0.0, legs=False, walk=0.0,
             phase=0.0, part='all', mitt=False, happy=False, tilt=0.0, bob=0.0):
    """lh/rh are WORLD coords for hands."""
    if blink is None:
        blink = blink_at(t)
    ctx.save(); pose.apply(ctx)
    ctx.translate(0, bob)
    sh = [(-56, -48), (56, -48)]
    lh_l = pose.local(lh) if lh else (-75, 70)
    rh_l = pose.local(rh) if rh else (75, 70)
    lh_l = (lh_l[0], lh_l[1] - bob); rh_l = (rh_l[0], rh_l[1] - bob)
    if part in ('all', 'body'):
        ant_abdomen(ctx, t=t)
        if legs:
            ant_legs(ctx, phase, walk)
        ant_torso(ctx)
        ant_head(ctx, t, look, blink, mouth, happy=happy, tilt=tilt)
    if part in ('all', 'arms'):
        arm_path(ctx, sh[0][0], sh[0][1], lh_l[0], lh_l[1], bend=1, mitt=mitt)
        arm_path(ctx, sh[1][0], sh[1][1], rh_l[0], rh_l[1], bend=-1, mitt=mitt)
    ctx.restore()

def draw_baby(ctx, x, y, s, t, look=(0, 0), mouth=0.0, bounce=0.0, happy=False, chew=0.0, seed=0, tilt=0.0,
              arms_up=0.0, hold=None, hold_cb=None):
    ctx.save(); ctx.translate(x, y - bounce); ctx.scale(s, s)
    ant_abdomen(ctx, x=-70, y=60, rx=55, ry=44, t=t + seed)
    ell(ctx, 0, 20, 48, 62)
    ctx.set_source(radial(-15, -15, 4, 80, [(0, ORL), (0.6, OR), (1, ORD)])); ctx.fill()
    # little bib
    ctx.move_to(-30, -30); ctx.curve_to(-34, 30, 34, 30, 30, -30); ctx.close_path()
    setc(ctx, '#FFFFFF' if seed % 2 == 0 else '#BFE6FF'); ctx.fill()
    # arms
    def arms():
        up = arms_up
        for side in (-1, 1):
            if hold is not None:
                hx, hy = hold[0] + side * 48, hold[1]
                arm_path(ctx, side * 40, -20, hx, hy, 60, 60, bend=-side)
                continue
            hx = side * lerp(62, 70, up); hy = lerp(55, -120, up) + math.sin(t * 9 + side) * 8 * up
            arm_path(ctx, side * 40, -20, hx, hy, 50, 50, bend=-side if up > 0.5 else side)
    if hold is None:
        arms()
    ant_head(ctx, t + seed, look, blink_at(t, 3.0, seed * 1.3), mouth, flower=False, baby=True, happy=happy,
             chew=chew, tilt=tilt)
    if hold is not None:
        if hold_cb:
            hold_cb(ctx, hold)
        arms()
    ctx.restore()

# ---------- cat ----------
def draw_cat(ctx, x, y, s, t, twitch=0.0, eye_open=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    br = 1 + math.sin(t * 1.6) * 0.025
    GREY = '#A7ADBD'; GD = '#7E8597'; GL = '#D3D8E4'
    # tail
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for wdt, col in ((62, GD), (50, GREY)):
        ctx.set_line_width(wdt); setc(ctx, col)
        ctx.move_to(260, 40); ctx.curve_to(380, 120, 300, 230, 120, 210); ctx.line_to(-80, 205); ctx.stroke()
    # body
    ctx.save(); ctx.translate(40, 60); ctx.scale(1, br)
    ell(ctx, 0, 0, 300, 165)
    ctx.set_source(radial(-60, -80, 10, 340, [(0, GL), (0.55, GREY), (1, GD)])); ctx.fill()
    ctx.save(); ell(ctx, 0, 0, 300, 165); ctx.clip()
    setc(ctx, '#6C7387', 0.55); ctx.set_line_width(20)
    for k in range(4):
        xx = -40 + k * 75
        ctx.move_to(xx, -175); ctx.curve_to(xx + 30, -110, xx - 10, -60, xx + 15, -30); ctx.stroke()
    ctx.restore(); ctx.restore()
    # paws
    for px in (-290, -190):
        setc(ctx, '#EEF0F6'); ell(ctx, px, 190, 62, 34); ctx.fill()
        setc(ctx, GD); ctx.set_line_width(3); ell(ctx, px, 190, 62, 34); ctx.stroke()
    # head
    hx, hy = -250, 80
    for side, rot in ((-1, -0.25 - twitch * 0.35), (1, 0.25)):
        ctx.save(); ctx.translate(hx + side * 85, hy - 105); ctx.rotate(rot)
        ctx.move_to(-48, 40); ctx.line_to(0, -75); ctx.line_to(48, 40); ctx.close_path(); setc(ctx, GREY); ctx.fill()
        ctx.move_to(-28, 32); ctx.line_to(0, -45); ctx.line_to(28, 32); ctx.close_path(); setc(ctx, '#F6A7B8'); ctx.fill()
        ctx.restore()
    ell(ctx, hx, hy, 150, 128)
    ctx.set_source(radial(hx - 50, hy - 60, 10, 190, [(0, GL), (0.6, GREY), (1, GD)])); ctx.fill()
    setc(ctx, '#F3F4F8'); ell(ctx, hx, hy + 60, 80, 50); ctx.fill()
    # sleeping eyes
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for side in (-1, 1):
        ex, ey = hx + side * 58, hy + 5
        if eye_open > 0.05:
            setc(ctx, '#FFFFFF'); ell(ctx, ex, ey, 26, 22 * eye_open); ctx.fill()
            setc(ctx, '#7BC96F'); ell(ctx, ex, ey, 14, 18 * eye_open); ctx.fill()
            setc(ctx, '#111'); ell(ctx, ex, ey, 5, 15 * eye_open); ctx.fill()
        else:
            setc(ctx, '#3D3F4A'); ctx.set_line_width(7)
            ctx.arc(ex, ey - 10, 26, math.pi * 0.2, math.pi * 0.8); ctx.stroke()
    setc(ctx, '#F27A99'); ctx.move_to(hx - 12, hy + 38); ctx.line_to(hx + 12, hy + 38); ctx.line_to(hx, hy + 50); ctx.close_path(); ctx.fill()
    setc(ctx, '#3D3F4A'); ctx.set_line_width(4)
    ctx.arc(hx - 11, hy + 52, 11, 0, math.pi); ctx.stroke(); ctx.arc(hx + 11, hy + 52, 11, 0, math.pi); ctx.stroke()
    setc(ctx, '#FFFFFF', 0.8); ctx.set_line_width(3)
    for side in (-1, 1):
        for k in range(3):
            ctx.move_to(hx + side * 55, hy + 45 + k * 10); ctx.line_to(hx + side * 150, hy + 30 + k * 18); ctx.stroke()
    ctx.restore()

# ---------- props ----------
class Bowl:
    def __init__(self, cx=540, rimy=1150, rx=240, ry=52, by=1385, brx=150):
        self.cx, self.rimy, self.rx, self.ry, self.by, self.brx = cx, rimy, rx, ry, by, brx
    def body(self, ctx):
        cx, ry_, rx, by, brx, rimy = self.cx, self.ry, self.rx, self.by, self.brx, self.rimy
        ctx.move_to(cx - rx, rimy)
        ctx.curve_to(cx - rx, rimy + 150, cx - brx - 50, by, cx - brx, by)
        ctx.line_to(cx + brx, by)
        ctx.curve_to(cx + brx + 50, by, cx + rx, rimy + 150, cx + rx, rimy)
        ctx.save(); ctx.translate(cx, rimy); ctx.scale(rx, ry_); ctx.arc_negative(0, 0, 1, 0, math.pi); ctx.restore()
        ctx.close_path()
    def width_at(self, y):
        f = clamp((y - self.rimy) / (self.by - self.rimy))
        return lerp(self.rx, self.brx + 30, f ** 1.6)
    def shadow(self, ctx):
        ctx.set_source(radial(self.cx, self.by + 10, 10, self.rx * 1.1, [(0, '#5A3014', 0.35), (1, '#5A3014', 0)]))
        ell(ctx, self.cx, self.by + 8, self.rx * 1.05, 40); ctx.fill()
    def back(self, ctx):
        self.shadow(ctx)
        self.body(ctx); setc(ctx, '#EAF6FF', 0.18); ctx.fill()
        ctx.save(); ctx.translate(self.cx, self.rimy); ctx.scale(self.rx, self.ry)
        ctx.arc(0, 0, 1, math.pi, TAU); ctx.restore()
        setc(ctx, '#FFFFFF', 0.55); ctx.set_line_width(5); ctx.stroke()
    def contents(self, ctx, fill, col, top, extra=None, swirl=0.0, t=0.0):
        """fill 0..1 of depth"""
        if fill <= 0.001:
            return
        level = lerp(self.by - 8, self.rimy + 25, fill)
        ctx.save(); self.body(ctx); ctx.clip()
        ctx.set_source(linear(0, level, 0, self.by, [(0, col), (1, top)]))
        ctx.rectangle(self.cx - self.rx, level, 2 * self.rx, self.by - level + 5); ctx.fill()
        w = self.width_at(level) - 6
        hh = self.ry * w / self.rx
        ell(ctx, self.cx, level, w, hh); setc(ctx, top); ctx.fill()
        if swirl > 0:
            setc(ctx, '#FFFFFF', 0.25 * swirl); ctx.set_line_width(5)
            for k in range(3):
                ctx.save(); ctx.translate(self.cx, level); ctx.scale(w * (0.3 + k * 0.22), hh * (0.3 + k * 0.22))
                ctx.arc(0, 0, 1, t * 5 + k, t * 5 + k + 2.2); ctx.restore(); ctx.stroke()
        if extra:
            extra(ctx, self.cx, level, w, hh)
        ctx.restore()
        return level
    def front(self, ctx):
        self.body(ctx); setc(ctx, '#FFFFFF', 0.10); ctx.fill()
        self.body(ctx); setc(ctx, '#FFFFFF', 0.55); ctx.set_line_width(4); ctx.stroke()
        ctx.save(); ctx.translate(self.cx, self.rimy); ctx.scale(self.rx, self.ry)
        ctx.arc(0, 0, 1, 0, math.pi); ctx.restore()
        setc(ctx, '#FFFFFF', 0.9); ctx.set_line_width(7); ctx.stroke()
        # highlight streaks
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        setc(ctx, '#FFFFFF', 0.55); ctx.set_line_width(12)
        ctx.move_to(self.cx - self.rx + 40, self.rimy + 60); ctx.curve_to(self.cx - self.rx + 50, self.rimy + 130,
                                                                          self.cx - self.brx - 10, self.by - 40, self.cx - self.brx + 10, self.by - 25)
        ctx.stroke()
        setc(ctx, '#FFFFFF', 0.35); ctx.set_line_width(6)
        ctx.move_to(self.cx + self.rx - 50, self.rimy + 70); ctx.line_to(self.cx + self.rx - 70, self.rimy + 140); ctx.stroke()

def canister(ctx, x, y, w, h, label=None, label_size=None):
    # ceramic jar, (x,y) = bottom center
    ctx.set_source(radial(x - w * 0.2, y - h * 0.6, 4, w * 1.0, [(0, '#FFFFFF'), (0.7, '#F6EFE2'), (1, '#D9CDB8')]))
    rr(ctx, x - w / 2, y - h, w, h, w * 0.16); ctx.fill()
    setc(ctx, '#6FA06A'); rr(ctx, x - w * 0.52, y - h - h * 0.13, w * 1.04, h * 0.16, 8); ctx.fill()
    setc(ctx, '#5D8D59'); ell(ctx, x, y - h - h * 0.16, w * 0.12, h * 0.05); ctx.fill()
    if label:
        text(ctx, label, x, y - h * 0.38, label_size or w * 0.26, '#4C7F48', font='Pacifico',
             weight=cairo.FONT_WEIGHT_NORMAL)
    else:
        # leaf
        ctx.save(); ctx.translate(x, y - h * 0.48); setc(ctx, '#6FA06A')
        for a in (-0.6, 0, 0.6):
            ctx.save(); ctx.rotate(a); ell(ctx, 0, -h * 0.12, w * 0.07, h * 0.13); ctx.fill(); ctx.restore()
        ctx.restore()

def egg(ctx, x, y, s, rot=0.0, crack=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ell(ctx, 0, 0, 40, 52)
    ctx.set_source(radial(-12, -18, 3, 60, [(0, '#FFFFFF'), (0.6, '#FBE9CF'), (1, '#E0C29C')])); ctx.fill()
    if crack > 0:
        setc(ctx, '#8A6A40'); ctx.set_line_width(3)
        ctx.move_to(-38, 0); ctx.line_to(-20, -8); ctx.line_to(-6, 6); ctx.line_to(10, -6); ctx.line_to(24, 5); ctx.line_to(38, -2)
        ctx.stroke()
    ctx.restore()

def shell_half(ctx, x, y, s, rot, top=True):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    if top:
        ctx.save(); ctx.scale(40, 52); ctx.arc(0, 0, 1, math.pi, TAU); ctx.restore()
        ctx.line_to(24, 5); ctx.line_to(10, -6); ctx.line_to(-6, 6); ctx.line_to(-20, -8); ctx.close_path()
    else:
        ctx.save(); ctx.scale(40, 52); ctx.arc(0, 0, 1, 0, math.pi); ctx.restore()
        ctx.line_to(-20, -8); ctx.line_to(-6, 6); ctx.line_to(10, -6); ctx.line_to(24, 5); ctx.close_path()
    ctx.set_source(radial(-10, -10, 3, 60, [(0, '#FFFFFF'), (0.6, '#FBE9CF'), (1, '#E0C29C')])); ctx.fill()
    ctx.restore()

def butter(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-40, -10); ctx.line_to(0, -28); ctx.line_to(48, -12); ctx.line_to(8, 6); ctx.close_path()
    setc(ctx, '#FFF2A6'); ctx.fill()
    ctx.move_to(-40, -10); ctx.line_to(8, 6); ctx.line_to(8, 40); ctx.line_to(-40, 24); ctx.close_path()
    setc(ctx, '#FBD95A'); ctx.fill()
    ctx.move_to(8, 6); ctx.line_to(48, -12); ctx.line_to(48, 22); ctx.line_to(8, 40); ctx.close_path()
    setc(ctx, '#EFC43E'); ctx.fill()
    ctx.restore()

def whisk(ctx, x, y, s, rot):
    # (x,y) is the hand position; whisk extends downward along rot
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    rr(ctx, -9, -60, 18, 80, 9); ctx.set_source(linear(-9, 0, 9, 0, [(0, '#E0A060'), (1, '#A8642C')])); ctx.fill()
    setc(ctx, '#C9CED6'); ctx.set_line_width(3.5)
    for k in (-1, -0.4, 0.4, 1):
        ctx.save(); ctx.translate(0, 85); ctx.scale(28 * abs(k) + 4, 70); ctx.arc(0, 0, 1, 0, TAU); ctx.restore(); ctx.stroke()
    ctx.restore()

def spoon(ctx, x, y, s, rot):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.set_source(linear(-8, 0, 8, 0, [(0, '#E8B074'), (1, '#B0703A')]))
    rr(ctx, -7, -70, 14, 170, 7); ctx.fill()
    ell(ctx, 0, 125, 26, 38); ctx.fill()
    ctx.restore()

def knife(ctx, x, y, s, rot):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    rr(ctx, -50, -10, 60, 20, 8); setc(ctx, '#3B2A20'); ctx.fill()
    ctx.move_to(10, -12); ctx.line_to(170, -12); ctx.curve_to(190, -12, 190, 0, 175, 18); ctx.line_to(10, 18); ctx.close_path()
    ctx.set_source(linear(0, -12, 0, 18, [(0, '#FFFFFF'), (0.5, '#C7CDD6'), (1, '#8E96A3')])); ctx.fill()
    ctx.restore()

def board(ctx, x, y, w, h):
    setc(ctx, '#5A3014', 0.25); ell(ctx, x, y + h * 0.55, w * 0.55, h * 0.3); ctx.fill()
    rr(ctx, x - w / 2, y - h / 2, w, h, 26)
    ctx.set_source(linear(0, y - h / 2, 0, y + h / 2, [(0, '#E7B47A'), (1, '#C48447')])); ctx.fill()
    setc(ctx, '#A86A34', 0.4); ctx.set_line_width(3)
    for k in range(4):
        yy = y - h / 2 + 12 + k * h / 4
        ctx.move_to(x - w / 2 + 30, yy); ctx.curve_to(x, yy + 6, x, yy - 6, x + w / 2 - 30, yy); ctx.stroke()
    rr(ctx, x - w / 2, y + h / 2 - 16, w, 16, 8); setc(ctx, '#9B5E2C'); ctx.fill()

def tray(ctx, cx, cy, w, h, depth=26):
    # perspective tray; returns inner rect (x0,y0,x1,y1)
    setc(ctx, '#5A3014', 0.25); ell(ctx, cx, cy + h / 2 + 18, w * 0.55, 30); ctx.fill()
    tw = w * 0.86
    ctx.move_to(cx - tw / 2, cy - h / 2); ctx.line_to(cx + tw / 2, cy - h / 2); ctx.line_to(cx + w / 2, cy + h / 2)
    ctx.line_to(cx - w / 2, cy + h / 2); ctx.close_path()
    ctx.set_source(linear(0, cy - h / 2, 0, cy + h / 2, [(0, '#C9CFD8'), (1, '#9AA2AE')])); ctx.fill()
    # front lip
    ctx.move_to(cx - w / 2, cy + h / 2); ctx.line_to(cx + w / 2, cy + h / 2); ctx.line_to(cx + w / 2 - 6, cy + h / 2 + depth)
    ctx.line_to(cx - w / 2 + 6, cy + h / 2 + depth); ctx.close_path()
    ctx.set_source(linear(0, cy + h / 2, 0, cy + h / 2 + depth, [(0, '#EEF1F5'), (1, '#9AA2AE')])); ctx.fill()
    # parchment
    pw = tw * 0.9
    ctx.move_to(cx - pw / 2, cy - h / 2 + 10); ctx.line_to(cx + pw / 2, cy - h / 2 + 10)
    ctx.line_to(cx + w * 0.45, cy + h / 2 - 8); ctx.line_to(cx - w * 0.45, cy + h / 2 - 8); ctx.close_path()
    setc(ctx, '#FFF5E4'); ctx.fill()

def tray_slots(cx, cy, w, h, cols=3, rows=3):
    out = []
    for r in range(rows):
        fy = (r + 0.5) / rows
        y = cy - h / 2 + 10 + fy * (h - 18)
        rowW = lerp(w * 0.86 * 0.9, w * 0.9, fy)
        for c in range(cols):
            fx = (c + 0.5) / cols
            out.append((cx - rowW / 2 + fx * rowW, y, lerp(0.82, 1.0, fy)))
    return out

def dough_ball(ctx, x, y, s, bake=0.0, seed=0):
    rnd = random.Random(seed)
    rx = lerp(34, 56, bake) * s; ry = lerp(28, 30, bake) * s
    top = lerp(0, 0, bake)
    col = ('#F1D3A0', '#D9A15C')
    c1 = '#F6DDB0' if bake < 0.5 else '#E7B46A'
    c2 = lerp_hex('#E9C58E', '#B9752E', bake)
    setc(ctx, '#5A3014', 0.18 + bake * 0.1); ell(ctx, x, y + ry * 0.6, rx * 1.02, ry * 0.5); ctx.fill()
    ell(ctx, x, y, rx, ry)
    ctx.set_source(radial(x - rx * 0.3, y - ry * 0.5, 2, rx * 1.2, [(0, lerp_hex('#FFF0D0', '#F2C57E', bake)), (0.6, lerp_hex('#F0D29C', '#D99A4E', bake)), (1, c2)]))
    ctx.fill()
    if bake > 0.5:
        setc(ctx, '#8A4A1A', 0.35 * (bake - 0.5) * 2); ctx.set_line_width(2.5 * s)
        for k in range(3):
            a = rnd.uniform(0, TAU); r0 = rnd.uniform(0.2, 0.6)
            ctx.move_to(x + math.cos(a) * rx * r0, y + math.sin(a) * ry * r0)
            ctx.line_to(x + math.cos(a + 0.5) * rx * (r0 + 0.3), y + math.sin(a + 0.5) * ry * (r0 + 0.3)); ctx.stroke()
    for k in range(5):
        a = rnd.uniform(0, TAU); r0 = rnd.uniform(0, 0.7)
        cx_ = x + math.cos(a) * rx * r0; cy_ = y + math.sin(a) * ry * r0 - 3 * s
        setc(ctx, '#4A220C'); ell(ctx, cx_, cy_, 7 * s, 6 * s); ctx.fill()
        setc(ctx, '#FFFFFF', 0.3); ell(ctx, cx_ - 2 * s, cy_ - 2 * s, 2 * s, 2 * s); ctx.fill()

def lerp_hex(a, b, x):
    ca, cb = hexc(a), hexc(b)
    r = [int(255 * lerp(ca[i], cb[i], clamp(x))) for i in range(3)]
    return '#%02X%02X%02X' % tuple(r)

def cookie(ctx, x, y, s, seed=0, bite=0):
    rnd = random.Random(seed)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.push_group()
    ell(ctx, 0, 0, 60, 52)
    ctx.set_source(radial(-15, -15, 3, 70, [(0, '#F7CB82'), (0.7, '#DFA058'), (1, '#B9752E')])); ctx.fill()
    setc(ctx, '#9A5A22', 0.4); ctx.set_line_width(3)
    for k in range(4):
        a = rnd.uniform(0, TAU); r0 = rnd.uniform(0.2, 0.6)
        ctx.move_to(math.cos(a) * 60 * r0, math.sin(a) * 52 * r0); ctx.line_to(math.cos(a + 0.4) * 60 * (r0 + 0.3), math.sin(a + 0.4) * 52 * (r0 + 0.3)); ctx.stroke()
    for k in range(7):
        a = rnd.uniform(0, TAU); r0 = rnd.uniform(0, 0.75)
        setc(ctx, '#4A220C'); ell(ctx, math.cos(a) * 60 * r0, math.sin(a) * 52 * r0, 9, 7); ctx.fill()
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    for k in range(bite):
        bx, by = 45, -25 + k * 22
        for j in range(3):
            ell(ctx, bx + 10, by + j * 12 - 12, 16, 16); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint()
    ctx.restore()

def oven_mitt(ctx, x, y, s=1.0):
    ell(ctx, x, y, 28 * s, 24 * s); ctx.set_source(gingham('#F2709A', 7)); ctx.fill()

# ---------- backgrounds ----------
def kitchen_bg():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source(linear(0, 0, 0, H, [(0, '#F9E7CF'), (0.6, '#F3D5B0'), (1, '#E9C397')])); c.paint()
    # window (left)
    wx, wy, ww, wh = 40, 380, 330, 620
    c.save(); c.move_to(wx, wy + wh); c.line_to(wx, wy + ww / 2); c.arc(wx + ww / 2, wy + ww / 2, ww / 2, math.pi, TAU)
    c.line_to(wx + ww, wy + wh); c.close_path(); c.clip()
    c.set_source(linear(0, wy, 0, wy + wh, [(0, '#FFF6D8'), (0.5, '#CFEAB0'), (1, '#8CC57A')])); c.paint()
    rnd = random.Random(3)
    for k in range(18):
        setc(c, rnd.choice(['#7DBB6A', '#9BD082', '#6AA85A']), 0.8)
        ell(c, wx + rnd.uniform(0, ww), wy + wh * rnd.uniform(0.55, 1.0), rnd.uniform(40, 90), rnd.uniform(30, 60)); c.fill()
    c.set_source(radial(wx + ww * 0.6, wy + 120, 10, 300, [(0, '#FFFFFF', 0.9), (1, '#FFFFFF', 0)])); c.paint()
    c.restore()
    # frame
    c.set_line_width(26); setc(c, '#D9965A')
    c.move_to(wx, wy + wh); c.line_to(wx, wy + ww / 2); c.arc(wx + ww / 2, wy + ww / 2, ww / 2, math.pi, TAU); c.line_to(wx + ww, wy + wh); c.stroke()
    c.set_line_width(12); c.move_to(wx + ww / 2, wy + 10); c.line_to(wx + ww / 2, wy + wh); c.stroke()
    c.move_to(wx, wy + wh * 0.55); c.line_to(wx + ww, wy + wh * 0.55); c.stroke()
    rr(c, wx - 30, wy + wh - 5, ww + 60, 34, 8); setc(c, '#C9824A'); c.fill()
    # pot plant on sill
    px, py = wx + ww * 0.3, wy + wh - 5
    c.move_to(px - 45, py - 80); c.line_to(px + 45, py - 80); c.line_to(px + 34, py); c.line_to(px - 34, py); c.close_path(); setc(c, '#D8774A'); c.fill()
    for k in range(9):
        a = -math.pi / 2 + (k - 4) * 0.28
        c.save(); c.translate(px, py - 85); c.rotate(a + math.pi / 2); setc(c, '#5E9E4E' if k % 2 else '#78B865')
        ell(c, 0, -55, 16, 52); c.fill(); c.restore()
    # shelf right with canisters
    sy = 400
    rr(c, 520, sy, 560, 26, 6); setc(c, '#C8834A'); c.fill()
    for i, (x, w_, h_) in enumerate([(610, 110, 150), (740, 120, 175), (875, 110, 140), (1000, 100, 120)]):
        canister(c, x, sy, w_, h_)
    # hanging plant top
    for k in range(7):
        c.save(); c.translate(560 + k * 20, 120); setc(c, '#5E9E4E' if k % 2 else '#78B865')
        for j in range(6):
            ell(c, math.sin(j + k) * 18, j * 38, 22, 15); c.fill()
        c.restore()
    rr(c, 520, 70, 150, 70, 20); setc(c, '#D8774A'); c.fill()
    # hanging utensils on right wall
    for i, x in enumerate([820, 950]):
        setc(c, '#B97B44'); c.set_line_width(5); c.move_to(x, 470); c.line_to(x, 490); c.stroke()
        rr(c, x - 10, 490, 20, 180, 10); setc(c, '#D9A066'); c.fill()
        ell(c, x, 730 if i == 0 else 720, 50 if i == 0 else 40, 75 if i == 0 else 60); setc(c, '#D9A066'); c.fill()
        if i == 1:
            setc(c, '#B97B44'); c.set_line_width(4)
            for k in range(-2, 3):
                c.move_to(x + k * 13, 680); c.line_to(x + k * 13, 765); c.stroke()
    # warm light
    c.set_source(radial(260, 600, 20, 900, [(0, '#FFF3C4', 0.55), (1, '#FFF3C4', 0)])); c.paint()
    # back counter & stove hint
    rr(c, 640, 1000, 460, 340, 10); setc(c, '#E9C9A6'); c.fill()
    rr(c, 640, 990, 460, 26, 6); setc(c, '#C88A52'); c.fill()
    setc(c, '#D2AE87'); c.set_line_width(4); c.move_to(870, 1030); c.line_to(870, 1340); c.stroke()
    for k in (760, 990):
        setc(c, '#B98A5E'); ell(c, k, 1100, 18, 8); c.fill()
    return s

def counter_fg():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    top = 1340
    c.rectangle(0, top, W, 80); c.set_source(linear(0, top, 0, top + 80, [(0, '#E7B27A'), (1, '#C98A4E')])); c.fill()
    setc(c, '#FFFFFF', 0.25); c.rectangle(0, top, W, 5); c.fill()
    c.rectangle(0, top + 80, W, H - top - 80); c.set_source(linear(0, top + 80, 0, H, [(0, '#B9773E'), (1, '#7E4A22')])); c.fill()
    setc(c, '#6A3C1A', 0.5); c.set_line_width(4)
    for x in range(0, W, 180):
        c.move_to(x, top + 80); c.line_to(x, H); c.stroke()
    # wood grain on top
    setc(c, '#A86A34', 0.25); c.set_line_width(2)
    for k in range(5):
        y = top + 12 + k * 14
        c.move_to(0, y); c.curve_to(300, y + 6, 700, y - 6, W, y + 3); c.stroke()
    # gingham towel
    c.move_to(60, top + 60); c.line_to(360, top + 60); c.line_to(340, top + 360); c.curve_to(250, top + 380, 150, top + 340, 80, top + 360); c.close_path()
    c.set_source(gingham('#F2709A', 18)); c.fill()
    rr(c, 50, top + 45, 320, 30, 12); setc(c, '#FFFFFF'); c.fill()
    return s

def room_bg():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source(linear(0, 0, 0, 1150, [(0, '#F6DDBE'), (1, '#EBC59C')])); c.paint()
    # wall art & lamp glow
    c.set_source(radial(900, 420, 10, 600, [(0, '#FFE9B0', 0.9), (1, '#FFE9B0', 0)])); c.paint()
    rr(c, 120, 300, 260, 200, 10); setc(c, '#C98E5A'); c.fill(); rr(c, 140, 320, 220, 160, 6); setc(c, '#BFE0D0'); c.fill()
    setc(c, '#8CC57A'); c.move_to(140, 480); c.line_to(220, 380); c.line_to(290, 450); c.line_to(360, 400); c.line_to(360, 480); c.close_path(); c.fill()
    setc(c, '#FFE27A'); ell(c, 310, 360, 22, 22); c.fill()
    # lamp
    c.move_to(840, 380); c.line_to(960, 380); c.line_to(1000, 520); c.line_to(800, 520); c.close_path(); setc(c, '#FFF0C8'); c.fill()
    rr(c, 892, 520, 16, 330, 8); setc(c, '#B97B44'); c.fill()
    # sofa (back)
    rr(c, -40, 640, 760, 360, 60); setc(c, '#C9B7A6'); c.fill()
    rr(c, -40, 860, 820, 250, 50); setc(c, '#BBA898'); c.fill()
    # knit throw
    c.move_to(40, 660); c.line_to(300, 650); c.line_to(330, 1080); c.line_to(60, 1100); c.close_path()
    setc(c, '#F3A6B9'); c.fill()
    setc(c, '#E58AA2'); c.set_line_width(5)
    for k in range(8):
        x = 60 + k * 34
        c.move_to(x, 665); c.line_to(x + 12, 1090); c.stroke()
    # baseboard
    c.rectangle(0, 1120, W, 40); setc(c, '#F7EBDD'); c.fill()
    # floor
    c.rectangle(0, 1160, W, H - 1160); c.set_source(linear(0, 1160, 0, H, [(0, '#C98A50'), (1, '#9A5E2C')])); c.fill()
    setc(c, '#7E4A22', 0.45); c.set_line_width(3)
    for k in range(-6, 14):
        c.move_to(540 + k * 40, 1160); c.line_to(540 + k * 160, H); c.stroke()
    for y in (1240, 1360, 1520, 1720):
        c.move_to(0, y); c.line_to(W, y); c.stroke()
    setc(c, '#FFFFFF', 0.08); c.rectangle(0, 1160, W, H); c.fill()
    # rug
    ell(c, 640, 1500, 520, 170); setc(c, '#F7D6DE'); c.fill()
    setc(c, '#E9AFC0'); c.set_line_width(6)
    for k in range(1, 4):
        ell(c, 640, 1500, 520 - k * 60, 170 - k * 25); c.stroke()
    # sunbeam
    c.move_to(0, 200); c.line_to(300, 200); c.line_to(900, H); c.line_to(300, H); c.close_path()
    setc(c, '#FFF6D0', 0.12); c.fill()
    return s

def home_bg():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source(linear(0, 0, 0, 1250, [(0, '#FBE6CC'), (1, '#F0CFA8')])); c.paint()
    # arched doorway
    dx, dy, dw, dh = 60, 520, 360, 760
    c.save(); c.move_to(dx, dy + dh); c.line_to(dx, dy + dw / 2); c.arc(dx + dw / 2, dy + dw / 2, dw / 2, math.pi, TAU); c.line_to(dx + dw, dy + dh); c.close_path(); c.clip()
    c.set_source(linear(0, dy, 0, dy + dh, [(0, '#FFF9E0'), (0.6, '#DFF2C0'), (1, '#9CCB7E')])); c.paint()
    c.set_source(radial(dx + dw / 2, dy + 200, 10, 400, [(0, '#FFFFFF', 1), (1, '#FFFFFF', 0)])); c.paint()
    c.restore()
    c.set_line_width(30); setc(c, '#C88A52')
    c.move_to(dx, dy + dh); c.line_to(dx, dy + dw / 2); c.arc(dx + dw / 2, dy + dw / 2, dw / 2, math.pi, TAU); c.line_to(dx + dw, dy + dh); c.stroke()
    # shelf & plant & jars
    rr(c, 560, 520, 460, 24, 6); setc(c, '#C8834A'); c.fill()
    canister(c, 650, 520, 90, 120); canister(c, 760, 520, 100, 140)
    c.move_to(880, 440); c.line_to(980, 440); c.line_to(965, 520); c.line_to(895, 520); c.close_path(); setc(c, '#D8774A'); c.fill()
    for k in range(9):
        c.save(); c.translate(930, 440); c.rotate((k - 4) * 0.3); setc(c, '#5E9E4E' if k % 2 else '#78B865'); ell(c, 0, -50, 14, 45); c.fill(); c.restore()
    # flowers vase
    # floor
    c.rectangle(0, 1250, W, H - 1250); c.set_source(linear(0, 1250, 0, H, [(0, '#D69A5C'), (1, '#A86A34')])); c.fill()
    setc(c, '#8A5228', 0.4); c.set_line_width(3)
    for k in range(-6, 14):
        c.move_to(540 + k * 45, 1250); c.line_to(540 + k * 150, H); c.stroke()
    c.set_source(radial(240, 700, 20, 900, [(0, '#FFF3C4', 0.45), (1, '#FFF3C4', 0)])); c.paint()
    return s

def table(ctx, cx, top_y, w, cloth=True):
    # round table front view with cloth
    setc(ctx, '#5A3014', 0.25); ell(ctx, cx, top_y + 430, w * 0.55, 40); ctx.fill()
    for lx in (cx - w * 0.35, cx + w * 0.35):
        rr(ctx, lx - 16, top_y + 100, 32, 330, 10); setc(ctx, '#B5743C'); ctx.fill()
    ell(ctx, cx, top_y, w / 2, 60); setc(ctx, '#FFF4DE'); ctx.fill()
    ctx.move_to(cx - w / 2, top_y)
    ctx.curve_to(cx - w / 2 - 10, top_y + 100, cx - w / 2 + 10, top_y + 200, cx - w / 2 + 20, top_y + 230)
    for k in range(8):
        x0 = cx - w / 2 + 20 + k * (w - 40) / 8
        ctx.curve_to(x0 + 20, top_y + 260, x0 + (w - 40) / 8 - 20, top_y + 260, x0 + (w - 40) / 8, top_y + 230)
    ctx.curve_to(cx + w / 2 - 10, top_y + 200, cx + w / 2 + 10, top_y + 100, cx + w / 2, top_y)
    ctx.save(); ctx.translate(cx, top_y); ctx.scale(w / 2, 60); ctx.arc(0, 0, 1, 0, math.pi); ctx.restore()
    ctx.close_path()
    ctx.set_source(linear(0, top_y, 0, top_y + 260, [(0, '#FFF4DE'), (1, '#EED9B6')])); ctx.fill()
    rnd = random.Random(5)
    for k in range(14):
        x = cx - w / 2 + 40 + rnd.uniform(0, w - 80); y = top_y + rnd.uniform(40, 220)
        ctx.save(); ctx.translate(x, y); setc(ctx, '#7FAE6A', 0.8)
        for a in (-0.7, 0, 0.7):
            ctx.save(); ctx.rotate(a); ell(ctx, 0, -14, 6, 14); ctx.fill(); ctx.restore()
        ctx.restore()

def plate(ctx, cx, cy, w):
    setc(ctx, '#5A3014', 0.2); ell(ctx, cx, cy + 14, w * 0.52, w * 0.13); ctx.fill()
    ell(ctx, cx, cy, w / 2, w * 0.14); setc(ctx, '#FFFFFF'); ctx.fill()
    ell(ctx, cx, cy, w * 0.36, w * 0.09); setc(ctx, '#F1EBE4'); ctx.fill()
    ell(ctx, cx, cy, w / 2, w * 0.14); setc(ctx, '#7FAE6A'); ctx.set_line_width(4); ctx.stroke()

def vignette(ctx, strength=0.35):
    ctx.set_source(radial(W / 2, H / 2, H * 0.35, H * 0.75, [(0, '#3A1A0A', 0), (1, '#3A1A0A', strength)]))
    ctx.paint()

def warm_glow(ctx, a=0.12):
    setc(ctx, '#FFB866', a)
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT); ctx.paint(); ctx.set_operator(cairo.OPERATOR_OVER)
