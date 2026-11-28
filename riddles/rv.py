"""Hard Malayalam Riddles #1 renderer (16:9 long video, 1920x1080). Hosts: Detective Arjun + Meenu (detective/chars.py).
Riddles: coconut profit (30), clock 3:15 (7.5 deg), boat crossing (7 trips), heavy laddoo jar (jar 4), trains + parrot (120 km), fake coin (2 weighings).
python3 rv.py stills | audio | video <part> <nparts> | final <nparts>"""
import sys, os, math, json, random, subprocess
import numpy as np, soundfile as sf, cairo
sys.path.insert(0, '/home/claude/detective'); sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/ml'); sys.path.insert(0, '/home/claude'); sys.path.insert(0, '/home/claude/riddles')
from chars import human, geo, ARJUN, MEENU, RAJU, KUTTAN, AMMINI, JOSE, hexc, mix, lt, dk, shade, vshade, ellipse, rrect, outline
import rbgs
from rbgs import coconut, CLOCK, TRACK_Y, SHELF_Y, W, H
from bgs import lin, rad, glow
from wd import text, text_w
from pz import voice, wav_dur, clamp, prog, sprog, back, lerp, sfx2
import audio as A
from script import B, SPK, SECTIONS
SR = 44100
OUT = '/home/claude/riddles/out'; os.makedirs(OUT, exist_ok=True)
NAME = 'KP_Hard_Malayalam_Riddles_1_YouTube'

# ------------------------------------------------------------------ timeline
def build_tl():
    t = 0.6
    for i, b in enumerate(B):
        b['wav'] = voice(b['ml'], SPK[b['spk']]); b['d'] = wav_dur(b['wav'])
        if b.get('timer'): t += 0.35
        b['t0'] = t; b['t1'] = t + b['d']
        t = b['t1'] + b.get('timer', 0) + b.get('post', 0) + (0.6 if (b.get('timer') or b.get('ans')) else 0.18)
        if b.get('timer'): b['tt0'] = b['t1'] + 0.25; b['tt1'] = b['tt0'] + b['timer'] - 0.25
        y, sr = sf.read(b['wav']); y = y if y.ndim == 1 else y.mean(1)
        hop = sr//30; env = np.array([np.sqrt(np.mean(y[k:k+hop]**2)) for k in range(0, len(y), hop)])
        b['env'] = env/(env.max() + 1e-6)
    for i, b in enumerate(B): b['end'] = B[i+1]['t0'] if i + 1 < len(B) else t + 0.5
    return t + 0.5

TOTAL = build_tl()
SEC_START = {}
for b in B: SEC_START.setdefault(b['sec'], b['t0'])
SEC_START['intro'] = 0.0

def talk_of(b, who, t):
    if b['spk'] != who or not (b['t0'] <= t <= b['t1']): return 0.0
    k = int((t - b['t0'])*30)
    return float(clamp(b['env'][min(k, len(b['env'])-1)]*1.4)) if len(b['env']) else 0.0

def cam(ctx, cx, cy, z):
    z = max(1.0, z); hw, hh_ = W/(2*z), H/(2*z)
    cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh_), H - hh_)
    ctx.translate(W/2, H/2); ctx.scale(z, z); ctx.translate(-cx, -cy)

def kb(c0, p, drift=(0.0, 0.0, 0.045)):
    cx, cy, z = c0; return (cx + drift[0]*p, cy + drift[1]*p, z*(1 + drift[2]*p))

def face_cam(spec, x, y, s, z=2.6):
    g = geo(spec); return (x, y + g['hc']*s + 60*s*(2.6/z), z)

def paint_clip(ctx, name, y0):
    ctx.save(); ctx.rectangle(0, y0, W, H - y0); ctx.clip(); rbgs.paint(ctx, name); ctx.restore()

# ------------------------------------------------------------------ small widgets
def ftext(ctx, s, x, y, size, col='#ffffff', alpha=1.0, outline_=True, align='c'):
    ctx.select_font_face('Poppins ExtraBold', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
    xb, yb, w, h, xa, ya = ctx.text_extents(s)
    x0 = x - (w/2 + xb) if align == 'c' else (x - xb if align == 'l' else x - w - xb)
    ctx.move_to(x0, y); ctx.text_path(s)
    if outline_:
        ctx.set_source_rgba(0.03, 0.03, 0.08, 0.85*alpha); ctx.set_line_width(size*0.14); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*hexc(col, alpha)); ctx.fill()
    return w

def tagb(ctx, x, y, s, p=1.0, col='#ffd23f', bg='#0a0c22', size=40):
    if p <= 0: return
    w = text_w(ctx, s, size) + 50
    ctx.save(); ctx.translate(x, y); sc = back(min(1, p)); ctx.scale(sc, sc)
    rrect(ctx, -w/2 + 4, -size*0.8 + 6, w, size*1.6, 14); ctx.set_source_rgba(0, 0, 0, 0.35); ctx.fill()
    rrect(ctx, -w/2, -size*0.8, w, size*1.6, 14); ctx.set_source_rgba(*hexc(bg, 0.92)); ctx.fill()
    ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(4); rrect(ctx, -w/2, -size*0.8, w, size*1.6, 14); ctx.stroke()
    text(ctx, s, 0, size*0.36, size, col); ctx.restore()

def green_box(ctx, x, y, s, p, size=64):
    if p <= 0: return
    w = text_w(ctx, s, size) + 80
    ctx.save(); ctx.translate(x, y); sc = back(min(1, p)); ctx.scale(sc, sc)
    rrect(ctx, -w/2, -size*0.85, w, size*1.7, 18); ctx.set_source_rgba(0.04, 0.24, 0.12, 0.95); ctx.fill()
    ctx.set_source_rgba(*hexc('#2ad06a')); ctx.set_line_width(8); rrect(ctx, -w/2, -size*0.85, w, size*1.7, 18); ctx.stroke()
    text(ctx, s, 0, size*0.36, size, '#ffffff'); ctx.restore()

def xmark(ctx, x, y, r, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(back(min(1, p)), back(min(1, p)))
    ctx.arc(0, 0, r, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#e2362c')); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(r*0.25); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(-r*0.4, -r*0.4); ctx.line_to(r*0.4, r*0.4); ctx.move_to(r*0.4, -r*0.4); ctx.line_to(-r*0.4, r*0.4); ctx.stroke(); ctx.restore()

def checkm(ctx, x, y, r, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(back(min(1, p)), back(min(1, p)))
    ctx.arc(0, 0, r, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#2fc76a')); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(r*0.24); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(-r*0.45, 0); ctx.line_to(-r*0.12, r*0.35); ctx.line_to(r*0.5, -r*0.35); ctx.stroke(); ctx.restore()

def marker(ctx, x, y, n, p=1.0):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(back(min(1, p)), back(min(1, p)))
    ctx.arc(0, 0, 34, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#2a6ae8')); ctx.fill()
    ctx.arc(0, 0, 34, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(5); ctx.stroke()
    text(ctx, str(n), 0, 14, 38, '#ffffff'); ctx.restore()

def measure(ctx, x0, x1, y, label, p=1.0, col='#ffffff'):
    if p <= 0: return
    xm = lerp(x0, x1, 0.5); half = (x1 - x0)/2*p
    ctx.set_source_rgba(*hexc(col, p)); ctx.set_line_width(5)
    ctx.move_to(xm - half, y); ctx.line_to(xm + half, y); ctx.stroke()
    for sx, d in ((xm - half, 1), (xm + half, -1)):
        ctx.move_to(sx + d*24, y - 16); ctx.line_to(sx, y); ctx.line_to(sx + d*24, y + 16); ctx.stroke()
    w = text_w(ctx, label, 40) + 30
    rrect(ctx, xm - w/2, y - 30, w, 60, 12); ctx.set_source_rgba(0.05, 0.05, 0.12, 0.9*p); ctx.fill()
    text(ctx, label, xm, y + 14, 40, col, alpha=p)

# ------------------------------------------------------------------ props
def clock_face(ctx, x, y, r, hh, mm, arc=0.0, labels=True):
    ctx.arc(x, y, r*1.12, 0, 2*math.pi); ctx.set_source(lin(ctx, x - r, y - r, x + r, y + r, [(0, '#f0d070'), (1, '#9a6a1a')])); ctx.fill()
    ctx.arc(x, y, r, 0, 2*math.pi); ctx.set_source(rad(x - r*0.3, y - r*0.3, r*0.1, r*1.2, [(0, (1, 1, 0.97, 1)), (1, (0.85, 0.82, 0.74, 1))])); ctx.fill()
    for k in range(60):
        a = k*math.pi/30; L = 0.12 if k % 5 == 0 else 0.05
        ctx.move_to(x + math.sin(a)*r*0.92, y - math.cos(a)*r*0.92); ctx.line_to(x + math.sin(a)*r*(0.92 - L), y - math.cos(a)*r*(0.92 - L))
        ctx.set_source_rgba(0.15, 0.12, 0.1, 1); ctx.set_line_width(r*(0.025 if k % 5 == 0 else 0.01)); ctx.stroke()
    if labels:
        for k in range(1, 13):
            a = k*math.pi/6; text(ctx, str(k), x + math.sin(a)*r*0.68, y - math.cos(a)*r*0.68 + r*0.07, r*0.2, '#2a1a12')
    ha = (hh % 12 + mm/60)*math.pi/6; ma = mm*math.pi/30
    if arc > 0:
        ctx.move_to(x, y); ctx.arc(x, y, r*0.55, ma - math.pi/2, ma - math.pi/2 + (ha - ma)*arc); ctx.close_path()
        ctx.set_source_rgba(1, 0.3, 0.2, 0.55); ctx.fill()
    for a, L, wdt, col in ((ha, 0.5, 0.07, '#1a1a2a'), (ma, 0.8, 0.045, '#2a2a3a')):
        ctx.move_to(x - math.sin(a)*r*0.1, y + math.cos(a)*r*0.1); ctx.line_to(x + math.sin(a)*r*L, y - math.cos(a)*r*L)
        ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(r*wdt); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.arc(x, y, r*0.06, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#c8302a')); ctx.fill()
    ctx.arc(x - r*0.3, y - r*0.35, r*0.5, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, 0.08); ctx.fill()

def boat(ctx, x, y, s, flip=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s*flip, s)
    ctx.move_to(-260, -40); ctx.curve_to(-180, 40, 180, 40, 260, -40); ctx.curve_to(200, -10, -200, -10, -260, -40); ctx.close_path()
    ctx.move_to(-300, -70); ctx.curve_to(-250, 30, 250, 30, 300, -70); ctx.line_to(260, -40); ctx.curve_to(180, 40, -180, 40, -260, -40); ctx.close_path()
    ctx.set_source(lin(ctx, 0, -70, 0, 40, [(0, '#8a5a2a'), (1, '#3a200c')])); ctx.fill()
    for k in range(3):
        ctx.move_to(-280 + k*6, -55 + k*16); ctx.curve_to(-200, 20 + k*6, 200, 20 + k*6, 280 - k*6, -55 + k*16); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    # water ripple
    ctx.save(); ctx.translate(x, y + 10*s); ctx.scale(1, 0.15); ctx.arc(0, 0, 300*s, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(1, 1, 1, 0.12); ctx.fill()

def dog(ctx, x, y, s, face=1, t=0.0, angry=False):
    ctx.save(); ctx.translate(x, y); ctx.scale(s*face, s)
    col = '#a8682a'
    for lx in (-50, -25, 30, 55):
        ctx.rectangle(lx - 8, -60, 16, 60); shade(ctx, dk(col, 0.1), lx - 8, lx + 8); ctx.fill()
    ellipse(ctx, 0, -80, 85, 40); shade(ctx, col, -85, 85); ctx.fill()
    wag = math.sin(t*12)*0.4
    ctx.move_to(-80, -90); ctx.curve_to(-110, -120 - 20*wag, -120, -150, -105, -165 - 10*wag); ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ellipse(ctx, 85, -125, 42, 36); shade(ctx, col, 45, 125); ctx.fill()
    ellipse(ctx, 120, -115, 26, 18); ctx.set_source_rgba(*hexc(lt(col, 0.25))); ctx.fill()
    ctx.arc(140, -120, 7, 0, 2*math.pi); ctx.set_source_rgba(0.1, 0.05, 0.05, 1); ctx.fill()
    ctx.arc(92, -135, 6, 0, 2*math.pi); ctx.set_source_rgba(0.1, 0.05, 0.05, 1); ctx.fill()
    ctx.move_to(60, -150); ctx.curve_to(40, -170, 45, -120, 60, -110); ctx.set_source_rgba(*hexc(dk(col, 0.35))); ctx.fill()
    if angry:
        ctx.move_to(110, -102); ctx.line_to(140, -100); ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(4); ctx.stroke()
        ctx.move_to(82, -146); ctx.line_to(102, -140); ctx.set_source_rgba(0.1, 0.05, 0.05, 1); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

def hen(ctx, x, y, s, face=1, t=0.0, peck=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s*face, s)
    for lx in (-12, 12): ctx.move_to(lx, -40); ctx.line_to(lx, 0); ctx.set_source_rgba(*hexc('#e8a02a')); ctx.set_line_width(6); ctx.stroke()
    ellipse(ctx, 0, -75, 55, 42); shade(ctx, '#f4ece0', -55, 55, 0.1, 0.25); ctx.fill()
    ctx.move_to(-50, -90); ctx.curve_to(-80, -130, -70, -140, -40, -110); ctx.set_source_rgba(*hexc('#c8b8a8')); ctx.fill()
    ellipse(ctx, -5, -75, 30, 20); ctx.set_source_rgba(0.85, 0.78, 0.7, 1); ctx.fill()
    ctx.save(); ctx.translate(40, -110); ctx.rotate(peck*0.8)
    ctx.arc(0, 0, 24, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#f4ece0')); ctx.fill()
    for k in range(3): ctx.arc(-6 + k*9, -24, 8, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#e2362c')); ctx.fill()
    ctx.move_to(20, -4); ctx.line_to(40, 2); ctx.line_to(20, 8); ctx.close_path(); ctx.set_source_rgba(*hexc('#f0a020')); ctx.fill()
    ellipse(ctx, 14, 14, 6, 9); ctx.set_source_rgba(*hexc('#e2362c')); ctx.fill()
    ctx.arc(8, -4, 4, 0, 2*math.pi); ctx.set_source_rgba(0, 0, 0, 1); ctx.fill()
    ctx.restore(); ctx.restore()

def sack(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-60, 0); ctx.curve_to(-75, -60, -60, -120, -40, -140); ctx.line_to(40, -140); ctx.curve_to(60, -120, 75, -60, 60, 0); ctx.close_path()
    shade(ctx, '#d8c08a', -70, 70); ctx.fill_preserve(); outline(ctx, 2, 0.4)
    ctx.move_to(-40, -140); ctx.curve_to(-30, -165, 30, -165, 40, -140); ctx.set_source_rgba(*hexc('#c8a870')); ctx.fill()
    ctx.move_to(-38, -142); ctx.line_to(38, -142); ctx.set_source_rgba(*hexc('#8a6a3a')); ctx.set_line_width(6); ctx.stroke()
    text(ctx, 'RICE', 0, -50, 30, '#7a3a1a')
    ctx.restore()

def laddoo(ctx, x, y, r, heavy=False):
    ctx.arc(x, y, r, 0, 2*math.pi); ctx.set_source(rad(x - r*0.35, y - r*0.35, r*0.1, r*1.1, [(0, (1, 0.85, 0.4, 1)), (1, (0.85, 0.45, 0.08, 1))])); ctx.fill()
    rnd = random.Random(int(x*7 + y))
    for k in range(5):
        ctx.arc(x + rnd.uniform(-r*0.6, r*0.6), y + rnd.uniform(-r*0.6, r*0.6), r*0.1, 0, 2*math.pi); ctx.set_source_rgba(1, 0.95, 0.75, 0.8); ctx.fill()

def jar(ctx, x, y, s, n, hl=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if hl > 0: glow(ctx, 0, -110, 190, (1, 0.9, 0.3), 0.6*hl)
    for r_ in range(4):
        for c in range(4 - (r_ % 2)):
            laddoo(ctx, -54 + c*36 + (r_ % 2)*18, -30 - r_*30, 18)
    rrect(ctx, -80, -190, 160, 190, 26); ctx.set_source_rgba(0.85, 0.95, 1, 0.25); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 0.7); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(-55, -170); ctx.line_to(-55, -30); ctx.set_source_rgba(1, 1, 1, 0.4); ctx.set_line_width(8); ctx.stroke()
    rrect(ctx, -64, -222, 128, 36, 10); shade(ctx, '#c8302a', -64, 64); ctx.fill()
    ctx.arc(0, -96, 34, 0, 2*math.pi); ctx.set_source_rgba(1, 0.97, 0.9, 0.95); ctx.fill(); ctx.arc(0, -96, 34, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#c8302a')); ctx.set_line_width(4); ctx.stroke()
    text(ctx, str(n), 0, -82, 40, '#8a1a1a')
    ctx.restore()

def dscale(ctx, x, y, s, reading='', blink=False):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -150, -70, 300, 70, 14); shade(ctx, '#d8d8e0', -150, 150, 0.2, 0.3); ctx.fill_preserve(); outline(ctx, 2, 0.4)
    ellipse(ctx, 0, -78, 140, 18); ctx.set_source(lin(ctx, -140, 0, 140, 0, [(0, '#f4f4f8'), (1, '#a8a8b8')])); ctx.fill()
    rrect(ctx, -90, -50, 180, 40, 6); ctx.set_source_rgba(*hexc('#1a2a1a')); ctx.fill()
    if reading: text(ctx, reading, 0, -18, 30, '#7aff8a')
    ctx.restore()

def train(ctx, x, y, s, face=1, col='#2a5ab8', t=0.0):
    """x = nose position, y = rail top; train extends behind the nose."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s*face, s)
    for k in range(3):  # 2 coaches + engine (k=0 engine at nose)
        x1 = -k*250; x0 = x1 - 240
        if k == 0:
            ctx.move_to(x0, -150); ctx.line_to(x1 - 50, -150); ctx.curve_to(x1 - 5, -150, x1, -110, x1, -60); ctx.line_to(x1, -22); ctx.line_to(x0, -22); ctx.close_path()
        else:
            rrect(ctx, x0, -150, 240, 128, 14)
        ctx.set_source(lin(ctx, 0, -150, 0, -22, [(0, lt(col, 0.15)), (1, dk(col, 0.3))])); ctx.fill()
        ctx.rectangle(x0, -70, 240 if k else 230, 14); ctx.set_source_rgba(*hexc('#f4e8c8')); ctx.fill()
        for j in range(4 if k else 2):
            wx = x0 + 18 + j*56; rrect(ctx, wx, -130, 40, 40, 6); ctx.set_source_rgba(*hexc('#cfe8ff')); ctx.fill()
        if k == 0:
            rrect(ctx, x1 - 60, -135, 46, 50, 8); ctx.set_source_rgba(*hexc('#cfe8ff')); ctx.fill()
            ctx.arc(x1 - 14, -40, 9, 0, 2*math.pi); ctx.set_source_rgba(1, 0.95, 0.6, 1); ctx.fill()
        for wx in (x0 + 40, x0 + 200):
            ctx.arc(wx, -18, 18, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#222228')); ctx.fill()
            ctx.arc(wx, -18, 7, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#8a8a90')); ctx.fill()
        if k: ctx.rectangle(x1 - 2, -90, 12, 30); ctx.set_source_rgba(0.1, 0.1, 0.1, 1); ctx.fill()
    ctx.restore()

def parrot(ctx, x, y, s, face=1, t=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s*face, s)
    fl = math.sin(t*18)
    ctx.move_to(-10, 0); ctx.curve_to(-60, -10 - 60*fl, -110, -20 - 70*fl, -130, -10 - 80*fl); ctx.curve_to(-80, 10, -40, 12, -10, 10); ctx.close_path()
    ctx.set_source_rgba(*hexc('#1f8a3a')); ctx.fill()
    ctx.move_to(-40, 6); ctx.curve_to(-90, 14, -130, 30, -170, 44); ctx.curve_to(-120, 18, -80, 18, -40, 16); ctx.close_path(); ctx.set_source_rgba(*hexc('#2a9a4a')); ctx.fill()
    ellipse(ctx, 0, 0, 52, 26); shade(ctx, '#3ac85a', -50, 50); ctx.fill()
    ctx.arc(48, -10, 22, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#3ac85a')); ctx.fill()
    ctx.move_to(64, -14); ctx.curve_to(90, -12, 88, 8, 70, 6); ctx.close_path(); ctx.set_source_rgba(*hexc('#e2362c')); ctx.fill()
    ctx.arc(54, -16, 5, 0, 2*math.pi); ctx.set_source_rgba(0, 0, 0, 1); ctx.fill()
    ctx.move_to(30, 4); ctx.curve_to(40, 14, 56, 12, 62, 4); ctx.set_source_rgba(0, 0, 0, 0.6); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

def coin(ctx, x, y, r, glint=0.0, fake=False, lab=None):
    ctx.arc(x, y + r*0.12, r, 0, 2*math.pi); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    ctx.arc(x, y, r, 0, 2*math.pi); ctx.set_source(rad(x - r*0.4, y - r*0.4, r*0.1, r*1.1, [(0, (1, 0.95, 0.6, 1)), (0.6, (0.92, 0.7, 0.2, 1)), (1, (0.6, 0.4, 0.08, 1))])); ctx.fill()
    ctx.arc(x, y, r*0.78, 0, 2*math.pi); ctx.set_source_rgba(0.6, 0.4, 0.08, 0.6); ctx.set_line_width(max(1, r*0.06)); ctx.stroke()
    ctx.move_to(x - r*0.3, y + r*0.2); ctx.line_to(x, y - r*0.35); ctx.line_to(x + r*0.3, y + r*0.2); ctx.set_source_rgba(0.6, 0.4, 0.08, 0.7); ctx.set_line_width(max(1, r*0.08)); ctx.stroke()
    if glint > 0:
        a = 0.5 + 0.5*math.sin(glint)
        ctx.save(); ctx.translate(x + r*0.4, y - r*0.4)
        for k in range(4):
            ctx.rotate(math.pi/4); ctx.move_to(0, -r*0.5*a); ctx.line_to(r*0.06, 0); ctx.line_to(0, r*0.5*a); ctx.line_to(-r*0.06, 0); ctx.close_path()
        ctx.set_source_rgba(1, 1, 0.9, 0.9*a); ctx.fill(); ctx.restore()
    if lab: text(ctx, lab, x, y + r*0.2, r*0.7, '#5a3a08')

def balance(ctx, x, y, s, tilt=0.0, left=0, right=0, labs=None):
    """brass balance; tilt>0: left pan goes UP (left lighter). left/right = number of coins on each pan."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -110, -24, 220, 24, 8); shade(ctx, '#b8862a', -110, 110); ctx.fill()
    ctx.rectangle(-12, -330, 24, 310); shade(ctx, '#d8a83a', -12, 12); ctx.fill()
    ctx.arc(0, -340, 22, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#f0c84a')); ctx.fill()
    a = 0.22*tilt
    ctx.save(); ctx.translate(0, -340); ctx.rotate(a)
    rrect(ctx, -260, -9, 520, 18, 8); shade(ctx, '#e0b040', -260, 260); ctx.fill()
    ends = [(-250, 0), (250, 0)]
    ctx.restore()
    for k, (ex, ey) in enumerate(ends):
        px = ex*math.cos(a) - ey*math.sin(a); py = -340 + ex*math.sin(a) + ey*math.cos(a)
        for dx in (-70, 70): ctx.move_to(px, py); ctx.line_to(px + dx, py + 170); ctx.set_source_rgba(0.6, 0.45, 0.15, 1); ctx.set_line_width(3); ctx.stroke()
        ellipse(ctx, px, py + 175, 95, 20); ctx.set_source(lin(ctx, px - 95, 0, px + 95, 0, [(0, '#f0c84a'), (1, '#8a6018')])); ctx.fill()
        n = left if k == 0 else right
        for j in range(n):
            cx_ = px - (min(n, 4) - 1)*18 + (j % 4)*36; cy_ = py + 160 - (j // 4)*22
            coin(ctx, cx_, cy_, 20)
        if labs: text(ctx, labs[k], px, py + 250, 44, '#ffd23f')
    ctx.restore()

# ------------------------------------------------------------------ worlds
def poses_for(b, who):
    sp = b['spk']; eat = b.get('meenu_eat')
    if who == 'A': return dict(arm_l='chin' if sp != 'A' else 'hip', arm_r='down' if sp != 'A' else 'point', expr='think' if sp != 'A' else 'smile')
    if who == 'M': return dict(arm_l='chips', arm_r='eat' if eat else 'down', expr='laugh' if (sp == 'M' and eat) else ('smile' if sp == 'M' else 'neutral'))
    return dict(expr='smile' if sp == who else 'neutral', arm_r='point' if sp == who else 'down', arm_l='hip')

ST = dict(A=(700, 1040, 0.74), M=(1230, 1040, 0.74))
def studio_world(ctx, t, b):
    rbgs.paint(ctx, 'studio')
    ftext(ctx, 'RIDDLE TIME', 980, 255, 64, '#f6f2e0', outline_=False)
    ftext(ctx, '6 HARD RIDDLES', 980, 345, 48, '#ffd23f', outline_=False)
    for k, (x, y, s) in ST.items():
        po = poses_for(b, k); po['face'] = 1 if k == 'A' else -1; po['talk'] = talk_of(b, k, t)
        human(ctx, x, y, s, ARJUN if k == 'A' else MEENU, po, t)

def market_world(ctx, t, b, signs=True):
    rbgs.paint(ctx, 'market')
    if signs:
        for x, lab, col in ((470, 'BUY 3 = ₹100', '#2a6ae8'), (820, 'SELL 2 = ₹100', '#2a9a4a')):
            sw_ = 0.03*math.sin(t*2 + x)
            ctx.save(); ctx.translate(x, 528); ctx.rotate(sw_)
            ctx.move_to(-60, 0); ctx.line_to(-60, 40); ctx.move_to(60, 0); ctx.line_to(60, 40); ctx.set_source_rgba(0.3, 0.2, 0.1, 1); ctx.set_line_width(3); ctx.stroke()
            rrect(ctx, -140, 40, 280, 80, 10); ctx.set_source_rgba(*hexc('#fff6dc')); ctx.fill(); ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(5); rrect(ctx, -140, 40, 280, 80, 10); ctx.stroke()
            text(ctx, lab, 0, 94, 38, col); ctx.restore()
    po = poses_for(b, 'R'); po['face'] = 1; po['talk'] = talk_of(b, 'R', t)
    human(ctx, 1170, 1050, 0.66, RAJU, po, t)
    if b['spk'] == 'M' or 'mk_two' in b['shots']:
        pm = poses_for(b, 'M'); pm['face'] = -1; pm['talk'] = talk_of(b, 'M', t)
        human(ctx, 1720, 1060, 0.6, MEENU, pm, t)

CH = dict(A=(1330, 1060, 0.46), M=(1480, 1062, 0.46))
def church_world(ctx, t, b, hh=3, mm=15):
    rbgs.paint(ctx, 'church')
    cx, cy, r = CLOCK; clock_face(ctx, cx, cy, r, hh, mm)
    for k, (x, y, s) in CH.items():
        po = poses_for(b, k); po['face'] = 1 if k == 'A' else -1; po['talk'] = talk_of(b, k, t)
        if k == 'M' and b['spk'] == 'M': po['arm_r'] = 'point'; po['face'] = -1
        human(ctx, x, y, s, ARJUN if k == 'A' else MEENU, po, t)

def river_world(ctx, t, b, mode='start'):
    rbgs.paint(ctx, 'river')
    bob = 6*math.sin(t*2)
    boat(ctx, 760, 930 + bob, 0.9)
    pk = poses_for(b, 'K'); pk['face'] = -1; pk['talk'] = talk_of(b, 'K', t); pk['arm_r'] = 'hip' if b['spk'] != 'K' else 'point'
    human(ctx, 800, 905 + bob, 0.5, KUTTAN, pk, t)
    ctx.move_to(950, 650 + bob); ctx.line_to(1010, 990 + bob); ctx.set_source_rgba(*hexc('#6a4a2a')); ctx.set_line_width(10); ctx.stroke()  # pole
    danger = mode in ('danger1', 'danger2')
    dog(ctx, 120, 1010, 0.62, 1, t, angry=mode == 'danger1')
    hen(ctx, 290, 990, 0.72, -1 if mode != 'danger2' else 1, t, peck=abs(math.sin(t*8)) if mode == 'danger2' else 0)
    sack(ctx, 430, 1010, 0.85)
    if mode == 'danger1':
        tagb(ctx, 210, 780, 'DOG + HEN', 1, '#ff6a5a', size=34); xmark(ctx, 210, 690, 40, 1)
    if mode == 'danger2':
        tagb(ctx, 360, 780, 'HEN + RICE', 1, '#ff6a5a', size=34); xmark(ctx, 360, 690, 40, 1)
    if mode == 'safe':
        tagb(ctx, 280, 780, 'DOG + RICE', 1, '#3fe08a', size=34); checkm(ctx, 280, 690, 40, 1)

JX = [560, 780, 1000, 1220, 1440]
def bakery_world(ctx, t, b, hl=None, reading=''):
    rbgs.paint(ctx, 'bakery')
    for k, x in enumerate(JX): jar(ctx, x, SHELF_Y, 0.95, k + 1, hl=1.0 if hl == k + 1 else 0)
    pa = poses_for(b, 'AM'); pa['face'] = -1; pa['talk'] = talk_of(b, 'AM', t)
    if b['spk'] == 'AM': pa['expr'] = 'shock'; pa['arm_r'] = 'up'
    human(ctx, 1600, 1150, 0.95, AMMINI, pa, t)
    pm = poses_for(b, 'M'); pm['face'] = 1; pm['talk'] = talk_of(b, 'M', t)
    human(ctx, 330, 1150, 0.95, MEENU, pm, t)
    paint_clip(ctx, 'bakery', 770)
    dscale(ctx, 960, 790, 1.0, reading)

def rail_world(ctx, t, b, lt_, mode='start'):
    rbgs.paint(ctx, 'rail')
    if mode == 'start': xa, xb = 520, 1400
    else:
        p = clamp(lt_/6.0); xa, xb = lerp(520, 760, p), lerp(1400, 1160, p)
    train(ctx, xa, TRACK_Y[0] + 2, 0.55, 1, '#2a5ab8', t)
    train(ctx, xb, TRACK_Y[1] + 2, 0.55, -1, '#c8382a', t)
    if mode in ('parrot', 'zigzag'):
        if mode == 'zigzag':
            pts = []; x_ = xa + 10; d = 1; y_ = 560
            for k in range(7): pts.append((x_, y_ + 20*(k % 2))); x_ = xb - 10 if d > 0 else xa + 10 + k*25; d = -d
            ctx.set_dash([18, 14]); ctx.set_source_rgba(1, 1, 1, 0.85); ctx.set_line_width(5)
            ctx.move_to(*pts[0])
            for pp in pts[1:]: ctx.line_to(*pp)
            ctx.stroke(); ctx.set_dash([])
            ph = (lt_*0.5) % 2; px = lerp(xa + 10, xb - 10, ph if ph < 1 else 2 - ph); fc = 1 if ph < 1 else -1
        else:
            px = lerp(xa + 20, xa + 380, clamp(lt_/4.0)); fc = 1
        parrot(ctx, px, 560 - 20*math.sin(t*3), 0.75, fc, t)

def jewel_world(ctx, t, b, coins=True, scale_=True, tilt=0.0):
    rbgs.paint(ctx, 'jewel')
    pj = poses_for(b, 'J'); pj['face'] = -1; pj['talk'] = talk_of(b, 'J', t)
    human(ctx, 1420, 1120, 0.72, JOSE, pj, t)
    paint_clip(ctx, 'jewel', 762)
    if scale_: balance(ctx, 560, 770, 0.75, tilt)
    if coins:
        for k in range(9): coin(ctx, 930 + (k % 5)*62 + (k // 5)*31, 760 - (k // 5)*30 + 8, 26, glint=t*2 + k)
    pa = poses_for(b, 'A'); pa['face'] = 1; pa['talk'] = talk_of(b, 'A', t)
    human(ctx, 230, 1090, 0.74, ARJUN, pa, t)

# ------------------------------------------------------------------ screen-space cards
def card(ctx, name='card'): rbgs.paint(ctx, name)

def title_card(ctx, t, lt_):
    rbgs.paint(ctx, 'studio'); ctx.set_source_rgba(0.02, 0.02, 0.06, 0.55); ctx.paint()
    human(ctx, 380, 1080, 0.85, ARJUN, dict(face=1, arm_l='chin', expr='smug'), t)
    human(ctx, 1560, 1080, 0.85, MEENU, dict(face=-1, arm_l='chips', arm_r='eat', expr='smile'), t)
    s = 1 + 0.03*sprog(lt_, 0, 4)
    ctx.save(); ctx.translate(W/2, 380); ctx.scale(s, s)
    ftext(ctx, 'HARD RIDDLES', 0, 0, 130, '#ffffff', alpha=prog(lt_, 0.1, 0.3))
    ftext(ctx, '#1', 0, 170, 170, '#ffd23f', alpha=prog(lt_, 0.4, 0.3)); ctx.restore()
    tagb(ctx, W/2, 760, 'ONLY 6% SOLVE ALL 6', prog(lt_, 1.0, 0.4), '#1a1a1a', bg='#ffd23f', size=54)

def q_overlay(ctx, lines, lt_):
    for k, (s, col) in enumerate(lines):
        tagb(ctx, W/2, 330 + k*105, s, prog(lt_, 0.3 + 0.35*k, 0.3), col, size=48)

def a1(ctx, t, lt_, step, which):
    card(ctx, 'card_blue')
    if which == 'a':
        ftext(ctx, 'TAKE 6 COCONUTS', W/2, 170, 70, '#ffd23f')
        for k in range(6): coconut(ctx, 560 + k*160, 360, 58, 0.3*k)
        tagb(ctx, W/2, 560, 'BUY 3 = ₹100, SO 6 = ₹200', prog(lt_, 0.5, 0.3), '#ffffff', size=56)
        if step: tagb(ctx, W/2, 720, 'COST = ₹200', prog(lt_, 0.4, 0.3), '#ff8a6a', size=64)
    elif which == 'b':
        ftext(ctx, 'SELL THE 6 COCONUTS', W/2, 170, 70, '#ffd23f')
        for k in range(6): coconut(ctx, 560 + k*160, 340, 58, 0.3*k)
        tagb(ctx, W/2, 520, 'SELL 2 = ₹100, SO 6 = ₹300', prog(lt_, 0.4, 0.3), '#ffffff', size=56)
        tagb(ctx, W/2, 680, '₹300 - ₹200 = ₹100 PROFIT', prog(lt_, 2.5, 0.3), '#3fe08a', size=60)
    else:
        ftext(ctx, 'PROFIT ₹100 ON EVERY 6', W/2, 170, 66, '#ffd23f')
        tagb(ctx, W/2, 360, '₹500 ÷ ₹100 = 5', prog(lt_, 0.3, 0.3), '#ffffff', size=64)
        tagb(ctx, W/2, 520, '5 × 6 = 30 COCONUTS', prog(lt_, 1.2, 0.3), '#ffffff', size=64)
        green_box(ctx, W/2, 720, 'ANS – 30', prog(lt_, 2.0, 0.35), 80)

def wrong_card(ctx, t, lt_, title, lines, good=None):
    card(ctx, 'card_red')
    ftext(ctx, 'WHY PEOPLE GET IT WRONG', W/2, 150, 60, '#ff8a7a')
    for k, s in enumerate(lines):
        tagb(ctx, W/2, 330 + k*130, s, prog(lt_, 0.4 + 0.8*k, 0.3), '#ffffff', size=50)
    xmark(ctx, W/2 + 700, 330, 50, prog(lt_, 1.0, 0.3))
    if good: tagb(ctx, W/2, 330 + len(lines)*130 + 40, good, prog(lt_, 0.4 + 0.8*len(lines), 0.3), '#3fe08a', size=54)

def a2(ctx, t, lt_, step, which):
    card(ctx, 'card_blue')
    if which == 'a':
        clock_face(ctx, 700, 560, 330, 3, 15, arc=sprog(lt_, 0.6, 1.2) if step else 0)
        tagb(ctx, 1400, 380, 'MINUTE HAND: 3', prog(lt_, 0.4, 0.3), '#ffffff', size=48)
        tagb(ctx, 1400, 520, 'HOUR HAND MOVES!', prog(lt_, 1.6, 0.3), '#ff8a6a', size=48)
        if step: tagb(ctx, 1400, 680, '1/4 OF THE WAY TO 4', prog(lt_, 0.3, 0.3), '#ffd23f', size=48)
    else:
        clock_face(ctx, 520, 560, 300, 3, 15, arc=1.0)
        tagb(ctx, 1300, 330, '360° ÷ 12 = 30°', prog(lt_, 0.3, 0.3), '#ffffff', size=60)
        tagb(ctx, 1300, 480, '30° ÷ 4 = 7.5°', prog(lt_, 1.4, 0.3), '#ffffff', size=60)
        if step: green_box(ctx, 1300, 700, 'ANS – 7.5°', prog(lt_, 0.2, 0.35), 80)

TRIPS = [('hen', 1), (None, -1), ('dog', 1), ('hen', -1), ('rice', 1), (None, -1), ('hen', 1)]
def trip_state(k):
    left = {'dog', 'hen', 'rice'}; side = 0
    for i in range(k):
        it, d = TRIPS[i]
        if it: (left.discard(it) if d > 0 else left.add(it))
        side = 1 - side
    return left, side

def draw_item(ctx, it, x, y, s, t):
    if it == 'dog': dog(ctx, x - 20*s, y, 0.5*s, 1, t)
    elif it == 'hen': hen(ctx, x, y, 0.6*s, 1, t)
    else: sack(ctx, x, y, 0.65*s)

def a3_card(ctx, t, lt_, b):
    card(ctx, 'card_blue')
    ctx.rectangle(0, 700, 420, 380); ctx.set_source(lin(ctx, 0, 700, 0, H, [(0, '#4a8a3a'), (1, '#2a5a1a')])); ctx.fill()
    ctx.rectangle(1500, 700, 420, 380); ctx.set_source(lin(ctx, 0, 700, 0, H, [(0, '#4a8a3a'), (1, '#2a5a1a')])); ctx.fill()
    ctx.rectangle(420, 760, 1080, 320); ctx.set_source(lin(ctx, 0, 760, 0, H, [(0, '#3a8ab0'), (1, '#1a4a6a')])); ctx.fill()
    text(ctx, 'THIS SIDE', 210, 1050, 40, '#ffffff'); text(ctx, 'OTHER SIDE', 1710, 1050, 40, '#ffffff')
    a, z = b['trip']; n = z - a; dur = max(1, b['d'])
    seg = dur/n; k = min(n - 1, int(lt_/seg)); q = clamp((lt_ - k*seg)/(seg*0.75)); trip = a + k
    left, side = trip_state(trip)
    it, d = TRIPS[trip]
    bx = lerp(560, 1360, q if d > 0 else 1 - q)
    lx = {'dog': 110, 'hen': 230, 'rice': 340}; rx = {'dog': 1590, 'hen': 1710, 'rice': 1820}
    for nm in ('dog', 'hen', 'rice'):
        if nm == it: continue
        if nm in left: draw_item(ctx, nm, lx[nm], 880, 1, t)
        else: draw_item(ctx, nm, rx[nm], 880, 1, t)
    boat(ctx, bx, 860, 0.55)
    human(ctx, bx + 40, 845, 0.3, KUTTAN, dict(face=1 if d > 0 else -1, expr='smile'), t)
    if it: draw_item(ctx, it, bx - 60, 845, 0.8, t)
    ftext(ctx, f'TRIP {trip + 1}', W/2, 170, 90, '#ffd23f')
    lab = f'TAKE THE {it.upper()} ACROSS' if it else 'COME BACK EMPTY'
    if it == 'hen' and d < 0: lab = 'BRING THE HEN BACK!'
    tagb(ctx, W/2, 330, lab, 1, '#ffffff' if not (it == 'hen' and d < 0) else '#ff8a6a', size=54)
    for j in range(7):
        x = W/2 - 6*55 + j*110
        ctx.arc(x, 470, 34, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#2a6ae8' if j <= trip else '#2a2a4a')); ctx.fill()
        text(ctx, str(j + 1), x, 484, 36, '#ffffff')
    if b.get('ans'): green_box(ctx, W/2, 610, 'ANS – 7 TRIPS', prog(lt_, b['d']*0.5, 0.35), 64)

def a4(ctx, t, lt_, step, which):
    card(ctx, 'card_blue')
    if which == 'a':
        ftext(ctx, 'TAKE 1, 2, 3, 4, 5 LADDOOS', W/2, 150, 64, '#ffd23f')
        for k, x in enumerate((360, 660, 960, 1260, 1560)):
            jar(ctx, x, 520, 1.1, k + 1)
            n = k + 1; p = prog(lt_, 0.6 + k*1.1, 0.4)
            for j in range(n):
                laddoo(ctx, x - (n - 1)*22 + j*44, 640 + 40*(1 - p), 20) if p > 0 else None
            if p > 0: text(ctx, f'{n}', x, 730, 50, '#ffffff', alpha=p)
    elif which == 'b':
        tagb(ctx, W/2, 220, '1+2+3+4+5 = 15 LADDOOS', prog(lt_, 0.3, 0.3), '#ffffff', size=60)
        tagb(ctx, W/2, 370, '15 × 50 g = 750 g', prog(lt_, 1.6, 0.3), '#ffffff', size=60)
        dscale(ctx, 700, 830, 1.6, '790 g' if step else '')
        if step:
            tagb(ctx, 1300, 650, 'SCALE: 790 g', prog(lt_, 0.2, 0.3), '#7aff8a', size=56)
            tagb(ctx, 1300, 800, '790 - 750 = 40 g EXTRA', prog(lt_, 1.6, 0.3), '#ff8a6a', size=52)
    else:
        tagb(ctx, W/2, 200, 'EACH HEAVY LADDOO = +10 g', prog(lt_, 0.3, 0.3), '#ffffff', size=56)
        tagb(ctx, W/2, 340, '40 ÷ 10 = 4', prog(lt_, 1.4, 0.3), '#ffffff', size=64)
        for k, x in enumerate((360, 660, 960, 1260, 1560)):
            jar(ctx, x, 800, 0.95, k + 1, hl=prog(lt_, 2.6, 0.4) if k == 3 else 0)
        green_box(ctx, W/2, 960, 'ANS – JAR 4', prog(lt_, b_ans_t(lt_), 0.35), 64)

def b_ans_t(lt_): return 3.4

def a5(ctx, t, lt_, step, which):
    card(ctx, 'card_blue')
    if which == 'a':
        ctx.rectangle(150, 700, 1620, 10); ctx.set_source_rgba(0.8, 0.8, 0.85, 1); ctx.fill()
        train(ctx, 520, 700, 0.5, 1, '#2a5ab8', t); train(ctx, 1400, 700, 0.5, -1, '#c8382a', t)
        measure(ctx, 520, 1400, 820, '150 km', prog(lt_, 0.2, 0.6))
        tagb(ctx, 400, 520, '40 KM/Hr', prog(lt_, 0.5, 0.3), '#7ab8ff', size=50)
        tagb(ctx, 1520, 520, '35 KM/Hr', prog(lt_, 0.8, 0.3), '#ff8a7a', size=50)
        if step: tagb(ctx, W/2, 250, 'TOGETHER: SPEED – 75 KM/Hr', prog(lt_, 1.0, 0.3), '#ffd23f', size=60)
    else:
        tagb(ctx, W/2, 230, '150 km ÷ 75 KM/Hr = 2 HOURS', prog(lt_, 0.3, 0.3), '#ffffff', size=60)
        parrot(ctx, W/2, 480, 1.4, 1, t)
        if step:
            tagb(ctx, W/2, 680, 'PARROT: 60 KM/Hr × 2 HOURS', prog(lt_, 0.3, 0.3), '#3ac85a', size=56)
            green_box(ctx, W/2, 880, 'ANS – 120 km', prog(lt_, 2.0, 0.35), 80)

def a6(ctx, t, lt_, step, which):
    card(ctx, 'card_blue')
    if which == 'a':
        if not step:
            ftext(ctx, '9 COINS = 3 GROUPS', W/2, 150, 70, '#ffd23f')
            for g in range(3):
                gx = 420 + g*540; p = prog(lt_, 0.8 + g*0.6, 0.4)
                ctx.set_source_rgba(1, 1, 1, 0.08*p); rrect(ctx, gx - 220, 330, 440, 330, 30); ctx.fill()
                for j in range(3): coin(ctx, gx - 130 + j*130, 500, 52)
                ftext(ctx, 'ABC'[g], gx, 780, 90, '#ffffff', alpha=p)
        else:
            ftext(ctx, 'WEIGHING 1:  A  vs  B', W/2, 150, 66, '#ffd23f')
            tl_ = 0.6*math.sin(clamp(lt_/2.0)*math.pi*2)*(1 if lt_ < 4 else 0)
            balance(ctx, 700, 900, 1.25, tl_, 3, 3, ('A', 'B'))
            tagb(ctx, 1500, 380, 'A GOES UP: FAKE IN A', prog(lt_, 1.0, 0.3), '#ffffff', size=44)
            tagb(ctx, 1500, 520, 'B GOES UP: FAKE IN B', prog(lt_, 2.2, 0.3), '#ffffff', size=44)
            tagb(ctx, 1500, 660, 'EQUAL: FAKE IN C', prog(lt_, 3.6, 0.3), '#ffd23f', size=44)
    else:
        ftext(ctx, 'WEIGHING 2:  1 COIN vs 1 COIN', W/2, 150, 62, '#ffd23f')
        balance(ctx, 700, 900, 1.25, 0.7 if lt_ > 1.5 else 0, 1, 1)
        coin(ctx, 1220, 820, 52)
        tagb(ctx, 1500, 380, 'GOES UP: FAKE', prog(lt_, 1.5, 0.3), '#ffffff', size=48)
        tagb(ctx, 1500, 520, 'EQUAL: THE 3rd COIN', prog(lt_, 3.0, 0.3), '#ffffff', size=48)
        if step: green_box(ctx, 1450, 720, 'ANS – 2 WEIGHINGS', prog(lt_, 0.8, 0.35), 60)

def score_card(ctx, t, lt_):
    rbgs.paint(ctx, 'studio'); ctx.set_source_rgba(0.02, 0.02, 0.06, 0.6); ctx.paint()
    ftext(ctx, 'HOW MANY DID YOU SOLVE?', W/2, 220, 84, '#ffffff', alpha=prog(lt_, 0.1, 0.3))
    for k in range(6):
        x = W/2 - 5*120 + k*240; p = prog(lt_, 0.6 + k*0.25, 0.3)
        ctx.arc(x, 470, 80, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#2a6ae8', p)); ctx.fill()
        text(ctx, str(k + 1), x, 495, 76, '#ffffff', alpha=p)
    tagb(ctx, W/2, 700, 'COMMENT YOUR SCORE: _ / 6', prog(lt_, 2.4, 0.3), '#1a1a1a', bg='#ffd23f', size=60)
    rrect(ctx, 460, 830, 1000, 150, 26); ctx.set_source_rgba(1, 1, 1, 0.95*prog(lt_, 3.0, 0.3)); ctx.fill()
    if lt_ > 3.0:
        text(ctx, 'Add a comment...', 520, 880, 34, '#9a9a9a', align='l')
        s = 'I got 6/6!'; n = int(clamp((lt_ - 3.3)/1.2)*len(s)); text(ctx, s[:n], 520, 950, 54, '#222222', align='l')

def sub_card(ctx, t, lt_):
    rbgs.paint(ctx, 'studio'); ctx.set_source_rgba(0.02, 0.02, 0.06, 0.55); ctx.paint()
    human(ctx, 420, 1080, 0.85, ARJUN, dict(face=1, arm_r='wave', expr='smile'), t)
    human(ctx, 1500, 1080, 0.85, MEENU, dict(face=-1, arm_l='chips', arm_r='wave', expr='laugh'), t)
    ftext(ctx, 'SUBSCRIBE FOR MORE RIDDLES!', W/2, 250, 72, '#ffffff', alpha=prog(lt_, 0.1, 0.3))
    pp = 1 + 0.06*math.sin(t*7); sub = lt_ > 2.4
    ctx.save(); ctx.translate(W/2, 520); ctx.scale(pp, pp)
    rrect(ctx, -280, -80, 560, 160, 80); ctx.set_source_rgba(*hexc('#555555' if sub else '#e62117')); ctx.fill()
    text(ctx, 'SUBSCRIBED' if sub else 'SUBSCRIBE', 0, 26, 66, '#ffffff'); ctx.restore()
    p = prog(lt_, 1.6, 0.5)
    if p > 0:
        yy = lerp(800, 560, sprog(lt_, 1.6, 0.6)) + 20*prog(lt_, 2.3, 0.15)
        ctx.arc(W/2 + 150, yy, 46, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#f3c39a')); ctx.fill()
    ftext(ctx, 'NEW MYSTERIES EVERY DAY', W/2, 760, 50, '#ffd23f', alpha=prog(lt_, 1.0, 0.3))

# ------------------------------------------------------------------ shot table
def shot(name, b, t, lt_, dur):
    """returns (draw_fn(ctx), camera list) ; camera None = screen-space card."""
    st = b.get('step', 0)
    fA = face_cam(ARJUN, *ST['A']); fM = face_cam(MEENU, *ST['M'])
    if name == 'title': return (lambda c: title_card(c, t, lt_)), None
    if name.startswith('st_'):
        cams = {'st_wide': [(960, 540, 1.0), (960, 560, 1.15)], 'st_two': [(960, 640, 1.35)], 'st_arjun': [fA, (700, 640, 1.6)], 'st_meenu': [fM, (1230, 660, 1.6)],
                'st_board': [(980, 300, 2.0), (960, 540, 1.0)]}[name]
        return (lambda c: studio_world(c, t, b)), cams
    if name.startswith('mk_') or name == 'q1':
        fR = face_cam(RAJU, 1170, 1050, 0.66)
        cams = {'mk_wide': [(960, 540, 1.0)], 'mk_pan': [(700, 600, 1.4), (1100, 620, 1.4)], 'mk_raju': [fR, (1170, 700, 1.7)], 'mk_heap': [(640, 760, 2.0), (1500, 940, 2.6)],
                'mk_buy': [(470, 610, 2.6)], 'mk_sell': [(820, 610, 2.6)], 'mk_two': [(1440, 700, 1.4)], 'mk_meenu': [face_cam(MEENU, 1720, 1060, 0.6)],
                'q1': [(960, 540, 1.0)]}[name]
        def d(c):
            market_world(c, t, b)
            if name == 'mk_buy': marker(c, 330, 600, 1)
            if name == 'mk_sell': marker(c, 680, 600, 2)
        if name == 'q1':
            return (lambda c: (market_world(c, t, b), c.set_source_rgba(0, 0, 0, 0.55), c.paint(), q_overlay(c, [('BUY 3 COCONUTS = ₹100', '#7ab8ff'), ('SELL 2 COCONUTS = ₹100', '#3fe08a'), ('PROFIT ₹500 = ? COCONUTS', '#ffd23f')], lt_))), [(960, 540, 1.0)]
        return d, cams
    if name in ('a1a', 'a1b', 'a1c'): return (lambda c: a1(c, t, lt_, st, name[-1])), None
    if name == 'wrong1': return (lambda c: wrong_card(c, t, lt_, '', ['"₹50 PROFIT EACH": 500 ÷ 50 = 10', 'BUT EACH ONE COST ₹33.33'], 'REAL PROFIT: ₹16.67 EACH = 30')), None
    if name.startswith('ch_') or name == 'q2':
        cx, cy, r = CLOCK
        cams = {'ch_wide': [(960, 540, 1.0)], 'ch_tower': [(960, 380, 1.7)], 'ch_clock': [(cx, cy, 3.4)], 'ch_two': [(1400, 840, 2.2), (1200, 640, 1.4)],
                'ch_walk': [(1400, 860, 2.6)], 'ch_meenu': [face_cam(MEENU, *CH['M'], z=3.4)], 'ch_arjun': [face_cam(ARJUN, *CH['A'], z=3.4)], 'q2': [(960, 400, 1.6)]}[name]
        def d(c):
            church_world(c, t, b)
            if name == 'q2':
                c.set_source_rgba(0, 0, 0, 0.0); c.paint()
        if name == 'q2':
            return (lambda c: (church_world(c, t, b), )), [(cx, cy + 60, 2.2)]
        return d, cams
    if name in ('a2a', 'a2b'): return (lambda c: a2(c, t, lt_, st, name[-1])), None
    if name == 'wrong2':
        def d(c):
            card(c, 'card_red'); ftext(c, 'WHY PEOPLE GET IT WRONG', W/2, 150, 60, '#ff8a7a')
            clock_face(c, 620, 600, 300, 3, 0); c.set_source_rgba(0, 0, 0, 0)
            tagb(c, 620, 1000, 'HOUR HAND STAYS ON 3?', prog(lt_, 0.4, 0.3), '#ffffff', size=44); xmark(c, 880, 360, 55, prog(lt_, 1.0, 0.3))
            tagb(c, 1380, 520, 'NOT 0°', prog(lt_, 1.2, 0.3), '#ff8a7a', size=70)
            tagb(c, 1380, 700, 'IT MOVES TOO: 7.5°', prog(lt_, 2.2, 0.3), '#3fe08a', size=52)
        return d, None
    if name.startswith('rv_') or name == 'q3':
        mode = {'rv_danger1': 'danger1', 'rv_danger2': 'danger2', 'rv_safe': 'safe'}.get(name, 'start')
        fK = face_cam(KUTTAN, 800, 905, 0.5, z=3.2)
        cams = {'rv_wide': [(960, 540, 1.0)], 'rv_pan': [(1300, 500, 1.5), (900, 600, 1.3)], 'rv_kuttan': [fK, (800, 760, 2.0)], 'rv_items': [(290, 880, 2.4), (290, 900, 2.0)],
                'rv_boat': [(760, 830, 1.8)], 'rv_danger1': [(220, 860, 2.4)], 'rv_danger2': [(360, 860, 2.4)], 'rv_safe': [(280, 860, 2.2)], 'q3': [(960, 540, 1.0)]}[name]
        if name == 'q3':
            return (lambda c: (river_world(c, t, b), c.set_source_rgba(0, 0, 0, 0.55), c.paint(), q_overlay(c, [('BOAT: KUTTAN + ONLY 1 THING', '#ffffff'), ('DOG EATS HEN • HEN EATS RICE', '#ff8a7a'), ('HOW MANY TRIPS?', '#ffd23f')], lt_))), [(960, 540, 1.0)]
        return (lambda c: river_world(c, t, b, mode)), cams
    if name == 'a3': return (lambda c: a3_card(c, t, lt_, b)), None
    if name == 'wrong3':
        def d(c):
            card(c, 'card_red'); ftext(c, 'WHY PEOPLE GET IT WRONG', W/2, 150, 60, '#ff8a7a')
            tagb(c, W/2, 330, 'ONLY GOING FORWARD = STUCK', prog(lt_, 0.4, 0.3), '#ffffff', size=52); xmark(c, 1600, 330, 50, prog(lt_, 1.0, 0.3))
            hen(c, W/2 - 120, 760, 1.6, -1, t)
            tagb(c, W/2, 900, 'THE TRICK: BRING THE HEN BACK!', prog(lt_, 1.6, 0.3), '#3fe08a', size=54)
        return d, None
    if name.startswith('bk_') or name == 'q4':
        hl = None; reading = ''
        if name == 'bk_scale': reading = '0 g'
        fAm = face_cam(AMMINI, 1600, 1150, 0.95, z=2.6)
        cams = {'bk_wide': [(960, 540, 1.0)], 'bk_pan': [(700, 500, 1.5), (1200, 500, 1.5)], 'bk_jars': [(1000, 380, 1.9), (1000, 400, 1.6)], 'bk_laddoo': [(780, 400, 3.2)],
                'bk_ammini': [fAm, (1550, 640, 1.8)], 'bk_scale': [(960, 760, 2.8)], 'bk_once': [(960, 700, 2.0)], 'bk_meenu': [face_cam(MEENU, 330, 1150, 0.95, z=2.6)], 'q4': [(960, 540, 1.0)]}[name]
        def d(c):
            bakery_world(c, t, b, hl, reading)
            if name == 'bk_laddoo': tagb(c, 780, 220, '1 LADDOO = 50 g', 1, '#ffffff', size=30)
            if name == 'bk_ammini' and b['spk'] == 'AM': pass
            if name == 'bk_once': tagb(c, 960, 600, 'ONLY 1 WEIGHING!', 1, '#ff8a7a', size=40)
        if name == 'q4':
            return (lambda c: (bakery_world(c, t, b), c.set_source_rgba(0, 0, 0, 0.55), c.paint(), q_overlay(c, [('5 JARS • NORMAL LADDOO = 50 g', '#ffffff'), ('1 JAR HAS 60 g LADDOOS', '#ff8a7a'), ('USE THE SCALE ONLY ONCE!', '#ffd23f')], lt_))), [(960, 540, 1.0)]
        if name == 'bk_ammini' and b['spk'] == 'AM':
            return d, cams
        return d, cams
    if name in ('a4a', 'a4b', 'a4c'): return (lambda c: a4(c, t, lt_, st, name[-1])), None
    if name == 'wrong4':
        def d(c):
            card(c, 'card_red'); ftext(c, 'WHY PEOPLE GET IT WRONG', W/2, 150, 60, '#ff8a7a')
            for k, x in enumerate((360, 660, 960, 1260, 1560)): jar(c, x, 560, 0.9, k + 1); laddoo(c, x, 650, 22)
            tagb(c, W/2, 820, '1 FROM EACH: +10 g ... BUT WHICH JAR?', prog(lt_, 0.6, 0.3), '#ffffff', size=48); xmark(c, 1680, 820, 46, prog(lt_, 1.4, 0.3))
            tagb(c, W/2, 960, 'TAKE A DIFFERENT NUMBER FROM EACH JAR', prog(lt_, 2.4, 0.3), '#3fe08a', size=48)
        return d, None
    if name.startswith('rl_') or name == 'q5':
        mode = 'start'
        if name in ('rl_parrot', 'rl_parrot_cu'): mode = 'parrot'
        if name == 'rl_zigzag': mode = 'zigzag'
        cams = {'rl_wide': [(960, 540, 1.0)], 'rl_pan': [(600, 650, 1.6), (1300, 650, 1.6)], 'rl_dist': [(960, 640, 1.15)], 'rl_train_a': [(420, 720, 2.4)], 'rl_train_b': [(1500, 790, 2.4)],
                'rl_parrot': [(700, 620, 1.8)], 'rl_parrot_cu': [(760, 560, 3.0)], 'rl_zigzag': [(960, 640, 1.2)], 'q5': [(960, 540, 1.0)]}[name]
        def d(c):
            rail_world(c, t, b, lt_, mode)
            if name == 'rl_dist': measure(c, 520, 1400, 930, '150 km', prog(lt_, 0.3, 0.6))
            if name == 'rl_train_a': tagb(c, 400, 560, '40 KM/Hr', 1, '#7ab8ff', size=26)
            if name == 'rl_train_b': tagb(c, 1500, 640, '35 KM/Hr', 1, '#ff8a7a', size=26)
            if name in ('rl_parrot', 'rl_parrot_cu'): tagb(c, 760, 470, '60 KM/Hr', 1, '#3fe08a', size=24)
        if name == 'q5':
            return (lambda c: (rail_world(c, t, b, lt_, 'start'), c.set_source_rgba(0, 0, 0, 0.55), c.paint(), q_overlay(c, [('TRAINS 150 km APART: 40 & 35 KM/Hr', '#ffffff'), ('PARROT FLIES BACK AND FORTH: 60 KM/Hr', '#3fe08a'), ('TOTAL DISTANCE = ?', '#ffd23f')], lt_))), [(960, 540, 1.0)]
        return d, cams
    if name in ('a5a', 'a5b'): return (lambda c: a5(c, t, lt_, st, name[-1])), None
    if name == 'wrong5':
        def d(c):
            card(c, 'card_red'); ftext(c, 'WHY PEOPLE GET IT WRONG', W/2, 150, 60, '#ff8a7a')
            pts = [(300 + k*120, 520 + (60 if k % 2 else -60)) for k in range(12)]
            c.set_dash([16, 12]); c.set_source_rgba(1, 1, 1, 0.8); c.set_line_width(5); c.move_to(*pts[0])
            for pp in pts[1:]: c.line_to(*pp)
            c.stroke(); c.set_dash([])
            parrot(c, 300 + (lt_*150) % 1300, 450, 0.8, 1, t)
            tagb(c, W/2, 760, 'ADDING EVERY TRIP NEVER ENDS', prog(lt_, 0.5, 0.3), '#ffffff', size=52); xmark(c, 1620, 760, 46, prog(lt_, 1.2, 0.3))
            tagb(c, W/2, 920, 'USE THE TIME: 2 HOURS × 60', prog(lt_, 2.4, 0.3), '#3fe08a', size=52)
        return d, None
    if name.startswith('jw_') or name == 'q6':
        fJ = face_cam(JOSE, 1420, 1120, 0.72, z=3.0); fAj = face_cam(ARJUN, 230, 1090, 0.74, z=3.0)
        cams = {'jw_wide': [(960, 540, 1.0)], 'jw_pan': [(1300, 500, 1.5), (700, 500, 1.5)], 'jw_coins': [(1060, 720, 3.0), (1060, 730, 2.4)], 'jw_jose': [fJ, (1380, 640, 1.8)],
                'jw_scale': [(560, 600, 2.0)], 'jw_scale_cu': [(560, 540, 3.0)], 'jw_two': [(800, 600, 1.2)], 'jw_arjun': [fAj], 'q6': [(960, 540, 1.0)]}[name]
        def d(c):
            jewel_world(c, t, b, tilt=0.3*math.sin(t*1.5) if name == 'jw_scale_cu' else 0)
            if name == 'jw_coins': tagb(c, 1060, 640, '9 COINS • 1 IS LIGHTER', 1, '#ffd23f', size=26)
            if name == 'jw_scale': tagb(c, 560, 360, 'NO WEIGHTS', 1, '#ffffff', size=32)
        if name == 'q6':
            return (lambda c: (jewel_world(c, t, b), c.set_source_rgba(0, 0, 0, 0.55), c.paint(), q_overlay(c, [('9 GOLD COINS • 1 FAKE (LIGHTER)', '#ffffff'), ('BALANCE SCALE • NO WEIGHTS', '#7ab8ff'), ('FEWEST WEIGHINGS = ?', '#ffd23f')], lt_))), [(960, 540, 1.0)]
        return d, cams
    if name in ('a6a', 'a6b'): return (lambda c: a6(c, t, lt_, st, name[-1])), None
    if name == 'wrong6':
        def d(c):
            card(c, 'card_red'); ftext(c, 'WHY PEOPLE GET IT WRONG', W/2, 150, 60, '#ff8a7a')
            for k, s in enumerate(('4 vs 4', '2 vs 2', '1 vs 1')):
                tagb(c, 420 + k*540, 400, s, prog(lt_, 0.5 + 0.7*k, 0.3), '#ffffff', size=60)
            tagb(c, W/2, 600, '= 3 WEIGHINGS', prog(lt_, 2.6, 0.3), '#ff8a7a', size=60); xmark(c, 1450, 600, 46, prog(lt_, 3.0, 0.3))
            tagb(c, W/2, 820, 'SPLIT INTO 3 GROUPS = ONLY 2', prog(lt_, 4.0, 0.3), '#3fe08a', size=58)
        return d, None
    if name == 'score': return (lambda c: score_card(c, t, lt_)), None
    if name == 'sub': return (lambda c: sub_card(c, t, lt_)), None
    raise KeyError(name)

# ------------------------------------------------------------------ overlays
BADGE = {'r1': 'RIDDLE 1/6', 'r2': 'RIDDLE 2/6', 'r3': 'RIDDLE 3/6', 'r4': 'RIDDLE 4/6', 'r5': 'RIDDLE 5/6', 'r6': 'RIDDLE 6/6'}
def overlays(ctx, t, b):
    sec = b['sec']
    if sec in BADGE:
        q = prog(t, SEC_START[sec] + 0.3, 0.4)
        lab = BADGE[sec]; w = text_w(ctx, lab, 30) + 50
        rrect(ctx, 40, 40, w, 58, 14); ctx.set_source_rgba(0.03, 0.06, 0.18, 0.82*q); ctx.fill()
        rrect(ctx, 40, 40, 10, 58, 4); ctx.set_source_rgba(*hexc('#ffd23f', q)); ctx.fill()
        text(ctx, lab, 40 + w/2 + 5, 80, 30, '#ffffff', alpha=q)
        if b.get('badge') and t < b['t0'] + 2.6:
            # big riddle number intro
            p = prog(t, b['t0'] - 0.05, 0.35)*(1 - prog(t, b['t0'] + 2.1, 0.4))
            ctx.save(); ctx.translate(W/2, 170); ctx.scale(back(min(1, p)) if p > 0 else 0.001, back(min(1, p)) if p > 0 else 0.001)
            ww = text_w(ctx, 'RIDDLE ' + sec[1], 76) + 90
            rrect(ctx, -ww/2, -62, ww, 124, 24); ctx.set_source_rgba(0.02, 0.02, 0.06, 0.88*p); ctx.fill()
            text(ctx, 'RIDDLE ' + sec[1], 0, 26, 76, '#ffd23f', alpha=p); ctx.restore()
    if b.get('card') and t >= b['t0']:
        q = prog(t, b['t0'] + 0.1, 0.35)
        lab = b['card']; w = text_w(ctx, lab, 54) + 80
        ctx.save(); ctx.translate(W/2, 120); ctx.scale(back(q), back(q))
        rrect(ctx, -w/2, -52, w, 104, 22); ctx.set_source_rgba(0.02, 0.02, 0.06, 0.9); ctx.fill()
        text(ctx, lab, 0, 20, 54, '#ffd23f'); ctx.restore()
    if b.get('timer') and t >= b['tt0'] - 0.25:
        p = clamp((t - b['tt0'])/(b['tt1'] - b['tt0']))
        ctx.rectangle(0, 0, W, 18); ctx.set_source_rgba(0, 0, 0, 0.6); ctx.fill()
        ctx.rectangle(0, 0, W*p, 18); ctx.set_source_rgba(*hexc('#ffd23f')); ctx.fill()
        q = prog(t, b['tt0'] - 0.25, 0.3)
        ctx.save(); ctx.translate(W/2, H - 110); ctx.scale(back(q), back(q))
        rrect(ctx, -360, -48, 720, 96, 48); ctx.set_source_rgba(0.9, 0.12, 0.1, 0.92); ctx.fill()
        for dx in (-300, -278): ctx.rectangle(dx, -20, 12, 40); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        text(ctx, 'PAUSE THE VIDEO AND THINK', 22, 15, 38, '#ffffff'); ctx.restore()
    if b.get('ans') and b['shots'][0] not in ('a3', 'a1c', 'a4c'):
        q = prog(t, b['t0'] + b['d']*0.45, 0.35)
        if q > 0 and b['shots'][0] not in ('a2b', 'a5b', 'a6b'):
            lab = b['ans']; w = text_w(ctx, lab, 52) + 90
            ctx.save(); ctx.translate(W/2, H - 120); ctx.scale(back(q), back(q))
            rrect(ctx, -w/2, -52, w, 104, 22); ctx.set_source_rgba(0.04, 0.24, 0.12, 0.92); ctx.fill()
            ctx.set_source_rgba(*hexc('#2ad06a')); ctx.set_line_width(7); rrect(ctx, -w/2, -52, w, 104, 22); ctx.stroke()
            text(ctx, lab, 0, 18, 52, '#ffffff'); ctx.restore()

# ------------------------------------------------------------------ frame draw
def beat_at(t):
    i = 0
    for j, b in enumerate(B):
        if t >= b['t0'] - 0.05: i = j
    return i

def plan(b):
    s0 = b['t0'] - (0.05 if b is not B[0] else b['t0']); s1 = b['end']
    n = len(b['shots']); seg = (s1 - s0)/n; out = []
    for k, nm in enumerate(b['shots']):
        a = s0 + k*seg
        out.append((nm, a, a + seg, max(1, int(seg/2.0))))
    return out

def draw_frame(ctx, t, bi=None):
    i = beat_at(t) if bi is None else bi
    b = B[i]; pl = plan(b)
    for (nm, a, z, nsub) in pl:
        if a <= t < z or (nm, a, z, nsub) == pl[-1]: break
    lt_ = t - a; dur = z - a
    sd = dur/nsub; k = min(nsub - 1, int(lt_/sd)); slt = lt_ - k*sd
    # answer cards keep beat-relative time across a beat (no reset at sub-shots)
    fn, cams = shot(nm, b, t, t - b['t0'] if nm.startswith(('a', 'q', 'wrong', 'score', 'sub', 'title')) else lt_, dur)
    ctx.save()
    if cams:
        c = cams[k % len(cams)]
        p = clamp(slt/sd)
        drift = ((-1)**(k + i))*14
        cx, cy, z_ = kb(c, p, (drift, 0, 0.05))
        cam(ctx, cx, cy, z_)
    else:
        s = 1 + 0.03*clamp(lt_/max(dur, 0.1)); ctx.translate(W/2, H/2); ctx.scale(s, s); ctx.translate(-W/2, -H/2)
    fn(ctx)
    ctx.restore()
    overlays(ctx, t, b)

def frame(ctx, t):
    i = beat_at(t); b = B[i]
    draw_frame(ctx, t, i)
    if i > 0 and B[i-1]['sec'] != b['sec'] and t < b['t0'] + 0.45 and t >= b['t0'] - 0.05:
        a = 1 - clamp((t - b['t0'] + 0.05)/0.5)
        ctx.push_group(); draw_frame(ctx, min(t, B[i-1]['end'] - 0.01), i - 1); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 600, 1200, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.28))])); ctx.fill()
    if t < 0.6: ctx.set_source_rgba(0, 0, 0, 1 - t/0.6); ctx.paint()
    if t > TOTAL - 0.8: ctx.set_source_rgba(0, 0, 0, clamp((t - (TOTAL - 0.8))/0.8)); ctx.paint()

# ------------------------------------------------------------------ audio
def sting():
    out = np.zeros(int(2.2*SR))
    for f in (146.8, 174.6, 220.0, 293.7): A.add(out, A.pluck(f, 2.0, dec=1.2)*0.5, 0)
    A.add(out, A.bell(587.3, 1.8, 2.0)*0.3, int(0.05*SR))
    return out
def softtick():
    n = int(0.05*SR); tt = np.arange(n)/SR; return np.sin(2*np.pi*1500*tt)*np.exp(-tt*90)*0.35

def mystery_bed(dur):
    n = int(dur*SR); y = np.zeros(n)
    prog_ = [(50, [62, 65, 69]), (46, [62, 65, 70]), (48, [60, 64, 67]), (45, [61, 64, 69])]
    pat = [0, 2, 1, 2, 0, 2, 1, 2]
    step = 0.45; k = 0
    while k*step < dur:
        bar = (k // 16) % 4; root, ch = prog_[bar]
        m = ch[pat[k % 8] % 3] + (12 if k % 16 in (6, 14) else 0)
        A.add(y, A.pluck(A.mtof(m), 0.6, dec=7, bright=0.6)*(0.45 if k % 2 else 0.6), int(k*step*SR))
        if k % 8 == 0: A.add(y, A.bass(A.mtof(root - 12), 3.0)*0.55, int(k*step*SR))
        if k % 16 == 0: A.add(y, A.bell(A.mtof(ch[2] + 12), 3.0, 1.2)*0.12, int((k*step + 0.21)*SR))
        k += 1
    blk = 16*step*4
    for j in range(int(dur/blk) + 1):
        for bi_, (root, ch) in enumerate(prog_):
            st = j*blk + bi_*16*step
            if st >= dur: break
            A.add(y, A.pad([A.mtof(c - 12) for c in ch], 16*step + 0.6)*0.18, int(st*SR))
    return y

def build_audio(path):
    n = int((TOTAL + 1)*SR); v = np.zeros(n); fx = np.zeros(n)
    for b in B:
        y, sr = sf.read(b['wav']); y = y if y.ndim == 1 else y.mean(1); A.add(v, y, int(b['t0']*SR))
    for i, b in enumerate(B):
        if i and B[i-1]['sec'] != b['sec']: A.add(fx, sfx2('whoosh')*0.45, int((b['t0'] - 0.25)*SR))
        for (nm, a, z, nsub) in plan(b):
            if a > b['t0'] + 0.3: A.add(fx, sfx2('whoosh')*0.12, int((a - 0.1)*SR))
        if b.get('sfx') == 'sting': A.add(fx, sting()*0.6, int((b['t0'] + 0.05)*SR))
        if b.get('timer'):
            tt = b['tt0']
            while tt < b['tt1']: A.add(fx, softtick(), int(tt*SR)); tt += 0.5
            A.add(fx, sfx2('right')*0.25, int(b['tt1']*SR))
        if b.get('ans'): A.add(fx, sting()*0.35, int((b['t0'] + b['d']*0.45)*SR))
    bed = mystery_bed(TOTAL + 1); bed = bed/np.abs(bed).max()
    env = np.convolve(np.abs(v), np.ones(int(0.25*SR))/int(0.25*SR), mode='same'); duck = 1 - 0.6*np.clip(env/0.04, 0, 1)
    tim = np.ones(n)
    for b in B:
        if b.get('timer'): tim[int(b['tt0']*SR):int(b['tt1']*SR)] = 0.55
    mix_ = (v*1.0 + bed[:n]*0.16*duck*tim + fx*0.8)[:int(TOTAL*SR)]
    tmp = path + '.tmp.wav'; sf.write(tmp, mix_.astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', path], check=True); os.remove(tmp)

def meta():
    ch = []
    for sid, lab in SECTIONS:
        s = SEC_START[sid]; ch.append(('%02d:%02d' % (int(s)//60, int(s) % 60), lab))
    return dict(total=TOTAL, chapters=ch)

def render_part(part, nparts):
    fps = 30; nf = int(TOTAL*fps); a = nf*part//nparts; z = nf*(part + 1)//nparts
    out = f'{OUT}/part{part}.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    import time; t0 = time.time()
    for fi in range(a, z):
        ctx.save(); ctx.set_source_rgb(0, 0, 0); ctx.paint(); frame(ctx, fi/fps); ctx.restore(); surf.flush(); p.stdin.write(surf.get_data())
        if (fi - a) % 300 == 0: print(part, fi - a, z - a, round(time.time() - t0), flush=True)
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    mode = sys.argv[1]
    print('TOTAL', round(TOTAL, 1))
    if mode == 'stills':
        ts = [float(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else [b['t0'] + 0.8 for b in B]
        os.makedirs(f'{OUT}/st', exist_ok=True)
        for j, tt in enumerate(ts):
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); frame(ctx, tt)
            small = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640, 360); c2 = cairo.Context(small); c2.scale(1/3, 1/3); c2.set_source_surface(surf); c2.paint()
            small.write_to_png(f'{OUT}/st/s{j:03d}.png')
    elif mode == 'audio':
        build_audio(f'{OUT}/{NAME}.wav'); json.dump(meta(), open(f'{OUT}/meta.json', 'w'), indent=1); print(meta())
    elif mode == 'video':
        render_part(int(sys.argv[2]), int(sys.argv[3]))
    elif mode == 'final':
        n = int(sys.argv[2])
        open(f'{OUT}/list.txt', 'w').write(''.join(f"file 'part{k}.mp4'\n" for k in range(n)))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-i', f'{OUT}/{NAME}.wav',
                        '-c:v', 'libx264', '-preset', 'medium', '-b:v', '1000k', '-maxrate', '1600k', '-bufsize', '3200k', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', f'{OUT}/{NAME}.mp4'], check=True)
