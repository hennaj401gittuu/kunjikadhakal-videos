"""9:16 TRY IT Short (brain/body trick done along with the video) for Kandupidi.
Trick: the floating arm (Kohnstamm effect) - push the back of the hand against a door frame for 30 s, step away, the arm rises by itself.
Soft pseudo-3D kid (yellow T-shirt, jeans) in a cosy room; two-line top captions (white + coloured); circular 30 s countdown;
glowing brain with a yellow signal line down to the shoulder muscle; KOHNSTAMM EFFECT name card; comment/share/follow end.
Soothing female narrator ('female', 1.05, 1.08). python3 tryit_short.py stills | render"""
import sys, math, os, random, subprocess, cairo
sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/money'); sys.path.insert(0, '/home/claude/ml')
import wd
wd.W, wd.H = 1080, 1920
from wd import text, text_w, pill
from pz import voice, wav_dur, clamp, prog, sprog, back, hexc, rrect, sfx2, SR, A, lerp, smooth
import numpy as np, soundfile as sf
W, H = 1080, 1920
VOICE = ('female', 0.95, 1.08)
OUT = '/home/claude/tryit/outs'; os.makedirs(OUT, exist_ok=True)
NAME = 'KP_Your_Arm_Will_Float_Mini'
FEET = 1470
DOOR_R = 540 + 196          # inner edge of the right door jamb (kid stands at x=540)
CD_LEN = 30.0

def grad(y0, y1, c0, c1, x0=0, x1=0):
    g = cairo.LinearGradient(x0, y0, x1, y1); g.add_color_stop_rgba(0, *hexc(c0)); g.add_color_stop_rgba(1, *hexc(c1)); return g

# ------------------------------------------------------------------ room
_bg = {}
def room():
    if 'room' in _bg: return _bg['room']
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source(grad(0, 1300, '#f6d9b8', '#e9b98f')); c.paint()
    # wallpaper stripes
    for x in range(0, W, 90): c.rectangle(x, 0, 36, 1300); c.set_source_rgba(1, 1, 1, 0.07); c.fill()
    # window with bars (left)
    rrect(c, 40, 560, 230, 330, 14); c.set_source(grad(560, 890, '#9fd3f0', '#e8f6ff')); c.fill()
    c.set_source_rgba(*hexc('#8a5a3a')); c.set_line_width(16); rrect(c, 40, 560, 230, 330, 14); c.stroke()
    c.set_line_width(7)
    for k in range(1, 4): c.move_to(40 + k*57, 560); c.line_to(40 + k*57, 890); c.stroke()
    # framed picture (top right)
    rrect(c, 830, 470, 190, 150, 8); c.set_source_rgba(*hexc('#6a4224')); c.fill()
    c.rectangle(848, 488, 154, 114); c.set_source(grad(488, 602, '#ffb36b', '#7fc6a0')); c.fill()
    c.move_to(848, 602); c.line_to(905, 530); c.line_to(950, 575); c.line_to(1002, 520); c.line_to(1002, 602); c.close_path()
    c.set_source_rgba(*hexc('#2f6d5e')); c.fill()
    # doorway (centre) - dark inner room
    c.rectangle(250, 470, DOOR_R - 250, FEET - 470 + 10); c.set_source(grad(470, FEET, '#3a2a4a', '#5a4560')); c.fill()
    c.rectangle(250, 470, DOOR_R - 250, FEET - 470 + 10); c.set_source(grad(0, 0, '#000000', '#000000')); c.set_source_rgba(0, 0, 0, 0.0); c.fill()
    for (x, w) in ((215, 40), (DOOR_R, 40)):
        c.rectangle(x, 440, w, FEET - 440 + 20); c.set_source(grad(0, 0, '#a8744a', '#7a4e2e', x, x + w)); c.fill()
    c.rectangle(215, 430, DOOR_R + 40 - 215, 44); c.set_source(grad(430, 474, '#b07a4a', '#7a4e2e')); c.fill()
    # floor
    c.rectangle(0, 1300, W, H - 1300); c.set_source(grad(1300, H, '#c98e5a', '#8e5a34')); c.fill()
    for k in range(8):
        y = 1300 + k*k*12 + k*20; c.rectangle(0, y, W, 3); c.set_source_rgba(0, 0, 0, 0.12); c.fill()
    c.rectangle(0, 1290, W, 18); c.set_source_rgba(*hexc('#f4e3c8')); c.fill()
    # rug
    c.save(); c.translate(540, 1480); c.scale(1, 0.22); c.arc(0, 0, 420, 0, 2*math.pi); c.restore()
    c.set_source_rgba(*hexc('#3f7fb0', 0.55)); c.fill()
    # potted plant (right floor)
    c.move_to(880, 1390); c.line_to(1020, 1390); c.line_to(1000, 1500); c.line_to(900, 1500); c.close_path(); c.set_source(grad(1390, 1500, '#e0784a', '#b0502a')); c.fill()
    for k in range(7):
        a = -math.pi/2 + (k - 3)*0.38
        c.save(); c.translate(950, 1390); c.rotate(a + math.pi/2)
        c.move_to(0, 0); c.curve_to(-45, -80, -30, -170, 0, -230); c.curve_to(30, -170, 45, -80, 0, 0); c.restore()
        c.set_source_rgba(*hexc('#2f8f5a' if k % 2 else '#3fae6a')); c.fill()
    # lamp glow
    g = cairo.RadialGradient(800, 300, 20, 800, 300, 700); g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.35); g.add_color_stop_rgba(1, 1, 0.9, 0.7, 0)
    c.set_source(g); c.paint()
    _bg['room'] = s; return s

def blur_room():
    if 'blur' in _bg: return _bg['blur']
    from PIL import Image, ImageFilter
    src = room(); src.flush()
    im = Image.frombuffer('RGBA', (W, H), bytes(src.get_data()), 'raw', 'BGRA', 0, 1).filter(ImageFilter.GaussianBlur(18))
    data = bytearray(im.tobytes('raw', 'BGRA'))
    s = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, W, H); _bg['blur_data'] = data
    _bg['blur'] = s; return s

def vignette(ctx, a=0.45):
    g = cairo.RadialGradient(W/2, H*0.45, 300, W/2, H*0.45, 1200); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, a)
    ctx.set_source(g); ctx.paint()

# ------------------------------------------------------------------ kid (soft pseudo-3D)
SKIN, SKIN_D = '#f3c39a', '#d99a6c'
def limb(ctx, x0, y0, x1, y1, w, c0, c1):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(w)
    nx, ny = (y1 - y0), -(x1 - x0); L = math.hypot(nx, ny) or 1; nx, ny = nx/L, ny/L
    g = cairo.LinearGradient(x0 - nx*w/2, y0 - ny*w/2, x0 + nx*w/2, y0 + ny*w/2)
    g.add_color_stop_rgba(0, *hexc(c0)); g.add_color_stop_rgba(1, *hexc(c1))
    ctx.set_source(g); ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()

def arm(ctx, side, a, glow=0.0):
    """side +1 = screen right. a = angle outward from hanging down (rad). returns hand pos."""
    sx, sy = side*118, -540
    L1, L2 = 120, 175
    dx, dy = side*math.sin(a), math.cos(a)
    ex, ey = sx + dx*L1, sy + dy*L1
    hx, hy = sx + dx*(L1 + L2), sy + dy*(L1 + L2)
    limb(ctx, ex, ey, hx, hy, 58, '#f8d2ae', SKIN_D)
    limb(ctx, sx, sy, ex + dx*8, ey + dy*8, 78, '#ffe066', '#e0a800')
    if glow > 0:
        g = cairo.RadialGradient(sx + dx*40, sy + dy*40, 5, sx + dx*40, sy + dy*40, 140)
        g.add_color_stop_rgba(0, 1, 0.35, 0.2, 0.75*glow); g.add_color_stop_rgba(1, 1, 0.35, 0.2, 0)
        ctx.set_source(g); ctx.arc(sx + dx*40, sy + dy*40, 140, 0, 2*math.pi); ctx.fill()
    g = cairo.RadialGradient(hx - 10, hy - 10, 4, hx, hy, 40); g.add_color_stop_rgba(0, *hexc('#ffe0c2')); g.add_color_stop_rgba(1, *hexc(SKIN_D))
    ctx.set_source(g); ctx.arc(hx, hy, 38, 0, 2*math.pi); ctx.fill()
    return hx, hy

def kid(ctx, x, y, s, t, aR=0.0, aL=0.0, mood='smile', talk=0.0, glowR=0.0, push=0.0, bob=True, nose=False):
    """mood: smile/effort/wow/closed (eyes shut, calm smile). nose=True draws a soft shaded nose."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    br = 4*math.sin(t*2.2) if bob else 0
    # shadow
    ctx.save(); ctx.translate(0, 0); ctx.scale(1, 0.18); ctx.arc(0, 0, 230, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(0, 0, 0, 0.22); ctx.fill()
    # legs (jeans) + shoes
    for sd in (-1, 1):
        limb(ctx, sd*55, -280, sd*62, -40, 92, '#5b8fd8', '#2f5aa0')
        ctx.save(); ctx.translate(sd*70, -22); ctx.scale(1.5, 0.8); ctx.arc(0, 0, 48, math.pi, 2*math.pi); ctx.close_path(); ctx.restore()
        ctx.set_source(grad(-60, 0, '#ffffff', '#c9c9d6')); ctx.fill()
    ctx.translate(0, br)
    # torso (T-shirt)
    rrect(ctx, -150, -590, 300, 330, 90); ctx.set_source(grad(0, 0, '#ffe77a', '#e8a900', -150, 150)); ctx.fill()
    rrect(ctx, -150, -320, 300, 70, 30); ctx.set_source(grad(0, 0, '#5b8fd8', '#2f5aa0', -150, 150)); ctx.fill()
    ctx.move_to(-40, -588); ctx.curve_to(-20, -555, 20, -555, 40, -588); ctx.set_source_rgba(*hexc('#c98a00')); ctx.set_line_width(8); ctx.stroke()
    jit = push*3*math.sin(t*60)
    hL = arm(ctx, -1, aL)
    ctx.save(); ctx.translate(jit, 0); hR = arm(ctx, 1, aR, glowR); ctx.restore()
    # neck + head
    rrect(ctx, -32, -640, 64, 70, 20); ctx.set_source_rgba(*hexc(SKIN_D)); ctx.fill()
    hy = -800
    for ex in (-162, 162):
        ctx.arc(ex, hy + 20, 34, 0, 2*math.pi); ctx.set_source_rgba(*hexc(SKIN_D)); ctx.fill()
    g = cairo.RadialGradient(-50, hy - 60, 20, 0, hy, 190); g.add_color_stop_rgba(0, *hexc('#ffe2c6')); g.add_color_stop_rgba(1, *hexc('#e8a878'))
    ctx.set_source(g); ctx.save(); ctx.translate(0, hy); ctx.scale(1.0, 0.94); ctx.arc(0, 0, 170, 0, 2*math.pi); ctx.restore(); ctx.fill()
    # hair
    ctx.save(); ctx.translate(0, hy)
    ctx.move_to(-172, 10); ctx.curve_to(-190, -150, -60, -200, 20, -190); ctx.curve_to(140, -185, 200, -110, 172, 10)
    ctx.curve_to(150, -70, 90, -95, 40, -90); ctx.curve_to(10, -60, -40, -100, -80, -80); ctx.curve_to(-130, -70, -150, -40, -172, 10); ctx.close_path()
    ctx.set_source(grad(-200, 0, '#4a2e1e', '#20120a')); ctx.fill()
    ctx.restore()
    # face
    ey = hy + 5
    for ex in (-62, 62):
        if mood == 'effort':
            ctx.set_source_rgba(*hexc('#2b1a12')); ctx.set_line_width(9); ctx.move_to(ex - 30, ey - 5); ctx.line_to(ex + 30, ey + 5 if ex < 0 else ey - 5); ctx.stroke()
            ctx.move_to(ex - 26, ey + 8); ctx.curve_to(ex - 10, ey + 20, ex + 10, ey + 20, ex + 26, ey + 8); ctx.stroke()
            continue
        if mood == 'closed':
            ctx.set_source_rgba(*hexc('#2b1a12')); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(ex - 30, ey); ctx.curve_to(ex - 12, ey + 22, ex + 12, ey + 22, ex + 30, ey); ctx.stroke()
            for k in (-18, 0, 18):
                ctx.move_to(ex + k, ey + 15); ctx.line_to(ex + k*1.3, ey + 30); ctx.stroke()
            ctx.set_source_rgba(*hexc('#3a2216')); ctx.move_to(ex - 30, ey - 48); ctx.curve_to(ex - 10, ey - 58, ex + 10, ey - 58, ex + 30, ey - 48); ctx.stroke()
            continue
        big = 1.25 if mood == 'wow' else 1.0
        ctx.save(); ctx.translate(ex, ey); ctx.scale(big, big)
        ctx.save(); ctx.scale(1, 1.15); ctx.arc(0, 0, 30, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.arc(3, 4, 20, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#2b1a12')); ctx.fill()
        ctx.arc(10, -4, 7, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.restore()
        ctx.set_source_rgba(*hexc('#3a2216')); ctx.set_line_width(9)
        lift = 16 if mood == 'wow' else 0
        ctx.move_to(ex - 30, ey - 52 - lift); ctx.curve_to(ex - 10, ey - 62 - lift, ex + 10, ey - 62 - lift, ex + 30, ey - 52 - lift); ctx.stroke()
    for ex in (-100, 100):
        g = cairo.RadialGradient(ex, ey + 55, 2, ex, ey + 55, 36); g.add_color_stop_rgba(0, 1, 0.45, 0.45, 0.55); g.add_color_stop_rgba(1, 1, 0.45, 0.45, 0)
        ctx.set_source(g); ctx.arc(ex, ey + 55, 36, 0, 2*math.pi); ctx.fill()
    if nose:
        ny = hy + 50
        g = cairo.RadialGradient(-6, ny - 8, 2, 0, ny, 34); g.add_color_stop_rgba(0, *hexc('#ffd9bb')); g.add_color_stop_rgba(1, *hexc('#e09a6c'))
        ctx.set_source(g); ctx.save(); ctx.translate(0, ny); ctx.scale(1.0, 0.82); ctx.arc(0, 0, 30, 0, 2*math.pi); ctx.restore(); ctx.fill()
        ctx.set_source_rgba(*hexc('#b8704a')); ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for sd in (-1, 1):
            ctx.move_to(sd*24, ny + 6); ctx.curve_to(sd*30, ny + 16, sd*18, ny + 22, sd*10, ny + 18); ctx.stroke()
        ctx.arc(-9, ny - 10, 7, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 0.55); ctx.fill()
    my = hy + 85
    if mood == 'closed': mood = 'smile'
    if mood == 'wow':
        ctx.save(); ctx.translate(0, my + 8); ctx.scale(1, 1.25); ctx.arc(0, 0, 26, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(*hexc('#7a2a2a')); ctx.fill()
    elif mood == 'effort':
        rrect(ctx, -45, my - 10, 90, 34, 12); ctx.set_source_rgba(*hexc('#7a2a2a')); ctx.fill()
        rrect(ctx, -40, my - 6, 80, 14, 6); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    else:
        o = 6 + 18*talk
        ctx.move_to(-48, my - 6); ctx.curve_to(-25, my + 22 + o, 25, my + 22 + o, 48, my - 6); ctx.curve_to(20, my + 6, -20, my + 6, -48, my - 6)
        ctx.set_source_rgba(*hexc('#8a2e2e')); ctx.fill()
    ctx.restore()
    return (x + hR[0]*s, y + (hR[1] + br)*s), (x + hL[0]*s, y + (hL[1] + br)*s)

# ------------------------------------------------------------------ widgets
def otext(ctx, s, x, y, size, col, lw=12, align='c', alpha=1.0, font='Poppins ExtraBold'):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
    xb, yb, w, h, xa, ya = ctx.text_extents(s)
    x0 = x - (w/2 + xb) if align == 'c' else x - xb
    ctx.move_to(x0, y); ctx.text_path(s)
    ctx.set_source_rgba(0.06, 0.05, 0.12, 0.9*alpha); ctx.set_line_width(lw); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*hexc(col, alpha)); ctx.fill()
    return w

def fit(ctx, s, size, maxw=1000):
    ctx.select_font_face('Poppins ExtraBold', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    while size > 40:
        ctx.set_font_size(size)
        if ctx.text_extents(s)[4] <= maxw: break
        size -= 2
    return size

def caption2(ctx, l1, l2, col, t, t0, t1, y=225):
    """two-line top caption: white line + coloured line, words revealed while spoken"""
    words = [(w_, 0) for w_ in l1.split()] + [(w_, 1) for w_ in l2.split()]
    n = len(words); dur = max(0.5, (t1 - t0)*0.85)
    sizes = [fit(ctx, l1, 70), fit(ctx, l2, 84)]
    pop = back(prog(t, t0 - 0.05, 0.25))
    for li, (line, size) in enumerate(((l1, sizes[0]), (l2, sizes[1]))):
        if not line: continue
        ctx.select_font_face('Poppins ExtraBold', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
        sp = ctx.text_extents(' ')[4]; ws = line.split(); tw = sum(ctx.text_extents(w_)[4] for w_ in ws) + sp*(len(ws) - 1)
        x = W/2 - tw/2; yy = y + li*96
        for w_ in ws:
            i = words.index((w_, li)) if (w_, li) in words else 0
            words[i] = (None, -1)
            rev = clamp((t - t0 - dur*i/n)/0.12)
            ww = ctx.text_extents(w_)[4]
            ctx.save(); sc = 0.85 + 0.15*back(rev) if rev < 1 else 1.0
            ctx.translate(x + ww/2, yy - size*0.35); ctx.scale(sc, sc); ctx.translate(-(x + ww/2), -(yy - size*0.35))
            otext(ctx, w_, x, yy, size, '#ffffff' if li == 0 else col, lw=14, align='l', alpha=0.2 + 0.8*rev)
            ctx.restore(); x += ww + sp
            ctx.select_font_face('Poppins ExtraBold', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)

def badge(ctx, x, y, label, p, col='#2fa86a'):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc); ctx.rotate(-0.04)
    w = text_w(ctx, label, 64) + 90
    rrect(ctx, -w/2, -52 + 8, w, 104, 52); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.fill()
    rrect(ctx, -w/2, -52, w, 104, 52); ctx.set_source(grad(-52, 52, col, '#145a38' if col == '#2fa86a' else '#8a1a1a')); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(6); rrect(ctx, -w/2 + 8, -44, w - 16, 88, 44); ctx.stroke()
    text(ctx, label, 0, 22, 64, '#ffffff'); ctx.restore()

def cd_remaining(t, cd0):
    return clamp(CD_LEN - (t - cd0), 0, CD_LEN)

def countdown(ctx, x, y, r, t, cd0, alpha=1.0, label=None):
    rem = cd_remaining(t, cd0); frac = rem/CD_LEN
    col = '#2fd27a' if rem > 20 else ('#ffb52a' if rem > 10 else '#ff4a3c')
    pulse = 1 + 0.04*max(0, math.cos((t - cd0)*2*math.pi)) if 0 < rem < CD_LEN else 1
    ctx.save(); ctx.translate(x, y); ctx.scale(pulse, pulse)
    g = cairo.RadialGradient(0, 0, r*0.4, 0, 0, r*1.35); g.add_color_stop_rgba(0, *hexc(col, 0.35*alpha)); g.add_color_stop_rgba(1, *hexc(col, 0))
    ctx.set_source(g); ctx.arc(0, 0, r*1.35, 0, 2*math.pi); ctx.fill()
    ctx.arc(0, 0, r, 0, 2*math.pi); ctx.set_source_rgba(0.08, 0.08, 0.2, 0.85*alpha); ctx.fill()
    ctx.set_line_width(r*0.16); ctx.set_source_rgba(1, 1, 1, 0.15*alpha); ctx.arc(0, 0, r*0.86, 0, 2*math.pi); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc(col, alpha))
    if frac > 0.001: ctx.arc(-math.pi/2, 0, 0, 0, 0); ctx.new_path(); ctx.arc(0, 0, r*0.86, -math.pi/2, -math.pi/2 + 2*math.pi*frac); ctx.stroke()
    n = int(math.ceil(rem)) if rem > 0 else 0
    text(ctx, str(n), 0, r*0.3, r*0.85, '#ffffff', alpha=alpha)
    if label: text(ctx, label, 0, r*0.62, r*0.17, '#ffffff', alpha=0.8*alpha)
    ctx.restore()

def brain(ctx, x, y, s, t, glow=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    g = cairo.RadialGradient(0, 0, 20, 0, 0, 220); g.add_color_stop_rgba(0, 1, 0.5, 0.8, 0.6*glow); g.add_color_stop_rgba(1, 1, 0.5, 0.8, 0)
    ctx.set_source(g); ctx.arc(0, 0, 220, 0, 2*math.pi); ctx.fill()
    for (dx, dy, r) in ((-60, -10, 68), (0, -42, 74), (60, -10, 68), (-36, 34, 62), (36, 34, 62)):
        ctx.new_sub_path(); ctx.arc(dx, dy, r, 0, 2*math.pi)
    g = cairo.RadialGradient(-30, -50, 10, 0, 0, 140); g.add_color_stop_rgba(0, *hexc('#ffc2dc')); g.add_color_stop_rgba(1, *hexc('#ff5fa0'))
    ctx.set_source(g); ctx.fill()
    ctx.set_source_rgba(*hexc('#d0407e')); ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0, -112); ctx.curve_to(-18, -40, 18, 20, 0, 92); ctx.stroke()
    for (a, b, c_, d) in ((-90, -30, -50, 10), (60, -40, 90, 0), (-70, 40, -30, 60), (40, 50, 70, 30)):
        ctx.move_to(a, b); ctx.curve_to((a + c_)/2, b - 20, (a + c_)/2, d + 20, c_, d); ctx.stroke()
    ctx.restore()

def signal(ctx, pts, t, p=1.0, speed=1.6):
    """glowing yellow line along pts with travelling pulses"""
    if p <= 0: return
    L = [0]
    for i in range(1, len(pts)): L.append(L[-1] + math.hypot(pts[i][0] - pts[i-1][0], pts[i][1] - pts[i-1][1]))
    tot = L[-1]
    def at(d):
        for i in range(1, len(pts)):
            if d <= L[i]:
                q = (d - L[i-1])/max(1e-6, L[i] - L[i-1]); return lerp(pts[i-1][0], pts[i][0], q), lerp(pts[i-1][1], pts[i][1], q)
        return pts[-1]
    upto = tot*p
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for w, a in ((34, 0.18), (18, 0.35), (8, 1.0)):
        ctx.set_line_width(w); ctx.set_source_rgba(1, 0.86, 0.2, a)
        ctx.move_to(*pts[0]); d = 0
        while d < upto: d = min(upto, d + 12); ctx.line_to(*at(d))
        ctx.stroke()
    for k in range(5):
        d = ((t*speed*0.25 + k/5) % 1)*tot
        if d > upto: continue
        x, y = at(d); g = cairo.RadialGradient(x, y, 1, x, y, 30); g.add_color_stop_rgba(0, 1, 1, 0.8, 1); g.add_color_stop_rgba(1, 1, 0.9, 0.3, 0)
        ctx.set_source(g); ctx.arc(x, y, 30, 0, 2*math.pi); ctx.fill()

def tag(ctx, x, y, s, p, col='#ffffff', bg='#1b1440', size=40):
    if p <= 0: return
    w = text_w(ctx, s, size) + 44
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    rrect(ctx, -w/2, -size*0.85, w, size*1.6, 16); ctx.set_source_rgba(*hexc(bg, 0.88)); ctx.fill()
    ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(4); rrect(ctx, -w/2, -size*0.85, w, size*1.6, 16); ctx.stroke()
    text(ctx, s, 0, size*0.35, size, col); ctx.restore()

def check(ctx, x, y, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    ctx.arc(0, 0, 90, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#2fc76a')); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(22); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(-42, 2); ctx.line_to(-12, 34); ctx.line_to(46, -30); ctx.stroke(); ctx.restore()

def push_arrows(ctx, x, y, t, p=1.0):
    if p <= 0: return
    for k, dy in enumerate((-60, 0, 60)):
        off = 18*math.sin(t*14 + k)
        ctx.save(); ctx.translate(x + 30 + off, y + dy)
        ctx.set_source_rgba(*hexc('#ff3b30', p)); ctx.move_to(0, -16); ctx.line_to(70, -16); ctx.line_to(70, -36); ctx.line_to(115, 0)
        ctx.line_to(70, 36); ctx.line_to(70, 16); ctx.line_to(0, 16); ctx.close_path(); ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, p); ctx.set_line_width(5); ctx.stroke(); ctx.restore()

def sparkles(ctx, t, n=14, seed=4, ymin=450, ymax=1300, col=(1, 0.95, 0.6)):
    rnd = random.Random(seed)
    for k in range(n):
        x = rnd.uniform(60, W - 60); y = rnd.uniform(ymin, ymax); ph = rnd.uniform(0, 6); r = rnd.uniform(8, 20)
        a = 0.5 + 0.5*math.sin(t*3 + ph); ctx.save(); ctx.translate(x, y + 10*math.sin(t + ph)); ctx.rotate(t + ph)
        ctx.move_to(0, -r*2); ctx.line_to(r*0.4, -r*0.4); ctx.line_to(r*2, 0); ctx.line_to(r*0.4, r*0.4); ctx.line_to(0, r*2)
        ctx.line_to(-r*0.4, r*0.4); ctx.line_to(-r*2, 0); ctx.line_to(-r*0.4, -r*0.4); ctx.close_path()
        ctx.set_source_rgba(*col, a*0.8); ctx.fill(); ctx.restore()

def comment_box(ctx, y, s, t, t0):
    rrect(ctx, 80, y + 10, 920, 250, 30); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.fill()
    rrect(ctx, 70, y, 940, 250, 30); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.arc(150, y + 75, 40, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#ffb52a')); ctx.fill()
    text(ctx, 'Add a comment...', 215, y + 90, 38, '#9a9a9a', align='l')
    n = int(clamp((t - t0 - 0.3)/1.2)*len(s)); word = s[:n]
    text(ctx, word, 215, y + 190, 64, '#2b2622', align='l')
    if (t*2) % 1 < 0.6: ctx.rectangle(215 + text_w(ctx, word, 64) + 8 if word else 215, y + 135, 7, 70); ctx.set_source_rgba(*hexc('#ff4a3c')); ctx.fill()

def follow_btn(ctx, x, y, t, following=False):
    pp = 1 + 0.07*math.sin(t*8)
    ctx.save(); ctx.translate(x, y); ctx.scale(pp, pp); rrect(ctx, -260, -66, 520, 132, 66)
    ctx.set_source_rgba(*hexc('#e62117' if not following else '#555555')); ctx.fill()
    text(ctx, '+ FOLLOW' if not following else 'FOLLOWING', 0, 22, 60, '#ffffff'); ctx.restore()

def hand_tap(ctx, x, y, t, t0):
    p = prog(t, t0, 0.5); q = prog(t, t0 + 0.5, 0.2)
    if p <= 0: return
    yy = lerp(y + 260, y + 40, smooth(p)) + 20*q
    ctx.save(); ctx.translate(x + 120, yy)
    ctx.arc(0, 0, 46, 0, 2*math.pi); ctx.set_source_rgba(*hexc(SKIN)); ctx.fill()
    rrect(ctx, -22, -110, 44, 120, 22); ctx.fill()
    ctx.restore()

# ------------------------------------------------------------------ beats
# at = start time relative to the countdown start (cd0); cd = beat that starts the countdown at its end
COL_O, COL_G, COL_B, COL_R, COL_Y = '#ff9a2a', '#3fe08a', '#4fb4ff', '#ff4a4a', '#ffd23f'
BEATS = [
 dict(id='h1', sc='hook', ml='നിങ്ങളുടെ കൈ തനിയെ പൊങ്ങും! എന്റെ കൂടെ ചെയ്തു നോക്കൂ!', l1='Your arm will', l2='FLOAT – try it with me!', col=COL_O),
 dict(id='s1', sc='door', ml='സ്റ്റെപ്പ് ഒന്ന്. ഒരു വാതിലിന്റെ നടുവിൽ, കൈ നേരെ താഴ്ത്തി നിൽക്കൂ.', l1='STEP 1: stand in a', l2='DOORWAY, arm down', col=COL_G, badge='STEP 1'),
 dict(id='s2', sc='door2', ml='കൈയുടെ പുറംഭാഗം, വാതിലിന്റെ ഫ്രെയിമിൽ ചേർത്തു വെക്കൂ.', l1='Put the BACK of your hand', l2='on the door frame', col=COL_O),
 dict(id='s3', sc='hand', ml='സ്റ്റെപ്പ് രണ്ട്. ഇനി കൈ കൊണ്ട്, ഫ്രെയിമിൽ പുറത്തേക്ക് ശക്തിയായി തള്ളൂ!', l1='STEP 2: push OUT', l2='as HARD as you can!', col=COL_R, badge='STEP 2'),
 dict(id='s4', sc='bigcd', ml='മുപ്പത് സെക്കൻഡ് നിർത്താതെ തള്ളണം. റെഡി? തുടങ്ങാം!', l1='Keep pushing for', l2='30 SECONDS – GO!', col=COL_G, cd=True),
 dict(id='c1', sc='hand', at=0.3, ml='തള്ളിക്കൊണ്ടേയിരിക്കൂ! ഇപ്പോൾ ഉള്ളിൽ എന്താണ് നടക്കുന്നത് എന്നറിയാമോ?', l1='Keep pushing!', l2="What's happening inside?", col=COL_O),
 dict(id='c2', sc='xray', ml='നിങ്ങളുടെ തലച്ചോറ്, തോളിലെ പേശിയിലേക്ക്, പൊക്കൂ, പൊക്കൂ, എന്ന സിഗ്നൽ അയച്ചുകൊണ്ടേയിരിക്കുന്നു.', l1='Your brain keeps sending', l2='LIFT! LIFT! to the shoulder', col=COL_Y),
 dict(id='c3', sc='bigcd', at=10.0, ml='ഇരുപത് സെക്കൻഡ് കൂടി. നിർത്തരുത്!', l1='20 seconds left –', l2="DON'T STOP!", col=COL_O),
 dict(id='c4', sc='xray', ml='പേശി കഠിനമായി പണിയെടുക്കുന്നു. തലച്ചോർ ആ ഓർഡർ ഓർത്തു വെക്കുകയാണ്.', l1='The muscle works hard,', l2='the brain REMEMBERS it', col=COL_B, x100=True),
 dict(id='c5', sc='hand', at=20.0, ml='പത്തു സെക്കൻഡ് കൂടി! അവസാനം വരെ ശക്തിയായി തള്ളൂ!', l1='10 more seconds –', l2='PUSH HARDER!', col=COL_R),
 dict(id='c6', sc='bigcd', at=25.0, ml='അഞ്ച്, നാല്, മൂന്ന്, രണ്ട്, ഒന്ന്!', l1='Almost there...', l2='5, 4, 3, 2, 1!', col=COL_Y),
 dict(id='r1', sc='release', at=30.0, ml='ഇനി വാതിലിൽ നിന്ന് മാറി നിൽക്കൂ. കൈ അയച്ചിടൂ, ഒന്നും ചെയ്യരുത്.', l1='Now step away and', l2='let your arm HANG', col=COL_G),
 dict(id='r2', sc='float', ml='നോക്കൂ! നിങ്ങളുടെ കൈ, തനിയെ മുകളിലേക്ക് പൊങ്ങുന്നു!', l1='Look! Your arm is', l2='FLOATING UP by itself!', col=COL_G),
 dict(id='n1', sc='name', ml='ഇതിന്റെ പേരാണ്, കോൺസ്റ്റാം എഫക്ട്.', l1='This is called the', l2='KOHNSTAMM EFFECT', col=COL_Y),
 dict(id='n2', sc='xray2', ml='നിങ്ങൾ നിർത്തിയിട്ടും, തലച്ചോർ പൊക്കാനുള്ള സിഗ്നൽ അയച്ചുകൊണ്ടേയിരിക്കുന്നു!', l1='You stopped, but your brain', l2='keeps sending LIFT!', col=COL_Y),
 dict(id='e1', sc='end1', ml='നിങ്ങളുടെ കൈ പൊങ്ങിയോ? കമന്റിൽ പറയൂ!', l1='Did yours float?', l2='Tell me in the comments!', col=COL_G),
 dict(id='e2', sc='share', ml='ഇത് ഒരു കൂട്ടുകാരന് അയച്ചു കൊടുക്കൂ, അവരും ഞെട്ടും!', l1='Send this to a friend', l2='and watch them FREAK OUT!', col=COL_O),
 dict(id='e3', sc='follow', ml='കൂടുതൽ രഹസ്യങ്ങൾക്ക്, ഫോളോ ചെയ്യൂ!', l1='Follow for more', l2='MYSTERIES!', col=COL_Y, post=1.4),
]

class TL:
    def __init__(self, beats, lead=0.15, gap=0.1):
        self.beats = beats; self.by = {}; t = lead; self.cd0 = None
        for b in beats:
            b['wav'] = voice(b['ml'], VOICE); b['d'] = wav_dur(b['wav'])
            if 'at' in b and self.cd0 is not None: t = max(t, self.cd0 + b['at'])
            b['t0'] = t; b['t1'] = t + b['d']; t = b['t1'] + gap + b.get('post', 0)
            if b.get('cd'): self.cd0 = b['t1'] + 0.25; t = max(t, self.cd0)
            self.by[b['id']] = b
        self.end = t

def room_kid_state(b, t, tl):
    """kid position/arm per scene"""
    t0, t1 = b['t0'], b['t1']; sc = b['sc']; cd0 = tl.cd0
    if sc == 'door':
        p = sprog(t, t0, 1.2); return dict(x=lerp(-200, 540, p), y=FEET, s=1.0, aR=0.0, mood='smile', walk=p < 1)
    if sc in ('door2',):
        return dict(x=540, y=FEET, s=1.0, aR=lerp(0.0, 0.145, sprog(t, t0 + 0.4, 0.8)), mood='smile')
    if sc in ('hand', 'bigcd', 'xray'):
        pushing = cd0 is None or t < cd0 + CD_LEN + 0.1
        return dict(x=540, y=FEET, s=1.0, aR=0.145, mood='effort' if (b['id'] != 's4' or t > t1 - 0.6) else 'smile', push=1.0 if pushing else 0)
    if sc == 'release':
        p = sprog(t, t0 + 0.3, 1.2); return dict(x=lerp(540, 470, p), y=lerp(FEET, FEET + 40, p), s=lerp(1.0, 1.08, p), aR=lerp(0.145, 0.03, p), mood='smile', walk=p < 1)
    if sc == 'float':
        p = sprog(t, t0 + 0.2, 3.0); return dict(x=470, y=FEET + 40, s=1.08, aR=lerp(0.03, 1.05, p) + 0.03*math.sin(t*3)*p, mood='wow')
    return dict(x=540, y=FEET, s=1.0, aR=1.05 + 0.03*math.sin(t*3), mood='smile')

def draw_kid(ctx, st, t, talk=0.0, glow=0.0):
    yb = -abs(math.sin(t*10))*14 if st.get('walk') else 0
    return kid(ctx, st['x'], st['y'] + yb, st['s'], t, aR=st['aR'], mood=st['mood'], talk=talk, glowR=glow, push=st.get('push', 0))

def draw_factory(tl):
    cd0 = tl.cd0
    def draw(ctx, t):
        i = 0
        for j, b in enumerate(tl.beats):
            if t >= b['t0'] - 0.12: i = j
        b = tl.beats[i]; t0, t1 = b['t0'], b['t1']; sc = b['sc']
        z = 1.0 + 0.07*(1 - sprog(t, t0 - 0.12, 0.35)) + 0.025*prog(t, t0, max(1, t1 - t0 + 0.5))
        ctx.save(); ctx.translate(W/2, H*0.45); ctx.scale(z, z); ctx.translate(-W/2, -H*0.45)
        st = room_kid_state(b, t, tl)
        talk = 0.0
        if sc == 'hook':
            ctx.set_source_surface(room()); ctx.paint(); vignette(ctx, 0.35)
            st = dict(x=540, y=FEET, s=1.0, aR=0.55 + 0.45*math.sin(t*1.8), mood='wow')
            draw_kid(ctx, st, t)
            sparkles(ctx, t, ymin=480, ymax=1250)
            for k, (qx, qy) in enumerate(((150, 520), (930, 560))):
                otext(ctx, '?', qx, qy + 14*math.sin(t*4 + k), 150, '#ffd23f', alpha=prog(t, t0 + 0.3 + k*0.15, 0.2))
        elif sc == 'intro':
            ctx.set_source_surface(room()); ctx.paint(); vignette(ctx, 0.35)
            draw_kid(ctx, dict(x=430, y=FEET, s=0.95, aR=0.0, mood='smile'), t, talk=abs(math.sin(t*12))*0.4)
            p = back(prog(t, t0 + 0.4, 0.4))
            if p > 0:
                brain(ctx, 820, 700 + 12*math.sin(t*3), 0.85*p, t)
                tag(ctx, 820, 900, 'BRAIN TRICK', prog(t, t0 + 1.0, 0.3), col='#ffd23f')
            otext(ctx, 'MAGIC?', 230, 560, 70, '#ffffff', alpha=prog(t, t0 + 0.1, 0.2))
            if t > t0 + 0.9:
                ctx.set_source_rgba(*hexc('#ff3b30')); ctx.set_line_width(14); ctx.move_to(80, 590); ctx.line_to(380, 520); ctx.stroke()
        elif sc in ('door', 'door2', 'release', 'float', 'end1', 'share'):
            ctx.set_source_surface(room()); ctx.paint(); vignette(ctx, 0.3)
            hR, _ = draw_kid(ctx, st, t)
            if sc == 'door': badge(ctx, 540, 470, 'STEP 1', prog(t, t0 + 0.2, 0.35))
            if sc == 'door2':
                p = prog(t, t0 + 1.1, 0.3)
                if p > 0:
                    ctx.set_source_rgba(1, 0.85, 0.2, p); ctx.set_line_width(10); ctx.arc(hR[0], hR[1], 70 + 6*math.sin(t*8), 0, 2*math.pi); ctx.stroke()
                    tag(ctx, hR[0] - 40, hR[1] + 130, 'BACK OF HAND', p, col='#ffd23f')
            if sc == 'float':
                p = prog(t, t0 + 0.2, 3.0)
                ctx.save(); ctx.set_source_rgba(1, 1, 1, 0.7); ctx.set_line_width(8); ctx.set_dash([18, 18], -t*60)
                ctx.new_path(); ctx.arc_negative(470 + 118*1.08, FEET + 40 - 540*1.08, 295*1.08, math.pi/2 - 0.03, math.pi/2 - 1.08); ctx.stroke(); ctx.restore()
                check(ctx, 860, 640, prog(t, t0 + 2.4, 0.35))
                sparkles(ctx, t, n=10, ymin=600, ymax=1100)
            if sc == 'end1':
                comment_box(ctx, 480, 'IT FLOATED!', t, t0)
            if sc == 'share':
                for k, x in enumerate((210, 870)): otext(ctx, 'HA', x, 620 + 10*math.sin(t*6 + k), 90, '#ffd23f', alpha=prog(t, t0 + 0.3 + 0.2*k, 0.2))
                tag(ctx, 540, 500, 'SEND TO A FRIEND', prog(t, t0 + 0.2, 0.3), col='#ffffff', bg='#ff7a2a', size=50)
        elif sc == 'hand':
            # close-up on the pushing hand
            hx, hy = 540 + 118 + 295*math.sin(0.145), FEET - 540 + 295*math.cos(0.145)
            ctx.save(); zc = 2.1; ctx.translate(W/2 - 60, 900); ctx.scale(zc, zc); ctx.translate(-hx, -hy)
            ctx.set_source_surface(blur_room() if b['id'] != 's3' else room()); ctx.paint()
            ctx.rectangle(DOOR_R, 440, 40, FEET); ctx.set_source(grad(0, 0, '#a8744a', '#7a4e2e', DOOR_R, DOOR_R + 40)); ctx.fill()
            draw_kid(ctx, st, t)
            ctx.restore()
            push_arrows(ctx, W/2 + 30, 900, t, prog(t, t0 + 0.3, 0.3))
            if b.get('badge'): badge(ctx, 540, 470, b['badge'], prog(t, t0 + 0.2, 0.35), col='#e2362c')
            else: pill(ctx, 540, 1250, 520, 100, '#e2362c', 'PUSH OUT!', size=54, p=prog(t, t0 + 0.2, 0.3))
        elif sc == 'bigcd':
            ctx.set_source_surface(blur_room()); ctx.paint(); ctx.set_source_rgba(0.05, 0.04, 0.15, 0.35); ctx.paint()
            draw_kid(ctx, dict(x=540, y=1640, s=0.55, aR=0.145, mood='effort', push=1.0), t)
            a = back(prog(t, t0 + 0.2, 0.4)) if b['id'] == 's4' else 1.0
            countdown(ctx, 540, 820, 260 * max(0.01, a), t, cd0 if t >= cd0 else t, label='SECONDS')
        elif sc in ('xray', 'xray2'):
            ctx.set_source_rgba(*hexc('#0d1030')); ctx.paint()
            g = cairo.RadialGradient(540, 800, 50, 540, 800, 1000); g.add_color_stop_rgba(0, 0.2, 0.2, 0.5, 1); g.add_color_stop_rgba(1, 0.05, 0.05, 0.15, 1)
            ctx.set_source(g); ctx.paint()
            for k in range(0, W, 60): ctx.rectangle(k, 0, 2, H); ctx.set_source_rgba(0.4, 0.6, 1, 0.06); ctx.fill()
            for k in range(0, H, 60): ctx.rectangle(0, k, W, 2); ctx.set_source_rgba(0.4, 0.6, 1, 0.06); ctx.fill()
            ks = 1.0; kx, ky = 470, FEET
            if sc == 'xray2':
                aR = lerp(0.03, 1.0, sprog(t, t0 + 0.6, 3.2))
            else: aR = 0.145
            ctx.push_group()
            kid(ctx, kx, ky, ks, t, aR=aR, mood='smile' if sc == 'xray2' else 'effort', glowR=0, bob=False)
            pat = ctx.pop_group()
            ctx.set_source(pat); ctx.paint_with_alpha(0.45)
            ctx.set_source_rgba(0.3, 0.6, 1, 0.25); ctx.mask(pat)
            if sc == 'xray':
                ctx.save(); ctx.translate(kx + 118 + 295*math.sin(0.145) + 40, ky - 540 + 295*math.cos(0.145)); ctx.restore()
                ctx.rectangle(DOOR_R - 70, 450, 40, FEET - 450); ctx.set_source_rgba(0.6, 0.45, 0.3, 0.6); ctx.fill()
            brain(ctx, kx, ky - 830, 0.62, t)
            sx, sy = kx + 118*ks, ky - 540*ks
            pts = [(kx, ky - 760), (kx, ky - 600), (kx + 40, ky - 570), (sx + 10, sy + 20)]
            signal(ctx, pts, t, sprog(t, t0 + 0.3, 0.9), speed=3.0 if sc == 'xray' else 2.0)
            mg = 0.6 + 0.4*math.sin(t*10)
            g = cairo.RadialGradient(sx + 20, sy + 40, 5, sx + 20, sy + 40, 120); g.add_color_stop_rgba(0, 1, 0.4, 0.2, 0.9*mg); g.add_color_stop_rgba(1, 1, 0.3, 0.2, 0)
            ctx.set_source(g); ctx.arc(sx + 20, sy + 40, 120, 0, 2*math.pi); ctx.fill()
            tag(ctx, 830, 560, 'BRAIN', prog(t, t0 + 0.2, 0.3), col='#ff8fc4')
            tag(ctx, 800, 1060, 'SHOULDER MUSCLE', prog(t, t0 + 0.8, 0.3), col='#ffb52a', size=36)
            ctx.set_source_rgba(1, 1, 1, 0.5*prog(t, t0 + 0.8, 0.3)); ctx.set_line_width(4); ctx.move_to(800, 1030); ctx.line_to(sx + 40, sy + 40); ctx.stroke()
            if sc == 'xray':
                n = int(clamp((t - t0)/max(0.5, t1 - t0))*100) if b.get('x100') else None
                tag(ctx, 830, 760, 'LIFT!' if n is None else f'LIFT! x{max(1, n)}', prog(t, t0 + 0.5, 0.3), col='#ffd23f', size=52)
            else:
                tag(ctx, 800, 760, 'STOPPED PUSHING', prog(t, t0 + 0.2, 0.3), col='#ffffff', bg='#3a3a5a', size=38)
                tag(ctx, 800, 870, 'STILL SENDING: LIFT!', prog(t, t0 + 1.6, 0.3), col='#ffd23f', size=38)
            if cd0 is not None and cd0 <= t <= cd0 + CD_LEN + 0.2:
                countdown(ctx, 140, 520, 85, t, cd0)
        elif sc == 'name':
            ctx.set_source_rgba(*hexc('#12103a')); ctx.paint()
            ctx.save(); ctx.translate(540, 900); ctx.rotate(t*0.2)
            for k in range(16):
                ctx.move_to(0, 0); ctx.arc(0, 0, 1600, k*2*math.pi/16, (k + 0.5)*2*math.pi/16); ctx.close_path(); ctx.set_source_rgba(0.35, 0.3, 0.9, 0.18); ctx.fill()
            ctx.restore()
            brain(ctx, 540, 690 + 10*math.sin(t*3), 0.95*back(prog(t, t0, 0.4)), t)
            p = back(prog(t, t0 + 0.6, 0.4))
            if p > 0:
                ctx.save(); ctx.translate(540, 1000); ctx.scale(p, p)
                otext(ctx, 'KOHNSTAMM', 0, 0, 128, '#ffd23f', lw=18)
                otext(ctx, 'EFFECT', 0, 140, 128, '#ffffff', lw=18)
                ctx.restore()
            tag(ctx, 540, 1250, 'a real effect studied by scientists', prog(t, t0 + 1.4, 0.3), col='#ffffff', bg='#2a2a6a', size=38)
            sparkles(ctx, t, n=16, ymin=450, ymax=1350)
        elif sc == 'follow':
            ctx.set_source(grad(0, H, '#1a1440', '#3a1a5a')); ctx.paint()
            sparkles(ctx, t, n=18, ymin=420, ymax=1400, col=(0.9, 0.8, 1))
            brain(ctx, 540, 640 + 10*math.sin(t*3), 0.9, t)
            follow_btn(ctx, 540, 960, t, following=(t - t0) > 2.4)
            hand_tap(ctx, 540, 960, t, t0 + 1.8)
            otext(ctx, 'NEW TRICKS EVERY DAY', 540, 1180, 56, '#ffd23f', alpha=prog(t, t0 + 0.5, 0.3))
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and i: ctx.set_source_rgba(1, 1, 1, 0.22*fl); ctx.paint()
        # top gradient so captions read on any scene
        g = cairo.LinearGradient(0, 0, 0, 420); g.add_color_stop_rgba(0, 0, 0, 0, 0.45); g.add_color_stop_rgba(1, 0, 0, 0, 0)
        ctx.set_source(g); ctx.rectangle(0, 0, W, 420); ctx.fill()
        caption2(ctx, b['l1'], b['l2'], b['col'], t, t0, t1)
        # small countdown during pushing scenes that are not big countdowns
        if cd0 is not None and sc in ('hand',) and cd0 <= t <= cd0 + CD_LEN + 0.2:
            countdown(ctx, 930, 520, 85, t, cd0)
    return draw

def ambient_bed(dur):
    n = int(dur*SR); y = np.zeros(n)
    chords = [(57, 60, 64, 67), (53, 57, 60, 64), (55, 59, 62, 67), (52, 55, 59, 64)]
    seg = 4.0; k = 0
    while k*seg < dur:
        fs = [A.mtof(m) for m in chords[k % 4]]
        p = A.pad(fs, seg + 1.5)*0.5; A.add(y, p, int(k*seg*SR)); k += 1
    rng = np.random.default_rng(7); notes = [69, 72, 76, 79, 81, 76, 72, 74]
    for j in range(int(dur/0.9)):
        if rng.random() < 0.55: A.add(y, A.bell(A.mtof(notes[j % len(notes)]), 1.6, 3)*0.12, int(j*0.9*SR))
    return A.lp(y, 3500)

def build_mix(path, tl, sfx, total):
    n = int((total + 1)*SR); v = np.zeros(n); fx = np.zeros(n)
    for b in tl.beats:
        y, sr = sf.read(b['wav']); y = y if y.ndim == 1 else y.mean(1); A.add(v, y, int(b['t0']*SR))
    for (t, kind, g) in sfx:
        s_ = sfx2(kind)*g
        if kind == 'tick': s_ = s_[:int(0.05*SR)]
        A.add(fx, s_, int(t*SR))
    bed = ambient_bed(total + 1); bed = bed/np.abs(bed).max()
    env = np.convolve(np.abs(v), np.ones(int(0.2*SR))/int(0.2*SR), mode='same'); duck = 1 - 0.5*np.clip(env/0.05, 0, 1)
    mix = (v*1.0 + bed[:n]*0.22*duck + fx*0.6)[:int(total*SR)]
    tmp = path + '.tmp.wav'; sf.write(tmp, mix.astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '44100', path], check=True); os.remove(tmp)

def sfx_list(tl):
    sfx = []; cd0 = tl.cd0
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0'] - 0.12, 'whoosh', 0.5))
        if b['id'] == 'h1': sfx.append((b['t0'] + 0.3, 'pop', 0.7))
        if b.get('badge'): sfx.append((b['t0'] + 0.2, 'pop', 0.7))
        if b['sc'] in ('xray', 'name', 'intro'): sfx.append((b['t0'] + 0.5, 'pop', 0.5))
        if b['sc'] == 'float': sfx.append((b['t0'] + 2.4, 'right', 0.6))
        if b['sc'] == 'end1':
            for k in range(8): sfx.append((b['t0'] + 0.35 + k*0.15, 'tick', 0.25))
        if b['sc'] == 'follow': sfx.append((b['t0'] + 2.4, 'pop', 0.6))
    for k in range(int(CD_LEN)):
        sfx.append((cd0 + k, 'tick', 0.22 if k < 25 else 0.45))
    sfx.append((cd0 + CD_LEN, 'right', 0.5))
    return sfx

if __name__ == '__main__':
    tl = TL(BEATS)
    total = tl.end + 0.4
    draw = draw_factory(tl)
    print('TOTAL', round(total, 1), 'cd0', round(tl.cd0, 1))
    for b in tl.beats: print(b['id'], round(b['t0'], 1), round(b['t1'], 1))
    if 'stills' in sys.argv:
        k = 0
        for b in tl.beats:
            for tt in (b['t0'] + 0.9, b['t1'] - 0.05):
                surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt)
                surf.write_to_png(f'{OUT}/s{k:02d}.png'); k += 1
    elif 'audio' in sys.argv:
        pass
    else:
        aud = f'{OUT}/{NAME}.wav'; build_mix(aud, tl, sfx_list(tl), total)
        wd.render_raw(f'{OUT}/{NAME}.mp4', total, draw, aud)
