"""Kandupidi recurring + guest characters (pycairo, shaded 2D, realistic proportions).
DETECTIVE ARJUN and MEENU must look IDENTICAL in every episode: always use ARJUN / MEENU specs from here.
human(ctx, x, y, s, spec, pose, t): feet at (x, y); s = scale (1.0 -> a 6 ft man is ~900 px tall).
pose: dict(face=+1/-1, expr='neutral|smile|shock|scared|smug|think|sad|angry|laugh', talk=0..1,
           arm_l=mode, arm_r=mode (screen-left / screen-right arm), lean=rad, blink=True, look=(dx,dy))
arm modes: down, hip, point, chin, notebook, write, chips, eat, up, cuffed, give, torch, mop, wave, hold
"""
import math, cairo

def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
def mix(c, d, k):
    a, b = hexc(c), hexc(d); return '#%02x%02x%02x' % tuple(int(255*(a[i]*(1-k)+b[i]*k)) for i in range(3))
def lt(c, k=0.18): return mix(c, '#ffffff', k)
def dk(c, k=0.25): return mix(c, '#000000', k)

def shade(ctx, col, x0, x1, light=0.16, dark=0.28):
    g = cairo.LinearGradient(x0, 0, x1, 0)
    g.add_color_stop_rgba(0, *hexc(lt(col, light))); g.add_color_stop_rgba(0.45, *hexc(col)); g.add_color_stop_rgba(1, *hexc(dk(col, dark)))
    ctx.set_source(g)

def vshade(ctx, col, y0, y1, light=0.12, dark=0.25):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *hexc(lt(col, light))); g.add_color_stop_rgba(1, *hexc(dk(col, dark))); ctx.set_source(g)

def outline(ctx, w=3.0, a=0.55):
    ctx.set_source_rgba(0.08, 0.05, 0.05, a); ctx.set_line_width(w); ctx.stroke()

def ellipse(ctx, x, y, rx, ry):
    ctx.save(); ctx.translate(x, y); ctx.scale(rx, ry); ctx.arc(0, 0, 1, 0, 2*math.pi); ctx.restore()

def rrect(ctx, x, y, w, h, r):
    r = min(r, w/2, h/2)
    ctx.new_sub_path(); ctx.arc(x+w-r, y+r, r, -math.pi/2, 0); ctx.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    ctx.arc(x+r, y+h-r, r, math.pi/2, math.pi); ctx.arc(x+r, y+r, r, math.pi, 1.5*math.pi); ctx.close_path()

# ------------------------------------------------------------------ specs
ARJUN = dict(name='ARJUN', h=1.0, sex='m', skin='#c98a5e', hair='#15110e', hairstyle='short', stache='neat', beard=None,
             top='trench', top_col='#8a8450', shirt='#f4f2ea', bottom='trousers', bot_col='#2a2a30', shoe='leather_brown',
             hat='flatcap', hat_col='#6b4a2e', glasses=None, build=1.0)
MEENU = dict(name='MEENU', h=0.86, sex='f', skin='#d49a6a', hair='#120e0c', hairstyle='side_ponytail', stache=None, beard=None,
             top='kurta', top_col='#16867f', shirt='#ffffff', bottom='churidar', bot_col='#f3efe6', shoe='flat_tan',
             hat=None, glasses='round', build=0.9, dupatta='#ffffff', bag='#d8a12a')
RAVI = dict(name='DR. RAVI MENON', h=1.03, sex='m', skin='#c58b62', hair='#2a2622', hairstyle='combed_grey', stache=None, beard=None,
            top='blazer', top_col='#6a4a32', shirt='#e8dcc0', tie='#7a1f2a', bottom='trousers', bot_col='#3a3a42', shoe='leather_black',
            hat=None, glasses=None, build=1.0)
VELU = dict(name='VELAYUDHAN', h=0.90, sex='m', skin='#a8704a', hair='#9a9590', hairstyle='receding', stache='thick_grey', beard=None,
            top='uniform', top_col='#b39a62', shirt='#b39a62', bottom='trousers', bot_col='#a88f58', shoe='chappal_blue',
            hat=None, glasses=None, build=1.05)
SHANTHA = dict(name='SHANTHA', h=0.83, sex='f', skin='#b5784e', hair='#1a1410', hairstyle='bun', stache=None, beard=None,
               top='saree', top_col='#2f8a4a', shirt='#c8a23a', bottom='saree', bot_col='#2f8a4a', border='#e0b23a', shoe='flat_sandal',
               hat=None, glasses=None, build=0.95)
FAIZAL = dict(name='FAIZAL', h=0.94, sex='m', skin='#bf8458', hair='#1a1310', hairstyle='curly', stache='light', beard='short',
              top='work', top_col='#2c4a7a', shirt='#2c4a7a', bottom='trousers', bot_col='#25406a', shoe='boots_yellow',
              hat=None, glasses=None, build=1.0, toolbelt=True)
POLICE = dict(name='POLICE', h=0.97, sex='m', skin='#b07a50', hair='#15110e', hairstyle='short', stache='neat', beard=None,
              top='uniform', top_col='#c2a46a', shirt='#c2a46a', bottom='trousers', bot_col='#b69860', shoe='leather_black',
              hat='police', hat_col='#c2a46a', glasses=None, build=1.05)

RAJU = dict(name='RAJU', h=0.95, sex='m', skin='#a86e46', hair='#15110e', hairstyle='short', stache='thick_grey', beard=None,
            top='work', top_col='#c8502e', shirt='#c8502e', bottom='mundu', bot_col='#f4f1e8', border='#d8a83a', shoe='chappal_blue',
            hat=None, glasses=None, build=1.05)
KUTTAN = dict(name='KUTTAN', h=0.92, sex='m', skin='#8e5a36', hair='#9a9590', hairstyle='receding', stache='thick_grey', beard=None,
              top='work', top_col='#3a6a8a', shirt='#3a6a8a', bottom='mundu', bot_col='#e8e2cc', border='#2a5a3a', shoe='chappal_blue',
              hat=None, glasses=None, build=1.0)
AMMINI = dict(name='AMMINI', h=0.84, sex='f', skin='#c08458', hair='#1a1410', hairstyle='bun', stache=None, beard=None,
              top='saree', top_col='#a8324a', shirt='#e0b23a', bottom='saree', bot_col='#a8324a', border='#e0b23a', shoe='flat_sandal',
              hat=None, glasses=None, build=1.0)
JOSE = dict(name='JOSE', h=0.97, sex='m', skin='#c08a60', hair='#2a2622', hairstyle='combed_grey', stache='neat', beard=None,
            top='blazer', top_col='#2e2a52', shirt='#f2ead2', tie='#b8862a', bottom='trousers', bot_col='#24243a', shoe='leather_black',
            hat=None, glasses=None, build=1.05)

# ------------------------------------------------------------------ geometry
def geo(spec):
    h = 900*spec['h']; hh = h/7.4; f = spec['sex'] == 'f'; b = spec.get('build', 1.0)
    return dict(h=h, hh=hh, top=-h, hc=-h+hh*0.52, rx=hh*0.40, ry=hh*0.52, chin=-h+hh*1.04, sh=-h+hh*1.42,
                sw=hh*(0.84 if f else 1.0)*b, wy=-h+hh*3.0, ww=hh*(0.52 if f else 0.62)*b, hy=-h+hh*3.6, hw=hh*(0.74 if f else 0.66)*b,
                ky=-h+hh*5.45, ay=-hh*0.28, L1=hh*1.45, L2=hh*1.32)

def ik(sx, sy, tx, ty, L1, L2, bend):
    dx, dy = tx-sx, ty-sy; d = math.hypot(dx, dy); d = max(1e-3, min(d, L1+L2-1e-3))
    a = math.atan2(dy, dx); c = (L1*L1 + d*d - L2*L2)/(2*L1*d); al = math.acos(max(-1, min(1, c)))
    ea = a + bend*al
    ex, ey = sx + L1*math.cos(ea), sy + L1*math.sin(ea)
    hx, hy = sx + math.cos(a)*d, sy + math.sin(a)*d
    return ex, ey, hx, hy

# ------------------------------------------------------------------ parts
def legs(ctx, spec, g, pose, t):
    hh = g['hh']; walk = pose.get('walk', 0.0)
    kind = spec['bottom']
    for sd in (-1, 1):
        ph = math.sin(t*7.5 + (0 if sd < 0 else math.pi))*walk
        x0 = sd*hh*0.30; xk = x0 + ph*hh*0.25; xa = x0 + ph*hh*0.45
        if kind in ('saree', 'mundu'):
            shoe(ctx, spec, x0, 0, hh, pose.get('face', 1), sd); continue
        col = spec['bot_col']
        wt, wa = hh*0.40, hh*(0.20 if kind == 'churidar' else 0.27)
        ctx.move_to(x0 - wt/2 - sd*0.02*hh, g['hy']-hh*0.25); ctx.line_to(x0 + wt/2, g['hy']-hh*0.25)
        ctx.line_to(xk + wt*0.42, g['ky']); ctx.line_to(xa + wa/2, g['ay']); ctx.line_to(xa - wa/2, g['ay']); ctx.line_to(xk - wt*0.42, g['ky']); ctx.close_path()
        shade(ctx, col, x0 - wt/2, x0 + wt/2); ctx.fill_preserve(); outline(ctx, 2.2, 0.35)
        if kind == 'trousers':  # crease
            ctx.move_to(x0 + sd*2, g['hy']); ctx.line_to(xa + sd*2, g['ay']-hh*0.1); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.set_line_width(3); ctx.stroke()
        if kind == 'churidar':
            for k in range(4):
                yy = g['ay'] - hh*0.12 - k*hh*0.07
                ctx.move_to(xa - wa*0.6, yy); ctx.curve_to(xa, yy+hh*0.04, xa, yy+hh*0.04, xa + wa*0.6, yy); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.set_line_width(2.5); ctx.stroke()
        shoe(ctx, spec, xa, 0, hh, pose.get('face', 1), sd)

def mundu(ctx, spec, g, pose, t):
    """Kerala mundu (white wrap from waist to ankles with a gold kasavu border); drawn after legs/shoes."""
    hh = g['hh']; col = spec.get('bot_col', '#f4f1e8'); bd = spec.get('border', '#d8a83a')
    top = g['wy'] + hh*0.15; bot = g['ay'] - hh*0.05; wt = g['hw']*1.05; wb = g['hw']*1.25
    ctx.move_to(-wt, top); ctx.line_to(wt, top); ctx.line_to(wb, bot); ctx.line_to(-wb, bot); ctx.close_path()
    shade(ctx, col, -wb, wb, 0.1, 0.22); ctx.fill_preserve(); outline(ctx, 2.2, 0.35)
    ctx.rectangle(-wb, bot - hh*0.12, 2*wb, hh*0.12); ctx.set_source_rgba(*hexc(bd)); ctx.fill()
    f = pose.get('face', 1)
    ctx.move_to(f*wt*0.2, top + hh*0.1); ctx.line_to(f*wb*0.35, bot); ctx.set_source_rgba(0, 0, 0, 0.13); ctx.set_line_width(3); ctx.stroke()
    ctx.rectangle(f*wb*0.35 - hh*0.03, top + hh*0.3, hh*0.06, bot - top - hh*0.3); ctx.set_source_rgba(*hexc(bd, 0.8)); ctx.fill()
    ctx.rectangle(-wt, top - hh*0.06, 2*wt, hh*0.12); ctx.set_source_rgba(*hexc(dk(col, 0.12))); ctx.fill()

def shoe(ctx, spec, x, y, hh, f, sd):
    k = spec['shoe']; L = hh*0.62; Hh = hh*0.22
    ctx.save(); ctx.translate(x + f*hh*0.08, y)
    if k.startswith('leather'):
        col = '#1a1416' if k == 'leather_black' else '#6a3e22'
        ctx.move_to(-f*L*0.38, -Hh); ctx.curve_to(f*L*0.1, -Hh*1.15, f*L*0.55, -Hh*0.9, f*L*0.62, -Hh*0.25)
        ctx.line_to(f*L*0.62, 0); ctx.line_to(-f*L*0.38, 0); ctx.close_path()
        shade(ctx, col, -L*0.4, L*0.6, 0.25, 0.2); ctx.fill_preserve(); outline(ctx, 2, 0.5)
        ellipse(ctx, f*L*0.25, -Hh*0.75, L*0.16, Hh*0.18); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.fill()
        ctx.rectangle(-f*L*0.38 - (L*0.2 if f < 0 else 0), -Hh*0.28, L*0.2, Hh*0.28); ctx.set_source_rgba(*hexc(dk(col, 0.5))); ctx.fill()  # heel block
    elif k == 'chappal_blue':
        ctx.rectangle(-f*L*0.35 - (L*0.95 if f < 0 else 0), -Hh*0.25, L*0.95, Hh*0.25); ctx.set_source_rgba(*hexc('#2a6ad8')); ctx.fill()
        ellipse(ctx, f*L*0.12, -Hh*0.55, L*0.42, Hh*0.42); shade(ctx, spec['skin'], -L*0.3, L*0.5); ctx.fill()
        ctx.move_to(f*L*0.25, -Hh*0.3); ctx.line_to(-f*L*0.05, -Hh*0.85); ctx.set_source_rgba(*hexc('#1a4aa8')); ctx.set_line_width(hh*0.07); ctx.stroke()
        for j in range(3): ellipse(ctx, f*(L*0.42 + j*L*0.04), -Hh*0.35 + j*2, L*0.05, Hh*0.12); ctx.set_source_rgba(*hexc(dk(spec['skin'], 0.1))); ctx.fill()
    elif k == 'boots_yellow':
        col = '#b07a2a'
        ctx.move_to(-f*L*0.38, -Hh*2.0); ctx.line_to(f*L*0.12, -Hh*2.0); ctx.curve_to(f*L*0.2, -Hh*1.0, f*L*0.68, -Hh*0.9, f*L*0.68, -Hh*0.2)
        ctx.line_to(f*L*0.68, 0); ctx.line_to(-f*L*0.38, 0); ctx.close_path(); shade(ctx, col, -L*0.4, L*0.6, 0.2, 0.25); ctx.fill_preserve(); outline(ctx, 2, 0.5)
        ctx.rectangle(-f*L*0.38 - (L*1.06 if f < 0 else 0), -Hh*0.3, L*1.06, Hh*0.3); ctx.set_source_rgba(*hexc('#3a2a1a')); ctx.fill()
        for j in range(5):  # zigzag sole edge
            xx = -f*L*0.36 + f*j*L*0.2
            ctx.move_to(xx, -Hh*0.05); ctx.line_to(xx + f*L*0.1, -Hh*0.25); ctx.line_to(xx + f*L*0.2, -Hh*0.05)
        ctx.set_source_rgba(*hexc('#c8a050')); ctx.set_line_width(2.5); ctx.stroke()
        for j in range(3): ctx.move_to(-f*L*0.1, -Hh*(1.7 - j*0.35)); ctx.line_to(f*L*0.1, -Hh*(1.6 - j*0.35))
        ctx.set_source_rgba(*hexc('#f2e2b0')); ctx.set_line_width(2.5); ctx.stroke()
    else:  # flat sandals (women)
        col = '#a8703a' if k == 'flat_sandal' else '#c08a50'
        ellipse(ctx, f*L*0.1, -Hh*0.5, L*0.44, Hh*0.45); shade(ctx, spec['skin'], -L*0.3, L*0.5); ctx.fill()
        ctx.rectangle(-f*L*0.35 - (L*0.92 if f < 0 else 0), -Hh*0.16, L*0.92, Hh*0.16); ctx.set_source_rgba(*hexc(dk(col, 0.2))); ctx.fill()
        ctx.move_to(-f*L*0.05, -Hh*0.75); ctx.line_to(f*L*0.3, -Hh*0.6); ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(hh*0.08); ctx.stroke()
        if k == 'flat_tan':  # closed juttis
            ellipse(ctx, f*L*0.12, -Hh*0.45, L*0.46, Hh*0.42); shade(ctx, col, -L*0.3, L*0.5); ctx.fill()
            ellipse(ctx, f*L*0.2, -Hh*0.5, L*0.12, Hh*0.12); ctx.set_source_rgba(*hexc('#e0b040')); ctx.fill()
    ctx.restore()

def torso(ctx, spec, g, pose, t):
    hh, sh, sw, wy, ww, hy, hw = g['hh'], g['sh'], g['sw'], g['wy'], g['ww'], g['hy'], g['hw']
    top = spec['top']; col = spec['top_col']; f = pose.get('face', 1)
    def body_path(bot_y, bot_w, flare=0.0):
        ctx.move_to(-sw*0.55, sh - hh*0.06)
        ctx.curve_to(-sw*0.9, sh, -sw, sh + hh*0.15, -sw*0.98, sh + hh*0.35)
        ctx.line_to(-ww - hh*0.02, wy); ctx.line_to(-bot_w - flare, bot_y); ctx.line_to(bot_w + flare, bot_y); ctx.line_to(ww + hh*0.02, wy)
        ctx.line_to(sw*0.98, sh + hh*0.35); ctx.curve_to(sw, sh + hh*0.15, sw*0.9, sh, sw*0.55, sh - hh*0.06); ctx.close_path()
    if top == 'trench':
        bot = g['ky'] + hh*0.15
        body_path(bot, hw*1.05, hh*0.25); shade(ctx, col, -sw, sw); ctx.fill_preserve(); outline(ctx, 2.6, 0.5)
        # shirt V + lapels
        ctx.move_to(-hh*0.2, sh - hh*0.05); ctx.line_to(0, sh + hh*0.75); ctx.line_to(hh*0.2, sh - hh*0.05); ctx.close_path(); ctx.set_source_rgba(*hexc(spec['shirt'])); ctx.fill()
        for sd in (-1, 1):
            ctx.move_to(sd*hh*0.2, sh - hh*0.08); ctx.line_to(sd*hh*0.62, sh + hh*0.05); ctx.line_to(sd*hh*0.42, sh + hh*0.35); ctx.line_to(sd*hh*0.18, sh + hh*0.95); ctx.line_to(0, sh + hh*0.8); ctx.close_path()
            shade(ctx, dk(col, 0.06), -hh*0.6, hh*0.6); ctx.fill_preserve(); outline(ctx, 2, 0.45)
        # front overlap edge + buttons
        ctx.move_to(hh*0.18, sh + hh*0.95); ctx.line_to(hh*0.24, bot); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.set_line_width(3); ctx.stroke()
        for row in (-1, 1):
            for k in range(3):
                bx, by = row*hh*0.30 + hh*0.05, sh + hh*1.05 + k*hh*0.42
                ctx.arc(bx, by, hh*0.055, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#d8a83a')); ctx.fill()
                ctx.arc(bx - hh*0.015, by - hh*0.015, hh*0.02, 0, 2*math.pi); ctx.set_source_rgba(1, 0.95, 0.7, 0.9); ctx.fill()
        # belt
        ctx.rectangle(-ww - hh*0.08, wy - hh*0.12, 2*ww + hh*0.16, hh*0.2); ctx.set_source_rgba(*hexc('#2a2418')); ctx.fill()
        rrect(ctx, -hh*0.12, wy - hh*0.15, hh*0.24, hh*0.26, hh*0.04); ctx.set_source_rgba(*hexc('#c99a3a')); ctx.set_line_width(hh*0.05); ctx.stroke()
        # coat folds
        ctx.set_source_rgba(0, 0, 0, 0.13); ctx.set_line_width(3)
        for k in (-0.5, 0.55): ctx.move_to(k*hw, wy + hh*0.2); ctx.line_to(k*hw*1.3, bot - hh*0.1); ctx.stroke()
        # pocket flaps
        for sd in (-1, 1): ctx.rectangle(sd*hw*0.55 - hh*0.22, hy - hh*0.15, hh*0.44, hh*0.1); ctx.set_source_rgba(*hexc(dk(col, 0.15))); ctx.fill()
    elif top == 'kurta':
        bot = g['ky'] - hh*0.05
        body_path(bot, hw*1.1, hh*0.15); shade(ctx, col, -sw, sw); ctx.fill_preserve(); outline(ctx, 2.4, 0.45)
        ctx.move_to(-hh*0.14, sh - hh*0.04); ctx.line_to(0, sh + hh*0.45); ctx.line_to(hh*0.14, sh - hh*0.04); ctx.set_source_rgba(*hexc(dk(col, 0.35))); ctx.set_line_width(3); ctx.stroke()
        # embroidery border + neck
        ctx.rectangle(-hw*1.1 - hh*0.15, bot - hh*0.14, 2*(hw*1.1 + hh*0.15), hh*0.1); ctx.set_source_rgba(*hexc('#e8c04a')); ctx.fill()
        for k in range(9): ctx.arc(-hw*1.15 + k*hw*0.29, bot - hh*0.09, hh*0.025, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
        for sd in (-1, 1): ctx.move_to(sd*hw*1.0, hy + hh*0.3); ctx.line_to(sd*hw*1.15, bot); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.set_line_width(3); ctx.stroke()
        # dupatta: around the neck, two ends falling behind shoulders + front drape
        dcol = spec.get('dupatta', '#ffffff')
        ctx.move_to(-sw*0.85, sh + hh*0.05); ctx.curve_to(-sw*0.3, sh + hh*0.75, sw*0.3, sh + hh*0.75, sw*0.85, sh + hh*0.05)
        ctx.curve_to(sw*0.35, sh + hh*0.45, -sw*0.35, sh + hh*0.45, -sw*0.85, sh + hh*0.05); ctx.close_path()
        vshade(ctx, dcol, sh, sh + hh*0.8, 0.0, 0.12); ctx.fill_preserve(); outline(ctx, 1.8, 0.3)
        for sd in (-1, 1):
            ctx.move_to(sd*sw*0.95, sh + hh*0.05); ctx.curve_to(sd*sw*1.08, sh + hh*0.8, sd*sw*1.0, sh + hh*1.6, sd*sw*1.04, wy + hh*0.6)
            ctx.line_to(sd*sw*0.82, wy + hh*0.6); ctx.curve_to(sd*sw*0.85, sh + hh*1.2, sd*sw*0.8, sh + hh*0.5, sd*sw*0.75, sh + hh*0.05); ctx.close_path()
            vshade(ctx, dcol, sh, wy, 0.0, 0.15); ctx.fill_preserve(); outline(ctx, 1.8, 0.3)
        # sling bag strap + bag
        ctx.move_to(-sw*0.6, sh - hh*0.02); ctx.line_to(hw*0.95, hy + hh*0.1); ctx.set_source_rgba(*hexc(dk(spec['bag'], 0.3))); ctx.set_line_width(hh*0.07); ctx.stroke()
        rrect(ctx, hw*0.65, hy - hh*0.05, hh*0.62, hh*0.5, hh*0.1); shade(ctx, spec['bag'], hw*0.6, hw*0.6 + hh*0.62); ctx.fill_preserve(); outline(ctx, 2, 0.5)
        ctx.move_to(hw*0.65, hy + hh*0.12); ctx.curve_to(hw*0.8, hy + hh*0.22, hw*0.65 + hh*0.5, hy + hh*0.22, hw*0.65 + hh*0.62, hy + hh*0.12)
        ctx.set_source_rgba(*hexc(dk(spec['bag'], 0.25))); ctx.set_line_width(3); ctx.stroke()
    elif top == 'blazer':
        bot = hy + hh*0.35
        body_path(bot, hw*1.02); shade(ctx, col, -sw, sw); ctx.fill_preserve(); outline(ctx, 2.6, 0.5)
        ctx.move_to(-hh*0.22, sh - hh*0.05); ctx.line_to(0, sh + hh*1.3); ctx.line_to(hh*0.22, sh - hh*0.05); ctx.close_path(); ctx.set_source_rgba(*hexc(spec['shirt'])); ctx.fill()
        ctx.move_to(-hh*0.06, sh + hh*0.02); ctx.line_to(hh*0.06, sh + hh*0.02); ctx.line_to(hh*0.09, sh + hh*1.05); ctx.line_to(0, sh + hh*1.2); ctx.line_to(-hh*0.09, sh + hh*1.05); ctx.close_path()
        shade(ctx, spec['tie'], -hh*0.1, hh*0.1); ctx.fill()
        for sd in (-1, 1):
            ctx.move_to(sd*hh*0.22, sh - hh*0.08); ctx.line_to(sd*hh*0.55, sh + hh*0.05); ctx.line_to(sd*hh*0.38, sh + hh*0.4); ctx.line_to(sd*hh*0.05, sh + hh*1.35); ctx.close_path()
            shade(ctx, dk(col, 0.1), -hh*0.5, hh*0.5); ctx.fill_preserve(); outline(ctx, 2, 0.45)
        for k in range(2): ctx.arc(hh*0.12, sh + hh*1.5 + k*hh*0.35, hh*0.045, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#2a1a10')); ctx.fill()
        ctx.rectangle(-sw*0.75, sh + hh*0.55, hh*0.35, hh*0.06); ctx.set_source_rgba(*hexc(dk(col, 0.2))); ctx.fill()
        ctx.move_to(-sw*0.7, sh + hh*0.55); ctx.line_to(-sw*0.62, sh + hh*0.42); ctx.line_to(-sw*0.55, sh + hh*0.55); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()  # pocket square
    elif top in ('uniform', 'work'):
        bot = hy + hh*0.15
        body_path(bot, hw*1.0); shade(ctx, col, -sw, sw); ctx.fill_preserve(); outline(ctx, 2.5, 0.5)
        ctx.move_to(0, sh); ctx.line_to(0, bot); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(3); ctx.stroke()
        for k in range(4): ctx.arc(hh*0.05, sh + hh*0.35 + k*hh*0.42, hh*0.04, 0, 2*math.pi); ctx.set_source_rgba(*hexc(dk(col, 0.45))); ctx.fill()
        for sd in (-1, 1):
            rrect(ctx, sd*hh*0.48 - hh*0.2, sh + hh*0.45, hh*0.4, hh*0.42, hh*0.05); ctx.set_source_rgba(*hexc(dk(col, 0.1))); ctx.fill_preserve(); outline(ctx, 1.8, 0.35)
            ctx.move_to(sd*hh*0.2, sh - hh*0.06); ctx.line_to(sd*hh*0.48, sh + hh*0.12); ctx.line_to(sd*hh*0.08, sh + hh*0.28); ctx.close_path(); ctx.set_source_rgba(*hexc(dk(col, 0.08))); ctx.fill_preserve(); outline(ctx, 1.5, 0.35)
        if top == 'uniform':
            for sd in (-1, 1): rrect(ctx, sd*sw*0.7 - hh*0.2, sh - hh*0.02, hh*0.4, hh*0.1, hh*0.03); ctx.set_source_rgba(*hexc(dk(col, 0.25))); ctx.fill()
            ctx.rectangle(-ww - hh*0.05, wy + hh*0.25, 2*ww + hh*0.1, hh*0.16); ctx.set_source_rgba(*hexc('#1e1812')); ctx.fill()
            rrect(ctx, -hh*0.1, wy + hh*0.22, hh*0.2, hh*0.22, hh*0.03); ctx.set_source_rgba(*hexc('#c9a24a')); ctx.fill()
            # name badge
            rrect(ctx, -hh*0.5, sh + hh*0.32, hh*0.32, hh*0.09, hh*0.02); ctx.set_source_rgba(*hexc('#1a2a5a')); ctx.fill()
        if spec.get('toolbelt'):
            ctx.rectangle(-ww - hh*0.08, wy + hh*0.25, 2*ww + hh*0.16, hh*0.18); ctx.set_source_rgba(*hexc('#6a4220')); ctx.fill()
            for k, cc in enumerate(('#8a5a2a', '#d23a2a', '#6a6a72')):
                rrect(ctx, -ww + k*ww*0.7, wy + hh*0.3, hh*0.3, hh*0.45, hh*0.05); ctx.set_source_rgba(*hexc(cc)); ctx.fill()
            ctx.rectangle(-ww + 0.05*hh, wy + hh*0.05, hh*0.05, hh*0.3); ctx.set_source_rgba(*hexc('#c0c0c8')); ctx.fill()  # screwdriver
    elif top == 'saree':
        bot = g['ay'] + hh*0.1
        # skirt part
        ctx.move_to(-hw*0.95, hy - hh*0.6); ctx.line_to(hw*0.95, hy - hh*0.6); ctx.curve_to(hw*1.25, g['ky'], hw*1.3, bot, hw*1.3, bot)
        ctx.line_to(-hw*1.3, bot); ctx.curve_to(-hw*1.3, bot, -hw*1.25, g['ky'], -hw*0.95, hy - hh*0.6); ctx.close_path()
        shade(ctx, col, -hw*1.3, hw*1.3); ctx.fill_preserve(); outline(ctx, 2.4, 0.45)
        for k in range(5): ctx.move_to(-hw*0.3 + k*hw*0.15, hy - hh*0.3); ctx.line_to(-hw*0.45 + k*hw*0.22, bot); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.set_line_width(3); ctx.stroke()
        ctx.rectangle(-hw*1.3, bot - hh*0.16, hw*2.6, hh*0.16); ctx.set_source_rgba(*hexc(spec['border'])); ctx.fill()
        # blouse + waist skin
        body_path(wy - hh*0.55, ww*0.95); shade(ctx, spec['shirt'], -sw, sw); ctx.fill_preserve(); outline(ctx, 2.2, 0.45)
        ctx.rectangle(-ww*0.95, wy - hh*0.55, ww*1.9, hh*0.5); shade(ctx, spec['skin'], -ww, ww); ctx.fill()
        # pallu across the chest to the left shoulder
        ctx.move_to(sw*0.9, hy - hh*0.5); ctx.line_to(-sw*0.2, sh + hh*0.05); ctx.line_to(-sw*0.95, sh - hh*0.02); ctx.line_to(-sw*1.05, wy + hh*0.4)
        ctx.line_to(-sw*0.55, wy + hh*0.5); ctx.line_to(-sw*0.6, sh + hh*0.6); ctx.line_to(sw*0.5, hy - hh*0.25); ctx.close_path()
        shade(ctx, lt(col, 0.05), -sw, sw); ctx.fill_preserve(); outline(ctx, 2.2, 0.45)
        ctx.move_to(sw*0.9, hy - hh*0.5); ctx.line_to(-sw*0.2, sh + hh*0.05); ctx.set_source_rgba(*hexc(spec['border'])); ctx.set_line_width(hh*0.08); ctx.stroke()

def arm(ctx, spec, g, side, mode, pose, t):
    """side: -1 screen-left arm, +1 screen-right arm."""
    hh, f = g['hh'], pose.get('face', 1)
    sx, sy = side*(g['sw'] - hh*0.16), g['sh'] + hh*0.14
    L1, L2 = g['L1'], g['L2']; bend = -side  # elbows bend outward/down by default
    tx, ty = sx + side*hh*0.28, sy + L1 + L2 - hh*0.12; prop = None
    if mode == 'hip': tx, ty = side*(g['ww'] + hh*0.12), g['wy'] + hh*0.1; bend = -side
    elif mode == 'point': tx, ty = sx + side*(L1 + L2 - hh*0.1), sy + hh*0.05; bend = side
    elif mode == 'chin':
        tx, ty = f*g['rx']*0.25 + side*hh*0.05, g['chin'] - hh*0.22 + hh*0.04*math.sin(t*3); bend = -side
    elif mode == 'notebook': tx, ty = side*hh*0.15 + f*hh*0.3, g['sh'] + hh*1.35; bend = -side; prop = 'notebook'
    elif mode == 'write': tx, ty = side*hh*0.05 + f*hh*0.3 + hh*0.06*math.sin(t*9), g['sh'] + hh*1.25; bend = -side; prop = 'pen'
    elif mode == 'chips': tx, ty = side*hh*0.25 + f*hh*0.25, g['sh'] + hh*1.5; bend = -side; prop = 'chips'
    elif mode == 'eat':
        ph = (math.sin(t*3.2) + 1)/2
        tx = (side*hh*0.2 + f*hh*0.2)*(1-ph) + f*g['rx']*0.3*ph; ty = (g['sh'] + hh*1.4)*(1-ph) + (g['chin'] - hh*0.25)*ph; bend = -side; prop = 'chip'
    elif mode == 'up': tx, ty = sx + side*hh*0.9, sy - hh*1.6; bend = side
    elif mode == 'wave': tx, ty = sx + side*hh*0.8 + hh*0.2*math.sin(t*8), sy - hh*1.5; bend = side
    elif mode == 'cuffed': tx, ty = side*hh*0.08, g['wy'] + hh*0.4; bend = -side; prop = 'cuff'
    elif mode == 'give': tx, ty = sx + f*(L1 + L2 - hh*0.2), sy + hh*0.8; bend = -side; prop = pose.get('give_prop')
    elif mode == 'torch': tx, ty = sx + f*(L1 + L2 - hh*0.15), sy + hh*0.45; bend = -side; prop = 'torch'
    elif mode == 'mop': tx, ty = side*hh*0.1 + f*hh*0.6, g['sh'] + hh*1.3; bend = -side; prop = 'mop'
    elif mode == 'hold': tx, ty = sx + f*hh*0.9, sy + hh*1.4; bend = -side; prop = pose.get('hold_prop')
    elif mode == 'down_back': tx, ty = sx + side*hh*0.15, sy + L1 + L2 - hh*0.1
    if mode in ('chin', 'notebook', 'write', 'chips', 'eat', 'cuffed', 'mop', 'hold', 'hip'):
        L1, L2 = L1*0.92, L2*(0.72 if mode != 'hip' else 0.9)   # forearm foreshortened (coming toward camera)
    ex, ey, hx, hy = ik(sx, sy, tx, ty, L1, L2, bend)
    sleeve = spec['top_col'] if spec['top'] != 'saree' else spec['shirt']
    long_sleeve = spec['top'] in ('trench', 'blazer', 'kurta', 'work')
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    w1 = hh*(0.36 if spec['sex'] == 'm' else 0.29); w2 = w1*0.86
    # upper arm
    ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.set_source_rgba(0.08, 0.05, 0.05, 0.45); ctx.set_line_width(w1 + 5); ctx.stroke()
    ctx.move_to(sx, sy); ctx.line_to(ex, ey); shade(ctx, sleeve, min(sx, ex) - w1, max(sx, ex) + w1); ctx.set_line_width(w1); ctx.stroke()
    if spec['top'] in ('uniform', 'saree'):
        mx, my = sx + (ex-sx)*0.55, sy + (ey-sy)*0.55
        ctx.move_to(mx, my); ctx.line_to(ex, ey); shade(ctx, spec['skin'], min(mx, ex) - w1, max(mx, ex) + w1); ctx.set_line_width(w1*0.82); ctx.stroke()
    fc = sleeve if long_sleeve else spec['skin']
    cx_ = hx - (hx-ex)*0.18; cy_ = hy - (hy-ey)*0.18
    ctx.move_to(ex, ey); ctx.line_to(cx_, cy_); ctx.set_source_rgba(0.08, 0.05, 0.05, 0.45); ctx.set_line_width(w2 + 5); ctx.stroke()
    ctx.move_to(ex, ey); ctx.line_to(cx_, cy_); shade(ctx, fc, min(ex, hx) - w2, max(ex, hx) + w2); ctx.set_line_width(w2); ctx.stroke()
    if long_sleeve:
        ctx.move_to(cx_, cy_); ctx.line_to(hx, hy); shade(ctx, spec['skin'], hx - w2, hx + w2); ctx.set_line_width(w2*0.62); ctx.stroke()
        ctx.arc(cx_, cy_, w2*0.52, 0, 2*math.pi); ctx.set_source_rgba(*hexc(dk(fc, 0.18))); ctx.fill()
        if spec['top'] == 'blazer': ctx.arc(cx_, cy_, w2*0.4, 0, 2*math.pi); ctx.set_source_rgba(*hexc(spec['shirt'])); ctx.fill()
    # hand
    ctx.arc(hx, hy, hh*0.15, 0, 2*math.pi); shade(ctx, spec['skin'], hx - hh*0.15, hx + hh*0.15); ctx.fill_preserve(); outline(ctx, 2, 0.4)
    if mode == 'point':
        ctx.move_to(hx, hy); ctx.line_to(hx + side*hh*0.32, hy - hh*0.02); ctx.set_line_width(hh*0.08); shade(ctx, spec['skin'], hx, hx + hh*0.3); ctx.stroke()
    if prop: draw_prop(ctx, prop, hx, hy, hh, f, side, t)

def draw_prop(ctx, prop, x, y, hh, f, side, t):
    if prop == 'notebook':
        ctx.save(); ctx.translate(x, y - hh*0.1); ctx.rotate(-0.15*f)
        rrect(ctx, -hh*0.3, -hh*0.42, hh*0.6, hh*0.75, hh*0.04); ctx.set_source_rgba(*hexc('#5a3a22')); ctx.fill()
        rrect(ctx, -hh*0.26, -hh*0.38, hh*0.52, hh*0.67, hh*0.03); ctx.set_source_rgba(*hexc('#f6efdc')); ctx.fill()
        for k in range(5): ctx.rectangle(-hh*0.2, -hh*0.28 + k*hh*0.11, hh*0.4, 2); ctx.set_source_rgba(0.3, 0.35, 0.6, 0.6); ctx.fill()
        ctx.restore()
    elif prop == 'pen':
        ctx.move_to(x, y); ctx.line_to(x - hh*0.05, y - hh*0.35); ctx.set_source_rgba(*hexc('#1a1a2a')); ctx.set_line_width(hh*0.05); ctx.stroke()
    elif prop in ('chips', 'chip'):
        if prop == 'chips':
            ctx.save(); ctx.translate(x, y - hh*0.2); ctx.rotate(0.1*f)
            ctx.move_to(-hh*0.3, -hh*0.45); ctx.line_to(hh*0.3, -hh*0.45); ctx.line_to(hh*0.34, hh*0.35); ctx.line_to(-hh*0.34, hh*0.35); ctx.close_path()
            shade(ctx, '#f2c21a', -hh*0.3, hh*0.3); ctx.fill_preserve(); outline(ctx, 2, 0.5)
            ctx.rectangle(-hh*0.32, -hh*0.08, hh*0.64, hh*0.2); ctx.set_source_rgba(*hexc('#d8282a')); ctx.fill()
            for k in range(3): ellipse(ctx, -hh*0.15 + k*hh*0.15, -hh*0.47, hh*0.09, hh*0.05); ctx.set_source_rgba(*hexc('#e8c058')); ctx.fill()
            ctx.restore()
        else:
            ellipse(ctx, x + f*hh*0.05, y - hh*0.15, hh*0.09, hh*0.07); ctx.set_source_rgba(*hexc('#ecc65a')); ctx.fill()
    elif prop == 'torch':
        ctx.save(); ctx.translate(x, y); ctx.rotate(0 if f > 0 else math.pi)
        rrect(ctx, -hh*0.1, -hh*0.08, hh*0.55, hh*0.16, hh*0.04); ctx.set_source_rgba(*hexc('#2a2a30')); ctx.fill()
        rrect(ctx, hh*0.42, -hh*0.12, hh*0.12, hh*0.24, hh*0.03); ctx.set_source_rgba(*hexc('#b8b8c0')); ctx.fill()
        ctx.restore()
    elif prop == 'mop':
        ctx.move_to(x, y - hh*1.0); ctx.line_to(x + f*hh*0.5, -hh*0.1); ctx.set_source_rgba(*hexc('#c8a060')); ctx.set_line_width(hh*0.08); ctx.stroke()
        for k in range(9):
            ctx.move_to(x + f*hh*0.5, -hh*0.15); ctx.line_to(x + f*hh*0.5 + (k-4)*hh*0.08, 0); ctx.set_source_rgba(*hexc('#e8e4da')); ctx.set_line_width(hh*0.06); ctx.stroke()
    elif prop == 'receipt':
        ctx.save(); ctx.translate(x, y - hh*0.2); ctx.rotate(0.12*f)
        ctx.rectangle(-hh*0.2, -hh*0.4, hh*0.4, hh*0.6); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill_preserve(); outline(ctx, 1.5, 0.4)
        for k in range(5): ctx.rectangle(-hh*0.14, -hh*0.32 + k*hh*0.1, hh*0.28, 2); ctx.set_source_rgba(0.2, 0.2, 0.2, 0.7); ctx.fill()
        ctx.restore()
    elif prop == 'cuff':
        ctx.arc(x, y - hh*0.05, hh*0.12, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#c0c4cc')); ctx.set_line_width(hh*0.05); ctx.stroke()
    elif prop == 'key':
        ctx.save(); ctx.translate(x, y - hh*0.1)
        ctx.arc(0, 0, hh*0.1, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#d8a83a')); ctx.set_line_width(hh*0.05); ctx.stroke()
        ctx.rectangle(hh*0.08, -hh*0.025, hh*0.35, hh*0.05); ctx.set_source_rgba(*hexc('#d8a83a')); ctx.fill(); ctx.restore()

def head(ctx, spec, g, pose, t):
    hh, rx, ry, hc, f = g['hh'], g['rx'], g['ry'], g['hc'], pose.get('face', 1)
    skin = spec['skin']; expr = pose.get('expr', 'neutral'); talk = pose.get('talk', 0.0)
    m = spec['sex'] == 'm'
    # neck
    ctx.rectangle(-rx*0.42, g['chin'] - hh*0.2, rx*0.84, g['sh'] - g['chin'] + hh*0.2); shade(ctx, dk(skin, 0.08), -rx*0.42, rx*0.42); ctx.fill()
    ctx.rectangle(-rx*0.42, g['chin'] - hh*0.05, rx*0.84, hh*0.12); ctx.set_source_rgba(0, 0, 0, 0.15); ctx.fill()
    if spec['top'] in ('uniform', 'work', 'blazer', 'trench'):  # collar
        for sd in (-1, 1):
            ctx.move_to(sd*rx*0.05, g['sh'] + hh*0.12); ctx.line_to(sd*rx*0.62, g['sh'] - hh*0.12); ctx.line_to(sd*rx*0.75, g['sh'] + hh*0.06); ctx.close_path()
            ctx.set_source_rgba(*hexc(spec['shirt'] if spec['top'] != 'trench' else spec['top_col'])); ctx.fill_preserve(); outline(ctx, 1.6, 0.4)
    ox = f*rx*0.10
    # back hair (long)
    hair = spec['hair']; hs = spec['hairstyle']
    if hs == 'side_ponytail':
        ctx.move_to(-rx*1.05, hc - ry*0.2); ctx.curve_to(-rx*1.2, hc + ry*0.8, -rx*0.9, hc + ry*1.3, -rx*0.7, hc + ry*1.3)
        ctx.line_to(rx*0.7, hc + ry*1.3); ctx.curve_to(rx*0.9, hc + ry*1.3, rx*1.2, hc + ry*0.8, rx*1.05, hc - ry*0.2); ctx.close_path()
        ctx.set_source_rgba(*hexc(hair)); ctx.fill()
    if hs == 'bun':
        ctx.arc(-f*rx*0.85, hc - ry*0.35, rx*0.42, 0, 2*math.pi); shade(ctx, hair, -rx, rx, 0.25, 0.2); ctx.fill()
        for k in range(5): ctx.arc(-f*rx*0.85 + (k-2)*rx*0.13, hc - ry*0.75, rx*0.07, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 0.97, 1); ctx.fill()
    # ears
    for sd in (-1, 1):
        if sd == f and abs(f) > 0: ex = sd*rx*0.92 + ox*0.3
        else: ex = sd*rx*0.98 + ox*0.3
        ellipse(ctx, ex, hc + ry*0.08, rx*0.17, ry*0.24); shade(ctx, skin, ex - rx*0.2, ex + rx*0.2); ctx.fill_preserve(); outline(ctx, 1.6, 0.4)
    # face shape
    ctx.move_to(-rx, hc - ry*0.1)
    ctx.curve_to(-rx, hc - ry*1.05, rx, hc - ry*1.05, rx, hc - ry*0.1)
    jaw = 0.82 if m else 0.62
    ctx.curve_to(rx*1.0, hc + ry*0.5, rx*jaw, hc + ry*0.85, ox*0.4, hc + ry*1.0)
    ctx.curve_to(-rx*jaw, hc + ry*0.85, -rx*1.0, hc + ry*0.5, -rx, hc - ry*0.1); ctx.close_path()
    shade(ctx, skin, -rx, rx, 0.12, 0.2); ctx.fill_preserve(); outline(ctx, 2.4, 0.5)
    # cheek light / shadow
    ellipse(ctx, -f*rx*0.55, hc + ry*0.35, rx*0.3, ry*0.18); ctx.set_source_rgba(1, 0.55, 0.5, 0.14 if m else 0.24); ctx.fill()
    if spec.get('beard') == 'short':
        ctx.move_to(-rx*0.95, hc + ry*0.05); ctx.curve_to(-rx*0.9, hc + ry*0.75, -rx*0.4, hc + ry*1.05, ox*0.4, hc + ry*1.06)
        ctx.curve_to(rx*0.4, hc + ry*1.05, rx*0.9, hc + ry*0.75, rx*0.95, hc + ry*0.05)
        ctx.curve_to(rx*0.75, hc + ry*0.6, rx*0.3, hc + ry*0.72, ox, hc + ry*0.7); ctx.curve_to(-rx*0.3, hc + ry*0.72, -rx*0.75, hc + ry*0.6, -rx*0.95, hc + ry*0.05)
        ctx.close_path(); ctx.set_source_rgba(*hexc(hair, 0.85)); ctx.fill()
    # eyes
    blink = pose.get('blink', True) and ((t + (hash(spec['name']) % 7)*0.37) % 3.7) < 0.12
    ey = hc + ry*0.02; esp = rx*0.42; ew, eh = rx*0.25, ry*0.13
    open_k = {'shock': 1.35, 'scared': 1.2, 'sad': 0.6, 'smug': 0.7, 'think': 0.8, 'laugh': 0.25, 'angry': 0.8}.get(expr, 1.0)
    look = pose.get('look', (f*0.35, 0.0))
    for sd in (-1, 1):
        ex = sd*esp + ox
        if blink or open_k < 0.3:
            ctx.move_to(ex - ew, ey); ctx.curve_to(ex - ew*0.3, ey + eh*0.8, ex + ew*0.3, ey + eh*0.8, ex + ew, ey); ctx.set_source_rgba(0.1, 0.06, 0.05, 1); ctx.set_line_width(3.5); ctx.stroke()
            continue
        ctx.save(); ellipse(ctx, ex, ey, ew, eh*open_k); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill_preserve(); ctx.clip()
        ix, iy = ex + look[0]*ew*0.45, ey + look[1]*eh*0.4
        ctx.arc(ix, iy, eh*0.95, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#4a2c18')); ctx.fill()
        ctx.arc(ix, iy, eh*0.55, 0, 2*math.pi); ctx.set_source_rgba(0.05, 0.03, 0.02, 1); ctx.fill()
        ctx.arc(ix - eh*0.3, iy - eh*0.35, eh*0.28, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 0.95); ctx.fill()
        ctx.restore()
        ctx.move_to(ex - ew*1.1, ey + eh*0.1); ctx.curve_to(ex - ew*0.5, ey - eh*1.35*open_k, ex + ew*0.5, ey - eh*1.35*open_k, ex + ew*1.1, ey - eh*0.1)
        ctx.set_source_rgba(0.08, 0.05, 0.04, 1); ctx.set_line_width(4 if m else 4.5); ctx.stroke()
        if not m:
            ctx.move_to(ex + sd*ew*0.9, ey - eh*0.4); ctx.line_to(ex + sd*ew*1.35, ey - eh*0.9); ctx.set_line_width(3); ctx.stroke()
    # eyebrows
    bro = {'shock': (-0.55, 0.0), 'scared': (-0.4, 0.35), 'sad': (-0.15, 0.4), 'angry': (0.1, -0.45), 'think': (0.0, -0.25),
           'smug': (-0.1, -0.1), 'laugh': (-0.15, 0.0)}.get(expr, (0.0, 0.0))
    for sd in (-1, 1):
        ex = sd*esp + ox; by = hc - ry*0.28 + bro[0]*ry*0.3
        inner = bro[1]*ry*0.25*(1 if not (expr == 'smug' and sd == f) else -2)
        if expr == 'think' and sd == -f: inner, by = 0.25*ry*0.25, by - ry*0.05
        ctx.move_to(ex - sd*ew*1.15, by + ry*0.05); ctx.curve_to(ex - sd*ew*0.3, by - ry*0.08, ex + sd*ew*0.2, by - ry*0.06, ex + sd*ew*1.1, by - inner*0 + ry*0.02 - inner)
        ctx.set_source_rgba(*hexc(dk(hair, 0.1) if hs not in ('receding', 'combed_grey') else ('#4a4440' if hs == 'receding' else '#2a2420')))
        ctx.set_line_width(hh*(0.07 if m else 0.045)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    # nose
    nx = ox + f*rx*0.12; ny = hc + ry*0.38
    ctx.move_to(nx - f*rx*0.02, hc + ry*0.02); ctx.curve_to(nx + f*rx*0.12, ny - ry*0.1, nx + f*rx*0.16, ny, nx, ny + ry*0.02)
    ctx.set_source_rgba(*hexc(dk(skin, 0.35))); ctx.set_line_width(3); ctx.stroke()
    ellipse(ctx, nx - f*rx*0.12, ny, rx*0.07, ry*0.035); ctx.set_source_rgba(*hexc(dk(skin, 0.45))); ctx.fill()
    # mouth
    mx, my = ox + f*rx*0.05, hc + ry*0.66
    stache = spec.get('stache')
    if talk > 0.05 or expr in ('shock', 'laugh'):
        o = max(talk, 0.9 if expr == 'shock' else 0.6 if expr == 'laugh' else 0)
        ctx.save(); ctx.translate(mx, my + ry*0.02); ctx.scale(rx*(0.24 if expr != 'laugh' else 0.32), ry*(0.06 + 0.16*o))
        ctx.arc(0, 0, 1, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(*hexc('#5a1a1e')); ctx.fill()
        if o > 0.4: ctx.rectangle(mx - rx*0.16, my - ry*0.08*o + ry*0.02, rx*0.32, ry*0.04); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()
    else:
        curve = {'smile': 0.12, 'smug': 0.06, 'sad': -0.09, 'scared': -0.06, 'angry': -0.07}.get(expr, 0.02)
        ctx.move_to(mx - rx*0.24, my - (curve if expr != 'smug' else 0)*ry*0.6)
        ctx.curve_to(mx - rx*0.08, my + curve*ry, mx + rx*0.08, my + curve*ry, mx + rx*0.24, my - curve*ry*(1.6 if expr == 'smug' else 0.6))
        ctx.set_source_rgba(*hexc('#6a2a28')); ctx.set_line_width(3.5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    if not m:
        ellipse(ctx, mx, my + ry*0.07, rx*0.15, ry*0.035); ctx.set_source_rgba(0.75, 0.3, 0.32, 0.5); ctx.fill()
    if stache:
        col = '#d8d4cc' if stache == 'thick_grey' else dk(hair, 0.05)
        th = {'neat': 0.08, 'thick_grey': 0.13, 'light': 0.05}[stache]
        ctx.move_to(mx - rx*0.36, my - ry*0.02); ctx.curve_to(mx - rx*0.25, my - ry*(0.16 + th), mx - rx*0.05, my - ry*(0.16 + th*0.6), mx, my - ry*0.12)
        ctx.curve_to(mx + rx*0.05, my - ry*(0.16 + th*0.6), mx + rx*0.25, my - ry*(0.16 + th), mx + rx*0.36, my - ry*0.02)
        ctx.curve_to(mx + rx*0.2, my - ry*0.09, mx - rx*0.2, my - ry*0.09, mx - rx*0.36, my - ry*0.02); ctx.close_path()
        ctx.set_source_rgba(*hexc(col)); ctx.fill()
    if spec['sex'] == 'f' and spec['hairstyle'] == 'bun':
        ctx.arc(ox, hc - ry*0.22, rx*0.05, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#c0202a')); ctx.fill()
    # front hair
    if hs in ('short', 'combed_grey', 'curly'):
        ctx.move_to(-rx*1.02, hc - ry*0.05); ctx.curve_to(-rx*1.15, hc - ry*1.25, rx*1.15, hc - ry*1.3, rx*1.02, hc - ry*0.05)
        ctx.curve_to(rx*0.95, hc - ry*0.55, rx*0.6, hc - ry*0.62, f*rx*0.2, hc - ry*0.62 - ry*0.08*f)
        ctx.curve_to(-rx*0.4, hc - ry*0.6, -rx*0.9, hc - ry*0.55, -rx*1.02, hc - ry*0.05); ctx.close_path()
        shade(ctx, hair, -rx, rx, 0.22, 0.2); ctx.fill()
        if hs == 'combed_grey':
            for sd in (-1, 1): ellipse(ctx, sd*rx*0.95, hc - ry*0.25, rx*0.12, ry*0.22); ctx.set_source_rgba(0.75, 0.74, 0.72, 0.9); ctx.fill()
            ctx.move_to(-f*rx*0.3, hc - ry*0.95); ctx.curve_to(0, hc - ry*0.7, f*rx*0.4, hc - ry*0.72, f*rx*0.9, hc - ry*0.5); ctx.set_source_rgba(1, 1, 1, 0.18); ctx.set_line_width(4); ctx.stroke()
        if hs == 'curly':
            for k in range(9): ctx.arc(-rx*0.85 + k*rx*0.21, hc - ry*(0.78 + 0.12*math.sin(k*1.7)), rx*0.16, 0, 2*math.pi); ctx.set_source_rgba(*hexc(hair)); ctx.fill()
        if hs == 'short':
            ctx.move_to(-f*rx*0.35, hc - ry*0.98); ctx.curve_to(-f*rx*0.1, hc - ry*0.7, f*rx*0.3, hc - ry*0.72, f*rx*0.9, hc - ry*0.45)
            ctx.set_source_rgba(1, 1, 1, 0.12); ctx.set_line_width(4); ctx.stroke()
        for sd in (-1, 1): ctx.rectangle(sd*rx*0.98 - (rx*0.1 if sd > 0 else 0), hc - ry*0.3, rx*0.1, ry*0.35); ctx.set_source_rgba(*hexc(hair)); ctx.fill()
    elif hs == 'receding':
        for sd in (-1, 1):
            ctx.move_to(sd*rx*1.02, hc + ry*0.1); ctx.curve_to(sd*rx*1.1, hc - ry*0.7, sd*rx*0.6, hc - ry*0.95, sd*rx*0.2, hc - ry*0.98)
            ctx.curve_to(sd*rx*0.55, hc - ry*0.7, sd*rx*0.85, hc - ry*0.5, sd*rx*0.9, hc + ry*0.1); ctx.close_path(); ctx.set_source_rgba(*hexc(hair)); ctx.fill()
        ellipse(ctx, -rx*0.3, hc - ry*0.7, rx*0.25, ry*0.12); ctx.set_source_rgba(1, 1, 1, 0.25); ctx.fill()
    elif hs in ('side_ponytail', 'bun'):
        ctx.move_to(-rx*1.04, hc + ry*0.1); ctx.curve_to(-rx*1.2, hc - ry*1.25, rx*1.2, hc - ry*1.25, rx*1.04, hc + ry*0.1)
        ctx.curve_to(rx*0.9, hc - ry*0.45, rx*0.3, hc - ry*0.6, 0, hc - ry*0.72)
        ctx.curve_to(-rx*0.3, hc - ry*0.6, -rx*0.9, hc - ry*0.45, -rx*1.04, hc + ry*0.1); ctx.close_path()
        shade(ctx, hair, -rx, rx, 0.25, 0.2); ctx.fill()
        ctx.move_to(0, hc - ry*1.0); ctx.line_to(0, hc - ry*0.72); ctx.set_source_rgba(*hexc(lt(hair, 0.3))); ctx.set_line_width(2); ctx.stroke()
        if hs == 'side_ponytail':
            # ponytail over her right shoulder (screen side opposite face) with a yellow clip
            sd = -1 if f > 0 else 1
            px = sd*rx*0.9
            ctx.move_to(sd*rx*0.95, hc + ry*0.15); ctx.curve_to(sd*rx*1.5, hc + ry*0.9, sd*rx*1.45, g['sh'] + hh*0.6, sd*rx*1.3, g['sh'] + hh*1.45)
            ctx.curve_to(sd*rx*1.1, g['sh'] + hh*1.6, sd*rx*0.95, g['sh'] + hh*1.5, sd*rx*0.95, g['sh'] + hh*1.3)
            ctx.curve_to(sd*rx*0.95, g['sh'] + hh*0.5, sd*rx*0.9, hc + ry*1.0, sd*rx*0.82, hc + ry*0.6); ctx.close_path()
            shade(ctx, hair, px - rx*0.5, px + rx*0.5, 0.25, 0.2); ctx.fill()
            rrect(ctx, sd*rx*1.08 - rx*0.21, hc + ry*0.42, rx*0.42, ry*0.2, ry*0.06); ctx.set_source_rgba(*hexc('#ffd21a')); ctx.fill_preserve(); outline(ctx, 1.8, 0.5)
    # glasses
    if spec.get('glasses') == 'round':
        ctx.set_source_rgba(0.06, 0.05, 0.06, 1); ctx.set_line_width(hh*0.035)
        for sd in (-1, 1): ctx.arc(sd*esp + ox, ey, rx*0.3, 0, 2*math.pi); ctx.stroke()
        ctx.move_to(-esp + ox + rx*0.3, ey - ry*0.02); ctx.curve_to(ox - rx*0.05, ey - ry*0.1, ox + rx*0.05, ey - ry*0.1, esp + ox - rx*0.3, ey - ry*0.02); ctx.stroke()
        for sd in (-1, 1):
            ctx.arc(sd*esp + ox - rx*0.1, ey - ry*0.08, rx*0.07, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.fill()
    # hats
    if spec.get('hat') == 'flatcap':
        col = spec['hat_col']
        ctx.move_to(-rx*1.1, hc - ry*0.35); ctx.curve_to(-rx*1.15, hc - ry*1.3, rx*1.2, hc - ry*1.35, rx*1.12, hc - ry*0.4)
        ctx.curve_to(rx*0.5, hc - ry*0.52, -rx*0.5, hc - ry*0.5, -rx*1.1, hc - ry*0.35); ctx.close_path()
        shade(ctx, col, -rx, rx, 0.2, 0.25); ctx.fill_preserve(); outline(ctx, 2.4, 0.5)
        # brim toward facing side
        ctx.move_to(-rx*0.9 + f*rx*0.3, hc - ry*0.45); ctx.curve_to(f*rx*0.3, hc - ry*0.3, f*rx*1.1, hc - ry*0.32, f*rx*1.32, hc - ry*0.45)
        ctx.curve_to(f*rx*1.0, hc - ry*0.58, -rx*0.4 + f*rx*0.3, hc - ry*0.6, -rx*0.9 + f*rx*0.3, hc - ry*0.45); ctx.close_path()
        ctx.set_source_rgba(*hexc(dk(col, 0.3))); ctx.fill()
        ctx.move_to(-rx*0.7, hc - ry*0.95); ctx.curve_to(0, hc - ry*1.08, rx*0.4, hc - ry*1.05, rx*0.9, hc - ry*0.75); ctx.set_source_rgba(0, 0, 0, 0.2); ctx.set_line_width(3); ctx.stroke()
        ctx.arc(0, hc - ry*1.08, rx*0.07, 0, 2*math.pi); ctx.set_source_rgba(*hexc(dk(col, 0.35))); ctx.fill()
        # tweed dots
        for k in range(14):
            ctx.arc(-rx*0.8 + (k % 7)*rx*0.27, hc - ry*(0.62 + 0.22*(k//7)), 1.8, 0, 2*math.pi); ctx.set_source_rgba(1, 0.9, 0.7, 0.25); ctx.fill()
    elif spec.get('hat') == 'police':
        col = spec['hat_col']
        ctx.move_to(-rx*1.15, hc - ry*0.4); ctx.line_to(-rx*1.0, hc - ry*1.15); ctx.line_to(rx*1.05, hc - ry*1.2); ctx.line_to(rx*1.15, hc - ry*0.4); ctx.close_path()
        shade(ctx, col, -rx, rx); ctx.fill_preserve(); outline(ctx, 2, 0.5)
        ctx.rectangle(-rx*1.15, hc - ry*0.55, rx*2.3, ry*0.16); ctx.set_source_rgba(*hexc('#1a1a1a')); ctx.fill()
        ctx.arc(0, hc - ry*0.85, rx*0.16, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#d8a83a')); ctx.fill()
        ctx.move_to(-rx*1.0 + f*rx*0.3, hc - ry*0.4); ctx.line_to(f*rx*1.4, hc - ry*0.38); ctx.line_to(f*rx*1.1, hc - ry*0.5); ctx.close_path(); ctx.set_source_rgba(*hexc('#1a1a1a')); ctx.fill()

def human(ctx, x, y, s, spec, pose=None, t=0.0, shadow=True):
    pose = dict(pose or {}); pose.setdefault('face', 1)
    g = geo(spec); hh = g['hh']
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if shadow:
        ctx.save(); ctx.scale(1, 0.18); ctx.arc(0, 0, hh*1.3, 0, 2*math.pi); ctx.restore()
        ctx.set_source_rgba(0, 0, 0, 0.28); ctx.fill()
    breathe = 1 + 0.006*math.sin(t*2.1 + x*0.01)
    ctx.translate(0, 0); ctx.rotate(pose.get('lean', 0.0)); ctx.scale(1, 1)
    al, ar = pose.get('arm_l', 'down'), pose.get('arm_r', 'down')
    legs(ctx, spec, g, pose, t)
    ctx.save(); ctx.translate(0, g['hy']*(1 - breathe));
    torso(ctx, spec, g, pose, t)
    if spec['bottom'] == 'mundu': mundu(ctx, spec, g, pose, t)
    arm(ctx, spec, g, -1, al, pose, t)
    arm(ctx, spec, g, 1, ar, pose, t)
    ctx.save(); ctx.translate(0, hh*0.02*math.sin(t*1.7 + x*0.02)); ctx.rotate(pose.get('tilt', 0.0))
    head(ctx, spec, g, pose, t)
    ctx.restore(); ctx.restore(); ctx.restore()

def face_pos(x, y, s, spec):
    """world position of the face centre for camera close-ups."""
    g = geo(spec); return x, y + g['hc']*s, g['h']*s

if __name__ == '__main__':
    W, H = 2400, 1100
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#2a2a5a')); g.add_color_stop_rgba(1, *hexc('#14142e')); ctx.set_source(g); ctx.paint()
    poses = [(ARJUN, dict(arm_l='notebook', arm_r='write', expr='think')), (MEENU, dict(arm_l='chips', arm_r='eat', expr='smile', face=-1)),
             (RAVI, dict(arm_l='hip', expr='smug', face=-1)), (VELU, dict(arm_r='torch', expr='scared')), (SHANTHA, dict(arm_r='mop', expr='neutral', face=-1)),
             (FAIZAL, dict(arm_l='hip', expr='angry')), (POLICE, dict(expr='neutral', face=-1)), (ARJUN, dict(arm_r='point', arm_l='chin', expr='smug'))]
    for i, (sp, po) in enumerate(poses): human(ctx, 160 + i*295, 1040, 1.0, sp, po, 1.0)
    surf.write_to_png('/home/claude/det/chars_test.png')
