"""9:16 STORY RIDDLE Short (lateral thinking, flat vector Kerala style) for Kandupidi.
Riddle (beard_short): Rahim shaves 20+ times a day but has a long beard he has not cut for 10 years (ANSWER: he is a barber - he shaves customers).
Generalised: bank bg -> 'stage' (Best Beard contest), form rows / chips / no-sign labels / count scene taken from BEATS.
python3 riddle_short.py stills | render"""
import sys, math, os, random, subprocess, cairo
sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/money'); sys.path.insert(0, '/home/claude/ml')
import money as M
import wd
wd.W, wd.H = 1080, 1920; M.W, M.H = 1080, 1920
from wd import text, text_w, caption, pill
from pz import Timeline, clamp, prog, sprog, back, hexc, rrect, sfx2, SR, A, lerp
import money_short as MS
import numpy as np
W, H = 1080, 1920
GROUND = 1100
STORY = ('male', 0.88, 1.27)
OUT = '/home/claude/money/outs_b'; os.makedirs(OUT, exist_ok=True)
NAME = 'KP_20_Shaves_a_Day_Still_a_Beard_Mini'

# flat look: soft shadow instead of paper offset
def flat(ctx, col, dx=0, dy=6, lw=0):
    ctx.save(); ctx.translate(dx, dy); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.fill_preserve(); ctx.restore()
    ctx.set_source_rgba(*hexc(col)); ctx.fill()
M.paper = flat
MS.paper = flat

def grad(ctx, y0, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgba(0, *hexc(c0)); g.add_color_stop_rgba(1, *hexc(c1)); return g

def palm(ctx, x, y, s, col='#1f5a3a', sway=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgba(*hexc('#7a5230')); ctx.set_line_width(22); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0, 0); ctx.curve_to(10, -150, 30, -300, 50+sway*10, -420); ctx.stroke()
    ctx.translate(50+sway*10, -420)
    for k in range(8):
        a = -math.pi/2 + (k-3.5)*0.45 + sway*0.05
        ctx.move_to(0, 0); ctx.curve_to(math.cos(a)*90, math.sin(a)*70-20, math.cos(a)*170, math.sin(a)*90+20, math.cos(a)*210, math.sin(a)*80+90)
        ctx.curve_to(math.cos(a)*150, math.sin(a)*80+20, math.cos(a)*80, math.sin(a)*50, 0, 10); ctx.close_path()
        ctx.set_source_rgba(*hexc(col)); ctx.fill()
    for k in range(3): ctx.arc(-14+k*14, 12, 13, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#5a3a1a')); ctx.fill()
    ctx.restore()

def bokeh(ctx, t, n=26, seed=3, col=(1, 0.95, 0.8), ymax=1000):
    rnd = random.Random(seed)
    for k in range(n):
        x = rnd.uniform(0, W); y = rnd.uniform(80, ymax); r = rnd.uniform(10, 34); ph = rnd.uniform(0, 6)
        ctx.arc(x + 20*math.sin(t*0.4+ph), y + 14*math.cos(t*0.5+ph), r, 0, 2*math.pi)
        ctx.set_source_rgba(*col, 0.10 + 0.08*math.sin(t*2+ph)); ctx.fill()

def sunburst(ctx, cx, cy, t, c0='#ffcf5a', c1='#ff9a3c', n=18, a=1.0):
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(t*0.25)
    for k in range(n):
        ctx.move_to(0, 0); ctx.arc(0, 0, 2000, k*2*math.pi/n, (k+0.5)*2*math.pi/n); ctx.close_path()
        ctx.set_source_rgba(*hexc(c0 if k % 2 else c1, a)); ctx.fill()
    ctx.restore()

_bg = {}
def bg(kind):
    if kind in _bg: return _bg[kind]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    if kind in ('road', 'night'):
        night = kind == 'night'
        ctx.set_source(grad(ctx, 0, 1000, '#0d1440' if night else '#ff8a4c', '#3b2a6a' if night else '#ffd38a')); ctx.paint()
        if night:
            rnd = random.Random(5)
            for k in range(90): ctx.arc(rnd.uniform(0, W), rnd.uniform(0, 900), rnd.uniform(1.5, 3.8), 0, 2*math.pi); ctx.set_source_rgba(1, 1, .9, rnd.uniform(.3, .9)); ctx.fill()
            ctx.arc(820, 260, 80, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#f6f1d0')); ctx.fill()
        else:
            g = cairo.RadialGradient(540, 760, 40, 540, 760, 520); g.add_color_stop_rgba(0, 1, 0.97, 0.8, 0.9); g.add_color_stop_rgba(1, 1, 0.8, 0.5, 0)
            ctx.set_source(g); ctx.paint()
            ctx.arc(540, 760, 150, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#fff2c4')); ctx.fill()
        for k, (y0, col) in enumerate(((800, '#2f6d5e' if not night else '#1b2c4a'), (860, '#245a4e' if not night else '#142340'))):
            ctx.move_to(0, H)
            for xx in range(0, W+40, 40): ctx.line_to(xx, y0 + 35*math.sin(xx/200 + k*2))
            ctx.line_to(W, H); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
        ctx.rectangle(0, 940, W, H); ctx.set_source(grad(ctx, 940, 1500, '#3d8a4a' if not night else '#12301f', '#2a6a38' if not night else '#0a1f14')); ctx.fill()
        ctx.move_to(470, 940); ctx.line_to(610, 940); ctx.line_to(1000, H); ctx.line_to(80, H); ctx.close_path(); ctx.set_source_rgba(*hexc('#4a4a55' if not night else '#22222c')); ctx.fill()
        for k in range(6):
            y = 960 + k*k*28; ctx.rectangle(533 - k*4, y, 14 + k*8, 18 + k*6); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.fill()
        col = '#1d4a30' if not night else '#081a10'
        for (x, y, s) in ((60, 1010, 1.2), (220, 960, 0.75), (900, 990, 1.1), (1040, 1060, 1.3), (760, 950, 0.6)): palm(ctx, x, y, s, col)
    elif kind == 'bank':
        ctx.set_source(grad(ctx, 0, H, '#d9ecf2', '#a9d2de')); ctx.paint()
        for k in range(5): ctx.rectangle(0, 120 + k*190, W, 8); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.fill()
        # window with palms outside
        rrect(ctx, 640, 380, 360, 300, 16); ctx.set_source(grad(ctx, 380, 680, '#ffb36b', '#ffe2a8')); ctx.fill()
        palm(ctx, 760, 690, 0.55, '#2c6a44')
        ctx.set_source_rgba(*hexc('#ffffff')); ctx.set_line_width(14); rrect(ctx, 640, 380, 360, 300, 16); ctx.stroke()
        ctx.move_to(820, 380); ctx.line_to(820, 680); ctx.stroke()
        # bank board
        rrect(ctx, 80, 120, 920, 120, 20); ctx.set_source(grad(ctx, 120, 240, '#c2307a', '#8a1a56')); ctx.fill()
        text(ctx, 'BEST BEARD CONTEST', W/2, 202, 62, '#ffffff')
        for k in range(9):
            ctx.move_to(80 + k*115, 250); ctx.line_to(137 + k*115, 250); ctx.line_to(108 + k*115, 310); ctx.close_path()
            ctx.set_source_rgba(*hexc(('#ffd23f', '#2fa86a', '#1f4fa8')[k % 3])); ctx.fill()
        # wall clock + plant
        ctx.arc(200, 480, 70, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.set_source_rgba(*hexc('#2b2622')); ctx.set_line_width(8); ctx.arc(200, 480, 70, 0, 2*math.pi); ctx.stroke()
        ctx.move_to(200, 480); ctx.line_to(200, 435); ctx.stroke(); ctx.move_to(200, 480); ctx.line_to(235, 490); ctx.stroke()
        # floor
        ctx.rectangle(0, GROUND-20, W, H); ctx.set_source(grad(ctx, GROUND, H, '#c79a6a', '#a87a4e')); ctx.fill()
    elif kind == 'dark':
        ctx.set_source(grad(ctx, 0, H, '#1a1440', '#3a1a5a')); ctx.paint()
    _bg[kind] = surf
    return surf

def counter(ctx):
    rrect(ctx, 520, GROUND-330, 560, 330, 16); ctx.set_source(grad(ctx, GROUND-330, GROUND, '#8a5a34', '#6a4224')); ctx.fill()
    rrect(ctx, 500, GROUND-350, 600, 40, 10); ctx.set_source_rgba(*hexc('#b07a4a')); ctx.fill()
    rrect(ctx, 600, GROUND-280, 240, 70, 12); ctx.set_source_rgba(*hexc('#f4e7c8')); ctx.fill()
    text(ctx, 'JUDGE', 720, GROUND-230, 44, '#6a4224')

def cheeks(ctx, x, y, s, face):
    hy = y + (-430 + 16)*s
    for ex in (-36, 36):
        ctx.arc(x + (ex + face*10)*s, hy, 13*s, 0, 2*math.pi); ctx.set_source_rgba(1, 0.45, 0.45, 0.45); ctx.fill()

def beard(ctx, x, y, s, face, t):
    """long thick beard drawn over M.person's head (same transform as person)."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.translate(0, 3*math.sin(t*3 + x))
    hy = -430; fx = face*8
    ctx.move_to(-62, hy+2); ctx.curve_to(-66, hy+70, -50, hy+170, fx, hy+215)
    ctx.curve_to(50, hy+170, 66, hy+70, 62, hy+2)
    ctx.curve_to(50, hy+40, 30, hy+30, 20+fx, hy+30); ctx.curve_to(10+fx, hy+48, -10+fx, hy+48, -20+fx, hy+30)
    ctx.curve_to(-30, hy+30, -50, hy+40, -62, hy+2); ctx.close_path()
    ctx.set_source_rgba(*hexc('#1d140f')); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.12); ctx.set_line_width(4)
    for k in range(-2, 3):
        ctx.move_to(k*18, hy+60); ctx.curve_to(k*20, hy+110, k*14, hy+150, k*8 + fx, hy+190); ctx.stroke()
    ctx.move_to(-22+fx, hy+28); ctx.curve_to(-8+fx, hy+20, 8+fx, hy+20, 22+fx, hy+28); ctx.set_source_rgba(*hexc('#2b1d14')); ctx.set_line_width(12); ctx.stroke()
    ctx.restore()

def form(ctx, x, y, p, rows, t, t0):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc); ctx.rotate(-0.03)
    rrect(ctx, -330, -230, 660, 460, 20); ctx.set_source_rgba(0, 0, 0, 0.2); ctx.fill()
    rrect(ctx, -340, -240, 660, 460, 20); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    rrect(ctx, -340, -240, 660, 90, 20); ctx.set_source_rgba(*hexc('#1f4fa8')); ctx.fill()
    text(ctx, 'ENTRY CARD', -10, -175, 50, '#ffffff')
    for i, (lab, val, tv) in enumerate(rows):
        yy = -70 + i*110
        text(ctx, lab, -300, yy, 40, '#555555', align='l')
        ctx.rectangle(-300, yy+22, 580, 4); ctx.set_source_rgba(0.75, 0.75, 0.75, 1); ctx.fill()
        if val and t >= t0 + tv:
            n = int(clamp((t - t0 - tv)/0.4)*len(val))
            text(ctx, val[:n], 260, yy, 52, '#d9283b', align='r')
    ctx.restore()

def chip(ctx, x, y, label, p, col='#1f4fa8', size=62):
    if p <= 0: return
    w = text_w(ctx, label, size) + 80
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    rrect(ctx, -w/2, -size*0.95+8, w, size*1.9, 26); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.fill()
    rrect(ctx, -w/2, -size*0.95, w, size*1.9, 26); ctx.set_source(grad(ctx, -size, size, col, '#0c2050' if col == '#1f4fa8' else col)); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(6); rrect(ctx, -w/2+8, -size*0.95+8, w-16, size*1.9-16, 20); ctx.stroke()
    text(ctx, label, 0, size*0.36, size, '#ffffff'); ctx.restore()

def nosign(ctx, x, y, r, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = 1 + 0.8*(1 - clamp(p*1.4)); ctx.scale(sc, sc)
    ctx.set_source_rgba(*hexc('#e62117', clamp(p*2))); ctx.set_line_width(22)
    ctx.arc(0, 0, r, 0, 2*math.pi); ctx.stroke()
    ctx.move_to(-r*0.7, -r*0.7); ctx.line_to(r*0.7, r*0.7); ctx.stroke(); ctx.restore()

def cake(ctx, x, y, s, n, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -120, -110, 240, 110, 18); ctx.set_source_rgba(*hexc('#f7b6c8')); ctx.fill()
    rrect(ctx, -120, -110, 240, 34, 14); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.rectangle(-150, -6, 300, 14); ctx.set_source_rgba(*hexc('#dddddd')); ctx.fill()
    text(ctx, str(n), 0, -30, 50, '#d9283b')
    for k in range(3):
        cx = -50 + k*50; ctx.rectangle(cx-6, -170, 12, 60); ctx.set_source_rgba(*hexc('#5aa0f0')); ctx.fill()
        fl = 1 + 0.15*math.sin(t*14 + k)
        ctx.save(); ctx.translate(cx, -185); ctx.scale(1, fl); ctx.arc(0, 0, 12, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(*hexc('#ffb52a')); ctx.fill()
    ctx.restore()

def brain(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y + 8*math.sin(t*3)); ctx.scale(s, s)
    for (dx, dy, r) in ((-60, -20, 70), (0, -50, 75), (60, -20, 70), (-40, 30, 65), (40, 30, 65)):
        ctx.new_sub_path(); ctx.arc(dx, dy, r, 0, 2*math.pi)
    ctx.set_source_rgba(*hexc('#ff8fb8')); ctx.fill()
    ctx.set_source_rgba(*hexc('#d95a8a')); ctx.set_line_width(7)
    ctx.move_to(0, -110); ctx.curve_to(-20, -40, 20, 20, 0, 90); ctx.stroke()
    for ex in (-35, 35):
        ctx.arc(ex, -5, 18, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.arc(ex+3, -3, 10, 0, 2*math.pi); ctx.set_source_rgba(0.1, 0.1, 0.1, 1); ctx.fill()
    ctx.arc(0, 30, 22, 0.2, math.pi-0.2); ctx.set_source_rgba(0.3, 0.1, 0.1, 1); ctx.set_line_width(7); ctx.stroke()
    ctx.restore()

def glowq(ctx, x, y, t, p, size=380):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p)*(1 + 0.04*math.sin(t*5)); ctx.scale(sc, sc)
    g = cairo.RadialGradient(0, -size*0.3, 10, 0, -size*0.3, size*0.8); g.add_color_stop_rgba(0, 1, 0.85, 0.2, 0.55); g.add_color_stop_rgba(1, 1, 0.85, 0.2, 0)
    ctx.set_source(g); ctx.arc(0, -size*0.3, size*0.8, 0, 2*math.pi); ctx.fill()
    text(ctx, '?', 0, 0, size, '#ffd23f'); ctx.restore()

def sweat(ctx, x, y, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y + 30*p)
    ctx.move_to(0, -30); ctx.curve_to(20, 0, 20, 20, 0, 22); ctx.curve_to(-20, 20, -20, 0, 0, -30)
    ctx.set_source_rgba(*hexc('#7fd0ff')); ctx.fill(); ctx.restore()

# ------------------------------------------------------------------ beats
CH = {'K': ('Rahim', '#3a6fd8', '#f4f1e8', False), 'S': ('Sunitha', '#f2b632', '#c2307a', True)}
BEATS = [
 dict(id='h1', sc='road', ml='ബുദ്ധിയുള്ളവർ മാത്രം ഇത് കാണുക!', en='Only people with *brains* should watch this!'),
 dict(id='s1', sc='road', ml='ഇത് കോഴിക്കോട്ടെ റഹീം. നീണ്ട, കട്ടിയുള്ള താടിയുള്ള ആൾ.', en='This is *Rahim* from *Kozhikode.* He has a long, thick *beard.*', pos=dict(K=540), walk='K', sign='KOZHIKODE'),
 dict(id='s2', sc='bank', ml='ഒരു ദിവസം, അവൻ ബീച്ചിലെ ഏറ്റവും നല്ല താടി മത്സരത്തിന് ചെന്നു.', en='One day he enters the *Best Beard* contest at the *beach.*', pos=dict(K=260, S=860), walk='K'),
 dict(id='s3', sc='bank', ml='ജഡ്ജി സുനിത ചോദിച്ചു, നിങ്ങൾ എത്ര തവണ ഷേവ് ചെയ്യും?', en='Judge *Sunitha* asks: "How often do you *shave?*"', pos=dict(K=260, S=860), bub=('S', 'SHAVE?')),
 dict(id='s4', sc='form', ml='റഹീം പറഞ്ഞു, പത്ത് വർഷമായി ഞാൻ ഈ താടി ഒരിക്കലും വെട്ടിയിട്ടില്ല.', en='Rahim says: "I have *not cut* this beard for *10 years.*"', chips=('BEARD: 10 YEARS',)),
 dict(id='s5', sc='form', ml='പക്ഷേ, എല്ലാ ദിവസവും ഞാൻ ഇരുപതിലേറെ തവണ ഷേവ് ചെയ്യുന്നുണ്ട്!', en='"But I *shave* more than *20 times* every single day!"', chips=('BEARD: 10 YEARS', 'SHAVES: 20+ A DAY')),
 dict(id='s6', sc='shock', ml='സുനിത ഞെട്ടിപ്പോയി! ദിവസവും ഇരുപത് ഷേവ്, എന്നിട്ടും ഇത്ര നീണ്ട താടിയോ?', en='Sunitha is *shocked!* 20 shaves a day, and still a *long beard?*'),
 dict(id='s7', sc='no', ml='അവൻ കള്ളം പറയുന്നില്ല. ഇത് ഒട്ടിച്ചുവെച്ച താടിയുമല്ല, ശരിക്കുള്ള താടിയാണ്.', en='He is *not lying.* And it is *not a fake* beard. It is *real!*'),
 dict(id='s8', sc='cake', ml='രാവിലെ മുതൽ രാത്രി വരെ, ഓരോ ദിവസവും ഇരുപതിലേറെ ഷേവ്. എന്നിട്ടും താടി അങ്ങനെ തന്നെ!', en='Morning to night, *20+ shaves* every day. The beard stays *the same!*', pos=dict(K=540)),
 dict(id='q1', sc='night', ml='അപ്പോൾ, ഇത് എങ്ങനെ സാധിക്കും?', en='So how is this *possible?*'),
 dict(id='th', sc='think', ml='ഉത്തരം ആലോചിക്കൂ!', en='Think about the *answer...*', post=4.3),
 dict(id='c1', sc='cta', ml='നിങ്ങളുടെ ഉത്തരം കമന്റിൽ ടൈപ്പ് ചെയ്യൂ!', en='Type *ANSWER* in the comments!'),
 dict(id='c2', sc='share', ml='ബുദ്ധിമാനാണെന്ന് കരുതുന്ന കൂട്ടുകാരന് ഇത് അയച്ചു കൊടുക്കൂ!', en='Send this to your friend who thinks he is *smart!*', pos=dict(K=300, S=780)),
 dict(id='c3', sc='follow', ml='ഉത്തരം അറിയാൻ, കണ്ടുപിടി ഫോളോ ചെയ്യൂ!', en='*Follow* Kandupidi for the answer!', post=1.6),
]

S = 1.1
def draw_people(ctx, t, b, ps, talker=None, mood=None):
    xs = {k: v[0] for k, v in ps.items()}
    for k in ('S', 'K'):
        if k not in ps: continue
        x, moving = ps[k]; nm, sh, lo, fem = CH[k]
        others = [xs[o] for o in xs if o != k]
        face = 1 if (not others or sum(others)/len(others) > x) else -1
        y = GROUND - 10 - (abs(math.sin(t*12))*18 if moving else 0)
        talk = abs(math.sin(t*13))*0.8 if (talker == k and b['t0'] < t < b['t1']) else 0
        M.person(ctx, x, y, S, sh, lo, fem, talk, 0.0, face, nm if b['sc'] in ('road', 'bank') else None, t)
        cheeks(ctx, x, y, S, face)
        if k == 'K': beard(ctx, x, y, S, face, t)

def pos_at(b, t):
    out = {}
    for k, x in (b.get('pos') or {}).items():
        if b.get('walk') == k:
            p = sprog(t, b['t0'], 1.2); x0 = -250 if b['sc'] != 'road' else 1350
            out[k] = (lerp(x0, x, p), p < 1)
        else: out[k] = (x, False)
    return out

def draw_factory(tl):
    def draw(ctx, t):
        i = 0
        for j, b in enumerate(tl.beats):
            if t >= b['t0'] - 0.12: i = j
        b = tl.beats[i]; t0, t1 = b['t0'], b['t1']; sc = b['sc']
        z = 1.0 + 0.07*(1 - sprog(t, t0-0.12, 0.35)) + 0.02*prog(t, t0, t1-t0+0.5)
        ctx.save(); ctx.translate(W/2, H*0.42); ctx.scale(z, z); ctx.translate(-W/2, -H*0.42)
        ps = pos_at(b, t)
        if sc == 'road':
            ctx.set_source_surface(bg('road')); ctx.paint(); bokeh(ctx, t)
            if b['id'] == 'h1':
                MS.bulb(ctx, W/2, 420, prog(t, t0+0.1, 0.4), t)
                for k, (qx, qy) in enumerate(((150, 360), (930, 340), (200, 760), (880, 760))):
                    text(ctx, '?', qx, qy + 12*math.sin(t*4+k), 130, '#ffffff', alpha=prog(t, t0+0.3+k*0.1, 0.2))
            else:
                draw_people(ctx, t, b, ps)
                MS.sign(ctx, W/2, 330, b['sign'], prog(t, t0+0.3, 0.35))
        elif sc == 'bank':
            ctx.set_source_surface(bg('bank')); ctx.paint()
            draw_people(ctx, t, b, {k: v for k, v in ps.items() if k == 'S'}, b.get('bub', [None])[0])
            counter(ctx)
            draw_people(ctx, t, b, {k: v for k, v in ps.items() if k == 'K'})
            if 'bub' in b: M.bubble(ctx, 860, 440, b['bub'][1], prog(t, t0+0.2, 0.3), size=70, col='#1f4fa8')
        elif sc == 'form':
            ctx.set_source_surface(bg('bank')); ctx.paint()
            ctx.set_source_rgba(0.05, 0.08, 0.2, 0.55); ctx.paint()
            sunburst(ctx, W/2, 640, t, '#3a5ab8', '#2a4296', a=0.35)
            rows = (('NAME', 'RAHIM', 0.0), ('NOT CUT FOR', '10 YEARS', 0.8 if b['id'] == 's4' else -9), ('SHAVES A DAY', '20+' if b['id'] == 's5' else '', 1.5))
            form(ctx, W/2, 560, 1.0 if b['id'] == 's5' else prog(t, t0, 0.35), rows, t, t0)
            for k, c in enumerate(b['chips']):
                fresh = (b['id'] == 's4' and k == 0) or (b['id'] == 's5' and k == 1)
                chip(ctx, W/2, 900 + k*120,
                     c, prog(t, t0 + (1.3 if fresh else -1) + (1.0 if k == 1 else 0), 0.35), '#1f4fa8' if k == 0 else '#d9283b', size=46)
        elif sc == 'shock':
            ctx.set_source_surface(bg('dark')); ctx.paint()
            sunburst(ctx, W/2, 600, t*3, '#ffcf5a', '#ff8a3c')
            zz = 1 + 0.25*sprog(t, t0, 0.5)
            ctx.save(); ctx.translate(W/2, 1000); ctx.scale(zz, zz); ctx.translate(-W/2, -1000)
            M.person(ctx, W/2, 1300, 1.5, CH['S'][1], CH['S'][2], True, 0.9, 0.0, 1, None, t)
            cheeks(ctx, W/2, 1300, 1.5, 1)
            ctx.restore()
            sweat(ctx, W/2 + 160, 520, prog(t, t0+0.5, 1.2))
            for k, (qx, qy) in enumerate(((180, 300), (900, 300))):
                text(ctx, '!' if k == 0 else '?', qx, qy + 10*math.sin(t*6+k), 170, '#ffffff', alpha=prog(t, t0+0.2, 0.2))
            chip(ctx, W/2, 230, '20 SHAVES + LONG BEARD?', prog(t, t0+1.2, 0.35), '#d9283b', size=50)
        elif sc == 'no':
            ctx.set_source_surface(bg('road')); ctx.paint(); ctx.set_source_rgba(0.05, 0.05, 0.2, 0.5); ctx.paint(); bokeh(ctx, t)
            chip(ctx, W/2, 420, 'LYING', prog(t, t0+0.1, 0.35), '#5a4a8a', size=80)
            nosign(ctx, W/2, 420, 190, prog(t, t0+0.8, 0.35))
            chip(ctx, W/2, 830, 'FAKE BEARD', prog(t, t0+2.2, 0.35), '#5a4a8a', size=80)
            nosign(ctx, W/2, 830, 190, prog(t, t0+2.9, 0.35))
        elif sc == 'cake':
            ctx.set_source_surface(bg('road')); ctx.paint(); bokeh(ctx, t, n=40, col=(1, 0.9, 0.6))
            draw_people(ctx, t, b, ps)
            for k in range(20):
                p = prog(t, t0 + 0.4 + k*0.16, 0.2)
                if p > 0:
                    cx = 115 + (k % 5)*212; cy = 150 + (k // 5)*108
                    ctx.save(); ctx.translate(cx, cy); ctx.scale(back(p), back(p))
                    ctx.arc(0, 0, 52, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#ffffff', 0.9)); ctx.fill()
                    text(ctx, str(k+1), 0, 19, 52, '#d9283b'); ctx.restore()
        elif sc == 'night':
            ctx.set_source_surface(bg('night')); ctx.paint(); bokeh(ctx, t, col=(0.7, 0.8, 1))
            glowq(ctx, W/2, 780, t, prog(t, t0+0.1, 0.45))
        elif sc == 'think':
            ctx.set_source_surface(bg('night')); ctx.paint(); ctx.set_source_rgba(0.03, 0.03, 0.1, 0.4); ctx.paint()
            M.bubble(ctx, W/2, 260, '20 shaves a day, still a beard?', 1.0, size=50)
            M.clock5(ctx, W/2, 660, t, b['t1'] + 0.1, r=170)
            pill(ctx, W/2, 980, 640, 96, '#d9483b', 'THINK...', size=54, p=prog(t, t0, 0.3))
        elif sc in ('cta', 'follow'):
            ctx.set_source_surface(bg('dark')); ctx.paint(); bokeh(ctx, t, col=(0.9, 0.7, 1))
            brain(ctx, W/2, 250, 0.9, t)
            MS.comment_box(ctx, 430, 'ANSWER', t, tl.by['c1']['t0'])
            if sc == 'follow':
                MS.follow_btn(ctx, W/2, 860, t, following=(t - t0) > 2.6)
                text(ctx, 'KANDUPIDI', W/2, 1040, 70, '#ffd23f')
            else:
                pill(ctx, W/2, 830, 760, 96, '#2fa86a', 'ANSWER in the comments!', size=46, p=prog(t, t0+0.2, 0.3))
        elif sc == 'share':
            ctx.set_source_surface(bg('road')); ctx.paint(); bokeh(ctx, t)
            draw_people(ctx, t, b, ps)
            M.bubble(ctx, W/2, 360, 'Send to a friend who thinks he is smart!', prog(t, t0, 0.3), size=40)
            for k, x in enumerate((300, 780)): text(ctx, '?', x, 520 + 10*math.sin(t*5+k), 120, '#ffd23f', alpha=prog(t, t0+0.4, 0.2))
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and i: ctx.set_source_rgba(1, 1, 1, 0.25*fl); ctx.paint()
        # caption band (lower-middle) with dark outline effect
        if b.get('en'):
            ctx.save()
            for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)):
                ctx.save(); ctx.translate(dx, dy); _shadow_caption(ctx, b, t); ctx.restore()
            ctx.restore()
            caption(ctx, b['en'], t, t0, t1, y=1200, size=66, maxw=980)
    return draw

def _shadow_caption(ctx, b, t):
    # draw same caption in black for outline
    s = b['en']; size = 66; maxw = 980
    words = [w.replace('*', '') for w in s.split()]
    sp = text_w(ctx, ' ', size); lines, cur, cw = [], [], 0
    for wd_ in words:
        ww = text_w(ctx, wd_, size)
        if cur and cw + sp + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((wd_, ww)); cw += (sp if cw else 0) + ww
    if cur: lines.append(cur)
    n = len(words); i = 0; dur = max(0.4, (b['t1'] - b['t0'])*0.85)
    for li, line in enumerate(lines):
        tw = sum(w for _, w in line) + sp*(len(line)-1); x = W/2 - tw/2; yy = 1200 + li*size*1.22
        for wd_, ww in line:
            rev = clamp((t - b['t0'] - dur*i/n)/0.12)
            text(ctx, wd_, x, yy, size, '#10102a', align='l', alpha=(0.25 + 0.75*rev)*0.9); x += ww + sp; i += 1

def sfx_list(tl):
    sfx = []
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0']-0.12, 'whoosh', 0.5))
        if b['id'] == 'h1': sfx.append((b['t0']+0.15, 'pop', 0.8))
        if 'sign' in b or 'bub' in b: sfx.append((b['t0']+0.25, 'pop', 0.6))
        if b['sc'] == 'form':
            for k in range(4): sfx.append((b['t0']+(0.8 if b['id'] == 's4' else 1.5)+k*0.1, 'tick', 0.3))
            sfx.append((b['t0']+(1.3 if b['id'] == 's4' else 2.3), 'pop', 0.7))
        if b['sc'] == 'shock': sfx.append((b['t0']+0.05, 'thud', 0.8)); sfx.append((b['t0']+1.2, 'pop', 0.6))
        if b['sc'] == 'no': sfx.append((b['t0']+0.8, 'wrong', 0.45)); sfx.append((b['t0']+2.9, 'wrong', 0.45))
        if b['sc'] == 'cake':
            for k in range(20): sfx.append((b['t0']+0.4+k*0.16, 'pop', 0.25))
        if b['sc'] == 'night': sfx.append((b['t0']+0.1, 'thud', 0.6))
        if b['sc'] == 'think':
            for k in range(5): sfx.append((b['t1']+0.1+k, 'tick', 0.6))
        if b['sc'] == 'cta':
            for k in range(6): sfx.append((b['t0']+0.3+k*0.2, 'tick', 0.25))
        if b['sc'] == 'follow': sfx.append((b['t0']+2.6, 'right', 0.5))
    return sfx

if __name__ == '__main__':
    tl = Timeline(BEATS, lead=0.15, gap=0.1, think=0, spk=STORY)
    total = tl.end + 0.4
    draw = draw_factory(tl)
    print('TOTAL', round(total, 1))
    if 'stills' in sys.argv:
        k = 0
        for b in tl.beats:
            for tt in ((b['t0'] + 0.9, b['t1'] - 0.05) if b['sc'] != 'think' else (b['t1'] + 2.0,)):
                surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt)
                surf.write_to_png(f'{OUT}/s{k:02d}.png'); k += 1
    else:
        aud = f'{OUT}/{NAME}.wav'; MS.build_mix(aud, tl, sfx_list(tl), total)
        wd.render_raw(f'{OUT}/{NAME}.mp4', total, draw, aud)
