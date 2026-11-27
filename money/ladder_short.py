"""9:16 STORY RIDDLE Short for Kandupidi (27 Nov 2026, run A).
Riddle: painter Kuttan falls off a 30-foot ladder onto concrete, no net/mattress/rope, nobody caught him, not a scratch.
ANSWER (hidden): he fell from the bottom step of the ladder.
Reuses beard_short.py look (flat vector, sunbursts, bokeh, palms, chips, no-signs, glowing ?, brain + comment box).
python3 ladder_short.py stills | render"""
import sys, math, os, random, cairo
sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/money'); sys.path.insert(0, '/home/claude/ml')
import beard_short as B
import money as M
import money_short as MS
import wd
from wd import text, text_w, caption, pill
from pz import Timeline, clamp, prog, sprog, back, hexc, rrect, lerp, dust
W, H = 1080, 1920
GROUND = 1100
STORY = ('male', 0.88, 1.27)
OUT = '/home/claude/money/outs_ladder'; os.makedirs(OUT, exist_ok=True)
NAME = 'KP_Fell_From_a_30_Foot_Ladder_Mini'
grad, palm, bokeh, sunburst, chip, nosign, glowq, sweat, cheeks = B.grad, B.palm, B.bokeh, B.sunburst, B.chip, B.nosign, B.glowq, B.sweat, B.cheeks

LAD_X0, LAD_X1, LAD_TOP, LAD_BOT = 300, 430, 120, GROUND - 6

_bg = {}
def church_bg():
    if 'church' in _bg: return _bg['church']
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    ctx.set_source(grad(ctx, 0, 1100, '#ff9a5a', '#ffe0a0')); ctx.paint()
    g = cairo.RadialGradient(900, 300, 30, 900, 300, 500); g.add_color_stop_rgba(0, 1, 0.97, 0.85, 0.9); g.add_color_stop_rgba(1, 1, 0.8, 0.5, 0)
    ctx.set_source(g); ctx.paint()
    for (x, y, s) in ((40, 1000, 0.9), (1040, 1010, 0.95)): palm(ctx, x, y, s, '#2c5a3e')
    # tall church facade (cream, half painted: top band fresh white, lower old/stained)
    ctx.rectangle(170, 60, 760, GROUND - 60); ctx.set_source(grad(ctx, 60, GROUND, '#fff8ea', '#efe0c4')); ctx.fill()
    ctx.move_to(170, 60); ctx.line_to(550, -60); ctx.line_to(930, 60); ctx.close_path(); ctx.set_source_rgba(*hexc('#f4ead6')); ctx.fill()
    # stains on the unpainted lower part
    rnd = random.Random(4)
    for k in range(26):
        ctx.arc(rnd.uniform(470, 920), rnd.uniform(560, 1060), rnd.uniform(10, 46), 0, 2*math.pi); ctx.set_source_rgba(0.45, 0.4, 0.3, 0.10); ctx.fill()
    ctx.rectangle(170, 520, 760, 8); ctx.set_source_rgba(0.6, 0.5, 0.35, 0.35); ctx.fill()
    # side shading + pilasters
    for x in (170, 900): ctx.rectangle(x, 60, 30, GROUND - 60); ctx.set_source_rgba(0.55, 0.45, 0.3, 0.18); ctx.fill()
    # arched windows (upper) + big door (lower right)
    for (x, y) in ((560, 180), (760, 180), (760, 640)):
        ctx.move_to(x-50, y+180); ctx.line_to(x-50, y+50); ctx.arc(x, y+50, 50, math.pi, 0); ctx.line_to(x+50, y+180); ctx.close_path()
        ctx.set_source(grad(ctx, y, y+180, '#4a6ab8', '#2a3a78')); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(5); ctx.move_to(x, y); ctx.line_to(x, y+180); ctx.stroke()
    ctx.move_to(520, GROUND); ctx.line_to(520, 760); ctx.arc(600, 760, 80, math.pi, 0); ctx.line_to(680, GROUND); ctx.close_path()
    ctx.set_source(grad(ctx, 680, GROUND, '#8a4a2a', '#5a2a16')); ctx.fill()
    # feast festoons
    for k in range(11):
        ctx.move_to(190 + k*68, 40 + 0); ctx.line_to(224 + k*68, 40); ctx.line_to(207 + k*68, 90); ctx.close_path()
        ctx.set_source_rgba(*hexc(('#ffd23f', '#d9283b', '#2fa86a')[k % 3])); ctx.fill()
    # concrete floor
    ctx.rectangle(0, GROUND - 10, W, H); ctx.set_source(grad(ctx, GROUND, H, '#a9a9ad', '#7c7c84')); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.12); ctx.set_line_width(4)
    for k in range(6): ctx.move_to(k*220 - 80, GROUND - 10); ctx.line_to(k*260 - 200, H); ctx.stroke()
    ctx.move_to(0, GROUND + 140); ctx.line_to(W, GROUND + 140); ctx.stroke()
    _bg['church'] = surf
    return surf

def ladder(ctx, a=1.0):
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    # shadow on the wall
    ctx.set_source_rgba(0, 0, 0, 0.12 * a); ctx.set_line_width(20)
    for (xb, xt) in ((LAD_X0, LAD_X0 + 30), (LAD_X1, LAD_X1 - 30)):
        ctx.move_to(xb + 22, LAD_BOT); ctx.line_to(xt + 22, LAD_TOP + 8); ctx.stroke()
    n = 16
    for k in range(1, n):
        f = k / n; y = lerp(LAD_BOT, LAD_TOP, f)
        xl = lerp(LAD_X0, LAD_X0 + 30, f); xr = lerp(LAD_X1, LAD_X1 - 30, f)
        ctx.set_source_rgba(*hexc('#8a5a2a', a)); ctx.set_line_width(13); ctx.move_to(xl, y); ctx.line_to(xr, y); ctx.stroke()
        ctx.set_source_rgba(1, 0.9, 0.7, 0.35 * a); ctx.set_line_width(4); ctx.move_to(xl, y - 4); ctx.line_to(xr, y - 4); ctx.stroke()
    for (xb, xt) in ((LAD_X0, LAD_X0 + 30), (LAD_X1, LAD_X1 - 30)):
        ctx.set_source_rgba(*hexc('#a8703a', a)); ctx.set_line_width(20); ctx.move_to(xb, LAD_BOT); ctx.line_to(xt, LAD_TOP); ctx.stroke()
        ctx.set_source_rgba(1, 0.92, 0.75, 0.4 * a); ctx.set_line_width(5); ctx.move_to(xb - 5, LAD_BOT); ctx.line_to(xt - 5, LAD_TOP); ctx.stroke()
    ctx.restore()

def bucket(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-50, -100); ctx.line_to(50, -100); ctx.line_to(40, 0); ctx.line_to(-40, 0); ctx.close_path()
    ctx.set_source(grad(ctx, -100, 0, '#d0d4da', '#8a9098')); ctx.fill()
    ctx.save(); ctx.scale(1, 0.3); ctx.arc(0, -333, 50, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
    ctx.move_to(-46, -96); ctx.curve_to(-48, -60, -30, -70, -28, -50); ctx.line_to(-24, -96); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()
    ctx.set_source_rgba(0.3, 0.3, 0.3, 1); ctx.set_line_width(4); ctx.arc(0, -100, 50, math.pi, 2*math.pi); ctx.stroke()
    ctx.restore()

def brush(ctx, x, y, s=1.0, ang=-0.6):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    rrect(ctx, -8, -70, 16, 70, 6); ctx.set_source_rgba(*hexc('#c0703a')); ctx.fill()
    rrect(ctx, -22, -110, 44, 40, 6); ctx.set_source_rgba(*hexc('#b8b8c0')); ctx.fill()
    rrect(ctx, -22, -140, 44, 34, 8); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.restore()

def splashes(ctx, x, y, s, face):
    """white paint splashes on Kuttan's shirt (same transform as person)."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    for (dx, dy, r) in ((-30, -320, 10), (25, -280, 13), (-10, -230, 8), (40, -130, 9), (-35, -80, 11)):
        ctx.arc(dx, dy, r, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 0.95); ctx.fill()
    ctx.restore()

def steth(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgba(*hexc('#2a2a3a')); ctx.set_line_width(7)
    ctx.move_to(-30, -370); ctx.curve_to(-40, -300, 30, -280, 20, -240); ctx.stroke()
    ctx.arc(20, -232, 13, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#c0c6d0')); ctx.fill()
    ctx.restore()

def stars(ctx, x, y, t, p):
    if p <= 0: return
    for k in range(4):
        a = t*4 + k*math.pi/2; sx, sy = x + math.cos(a)*80, y + math.sin(a)*24
        ctx.save(); ctx.translate(sx, sy); ctx.scale(p, p)
        for j in range(5):
            aa = j*2*math.pi/5 - math.pi/2
            ctx.line_to(math.cos(aa)*22, math.sin(aa)*22); ctx.line_to(math.cos(aa+0.63)*9, math.sin(aa+0.63)*9)
        ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd23f')); ctx.fill(); ctx.restore()

def measure(ctx, x, p, label='30 FT'):
    if p <= 0: return
    y0, y1 = LAD_BOT, lerp(LAD_BOT, LAD_TOP, sprog(p, 0, 1))
    ctx.save(); ctx.set_source_rgba(*hexc('#d9283b')); ctx.set_line_width(8); ctx.set_dash([22, 14])
    ctx.move_to(x, y0); ctx.line_to(x, y1); ctx.stroke(); ctx.set_dash([])
    for yy, d in ((y0, 1), (y1, -1)):
        ctx.move_to(x - 30, yy); ctx.line_to(x + 30, yy); ctx.stroke()
    ctx.move_to(x, y1); ctx.line_to(x - 22, y1 + 34*1); ctx.line_to(x + 22, y1 + 34); ctx.close_path(); ctx.fill()
    ctx.restore()
    if p > 0.8: chip(ctx, x, (y0 + LAD_TOP)/2, label, prog(p, 0.8, 0.2), '#d9283b', size=56)

def safety_card(ctx, x, y, p, rows, t, t0):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc); ctx.rotate(-0.03)
    rrect(ctx, -330, -230, 660, 470, 20); ctx.set_source_rgba(0, 0, 0, 0.2); ctx.fill()
    rrect(ctx, -340, -240, 660, 470, 20); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    rrect(ctx, -340, -240, 660, 90, 20); ctx.set_source_rgba(*hexc('#1f4fa8')); ctx.fill()
    text(ctx, 'SAFETY CHECK', -10, -175, 50, '#ffffff')
    for i, (lab, tv) in enumerate(rows):
        yy = -60 + i*110
        text(ctx, lab, -290, yy, 46, '#444444', align='l')
        ctx.rectangle(-300, yy+24, 580, 4); ctx.set_source_rgba(0.75, 0.75, 0.75, 1); ctx.fill()
        if t >= t0 + tv:
            q = prog(t, t0 + tv, 0.25)
            ctx.save(); ctx.translate(130, yy - 16); ctx.scale(back(q), back(q))
            ctx.set_source_rgba(*hexc('#e62117')); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(-22, -22); ctx.line_to(22, 22); ctx.move_to(22, -22); ctx.line_to(-22, 22); ctx.stroke(); ctx.restore()
            text(ctx, 'NO', 280, yy, 46, '#e62117', align='r', alpha=q)
    ctx.restore()

# ------------------------------------------------------------------ beats
CH = {'K': ('Kuttan', '#5a7fa8', '#f4f1e8', False), 'D': ('Dr. Mini', '#ffffff', '#3a8fd8', True)}
BEATS = [
 dict(id='h1', sc='road', ml='ബുദ്ധിയുള്ളവർ മാത്രം ഇത് കാണുക!', en='Only people with *brains* should watch this!'),
 dict(id='s1', sc='road', ml='ഇത് കോട്ടയത്തെ പെയിന്റർ കുട്ടൻ.', en='This is *Kuttan,* a painter from *Kottayam.*', pos=dict(K=540), walk='K', sign='KOTTAYAM'),
 dict(id='s2', sc='wall', ml='പെരുന്നാളിന് മുൻപ്, വലിയ പള്ളിയുടെ ചുമര് പെയിന്റ് ചെയ്യുകയാണ് അവൻ.', en='He is painting a tall *church wall* before the *feast.*', pos=dict(K=700), walk='K'),
 dict(id='s3', sc='wall', ml='അവന്റെ ഏണിക്ക് മുപ്പത് അടി ഉയരമുണ്ട്. താഴെ, കട്ടിയുള്ള കോൺക്രീറ്റ് തറ.', en='His *ladder* is *30 feet* tall. Below it, a hard *concrete* floor.', pos=dict(K=700), measure=True),
 dict(id='s4', sc='fall', ml='പെട്ടെന്ന് കാൽ വഴുതി! കുട്ടൻ ഏണിയിൽ നിന്ന് കോൺക്രീറ്റ് തറയിലേക്ക് വീണു!', en='Suddenly his foot *slips!* Kuttan *falls* off the ladder onto the *concrete!*'),
 dict(id='s5', sc='card', ml='താഴെ വലയില്ല, മെത്തയില്ല, കയറുമില്ല.', en='*No* safety net. *No* mattress. *No* rope.'),
 dict(id='s6', sc='doc', ml='ഡോക്ടർ മിനി ഓടിവന്ന് അവനെ പരിശോധിച്ചു. ഒരു പോറൽ പോലുമില്ല!', en='Doctor *Mini* checks him. Not even a *scratch!*', pos=dict(K=520, D=820), walk='D', bub=('D', 'NOT A SCRATCH!')),
 dict(id='s7', sc='shock', ml='മിനി ഞെട്ടിപ്പോയി! മുപ്പത് അടി ഏണിയിൽ നിന്ന് വീണിട്ടും, ഒന്നും പറ്റിയില്ലേ?', en='Mini is *shocked!* He fell off a *30-foot* ladder, and *nothing* happened?'),
 dict(id='s8', sc='no', ml='അവൻ സൂപ്പർഹീറോ അല്ല. ആരും അവനെ താങ്ങിപ്പിടിച്ചതുമില്ല.', en='He is *not* a superhero. And *nobody* caught him.'),
 dict(id='q1', sc='night', ml='അപ്പോൾ, ഇത് എങ്ങനെ സാധിക്കും?', en='So how is this *possible?*'),
 dict(id='th', sc='think', ml='ഉത്തരം ആലോചിക്കൂ!', en='Think about the *answer...*', post=4.3),
 dict(id='c1', sc='cta', ml='നിങ്ങളുടെ ഉത്തരം കമന്റിൽ ടൈപ്പ് ചെയ്യൂ!', en='Type *ANSWER* in the comments!'),
 dict(id='c2', sc='share', ml='ബുദ്ധിമാനാണെന്ന് കരുതുന്ന കൂട്ടുകാരന് ഇത് അയച്ചു കൊടുക്കൂ!', en='Send this to your friend who thinks he is *smart!*', pos=dict(K=300, D=780)),
 dict(id='c3', sc='follow', ml='ഇതുപോലുള്ള കൂടുതൽ കടങ്കഥകൾക്കായി, ഫോളോ ചെയ്യൂ!', en='*Follow* for more riddles!', post=1.6),
]

def draw_person(ctx, k, x, y, s, t, talk=0.0, face=1, name=True):
    nm, sh, lo, fem = CH[k]
    M.person(ctx, x, y, s, sh, lo, fem, talk, 0.0, face, nm if name else None, t)
    cheeks(ctx, x, y, s, face)
    if k == 'K': splashes(ctx, x, y, s, face)
    else: steth(ctx, x, y, s)

def pos_at(b, t):
    out = {}
    for k, x in (b.get('pos') or {}).items():
        if b.get('walk') == k:
            p = sprog(t, b['t0'], 1.2); x0 = 1350
            out[k] = (lerp(x0, x, p), p < 1)
        else: out[k] = (x, False)
    return out

def people(ctx, t, b, ps, s=1.1, name=True):
    xs = {k: v[0] for k, v in ps.items()}
    for k, (x, moving) in ps.items():
        others = [xs[o] for o in xs if o != k]
        face = 1 if (not others or sum(others)/len(others) > x) else -1
        if b['sc'] == 'wall': face = -1
        y = GROUND - 10 - (abs(math.sin(t*12))*14 if moving else 0)
        talk = abs(math.sin(t*13))*0.8 if (b.get('bub', [None])[0] == k and b['t0'] + 1.0 < t < b['t1']) else 0
        draw_person(ctx, k, x, y, s, t, talk, face, name)

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
            ctx.set_source_surface(B.bg('road')); ctx.paint(); bokeh(ctx, t)
            if b['id'] == 'h1':
                MS.bulb(ctx, W/2, 420, prog(t, t0+0.1, 0.4), t)
                for k, (qx, qy) in enumerate(((150, 360), (930, 340), (200, 760), (880, 760))):
                    text(ctx, '?', qx, qy + 12*math.sin(t*4+k), 130, '#ffffff', alpha=prog(t, t0+0.3+k*0.1, 0.2))
            else:
                people(ctx, t, b, ps)
                bucket(ctx, 700, GROUND - 4, 0.9)
                MS.sign(ctx, W/2, 330, b['sign'], prog(t, t0+0.3, 0.35))
        elif sc == 'wall':
            ctx.set_source_surface(church_bg()); ctx.paint()
            ladder(ctx)
            bucket(ctx, 520, GROUND, 0.8)
            people(ctx, t, b, ps, s=0.62, name=False)
            x = ps['K'][0]
            brush(ctx, x - 70, GROUND - 200, 0.8, -0.3 + 0.3*math.sin(t*5))
            if b.get('measure'):
                measure(ctx, 190, prog(t, t0+0.2, 1.4))
                chip(ctx, 800, GROUND - 40, 'CONCRETE', prog(t, t0 + 2.6, 0.35), '#5a5a66', size=46)
        elif sc == 'fall':
            ctx.set_source_surface(church_bg()); ctx.paint()
            # camera shake on impact
            sh = 14*math.sin(t*70)*(1 - prog(t, t0+0.9, 0.5)) if t > t0 + 0.9 else 0
            ctx.save(); ctx.translate(sh, 0)
            ladder(ctx)
            bucket(ctx, 560, GROUND, 0.8)
            ctx.restore()
            if t < t0 + 0.9:
                text(ctx, 'SLIP!', 640, 520, 150, '#d9283b', alpha=prog(t, t0+0.1, 0.15))
                for k in range(5):
                    ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(8)
                    ctx.move_to(470 + k*30, 600 + k*20); ctx.line_to(470 + k*30, 760 + k*20); ctx.stroke()
            else:
                # Kuttan sitting on the floor beside the ladder, dizzy (never shows the height he fell from)
                ctx.save(); ctx.translate(620, GROUND + 60); ctx.rotate(-0.12)
                draw_person(ctx, 'K', 0, 0, 0.62, t, 0.6, -1, False); ctx.restore()
                stars(ctx, 612, GROUND + 60 - 300, t, prog(t, t0+1.1, 0.3))
                dust(ctx, 600, GROUND + 40, t, t0 + 0.9, dur=1.0, n=14, spread=260)
                text(ctx, 'THUD!', 760, 620, 150, '#ffffff', alpha=prog(t, t0+0.9, 0.12))
                text(ctx, 'THUD!', 754, 614, 150, '#d9283b', alpha=prog(t, t0+0.9, 0.12))
        elif sc == 'card':
            ctx.set_source_surface(church_bg()); ctx.paint()
            ctx.set_source_rgba(0.05, 0.08, 0.2, 0.6); ctx.paint()
            sunburst(ctx, W/2, 640, t, '#3a5ab8', '#2a4296', a=0.35)
            d = (t1 - t0)
            safety_card(ctx, W/2, 600, prog(t, t0, 0.35), (('SAFETY NET', 0.3), ('MATTRESS', d*0.38), ('ROPE', d*0.72)), t, t0)
        elif sc == 'doc':
            ctx.set_source_surface(church_bg()); ctx.paint()
            ctx.save(); ctx.translate(0, 0)
            ladder(ctx, 0.9)
            ctx.restore()
            people(ctx, t, b, ps, s=1.0)
            if 'bub' in b: M.bubble(ctx, 780, 380, b['bub'][1], prog(t, t0+1.3, 0.3), size=62, col='#1f4fa8')
            if t > t0 + 1.6:
                ctx.save(); ctx.translate(520, 560); ctx.scale(back(prog(t, t0+1.6, 0.3)), back(prog(t, t0+1.6, 0.3)))
                ctx.set_source_rgba(*hexc('#2fa86a')); ctx.set_line_width(20); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.move_to(-40, 0); ctx.line_to(-10, 32); ctx.line_to(46, -36); ctx.stroke(); ctx.restore()
        elif sc == 'shock':
            ctx.set_source_surface(B.bg('dark')); ctx.paint()
            sunburst(ctx, W/2, 600, t*3, '#ffcf5a', '#ff8a3c')
            zz = 1 + 0.25*sprog(t, t0, 0.5)
            ctx.save(); ctx.translate(W/2, 1000); ctx.scale(zz, zz); ctx.translate(-W/2, -1000)
            M.person(ctx, W/2, 1300, 1.5, CH['D'][1], CH['D'][2], True, 0.9, 0.0, 1, None, t)
            cheeks(ctx, W/2, 1300, 1.5, 1); steth(ctx, W/2, 1300, 1.5)
            ctx.restore()
            sweat(ctx, W/2 + 160, 520, prog(t, t0+0.5, 1.2))
            for k, (qx, qy) in enumerate(((180, 300), (900, 300))):
                text(ctx, '!' if k == 0 else '?', qx, qy + 10*math.sin(t*6+k), 170, '#ffffff', alpha=prog(t, t0+0.2, 0.2))
            chip(ctx, W/2, 230, '30 FT FALL + NO SCRATCH?', prog(t, t0+1.2, 0.35), '#d9283b', size=50)
        elif sc == 'no':
            ctx.set_source_surface(B.bg('road')); ctx.paint(); ctx.set_source_rgba(0.05, 0.05, 0.2, 0.5); ctx.paint(); bokeh(ctx, t)
            chip(ctx, W/2, 420, 'SUPERHERO', prog(t, t0+0.1, 0.35), '#5a4a8a', size=80)
            nosign(ctx, W/2, 420, 190, prog(t, t0+0.9, 0.35))
            chip(ctx, W/2, 830, 'SOMEONE CAUGHT HIM', prog(t, t0+1.8, 0.35), '#5a4a8a', size=62)
            nosign(ctx, W/2, 830, 190, prog(t, t0+2.6, 0.35))
        elif sc == 'night':
            ctx.set_source_surface(B.bg('night')); ctx.paint(); bokeh(ctx, t, col=(0.7, 0.8, 1))
            glowq(ctx, W/2, 780, t, prog(t, t0+0.1, 0.45))
        elif sc == 'think':
            ctx.set_source_surface(B.bg('night')); ctx.paint(); ctx.set_source_rgba(0.03, 0.03, 0.1, 0.4); ctx.paint()
            M.bubble(ctx, W/2, 260, '30 ft ladder, not a scratch?', 1.0, size=50)
            M.clock5(ctx, W/2, 660, t, b['t1'] + 0.1, r=170)
            pill(ctx, W/2, 980, 640, 96, '#d9483b', 'THINK...', size=54, p=prog(t, t0, 0.3))
        elif sc in ('cta', 'follow'):
            ctx.set_source_surface(B.bg('dark')); ctx.paint(); bokeh(ctx, t, col=(0.9, 0.7, 1))
            B.brain(ctx, W/2, 250, 0.9, t)
            MS.comment_box(ctx, 430, 'ANSWER', t, tl.by['c1']['t0'])
            if sc == 'follow':
                MS.follow_btn(ctx, W/2, 860, t, following=(t - t0) > 2.4)
                text(ctx, 'MORE RIDDLES DAILY', W/2, 1040, 60, '#ffd23f')
            else:
                pill(ctx, W/2, 830, 760, 96, '#2fa86a', 'ANSWER in the comments!', size=46, p=prog(t, t0+0.2, 0.3))
        elif sc == 'share':
            ctx.set_source_surface(B.bg('road')); ctx.paint(); bokeh(ctx, t)
            people(ctx, t, b, ps)
            M.bubble(ctx, W/2, 360, 'Send to a friend who thinks he is smart!', prog(t, t0, 0.3), size=40)
            for k, x in enumerate((300, 780)): text(ctx, '?', x, 520 + 10*math.sin(t*5+k), 120, '#ffd23f', alpha=prog(t, t0+0.4, 0.2))
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and i: ctx.set_source_rgba(1, 1, 1, 0.25*fl); ctx.paint()
        if b.get('en'):
            for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)):
                ctx.save(); ctx.translate(dx, dy); B._shadow_caption(ctx, b, t); ctx.restore()
            caption(ctx, b['en'], t, t0, t1, y=1200, size=66, maxw=980)
    return draw

def sfx_list(tl):
    sfx = []
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0']-0.12, 'whoosh', 0.5))
        if b['id'] == 'h1': sfx.append((b['t0']+0.15, 'pop', 0.8))
        if 'sign' in b or 'bub' in b: sfx.append((b['t0']+(0.25 if 'sign' in b else 1.3), 'pop', 0.6))
        if b.get('measure'): sfx.append((b['t0']+1.6, 'pop', 0.6)); sfx.append((b['t0']+2.6, 'pop', 0.5))
        if b['sc'] == 'fall': sfx.append((b['t0']+0.1, 'whoosh', 0.7)); sfx.append((b['t0']+0.9, 'thud', 1.0))
        if b['sc'] == 'card':
            d = b['t1'] - b['t0']
            for tv in (0.3, d*0.38, d*0.72): sfx.append((b['t0']+tv, 'wrong', 0.35))
        if b['sc'] == 'doc': sfx.append((b['t0']+1.6, 'right', 0.5))
        if b['sc'] == 'shock': sfx.append((b['t0']+0.05, 'thud', 0.8)); sfx.append((b['t0']+1.2, 'pop', 0.6))
        if b['sc'] == 'no': sfx.append((b['t0']+0.9, 'wrong', 0.45)); sfx.append((b['t0']+2.6, 'wrong', 0.45))
        if b['sc'] == 'night': sfx.append((b['t0']+0.1, 'thud', 0.6))
        if b['sc'] == 'think':
            for k in range(5): sfx.append((b['t1']+0.1+k, 'tick', 0.6))
        if b['sc'] == 'cta':
            for k in range(6): sfx.append((b['t0']+0.3+k*0.2, 'tick', 0.25))
        if b['sc'] == 'follow': sfx.append((b['t0']+2.4, 'right', 0.5))
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
