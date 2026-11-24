"""16:9 'Money Brain Teasers Marathon' (paper-cut Kerala shop street) for Kunjikadhakal.
python3 money.py stills | audio | video PART NPARTS"""
import sys, math, os, random, subprocess, json, cairo
sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/money')
import wd
wd.W, wd.H = 1920, 1080
from wd import text, text_w, caption, pill, build_mix, NARR
from pz import Timeline, clamp, prog, sprog, back, hexc, rrect, fill_stroke, mark
import stories
W, H = 1920, 1080
BAND = 800          # top of the blue caption band
GROUND = 790
NUM = ['ഒന്ന്', 'രണ്ട്', 'മൂന്ന്', 'നാല്', 'അഞ്ച്', 'ആറ്', 'ഏഴ്', 'എട്ട്', 'ഒൻപത്']
OUTL = (0.18, 0.12, 0.10, 1)
SL = stories.S; N = len(SL)

def paper(ctx, col, dx=6, dy=6, lw=0):
    """fill current path with a soft paper drop-shadow"""
    path = ctx.copy_path()
    ctx.save(); ctx.translate(dx, dy); ctx.new_path(); ctx.append_path(path); ctx.set_source_rgba(0.25, 0.12, 0.05, 0.22); ctx.fill(); ctx.restore()
    ctx.new_path(); ctx.append_path(path); ctx.set_source_rgba(*hexc(col)); ctx.fill()

# ------------------------------------------------------------------ background (cached per story)
_bg = {}
def street_bg(shops, seed=0):
    key = (shops, seed)
    if key in _bg: return _bg[key]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    g = cairo.LinearGradient(0, 0, 0, 640); g.add_color_stop_rgba(0, *hexc('#f59a5e')); g.add_color_stop_rgba(1, *hexc('#fcd9a8'))
    ctx.set_source(g); ctx.paint()
    sx, sy = 1560, 230
    ctx.arc(sx, sy, 150, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#fff3d6', 0.55)); ctx.fill()
    ctx.arc(sx, sy, 110, 0, 2*math.pi); paper(ctx, '#fffaf0', 0, 0)
    rnd = random.Random(seed)
    for k, (y0, col) in enumerate(((470, '#5fb3a7'), (520, '#3f978d'), (570, '#2b7a73'))):
        ctx.move_to(0, H)
        ph = rnd.uniform(0, 6)
        for xx in range(0, W+40, 40): ctx.line_to(xx, y0 + 45*math.sin(xx/300 + ph + k))
        ctx.line_to(W, H); ctx.close_path(); paper(ctx, col, 0, -6)
    # coconut palms behind shops
    for px in (90, 1830, 980):
        ctx.set_source_rgba(*hexc('#2a5a3a')); ctx.set_line_width(14)
        ctx.move_to(px, 600); ctx.curve_to(px+10, 500, px+20, 420, px+30, 330); ctx.stroke()
        for kk in range(7):
            a = -math.pi/2 + (kk-3)*0.5
            ctx.move_to(px+30, 330); ctx.curve_to(px+30+math.cos(a)*70, 330+math.sin(a)*60, px+30+math.cos(a)*130, 330+math.sin(a)*80+30, px+30+math.cos(a)*150, 330+math.sin(a)*70+70)
            ctx.set_line_width(10); ctx.stroke()
    # shop row
    cols = ('#f2d16b', '#e88a6a', '#8fc7e8', '#b9d98a')
    xs = [(60, 560), (680, 560), (1300, 560)]
    for i, (x0, w0) in enumerate(xs):
        top = 400 + (i % 2)*20
        ctx.rectangle(x0, top, w0, GROUND - top); paper(ctx, cols[(i+seed) % 4])
        ctx.move_to(x0-30, top+10); ctx.line_to(x0+w0/2, top-80); ctx.line_to(x0+w0+30, top+10); ctx.close_path(); paper(ctx, '#b5452f')
        for k in range(8):
            ctx.set_source_rgba(0.5, 0.15, 0.08, 0.35); ctx.set_line_width(3); ctx.move_to(x0-20+k*(w0+40)/8, top+6); ctx.line_to(x0+w0/2, top-74); ctx.stroke()
        rrect(ctx, x0+60, top+28, w0-120, 70, 10); paper(ctx, '#2b2622')
        text(ctx, shops[i], x0+w0/2, top+76, 38, '#ffe9a8')
        # door + window + counter
        rrect(ctx, x0+40, top+130, 160, GROUND-top-130, 8); paper(ctx, '#6b4428')
        rrect(ctx, x0+w0-230, top+140, 180, 120, 8); paper(ctx, '#fff4dc')
        ctx.set_source_rgba(0.4, 0.25, 0.1, 0.6); ctx.set_line_width(5); ctx.move_to(x0+w0-140, top+140); ctx.line_to(x0+w0-140, top+260); ctx.stroke()
        # awning stripes
        for k in range(7):
            ctx.rectangle(x0+k*w0/7, top+100, w0/7, 24); ctx.set_source_rgba(*hexc('#ffffff' if k % 2 else '#d9483b')); ctx.fill()
    ctx.rectangle(0, GROUND-6, W, 30); paper(ctx, '#c9a57a', 0, -4)
    # blue paper band with torn edge
    ctx.move_to(0, BAND+12)
    for xx in range(0, W+30, 30): ctx.line_to(xx, BAND + 8*math.sin(xx*0.37) + 4*math.sin(xx*1.3))
    ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path(); paper(ctx, '#1e3a8a', 0, -6)
    ctx.set_source_rgba(1, 1, 1, 0.04)
    for k in range(400):
        ctx.arc(rnd.uniform(0, W), rnd.uniform(BAND, H), rnd.uniform(1, 3), 0, 2*math.pi); ctx.fill()
    _bg[key] = surf
    return surf

def clouds(ctx, t):
    for i, (x0, y0, s) in enumerate(((200, 150, 1.0), (760, 110, 0.8), (1150, 210, 1.2))):
        x = (x0 + t*12*(1+i*0.3)) % (W+400) - 200
        ctx.save(); ctx.translate(x, y0); ctx.scale(s, s)
        for (dx, dy, r) in ((0, 0, 50), (55, -20, 60), (115, 0, 48), (60, 18, 50)): ctx.new_sub_path(); ctx.arc(dx, dy, r, 0, 2*math.pi)
        paper(ctx, '#fff8ee', 5, 7); ctx.restore()

# ------------------------------------------------------------------ characters
SKIN = '#a8673d'
def person(ctx, x, y, s, shirt, lower, female=False, talk=0.0, arm=0.0, face=1, name=None, t=0.0, old=False):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    bob = 3*math.sin(t*3 + x)
    ctx.translate(0, bob)
    # legs / mundu / saree
    if female:
        ctx.move_to(-70, -230); ctx.line_to(70, -230); ctx.line_to(95, 0); ctx.line_to(-95, 0); ctx.close_path(); paper(ctx, lower)
        ctx.rectangle(-95, -24, 190, 14); ctx.set_source_rgba(*hexc('#e0b040')); ctx.fill()
    else:
        ctx.move_to(-62, -200); ctx.line_to(62, -200); ctx.line_to(72, -10); ctx.line_to(-72, -10); ctx.close_path(); paper(ctx, lower)
        ctx.set_source_rgba(*hexc('#d4a640')); ctx.rectangle(-72, -24, 144, 8); ctx.fill()
        for fx in (-28, 28): rrect(ctx, fx-20, -12, 40, 14, 6); paper(ctx, '#3a2a20', 2, 2)
    # torso
    rrect(ctx, -70, -360, 140, 175, 40); paper(ctx, shirt)
    if female:
        ctx.move_to(-70, -350); ctx.line_to(30, -360); ctx.line_to(80, -190); ctx.line_to(40, -190); ctx.close_path(); ctx.set_source_rgba(*hexc(lower)); ctx.fill()
        ctx.set_source_rgba(*hexc('#e0b040')); ctx.set_line_width(6); ctx.move_to(30, -360); ctx.line_to(80, -190); ctx.stroke()
    else:
        ctx.set_source_rgba(0, 0, 0, 0.18)
        for k in range(3): ctx.arc(0, -330+k*45, 5, 0, 2*math.pi); ctx.fill()
    # arms
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sd in (-1, 1):
        lift = arm if sd == face else 0.0
        ex, ey = sd*95, -270 - lift*60
        hx, hy = sd*(110 + lift*40), -200 - lift*150
        ctx.set_source_rgba(*hexc(shirt)); ctx.set_line_width(36); ctx.move_to(sd*60, -335); ctx.line_to(ex, ey); ctx.stroke()
        ctx.set_source_rgba(*hexc(SKIN)); ctx.set_line_width(26); ctx.move_to(ex, ey); ctx.line_to(hx, hy); ctx.stroke()
        ctx.arc(hx, hy, 16, 0, 2*math.pi); ctx.fill()
    # head
    hy = -430
    ctx.rectangle(-16, -380, 32, 30); ctx.set_source_rgba(*hexc(SKIN)); ctx.fill()
    ctx.arc(0, hy, 62, 0, 2*math.pi); paper(ctx, SKIN)
    hair = '#d8d8d8' if old else '#1d140f'
    if female:
        ctx.arc(-face*40, hy-30, 34, 0, 2*math.pi); ctx.set_source_rgba(*hexc(hair)); ctx.fill()
        ctx.move_to(-64, hy+5); ctx.curve_to(-70, hy-80, 70, hy-80, 64, hy+5); ctx.curve_to(40, hy-35, -40, hy-35, -64, hy+5); ctx.close_path(); ctx.fill()
        for k in range(4): ctx.set_source_rgba(1, 1, 1, 1); ctx.arc(-face*40 - 20 + k*13, hy-62, 6, 0, 2*math.pi); ctx.fill()
        ctx.arc(0, hy-22, 6, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#d0202a')); ctx.fill()
    else:
        ctx.move_to(-63, hy-2); ctx.curve_to(-66, hy-78, 62, hy-86, 63, hy-6); ctx.curve_to(40, hy-42, -30, hy-44, -63, hy-2); ctx.close_path()
        ctx.set_source_rgba(*hexc(hair)); ctx.fill()
        ctx.move_to(-26+face*10, hy+24); ctx.curve_to(-10+face*10, hy+14, 10+face*10, hy+14, 26+face*10, hy+24); ctx.set_source_rgba(*hexc(hair)); ctx.set_line_width(9); ctx.stroke()
    for ex in (-20, 20):
        ctx.arc(ex+face*10, hy-6, 11, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.arc(ex+face*14, hy-5, 6, 0, 2*math.pi); ctx.set_source_rgba(0.1, 0.07, 0.05, 1); ctx.fill()
    my = hy + 38
    if talk > 0.05:
        ctx.save(); ctx.translate(face*10, my); ctx.scale(1, 0.35+talk); ctx.arc(0, 0, 12, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(*hexc('#5a1a1a')); ctx.fill()
    else:
        ctx.arc(face*10, my-6, 14, 0.3, math.pi-0.3); ctx.set_source_rgba(*OUTL); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()
    if name:
        w = text_w(ctx, name.upper(), 30) + 40
        rrect(ctx, x-w/2, y+2, w, 44, 10); paper(ctx, '#2b2622', 3, 3)
        text(ctx, name.upper(), x, y+35, 30, '#ffe9a8')

# ------------------------------------------------------------------ props
def note(ctx, x, y, label, s=1.0, ang=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    rrect(ctx, -95, -48, 190, 96, 8); paper(ctx, '#7fbf6a', 4, 5)
    rrect(ctx, -82, -36, 164, 72, 6); ctx.set_source_rgba(0.2, 0.4, 0.15, 0.5); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(-55, 0, 20, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 0.5); ctx.fill()
    text(ctx, label, 15, 14, 36 if len(label) < 6 else 30, '#173a10')
    ctx.restore()

def item(ctx, kind, x, y, s=1.0, t=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if kind == 'goat':
        ctx.save(); ctx.scale(1, 0.75); ctx.arc(0, -90, 80, 0, 2*math.pi); ctx.restore(); paper(ctx, '#f4f1e8')
        for lx in (-50, -20, 25, 55): ctx.rectangle(lx-8, -60, 16, 60); paper(ctx, '#f4f1e8', 2, 2)
        ctx.arc(85, -125, 36, 0, 2*math.pi); paper(ctx, '#f4f1e8')
        ctx.move_to(80, -158); ctx.curve_to(70, -200, 100, -205, 105, -185); ctx.set_source_rgba(*hexc('#7a5a3a')); ctx.set_line_width(8); ctx.stroke()
        ctx.arc(95, -130, 6, 0, 2*math.pi); ctx.set_source_rgba(0, 0, 0, 1); ctx.fill()
        ctx.move_to(100, -95); ctx.line_to(106, -70); ctx.set_line_width(6); ctx.stroke()
    elif kind == 'tea':
        rrect(ctx, -120, -40, 330, 40, 6); paper(ctx, '#8a5a34')
        ctx.move_to(-90, -170); ctx.line_to(-30, -170); ctx.line_to(-38, -40); ctx.line_to(-82, -40); ctx.close_path(); paper(ctx, '#c8823f')
        ctx.rectangle(-90, -170, 60, 22); ctx.set_source_rgba(1, 0.95, 0.85, 0.9); ctx.fill()
        for k in range(3):
            ph = t*2 + k
            ctx.move_to(-70+k*12, -185); ctx.curve_to(-80+k*12+8*math.sin(ph), -215, -60+k*12, -235, -70+k*12+6*math.sin(ph), -260)
            ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(4); ctx.stroke()
        ctx.save(); ctx.translate(100, -75); ctx.scale(1, 0.55); ctx.arc(0, 0, 70, 0, 2*math.pi); ctx.arc_negative(0, 0, 22, 2*math.pi, 0); ctx.restore(); paper(ctx, '#b8691f')
    elif kind == 'saree':
        for k, c in enumerate(('#d23a7a', '#f2b632', '#2fa86a')):
            rrect(ctx, -120 + k*10, -60 - k*55, 240, 52, 8); paper(ctx, c)
            ctx.rectangle(-120 + k*10, -26 - k*55, 240, 10); ctx.set_source_rgba(*hexc('#e8c35a')); ctx.fill()
    elif kind == 'soda':
        for k in range(3):
            bx = -70 + k*70
            rrect(ctx, bx-22, -150, 44, 150, 12); paper(ctx, '#a8e0d8')
            ctx.rectangle(bx-10, -190, 20, 44); paper(ctx, '#a8e0d8', 2, 2)
            ctx.arc(bx, -110, 12, 0, 2*math.pi); ctx.set_source_rgba(0.2, 0.5, 0.5, 0.6); ctx.fill()
    elif kind == 'puttu':
        rrect(ctx, -160, -20, 320, 20, 6); paper(ctx, '#3f8f3f')
        for k in range(5):
            px = -120 + k*60
            rrect(ctx, px-24, -110, 48, 92, 10); paper(ctx, '#fbf5e6', 3, 3)
            for b in range(2): ctx.rectangle(px-24, -85+b*35, 48, 8); ctx.set_source_rgba(*hexc('#8a5a34')); ctx.fill()
    elif kind == 'chips':
        for k in range(3):
            ctx.save(); ctx.translate(-90 + k*90, 0); ctx.rotate((k-1)*0.08)
            ctx.move_to(-40, -170); ctx.line_to(40, -170); ctx.line_to(46, 0); ctx.line_to(-46, 0); ctx.close_path(); paper(ctx, '#f2c230')
            ctx.arc(0, -85, 24, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#e8762a')); ctx.fill()
            text(ctx, 'CHIPS', 0, -130, 20, '#7a2a10'); ctx.restore()
    elif kind == 'onam':
        for r, c in ((150, '#f2b632'), (115, '#e8762a'), (80, '#d23a3a'), (45, '#f4f1e8'), (18, '#2fa86a')):
            ctx.save(); ctx.scale(1, 0.4); ctx.arc(0, -10, r, 0, 2*math.pi); ctx.restore(); paper(ctx, c, 2, 3)
    elif kind == 'calendar':
        rrect(ctx, -110, -260, 220, 250, 14); paper(ctx, '#ffffff')
        rrect(ctx, -110, -260, 220, 70, 14); ctx.set_source_rgba(*hexc('#d9483b')); ctx.fill()
        text(ctx, 'TUESDAY', 0, -213, 32, '#ffffff'); text(ctx, '24', 0, -60, 110, '#2b2622')
    elif kind == 'key':
        rrect(ctx, -30, -160, 60, 110, 10); paper(ctx, '#d9483b'); text(ctx, '7', 0, -92, 46, '#ffffff')
        ctx.set_source_rgba(*hexc('#e8c35a')); ctx.set_line_width(10); ctx.move_to(0, -50); ctx.line_to(0, 10); ctx.stroke()
    ctx.restore()

def bubble(ctx, x, y, s, p=1.0, size=48, col='#2b2622', bg='#ffffff', tail=0):
    if p <= 0: return
    w = text_w(ctx, s, size) + 70; h = size + 50
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    rrect(ctx, -w/2, -h/2, w, h, 30); ctx.move_to(tail-20, h/2-4); ctx.line_to(tail, h/2+36); ctx.line_to(tail+24, h/2-4); ctx.close_path(); paper(ctx, bg, 4, 5)
    text(ctx, s, 0, size*0.36, size, col); ctx.restore()

def stamp(ctx, x, y, s, p, size=80, col='#d9283b', ang=-0.12):
    if p <= 0: return
    sc = 1 + 1.6*(1-clamp(p*1.5))
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(sc, sc)
    w = text_w(ctx, s, size) + 60; a = clamp(p*2)
    rrect(ctx, -w/2, -size*0.75, w, size*1.5, 14); ctx.set_source_rgba(*hexc(col, a)); ctx.set_line_width(10); ctx.stroke()
    text(ctx, s, 0, size*0.36, size, col, alpha=a); ctx.restore()

def sign(ctx, x, y, s, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc); ctx.rotate(-0.03)
    w = text_w(ctx, s, 58) + 80
    rrect(ctx, -w/2, -60, w, 120, 10); paper(ctx, '#fff4dc', 6, 8)
    ctx.set_source_rgba(0.85, 0.3, 0.2, 1); ctx.set_line_width(6); rrect(ctx, -w/2+10, -50, w-20, 100, 8); ctx.stroke()
    for px in (-w/2+24, w/2-24): ctx.arc(px, -40, 7, 0, 2*math.pi); ctx.set_source_rgba(0.3, 0.3, 0.3, 1); ctx.fill()
    text(ctx, s, 0, 20, 58, '#2b2622'); ctx.restore()

def clock5(ctx, x, y, t, t0, r=120):
    left = 5 - (t - t0)
    n = max(1, min(5, math.ceil(left)))
    frac = clamp(left - (n-1))
    ctx.arc(x, y, r+14, 0, 2*math.pi); paper(ctx, '#2b2622')
    ctx.arc(x, y, r, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.move_to(x, y); ctx.arc(x, y, r-10, -math.pi/2, -math.pi/2 + 2*math.pi*clamp(left/5)); ctx.close_path(); ctx.set_source_rgba(*hexc('#f2b632', 0.6)); ctx.fill()
    sc = 1 + 0.25*frac**3
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc); text(ctx, str(n), 0, 45, 130, '#d9283b'); ctx.restore()

def score_tag(ctx, i):
    rrect(ctx, W-330, 24, 300, 64, 32); paper(ctx, '#2b2622', 3, 4)
    text(ctx, f'PUZZLE {i+1}/{N}', W-180, 68, 34, '#ffe9a8')

HOOKS = [('ഇത് എളുപ്പമാണെന്ന് തോന്നും. പക്ഷേ ശ്രദ്ധിക്കണം!', 'Looks easy... be *careful!*'),
         ('ഇത് കേട്ടാൽ പലരും കുഴങ്ങും!', 'This one confuses *many!*'),
         ('നന്നായി കേൾക്കൂ, ഓരോ സംഖ്യയും പ്രധാനമാണ്.', 'Listen closely, *every number* matters.')]
WRONG2 = {'puttu': dict(ml='മിക്കവരും പറയും ബാബു പറഞ്ഞത് ശരിയാണെന്ന്.', en='Most people say Babu is *right...*'),
          'exam': dict(ml='മിക്കവരും വിരലിൽ എണ്ണാൻ തുടങ്ങും!', en='Most people start counting on their *fingers!*'),
          'lodge': dict(ml='ഇത് കേട്ട് എല്ലാവരും കുഴങ്ങി.', en='Everyone is *confused...*')}
TAKE = {'goat': ('ഓർക്കുക, ഓരോ കച്ചവടവും വേറെ വേറെ കണക്കാക്കണം.', 'Remember: count *each deal* separately.'),
        'tea': ('ആദ്യം തോന്നുന്ന ഉത്തരം എപ്പോഴും ശരിയാകില്ല.', 'The *first* answer that pops up is not always right.'),
        'saree': ('കിഴിവിനു മുകളിൽ കിഴിവ്, എപ്പോഴും കുറഞ്ഞ ലാഭമാണ്.', 'Discount on discount always saves *less.*'),
        'soda': ('ഫ്രീ കിട്ടിയ കുപ്പികളും വീണ്ടും കാലിയാകും!', 'Free bottles become *empties* too!'),
        'puttu': ('ആരു കൂടുതൽ കൊടുത്തോ, അവർക്കാണ് കൂടുതൽ പണം.', 'Whoever *gave more* gets more money.'),
        'chips': ('മെഷീനുകൾ കൂടുമ്പോൾ ജോലിയും കൂടുന്നു. സമയം മാറുന്നില്ല.', 'More machines, more work, *same time.*'),
        'age': ('പ്രായം കൂടുന്നത് രണ്ടുപേർക്കും ഒരുപോലെയാണ്.', 'Both get older at the *same speed.*'),
        'exam': ('മുഴുവൻ ആഴ്ചകൾ മാറ്റിവെച്ച്, ബാക്കി ദിവസം മാത്രം എണ്ണിയാൽ മതി.', 'Remove full weeks, count only the *rest.*'),
        'lodge': ('തെറ്റായ കൂട്ടലാണ് നമ്മളെ കുഴപ്പിക്കുന്നത്.', 'Only the *wrong sum* tricks you.')}

XS = {1: [700], 2: [560, 1360], 3: [420, 960, 1500]}

# ------------------------------------------------------------------ beats
def make_beats():
    beats = []
    hard = SL[-1]
    beats.append(dict(id='t1', scene='teaser', st=hard, ml=f'ഒൻപത് പണക്കണക്ക് ചോദ്യങ്ങൾ. ഒരു ശതമാനം പേർക്ക് മാത്രമേ എല്ലാം ശരിയാക്കാൻ പറ്റൂ!',
                      en=f'*{N}* money brain teasers. Only *1%* get all of them!'))
    beats.append(dict(id='t2', scene='teaser', st=hard, ml='ഓരോ ശരിയുത്തരത്തിനും ഒരു പോയിന്റ്. തുടങ്ങാം!', en='*1 point* for each right answer. Let\'s *go!*'))
    for i, st in enumerate(SL):
        p = f'p{i}_'
        beats.append(dict(id=p+'a', scene='title', st=st, i=i, ml=f'ചോദ്യം നമ്പർ {NUM[i]}.', en=f'Puzzle {i+1}: *{st["title"]}*'))
        hk = HOOKS[i % len(HOOKS)]
        beats.append(dict(id=p+'h', scene='title', st=st, i=i, ml=hk[0], en=f'Puzzle {i+1}: *{st["title"]}*  ' + hk[1]))
        for j, b in enumerate(st['setup']):
            d = dict(b); d.update(id=p+f's{j}', scene='story', st=st, i=i, j=j); beats.append(d)
        if not st['wrong'] and st['key'] in WRONG2: st['wrong'] = WRONG2[st['key']]
        if st['wrong']:
            d = dict(st['wrong']); d.update(id=p+'w', scene='story', st=st, i=i, j=len(st['setup'])-1, keep=True, wrongbub=True); beats.append(d)
        d = dict(st['q']); d.update(id=p+'q', scene='question', st=st, i=i); beats.append(d)
        beats.append(dict(id=p+'p', scene='pause', st=st, i=i, ml='ഉത്തരം ആലോചിക്കൂ!', en='Think about the *answer...*', post=5.0))
        for j, b in enumerate(st['ans']):
            d = dict(b); d.update(id=p+f'x{j}', scene='answer', st=st, i=i, j=j, last=(j == len(st['ans'])-1))
            if j == len(st['ans'])-1: d['post'] = 0.8
            beats.append(d)
        tk = TAKE[st['key']]
        beats.append(dict(id=p+'tk', scene='answer', st=st, i=i, j=len(st['ans']), last=True, ml=tk[0], en=tk[1]))
        beats.append(dict(id=p+'pt', scene='answer', st=st, i=i, j=len(st['ans']), last=True, point=True, ml='ശരിയായെങ്കിൽ, ഒരു പോയിന്റ് എടുക്കൂ!', en='Got it right? Take *+1 point!*', post=0.4))
        if i == 4:
            beats.append(dict(id='half', scene='end', half=True, ml='പകുതി കഴിഞ്ഞു! ഇതുവരെ എത്ര ശരിയായി? ബാക്കി നാലെണ്ണം കൂടുതൽ കടുപ്പമാണ്!', en='Halfway! How many so far? The last *4* are *harder!*'))
    beats.append(dict(id='e1', scene='end', ml='നിങ്ങൾക്ക് എത്ര എണ്ണം ശരിയായി? സ്കോർ കമന്റ് ചെയ്യൂ!', en='How many did you get? *Comment your score!*'))
    beats.append(dict(id='e2', scene='end', share=True, ml='ബുദ്ധിമാനാണെന്ന് കരുതുന്ന ഒരു കൂട്ടുകാരന് ഇത് അയച്ചു കൊടുക്കൂ. പിന്നെ സബ്സ്ക്രൈബ് ചെയ്യൂ!',
                      en='Send this to a friend who thinks they\'re *smart.* And *Subscribe!*', post=4.0))
    return beats

# ------------------------------------------------------------------ draw
def draw_street(ctx, t, b, tl):
    st = b['st']; seed = SL.index(st)
    ctx.set_source_surface(street_bg(st['shops'], seed)); ctx.paint()
    clouds(ctx, t)
    chars = st['chars']; xs = XS[len(chars)]
    j = b.get('j', 0)
    # item position: held by item_at (last set in setup up to j)
    at = None; sg = None
    for k in range(j+1):
        sb = st['setup'][k]
        if 'item_at' in sb: at = sb['item_at']
    if b['scene'] == 'story' and 'sign' in b and not b.get('wrongbub'): sg = b['sign']
    talker = None
    if b['scene'] == 'story' and not b.get('wrongbub'):
        if 'bub' in b: talker = b['bub'][0]
        elif 'pay' in b: talker = b['pay'][0]
    for ci, (nm, sh, lo, fem) in enumerate(chars):
        face = 1 if xs[ci] < W/2 else -1
        if len(chars) == 1: face = 1
        talk = abs(math.sin(t*13))*0.8 if (talker == ci and b['t0'] < t < b['t1']) else 0
        arm = 0.0
        if b['scene'] == 'story' and 'pay' in b and b['pay'][0] == ci: arm = clamp(prog(t, b['t0'], 0.4))
        person(ctx, xs[ci], GROUND-10, 0.95, sh, lo, fem, talk, arm, face, nm, t, old=(nm == 'Grandma'))
    if at is not None:
        ix = W/2 + 0 if at == -1 else xs[at] + (170 if xs[at] < W/2 or len(chars) == 1 else -170)
        item(ctx, st['item'], ix, GROUND-10, 1.0, t)
    if b['scene'] != 'story': return
    t0 = b['t0']
    if 'pay' in b and not b.get('wrongbub'):
        a, c, lab = b['pay']; pp = sprog(t, t0+0.3, 1.2)
        x = xs[a] + (xs[c]-xs[a])*pp; y = 520 - 120*math.sin(math.pi*pp)
        note(ctx, x, y, lab, 1.1, 0.25*math.sin(pp*6))
    if 'bub' in b and not b.get('wrongbub'):
        ci, s = b['bub']; bubble(ctx, xs[ci], 170, s, prog(t, t0+0.2, 0.3), size=54, tail=0)
    if 'bub2' in b:
        ci, s = b['bub2']; bubble(ctx, xs[ci], 170, s, prog(t, t0+0.8, 0.3), size=54, tail=0)
    if sg: sign(ctx, W/2, 230, sg, prog(t, t0+0.2, 0.35))
    if b.get('wrongbub'):
        bubble(ctx, W/2, 200, 'MOST SAY... ?', prog(t, t0+0.1, 0.3), size=58, col='#d9283b')

def draw_factory(tl):
    def draw(ctx, t):
        cur = None
        for b in tl.beats:
            if t >= b['t0'] - 0.12: cur = b
        b = cur or tl.beats[0]
        t0, t1 = b['t0'], b['t1']; sc = b['scene']
        z = 1.0 + 0.05*(1 - sprog(t, t0-0.12, 0.35)) + 0.015*prog(t, t0, t1-t0+0.5)
        ctx.save(); ctx.translate(W/2, H/2); ctx.scale(z, z); ctx.translate(-W/2, -H/2)
        if sc == 'teaser':
            st = b['st']; draw_street(ctx, t, dict(b, scene='question', j=len(st['setup'])-1), tl)
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.35); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            bubble(ctx, W/2, 250, st['q']['box'], prog(t, 0.1, 0.35), size=86)
            if b['id'] == 't1': stamp(ctx, W/2, 520, 'ONLY 1% GET ALL!', prog(t, t0+1.2, 0.4), size=70, col='#ffd23f', ang=-0.06)
            else: pill(ctx, W/2, 520, 560, 110, '#2fa86a', '+1 POINT EACH', size=56, p=prog(t, t0+0.3, 0.3))
        elif sc == 'title':
            st = b['st']; draw_street(ctx, t, dict(b, scene='question', j=-1), tl)
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.45); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            p = back(prog(t, t0, 0.4))
            ctx.save(); ctx.translate(W/2, 400); ctx.scale(p, p); ctx.rotate(-0.02)
            rrect(ctx, -520, -190, 1040, 380, 26); paper(ctx, '#fff4dc', 10, 12)
            text(ctx, f'PUZZLE {b["i"]+1}', 0, -50, 120, '#d9483b'); text(ctx, b['st']['title'].upper(), 0, 90, 70, '#2b2622')
            ctx.restore()
            score_tag(ctx, b['i'])
        elif sc == 'story':
            draw_street(ctx, t, b, tl); score_tag(ctx, b['i'])
        elif sc == 'question':
            st = b['st']; draw_street(ctx, t, dict(b, j=len(st['setup'])-1), tl)
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.25); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            bubble(ctx, W/2, 260, st['q']['box'], prog(t, t0+0.15, 0.35), size=92)
            for k, (qx, qy) in enumerate(((330, 200), (1590, 230), (420, 520), (1500, 540))):
                text(ctx, '?', qx, qy + 10*math.sin(t*4+k), 130, '#ffd23f', alpha=prog(t, t0+0.3+k*0.1, 0.2))
            score_tag(ctx, b['i'])
        elif sc == 'pause':
            st = b['st']; draw_street(ctx, t, dict(b, j=len(st['setup'])-1), tl)
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.55); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            bubble(ctx, W/2, 140, st['q']['box'], 1.0, size=60)
            clock5(ctx, W/2, 440, t, b['t1'] + 0.1 if t > b['t1'] else b['t1'] + 0.1)
            pill(ctx, W/2, 680, 620, 90, '#d9483b', 'PAUSE AND THINK!', size=48, p=prog(t, t0, 0.3))
            score_tag(ctx, b['i'])
        elif sc == 'answer':
            st = b['st']
            ctx.set_source_surface(street_bg(st['shops'], SL.index(st))); ctx.paint()
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.5); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            first = tl.by[f'p{b["i"]}_x0']['t0']
            p = back(prog(t, first, 0.35))
            ctx.save(); ctx.translate(W/2, 410); ctx.scale(p, p)
            rrect(ctx, -620, -360, 1240, 700, 24); paper(ctx, '#fff8ea', 10, 12)
            for k in range(1, 9):
                ctx.set_source_rgba(0.55, 0.7, 0.9, 0.35); ctx.set_line_width(2); ctx.move_to(-580, -300+k*70); ctx.line_to(580, -300+k*70); ctx.stroke()
            ctx.set_source_rgba(0.85, 0.3, 0.3, 0.5); ctx.move_to(-500, -340); ctx.line_to(-500, 330); ctx.stroke()
            text(ctx, 'ANSWER', 0, -290, 52, '#d9483b')
            nl = len(st['ans'])
            for k, a in enumerate(st['ans']):
                bk = tl.by[f'p{b["i"]}_x{k}']
                if t < bk['t0'] - 0.05: continue
                ap = prog(t, bk['t0'], 0.3)
                yy = -170 + k*(110 if nl <= 3 else 92)
                text(ctx, a['line'], -470, yy, 56 if nl <= 3 else 50, '#2b2622', align='l', alpha=ap)
            ctx.restore()
            if b['j'] >= nl - 1:
                st0 = tl.by[f'p{b["i"]}_x{nl-1}']['t0']
                stamp(ctx, W/2 + 260, 650, st['stamp'], prog(t, st0+0.5, 0.35), size=74)
            if b.get('point'):
                pill(ctx, 260, 140, 360, 90, '#2fa86a', '+1 POINT', size=50, p=prog(t, t0+0.2, 0.3))
            score_tag(ctx, b['i'])
        elif sc == 'end':
            ctx.set_source_surface(street_bg(SL[0]['shops'], 0)); ctx.paint(); clouds(ctx, t)
            ctx.set_source_rgba(0.05, 0.05, 0.15, 0.45); ctx.rectangle(0, 0, W, BAND); ctx.fill()
            # comment box mock-up
            rrect(ctx, 460, 120, 1000, 300, 26); paper(ctx, '#ffffff', 8, 10)
            ctx.arc(540, 200, 40, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#8fc7e8')); ctx.fill()
            text(ctx, 'Add a comment...', 610, 214, 40, '#9a9a9a', align='l')
            word = f'My score: {min(N, int(max(0, t-t0)*3))}/{N}' if not b.get('half') else 'So far: 5/5!'
            text(ctx, word, 610, 320, 60, '#2b2622', align='l')
            if (t*2) % 1 < 0.6: ctx.rectangle(610 + text_w(ctx, word, 60) + 8, 270, 7, 66); ctx.set_source_rgba(*hexc('#d9283b')); ctx.fill()
            if b.get('half'):
                pill(ctx, W/2, 560, 700, 110, '#2fa86a', 'HALFWAY: __/5 ?', size=56, p=prog(t, t0+0.2, 0.3))
            if b.get('share'):
                bubble(ctx, W/2, 530, 'Send this to a friend who thinks they\'re smart!', prog(t, t0, 0.3), size=44)
            pp = 1 + 0.06*math.sin(t*8)
            ctx.save(); ctx.translate(W/2, 700); ctx.scale(pp, pp); rrect(ctx, -230, -55, 460, 110, 55); ctx.set_source_rgba(*hexc('#e62117')); ctx.fill()
            text(ctx, 'SUBSCRIBE', 0, 18, 52, '#ffffff'); ctx.restore()
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and b is not tl.beats[0]: ctx.set_source_rgba(1, 1, 1, 0.25*fl); ctx.paint()
        caption(ctx, b.get('en'), t, t0, t1, y=900, size=56, maxw=1700)
    return draw

def sfx_list(tl):
    sfx = []
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0']-0.12, 'whoosh', 0.5))
        sc = b['scene']
        if sc == 'story' and 'pay' in b and not b.get('wrongbub'): sfx.append((b['t0']+0.3, 'pop', 0.5))
        if sc == 'story' and ('bub' in b or 'sign' in b): sfx.append((b['t0']+0.2, 'pop', 0.6))
        if sc == 'story' and b.get('wrongbub'): sfx.append((b['t0']+0.1, 'wrong', 0.45))
        if sc == 'question': sfx.append((b['t0']+0.15, 'thud', 0.6))
        if sc == 'pause':
            for k in range(5): sfx.append((b['t1']+0.1+k, 'tick', 0.5))
        if sc == 'answer' and b['j'] == len(b['st']['ans'])-1: sfx.append((b['t0']+0.5, 'thud', 0.6))
        if sc == 'answer' and b.get('point'): sfx.append((b['t0']+0.2, 'right', 0.6))
        if sc == 'end' and not b.get('share') and not b.get('half'):
            for k in range(8): sfx.append((b['t0']+k*0.33, 'tick', 0.25))
    return sfx

if __name__ == '__main__':
    beats = make_beats()
    tl = Timeline(beats, lead=0.15, gap=0.2, think=0, spk=NARR)
    total = tl.end + 0.5
    draw = draw_factory(tl)
    mode = sys.argv[1]
    OUT = '/home/claude/money/out'; os.makedirs(OUT, exist_ok=True)
    print('TOTAL', round(total, 1), 'beats', len(beats))
    if mode == 'stills':
        ids = ['t1', 'p0_a', 'p0_s0', 'p0_s1', 'p0_w', 'p0_q', 'p0_p', 'p0_x2', 'p1_s2', 'p2_s2', 'p3_s2', 'p4_s1', 'p4_x3', 'p6_s1', 'p8_s2', 'p8_x2', 'e2', 'p4_pt', 'half', 'p0_h']
        for i, k in enumerate(ids):
            b = tl.by[k]; tt = b['t1'] - 0.1 if b['scene'] != 'pause' else b['t1'] + 2.3
            if b['scene'] == 'story' and 'pay' in b: tt = b['t0'] + 0.9
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt); surf.write_to_png(f'{OUT}/s{i:02d}.png')
    elif mode == 'audio':
        build_mix(f'{OUT}/long.wav', tl, sfx_list(tl), total)
        ch = [(0, 'Intro')] + [(tl.by[f'p{i}_a']['t0'], f'Puzzle {i+1}: {s["title"]}') for i, s in enumerate(SL)] + [(tl.by['e1']['t0'], 'Your score')]
        json.dump(dict(total=total, ch=ch, ans=[(s['title'], s['short']) for s in SL]), open(f'{OUT}/meta.json', 'w'))
    elif mode == 'video':
        part, nparts = int(sys.argv[2]), int(sys.argv[3])
        nf = int(total*30); a = nf*part//nparts; z = nf*(part+1)//nparts
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
               '-b:v', '1000k', '-maxrate', '1600k', '-bufsize', '3200k', '-pix_fmt', 'yuv420p', f'{OUT}/part{part}.mp4']
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
        for i in range(a, z):
            ctx.save(); draw(ctx, i/30); ctx.restore(); surf.flush(); p.stdin.write(surf.get_data())
            if i % 600 == 0: print(part, i, z, flush=True)
        p.stdin.close(); p.wait()
