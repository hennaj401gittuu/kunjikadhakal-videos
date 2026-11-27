"""9:16 TRY IT Short for Kandupidi: the ring finger that won't lift.
Hand flat on a table, fold the MIDDLE finger under (knuckle on the table): thumb, index and little finger lift, the RING finger can't.
Why: the extensor tendons of the middle and ring fingers are linked by tendon bridges (juncturae tendinum); index and little finger
also have their own extra extensor muscles (extensor indicis, extensor digiti minimi), the ring finger has none.
Top-down pseudo-3D hand on a wooden table (hand()), x-ray tendons with bridges, 10 s countdown, reuses tryit_short.py room/kid/widgets.
python3 ring_short.py stills | render"""
import sys, math, os, random, cairo
sys.path.insert(0, '/home/claude/tryit'); sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/money')
import tryit_short as T
import wd
from wd import text, text_w, pill
from pz import clamp, prog, sprog, back, hexc, rrect, lerp, smooth
W, H = 1080, 1920
NAME = 'KP_The_Finger_You_Cant_Lift_Mini'
OUT = T.OUT
CD = 10.0
T.CD_LEN = CD
grad, otext, badge, tag, check, sparkles = T.grad, T.otext, T.badge, T.tag, T.check, T.sparkles

# ------------------------------------------------------------------ table
_bg = {}
def table():
    if 'table' in _bg: return _bg['table']
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source(grad(0, H, '#c98a52', '#8a5430')); c.paint()
    rnd = random.Random(3)
    for k in range(6):
        x = k*190 - 30
        c.rectangle(x, 0, 6, H); c.set_source_rgba(0.3, 0.15, 0.05, 0.35); c.fill()
        for j in range(18):
            yy = rnd.uniform(0, H); c.move_to(x + rnd.uniform(15, 175), yy)
            c.curve_to(x + rnd.uniform(10, 180), yy + 120, x + rnd.uniform(10, 180), yy + 260, x + rnd.uniform(10, 180), yy + 400)
            c.set_source_rgba(0.35, 0.18, 0.06, 0.12); c.set_line_width(rnd.uniform(2, 5)); c.stroke()
    # mug (top-right) and pencil (left) as props
    c.arc(905, 1640, 120, 0, 2*math.pi); c.set_source_rgba(0, 0, 0, 0.25); c.fill()
    c.arc(895, 1625, 115, 0, 2*math.pi); c.set_source(grad(1510, 1740, '#f2f2f2', '#c8c8d0')); c.fill()
    c.arc(895, 1625, 88, 0, 2*math.pi); c.set_source(grad(1540, 1710, '#6a3a1a', '#3a1e0a')); c.fill()
    c.save(); c.translate(130, 1600); c.rotate(-0.5)
    c.rectangle(-170, -14, 300, 28); c.set_source_rgba(*hexc('#ffc93a')); c.fill()
    c.move_to(130, -14); c.line_to(185, 0); c.line_to(130, 14); c.close_path(); c.set_source_rgba(*hexc('#f2d2a8')); c.fill()
    c.rectangle(-200, -14, 30, 28); c.set_source_rgba(*hexc('#ff7a8a')); c.fill(); c.restore()
    g = cairo.RadialGradient(540, 900, 100, 540, 900, 1200); g.add_color_stop_rgba(0, 1, 0.92, 0.75, 0.30); g.add_color_stop_rgba(1, 0, 0, 0, 0.45)
    c.set_source(g); c.paint()
    _bg['table'] = s; return s

# ------------------------------------------------------------------ hand (top view, right hand palm down)
FING = {  # name: (base x, base y, angle from vertical, length, width)
    'thumb': (-150, 70, -1.0, 215, 86),
    'index': (-122, -135, -0.13, 285, 76),
    'middle': (-40, -150, -0.04, 315, 80),
    'ring': (42, -145, 0.05, 295, 76),
    'pinky': (122, -118, 0.16, 225, 64),
}
SK0, SK1, SK2 = '#ffd9b8', '#f0b48a', '#c98260'

def capsule(ctx, x0, y0, x1, y1, w, c_mid, c_edge, alpha=1.0):
    nx, ny = (y1 - y0), -(x1 - x0); L = math.hypot(nx, ny) or 1; nx, ny = nx/L, ny/L
    g = cairo.LinearGradient(x0 - nx*w/2, y0 - ny*w/2, x0 + nx*w/2, y0 + ny*w/2)
    g.add_color_stop_rgba(0, *hexc(c_edge, alpha)); g.add_color_stop_rgba(0.45, *hexc(c_mid, alpha)); g.add_color_stop_rgba(1, *hexc(c_edge, alpha))
    ctx.set_source(g); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(w)
    ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()

def finger_pts(name, lift=0.0, fold=0.0, jit=0.0):
    bx, by, a, L, w = FING[name]
    Lv = L*(1 - 0.22*lift)*(1 - 0.68*fold)
    tx, ty = bx + math.sin(a)*Lv + jit, by - math.cos(a)*Lv - 10*lift
    return bx, by, tx, ty, w*(1 + 0.08*lift), a, Lv

def hand(ctx, x, y, s, t, lift=None, fold=0.0, tremble=0.0, xray=0.0, glow=None, alpha=1.0):
    """lift: dict finger->0..1 ; fold: middle finger folded under 0..1 ; tremble: ring finger strain ; xray 0..1 ; glow: finger to ring-highlight"""
    lift = lift or {}
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    jit = tremble*4*math.sin(t*55)
    # table shadows (always at full length on the table)
    for nm in FING:
        bx, by, a, L, w = FING[nm]
        Ls = L*(1 - 0.68*fold) if nm == 'middle' else L
        off = 10 + 22*lift.get(nm, 0)
        tx, ty = bx + math.sin(a)*Ls, by - math.cos(a)*Ls
        ctx.set_source_rgba(0, 0, 0, 0.22 - 0.08*lift.get(nm, 0)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(w + 8)
        ctx.move_to(bx + off, by + off); ctx.line_to(tx + off, ty + off); ctx.stroke()
    rrect(ctx, -178 + 16, -170 + 18, 356, 600, 120); ctx.set_source_rgba(0, 0, 0, 0.22); ctx.fill()
    ctx.push_group()
    # forearm + palm (back of hand)
    rrect(ctx, -150, 180, 300, 420, 60); ctx.set_source(grad(0, 0, SK2, SK1, -150, 150)); ctx.fill()
    rrect(ctx, -150, 330, 300, 270, 50); ctx.set_source(grad(0, 0, '#3f7fd0', '#24508f', -150, 150)); ctx.fill()   # sleeve
    rrect(ctx, -178, -170, 356, 420, 130); ctx.set_source(grad(0, 0, SK1, SK1, -178, 178))
    g = cairo.RadialGradient(-30, -40, 30, 0, 20, 260); g.add_color_stop_rgba(0, *hexc(SK0)); g.add_color_stop_rgba(1, *hexc(SK1)); ctx.set_source(g); ctx.fill()
    # fingers (thumb first, then index..pinky)
    order = ['thumb', 'index', 'ring', 'pinky', 'middle'] if fold > 0.5 else ['thumb', 'index', 'middle', 'ring', 'pinky']
    tips = {}
    for nm in order:
        lf = lift.get(nm, 0); fd = fold if nm == 'middle' else 0
        bx, by, tx, ty, w, a, Lv = finger_pts(nm, lf, fd, jit if nm == 'ring' else 0)
        tips[nm] = (tx, ty)
        light = '#ffe6cf' if lf > 0.3 else SK0
        capsule(ctx, bx, by, tx, ty, w, light, SK2 if fd < 0.5 else '#b87050')
        if fd < 0.6:
            # nail
            ctx.save(); ctx.translate(tx - math.sin(a)*w*0.25, ty + math.cos(a)*w*0.25); ctx.rotate(a)
            rrect(ctx, -w*0.27, -w*0.42, w*0.54, w*0.62, w*0.22); ctx.set_source(grad(-w*0.4, w*0.2, '#ffeef0', '#f2b9b4')); ctx.fill(); ctx.restore()
            # knuckle creases
            for q in (0.38, 0.66):
                kx, ky = lerp(bx, tx, q), lerp(by, ty, q)
                ctx.save(); ctx.translate(kx, ky); ctx.rotate(a)
                ctx.move_to(-w*0.22, 0); ctx.curve_to(-w*0.08, 5, w*0.08, 5, w*0.22, 0); ctx.set_source_rgba(*hexc(SK2, 0.7)); ctx.set_line_width(4); ctx.stroke(); ctx.restore()
        else:
            # folded knuckle bump
            ctx.save(); ctx.translate(tx, ty); ctx.rotate(a)
            g = cairo.RadialGradient(-8, -8, 5, 0, 0, w*0.62); g.add_color_stop_rgba(0, *hexc('#f6c49c')); g.add_color_stop_rgba(1, *hexc('#b87050'))
            ctx.set_source(g); ctx.arc(0, 0, w*0.6, 0, 2*math.pi); ctx.fill()
            ctx.restore()
    # knuckle bumps on the back of the hand
    for nm in ('index', 'middle', 'ring', 'pinky'):
        bx, by = FING[nm][0], FING[nm][1]
        g = cairo.RadialGradient(bx - 6, by + 18, 3, bx, by + 24, 34); g.add_color_stop_rgba(0, 1, 0.92, 0.85, 0.55); g.add_color_stop_rgba(1, 1, 0.9, 0.8, 0)
        ctx.set_source(g); ctx.arc(bx, by + 24, 34, 0, 2*math.pi); ctx.fill()
    pat = ctx.pop_group()
    if xray > 0:
        ctx.set_source(pat); ctx.paint_with_alpha(alpha*(1 - 0.6*xray))
        ctx.set_source_rgba(0.35, 0.6, 1.0, 0.35*xray); ctx.mask(pat)
    else:
        ctx.set_source(pat); ctx.paint_with_alpha(alpha)
    if glow:
        tx, ty = tips[glow]
        ctx.set_source_rgba(1, 0.25, 0.2, 0.9); ctx.set_line_width(10); ctx.arc(tx, ty + 40, 70 + 6*math.sin(t*8), 0, 2*math.pi); ctx.stroke()
    ctx.restore()
    return {k: (x + v[0]*s, y + v[1]*s) for k, v in tips.items()}

def tendons(ctx, x, y, s, t, p, fold=1.0, pull=0.0, bridge=0.0):
    """x-ray overlay: tendons from wrist to each finger + juncturae tendinum bridges"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    wrist = {'index': (-55, 520), 'middle': (-18, 520), 'ring': (18, 520), 'pinky': (55, 520)}
    pts = {}
    for nm in ('index', 'middle', 'ring', 'pinky'):
        bx, by, tx, ty, w, a, Lv = finger_pts(nm, 0, fold if nm == 'middle' else 0)
        wx, wy = wrist[nm]
        mid = (lerp(wx, bx, 0.7), lerp(wy, by, 0.85) + 40)
        pts[nm] = [(wx, wy), mid, (bx, by), (lerp(bx, tx, 0.85), lerp(by, ty, 0.85))]
        hot = nm == 'middle' and pull > 0
        col = (1, 0.35, 0.3) if hot else (1, 0.86, 0.25)
        for lw, al in ((26, 0.18), (12, 0.45), (5, 1.0)):
            ctx.set_line_width(lw); ctx.set_source_rgba(*col, al*p); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            P = pts[nm]; ctx.move_to(*P[0]); ctx.curve_to(P[1][0], P[1][1], P[1][0], P[1][1], P[2][0], P[2][1]); ctx.line_to(*P[3]); ctx.stroke()
    if bridge > 0:
        for (a_, b_, yy) in (('middle', 'ring', 40), ('ring', 'pinky', 70)):
            ya = yy; xa = lerp(pts[a_][1][0], pts[a_][2][0], 0.5); xb = lerp(pts[b_][1][0], pts[b_][2][0], 0.5)
            pul = 0.6 + 0.4*math.sin(t*6)
            g = cairo.RadialGradient((xa + xb)/2, ya, 4, (xa + xb)/2, ya, 90); g.add_color_stop_rgba(0, 1, 0.4, 0.8, 0.7*bridge*pul); g.add_color_stop_rgba(1, 1, 0.4, 0.8, 0)
            ctx.set_source(g); ctx.arc((xa + xb)/2, ya, 90, 0, 2*math.pi); ctx.fill()
            ctx.set_source_rgba(1, 0.5, 0.85, bridge); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(xa, ya + 20); ctx.line_to(xb, ya - 20); ctx.stroke()
    if pull > 0:
        # arrow along middle tendon pointing to the folded finger: pulled tight
        off = 20*math.sin(t*8)
        ctx.set_source_rgba(1, 0.3, 0.25, pull); ctx.set_line_width(10)
        ctx.move_to(-95, 330 - off); ctx.line_to(-95, 90 - off); ctx.stroke()
        ctx.move_to(-125, 120 - off); ctx.line_to(-95, 70 - off); ctx.line_to(-65, 120 - off); ctx.stroke()
    ctx.restore()

def xmark(ctx, x, y, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    ctx.arc(0, 0, 80, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#e8362c')); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(20); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(-32, -32); ctx.line_to(32, 32); ctx.move_to(32, -32); ctx.line_to(-32, 32); ctx.stroke(); ctx.restore()

def up_arrow(ctx, x, y, t, p, col='#2fc76a'):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y - 14*math.sin(t*6)); sc = back(p); ctx.scale(sc, sc)
    ctx.move_to(0, -70); ctx.line_to(50, -10); ctx.line_to(18, -10); ctx.line_to(18, 60); ctx.line_to(-18, 60); ctx.line_to(-18, -10); ctx.line_to(-50, -10); ctx.close_path()
    ctx.set_source_rgba(*hexc(col)); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(5); ctx.stroke(); ctx.restore()

def countdown(ctx, x, y, r, t, cd0, alpha=1.0, label=None):
    rem = clamp(CD - (t - cd0), 0, CD); frac = rem/CD
    col = '#2fd27a' if rem > 6 else ('#ffb52a' if rem > 3 else '#ff4a3c')
    pulse = 1 + 0.05*max(0, math.cos((t - cd0)*2*math.pi)) if 0 < rem < CD else 1
    ctx.save(); ctx.translate(x, y); ctx.scale(pulse, pulse)
    g = cairo.RadialGradient(0, 0, r*0.4, 0, 0, r*1.35); g.add_color_stop_rgba(0, *hexc(col, 0.35*alpha)); g.add_color_stop_rgba(1, *hexc(col, 0))
    ctx.set_source(g); ctx.arc(0, 0, r*1.35, 0, 2*math.pi); ctx.fill()
    ctx.arc(0, 0, r, 0, 2*math.pi); ctx.set_source_rgba(0.08, 0.08, 0.2, 0.85*alpha); ctx.fill()
    ctx.set_line_width(r*0.16); ctx.set_source_rgba(1, 1, 1, 0.15*alpha); ctx.arc(0, 0, r*0.86, 0, 2*math.pi); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc(col, alpha))
    if frac > 0.001: ctx.new_path(); ctx.arc(0, 0, r*0.86, -math.pi/2, -math.pi/2 + 2*math.pi*frac); ctx.stroke()
    n = int(math.ceil(rem)) if rem > 0 else 0
    text(ctx, str(n), 0, r*0.3, r*0.85, '#ffffff', alpha=alpha)
    if label: text(ctx, label, 0, r*0.62, r*0.17, '#ffffff', alpha=0.8*alpha)
    ctx.restore()

def sweat(ctx, x, y, t):
    yy = y + (t*80) % 60
    ctx.move_to(x, yy - 40); ctx.curve_to(x + 26, yy, x + 22, yy + 26, x, yy + 26); ctx.curve_to(x - 22, yy + 26, x - 26, yy, x, yy - 40)
    ctx.set_source_rgba(0.55, 0.85, 1, 0.9); ctx.fill()

# ------------------------------------------------------------------ beats
COL_O, COL_G, COL_B, COL_R, COL_Y = T.COL_O, T.COL_G, T.COL_B, T.COL_R, T.COL_Y
BEATS = [
 dict(id='h1', sc='hook', ml='ഈ വിരൽ നിങ്ങൾക്ക് പൊക്കാൻ പറ്റില്ല! എന്റെ കൂടെ ചെയ്തു നോക്കൂ!', l1="You CAN'T lift", l2='this finger – try it!', col=COL_O),
 dict(id='s1', sc='flat', ml='സ്റ്റെപ്പ് ഒന്ന്. കൈപ്പത്തി ഒരു മേശയിൽ, നിവർത്തി വെക്കൂ.', l1='STEP 1: put your hand', l2='FLAT on a table', col=COL_G, badge='STEP 1'),
 dict(id='s2', sc='fold', ml='സ്റ്റെപ്പ് രണ്ട്. നടുവിരൽ മാത്രം താഴേക്ക് മടക്കി, മേശയിൽ കുത്തി വെക്കൂ.', l1='STEP 2: fold your', l2='MIDDLE finger under', col=COL_B, badge='STEP 2'),
 dict(id='t1', sc='lift', f='thumb', ml='ഇനി തള്ളവിരൽ പൊക്കി നോക്കൂ. എളുപ്പം, അല്ലേ?', l1='Lift your THUMB –', l2='easy, right?', col=COL_G),
 dict(id='t2', sc='lift', f='index', ml='ചൂണ്ടുവിരൽ പൊക്കൂ. അതും പൊങ്ങും.', l1='Now your INDEX finger –', l2='it lifts too!', col=COL_G),
 dict(id='t3', sc='lift', f='pinky', ml='ചെറുവിരലും പൊക്കി നോക്കൂ. ശരി!', l1='Your LITTLE finger?', l2='No problem!', col=COL_G),
 dict(id='r1', sc='ring', ml='ഇനി, മോതിരവിരൽ പൊക്കൂ! പത്തു സെക്കൻഡ് തരാം. തുടങ്ങൂ!', l1='STEP 3: lift your', l2='RING FINGER – GO!', col=COL_R, badge='STEP 3', cd=True),
 dict(id='c1', sc='bigcd', at=0.2, ml='പൊക്കൂ, പൊക്കൂ! ശക്തിയായി ശ്രമിക്കൂ!', l1='Lift it! Lift it!', l2='TRY HARDER!', col=COL_O),
 dict(id='c2', sc='kid', ml='പറ്റുന്നില്ല, അല്ലേ? വിരൽ മേശയിൽ ഒട്ടിപ്പിടിച്ചതു പോലെ!', l1="Can't do it?", l2="It's GLUED to the table!", col=COL_Y),
 dict(id='c3', sc='ring', at=6.6, ml='മൂന്ന്, രണ്ട്, ഒന്ന്! സമയം കഴിഞ്ഞു!', l1="Time's up!", l2='STUCK, right?', col=COL_R, stuck=True),
 dict(id='x1', sc='xray', ml='കാരണം ഇതാണ്. ഓരോ വിരലിനെയും പൊക്കുന്നത്, കൈയുടെ പുറത്തുള്ള ഓരോ ടെൻഡൻ ആണ്.', l1='Each finger is lifted', l2='by a TENDON', col=COL_Y),
 dict(id='x2', sc='xray', bridge=True, ml='നടുവിരലിന്റെയും മോതിരവിരലിന്റെയും ടെൻഡനുകൾ, ഒരു ചെറിയ പാലം കൊണ്ട് ചേർന്നിരിക്കുന്നു.', l1='Middle and ring tendons', l2='are joined by a BRIDGE', col=COL_B),
 dict(id='x3', sc='xray', bridge=True, pull=True, ml='നടുവിരൽ മടക്കുമ്പോൾ, ആ പാലം മോതിരവിരലിനെയും പിടിച്ചു വെക്കുന്നു.', l1='Middle finger folded =', l2='ring finger LOCKED', col=COL_R),
 dict(id='x4', sc='own', ml='ചൂണ്ടുവിരലിനും ചെറുവിരലിനും, സ്വന്തമായി ഒരു പേശി കൂടി ഉണ്ട്. മോതിരവിരലിന് അതില്ല!', l1='Index and little finger have', l2='their OWN extra muscle', col=COL_G),
 dict(id='n1', sc='name', ml='ഈ ടെൻഡൻ പാലങ്ങളുടെ പേരാണ്, ജങ്ചൂറേ ടെൻഡിനം.', l1='These bridges are called', l2='JUNCTURAE TENDINUM', col=COL_Y),
 dict(id='n2', sc='free', ml='ഇനി നടുവിരൽ നിവർത്തി നോക്കൂ. മോതിരവിരൽ എളുപ്പം പൊങ്ങും!', l1='Straighten the middle finger:', l2='the ring finger is FREE!', col=COL_G),
 dict(id='e1', sc='end1', ml='നിങ്ങളുടെ വിരൽ പൊങ്ങിയോ? കമന്റിൽ പറയൂ!', l1='Did yours lift?', l2='Tell me in the comments!', col=COL_G),
 dict(id='e2', sc='share', ml='ഇത് ഒരു കൂട്ടുകാരന് അയച്ചു കൊടുക്കൂ, അവരും തോൽക്കും!', l1='Send this to a friend', l2='and watch them TRY!', col=COL_O),
 dict(id='e3', sc='follow', ml='കൂടുതൽ രഹസ്യങ്ങൾക്ക്, ഫോളോ ചെയ്യൂ!', l1='Follow for more', l2='MYSTERIES!', col=COL_Y, post=1.4),
]

HX, HY, HS = 540, 1130, 1.3   # hand placement on the table close-up

def draw_factory(tl):
    cd0 = tl.cd0
    def draw(ctx, t):
        i = 0
        for j, b in enumerate(tl.beats):
            if t >= b['t0'] - 0.12: i = j
        b = tl.beats[i]; t0, t1 = b['t0'], b['t1']; sc = b['sc']
        z = 1.0 + 0.07*(1 - sprog(t, t0 - 0.12, 0.35)) + 0.025*prog(t, t0, max(1, t1 - t0 + 0.5))
        ctx.save(); ctx.translate(W/2, H*0.5); ctx.scale(z, z); ctx.translate(-W/2, -H*0.5)
        trying = cd0 is not None and cd0 <= t <= cd0 + CD
        if sc == 'hook':
            ctx.set_source_surface(table()); ctx.paint()
            tips = hand(ctx, HX, HY, HS, t, fold=1.0, tremble=0.8, glow='ring', lift={'thumb': 0.5 + 0.5*math.sin(t*5), 'index': 0.5 + 0.5*math.sin(t*5 + 2), 'pinky': 0.5 + 0.5*math.sin(t*5 + 4)})
            for k, (qx, qy) in enumerate(((160, 560), (920, 600))):
                otext(ctx, '?', qx, qy + 14*math.sin(t*4 + k), 150, '#ffd23f', alpha=prog(t, t0 + 0.3 + k*0.15, 0.2))
            pill(ctx, 540, 1430, 560, 110, '#e2362c', '99% CAN\'T DO IT', size=56, p=prog(t, t0 + 0.6, 0.3))
        elif sc in ('flat', 'fold', 'lift', 'ring', 'free'):
            ctx.set_source_surface(table()); ctx.paint()
            fold = 0.0; lift = {}; glow = None; trem = 0.0
            if sc == 'flat':
                yy = lerp(1500, HY, sprog(t, t0, 0.9)); tips = hand(ctx, HX, yy, HS, t)
            else:
                if sc == 'fold': fold = sprog(t, t0 + 0.8, 1.0)
                else: fold = 1.0
                if sc == 'lift':
                    f = b['f']; lift[f] = sprog(t, t0 + 0.4, 0.5) * (0.85 + 0.15*math.sin(t*6))
                if sc == 'ring':
                    glow = 'ring'; trem = 1.0 if trying or b.get('stuck') else 0.0
                    lift['ring'] = 0.06*abs(math.sin(t*7)) if trem else 0
                if sc == 'free':
                    fold = 1 - sprog(t, t0 + 0.5, 0.8); lift['ring'] = sprog(t, t0 + 1.6, 0.6)*(0.85 + 0.15*math.sin(t*6))
                tips = hand(ctx, HX, HY, HS, t, fold=fold, lift=lift, glow=glow, tremble=trem)
            if b.get('badge'):
                badge(ctx, 540, 470, b['badge'], prog(t, t0 + 0.2, 0.35), col='#2fa86a' if b['badge'] != 'STEP 3' else '#e2362c')
            if sc == 'fold':
                mx, my = tips['middle']; p = prog(t, t0 + 1.8, 0.3)
                tag(ctx, 540, 1430, 'KNUCKLE ON THE TABLE', p, col='#ffd23f', size=44)
                if p > 0:
                    ctx.set_source_rgba(1, 0.85, 0.2, p); ctx.set_line_width(10); ctx.arc(mx, my, 75 + 6*math.sin(t*8), 0, 2*math.pi); ctx.stroke()
            if sc == 'lift':
                fx, fy = tips[b['f']]
                up_arrow(ctx, fx, fy - 120, t, prog(t, t0 + 0.6, 0.3))
                check(ctx, 860 if b['f'] != 'pinky' else 220, 1400, prog(t, t0 + 1.0, 0.35))
            if sc == 'ring':
                rx, ry = tips['ring']
                if trying or b.get('stuck'):
                    tag(ctx, rx + 60, ry - 100, 'LIFT!', 0.6 + 0.4*abs(math.sin(t*5)), col='#ff4a4a', size=56)
                if b.get('stuck'):
                    xmark(ctx, 860, 1400, prog(t, t0 + 1.2, 0.35))
                    pill(ctx, 420, 1400, 420, 110, '#e2362c', 'STUCK!', size=64, p=prog(t, t0 + 1.4, 0.3))
            if sc == 'free':
                rx, ry = tips['ring']
                up_arrow(ctx, rx + 120, ry, t, prog(t, t0 + 1.8, 0.3))
                check(ctx, 860, 1400, prog(t, t0 + 2.2, 0.35))
                sparkles(ctx, t, n=10, ymin=500, ymax=1300)
        elif sc == 'bigcd':
            ctx.set_source_surface(table()); ctx.paint(); ctx.set_source_rgba(0.05, 0.04, 0.15, 0.45); ctx.paint()
            hand(ctx, 540, 1250, 0.75, t, fold=1.0, tremble=1.0, glow='ring', lift={'ring': 0.06*abs(math.sin(t*7))})
            countdown(ctx, 540, 720, 230, t, cd0 if t >= cd0 else t, label='SECONDS')
        elif sc in ('kid', 'end1', 'share'):
            ctx.set_source_surface(T.room()); ctx.paint(); T.vignette(ctx, 0.3)
            mood = 'effort' if sc == 'kid' else ('wow' if sc == 'end1' else 'smile')
            T.kid(ctx, 540, T.FEET, 1.0, t, aR=0.35 if sc != 'share' else 0.9 + 0.2*math.sin(t*4), aL=0.12, mood=mood)
            if sc == 'kid':
                sweat(ctx, 760, 620, t)
                tag(ctx, 830, 1080, 'STUCK!', prog(t, t0 + 0.5, 0.3), col='#ffffff', bg='#e2362c', size=56)
                hand(ctx, 230, 1180, 0.42, t, fold=1.0, tremble=1.0, glow='ring')
                countdown(ctx, 930, 520, 85, t, cd0)
            if sc == 'end1':
                T.comment_box(ctx, 480, "IT'S STUCK!", t, t0)
            if sc == 'share':
                for k, x in enumerate((210, 870)): otext(ctx, 'HA', x, 620 + 10*math.sin(t*6 + k), 90, '#ffd23f', alpha=prog(t, t0 + 0.3 + 0.2*k, 0.2))
                tag(ctx, 540, 500, 'SEND TO A FRIEND', prog(t, t0 + 0.2, 0.3), col='#ffffff', bg='#ff7a2a', size=50)
        elif sc in ('xray', 'own'):
            ctx.set_source_rgba(*hexc('#0d1030')); ctx.paint()
            g = cairo.RadialGradient(540, 900, 50, 540, 900, 1000); g.add_color_stop_rgba(0, 0.2, 0.2, 0.5, 1); g.add_color_stop_rgba(1, 0.05, 0.05, 0.15, 1)
            ctx.set_source(g); ctx.paint()
            for k in range(0, W, 60): ctx.rectangle(k, 0, 2, H); ctx.set_source_rgba(0.4, 0.6, 1, 0.06); ctx.fill()
            for k in range(0, H, 60): ctx.rectangle(0, k, W, 2); ctx.set_source_rgba(0.4, 0.6, 1, 0.06); ctx.fill()
            s_ = 1.15; hy_ = 1060
            tips = hand(ctx, 540, hy_, s_, t, fold=1.0, xray=1.0, tremble=0.6 if b.get('pull') else 0)
            if sc == 'xray':
                tendons(ctx, 540, hy_, s_, t, sprog(t, t0 + 0.2, 0.8), fold=1.0, pull=prog(t, t0 + 0.5, 0.3) if b.get('pull') else 0,
                        bridge=prog(t, t0 + 0.6, 0.4) if b.get('bridge') else 0)
                if not b.get('pull'): tag(ctx, 200, 1430, 'TENDONS', prog(t, t0 + 0.4, 0.3), col='#ffd23f', size=44)
                if b.get('bridge'):
                    tag(ctx, 830, 1000, 'BRIDGE', prog(t, t0 + 0.8, 0.3), col='#ff8fd0', size=48)
                    ctx.set_source_rgba(1, 0.55, 0.85, 0.7*prog(t, t0 + 0.8, 0.3)); ctx.set_line_width(4)
                    ctx.move_to(760, 1000); ctx.line_to(540 + 30*s_, hy_ + 50*s_); ctx.stroke()
                if b.get('pull'):
                    tag(ctx, 230, 1400, 'PULLED TIGHT', prog(t, t0 + 0.6, 0.3), col='#ff6a5a', size=40)
                    rx, ry = tips['ring']; xmark(ctx, rx + 150, ry + 60, prog(t, t0 + 1.4, 0.35))
            else:
                tendons(ctx, 540, hy_, s_, t, 1.0, fold=1.0, bridge=1.0)
                for nm, ok, (lx, ly) in (('index', True, (175, 760)), ('pinky', True, (905, 760)), ('ring', False, (720, 1420))):
                    p = prog(t, t0 + (0.5 if nm == 'index' else 1.3 if nm == 'pinky' else 2.6), 0.35)
                    bx_, by_ = 540 + FING[nm][0]*s_, hy_ + FING[nm][1]*s_
                    if p > 0:
                        ctx.set_source_rgba(1, 1, 1, 0.6*p); ctx.set_line_width(4); ctx.move_to(lx, ly + (40 if ok else -30)); ctx.line_to(bx_, by_ + 40); ctx.stroke()
                    tag(ctx, lx, ly, 'OWN MUSCLE' if ok else 'NO EXTRA MUSCLE', p, col='#3fe08a' if ok else '#ff4a4a', size=36)
                    if ok: check(ctx, lx, ly - 120, p*0.6)
                    else: xmark(ctx, 720, 1300 - 10, p*0.6)
        elif sc == 'name':
            ctx.set_source_rgba(*hexc('#12103a')); ctx.paint()
            ctx.save(); ctx.translate(540, 900); ctx.rotate(t*0.2)
            for k in range(16):
                ctx.move_to(0, 0); ctx.arc(0, 0, 1600, k*2*math.pi/16, (k + 0.5)*2*math.pi/16); ctx.close_path(); ctx.set_source_rgba(0.35, 0.3, 0.9, 0.18); ctx.fill()
            ctx.restore()
            hand(ctx, 540, 640, 0.6*back(prog(t, t0, 0.4)) + 0.001, t, fold=1.0, xray=1.0)
            tendons(ctx, 540, 640, 0.6*back(prog(t, t0, 0.4)) + 0.001, t, 1.0, bridge=1.0)
            p = back(prog(t, t0 + 0.6, 0.4))
            if p > 0:
                ctx.save(); ctx.translate(540, 1080); ctx.scale(p, p)
                otext(ctx, 'JUNCTURAE', 0, 0, 120, '#ffd23f', lw=18)
                otext(ctx, 'TENDINUM', 0, 135, 120, '#ffffff', lw=18)
                ctx.restore()
            tag(ctx, 540, 1350, 'the tendon bridges of your hand', prog(t, t0 + 1.4, 0.3), col='#ffffff', bg='#2a2a6a', size=38)
            sparkles(ctx, t, n=16, ymin=450, ymax=1400)
        elif sc == 'follow':
            ctx.set_source(grad(0, H, '#1a1440', '#3a1a5a')); ctx.paint()
            sparkles(ctx, t, n=18, ymin=420, ymax=1400, col=(0.9, 0.8, 1))
            T.brain(ctx, 540, 640 + 10*math.sin(t*3), 0.9, t)
            T.follow_btn(ctx, 540, 960, t, following=(t - t0) > 2.4)
            T.hand_tap(ctx, 540, 960, t, t0 + 1.8)
            otext(ctx, 'NEW TRICKS EVERY DAY', 540, 1180, 56, '#ffd23f', alpha=prog(t, t0 + 0.5, 0.3))
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and i: ctx.set_source_rgba(1, 1, 1, 0.22*fl); ctx.paint()
        g = cairo.LinearGradient(0, 0, 0, 420); g.add_color_stop_rgba(0, 0, 0, 0, 0.5); g.add_color_stop_rgba(1, 0, 0, 0, 0)
        ctx.set_source(g); ctx.rectangle(0, 0, W, 420); ctx.fill()
        T.caption2(ctx, b['l1'], b['l2'], b['col'], t, t0, t1)
        if trying and sc in ('ring',):
            countdown(ctx, 930, 520, 85, t, cd0)
    return draw

def sfx_list(tl):
    sfx = []; cd0 = tl.cd0
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0'] - 0.12, 'whoosh', 0.5))
        if b['id'] == 'h1': sfx.append((b['t0'] + 0.6, 'pop', 0.7))
        if b.get('badge'): sfx.append((b['t0'] + 0.2, 'pop', 0.7))
        if b['sc'] == 'lift': sfx.append((b['t0'] + 1.0, 'right', 0.45))
        if b.get('stuck'): sfx.append((b['t0'] + 1.2, 'wrong', 0.6))
        if b['sc'] in ('xray', 'name', 'own'): sfx.append((b['t0'] + 0.5, 'pop', 0.5))
        if b['sc'] == 'free': sfx.append((b['t0'] + 2.2, 'right', 0.6))
        if b['sc'] == 'end1':
            for k in range(8): sfx.append((b['t0'] + 0.35 + k*0.15, 'tick', 0.25))
        if b['sc'] == 'follow': sfx.append((b['t0'] + 2.4, 'pop', 0.6))
    for k in range(int(CD)):
        sfx.append((cd0 + k, 'tick', 0.25 if k < 7 else 0.45))
    return sfx

if __name__ == '__main__':
    tl = T.TL(BEATS)
    total = tl.end + 0.4
    draw = draw_factory(tl)
    print('TOTAL', round(total, 1), 'cd0', round(tl.cd0, 1))
    for b in tl.beats: print(b['id'], round(b['t0'], 1), round(b['t1'], 1))
    if 'stills' in sys.argv:
        k = 0
        for b in tl.beats:
            for tt in ((b['t0'] + b['t1'])/2 + 0.4,):
                surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt)
                surf.write_to_png(f'{OUT}/r{k:02d}.png'); k += 1
    else:
        aud = f'{OUT}/{NAME}.wav'; T.build_mix(aud, tl, sfx_list(tl), total)
        wd.render_raw(f'{OUT}/{NAME}.mp4', total, draw, aud)
