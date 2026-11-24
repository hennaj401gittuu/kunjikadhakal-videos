import sys, math, os, random, subprocess, cairo
sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/long')
import wd
wd.W, wd.H, wd.FLOOR = 1920, 1080, 930
from wd import text, text_w, caption, pill, namebox, bubble, suspect, spot, tape, solve, evaluate, build_mix, NARR
from pz import Timeline, clamp, prog, sprog, back, hexc, rrect, mark, fill_stroke
import cases
W, H, FL = 1920, 1080, 930
NUM = ['ഒന്ന്', 'രണ്ട്', 'മൂന്ന്', 'നാല്', 'അഞ്ച്', 'ആറ്', 'ഏഴ്', 'എട്ട്', 'ഒൻപത്']
CNT = {0: 'ആരും സത്യം പറയുന്നില്ല', 1: 'ഒരാൾ മാത്രം സത്യം പറയുന്നു', 2: 'രണ്ടു പേർ സത്യം പറയുന്നു', 3: 'മൂന്നു പേരും സത്യം പറയുന്നു'}
XS = (520, 960, 1400)

def stmt_txt(c, s, me):
    k, x = s[6]; mur = c['kind'] == 'murder'
    nm = {q[0]: q[1] for q in c['sus']}
    if k == 'did':
        return (f'{nm[x]} ആണ് ' + ('കൊന്നത്' if mur else 'മോഷ്ടിച്ചത്'), f'"{x} did it!"' if mur else f'"{x} stole it!"', f'{x.upper()} DID IT!' if mur else f'{x.upper()} STOLE IT!')
    if k == 'not':
        if x == me: return ('ഞാനല്ല ' + ('കൊന്നത്' if mur else 'മോഷ്ടിച്ചത്'), '"I didn\'t do it."' if mur else '"I didn\'t steal it."', 'NOT ME!')
        return (f'{nm[x]} അല്ല ' + ('കൊന്നത്' if mur else 'മോഷ്ടിച്ചത്'), f'"It wasn\'t {x}."', f'NOT {x.upper()}!')
    if k == 'liar': return (f'{nm[x]} കള്ളം പറയുകയാണ്', f'"{x} is lying!"', f'{x.upper()} IS LYING!')
    if k == 'honest': return (f'{nm[x]} സത്യം പറയുന്നു', f'"{x} tells the truth."', f'{x.upper()} IS HONEST!')

def make_beats(clist):
    N = len(clist); beats = []
    hard = clist[-1]
    beats.append(dict(id='t1', scene='teaser', c=hard, ml=f'{NUM[N-1].replace("്","ു") if False else NUM[N-1]} കുറ്റാന്വേഷണ കഥകൾ. ഒരു ശതമാനം പേർക്ക് മാത്രമേ എല്ലാം ശരിയാക്കാൻ പറ്റൂ! നിങ്ങൾക്ക് പറ്റുമോ?',
                      en=f'*{N}* mysteries. Only *1%* get all of them right! Can you?'))
    beats.append(dict(id='t2', scene='teaser', c=hard, ml='ഓരോ ശരിയുത്തരത്തിനും ഒരു പോയിന്റ്. പേനയും പേപ്പറും എടുക്കൂ, തുടങ്ങാം!',
                      en='*1 point* for each right answer. Grab a pen, let\'s *start!*'))
    for i, c in enumerate(clist):
        c['i'] = i; c['N'] = N
        names = [s[0] for s in c['sus']]; st = {s[0]: s[6] for s in c['sus']}
        sol = solve(names, st, c['n_true']); assert len(sol) == 1, (c['place'], sol); c['ans'] = sol[0]
        c['tv'] = {k: evaluate(names, st, k) for k in names}
        c['st'] = [stmt_txt(c, s, s[0]) for s in c['sus']]
        mur = c['kind'] == 'murder'
        p = f'c{i}_'
        beats.append(dict(id=p+'a', scene='title', c=c, ml=f'കേസ് നമ്പർ {NUM[i]}. ' + c['victim_ml'], en=f'Case {i+1}: ' + c['victim_en']))
        beats.append(dict(id=p+'b', scene='line', c=c, show=0, ml='പോലീസ് മൂന്നു പേരെ ചോദ്യം ചെയ്തു.', en='Police questioned *three* people.'))
        for j, s in enumerate(c['sus']):
            beats.append(dict(id=p+f's{j}', scene='line', c=c, show=j+1, talk=j, ml=f'{s[3]} {s[1]} പറഞ്ഞു, {c["st"][j][0]}.',
                              en=f'The {s[2]} *{s[0]}* said: {c["st"][j][1]}'))
        who = 'കൊലയാളി' if mur else 'കള്ളൻ'
        if c['n_true'] == 1:
            beats.append(dict(id=p+'r', scene='line', c=c, show=3, rule=True, ml=f'ഒരാൾ മാത്രമേ സത്യം പറയുന്നുള്ളൂ. {who} ആരാണ്?',
                              en=f'Only *ONE* tells the *truth.* Who is the *{"killer" if mur else "thief"}?*'))
        else:
            beats.append(dict(id=p+'r', scene='line', c=c, show=3, rule=True, ml=f'ഒരാൾ മാത്രമേ കള്ളം പറയുന്നുള്ളൂ. {who} ആരാണ്?',
                              en=f'Only *ONE* is *lying.* Who is the *{"killer" if mur else "thief"}?*'))
        beats.append(dict(id=p+'p', scene='pause', c=c, ml='ഇവിടെ നിർത്തി ആലോചിക്കൂ!', en='*Pause* and think!', post=5.0))
        for j, s in enumerate(c['sus']):
            n = sum(c['tv'][s[0]]); ok = n == c['n_true']
            ml = f'{s[1]} ആണ് {who} എങ്കിൽ, {CNT[n]}. ' + ('ഇത് ശരിയാണ്!' if ok else 'അത് പറ്റില്ല.')
            en = f'If *{s[0]}* did it: *{n}* true. ' + ('*It fits!*' if ok else 'Not possible.')
            beats.append(dict(id=p+f'x{j}', scene='test', c=c, row=j, ml=ml, en=en))
        a = c['ans']; anm = {q[0]: q[1] for q in c['sus']}
        if c['n_true'] == 1:
            key = [n for n in names if c['tv'][a][names.index(n)]][0]; why_ml = f'{anm[key]} മാത്രമാണ് സത്യം പറഞ്ഞത്.'; why_en = f'Only *{key}* told the truth.'
        else:
            key = [n for n in names if not c['tv'][a][names.index(n)]][0]; why_ml = f'{anm[key]} മാത്രമാണ് കള്ളം പറഞ്ഞത്.'; why_en = f'Only *{key}* lied.'
        c['why_en'] = why_en.replace('*', '')
        beats.append(dict(id=p+'z', scene='reveal', c=c, ml=f'അപ്പോൾ {who} {anm[a]}! {why_ml} ശരിയായെങ്കിൽ ഒരു പോയിന്റ് എടുക്കൂ!',
                          en=f'The {"killer" if mur else "thief"} is *{a.upper()}!* {why_en} Got it? Take *1 point!*', post=0.6))
    beats.append(dict(id='e1', scene='end', ml=f'നിങ്ങൾക്ക് എത്ര കിട്ടി? നിങ്ങളുടെ സ്കോർ കമന്റ് ചെയ്യൂ! ദിവസവും പുതിയ രഹസ്യങ്ങൾക്കായി സബ്സ്ക്രൈബ് ചെയ്യൂ!',
                      en=f'How many did you get? *Comment* your score and *Subscribe* for new mysteries!', post=2.5))
    return beats

# ---------------- drawing
def stage(ctx, t, police=True, cone=None):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#1b2033')); g.add_color_stop_rgba(1, *hexc('#0c0e18'))
    ctx.set_source(g); ctx.paint()
    if police:
        for (cx, cy, col, ph) in ((180, 330, '#ff2d55', 0), (1740, 330, '#2d6bff', math.pi)):
            a = 0.30 + 0.18*math.sin(t*5 + ph)
            rg = cairo.RadialGradient(cx, cy, 10, cx, cy, 560); rg.add_color_stop_rgba(0, *hexc(col, a)); rg.add_color_stop_rgba(1, *hexc(col, 0))
            ctx.set_source(rg); ctx.paint()
    ctx.rectangle(0, FL-30, W, H); ctx.set_source_rgba(*hexc('#3a2a1e')); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.35); ctx.set_line_width(3)
    for k in range(1, 4): ctx.move_to(0, FL-30+k*45); ctx.line_to(W, FL-30+k*45); ctx.stroke()
    for k in range(18):
        x = (k*211) % W; row = k % 3; ctx.move_to(x, FL-30+row*45); ctx.line_to(x, FL+15+row*45); ctx.stroke()
    if cone:
        for x in cone: spot(ctx, x, 260, top=250, a=0.13)

def cnum(ctx, c):
    rrect(ctx, 24, 1000, 230, 60, 14); ctx.set_source_rgba(*hexc('#e8283c')); ctx.fill()
    text(ctx, f'CASE {c["i"]+1}/{c["N"]}', 139, 1043, 32, '#ffffff')

def three(ctx, t, c, s=0.5, show=0, talk=-1, t0=0, t1=0, dim=False, bub=True):
    for j, (x, q) in enumerate(zip(XS, c['sus'])):
        tk = clamp(abs(math.sin(t*13))*0.9) if (j == talk and t0+0.2 < t < t1-0.1) else 0
        suspect(ctx, x, FL+10, s, q[4], t, pose='point' if j == talk else 'down', talk=tk, cap=q[5],
                stache=q[0] not in FEM, mood='angry' if j == talk else 'sus')
        namebox(ctx, x, FL+60, f'{q[0].upper()} · {q[2].upper()}', 26)
        if bub and j < show:
            pp = prog(t, t0+0.3, 0.3) if j == show-1 and talk == j else 1
            bubble(ctx, x, FL - 470*s - 80, c['st'][j][2], col='#e8283c' if c['sus'][j][6][0] == 'did' else '#1a1a1a', size=34, p=pp)
    if dim: ctx.set_source_rgba(0, 0, 0, 0.55); ctx.paint()

FEM = {'Reena', 'Priya', 'Ammini', 'Sajitha', 'Sheela', 'Leela', 'Lakshmi'}

def place(ctx, t, c):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#0a0f24')); g.add_color_stop_rgba(1, *hexc('#1b2550')); ctx.set_source(g); ctx.paint()
    rnd = random.Random(c['i'])
    for k in range(120):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 600); ctx.set_source_rgba(1, 1, 1, 0.4+0.4*math.sin(t*3+k)); ctx.arc(x, y, rnd.uniform(1.5, 3), 0, 2*math.pi); ctx.fill()
    ctx.set_source_rgba(1, 0.97, 0.85, 0.95); ctx.arc(1620, 260, 70, 0, 2*math.pi); ctx.fill()
    ctx.set_source_rgba(*hexc('#0a0f24')); ctx.arc(1590, 245, 62, 0, 2*math.pi); ctx.fill()
    bg = c['bg']; a = 0.75 + 0.25*math.sin(t*6)
    if bg in ('hills', 'harbour'):
        for k, (y0, col) in enumerate(((620, '#0f2a24'), (720, '#143a30'))):
            ctx.move_to(0, y0)
            for xx in range(0, W+80, 80): ctx.line_to(xx, y0 + 50*math.sin(xx/300 + k*2))
            ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    if bg == 'harbour':
        ctx.rectangle(0, 760, W, H); ctx.set_source_rgba(*hexc('#0d1838')); ctx.fill()
        for k in range(16):
            ctx.set_source_rgba(0.6, 0.7, 1, 0.18); ctx.rectangle((k*157 + t*30) % W, 790 + (k % 6)*45, 160, 4); ctx.fill()
    # building with one red window (the scene)
    bx, by = 960, 800
    roof = {'temple': '#7a2e22', 'wedding': '#b03a6a', 'toddy': '#5a3a22', 'school': '#a04000', 'bus': None}.get(bg, '#3a3f55')
    if bg == 'bus':
        rrect(ctx, bx-420, by-260, 840, 240, 30); fill_stroke(ctx, '#c0392b', 6)
        ctx.rectangle(bx-420, by-110, 840, 26); ctx.set_source_rgba(*hexc('#f1c40f')); ctx.fill()
        for k in range(6):
            rrect(ctx, bx-380+k*130, by-230, 100, 90, 10); ctx.set_source_rgba(*(hexc('#ff2a2a', a) if k == 3 else hexc('#ffb84a'))); ctx.fill()
        for wx in (-260, 260): ctx.arc(bx+wx, by-20, 50, 0, 2*math.pi); fill_stroke(ctx, '#222222', 6)
        text(ctx, 'KSRTC', bx, by-40, 40, '#ffffff'); rx = bx+70
    else:
        ctx.rectangle(bx-380, by-300, 760, 300); fill_stroke(ctx, '#2a2f45' if roof == '#3a3f55' else '#e8dcc0', 6)
        ctx.move_to(bx-440, by-300); ctx.line_to(bx, by-440); ctx.line_to(bx+440, by-300); ctx.close_path(); fill_stroke(ctx, roof, 6)
        for r in range(2):
            for k in range(5):
                red = (r == 0 and k == 3)
                rrect(ctx, bx-330+k*140, by-270+r*130, 90, 90, 8); ctx.set_source_rgba(*(hexc('#ff2a2a', a) if red else hexc('#ffb84a', 0.9))); ctx.fill()
        rx = bx-330+3*140+45
    rg = cairo.RadialGradient(rx, by-220, 10, rx, by-220, 360); rg.add_color_stop_rgba(0, 1, 0.1, 0.1, 0.4*a); rg.add_color_stop_rgba(1, 1, 0, 0, 0)
    ctx.set_source(rg); ctx.paint()
    ctx.rectangle(0, by, W, H); ctx.set_source_rgba(*hexc('#0b0d16', 0.9)); ctx.fill()
    tape(ctx, 930, -0.03, t)
    pill(ctx, 960, 1010, 520, 80, '#e8283c' if c['kind'] == 'murder' else '#2d6bff', c['place'].upper(), size=40)

def clock(ctx, t, t0):
    left = 5 - (t - t0); n = max(1, math.ceil(left)) if left > 0 else 0
    cx, cy, r = 960, 590, 160
    ctx.arc(cx, cy, r+16, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#141826')); ctx.fill()
    ctx.set_line_width(22); ctx.set_source_rgba(1, 1, 1, 0.15); ctx.arc(cx, cy, r, 0, 2*math.pi); ctx.stroke()
    f = clamp(left/5); ctx.set_source_rgba(*hexc('#ffd23f')); ctx.arc(cx, cy, r, -math.pi/2, -math.pi/2 + 2*math.pi*f); ctx.stroke()
    if t < t0: n = 5
    sc = 1 + 0.15*(1 - ((t - t0) % 1)) if t >= t0 else 1
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc); text(ctx, str(n) if n else '!', 0, 60, 170, '#ffffff'); ctx.restore()

def test(ctx, t, c, row, t0):
    stage(ctx, t, police=False)
    ctx.set_source_rgba(0, 0, 0, 0.45); ctx.paint()
    cnum(ctx, c)
    cols = (870, 1150, 1430)
    for j, q in enumerate(c['sus']):
        text(ctx, q[0].upper(), cols[j], 260, 30, '#ffd23f')
        text(ctx, c['st'][j][1], cols[j], 300, 24, '#ffffff')
    text(ctx, 'TRUE', 1690, 280, 30, '#9aa3bd')
    for i, q in enumerate(c['sus']):
        if i > row: break
        y = 360 + i*165; p = back(prog(t, t0, 0.3)) if i == row else 1
        n = sum(c['tv'][q[0]]); ok = n == c['n_true']
        rrect(ctx, 120, y, 1680, 140, 18); ctx.set_source_rgba(*hexc('#17331f' if ok else '#1d2236')); ctx.fill_preserve()
        ctx.set_source_rgba(*hexc('#2fbf4f' if ok else '#ffffff', 0.9 if ok else 0.15)); ctx.set_line_width(4); ctx.stroke()
        suspect(ctx, 200, y+130, 0.24, q[4], t, cap=q[5], stache=q[0] not in FEM, badge=False)
        text(ctx, f'IF {q[0].upper()} DID IT', 260, y+84, 34, '#ffffff', align='l')
        for j in range(3):
            pj = prog(t, t0 + 0.4 + j*0.35, 0.25) if i == row else 1
            if pj > 0: mark(ctx, cols[j], y+70, 34, c['tv'][q[0]][j], back(pj))
        pc = prog(t, t0 + 1.5, 0.3) if i == row else 1
        if pc > 0:
            text(ctx, str(n), 1690, y+95, 70, '#2fbf4f' if ok else '#e8283c', alpha=pc)
    need = 'NEED: 1 TRUE' if c['n_true'] == 1 else 'NEED: 2 TRUE (1 LIE)'
    pill(ctx, 960, 900, 560, 70, '#ffd23f', need, tcol='#141414', size=34)

def draw_factory(tl, clist, N):
    def draw(ctx, t):
        cur = None
        for b in tl.beats:
            if t >= b['t0'] - 0.12: cur = b
        b = cur or tl.beats[0]; sc = b['scene']; t0, t1 = b['t0'], b['t1']; c = b.get('c')
        z = 1.0 + 0.04*(1 - sprog(t, t0-0.12, 0.35)) + 0.015*prog(t, t0, t1-t0+0.5)
        ctx.save(); ctx.translate(W/2, H/2); ctx.scale(z, z); ctx.translate(-W/2, -H/2)
        if sc == 'teaser':
            stage(ctx, t, cone=XS); three(ctx, t, c, 0.66, show=3, t0=-9, t1=-9)
            ctx.set_source_rgba(0, 0, 0, 0.35); ctx.paint()
            ctx.save(); ctx.translate(960, 330); ctx.rotate(-0.04)
            pill(ctx, 0, 0, 900, 140, '#e8283c', f'ONLY 1% GET ALL {N}!', size=66, p=prog(t, tl.beats[0]['t0']+0.5, 0.35)); ctx.restore()
            if b['id'] == 't2': pill(ctx, 960, 470, 520, 90, '#ffd23f', 'SCORE: __/%d' % N, tcol='#141414', size=46, p=prog(t, t0+0.3, 0.3))
        elif sc == 'title': place(ctx, t, c); cnum(ctx, c)
        elif sc == 'line':
            stage(ctx, t, cone=XS); three(ctx, t, c, 0.66, show=b['show'], talk=b.get('talk', -1), t0=t0, t1=t1); cnum(ctx, c)
            if b.get('rule'):
                lab = 'ONLY 1 TELLS THE TRUTH' if c['n_true'] == 1 else 'ONLY 1 IS LYING'
                pill(ctx, 960, 262, 640, 74, '#2fbf4f' if c['n_true'] == 1 else '#e8283c', lab, size=36, p=prog(t, t0+0.3, 0.3))
        elif sc == 'pause':
            stage(ctx, t, cone=XS); three(ctx, t, c, 0.66, show=3, t0=-9, t1=-9, dim=True); cnum(ctx, c)
            clock(ctx, t, t1 + 0.1)
            pill(ctx, 960, 270, 560, 84, '#ffd23f', 'PAUSE AND THINK!', tcol='#141414', size=42)
        elif sc == 'test': test(ctx, t, c, b['row'], t0)
        elif sc == 'reveal':
            stage(ctx, t, cone=(960,))
            a = c['ans']; q = [s for s in c['sus'] if s[0] == a][0]
            suspect(ctx, 960, FL+10, 0.8, q[4], t, pose='chest', cap=q[5], stache=a not in FEM, mood='scared')
            namebox(ctx, 960, FL+60, a.upper(), 34)
            ctx.save(); ctx.translate(960, 330); ctx.rotate(-0.05)
            pill(ctx, 0, 0, 640, 110, '#e8283c', ('KILLER: ' if c['kind'] == 'murder' else 'THIEF: ') + a.upper(), size=56, p=prog(t, t0+0.4, 0.3)); ctx.restore()
            pp = prog(t, t1 - 1.0, 0.3)
            if pp > 0:
                ctx.save(); ctx.translate(1600, 640); s_ = back(pp); ctx.scale(s_, s_)
                rrect(ctx, -170, -70, 340, 140, 20); ctx.set_source_rgba(*hexc('#2fbf4f')); ctx.fill()
                text(ctx, '+1 POINT', 0, 18, 50, '#ffffff'); ctx.restore()
            cnum(ctx, c)
        elif sc == 'end':
            stage(ctx, t, police=True)
            ctx.set_source_rgba(0, 0, 0, 0.4); ctx.paint()
            text(ctx, 'YOUR SCORE', 960, 400, 70, '#ffffff')
            rrect(ctx, 660, 450, 600, 170, 30); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
            text(ctx, f'__ / {N}', 960, 575, 110, '#141414')
            pill(ctx, 960, 720, 640, 84, '#ffd23f', 'COMMENT YOUR SCORE!', tcol='#141414', size=42)
            p = 1 + 0.06*math.sin(t*8)
            ctx.save(); ctx.translate(960, 870); ctx.scale(p, p); rrect(ctx, -230, -55, 460, 110, 55); ctx.set_source_rgba(*hexc('#e8283c')); ctx.fill()
            text(ctx, 'SUBSCRIBE', 0, 18, 52, '#ffffff'); ctx.restore()
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and b is not tl.beats[0]: ctx.set_source_rgba(1, 1, 1, 0.22*fl); ctx.paint()
        caption(ctx, b.get('en'), t, t0, t1, y=110, size=54, maxw=1600)
    return draw

def sfx_list(tl):
    sfx = []
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0']-0.12, 'whoosh', 0.5))
        sc = b['scene']
        if sc == 'line' and b.get('talk', -1) >= 0: sfx.append((b['t0']+0.3, 'pop', 0.6))
        if sc == 'line' and b.get('rule'): sfx.append((b['t0']+0.3, 'thud', 0.6))
        if sc == 'pause':
            for k in range(5): sfx.append((b['t1']+0.1+k, 'tick', 0.6))
        if sc == 'test':
            c = b['c']; q = c['sus'][b['row']]; ok = sum(c['tv'][q[0]]) == c['n_true']
            sfx.append((b['t0']+1.5, 'right' if ok else 'wrong', 0.55))
        if sc == 'reveal': sfx.append((b['t0']+0.4, 'thud', 0.7)); sfx.append((b['t1']-1.0, 'right', 0.5))
    return sfx
