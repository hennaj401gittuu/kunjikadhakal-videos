"""9:16 money-story Short (paper-cut Kerala shop row) for Kandupidi.
Story: The Thief Came Back (Pappan's shop). Answer verified in ledger_thief.py.
python3 money_short.py stills | render"""
import sys, math, os, random, subprocess, cairo
sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/money'); sys.path.insert(0, '/home/claude/ml')
import money as M            # reuse paper-cut helpers (person, note, bubble, stamp, sign, clock5, paper)
import wd
wd.W, wd.H = 1080, 1920; M.W, M.H = 1080, 1920
from wd import text, text_w, caption, pill, render_raw
from pz import Timeline, clamp, prog, sprog, back, hexc, rrect, sfx2, SR, A, lerp
import numpy as np, soundfile as sf
paper, person, note, bubble, stamp, sign, clock5 = M.paper, M.person, M.note, M.bubble, M.stamp, M.sign, M.clock5
W, H = 1080, 1920
GROUND = 1180; BAND = 1200
STORY = ('male', 0.88, 1.27)     # deeper warm storyteller (target ~110-125 Hz)
OUT = '/home/claude/money/outs'; os.makedirs(OUT, exist_ok=True)
NAME = 'KP_Thief_Came_Back_Mini'

# ------------------------------------------------------------------ background
_bg = {}
def street(night=False):
    if night in _bg: return _bg[night]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    g = cairo.LinearGradient(0, 0, 0, 900)
    if night: g.add_color_stop_rgba(0, *hexc('#141a3c')); g.add_color_stop_rgba(1, *hexc('#3a3a6e'))
    else: g.add_color_stop_rgba(0, *hexc('#f59a5e')); g.add_color_stop_rgba(1, *hexc('#fcd9a8'))
    ctx.set_source(g); ctx.paint()
    sx, sy = 800, 300
    if night:
        ctx.arc(sx, sy, 90, 0, 2*math.pi); paper(ctx, '#f4f1d8', 0, 0)
        ctx.arc(sx+40, sy-25, 80, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#1d2350')); ctx.fill()
        rnd = random.Random(4)
        for k in range(60):
            ctx.arc(rnd.uniform(0, W), rnd.uniform(0, 650), rnd.uniform(1.5, 3.5), 0, 2*math.pi); ctx.set_source_rgba(1, 1, 0.9, rnd.uniform(0.4, 0.9)); ctx.fill()
    else:
        ctx.arc(sx, sy, 170, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#fff3d6', 0.55)); ctx.fill()
        ctx.arc(sx, sy, 125, 0, 2*math.pi); paper(ctx, '#fffaf0', 0, 0)
    rnd = random.Random(7)
    hc = (('#5fb3a7', '#3f978d', '#2b7a73') if not night else ('#2c4a5a', '#233e4e', '#1a3040'))
    for k, (y0, col) in enumerate(((640, hc[0]), (700, hc[1]), (760, hc[2]))):
        ctx.move_to(0, H); ph = rnd.uniform(0, 6)
        for xx in range(0, W+40, 40): ctx.line_to(xx, y0 + 40*math.sin(xx/220 + ph + k))
        ctx.line_to(W, H); ctx.close_path(); paper(ctx, col, 0, -6)
    for px in (60, 1020):
        ctx.set_source_rgba(*hexc('#2a5a3a' if not night else '#10261a')); ctx.set_line_width(14)
        ctx.move_to(px, 800); ctx.curve_to(px+10, 700, px+20, 620, px+30, 540); ctx.stroke()
        for kk in range(7):
            a = -math.pi/2 + (kk-3)*0.5
            ctx.move_to(px+30, 540); ctx.curve_to(px+30+math.cos(a)*70, 540+math.sin(a)*60, px+30+math.cos(a)*130, 540+math.sin(a)*80+30, px+30+math.cos(a)*150, 540+math.sin(a)*70+70)
            ctx.set_line_width(10); ctx.stroke()
    shops = (('PAPPAN STORES', 30, '#f2d16b'), ('LEELA BAKERY', 555, '#8fc7e8'))
    for i, (nm, x0, col) in enumerate(shops):
        w0 = 495; top = 660 + i*20
        ctx.rectangle(x0, top, w0, GROUND - top); paper(ctx, col)
        ctx.move_to(x0-20, top+10); ctx.line_to(x0+w0/2, top-70); ctx.line_to(x0+w0+20, top+10); ctx.close_path(); paper(ctx, '#b5452f')
        rrect(ctx, x0+40, top+22, w0-80, 64, 10); paper(ctx, '#2b2622')
        text(ctx, nm, x0+w0/2, top+68, 36, '#ffe9a8')
        for k in range(7):
            ctx.rectangle(x0+k*w0/7, top+96, w0/7, 22); ctx.set_source_rgba(*hexc('#ffffff' if k % 2 else '#d9483b')); ctx.fill()
        rrect(ctx, x0+30, top+140, 130, GROUND-top-140, 8); paper(ctx, '#6b4428')
        rrect(ctx, x0+w0-190, top+150, 150, 110, 8); paper(ctx, '#fff4dc' if not night else '#f7d36a')
        ctx.set_source_rgba(0.4, 0.25, 0.1, 0.6); ctx.set_line_width(5); ctx.move_to(x0+w0-115, top+150); ctx.line_to(x0+w0-115, top+260); ctx.stroke()
    ctx.rectangle(0, GROUND-6, W, 30); paper(ctx, '#c9a57a', 0, -4)
    if night:
        ctx.set_source_rgba(0.05, 0.06, 0.2, 0.45); ctx.rectangle(0, 0, W, BAND); ctx.fill()
    ctx.move_to(0, BAND+12)
    for xx in range(0, W+30, 30): ctx.line_to(xx, BAND + 8*math.sin(xx*0.37) + 4*math.sin(xx*1.3))
    ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path(); paper(ctx, '#1e3a8a', 0, -6)
    ctx.set_source_rgba(1, 1, 1, 0.04)
    for k in range(250):
        ctx.arc(rnd.uniform(0, W), rnd.uniform(BAND, H), rnd.uniform(1, 3), 0, 2*math.pi); ctx.fill()
    _bg[night] = surf
    return surf

def clouds(ctx, t, night=False):
    for i, (x0, y0, s) in enumerate(((100, 170, 0.8), (600, 120, 0.65), (900, 470, 0.7))):
        x = (x0 + t*14*(1+i*0.3)) % (W+400) - 200
        ctx.save(); ctx.translate(x, y0); ctx.scale(s, s)
        for (dx, dy, r) in ((0, 0, 50), (55, -20, 60), (115, 0, 48), (60, 18, 50)): ctx.new_sub_path(); ctx.arc(dx, dy, r, 0, 2*math.pi)
        paper(ctx, '#fff8ee' if not night else '#4a4f80', 5, 7); ctx.restore()

# ------------------------------------------------------------------ props
def cap(ctx, x, y, s, face, t):
    bob = 3*math.sin(t*3 + x)
    hx, hy = x, y + (bob - 430 - 40)*s
    ctx.save(); ctx.translate(hx, hy); ctx.scale(s, s)
    ctx.arc(0, 0, 66, math.pi, 2*math.pi); ctx.close_path(); paper(ctx, '#3a3a3a', 2, 3)
    ctx.move_to(face*10, -2); ctx.line_to(face*110, 6); ctx.line_to(face*100, 18); ctx.line_to(-face*40, 10); ctx.close_path(); paper(ctx, '#262626', 2, 2)
    ctx.restore()

def sack(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-70, 0); ctx.curve_to(-90, -80, -70, -150, -45, -165); ctx.line_to(45, -165); ctx.curve_to(70, -150, 90, -80, 70, 0); ctx.close_path(); paper(ctx, '#e9d8b0', 4, 5)
    ctx.set_source_rgba(0.5, 0.35, 0.15, 1); ctx.set_line_width(7); ctx.move_to(-48, -158); ctx.line_to(48, -158); ctx.stroke()
    for k in range(5): ctx.arc(-30+k*15, -178 - 6*math.sin(k), 9, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    text(ctx, 'RICE', 0, -60, 38, '#7a2a10'); text(ctx, '₹600', 0, -18, 30, '#2b2622')
    ctx.restore()

def bulb(ctx, x, y, p, t):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    for k in range(12):
        a = k*math.pi/6 + t*0.6; r0, r1 = 120, 165 + 12*math.sin(t*8+k)
        ctx.move_to(math.cos(a)*r0, math.sin(a)*r0); ctx.line_to(math.cos(a)*r1, math.sin(a)*r1)
        ctx.set_source_rgba(*hexc('#ffd23f')); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.arc(0, -10, 95, 0, 2*math.pi); paper(ctx, '#ffe25a', 5, 6)
    ctx.arc(-30, -40, 25, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
    rrect(ctx, -45, 70, 90, 70, 12); paper(ctx, '#8a8a8a', 3, 3)
    for k in range(3): ctx.rectangle(-45, 82+k*20, 90, 6); ctx.set_source_rgba(0.35, 0.35, 0.35, 1); ctx.fill()
    ctx.restore()

def bignote(ctx, x, y, p, t, mark=True):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc*2.4, sc*2.4); ctx.rotate(-0.06)
    note(ctx, 0, 0, '₹1000', 1.0)
    ctx.restore()
    if mark:
        mp = prog(t, 0, 1) if False else 1
        ctx.save(); ctx.translate(x + 120, y + 55)
        ctx.set_source_rgba(*hexc('#1a3fbf')); ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(-28, 0); ctx.line_to(-6, 18); ctx.line_to(30, -22); ctx.stroke()   # little pen tick
        ctx.restore()

def circle_mark(ctx, x, y, p):
    if p <= 0: return
    ctx.save(); ctx.set_source_rgba(*hexc('#d9283b')); ctx.set_line_width(9)
    ctx.arc(x, y, 70, -math.pi/2, -math.pi/2 + 2*math.pi*clamp(p)); ctx.stroke(); ctx.restore()

def comment_box(ctx, y, s, t, t0):
    rrect(ctx, 70, y, 940, 260, 26); paper(ctx, '#ffffff', 8, 10)
    ctx.arc(150, y+75, 40, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#8fc7e8')); ctx.fill()
    text(ctx, 'Add a comment...', 215, y+90, 38, '#9a9a9a', align='l')
    n = int(clamp((t-t0-0.3)/1.2)*len(s)); word = s[:n]
    text(ctx, word, 215, y+195, 70, '#2b2622', align='l')
    if (t*2) % 1 < 0.6: ctx.rectangle(215 + text_w(ctx, word, 70) + 8 if word else 215, y+138, 7, 72); ctx.set_source_rgba(*hexc('#d9283b')); ctx.fill()

def follow_btn(ctx, x, y, t, following=False):
    pp = 1 + 0.07*math.sin(t*8)
    ctx.save(); ctx.translate(x, y); ctx.scale(pp, pp); rrect(ctx, -250, -62, 500, 124, 62)
    ctx.set_source_rgba(*hexc('#e62117' if not following else '#555555')); ctx.fill()
    text(ctx, '+ FOLLOW' if not following else 'FOLLOWING', 0, 20, 58, '#ffffff'); ctx.restore()

# ------------------------------------------------------------------ characters
CH = {'P': ('Pappan', '#2f6fd6', '#f4f1e8', False), 'T': ('Man in cap', '#5a4a6a', '#3a3a50', False), 'L': ('Leela', '#f2b632', '#d23a7a', True)}
def stripes(ctx, x, y, s, t):
    bob = 3*math.sin(t*3 + x)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.translate(0, bob)
    rrect(ctx, -70, -360, 140, 175, 40); ctx.clip()
    for k in range(-4, 5): ctx.rectangle(-70 + k*34 + 12, -360, 12, 175); ctx.set_source_rgba(1, 1, 1, 0.45); ctx.fill()
    ctx.restore()

BEATS = [
 dict(id='h1', sc='hook', ml='നിങ്ങൾക്ക് ബുദ്ധിയുണ്ടോ? നമുക്ക് നോക്കാം!', en='Do you have *brains?* Let\'s *see!*', pos=dict(P=230, T=540, L=850)),
 dict(id='s1', sc='st', ml='പപ്പൻ ഒരു കടക്കാരനാണ്.', en='*Pappan* is a shopkeeper.', pos=dict(P=330), sign='PAPPAN STORES'),
 dict(id='s2', sc='night', ml='ഒരു രാത്രി, ഒരു കള്ളൻ പപ്പന്റെ മേശയിൽ നിന്ന് ആയിരം രൂപ മോഷ്ടിച്ചു.', en='One night, a thief *stole ₹1000* from Pappan\'s cash box.', pos=dict(T=700), bub=('T', '-₹1000', '#d9283b')),
 dict(id='s3', sc='mark', ml='ആ നോട്ടിൽ, പപ്പൻ പേന കൊണ്ട് ഒരു ചെറിയ അടയാളം ഇട്ടിരുന്നു.', en='That note had a small *pen mark* by Pappan.'),
 dict(id='s4', sc='st', ml='പിറ്റേന്ന് രാവിലെ, തൊപ്പി വെച്ച ഒരാൾ കടയിൽ വന്നു.', en='Next morning, a man in a *cap* comes to the shop.', pos=dict(P=300, T=720), walk='T'),
 dict(id='s5', sc='st', ml='അയാൾ അറുന്നൂറ് രൂപയുടെ അരി വാങ്ങി, ഒരു ആയിരം രൂപ നോട്ട് കൊടുത്തു.', en='He buys rice worth *₹600* and pays with a *₹1000* note.', pos=dict(P=300, T=720), pay=('T', 'P', '₹1000'), rice='P', bub=('P', '₹600', '#2b2622')),
 dict(id='s6', sc='st', ml='പപ്പന്റെ കയ്യിൽ ചില്ലറയില്ല. അയാൾ ലീലയുടെ കടയിലേക്ക് ഓടി.', en='Pappan has *no change.* He runs to *Leela\'s* shop next door.', pos=dict(P=600, T=180, L=880), rice='P0', bub=('P', 'NO CHANGE!', '#d9283b')),
 dict(id='s7', sc='st', ml='ലീല ആ നോട്ട് വാങ്ങി, പത്ത് നൂറു രൂപ നോട്ടുകൾ കൊടുത്തു.', en='Leela takes the note and gives him *ten ₹100* notes.', pos=dict(P=600, T=180, L=880), rice='P0', pay=('P', 'L', '₹1000'), pay2=('L', 'P', '10 x ₹100')),
 dict(id='s8', sc='st', ml='പപ്പൻ തിരികെ വന്ന്, അരിയും നാനൂറ് രൂപ ബാക്കിയും കൊടുത്തു.', en='Pappan comes back and gives the *rice* and *₹400* change.', pos=dict(P=480, T=180, L=880), pay=('P', 'T', '₹400'), rice='T'),
 dict(id='s9', sc='st', ml='അപ്പോഴാണ് ലീല വിളിച്ചു പറഞ്ഞത്, ഈ നോട്ടിൽ പപ്പന്റെ അടയാളം ഉണ്ടല്ലോ!', en='Then Leela shouts: "This note has *your mark!*"', pos=dict(P=480, T=180, L=880), rice='T', bub=('L', 'YOUR MARK!', '#1a3fbf'), stampit='STOLEN NOTE!'),
 dict(id='s10', sc='st', ml='മോഷണം പോയ നോട്ട് തന്നെ! പക്ഷേ തൊപ്പിക്കാരൻ ഓടിപ്പോയി.', en='It\'s the *stolen* note! But the man in the cap has *run away!*', pos=dict(P=480, T=-260, L=880), rice='T', walk='T', bub=('P', '?!', '#d9283b')),
 dict(id='q1', sc='q', ml='ഇനി ചോദ്യം.', en='Now the *question:*', pos=dict(P=300, L=780)),
 dict(id='q2', sc='q', ml='പപ്പന് ആകെ എത്ര രൂപയുടെ നഷ്ടം വന്നു?', en='How much did *Pappan* lose in *total?*', pos=dict(P=300, L=780), box=True),
 dict(id='th', sc='think', ml='ഉത്തരം ആലോചിക്കൂ!', en='Think about the *answer...*', post=4.3),
 dict(id='c1', sc='cta', ml='നിങ്ങളുടെ ഉത്തരം കമന്റിൽ ടൈപ്പ് ചെയ്യൂ!', en='Type *ANSWER* in the comments!'),
 dict(id='c2', sc='share', ml='ബുദ്ധിമാനാണെന്ന് കരുതുന്ന കൂട്ടുകാരന് ഇത് അയച്ചു കൊടുക്കൂ!', en='Send this to your friend who thinks he is *smart!*', pos=dict(P=300, L=780)),
 dict(id='c3', sc='follow', ml='ഉത്തരം അറിയാൻ, കണ്ടുപിടി ഫോളോ ചെയ്യൂ!', en='*Follow* Kandupidi for the answer!', post=1.6),
]

def pos_at(tl, i, t):
    """character x positions, eased from previous beat's"""
    b = tl.beats[i]; cur = b.get('pos') or {}
    prev = {}
    for j in range(i-1, -1, -1):
        if tl.beats[j].get('pos'): prev = tl.beats[j]['pos']; break
    out = {}
    for k, x in cur.items():
        if b.get('walk') == k:
            x0 = 1300 if k not in prev or b['id'] == 's4' else prev[k]
            p = sprog(t, b['t0'], 1.3 if b['id'] == 's4' else 1.0)
            out[k] = (lerp(x0, x, p), p < 1)
        elif k in prev and prev[k] != x and b['sc'] == tl.beats[i-1]['sc']:
            p = sprog(t, b['t0'] - 0.1, 0.6); out[k] = (lerp(prev[k], x, p), p < 1)
        else: out[k] = (x, False)
    return out

S = 1.12
def draw_people(ctx, t, b, ps, talker=None, arm_of=None):
    xs = {k: v[0] for k, v in ps.items()}
    for k in ('L', 'P', 'T'):
        if k not in ps: continue
        x, moving = ps[k]
        nm, sh, lo, fem = CH[k]
        others = [xs[o] for o in xs if o != k]
        face = 1 if (not others or sum(others)/len(others) > x) else -1
        if k == 'T' and b['id'] in ('s10',): face = -1
        y = GROUND - 10 - (abs(math.sin(t*12))*18 if moving else 0)
        talk = abs(math.sin(t*13))*0.8 if (talker == k and b['t0'] < t < b['t1']) else 0
        arm = clamp(prog(t, b['t0'], 0.4)) if arm_of == k else 0.0
        person(ctx, x, y, S, sh, lo, fem, talk, arm, face, nm if b['sc'] in ('st', 'hook') else None, t)
        if k == 'P': stripes(ctx, x, y, S, t)
        if k == 'T': cap(ctx, x, y, S, face, t)

def hand(ps, k):
    x = ps[k][0]; return x, GROUND - 300*S

def draw_factory(tl):
    def draw(ctx, t):
        i = 0
        for j, b in enumerate(tl.beats):
            if t >= b['t0'] - 0.12: i = j
        b = tl.beats[i]; t0, t1 = b['t0'], b['t1']; sc = b['sc']
        z = 1.0 + 0.06*(1 - sprog(t, t0-0.12, 0.35)) + 0.015*prog(t, t0, t1-t0+0.5)
        ctx.save(); ctx.translate(W/2, H*0.45); ctx.scale(z, z); ctx.translate(-W/2, -H*0.45)
        night = sc == 'night'
        ctx.set_source_surface(street(night)); ctx.paint(); clouds(ctx, t, night)
        ps = pos_at(tl, i, t)
        if sc in ('hook', 'st', 'night', 'q', 'share'):
            talker = b['bub'][0] if 'bub' in b else None
            arm_of = b['pay'][0] if 'pay' in b else None
            draw_people(ctx, t, b, ps, talker, arm_of)
            # rice sack
            r = b.get('rice')
            if r == 'P0': sack(ctx, 340, GROUND-10, 0.9)
            elif r == 'P' and 'P' in ps: sack(ctx, ps['P'][0] + 150, GROUND-10, 0.9)
            elif r == 'T' and 'T' in ps:
                if b['id'] == 's8':
                    pp = sprog(t, t0+1.6, 0.8); x = lerp(340, ps['T'][0] + 130, pp)
                    sack(ctx, x, GROUND-10 - 80*math.sin(math.pi*pp), 0.9)
                else: sack(ctx, ps['T'][0] + (130 if b['id'] != 's10' else 120), GROUND-10, 0.9)
            if 'pay' in b:
                a, c, lab = b['pay']; pp = sprog(t, t0+0.3, 1.1)
                (xa, ya), (xc, yc) = hand(ps, a), hand(ps, c)
                if pp < 1: note(ctx, lerp(xa, xc, pp), ya - 150*math.sin(math.pi*pp), lab, 1.0, 0.25*math.sin(pp*6))
                else: note(ctx, xc, ya - 40, lab, 0.9)
            if 'pay2' in b:
                a, c, lab = b['pay2']; pp = sprog(t, t0+1.9, 1.1)
                if pp > 0:
                    (xa, ya), (xc, yc) = hand(ps, a), hand(ps, c)
                    note(ctx, lerp(xa, xc, pp), ya - 220 - 150*math.sin(math.pi*pp), lab, 1.0, 0.2*math.sin(pp*6))
            if night:
                pp = sprog(t, t0+0.3, 1.2); note(ctx, lerp(380, ps['T'][0] - 60, pp), 1000 - 200*math.sin(math.pi*pp), '₹1000', 0.9, 0.3*math.sin(pp*6))
            if 'bub' in b:
                k, s, col = b['bub']
                if k in ps: bubble(ctx, clamp(ps[k][0], 260, 820), 420, s, prog(t, t0+0.2, 0.3), size=64, col=col)
            if 'sign' in b: sign(ctx, W/2, 400, b['sign'], prog(t, t0+0.2, 0.35))
            if 'stampit' in b:
                note(ctx, 300, 430, '₹1000', 1.4, -0.1); stamp(ctx, W/2, 250, b['stampit'], prog(t, t0+1.6, 0.35), size=86)
            if sc == 'hook':
                bulb(ctx, W/2, 300, prog(t, t0+0.15, 0.4), t)
                text(ctx, '?', 120, 520 + 12*math.sin(t*4), 140, '#ffd23f'); text(ctx, '?', 960, 500 + 12*math.sin(t*4+1), 140, '#ffd23f')
            if sc == 'q':
                if b['id'] == 'q1':
                    p = back(prog(t, t0+0.1, 0.4)); ctx.save(); ctx.translate(W/2, 360); ctx.scale(p, p)
                    ctx.arc(0, 0, 170, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#ffd23f', 0.25)); ctx.fill()
                    text(ctx, '?', 0, 110, 330, '#ffd23f'); ctx.restore()
                    bubble(ctx, 850, 260, '-₹ ???', prog(t, t0+0.5, 0.3), size=60, col='#d9283b')
                else:
                    bubble(ctx, W/2, 300, 'Total loss = ₹?', prog(t, t0+0.15, 0.35), size=86)
                    pill(ctx, W/2, 470, 620, 90, '#2b2622', 'cash + rice', size=46, p=prog(t, t0+0.9, 0.3))
                    for k, (qx, qy) in enumerate(((140, 250), (950, 260), (120, 720), (960, 720))):
                        text(ctx, '?', qx, qy + 10*math.sin(t*4+k), 120, '#ffd23f', alpha=prog(t, t0+0.3+k*0.1, 0.2))
            if sc == 'share':
                bubble(ctx, W/2, 360, 'Send to a friend who thinks he is smart!', prog(t, t0, 0.3), size=40)
                for k, x in enumerate((300, 780)): text(ctx, '?', x, 520 + 10*math.sin(t*5+k), 120, '#ffd23f', alpha=prog(t, t0+0.4, 0.2))
        elif sc == 'mark':
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.5); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            bignote(ctx, W/2, 620, prog(t, t0, 0.35), t)
            circle_mark(ctx, W/2 + 122, 660, prog(t, t0+1.0, 0.6))
            pill(ctx, W/2, 900, 560, 96, '#1a3fbf', 'PEN MARK', size=54, p=prog(t, t0+1.4, 0.3))
        elif sc == 'think':
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.55); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            bubble(ctx, W/2, 230, 'Total loss = ₹?', 1.0, size=72)
            clock5(ctx, W/2, 640, t, b['t1'] + 0.1, r=170)
            pill(ctx, W/2, 960, 640, 96, '#d9483b', 'THINK...', size=54, p=prog(t, t0, 0.3))
        elif sc in ('cta', 'follow'):
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.45); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            comment_box(ctx, 300, 'ANSWER', t, tl.by['c1']['t0'])
            text(ctx, '👇', W/2, 700, 90, '#ffffff') if False else None
            if sc == 'follow':
                follow_btn(ctx, W/2, 820, t, following=(t - t0) > 2.6)
                text(ctx, 'KANDUPIDI', W/2, 1010, 70, '#ffd23f')
            else:
                pill(ctx, W/2, 720, 760, 96, '#2fa86a', 'ANSWER in the comments!', size=46, p=prog(t, t0+0.2, 0.3))
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and i: ctx.set_source_rgba(1, 1, 1, 0.25*fl); ctx.paint()
        caption(ctx, b.get('en'), t, t0, t1, y=1300, size=70, maxw=980)
    return draw

# ------------------------------------------------------------------ audio
def coin():
    out = np.zeros(int(0.5*SR))
    for k, f in enumerate((2637, 3520)): A.add(out, A.bell(f, 0.4, 9)*0.3, int(k*0.06*SR))
    return out
def register():
    out = np.zeros(int(0.9*SR)); rng = np.random.default_rng(3); n = int(0.12*SR)
    A.add(out, A.hp(rng.standard_normal(n), 2000)*np.exp(-np.arange(n)/SR*40)*0.4, 0)
    A.add(out, A.bell(1568, 0.8, 4)*0.45, int(0.1*SR)); A.add(out, A.bell(2093, 0.7, 4)*0.3, int(0.1*SR))
    return out
def pluck_bed(dur):
    n = int(dur*SR); y = np.zeros(n)
    scale = [62, 64, 66, 69, 71, 74, 76, 78]       # D major pentatonic-ish
    pat = [0, 2, 4, 2, 5, 4, 2, 3, 1, 3, 4, 6, 5, 3, 2, 1]
    step = 0.3; rng = np.random.default_rng(2); k = 0
    while k*step < dur:
        m = scale[pat[k % len(pat)]]
        A.add(y, A.pluck(A.mtof(m), 0.9, dec=3.5)*(0.5 if k % 2 else 0.7), int(k*step*SR))
        if k % 8 == 0:
            A.add(y, A.bass(A.mtof([50, 47, 43, 45][(k//8) % 4]), 2.4)*0.5, int(k*step*SR))
        k += 1
    padd = A.pad([A.mtof(62), A.mtof(66), A.mtof(69)], dur)*0.15
    return y + padd[:n]

def build_mix(path, tl, sfx, total):
    n = int((total+1)*SR); v = np.zeros(n); fx = np.zeros(n)
    for b in tl.beats:
        if b['wav']:
            y, sr = sf.read(b['wav']); y = y if y.ndim == 1 else y.mean(1); A.add(v, y, int(b['t0']*SR))
    for (t, kind, g) in sfx:
        s_ = {'coin': coin, 'register': register}.get(kind, lambda: sfx2(kind))()*g
        if kind == 'tick': s_ = s_[:int(0.05*SR)]
        A.add(fx, s_, int(t*SR))
    bed = pluck_bed(total+1); bed = bed/np.abs(bed).max()
    env = np.convolve(np.abs(v), np.ones(int(0.2*SR))/int(0.2*SR), mode='same'); duck = 1 - 0.55*np.clip(env/0.05, 0, 1)
    mix = (v*1.0 + bed[:n]*0.2*duck + fx*0.7)[:int(total*SR)]
    tmp = path + '.tmp.wav'; sf.write(tmp, mix.astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '44100', path], check=True); os.remove(tmp)

def sfx_list(tl):
    sfx = []
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0']-0.12, 'whoosh', 0.5))
        if b['sc'] == 'hook': sfx.append((b['t0']+0.15, 'pop', 0.8))
        if 'pay' in b: sfx.append((b['t0']+1.3, 'coin', 0.7))
        if 'pay2' in b: sfx.append((b['t0']+2.9, 'register', 0.7))
        if b['sc'] == 'night': sfx.append((b['t0']+1.4, 'coin', 0.5))
        if 'bub' in b or 'sign' in b: sfx.append((b['t0']+0.2, 'pop', 0.6))
        if 'stampit' in b: sfx.append((b['t0']+1.6, 'thud', 0.8)); sfx.append((b['t0']+1.7, 'wrong', 0.4))
        if b['sc'] == 'mark': sfx.append((b['t0']+1.0, 'pop', 0.6))
        if b['sc'] == 'q': sfx.append((b['t0']+0.15, 'thud', 0.6))
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
        aud = f'{OUT}/{NAME}.wav'; build_mix(aud, tl, sfx_list(tl), total)
        render_raw(f'{OUT}/{NAME}.mp4', total, draw, aud)
