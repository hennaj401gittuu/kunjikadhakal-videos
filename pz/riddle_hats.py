"""Logic-riddle Short: 3 prisoners, 5 hats (3 white, 2 black), line facing a wall.
Ravi (back) 'don't know', Sunil 'don't know', Kunjan (front, sees only the wall) 'I know' -> WHITE.
Checked by brute force in check/hats_verify.py (exactly one answer). Answer never shown."""
import sys, math, os, cairo
sys.path.insert(0, '/home/claude/pz')
from wd import (W, H, NARR, text, text_w, caption, pill, namebox, bubble, suspect, spot, build_mix, render_raw)
from pz import Timeline, clamp, prog, sprog, back, hexc, rrect, fill_stroke, OUT
from riddle_bridge import sky, wall, ground, led, clock_pole, prisoner, paper, dashed_arrow, thought, GROUND

NAMES = ('KUNJAN', 'SUNIL', 'RAVI')       # front (next to the wall) -> back
XS = (320, 590, 860); FEET = 1560; SC = 0.88
HAIR = ('#1b1410', '#1b1410', '#5a5a5a')
CLOCK0 = 600

def bob(x, t): return 3*math.sin(t*2.2 + x*0.01)

def hat(ctx, x, y, s, t, col='hidden', p=1.0, lift=0.0):
    """top hat sitting on a suspect() head (feet at x,y, scale s)."""
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.translate(0, bob(x, t) - 400 - 52 - lift)
    sc = back(p); ctx.scale(sc, sc)
    fills = {'hidden': '#6f5a9a', 'W': '#f6f3ea', 'B': '#1c1c22'}
    f = fills[col]
    ctx.save(); ctx.scale(1, 0.32); ctx.arc(0, 0, 92, 0, 2*math.pi); ctx.restore(); fill_stroke(ctx, f, 5)
    rrect(ctx, -56, -118, 112, 120, 10); fill_stroke(ctx, f, 5)
    ctx.rectangle(-56, -30, 112, 20); ctx.set_source_rgba(*hexc('#c0392b' if col != 'hidden' else '#ffd23f')); ctx.fill()
    if col == 'hidden': text(ctx, '?', 0, -38, 86, '#ffffff')
    ctx.restore()

def wall_slab(ctx, t):
    ctx.rectangle(0, 700, 150, GROUND-700+60); fill_stroke(ctx, '#7a3e30', 6)
    ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(3)
    for r in range(22):
        yy = 700 + r*40; ctx.move_to(0, yy); ctx.line_to(150, yy); ctx.stroke()
        xx = 75 if r % 2 else 40; ctx.move_to(xx, yy); ctx.line_to(xx, yy+40); ctx.stroke()
    ctx.save(); ctx.translate(75, 1060); ctx.rotate(-math.pi/2); text(ctx, 'WALL', 0, 18, 54, '#ffd23f'); ctx.restore()

def yard_bg(ctx, t, dark=0.0):
    sky(ctx, t); wall(ctx, t); ground(ctx)
    if dark: ctx.set_source_rgba(0.03, 0.02, 0.1, dark); ctx.paint()

def clock(ctx, t, T, x=900, y=600, s=0.8):
    led(ctx, x, y, s, CLOCK0 - max(0, t - T['h1']['t0']))

def row(ctx, t, moods=('sus', 'sus', 'sus'), talk=(0, 0, 0), hl=None, hats=True, look=-0.8):
    for i, x in enumerate(XS):
        s = SC*(1.08 if hl == i else 1.0)
        prisoner(ctx, x, FEET, s, t, mood=moods[i], stache=(i != 0), hair=HAIR[i], talk=talk[i], look=look)
        if hats: hat(ctx, x, FEET, s, t)
        namebox(ctx, x, FEET+70, NAMES[i], 28)

def talkv(t, b, on): return abs(math.sin(t*14))*0.7 if on and b['t0'] < t < b['t1'] else 0

# ------------------------------------------------------------------ scenes
def sc_hook(ctx, t, b, T):
    yard_bg(ctx, t); clock_pole(ctx, 950, CLOCK0 - max(0, t - T['h1']['t0']), top=760)
    for i, x in enumerate((180, 430, 680)):
        p = back(prog(t, b['t0'] + i*0.1, 0.3)); ctx.save(); ctx.translate(x, GROUND); ctx.scale(1, max(0.01, p)); ctx.translate(-x, -GROUND)
        prisoner(ctx, x, GROUND+60, 0.72, t, mood='sus', stache=(i != 0), hair=HAIR[i], look=math.sin(t*2+i))
        hat(ctx, x, GROUND+60, 0.72, t, p=prog(t, b['t0']+0.35+i*0.12, 0.3)); ctx.restore()
    ctx.save(); ctx.translate(W/2, 1720); ctx.rotate(-0.05); pill(ctx, 0, 0, 560, 120, '#e8283c', 'ONLY 1% SOLVE', size=58, p=prog(t, b['t0']+0.6, 0.3)); ctx.restore()

def sc_jailer(ctx, t, b, T):
    yard_bg(ctx, t); clock(ctx, t, T)
    suspect(ctx, 270, FEET+40, 0.8, '#c8b07a', t, cap='police', mood='angry', pose='point', talk=talkv(t, b, True))
    namebox(ctx, 270, FEET+100, 'JAILER', 30)
    for i, x in enumerate((640, 800, 960)):
        prisoner(ctx, x, FEET+40, 0.5, t, mood='scared', stache=(i != 0), hair=HAIR[i], look=-1)
    pill(ctx, 760, 1010, 420, 100, '#2ecc71', 'WIN = FREE', size=52, p=prog(t, b['t0']+0.6, 0.3))

def table(ctx):
    rrect(ctx, 120, 1270, 840, 60, 10); fill_stroke(ctx, '#8a5a32', 6)
    for lx in (180, 880): ctx.rectangle(lx, 1330, 30, 260); fill_stroke(ctx, '#6a4426', 5)

def sc_hats(ctx, t, b, T, hide=False):
    yard_bg(ctx, t); clock(ctx, t, T, x=W/2, y=560, s=0.7)
    table(ctx)
    cols = ('W', 'W', 'W', 'B', 'B'); xs = (230, 380, 530, 720, 870)
    for i, (c, x) in enumerate(zip(cols, xs)):
        p = 1 if hide else prog(t, b['t0'] + 0.2 + i*0.18, 0.3)
        lift = 0
        if hide: continue
        ctx.save(); ctx.translate(x, 1270); sc = back(p) if p > 0 else 0; ctx.scale(max(sc, 0.001), max(sc, 0.001))
        ctx.translate(-x, -1270); hat(ctx, x, 1270 + 452*0.9, 0.9, 0, col=c); ctx.restore()
    if not hide:
        pill(ctx, 380, 1450, 330, 90, '#f6f3ea', '3 WHITE', tcol='#141414', size=48, p=prog(t, b['t0']+1.0, 0.3))
        pill(ctx, 795, 1450, 330, 90, '#1c1c22', '2 BLACK', size=48, p=prog(t, b['t0']+1.6, 0.3))
    else:
        # all hats under a cloth, two pulled into a sealed box
        rrect(ctx, 150, 1050, 780, 225, 30); fill_stroke(ctx, '#6f5a9a', 6)
        text(ctx, '?  ?  ?', 540, 1195, 110, '#ffffff')
        p = prog(t, b['t0']+0.3, 0.4)
        ctx.save(); ctx.translate(820, 1650); ctx.scale(back(p) if p > 0 else 0.001, back(p) if p > 0 else 0.001)
        rrect(ctx, -170, -110, 340, 200, 16); fill_stroke(ctx, '#3a2a1e', 6)
        text(ctx, '2 HATS', 0, -10, 48, '#ffd23f'); text(ctx, 'HIDDEN', 0, 55, 48, '#ffffff'); ctx.restore()
        prisoner(ctx, 250, 1800, 0.45, t, mood='scared', look=1)
        thought(ctx, 300, 1450, 'MY HAT?', prog(t, b['t0']+0.8, 0.3), 50)

def sc_line(ctx, t, b, T, step):
    yard_bg(ctx, t); wall_slab(ctx, t); clock(ctx, t, T)
    row(ctx, t, look=-1)
    if step == 0:
        for i, x in enumerate(XS):
            hat(ctx, x, FEET, SC, t, p=1)
        dashed_arrow(ctx, 940, 760, 200, 760, prog(t, b['t0']+0.4, 0.6), col='#ffd23f')
        pill(ctx, 560, 700, 420, 84, '#141826', 'ALL FACE THE WALL', size=38, p=prog(t, b['t0']+0.4, 0.3))
    if step >= 1:   # Ravi sees two hats
        hy = FEET - 470*SC
        p = prog(t, b['t0']+0.3, 0.5)
        dashed_arrow(ctx, XS[2]-40, hy+30, XS[1]+40, hy-10, p)
        dashed_arrow(ctx, XS[2]-40, hy+10, XS[0]+50, hy-40, prog(t, b['t0']+0.7, 0.6))
        pill(ctx, XS[2], 840, 300, 80, '#ff9a1e', 'SEES 2', size=44, p=prog(t, b['t0']+0.9, 0.3))
    if step >= 2:
        hy = FEET - 470*SC
        dashed_arrow(ctx, XS[1]-40, hy+40, XS[0]+50, hy+10, prog(t, b['t0']+0.2, 0.5))
        pill(ctx, XS[1], 940, 300, 80, '#ff9a1e', 'SEES 1', size=44, p=prog(t, b['t0']+0.5, 0.3))
        dashed_arrow(ctx, XS[0]-60, hy+60, 170, hy+60, prog(t, b['t0']+1.4, 0.4))
        pill(ctx, XS[0], 840, 330, 80, '#e8283c', 'SEES 0', size=44, p=prog(t, b['t0']+1.6, 0.3))

def sc_ask(ctx, t, b, T):
    yard_bg(ctx, t, 0.15); wall_slab(ctx, t); clock(ctx, t, T)
    row(ctx, t, moods=('scared', 'scared', 'scared'))
    bubble(ctx, 540, 860, 'WHAT COLOUR IS YOUR HAT?', size=46, p=prog(t, b['t0']+0.2, 0.3), tail=0)

def sc_say(ctx, t, b, T, who):
    yard_bg(ctx, t, 0.3); wall_slab(ctx, t); clock(ctx, t, T)
    spot(ctx, XS[who], 360, top=520, a=0.2)
    moods = ['sus', 'sus', 'sus']; moods[who] = 'happy' if who == 0 else 'scared'
    tk = [0, 0, 0]; tk[who] = talkv(t, b, True)
    row(ctx, t, moods=tuple(moods), talk=tuple(tk), hl=who)
    lines = {2: "I DON'T KNOW!", 1: "I DON'T KNOW!", 0: 'I KNOW!'}
    bx = clamp(XS[who], 250, 830)
    bubble(ctx, bx, 900, lines[who], col='#e8283c' if who else '#1e8e3e', size=56, p=prog(t, b['t0']+0.3, 0.3), tail=0)
    # earlier answers stay as small tags
    for k in (2, 1):
        if k > who: pill(ctx, XS[k], 990, 230, 64, '#2a2f45', "DON'T KNOW", size=30, p=1)

def sc_question(ctx, t, b, T):
    yard_bg(ctx, t, 0.35); wall_slab(ctx, t); clock(ctx, t, T, x=850, y=560, s=0.7)
    spot(ctx, 470, 460, top=520, a=0.22)
    prisoner(ctx, 470, 1560, 1.0, t, mood='happy', stache=False, look=-0.6)
    hat(ctx, 470, 1560, 1.0, t)
    namebox(ctx, 470, 1630, 'KUNJAN', 34)
    pill(ctx, 860, 1050, 260, 90, '#f6f3ea', 'WHITE?', tcol='#141414', size=46, p=prog(t, b['t0']+0.4, 0.3))
    pill(ctx, 860, 1170, 260, 90, '#1c1c22', 'BLACK?', size=46, p=prog(t, b['t0']+0.7, 0.3))

def sc_think(ctx, t, b, T):
    yard_bg(ctx, t, 0.4); wall_slab(ctx, t)
    left = 5 - (t - b['t1'])
    led(ctx, W/2, 620, 1.8, clamp(left, 0, 5) if t > b['t1'] else 5)
    row(ctx, t)
    for i, x in enumerate(XS):
        thought(ctx, x+40, 900, '?', prog(t, b['t0']+0.2+i*0.1, 0.3), 70)

def sc_end(ctx, t, b, T):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#2a1546')); g.add_color_stop_rgba(1, *hexc('#0c0e18')); ctx.set_source(g); ctx.paint()
    paper(ctx, W/2, 720, 840, 300, [("KUNJAN'S HAT", '#1a1a1a'), ('WHITE OR BLACK?', '#c0392b')], p=1, size=64)
    rrect(ctx, 250, 1000, 580, 110, 55); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    word = 'ANSWER'; ty = b['t0'] + 0.3; n = int(clamp((t - ty)/1.0)*len(word)) if t >= ty else 0
    full = text_w(ctx, word, 56)
    if n: text(ctx, word[:n], W/2 - full/2, 1076, 56, '#141414', align='l')
    cx = W/2 - full/2 + (text_w(ctx, word[:n], 56) + 6 if n else 0)
    if (t*2) % 1 < 0.6: ctx.rectangle(cx, 1020, 8, 70); ctx.set_source_rgba(*hexc('#e8283c')); ctx.fill()
    text(ctx, 'Type ANSWER in the comments!', W/2, 1200, 46, '#ffd23f')
    p = 1 + 0.06*math.sin(t*8)
    ctx.save(); ctx.translate(W/2, 1340); ctx.scale(p, p); rrect(ctx, -170, -50, 340, 100, 50); ctx.set_source_rgba(*hexc('#2d6bff')); ctx.fill()
    text(ctx, '+ Follow', 0, 16, 46, '#ffffff'); ctx.restore()
    text(ctx, 'Follow for more mysteries!', W/2, 1450, 38, '#ffffff')

BEATS = [
    dict(id='h1', sc='hook', ml='ഒരു ശതമാനം പേർക്ക് മാത്രമേ ഇതിന് ഉത്തരം കിട്ടൂ!', en='Only *1%* can solve this!'),
    dict(id='h2', sc='jailer', ml='ജയിലർ മൂന്നു തടവുകാരോട് പറഞ്ഞു, ഈ കളി ജയിച്ചാൽ നിങ്ങൾ സ്വതന്ത്രർ!', en='The jailer: win this game and you go *FREE!*'),
    dict(id='h3', sc='hats', ml='അയാളുടെ കയ്യിൽ അഞ്ചു തൊപ്പികൾ. മൂന്നു വെള്ള, രണ്ടു കറുപ്പ്.', en='He has *5 hats:* *3 WHITE* and *2 BLACK.*'),
    dict(id='h4', sc='line0', ml='മൂന്നുപേരെയും ഒരു വരിയിൽ, മതിലിനു നേരെ നിർത്തി, ഓരോ തലയിലും ഒരു തൊപ്പി വെച്ചു.', en='All 3 stand in a *line* facing the *wall.* One hat on each head.'),
    dict(id='h5', sc='hide', ml='ബാക്കി രണ്ടു തൊപ്പികൾ ഒളിപ്പിച്ചു. ആർക്കും സ്വന്തം തൊപ്പി കാണാൻ പറ്റില്ല.', en='The other 2 hats are *hidden.* Nobody can see *his own* hat.'),
    dict(id='h6', sc='line1', ml='ഏറ്റവും പിന്നിലുള്ള രവി, മുന്നിലെ രണ്ടു തൊപ്പികളും കാണും.', en='*Ravi* at the back sees *BOTH* hats in front.'),
    dict(id='h7', sc='line2', ml='നടുവിലെ സുനിൽ കുഞ്ഞന്റെ തൊപ്പി മാത്രം. മുന്നിലെ കുഞ്ഞൻ മതിൽ മാത്രം കാണും.', en='*Sunil* sees only Kunjan\'s hat. *Kunjan* sees just the *wall.*'),
    dict(id='h8', sc='ask', ml='ജയിലർ ചോദിച്ചു, നിന്റെ തൊപ്പിയുടെ നിറം എന്ത്?', en='The jailer asks: *what colour* is YOUR hat?'),
    dict(id='h9', sc='say2', ml='രവി പറഞ്ഞു, എനിക്കറിയില്ല!', en='Ravi: *"I don\'t know!"*'),
    dict(id='h10', sc='say1', ml='സുനിൽ പറഞ്ഞു, എനിക്കും അറിയില്ല!', en='Sunil: *"I don\'t know either!"*'),
    dict(id='h11', sc='say0', ml='അപ്പോൾ, മതിൽ മാത്രം കാണുന്ന കുഞ്ഞൻ ചിരിച്ചു, എനിക്കറിയാം!', en='Then Kunjan, who sees only the *wall*, smiles: *"I KNOW!"*'),
    dict(id='h12', sc='question', ml='കുഞ്ഞന്റെ തൊപ്പിയുടെ നിറം എന്താണ്? അവൻ അത് എങ്ങനെ അറിഞ്ഞു?', en='What colour is *KUNJAN\'S* hat? And *HOW* did he know?'),
    dict(id='h13', sc='think', ml='അഞ്ചു സെക്കൻഡ് ആലോചിക്കൂ!', en='Think for *5 seconds!*', post=4.6),
    dict(id='h14', sc='end', ml='ഉത്തരം കമന്റ് ചെയ്യൂ! കൂടുതൽ മിസ്റ്ററികൾക്ക് ഫോളോ ചെയ്യൂ!', en='Type *ANSWER* in the comments! *Follow* for more!', post=1.8),
]

def main():
    stills = 'stills' in sys.argv
    tl = Timeline(BEATS, lead=0.15, gap=0.1, think=0, spk=NARR); T = tl.by; total = tl.end + 0.3
    def draw(ctx, t):
        cur = tl.beats[0]
        for b in tl.beats:
            if t >= b['t0'] - 0.12: cur = b
        b = cur; t0, t1 = b['t0'], b['t1']
        z = 1.0 + 0.06*(1 - sprog(t, t0-0.12, 0.3)) + 0.025*prog(t, t0, t1-t0+0.5)
        ctx.save(); ctx.translate(W/2, H/2); ctx.scale(z, z); ctx.translate(-W/2, -H/2)
        sc = b['sc']
        if sc == 'hook': sc_hook(ctx, t, b, T)
        elif sc == 'jailer': sc_jailer(ctx, t, b, T)
        elif sc == 'hats': sc_hats(ctx, t, b, T)
        elif sc == 'hide': sc_hats(ctx, t, b, T, hide=True)
        elif sc.startswith('line'): sc_line(ctx, t, b, T, int(sc[-1]))
        elif sc == 'ask': sc_ask(ctx, t, b, T)
        elif sc.startswith('say'): sc_say(ctx, t, b, T, int(sc[-1]))
        elif sc == 'question': sc_question(ctx, t, b, T)
        elif sc == 'think': sc_think(ctx, t, b, T)
        elif sc == 'end': sc_end(ctx, t, b, T)
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and b is not tl.beats[0]: ctx.set_source_rgba(1, 1, 1, 0.25*fl); ctx.paint()
        caption(ctx, b.get('en'), t, t0, t1, y=230)
    out = '/home/claude/pz/out'; os.makedirs(out, exist_ok=True)
    name = 'KP_Three_Hats_Riddle_Mini'
    print('TOTAL', round(total, 1))
    if stills:
        for i, b in enumerate(tl.beats):
            for k, f in enumerate((0.35, 0.9)):
                tt = b['t0'] + (b['t1']-b['t0'])*f + (3 if b['sc'] == 'think' and k else 0) + (1.0 if b['sc'] == 'end' and k else 0)
                surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt); surf.write_to_png(f'{out}/h{i:02d}{k}.png')
        return
    sfx = []
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0']-0.12, 'whoosh', 0.55))
        if b['id'] == 'h1': sfx.append((b['t0']+0.6, 'thud', 0.7))
        if b['sc'] in ('hats', 'line1', 'line2', 'hide'): sfx.append((b['t0']+0.3, 'pop', 0.6))
        if b['id'] in ('h9', 'h10'): sfx.append((b['t0']+0.3, 'wrong', 0.45))
        if b['id'] == 'h11': sfx.append((b['t0']+0.3, 'pop', 0.7))
        if b['sc'] == 'think':
            for k in range(5): sfx.append((b['t1']+k, 'tick', 0.5))
        if b['sc'] == 'end':
            for k in range(6): sfx.append((b['t0']+0.3+k*0.17, 'tick', 0.25))
    aud = f'{out}/{name}.wav'; build_mix(aud, tl, sfx, total); render_raw(f'{out}/{name}.mp4', total, draw, aud)

if __name__ == '__main__': main()
