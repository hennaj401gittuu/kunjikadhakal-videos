"""Puzzle-video engine for the new Kunjikadhakal format: narration timeline, drawing primitives, audio, ASS, render."""
import os, sys, math, hashlib, subprocess, json, random
import numpy as np, cairo, soundfile as sf
sys.path.insert(0, '/home/claude/ml'); sys.path.insert(0, '/home/claude')
import audio as A

FONTS = '/home/claude/fonts'
SR = 44100
VO_DIR = '/home/claude/pz/vo'; os.makedirs(VO_DIR, exist_ok=True)

# ---------------- math helpers
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, p): return a+(b-a)*p
def prog(t, t0, d): return clamp((t-t0)/d) if d > 0 else (1. if t >= t0 else 0.)
def sprog(t, t0, d): return smooth(prog(t, t0, d))
def back(x, s=1.7):  # overshoot ease-out
    x = clamp(x)-1; return 1+x*x*((s+1)*x+s)
def bounce(x):
    x = clamp(x)
    if x < 1/2.75: return 7.5625*x*x
    if x < 2/2.75: x -= 1.5/2.75; return 7.5625*x*x+.75
    if x < 2.5/2.75: x -= 2.25/2.75; return 7.5625*x*x+.9375
    x -= 2.625/2.75; return 7.5625*x*x+.984375
def hexc(h, a=1.):
    h = h.lstrip('#'); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)

OUT = (0.16, 0.12, 0.10, 1)  # outline

def fill_stroke(ctx, col, lw=4, out=OUT):
    ctx.set_source_rgba(*hexc(col) if isinstance(col, str) else col); ctx.fill_preserve()
    ctx.set_source_rgba(*out); ctx.set_line_width(lw); ctx.stroke()

def rrect(ctx, x, y, w, h, r):
    r = min(r, w/2, h/2)
    ctx.new_sub_path(); ctx.arc(x+w-r, y+r, r, -math.pi/2, 0); ctx.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    ctx.arc(x+r, y+h-r, r, math.pi/2, math.pi); ctx.arc(x+r, y+r, r, math.pi, 1.5*math.pi); ctx.close_path()

# ---------------- TTS
TTS_OK = set(' ,?ംഃഅആഇഈഉഊഋഎഏഐഒഓഔകഖഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരറലളഴവശഷസഹാിീുൂൃെേൈൊോൌ്ൗൺൻർൽൾ' + "!¡'(),-.:;¿? ")
def clean(text):
    t = text.replace('‍', '').replace('‌', '').replace('...', ',').replace('—', ',').replace('–', ',')
    t = t.replace('‘', "'").replace('’', "'").replace('“', '').replace('”', '').replace('"', '')
    bad = [c for c in t if c not in TTS_OK]
    if bad: raise ValueError('bad chars %r in %s' % (set(bad), text))
    return t

NARR = ('female', 1.0, 1.10)  # speaker, pitch, tempo (lively)
def voice(text, spk=NARR):
    text = clean(text)
    key = hashlib.md5(('%s|%s|%s|%s' % (spk[0], spk[1], spk[2], text)).encode()).hexdigest()[:16]
    out = f'{VO_DIR}/{key}.wav'
    if not os.path.exists(out):
        import mltts
        raw = out + '.raw.wav'; mltts.say(text, spk[0], raw)
        P, T = spk[1], spk[2]
        af = (f'asetrate=22050*{P},aresample=44100,atempo={T/P:.4f},'
              'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
              'loudnorm=I=-17:TP=-2')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', af, '-ar', '44100', '-ac', '1', out], check=True)
        os.remove(raw)
    return out

def wav_dur(p): return sf.info(p).duration

# ---------------- timeline
class Timeline:
    """beats: list of dict(id, ml, en, pre=0, post=0, think=False). Builds start/end times."""
    def __init__(self, beats, lead=0.4, gap=0.35, think=2.2, spk=None):
        self.beats = beats; t = lead; self.by = {}; self.think = think
        for b in beats:
            t += b.get('pre', 0)
            b['wav'] = (voice(b['ml'], spk) if spk else voice(b['ml'])) if b.get('ml') else None
            b['d'] = wav_dur(b['wav']) if b['wav'] else b.get('dur', 1.0)
            b['t0'] = t; b['t1'] = t + b['d']
            t = b['t1'] + gap + b.get('post', 0)
            if b.get('think'): b['think_t'] = b['t1'] + 0.15; t += self.think
            self.by[b['id']] = b
        self.end = t
    def __getitem__(self, k): return self.by[k]
    def t0(self, k): return self.by[k]['t0']
    def t1(self, k): return self.by[k]['t1']

# ---------------- drawing primitives
def sky(ctx, W, H, top='#7cc6f2', bot='#cfeefc', h=None):
    h = h or H
    g = cairo.LinearGradient(0, 0, 0, h); g.add_color_stop_rgba(0, *hexc(top)); g.add_color_stop_rgba(1, *hexc(bot))
    ctx.set_source(g); ctx.rectangle(0, 0, W, h); ctx.fill()

def cloud(ctx, x, y, s, a=0.95):
    ctx.set_source_rgba(1, 1, 1, a)
    for dx, dy, r in ((0, 0, 34), (38, -14, 42), (82, 0, 34), (40, 12, 36)):
        ctx.arc(x+dx*s, y+dy*s, r*s, 0, 2*math.pi); ctx.fill()

def hills(ctx, W, y, cols=('#9cc7a0', '#86b98d')):
    for i, c in enumerate(cols):
        ctx.set_source_rgba(*hexc(c)); ctx.move_to(0, y+40)
        for k in range(0, W+80, 80):
            ctx.line_to(k, y - 40*math.sin(k/170.0+i*1.7) - 25*i)
        ctx.line_to(W, y+200); ctx.line_to(0, y+200); ctx.close_path(); ctx.fill()

def grass(ctx, x0, y0, w, h, stripes=True):
    ctx.set_source_rgba(*hexc('#6cc04a')); ctx.rectangle(x0, y0, w, h); ctx.fill()
    if stripes:
        ctx.set_source_rgba(1, 1, 1, 0.06)
        for k in range(int(x0)-int(h), int(x0+w), 90):
            ctx.move_to(k, y0+h); ctx.line_to(k+45, y0+h); ctx.line_to(k+45+h*0.5, y0); ctx.line_to(k+h*0.5, y0); ctx.close_path(); ctx.fill()

def pine(ctx, x, y, s=1.0):
    ctx.set_source_rgba(*hexc('#6b4a2b')); ctx.rectangle(x-6*s, y-30*s, 12*s, 32*s); ctx.fill()
    for i, (w, hh) in enumerate(((60, 55), (48, 50), (34, 44))):
        yy = y-30*s-i*32*s
        ctx.move_to(x-w*s, yy); ctx.line_to(x, yy-hh*s*1.4); ctx.line_to(x+w*s, yy); ctx.close_path()
        fill_stroke(ctx, '#3f8f4a', 3)

def round_tree(ctx, x, y, s=1.0):
    ctx.set_source_rgba(*hexc('#6b4a2b')); ctx.rectangle(x-7*s, y-60*s, 14*s, 62*s); ctx.fill()
    ctx.arc(x, y-95*s, 48*s, 0, 2*math.pi); fill_stroke(ctx, '#58b04a', 3)

def coconut(ctx, x, y, s=1.0, sway=0.0):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(-8*s, 0); ctx.curve_to(-6*s, -100*s, 10*s+sway*10, -200*s, 18*s+sway*20, -300*s)
    ctx.line_to(30*s+sway*20, -300*s); ctx.curve_to(22*s+sway*10, -200*s, 6*s, -100*s, 8*s, 0); ctx.close_path()
    fill_stroke(ctx, '#9b6b3f', 3)
    tx, ty = 24*s+sway*20, -300*s
    for k in range(7):
        a = -math.pi/2 + (k-3)*0.55 + sway*0.1
        ctx.move_to(tx, ty)
        ctx.curve_to(tx+math.cos(a-0.3)*60*s, ty+math.sin(a-0.3)*60*s-20*s, tx+math.cos(a)*110*s, ty+math.sin(a)*110*s, tx+math.cos(a+0.25)*130*s, ty+math.sin(a+0.25)*130*s+30*s)
        ctx.set_source_rgba(*hexc('#3f9a3a')); ctx.set_line_width(14*s); ctx.stroke()
    for dx in (-10, 8, 0):
        ctx.arc(tx+dx*s, ty+12*s, 9*s, 0, 2*math.pi); fill_stroke(ctx, '#7a5a2a', 2)
    ctx.restore()

def house(ctx, x, y, s=1.0, wall='#f4e3c1', roof='#c8553d'):
    w, h = 160*s, 90*s
    ctx.rectangle(x-w/2, y-h, w, h); fill_stroke(ctx, wall, 3)
    ctx.move_to(x-w/2-22*s, y-h); ctx.line_to(x, y-h-70*s); ctx.line_to(x+w/2+22*s, y-h); ctx.close_path(); fill_stroke(ctx, roof, 3)
    ctx.rectangle(x-18*s, y-55*s, 36*s, 55*s); fill_stroke(ctx, '#8a5a35', 3)
    ctx.rectangle(x-62*s, y-65*s, 28*s, 26*s); fill_stroke(ctx, '#9fd6f0', 3)
    ctx.rectangle(x+34*s, y-65*s, 28*s, 26*s); fill_stroke(ctx, '#9fd6f0', 3)

def bush(ctx, x, y, s=1.0):
    for dx, r in ((-18, 18), (0, 24), (20, 17)):
        ctx.arc(x+dx*s, y-r*s*0.8, r*s, 0, 2*math.pi); fill_stroke(ctx, '#4ea33f', 3)

def stone(ctx, x, y, w, h, col='#a9adb3', seed=0):
    rnd = random.Random(seed); n = 9
    pts = []
    for k in range(n):
        a = math.pi + k*math.pi/(n-1)
        rr = 1 + rnd.uniform(-0.12, 0.1)
        pts.append((x+math.cos(a)*w/2*rr, y+math.sin(a)*h*rr))
    ctx.move_to(x-w/2, y)
    for p in pts: ctx.line_to(*p)
    ctx.line_to(x+w/2, y); ctx.close_path(); fill_stroke(ctx, col, 4)

def boulder(ctx, cx, cy, r, ang=0.0, col='#9aa0a8'):
    """round-ish rock centred at cx,cy, radius r, rotation ang"""
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(ang)
    rnd = random.Random(7); n = 14
    ctx.move_to(r, 0)
    for k in range(1, n+1):
        a = 2*math.pi*k/n; rr = r*(1+0.07*math.sin(3*a)+rnd.uniform(-0.03, 0.03))
        ctx.line_to(math.cos(a)*rr, math.sin(a)*rr*0.92)
    ctx.close_path(); fill_stroke(ctx, col, 5)
    ctx.set_source_rgba(1, 1, 1, 0.18); ctx.arc(-r*0.3, -r*0.35, r*0.35, 0, 2*math.pi); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(4)
    ctx.move_to(r*0.1, -r*0.2); ctx.line_to(r*0.35, r*0.05); ctx.line_to(r*0.25, r*0.3); ctx.stroke()
    ctx.restore()

def log(ctx, x, y, L, r, ang=0.0, col='#b07a45'):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    rrect(ctx, -L/2, -r, L, 2*r, r*0.5); fill_stroke(ctx, col, 4)
    ctx.set_source_rgba(0, 0, 0, 0.15); ctx.set_line_width(3)
    for k in range(1, 4): ctx.move_to(-L/2+k*L/4, -r*0.6); ctx.line_to(-L/2+k*L/4+12, r*0.4); ctx.stroke()
    ctx.restore()

def log_end(ctx, x, y, r, col='#c98d52'):
    ctx.arc(x, y, r, 0, 2*math.pi); fill_stroke(ctx, col, 4)
    ctx.set_source_rgba(0.45, 0.28, 0.12, 0.8); ctx.set_line_width(2.5)
    for k in (0.65, 0.35): ctx.arc(x, y, r*k, 0, 2*math.pi); ctx.stroke()

def rope(ctx, pts, col='#c9a26b', w=7):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.set_source_rgba(*OUT); ctx.set_line_width(w+4); ctx.stroke_preserve()
    ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(w); ctx.stroke()

def mark(ctx, x, y, r, ok, p=1.0):
    """big red X or green check in a circle, popping with scale p"""
    if p <= 0: return
    s = back(p)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.arc(0, 0, r, 0, 2*math.pi); ctx.set_source_rgba(*(hexc('#2fb34a') if ok else hexc('#e23b3b'))); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(r*0.12); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(r*0.24); ctx.set_source_rgba(1, 1, 1, 1)
    if ok:
        ctx.move_to(-r*0.45, 0); ctx.line_to(-r*0.1, r*0.35); ctx.line_to(r*0.5, -r*0.35)
    else:
        ctx.move_to(-r*0.4, -r*0.4); ctx.line_to(r*0.4, r*0.4); ctx.move_to(r*0.4, -r*0.4); ctx.line_to(-r*0.4, r*0.4)
    ctx.stroke(); ctx.restore()

def arrow(ctx, x0, y0, x1, y1, col='#ff3b30', w=14, head=34, p=1.0):
    if p <= 0: return
    x1 = lerp(x0, x1, p); y1 = lerp(y0, y1, p)
    a = math.atan2(y1-y0, x1-x0)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x0, y0); ctx.line_to(x1-math.cos(a)*head*0.6, y1-math.sin(a)*head*0.6)
    ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(w+8); ctx.stroke_preserve()
    ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(w); ctx.stroke()
    ctx.move_to(x1, y1); ctx.line_to(x1-math.cos(a-0.45)*head, y1-math.sin(a-0.45)*head)
    ctx.line_to(x1-math.cos(a+0.45)*head, y1-math.sin(a+0.45)*head); ctx.close_path()
    ctx.set_source_rgba(*hexc(col)); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(4); ctx.stroke()

def confetti(ctx, W, H, t, t0, n=90, seed=3):
    if t < t0: return
    rnd = random.Random(seed); cols = ['#ff5a5f', '#ffd23f', '#3bceac', '#5e60ce', '#ff8fab', '#4cc9f0']
    for i in range(n):
        x0 = rnd.uniform(0, W); sp = rnd.uniform(220, 420); ph = rnd.uniform(0, 6)
        dt = t - t0 - rnd.uniform(0, 0.8)
        if dt < 0: continue
        y = -30 + dt*sp; x = x0 + 40*math.sin(dt*3+ph)
        if y > H+40: continue
        ctx.save(); ctx.translate(x, y); ctx.rotate(dt*5+ph)
        ctx.set_source_rgba(*hexc(cols[i % len(cols)])); ctx.rectangle(-9, -5, 18, 10); ctx.fill(); ctx.restore()

def dust(ctx, x, y, t, t0, dur=0.9, n=10, spread=160, seed=1):
    p = prog(t, t0, dur)
    if p <= 0 or p >= 1: return
    rnd = random.Random(seed)
    for i in range(n):
        a = math.pi + rnd.uniform(0, math.pi); d = spread*smooth(p)*rnd.uniform(0.5, 1)
        r = rnd.uniform(14, 30)*(1-p*0.5)
        ctx.set_source_rgba(0.82, 0.74, 0.62, 0.75*(1-p))
        ctx.arc(x+math.cos(a)*d, y+math.sin(a)*d*0.35, r, 0, 2*math.pi); ctx.fill()

def splash(ctx, x, y, t, t0, dur=0.8, n=12, seed=2):
    p = prog(t, t0, dur)
    if p <= 0 or p >= 1: return
    rnd = random.Random(seed)
    for i in range(n):
        a = -math.pi/2 + rnd.uniform(-1.1, 1.1); v = rnd.uniform(180, 320)
        xx = x + math.cos(a)*v*p; yy = y + math.sin(a)*v*p + 500*p*p
        ctx.set_source_rgba(0.85, 0.95, 1, 1-p); ctx.arc(xx, yy, 9*(1-p*0.4), 0, 2*math.pi); ctx.fill()

# ---------------- stick-figure hero (Appu)
def person(ctx, x, y, s=1.0, face=1, mood='happy', lean=0.0, arm_l=(0.35, 0.2), arm_r=(-0.35, -0.2), walk=0.0,
           blink=False, sweat=0.0, shirt='#f6c445', pants='#3b6fc4', jump=0.0, lying=0.0):
    """y = feet ground. arm angles: (shoulder, elbow) radians from straight down, positive = forward."""
    ctx.save(); ctx.translate(x, y - jump*s); ctx.scale(s*face, s)
    if lying: ctx.translate(0, -0); ctx.rotate(-lying*math.pi/2*0.95)
    ctx.rotate(lean)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    hip = (0, -70)
    # legs
    for side, ph in ((-1, 0), (1, math.pi)):
        sw = math.sin(walk*2*math.pi + ph)*0.45 if walk else 0
        kx = hip[0] + side*6 + math.sin(sw)*34; ky = hip[1] + math.cos(sw)*34
        fx = kx + math.sin(sw*0.6)*36; fy = ky + 36
        ctx.move_to(hip[0]+side*6, hip[1]); ctx.line_to(kx, ky); ctx.line_to(fx, fy)
        ctx.set_source_rgba(*OUT); ctx.set_line_width(20); ctx.stroke_preserve()
        ctx.set_source_rgba(*hexc(pants)); ctx.set_line_width(14); ctx.stroke()
        rrect(ctx, fx-6, fy-6, 24, 12, 5); fill_stroke(ctx, '#5a3b2a', 3)
    # body
    rrect(ctx, -22, -138, 44, 74, 12); fill_stroke(ctx, shirt, 4)
    def arm(sh, el, side):
        sx, sy = side*20, -126
        a1 = sh; ex = sx + math.sin(a1)*30; ey = sy + math.cos(a1)*30
        a2 = sh + el; hx = ex + math.sin(a2)*30; hy = ey + math.cos(a2)*30
        ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.line_to(hx, hy)
        ctx.set_source_rgba(*OUT); ctx.set_line_width(16); ctx.stroke_preserve()
        ctx.set_source_rgba(*hexc('#e9b98f')); ctx.set_line_width(10); ctx.stroke()
        ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.set_source_rgba(*hexc(shirt)); ctx.set_line_width(11); ctx.stroke()
    arm(arm_l[0], arm_l[1], 1); arm(arm_r[0], arm_r[1], -1)
    # head
    hx, hy = 0, -170
    ctx.arc(hx, hy, 30, 0, 2*math.pi); fill_stroke(ctx, '#f0c39a', 4)
    ctx.move_to(hx-31, hy-4); ctx.curve_to(hx-30, hy-38, hx+30, hy-44, hx+31, hy-6)
    ctx.curve_to(hx+18, hy-20, hx-10, hy-22, hx-31, hy-4); ctx.close_path(); fill_stroke(ctx, '#3a2a20', 3)
    # face (looking right)
    ex1, ex2, ey = hx+6, hx+20, hy-2
    ctx.set_source_rgba(*OUT)
    if blink or mood == 'strain':
        ctx.set_line_width(3)
        for ex in (ex1, ex2): ctx.move_to(ex-5, ey); ctx.line_to(ex+5, ey); ctx.stroke()
    else:
        for ex in (ex1, ex2): ctx.arc(ex, ey, 3.6, 0, 2*math.pi); ctx.fill()
    ctx.set_line_width(3)
    if mood in ('worried', 'shock'):
        for ex, d in ((ex1, -1), (ex2, 1)): ctx.move_to(ex-6, ey-12+d*2); ctx.line_to(ex+6, ey-12-d*2); ctx.stroke()
    mx, my = hx+14, hy+14
    if mood == 'happy':
        ctx.arc(mx, my-4, 8, 0.2, math.pi-0.2); ctx.stroke()
    elif mood == 'big':
        ctx.arc(mx, my-4, 10, 0, math.pi); ctx.close_path(); fill_stroke(ctx, '#b03a3a', 3)
    elif mood == 'shock':
        ctx.arc(mx, my, 6, 0, 2*math.pi); fill_stroke(ctx, '#7a2a2a', 3)
    elif mood == 'worried':
        ctx.arc(mx, my+6, 7, math.pi+0.3, 2*math.pi-0.3); ctx.stroke()
    elif mood == 'strain':
        ctx.move_to(mx-8, my); ctx.line_to(mx+8, my); ctx.stroke()
    elif mood == 'think':
        ctx.move_to(mx-6, my+2); ctx.line_to(mx+7, my-1); ctx.stroke()
    ctx.set_source_rgba(1, 0.55, 0.55, 0.45); ctx.arc(hx+24, hy+8, 6, 0, 2*math.pi); ctx.fill()
    if sweat > 0:
        ctx.set_source_rgba(0.45, 0.75, 1, sweat)
        ctx.move_to(hx-20, hy-26); ctx.curve_to(hx-28, hy-14, hx-22, hy-6, hx-17, hy-12); ctx.curve_to(hx-14, hy-16, hx-16, hy-22, hx-20, hy-26)
        ctx.fill()
    ctx.restore()

# ---------------- ASS
def ts(x):
    x = max(0, x); h = int(x//3600); m = int(x % 3600//60); s = x % 60
    return '%d:%02d:%05.2f' % (h, m, s)

def ass_header(W, H, sub_size, sub_margin):
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Baloo Chettan 2,{sub_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,2,2,60,60,{sub_margin},1
Style: Big,Baloo Chettan 2,{int(sub_size*1.6)},&H0000E1FF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,40,40,40,1
Style: Label,Baloo Chettan 2,{int(sub_size*0.8)},&H00FFFFFF,&H00FFFFFF,&H00202020,&H64000000,-1,0,0,0,100,100,0,0,1,4,0,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ass_write(path, W, H, tl, extra, sub_size=60, sub_margin=42):
    lines = [ass_header(W, H, sub_size, sub_margin)]
    for b in tl.beats:
        if b.get('en'):
            lines.append(f"Dialogue: 0,{ts(b['t0'])},{ts(b['t1']+0.25)},Sub,,0,0,0,,{b['en']}")
    for (t0, t1, style, x, y, text, extra_tag) in extra:
        lines.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},{style},,0,0,0,,{{\\pos({x},{y})\\fad(150,150){extra_tag}}}{text}")
    open(path, 'w').write('\n'.join(lines)+'\n')

# ---------------- extra SFX
def sfx2(kind):
    rng = np.random.default_rng(5)
    if kind == 'wrong':
        n = int(0.45*SR); t = np.arange(n)/SR
        y = (np.sign(np.sin(2*np.pi*140*t))*0.5 + np.sin(2*np.pi*95*t)*0.5) * np.exp(-t*3)
        return A.lp(y, 1800)*0.5
    if kind == 'right':
        out = np.zeros(int(0.7*SR))
        for i, f in enumerate((784, 988, 1319)):
            A.add(out, A.bell(f, 0.5, 4)*0.35, int(i*0.09*SR))
        return out
    if kind == 'snap':
        n = int(0.25*SR); t = np.arange(n)/SR
        return A.hp(rng.standard_normal(n), 1500)*np.exp(-t*30)*0.9
    if kind == 'thud':
        n = int(0.6*SR); t = np.arange(n)/SR
        return (np.sin(2*np.pi*60*t*(1-0.4*t)) + 0.4*A.lp(rng.standard_normal(n), 300))*np.exp(-t*7)*0.9
    if kind == 'tick':
        out = np.zeros(int(2.0*SR))
        for i in range(4):
            n = int(0.04*SR); t = np.arange(n)/SR
            A.add(out, np.sin(2*np.pi*(1800 if i % 2 == 0 else 1400)*t)*np.exp(-t*90)*0.4, int(i*0.5*SR))
        return out
    if kind == 'creak':
        n = int(0.8*SR); t = np.arange(n)/SR
        f = 220 + 80*np.sin(2*np.pi*3*t)
        return np.sin(2*np.pi*np.cumsum(f)/SR) * (0.5+0.5*np.sin(2*np.pi*31*t)) * np.exp(-t*2) * 0.25
    if kind == 'whoosh':
        n = int(0.5*SR); t = np.arange(n)/SR
        return A.bp(rng.standard_normal(n), 400, 3000)*np.sin(np.pi*t/0.5)*0.35
    if kind == 'pop': return A.sfx('pop')
    if kind == 'splash':
        n = int(0.9*SR); t = np.arange(n)/SR
        return A.bp(rng.standard_normal(n), 300, 5000)*np.exp(-t*5)*0.6
    if kind == 'cheer':
        return A.sfx('chime')
    if kind == 'rumble':
        n = int(1.2*SR); t = np.arange(n)/SR
        return A.lp(rng.standard_normal(n), 160)*np.minimum(1, t*4)*np.exp(-t*2)*1.2
    if kind == 'grunt':
        n = int(0.35*SR); t = np.arange(n)/SR
        return A.bp(rng.standard_normal(n), 200, 900)*np.sin(np.pi*t/0.35)*0.25
    return np.zeros(10)

def build_audio(path, tl, sfx_events, music_plan, total):
    """music_plan: list of (t0, t1, mood). sfx_events: list of (t, kind, gain)."""
    n = int((total+1)*SR)
    voice_buf = np.zeros(n); mus = np.zeros(n); fx = np.zeros(n)
    for b in tl.beats:
        if b['wav']:
            y, sr = sf.read(b['wav']); y = y if y.ndim == 1 else y.mean(1)
            A.add(voice_buf, y, int(b['t0']*SR))
        if b.get('think'):
            A.add(fx, sfx2('tick'), int(b['think_t']*SR))
            if getattr(tl, 'think', 2.2) > 2.6: A.add(fx, sfx2('tick'), int((b['think_t']+2.0)*SR))
    for (t0, t1, mood) in music_plan:
        m = A.music(mood, t1-t0+1)
        m = m if m.ndim == 1 else m.mean(1)
        m = m[:int((t1-t0)*SR)]
        fade = np.ones(len(m)); k = int(0.5*SR)
        if len(m) > 2*k: fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
        A.add(mus, m*fade/ (np.abs(m).max()+1e-9), int(t0*SR))
    for (t, kind, g) in sfx_events:
        A.add(fx, sfx2(kind)*g, int(t*SR))
    env = np.abs(voice_buf); win = int(0.25*SR)
    env = np.convolve(env, np.ones(win)/win, mode='same')
    duck = 1 - 0.65*np.clip(env/0.05, 0, 1)
    mix = voice_buf*1.0 + mus*0.16*duck + fx*0.7
    mix = mix[:int(total*SR)]
    tmp = path + '.tmp.wav'; sf.write(tmp, mix.astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '44100', path], check=True)
    os.remove(tmp)

# ---------------- render
def render(out, W, H, total, draw, ass, audio, fps=30, vbit=None, crf=20, stills=None):
    if stills:
        for i, t in enumerate(stills):
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, t)
            surf.write_to_png(f'{out}.still{i:02d}.png')
        return
    vf = f"ass={ass}:fontsdir={FONTS}"
    enc = ['-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p']
    enc += (['-b:v', vbit, '-maxrate', '1600k', '-bufsize', '3200k'] if vbit else ['-crf', str(crf)])
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
           '-i', audio, '-vf', vf, *enc, '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    N = int(total*fps)
    for i in range(N):
        t = i/fps
        ctx.save(); draw(ctx, t); ctx.restore(); surf.flush()
        p.stdin.write(surf.get_data())
        if i % 300 == 0: print('frame', i, '/', N, flush=True)
    p.stdin.close(); p.wait()
