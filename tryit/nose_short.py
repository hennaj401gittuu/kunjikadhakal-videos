"""9:16 TRY IT Short for Kandupidi: feel TWO noses (Aristotle's illusion).
Cross the middle finger over the index finger, close the eyes, rub the tip of the nose with both crossed fingertips:
it feels like two noses. Why: normally the outer sides of these two fingers can never touch one object at the same time,
so the brain (using its usual map of the fingers) reports two separate objects.
Reuses tryit_short.py (room, kid with nose=True / mood='closed', captions, countdown, brain, signal, comment box, follow)
and ring_short.py (table, countdown with CD, xmark). New: front-view hand vhand() with crossing fingers.
python3 nose_short.py stills | render"""
import sys, math, os, random, cairo
sys.path.insert(0, '/home/claude/tryit'); sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/money')
import tryit_short as T
import ring_short as R
import wd
from wd import text, text_w, pill
from pz import clamp, prog, sprog, back, hexc, rrect, lerp, smooth
W, H = 1080, 1920
NAME = 'KP_You_Will_Feel_Two_Noses_Mini'
OUT = T.OUT
CD = 10.0
R.CD = CD
grad, otext, badge, tag, check, sparkles = T.grad, T.otext, T.badge, T.tag, T.check, T.sparkles
SK0, SK1, SK2 = '#ffd9b8', '#f0b48a', '#c98260'

# ------------------------------------------------------------------ front-view hand, fingers up, back of hand to camera
VF = {'index': (-45, -70, 230, 58), 'middle': (15, -78, 250, 60)}
def vtips(cross):
    ai = 0.42*cross - 0.04; am = 0.05 - 0.62*cross
    out = {}
    for nm, a in (('index', ai), ('middle', am)):
        bx, by, L, w = VF[nm]; out[nm] = (bx + math.sin(a)*L, by - math.cos(a)*L, a)
    return out

def vhand(ctx, x, y, s, t, cross=0.0, outer=0.0, alpha=1.0, xray=0.0):
    """x,y = palm centre. outer: glow on the OUTER sides (index left side, middle right side as uncrossed)."""
    tp = vtips(cross)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.push_group()
    T.limb(ctx, 0, 120, 20, 700, 150, SK1, SK2)                       # forearm
    rrect(ctx, -10 - 95, 470, 230, 260, 50); ctx.set_source(grad(0, 0, '#ffe066', '#e0a800', -100, 120)); ctx.fill()   # yellow sleeve
    rrect(ctx, -105, -90, 210, 250, 90)
    g = cairo.RadialGradient(-30, -20, 20, 0, 30, 200); g.add_color_stop_rgba(0, *hexc(SK0)); g.add_color_stop_rgba(1, *hexc(SK1)); ctx.set_source(g); ctx.fill()
    # curled ring + little finger (knuckles folded down)
    for (kx, ky, r) in ((62, -62, 34), (100, -40, 30)):
        g = cairo.RadialGradient(kx - 8, ky - 10, 3, kx, ky, r + 6); g.add_color_stop_rgba(0, *hexc('#ffe2c8')); g.add_color_stop_rgba(1, *hexc(SK2))
        ctx.set_source(g); rrect(ctx, kx - r, ky - r, 2*r, 2*r + 30, r); ctx.fill()
    # thumb on the left
    R.capsule(ctx, -92, 100, -128, -10, 56, SK0, SK2)
    ctx.save(); ctx.translate(-128, -10); ctx.rotate(-0.3); rrect(ctx, -14, -24, 28, 30, 10); ctx.set_source_rgba(*hexc('#f7c9c0')); ctx.fill(); ctx.restore()
    order = ('index', 'middle')
    for nm in order:
        bx, by, L, w = VF[nm]; tx, ty, a = tp[nm]
        R.capsule(ctx, bx, by, tx, ty, w, SK0, SK2)
        for q in (0.4, 0.68):
            kx, ky = lerp(bx, tx, q), lerp(by, ty, q)
            ctx.save(); ctx.translate(kx, ky); ctx.rotate(a)
            ctx.move_to(-w*0.22, 0); ctx.curve_to(-w*0.08, 5, w*0.08, 5, w*0.22, 0); ctx.set_source_rgba(*hexc(SK2, 0.7)); ctx.set_line_width(4); ctx.stroke(); ctx.restore()
        ctx.save(); ctx.translate(tx + math.sin(a)*(-w*0.22), ty + math.cos(a)*(w*0.22)); ctx.rotate(a)
        rrect(ctx, -w*0.26, -w*0.38, w*0.52, w*0.58, w*0.2); ctx.set_source(grad(-w*0.4, w*0.2, '#ffeef0', '#f2b9b4')); ctx.fill(); ctx.restore()
    pat = ctx.pop_group()
    ctx.set_source(pat); ctx.paint_with_alpha(alpha*(1 - 0.6*xray))
    if xray: ctx.set_source_rgba(0.35, 0.6, 1.0, 0.35*xray); ctx.mask(pat)
    if outer > 0:
        # outer sides: index's thumb-side, middle's ring-side (when crossed they face each other)
        for nm, side in (('index', -1), ('middle', 1)):
            bx, by, L, w = VF[nm]; tx, ty, a = tp[nm]
            nx, ny = math.cos(a)*side, math.sin(a)*side
            x0, y0 = lerp(bx, tx, 0.72) + nx*w*0.5, lerp(by, ty, 0.72) + ny*w*0.5
            x1, y1 = tx + nx*w*0.5, ty + ny*w*0.5
            for lw_, al in ((26, 0.25), (12, 0.6), (6, 1.0)):
                ctx.set_source_rgba(1, 0.3, 0.3, al*outer); ctx.set_line_width(lw_); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()
    ctx.restore()
    return {k: (x + v[0]*s, y + v[1]*s) for k, v in tp.items()}

def hand_at_nose(ctx, nx, ny, s, t, cross=1.0, rub=0.0, alpha=1.0):
    tp = vtips(cross); mx = (tp['index'][0] + tp['middle'][0])/2; my = min(tp['index'][1], tp['middle'][1])
    off = 14*math.sin(t*7)*rub
    return vhand(ctx, nx - mx*s, ny - my*s - 6*s + off, s, t, cross=cross, alpha=alpha)

# ------------------------------------------------------------------ face close-up
FS, FY = 2.2, 2600
def face(ctx, t, mood='smile', ghost=0.0):
    ctx.set_source_surface(T.blur_room()); ctx.paint()
    T.kid(ctx, 540, FY, FS, t, mood=mood, nose=True)
    br = 4*math.sin(t*2.2); nx, ny = 540, FY + FS*(-750 + br)
    if ghost > 0:
        for sd in (-1, 1):
            dx = sd*(120 + 10*math.sin(t*5)); a = 0.45*ghost*(0.7 + 0.3*math.sin(t*6 + sd))
            ctx.save(); ctx.translate(nx + dx, ny); ctx.scale(FS, FS*0.82)
            g = cairo.RadialGradient(-6, -8, 2, 0, 0, 34); g.add_color_stop_rgba(0, 1, 0.85, 0.75, a); g.add_color_stop_rgba(1, 0.9, 0.55, 0.4, a*0.8)
            ctx.set_source(g); ctx.arc(0, 0, 30, 0, 2*math.pi); ctx.fill(); ctx.restore()
    T.vignette(ctx, 0.35)
    return nx, ny

def dark_bg(ctx, t):
    ctx.set_source_rgba(*hexc('#0d1030')); ctx.paint()
    g = cairo.RadialGradient(540, 900, 50, 540, 900, 1000); g.add_color_stop_rgba(0, 0.2, 0.2, 0.5, 1); g.add_color_stop_rgba(1, 0.05, 0.05, 0.15, 1)
    ctx.set_source(g); ctx.paint()
    for k in range(0, W, 60): ctx.rectangle(k, 0, 2, H); ctx.set_source_rgba(0.4, 0.6, 1, 0.06); ctx.fill()
    for k in range(0, H, 60): ctx.rectangle(0, k, W, 2); ctx.set_source_rgba(0.4, 0.6, 1, 0.06); ctx.fill()

def ball(ctx, x, y, r, col='#4fb4ff', alpha=1.0):
    g = cairo.RadialGradient(x - r*0.35, y - r*0.35, r*0.1, x, y, r); g.add_color_stop_rgba(0, 1, 1, 1, alpha); g.add_color_stop_rgba(0.35, *hexc(col, alpha)); g.add_color_stop_rgba(1, *hexc('#123a7a', alpha))
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2*math.pi); ctx.fill()

def mini_nose(ctx, x, y, s, alpha=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s*0.82)
    g = cairo.RadialGradient(-6, -8, 2, 0, 0, 34); g.add_color_stop_rgba(0, *hexc('#ffd9bb', alpha)); g.add_color_stop_rgba(1, *hexc('#e09a6c', alpha))
    ctx.set_source(g); ctx.arc(0, 0, 30, 0, 2*math.pi); ctx.fill(); ctx.restore()

def thought(ctx, x, y, w, h, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    for (cx, cy, r) in ((-w*0.3, -h*0.1, h*0.45), (0, -h*0.3, h*0.5), (w*0.3, -h*0.1, h*0.45), (-w*0.15, h*0.2, h*0.4), (w*0.15, h*0.2, h*0.4)):
        ctx.new_sub_path(); ctx.arc(cx, cy, r, 0, 2*math.pi)
    ctx.set_source_rgba(1, 1, 1, 0.96); ctx.fill()
    ctx.restore()

# ------------------------------------------------------------------ beats
COL_O, COL_G, COL_B, COL_R, COL_Y = T.COL_O, T.COL_G, T.COL_B, T.COL_R, T.COL_Y
BEATS = [
 dict(id='h1', sc='hook', ml='നിങ്ങൾക്ക് രണ്ടു മൂക്ക് ഉണ്ടെന്ന് തോന്നും! എന്റെ കൂടെ ചെയ്തു നോക്കൂ!', l1="You'll feel TWO noses", l2='– try it with me!', col=COL_O),
 dict(id='s1', sc='hand', ml='സ്റ്റെപ്പ് ഒന്ന്. ചൂണ്ടുവിരലും നടുവിരലും നിവർത്തി പിടിക്കൂ.', l1='STEP 1: hold up your', l2='INDEX + MIDDLE finger', col=COL_G, badge='STEP 1'),
 dict(id='s2', sc='cross', ml='ഇനി നടുവിരൽ, ചൂണ്ടുവിരലിന്റെ മുകളിലൂടെ കുറുകെ വെക്കൂ. നന്നായി ക്രോസ് ചെയ്യണം.', l1='Now CROSS your middle', l2='finger over your index', col=COL_B),
 dict(id='s3', sc='closed', ml='സ്റ്റെപ്പ് രണ്ട്. കണ്ണുകൾ അടയ്ക്കൂ.', l1='STEP 2:', l2='CLOSE your eyes', col=COL_G, badge='STEP 2'),
 dict(id='s4', sc='touch', ml='സ്റ്റെപ്പ് മൂന്ന്. ക്രോസ് ചെയ്ത വിരൽത്തുമ്പുകൾ കൊണ്ട്, മൂക്കിന്റെ അറ്റം തൊടൂ.', l1='STEP 3: touch your nose tip', l2='with BOTH fingertips', col=COL_O, badge='STEP 3'),
 dict(id='s5', sc='touch', rub=True, ml='ഇനി പതുക്കെ, മുകളിലേക്കും താഴേക്കും ഉരസൂ. പത്തു സെക്കൻഡ്. തുടങ്ങൂ!', l1='Rub GENTLY up and down', l2='10 SECONDS – GO!', col=COL_R, cd=True),
 dict(id='c1', sc='bigcd', at=0.2, ml='പതുക്കെ, പതുക്കെ. കണ്ണു തുറക്കരുത്!', l1='Gently... gently...', l2="DON'T open your eyes!", col=COL_Y),
 dict(id='c2', sc='double', at=3.6, ml='എന്തെങ്കിലും തോന്നുന്നുണ്ടോ? ഒരു മൂക്കല്ല, രണ്ടു മൂക്ക് പോലെ!', l1='Do you feel it?', l2='TWO NOSES!', col=COL_O),
 dict(id='c3', sc='wow', at=CD + 0.1, ml='ഇനി കണ്ണു തുറന്നോളൂ! ഒരു മൂക്കേ ഉള്ളൂ, അല്ലേ?', l1='Open your eyes!', l2='Still only ONE nose!', col=COL_G),
 dict(id='x1', sc='normal', ml='കാരണം ഇതാണ്. സാധാരണ, ഈ രണ്ടു വിരലുകളുടെ പുറംവശങ്ങൾ, ഒരിക്കലും ഒരേ സാധനത്തെ തൊടില്ല.', l1='Normally these OUTER sides', l2='never touch ONE thing', col=COL_Y),
 dict(id='x2', sc='crossed', ml='വിരൽ ക്രോസ് ചെയ്യുമ്പോൾ, ഒരേ മൂക്ക് ആ രണ്ടു പുറംവശങ്ങളെയും ഒരുമിച്ചു തൊടുന്നു.', l1='Crossed: ONE nose touches', l2='BOTH outer sides', col=COL_B),
 dict(id='x3', sc='brain', ml='പക്ഷേ തലച്ചോറ് പഴയ മാപ്പ് തന്നെ നോക്കുന്നു. അതുകൊണ്ട്, രണ്ടു വ്യത്യസ്ത സാധനങ്ങൾ ആണെന്ന് പറയുന്നു!', l1='Your brain uses its OLD map', l2='and says: TWO THINGS!', col=COL_R),
 dict(id='n1', sc='name', ml='ഇതിന്റെ പേരാണ്, അരിസ്റ്റോട്ടിൽ ഇല്യൂഷൻ. രണ്ടായിരം വർഷത്തിലേറെ പഴയ ട്രിക്ക്!', l1="It's called", l2="ARISTOTLE'S ILLUSION", col=COL_Y),
 dict(id='e1', sc='end1', ml='നിങ്ങൾക്ക് രണ്ടു മൂക്ക് തോന്നിയോ? കമന്റിൽ പറയൂ!', l1='Did you feel two noses?', l2='Tell me in the comments!', col=COL_G),
 dict(id='e2', sc='share', ml='ഇത് ഒരു കൂട്ടുകാരന് അയച്ചു കൊടുക്കൂ, അവരും ഞെട്ടും!', l1='Send this to a friend', l2='and watch them TRY!', col=COL_O),
 dict(id='e3', sc='follow', ml='കൂടുതൽ രഹസ്യങ്ങൾക്ക്, ഫോളോ ചെയ്യൂ!', l1='Follow for more', l2='MYSTERIES!', col=COL_Y, post=1.4),
]

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
            nx, ny = face(ctx, t, mood='wow', ghost=0.8)
            hand_at_nose(ctx, nx, ny, 1.25, t, rub=1.0)
            for k, (qx, qy) in enumerate(((150, 640), (930, 680))):
                otext(ctx, '?', qx, qy + 14*math.sin(t*4 + k), 150, '#ffd23f', alpha=prog(t, t0 + 0.3 + k*0.15, 0.2))
            pill(ctx, 540, 1480, 520, 110, '#e2362c', '2 NOSES?!', size=64, p=prog(t, t0 + 0.6, 0.3))
        elif sc in ('hand', 'cross'):
            ctx.set_source_surface(T.blur_room()); ctx.paint(); T.vignette(ctx, 0.4)
            cross = 0.0 if sc == 'hand' else sprog(t, t0 + 0.6, 1.0)
            yy = lerp(1500, 1050, sprog(t, t0, 0.7)) if sc == 'hand' else 1050
            tips = vhand(ctx, 520, yy, 1.55, t, cross=cross)
            if b.get('badge'): badge(ctx, 540, 470, b['badge'], prog(t, t0 + 0.2, 0.35))
            if sc == 'hand':
                for k, nm in enumerate(('index', 'middle')):
                    x_, y_ = tips[nm]; p = prog(t, t0 + 1.0 + 0.5*k, 0.3)
                    tag(ctx, x_ + (-200 if k == 0 else 210), y_ + 40, nm.upper(), p, col='#ffd23f', size=44)
            else:
                p = prog(t, t0 + 1.8, 0.3)
                tag(ctx, 540, 1450, 'MIDDLE OVER INDEX', p, col='#ffd23f', size=46)
                if cross > 0.95: check(ctx, 880, 700, prog(t, t0 + 2.2, 0.35))
        elif sc == 'closed':
            nx, ny = face(ctx, t, mood='closed' if t > t0 + 0.9 else 'smile')
            if b.get('badge'): badge(ctx, 540, 470, b['badge'], prog(t, t0 + 0.2, 0.35))
            p = prog(t, t0 + 1.0, 0.3)
            tag(ctx, 540, 1480, 'EYES CLOSED', p, col='#ffffff', bg='#2a2a6a', size=50)
        elif sc == 'touch':
            ap = sprog(t, t0, 0.8) if b['id'] == 's4' else 1.0
            nx, ny = face(ctx, t, mood='closed')
            hand_at_nose(ctx, nx, ny + (1 - ap)*700, 1.25, t, rub=1.0 if (b.get('rub') or trying) else 0.0)
            if b.get('badge'): badge(ctx, 540, 470, b['badge'], prog(t, t0 + 0.2, 0.35), col='#e2362c')
            if b['id'] == 's4':
                p = prog(t, t0 + 1.4, 0.3)
                if p > 0:
                    ctx.set_source_rgba(1, 0.85, 0.2, p); ctx.set_line_width(10); ctx.arc(nx, ny, 115 + 6*math.sin(t*8), 0, 2*math.pi); ctx.stroke()
                tag(ctx, 540, 1500, 'NOSE TIP', p, col='#ffd23f', size=48)
            if b.get('rub') or trying:
                for sd in (-1, 1):
                    yy = ny + 30*math.sin(t*7)
                    ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                    ctx.move_to(nx + sd*230, yy - 60); ctx.line_to(nx + sd*230, yy + 60); ctx.stroke()
                    for dy in (-60, 60):
                        ctx.move_to(nx + sd*230 - 18, yy + dy - (14 if dy < 0 else -14)*-1); ctx.line_to(nx + sd*230, yy + dy); ctx.line_to(nx + sd*230 + 18, yy + dy - (14 if dy < 0 else -14)*-1); ctx.stroke()
                tag(ctx, 540, 1500, 'GENTLY!', 0.6 + 0.4*abs(math.sin(t*3)), col='#ffffff', bg='#2fa86a', size=50)
        elif sc == 'bigcd':
            nx, ny = face(ctx, t, mood='closed'); hand_at_nose(ctx, nx, ny, 1.25, t, rub=1.0)
            ctx.set_source_rgba(0.05, 0.04, 0.15, 0.55); ctx.paint()
            R.countdown(ctx, 540, 860, 240, t, cd0 if t >= cd0 else t, label='SECONDS')
            tag(ctx, 540, 1250, 'KEEP RUBBING', 0.6 + 0.4*abs(math.sin(t*3)), col='#ffd23f', size=52)
        elif sc == 'double':
            nx, ny = face(ctx, t, mood='closed', ghost=sprog(t, t0 + 0.6, 0.6))
            hand_at_nose(ctx, nx, ny, 1.25, t, rub=1.0)
            for k, sd in enumerate((-1, 1)):
                otext(ctx, '1' if sd < 0 else '2', nx + sd*170, ny - 150, 110, '#ffd23f', alpha=prog(t, t0 + 0.9 + 0.3*k, 0.25))
            R.countdown(ctx, 930, 520, 85, t, cd0)
        elif sc == 'wow':
            nx, ny = face(ctx, t, mood='wow')
            vhand(ctx, 860, 1520 + 40*math.sin(t*2), 0.8, t, cross=1.0)
            check(ctx, 200, 1450, prog(t, t0 + 0.6, 0.35))
            pill(ctx, 540, 1560, 460, 100, '#2fa86a', 'ONLY ONE!', size=56, p=prog(t, t0 + 1.0, 0.3))
            sparkles(ctx, t, n=10, ymin=500, ymax=1300)
        elif sc in ('normal', 'crossed'):
            dark_bg(ctx, t)
            cr = 1.0 if sc == 'crossed' else 0.0
            tips = vhand(ctx, 520, 1080, 1.6, t, cross=cr, xray=0.5, outer=prog(t, t0 + 0.5, 0.4))
            if sc == 'normal':
                xi, yi = tips['index']; xm, ym = tips['middle']
                ball(ctx, xi - 75, yi + 40, 44, alpha=prog(t, t0 + 1.2, 0.3)); ball(ctx, xm + 80, ym + 40, 44, col='#ff9a2a', alpha=prog(t, t0 + 1.5, 0.3))
                tag(ctx, 540, 1500, 'OUTER SIDES', prog(t, t0 + 0.6, 0.3), col='#ff6a5a', size=46)
                tag(ctx, 540, 470, 'ALWAYS 2 DIFFERENT THINGS', prog(t, t0 + 2.0, 0.3), col='#ffd23f', size=40)
            else:
                xi, yi = tips['index']; xm, ym = tips['middle']
                mini_nose(ctx, (xi + xm)/2, min(yi, ym) - 6, 2.4, alpha=prog(t, t0 + 0.8, 0.3))
                tag(ctx, 540, 1500, 'BOTH OUTER SIDES TOUCH', prog(t, t0 + 1.2, 0.3), col='#ff6a5a', size=42)
                tag(ctx, 540, 470, 'ONE NOSE', prog(t, t0 + 1.6, 0.3), col='#3fe08a', size=50)
        elif sc == 'brain':
            dark_bg(ctx, t)
            tips = vhand(ctx, 540, 1350, 1.0, t, cross=1.0, xray=0.5, outer=1.0)
            mini_nose(ctx, (tips['index'][0] + tips['middle'][0])/2, min(tips['index'][1], tips['middle'][1]) - 2, 1.6)
            T.brain(ctx, 540, 640, 1.1, t)
            for nm in ('index', 'middle'):
                x_, y_ = tips[nm]
                T.signal(ctx, [(x_, y_), (x_ + (-160 if nm == 'index' else 160), 1000), (540 + (-60 if nm == 'index' else 60), 760)], t, p=sprog(t, t0 + 0.2, 0.9))
            p = prog(t, t0 + 1.6, 0.35)
            thought(ctx, 830, 540, 300, 170, p)
            if p > 0:
                mini_nose(ctx, 770, 540, 1.6*p); mini_nose(ctx, 890, 540, 1.6*p)
                otext(ctx, '2?!', 830, 650, 64, '#e2362c', lw=8, alpha=p)
            tag(ctx, 250, 520, 'OLD MAP', prog(t, t0 + 0.8, 0.3), col='#ff8fd0', size=44)
        elif sc == 'name':
            ctx.set_source_rgba(*hexc('#12103a')); ctx.paint()
            ctx.save(); ctx.translate(540, 900); ctx.rotate(t*0.2)
            for k in range(16):
                ctx.move_to(0, 0); ctx.arc(0, 0, 1600, k*2*math.pi/16, (k + 0.5)*2*math.pi/16); ctx.close_path(); ctx.set_source_rgba(0.35, 0.3, 0.9, 0.18); ctx.fill()
            ctx.restore()
            vhand(ctx, 540, 760, 0.75*back(prog(t, t0, 0.4)) + 0.001, t, cross=1.0, outer=1.0)
            p = back(prog(t, t0 + 0.6, 0.4))
            if p > 0:
                ctx.save(); ctx.translate(540, 1110); ctx.scale(p, p)
                otext(ctx, "ARISTOTLE'S", 0, 0, 120, '#ffd23f', lw=18)
                otext(ctx, 'ILLUSION', 0, 135, 130, '#ffffff', lw=18)
                ctx.restore()
            tag(ctx, 540, 1390, 'written down over 2,000 years ago', prog(t, t0 + 1.4, 0.3), col='#ffffff', bg='#2a2a6a', size=38)
            sparkles(ctx, t, n=16, ymin=450, ymax=1400)
        elif sc == 'marble':
            ctx.set_source_surface(R.table()); ctx.paint()
            ball(ctx, 540, 860, 70, col='#3fd2a0')
            ctx.save(); ctx.translate(540, 860 + 80); ctx.scale(1, 0.25); ctx.arc(0, 0, 70, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.fill()
            tp = vtips(1.0); s_ = 1.25; mx = (tp['index'][0] + tp['middle'][0])/2; my = min(tp['index'][1], tp['middle'][1])
            vhand(ctx, 540 - mx*s_, 860 - my*s_ + 40 + 12*math.sin(t*7), s_, t, cross=1.0, outer=0.6)
            p = prog(t, t0 + 1.2, 0.3)
            if p > 0:
                ball(ctx, 300, 640, 50, col='#3fd2a0', alpha=0.5*p); ball(ctx, 780, 640, 50, col='#3fd2a0', alpha=0.5*p)
                otext(ctx, '2?', 540, 660, 90, '#ffd23f', alpha=p)
            tag(ctx, 540, 1500, 'MARBLE', prog(t, t0 + 0.4, 0.3), col='#ffffff', bg='#2a2a6a', size=50)
        elif sc in ('end1', 'share'):
            ctx.set_source_surface(T.room()); ctx.paint(); T.vignette(ctx, 0.3)
            T.kid(ctx, 540, T.FEET, 1.0, t, aR=0.35 if sc != 'share' else 0.9 + 0.2*math.sin(t*4), aL=0.12, mood='wow' if sc == 'end1' else 'smile', nose=True)
            if sc == 'end1':
                T.comment_box(ctx, 480, 'TWO NOSES!', t, t0)
            else:
                for k, x in enumerate((210, 870)): otext(ctx, 'HA', x, 620 + 10*math.sin(t*6 + k), 90, '#ffd23f', alpha=prog(t, t0 + 0.3 + 0.2*k, 0.2))
                tag(ctx, 540, 500, 'SEND TO A FRIEND', prog(t, t0 + 0.2, 0.3), col='#ffffff', bg='#ff7a2a', size=50)
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
        if trying and sc == 'touch':
            R.countdown(ctx, 930, 520, 85, t, cd0)
    return draw

def sfx_list(tl):
    sfx = []; cd0 = tl.cd0
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0'] - 0.12, 'whoosh', 0.5))
        if b['id'] == 'h1': sfx.append((b['t0'] + 0.6, 'pop', 0.7))
        if b.get('badge'): sfx.append((b['t0'] + 0.2, 'pop', 0.7))
        if b['sc'] == 'cross': sfx.append((b['t0'] + 2.2, 'right', 0.45))
        if b['sc'] == 'double': sfx.append((b['t0'] + 0.9, 'pop', 0.6))
        if b['sc'] == 'wow': sfx.append((b['t0'] + 0.6, 'right', 0.6))
        if b['sc'] in ('crossed', 'brain', 'name', 'normal'): sfx.append((b['t0'] + 0.5, 'pop', 0.5))
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
            tt = (b['t0'] + b['t1'])/2 + 0.4
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt)
            surf.write_to_png(f'{OUT}/n{k:02d}.png'); k += 1
    else:
        aud = f'{OUT}/{NAME}.wav'; T.build_mix(aud, tl, sfx_list(tl), total)
        wd.render_raw(f'{OUT}/{NAME}.mp4', total, draw, aud)
