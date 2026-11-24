"""Logic-riddle Short: 4 prisoners, 1 torch, rope bridge (times 1,3,6,8; answer 18 min, checked by BFS)."""
import sys, math, random, itertools, heapq, cairo
sys.path.insert(0, '/home/claude/pz')
from wd import (W, H, NARR, text, text_w, caption, pill, namebox, bubble, suspect, spot, build_mix, render_raw)
from pz import Timeline, clamp, prog, sprog, back, hexc, rrect, fill_stroke, OUT
import os

TIMES = (1, 3, 6, 8)
def fastest(T):
    full = frozenset(range(len(T))); best = {(full, 0): 0}; pq = [(0, 0, full)]
    while pq:
        c, s, L = heapq.heappop(pq)
        if not L: return c
        side = L if s == 0 else full - L
        for k in (1, 2):
            for g in itertools.combinations(side, k):
                nc = c + max(T[i] for i in g); nL = frozenset(L - set(g) if s == 0 else L | set(g)); st = (nL, 1-s)
                if nc < best.get(st, 999): best[st] = nc; heapq.heappush(pq, (nc, 1-s, nL))
ANS = fastest(TIMES); assert ANS == 18, ANS
NAMES = ('SHIVAN', 'BASHEER', 'MATHAI', 'APPU')
GROUND = 1500

# ------------------------------------------------------------------ art
def sky(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, GROUND); g.add_color_stop_rgba(0, *hexc('#3a1d5c')); g.add_color_stop_rgba(0.55, *hexc('#b9466a'))
    g.add_color_stop_rgba(1, *hexc('#ff9a3c')); ctx.set_source(g); ctx.paint()
    rg = cairo.RadialGradient(W*0.7, 1180, 20, W*0.7, 1180, 420); rg.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.8); rg.add_color_stop_rgba(1, 1, 0.6, 0.3, 0)
    ctx.set_source(rg); ctx.paint()
    ctx.arc(W*0.7, 1200, 110, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#ffd27a')); ctx.fill()

def wall(ctx, t, y=1180):
    ctx.rectangle(0, y, W, GROUND-y); ctx.set_source_rgba(*hexc('#5b4a5e')); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.22); ctx.set_line_width(3)
    for r in range(0, int((GROUND-y)/40)+1):
        yy = y + r*40; ctx.move_to(0, yy); ctx.line_to(W, yy); ctx.stroke()
        for k in range(14):
            xx = k*90 + (45 if r % 2 else 0); ctx.move_to(xx, yy); ctx.line_to(xx, yy+40); ctx.stroke()
    # barbed wire
    ctx.set_source_rgba(*hexc('#2a2230')); ctx.set_line_width(4)
    for k in range(0, W, 60):
        ctx.move_to(k, y-30); ctx.line_to(k, y); ctx.stroke()
    for off in (-26, -12):
        ctx.move_to(0, y+off)
        for k in range(0, W+40, 40): ctx.line_to(k, y+off+ (6 if (k//40) % 2 else -6))
        ctx.stroke()
        for k in range(20, W, 40):
            ctx.move_to(k-8, y+off-8); ctx.line_to(k+8, y+off+8); ctx.move_to(k+8, y+off-8); ctx.line_to(k-8, y+off+8); ctx.stroke()
    # brick pillar
    rrect(ctx, 60, y-160, 120, GROUND-y+160, 4); fill_stroke(ctx, '#8a4a3a', 5)
    ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(3)
    for r in range(int((GROUND-y+160)/36)):
        ctx.move_to(60, y-160+r*36); ctx.line_to(180, y-160+r*36); ctx.stroke()

def ground(ctx):
    ctx.rectangle(0, GROUND, W, H-GROUND); ctx.set_source_rgba(*hexc('#6b4a36')); ctx.fill()
    g = cairo.LinearGradient(0, GROUND, 0, H); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    ctx.set_source(g); ctx.rectangle(0, GROUND, W, H); ctx.fill()

def led(ctx, x, y, s, secs, glow=True):
    secs = max(0, int(secs)); lab = f'{secs//60:02d}:{secs%60:02d}'
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -170, -70, 340, 140, 14); fill_stroke(ctx, '#111111', 6)
    if glow:
        rg = cairo.RadialGradient(0, 0, 10, 0, 0, 220); rg.add_color_stop_rgba(0, 1, 0, 0, 0.25); rg.add_color_stop_rgba(1, 1, 0, 0, 0)
        ctx.set_source(rg); ctx.arc(0, 0, 220, 0, 2*math.pi); ctx.fill()
    text(ctx, '88:88', 0, 38, 104, '#3a0808')
    text(ctx, lab, 0, 38, 104, '#ff2a2a')
    ctx.restore()

def clock_pole(ctx, x, secs, top=820):
    ctx.rectangle(x-12, top, 24, GROUND-top); fill_stroke(ctx, '#3a3a44', 4)
    led(ctx, x, top, 0.75, secs)

def prisoner(ctx, x, y, s, t, pose='down', mood='sus', talk=0.0, stache=True, cap=None, hair='#1b1410', look=0.0):
    suspect(ctx, x, y, s, '#f1efe6', t, pose=pose, mood=mood, talk=talk, stache=stache, cap=cap, badge=False, hair=hair, look=look)
    # stripes on the robe
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.translate(0, 3*math.sin(t*2.2 + x*0.01))
    ctx.move_to(-62, -330); ctx.curve_to(-70, -250, -82, -120, -88, 0); ctx.line_to(88, 0); ctx.curve_to(82, -120, 70, -250, 62, -330)
    ctx.curve_to(40, -350, -40, -350, -62, -330); ctx.close_path(); ctx.clip()
    ctx.set_source_rgba(*hexc('#1d1d24'))
    for k in range(9): ctx.rectangle(-100, -300 + k*36, 200, 16); ctx.fill()
    ctx.restore()
    # ball and chain
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgba(*hexc('#555555')); ctx.set_line_width(6); ctx.move_to(40, -6); ctx.curve_to(80, 10, 110, 10, 130, -30); ctx.stroke()
    ctx.arc(150, -34, 34, 0, 2*math.pi); fill_stroke(ctx, '#2b2b30', 5)
    ctx.arc(140, -46, 9, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 0.3); ctx.fill()
    ctx.restore()

def torch(ctx, x, y, s=1.0, t=0.0, on=True):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if on:
        rg = cairo.RadialGradient(0, -60, 5, 0, -60, 150); rg.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.7); rg.add_color_stop_rgba(1, 1, 0.6, 0.2, 0)
        ctx.set_source(rg); ctx.arc(0, -60, 150, 0, 2*math.pi); ctx.fill()
        fl = 1 + 0.12*math.sin(t*17)
        ctx.save(); ctx.translate(0, -50); ctx.scale(fl, 1/fl)
        ctx.move_to(0, -60); ctx.curve_to(30, -20, 26, 10, 0, 14); ctx.curve_to(-26, 10, -30, -20, 0, -60); ctx.set_source_rgba(*hexc('#ff8a1e')); ctx.fill()
        ctx.move_to(0, -30); ctx.curve_to(14, -10, 12, 6, 0, 8); ctx.curve_to(-12, 6, -14, -10, 0, -30); ctx.set_source_rgba(*hexc('#ffe27a')); ctx.fill()
        ctx.restore()
    ctx.move_to(-14, -40); ctx.line_to(14, -40); ctx.line_to(8, 60); ctx.line_to(-8, 60); ctx.close_path(); fill_stroke(ctx, '#7a4a26', 4)
    ctx.restore()

def paper(ctx, x, y, w, h, lines, ang=0.03, p=1.0, size=50):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); sc = back(p); ctx.scale(sc, sc)
    ctx.set_source_rgba(0, 0, 0, 0.35); ctx.rectangle(-w/2+10, -h/2+12, w, h); ctx.fill()
    ctx.rectangle(-w/2, -h/2, w, h); fill_stroke(ctx, '#f4ead2', 4)
    for tx in (-w/2+40, w/2-40):
        ctx.save(); ctx.translate(tx, -h/2); ctx.rotate(-0.4 if tx < 0 else 0.4); ctx.rectangle(-40, -14, 80, 28); ctx.set_source_rgba(1, 1, 0.8, 0.7); ctx.fill(); ctx.restore()
    n = len(lines); y0 = -h/2 + (h - n*size*1.35)/2 + size
    for i, (s, col) in enumerate(lines):
        text(ctx, s, 0, y0 + i*size*1.35, size, col)
    ctx.restore()

def dashed_arrow(ctx, x0, y0, x1, y1, p=1.0, col='#ff9a1e'):
    if p <= 0: return
    x1 = x0 + (x1-x0)*p; y1 = y0 + (y1-y0)*p
    ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(8); ctx.set_dash([22, 14]); ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke(); ctx.set_dash([])
    a = math.atan2(y1-y0, x1-x0)
    ctx.move_to(x1, y1); ctx.line_to(x1 - 34*math.cos(a-0.45), y1 - 34*math.sin(a-0.45)); ctx.line_to(x1 - 34*math.cos(a+0.45), y1 - 34*math.sin(a+0.45)); ctx.close_path(); ctx.fill()

def thought(ctx, x, y, s, p=1.0, size=60):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    for (cx, cy, r) in ((-40, 110, 14), (-20, 70, 22)):
        ctx.arc(cx, cy, r, 0, 2*math.pi); fill_stroke(ctx, '#ffffff', 4)
    w = text_w(ctx, s, size) + 80
    ctx.save(); ctx.scale(1, 0.62); ctx.arc(0, -40, w/2, 0, 2*math.pi); ctx.restore(); fill_stroke(ctx, '#ffffff', 5)
    text(ctx, s, 0, size*0.1, size, '#1a1a1a'); ctx.restore()

def bridge_scene(ctx, t, b, people=True):
    sky(ctx, t)
    # gorge
    ctx.move_to(0, 1000); ctx.line_to(300, 1010); ctx.line_to(330, H); ctx.line_to(0, H); ctx.close_path(); fill_stroke(ctx, '#5a3b2a', 5)
    ctx.move_to(W, 1000); ctx.line_to(W-300, 1010); ctx.line_to(W-330, H); ctx.line_to(W, H); ctx.close_path(); fill_stroke(ctx, '#5a3b2a', 5)
    ctx.rectangle(330, 1650, W-660, 270); ctx.set_source_rgba(*hexc('#2f5a8a')); ctx.fill()
    for k in range(6):
        xx = 340 + ((k*83 + t*60) % (W-700)); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.rectangle(xx, 1700 + k*30, 60, 5); ctx.fill()
    # rope bridge
    sag = 70 + 6*math.sin(t*2)
    def rope_y(x, base): u = (x-300)/(W-600); return base + sag*4*u*(1-u)
    ctx.set_source_rgba(*hexc('#c9a26b')); ctx.set_line_width(7)
    for base in (1000, 900):
        ctx.move_to(300, base)
        for x in range(300, W-299, 20): ctx.line_to(x, rope_y(x, base))
        ctx.stroke()
    for x in range(310, W-300, 34):
        ctx.rectangle(x, rope_y(x, 1000)-6, 26, 16); fill_stroke(ctx, '#8a5a32', 3)
        ctx.move_to(x+13, rope_y(x, 1000)); ctx.line_to(x+13, rope_y(x, 900)); ctx.set_source_rgba(*hexc('#c9a26b')); ctx.set_line_width(3); ctx.stroke()
    for px in (300, W-300):
        ctx.rectangle(px-14, 860, 28, 160); fill_stroke(ctx, '#6a4426', 4)
    if people:
        for i, x in enumerate((70, 160, 250)):
            prisoner(ctx, x, 1010, 0.42, t, mood='scared')
        prisoner(ctx, 120, 1100, 0.42, t, mood='sus')
        torch(ctx, 270, 900, 0.6, t)

# ------------------------------------------------------------------ scenes
def yard(ctx, t, b, T):
    sky(ctx, t); wall(ctx, t); ground(ctx)
    c0 = T['h3']['t0']
    secs = 20*60 - max(0, t - c0)*1.0 if t >= c0 else 20*60
    clock_pole(ctx, 930, secs)
    sc = b['id']
    xs = (190, 420, 650, 860) if sc not in ('h1',) else (170, 400, 630, 840)
    for i, x in enumerate(xs):
        if x > 800 and sc not in ('h1',): x = 840
    if sc == 'h1':
        for i, x in enumerate((150, 380, 610)):
            p = back(prog(t, b['t0'] + i*0.1, 0.3)); ctx.save(); ctx.translate(x, GROUND); ctx.scale(1, p); ctx.translate(-x, -GROUND)
            prisoner(ctx, x, GROUND+40, 0.72, t, mood='sus', stache=(i != 1), look=math.sin(t*2+i)); ctx.restore()
            thought(ctx, x+40, 900, '?', prog(t, b['t0']+0.4+i*0.12, 0.3), 80)
        ctx.save(); ctx.translate(W/2, 1700); ctx.rotate(-0.05); pill(ctx, 0, 0, 520, 120, '#e8283c', 'ONLY 1% SOLVE', size=56, p=prog(t, b['t0']+0.5, 0.3)); ctx.restore()

def scene_clock(ctx, t, b, T):
    sky(ctx, t); wall(ctx, t); ground(ctx)
    secs = 20*60 - max(0, t - T['h3']['t0'])
    led(ctx, W/2, 900, 1.6 + 0.04*math.sin(t*6), secs)
    suspect(ctx, 220, GROUND+60, 0.6, '#2c3e66', t, cap='police', mood='angry')
    namebox(ctx, 220, GROUND+120, 'POLICE', 30)
    dashed_arrow(ctx, 330, 1230, 640, 1080, prog(t, b['t0']+0.4, 0.5))
    pill(ctx, W/2, 1700, 520, 100, '#ffd23f', '20 MINUTES', tcol='#141414', size=54, p=prog(t, b['t0']+0.6, 0.3))

def scene_torch(ctx, t, b, T):
    sky(ctx, t)
    ctx.set_source_rgba(0.05, 0.02, 0.12, 0.55); ctx.paint()
    wall(ctx, t); ground(ctx); ctx.set_source_rgba(0.05, 0.02, 0.12, 0.35); ctx.paint()
    torch(ctx, W/2, 1150, 2.2 + 0.05*math.sin(t*4), t)
    pill(ctx, W/2, 1500, 420, 100, '#ff9a1e', '1 TORCH', size=58, p=prog(t, b['t0']+0.4, 0.3))
    for i, x in enumerate((140, 940)):
        prisoner(ctx, x, 1850, 0.55, t, mood='scared', look=(1 if i == 0 else -1))

def scene_rules(ctx, t, b, T):
    bridge_scene(ctx, t, b, people=False)
    paper(ctx, W/2, 1290, 860, 420, [('MAX 2 ON THE BRIDGE', '#c0392b'), ('NO TORCH = NO CROSSING', '#c0392b'), ('ONLY 1 TORCH', '#1a1a1a')],
          p=prog(t, b['t0']+0.2, 0.35), size=54)

def scene_lineup(ctx, t, b, T, which):
    sky(ctx, t); wall(ctx, t); ground(ctx)
    xs = (160, 400, 640, 880)
    for i, x in enumerate(xs):
        hl = i in which
        prisoner(ctx, x, GROUND+120, 0.62 if hl else 0.55, t, mood='sus' if i < 3 else 'scared', stache=(i != 1), hair='#cfcfcf' if i == 3 else '#1b1410',
                 talk=0.0)
        namebox(ctx, x, GROUND+180, NAMES[i], 28)
        ref = T['h6']['t0'] if i < 2 else T['h7']['t0']
        if i in which or (b['id'] != 'h6' and i < 2) or b['id'] == 'h8':
            dt = (i % 2)*1.2 if i in which else 0
            pill(ctx, x, 1010, 200, 84, '#ffd23f' if i in which else '#2a2f45', f'{TIMES[i]} MIN', tcol='#141414' if i in which else '#ffffff', size=44,
                 p=prog(t, ref + 0.3 + dt, 0.3) if i in which else 1)
            if i in which: dashed_arrow(ctx, x, 1060, x, 1160, prog(t, ref + 0.5 + dt, 0.3))
    if b['id'] == 'h8':
        paper(ctx, W/2, 1820, 900, 150, [('2 TOGETHER = SLOWER SPEED', '#c0392b')], ang=-0.02, p=prog(t, b['t0']+0.3, 0.3), size=50)

def scene_question(ctx, t, b, T):
    bridge_scene(ctx, t, b)
    paper(ctx, W/2, 1330, 820, 300, [('FASTEST TIME', '#1a1a1a'), ('FOR ALL 4 = ?', '#c0392b')], p=prog(t, b['t0']+0.2, 0.35), size=66)
    pill(ctx, W/2, 1560, 760, 76, '#141826', '1 MIN · 3 MIN · 6 MIN · 8 MIN', size=38, p=1)
    if b['id'] == 'h10':
        p = prog(t, b['t0']+0.3, 0.25)
        ctx.save(); ctx.translate(W/2+230, 1180); ctx.rotate(0.15); s = 1 + 1.5*(1-p)
        if p > 0:
            ctx.scale(s, s); rrect(ctx, -160, -70, 320, 140, 14); ctx.set_source_rgba(*hexc('#e8283c', p)); ctx.set_line_width(12); ctx.stroke()
            text(ctx, '19', 0, 30, 96, '#e8283c', alpha=p); ctx.set_line_width(12); ctx.move_to(-110, 40); ctx.line_to(110, -40); ctx.stroke()
        ctx.restore()

def scene_think(ctx, t, b, T):
    sky(ctx, t); wall(ctx, t); ground(ctx)
    ctx.set_source_rgba(0, 0, 0, 0.35); ctx.paint()
    left = 5 - (t - b['t1'])
    led(ctx, W/2, 900, 1.8, clamp(left, 0, 5) if t > b['t1'] else 5)
    for i, x in enumerate((180, 420, 660, 900)):
        prisoner(ctx, x, GROUND+150, 0.5, t, mood='sus', stache=(i != 1), hair='#cfcfcf' if i == 3 else '#1b1410')
        thought(ctx, x+30, 1180, '?', prog(t, b['t0']+0.2+i*0.1, 0.3), 70)

def scene_end(ctx, t, b, T):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#2a1546')); g.add_color_stop_rgba(1, *hexc('#0c0e18')); ctx.set_source(g); ctx.paint()
    paper(ctx, W/2, 760, 820, 300, [('FASTEST TIME', '#1a1a1a'), ('FOR ALL 4 = ?', '#c0392b')], p=1, size=66)
    rrect(ctx, 250, 1060, 580, 110, 55); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    word = 'ANSWER'; ty = b['t0'] + 0.3; n = int(clamp((t - ty)/1.0)*len(word)) if t >= ty else 0
    full = text_w(ctx, word, 56)
    if n: text(ctx, word[:n], W/2 - full/2, 1136, 56, '#141414', align='l')
    cx = W/2 - full/2 + (text_w(ctx, word[:n], 56) + 6 if n else 0)
    if (t*2) % 1 < 0.6: ctx.rectangle(cx, 1080, 8, 70); ctx.set_source_rgba(*hexc('#e8283c')); ctx.fill()
    text(ctx, 'Comment your answer!', W/2, 1260, 44, '#ffd23f')
    p = 1 + 0.06*math.sin(t*8)
    ctx.save(); ctx.translate(W/2, 1400); ctx.scale(p, p); rrect(ctx, -170, -50, 340, 100, 50); ctx.set_source_rgba(*hexc('#2d6bff')); ctx.fill()
    text(ctx, '+ Follow', 0, 16, 46, '#ffffff'); ctx.restore()
    text(ctx, 'for the answer', W/2, 1510, 36, '#ffffff')
    text(ctx, '@kunjikadhakal', W/2, 1600, 30, '#9aa3bd')

BEATS = [
    dict(id='h1', sc='yard', ml='ഒരു ശതമാനം പേർക്ക് മാത്രമേ ഇതിന് ഉത്തരം കിട്ടൂ!', en='Only *1%* can solve this!'),
    dict(id='h2', sc='bridge', ml='നാലു തടവുകാർ ജയിൽ ചാടി. മുന്നിൽ ഒരു പഴയ കയർപാലം.', en='*Four* prisoners escaped. Ahead: an old *rope bridge.*'),
    dict(id='h3', sc='clock', ml='ഇരുപത് മിനിറ്റിനുള്ളിൽ പോലീസ് തിരിച്ചെത്തും!', en='The police return in *20 minutes!*'),
    dict(id='h4', sc='torch', ml='ഇരുട്ടായി. അവരുടെ കയ്യിൽ ഒരു ടോർച്ച് മാത്രം.', en='It\'s getting dark. They have only *ONE* torch.'),
    dict(id='h5', sc='rules', ml='പാലത്തിൽ ഒരേ സമയം രണ്ടു പേർ മാത്രം. ടോർച്ച് ഇല്ലാതെ ആരും കടക്കില്ല.', en='Only *2* on the bridge at a time. No one crosses *without the torch.*'),
    dict(id='h6', sc='lineup', which=(0, 1), ml='ശിവൻ ഒരു മിനിറ്റിൽ കടക്കും. ബഷീർ മൂന്നു മിനിറ്റിൽ.', en='*Shivan* crosses in *1 min.* *Basheer* in *3 min.*'),
    dict(id='h7', sc='lineup', which=(2, 3), ml='മത്തായിക്ക് ആറു മിനിറ്റ്. വയസ്സൻ അപ്പുവിന് എട്ടു മിനിറ്റ്.', en='*Mathai* takes *6 min.* Old *Appu* takes *8 min.*'),
    dict(id='h8', sc='lineup', which=(), ml='രണ്ടുപേർ ഒരുമിച്ചു പോയാൽ, പതുക്കെ നടക്കുന്ന ആളുടെ വേഗത്തിൽ.', en='Two together walk at the *slower* one\'s speed.'),
    dict(id='h9', sc='question', ml='നാലു പേരും കടക്കാൻ ഏറ്റവും കുറഞ്ഞത് എത്ര മിനിറ്റ് വേണം?', en='What is the *FASTEST* time for all *4* to cross?'),
    dict(id='h10', sc='question', ml='മിക്കവരും പത്തൊമ്പത് എന്ന് പറയും. പക്ഷേ അത് തെറ്റാണ്!', en='Most people say *19.* But that\'s *WRONG!*'),
    dict(id='h11', sc='think', ml='അഞ്ചു സെക്കൻഡ് ആലോചിക്കൂ!', en='Think for *5 seconds!*', post=4.6),
    dict(id='h12', sc='end', ml='ഉത്തരം കമന്റ് ചെയ്യൂ! അറിയില്ലെങ്കിൽ ഫോളോ ചെയ്ത് ഉത്തരം കാണൂ!', en='*Comment* your answer! Not sure? *Follow* for the answer!', post=1.6),
]

def main():
    stills = 'stills' in sys.argv
    tl = Timeline(BEATS, lead=0.15, gap=0.12, think=0, spk=NARR); T = tl.by; total = tl.end + 0.3
    def draw(ctx, t):
        cur = tl.beats[0]
        for b in tl.beats:
            if t >= b['t0'] - 0.12: cur = b
        b = cur; t0, t1 = b['t0'], b['t1']
        z = 1.0 + 0.06*(1 - sprog(t, t0-0.12, 0.3)) + 0.025*prog(t, t0, t1-t0+0.5)
        ctx.save(); ctx.translate(W/2, H/2); ctx.scale(z, z); ctx.translate(-W/2, -H/2)
        sc = b['sc']
        if sc == 'yard': yard(ctx, t, b, T)
        elif sc == 'bridge': bridge_scene(ctx, t, b)
        elif sc == 'clock': scene_clock(ctx, t, b, T)
        elif sc == 'torch': scene_torch(ctx, t, b, T)
        elif sc == 'rules': scene_rules(ctx, t, b, T)
        elif sc == 'lineup': scene_lineup(ctx, t, b, T, b['which'])
        elif sc == 'question': scene_question(ctx, t, b, T)
        elif sc == 'think': scene_think(ctx, t, b, T)
        elif sc == 'end': scene_end(ctx, t, b, T)
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and b is not tl.beats[0]: ctx.set_source_rgba(1, 1, 1, 0.25*fl); ctx.paint()
        # caption plate for readability
        ctx.set_source_rgba(0, 0, 0, 0.0)
        caption(ctx, b.get('en'), t, t0, t1, y=230)
    out = '/home/claude/pz/out'; os.makedirs(out, exist_ok=True)
    name = 'ML_Prison_Bridge_Riddle_Mini'
    print('TOTAL', round(total, 1))
    if stills:
        for i, b in enumerate(tl.beats):
            tt = b['t0'] + (b['t1']-b['t0'])*0.85 + (3 if b['sc'] == 'think' else 0)
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt); surf.write_to_png(f'{out}/r{i:02d}.png')
        return
    sfx = []
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0']-0.12, 'whoosh', 0.55))
        if b['id'] == 'h1': sfx.append((b['t0']+0.5, 'thud', 0.7))
        if b['id'] == 'h10': sfx.append((b['t0']+0.3, 'wrong', 0.6))
        if b['sc'] in ('lineup', 'rules'): sfx.append((b['t0']+0.3, 'pop', 0.6))
        if b['sc'] == 'think':
            for k in range(5): sfx.append((b['t1']+k, 'tick', 0.5))
        if b['sc'] == 'end':
            for k in range(6): sfx.append((b['t0']+0.3+k*0.17, 'tick', 0.25))
    aud = f'{out}/{name}.wav'; build_mix(aud, tl, sfx, total); render_raw(f'{out}/{name}.mp4', total, draw, aud)

if __name__ == '__main__': main()
