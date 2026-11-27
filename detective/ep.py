"""Detective Arjun episode renderer (16:9 long video, 1920x1080).
Episode: Who Stole the Palace Sword?  Culprit: Dr. Ravi Menon (key + leather heeled shoe + over 6 ft + yesterday's receipt).
python3 ep.py stills | audio | video <part> <nparts> | final"""
import sys, os, math, json, random, subprocess
import numpy as np, soundfile as sf, cairo
sys.path.insert(0, '/home/claude/det'); sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/ml'); sys.path.insert(0, '/home/claude')
from chars import human, geo, ARJUN, MEENU, RAVI, VELU, SHANTHA, FAIZAL, POLICE, hexc, mix, lt, dk, shade, vshade, ellipse, rrect, outline
import bgs
from bgs import lin, rad, glow, W, H, FLOOR
from wd import text, text_w
from pz import voice, wav_dur, clamp, prog, sprog, back, lerp, sfx2
import audio as A
from script import B, SPK, SECTIONS
SR = 44100
OUT = '/home/claude/det/out'; os.makedirs(OUT, exist_ok=True)
NAME = 'KP_Who_Stole_the_Palace_Sword_YouTube'
SW = 0.62  # gallery character scale

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

# ------------------------------------------------------------------ camera
def cam(ctx, cx, cy, z):
    z = max(1.0, z); hw, hh_ = W/(2*z), H/(2*z)
    cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh_), H - hh_)
    ctx.translate(W/2, H/2); ctx.scale(z, z); ctx.translate(-cx, -cy)

def kb(c0, p, drift=(0.0, 0.0, 0.045)):
    cx, cy, z = c0; return (cx + drift[0]*p, cy + drift[1]*p, z*(1 + drift[2]*p))

# ------------------------------------------------------------------ props in the world
def sword(ctx, x, y, s=1.0, ang=0.0, glint=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.move_to(-10, -9); ctx.line_to(150, -6); ctx.curve_to(175, -4, 182, 2, 186, 6); ctx.curve_to(170, 6, 160, 8, 150, 8); ctx.line_to(-10, 9); ctx.close_path()
    ctx.set_source(lin(ctx, 0, -9, 0, 9, [(0, '#fff6d0'), (0.5, '#e8c860'), (1, '#9a7420')])); ctx.fill_preserve(); outline(ctx, 1.5, 0.5)
    ctx.move_to(0, 0); ctx.line_to(150, 1); ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(1.5); ctx.stroke()
    rrect(ctx, -22, -30, 14, 60, 5); ctx.set_source(lin(ctx, 0, -30, 0, 30, [(0, '#f8d870'), (1, '#a07018')])); ctx.fill()
    rrect(ctx, -70, -8, 50, 16, 7); ctx.set_source(lin(ctx, 0, -8, 0, 8, [(0, '#a01a2a'), (1, '#5a0a14')])); ctx.fill()
    for k in range(4): ctx.arc(-64 + k*13, 0, 3, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#f0c860')); ctx.fill()
    ctx.arc(-76, 0, 10, 0, 2*math.pi); ctx.set_source(lin(ctx, -86, 0, -66, 0, [(0, '#f8d870'), (1, '#a07018')])); ctx.fill()
    ctx.arc(-15, 0, 5, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#d0203a')); ctx.fill()
    if glint > 0:
        gx = -60 + (glint % 1.0)*240
        for a in (0, math.pi/2):
            ctx.save(); ctx.translate(gx, 0); ctx.rotate(a + 0.6)
            ctx.move_to(-22, 0); ctx.line_to(0, -3); ctx.line_to(22, 0); ctx.line_to(0, 3); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill(); ctx.restore()
    ctx.restore()

def case(ctx, t, has_sword=False, lit=True, glint=False):
    x0, x1 = 860, 1060
    ctx.rectangle(880, 760, 160, 225); ctx.set_source(lin(ctx, 880, 0, 1040, 0, [(0, '#7a4a2a'), (0.5, '#5a321a'), (1, '#2a160a')])); ctx.fill()
    for yy in (760, 960): rrect(ctx, 868, yy, 184, 24, 5); ctx.set_source(lin(ctx, 0, yy, 0, yy+24, [(0, '#9a6a3a'), (1, '#4a2a14')])); ctx.fill()
    rrect(ctx, 905, 800, 110, 130, 8); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.set_line_width(4); ctx.stroke()
    # velvet cushion + stand
    rrect(ctx, 870, 720, 180, 40, 12); ctx.set_source(lin(ctx, 0, 720, 0, 760, [(0, '#c0283a'), (1, '#6a0a18')])); ctx.fill()
    for x in (905, 1015): ctx.rectangle(x - 4, 690, 8, 32); ctx.set_source_rgba(*hexc('#d8a83a')); ctx.fill(); ctx.arc(x, 690, 8, math.pi, 0); ctx.set_line_width(4); ctx.stroke()
    if has_sword: sword(ctx, 960 - 40, 688, 0.62, 0.0, glint=(t*0.4) if glint else 0)
    # glass box
    ctx.rectangle(x0, 600, x1 - x0, 160); ctx.set_source_rgba(0.75, 0.88, 1, 0.10 if lit else 0.07); ctx.fill()
    ctx.move_to(x0 + 20, 610); ctx.line_to(x0 + 60, 610); ctx.line_to(x0 + 18, 750); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.16); ctx.fill()
    ctx.move_to(x1 - 50, 610); ctx.line_to(x1 - 34, 610); ctx.line_to(x1 - 70, 750); ctx.line_to(x1 - 86, 750); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.1); ctx.fill()
    ctx.rectangle(x0, 600, x1 - x0, 160); ctx.set_source_rgba(0.85, 0.75, 0.45, 0.9); ctx.set_line_width(4); ctx.stroke()
    rrect(ctx, 946, 744, 28, 20, 3); ctx.set_source(lin(ctx, 0, 744, 0, 764, [(0, '#f0c860'), (1, '#9a7020')])); ctx.fill()
    ctx.arc(960, 752, 3, 0, 2*math.pi); ctx.set_source_rgba(0.1, 0.05, 0, 1); ctx.fill()
    if lit: glow(ctx, 960, 650, 220, (1, 0.9, 0.6), 0.16)

def cctv(ctx, t, turned=True):
    ctx.save(); ctx.translate(1690, 246)
    ctx.rectangle(-8, -12, 16, 26); ctx.set_source_rgba(*hexc('#b8b8c2')); ctx.fill()
    ctx.rotate(-1.15 if turned else 0.45)
    rrect(ctx, -10, -14, 74, 28, 7); ctx.set_source(lin(ctx, 0, -14, 0, 14, [(0, '#ffffff'), (1, '#a8acb8')])); ctx.fill_preserve(); outline(ctx, 1.5, 0.5)
    rrect(ctx, 56, -12, 14, 24, 4); ctx.set_source_rgba(*hexc('#1a1a22')); ctx.fill()
    ctx.arc(66, 0, 6, 0, 2*math.pi); ctx.set_source_rgba(0.2, 0.3, 0.6, 1); ctx.fill()
    ctx.arc(4, -6, 3, 0, 2*math.pi); ctx.set_source_rgba(1, 0.1, 0.1, 0.5 + 0.5*(int(t*2) % 2)); ctx.fill()
    ctx.restore()

def wet_sign(ctx, x, y):
    ctx.move_to(x - 40, y); ctx.line_to(x - 12, y - 130); ctx.line_to(x + 12, y - 130); ctx.line_to(x + 40, y); ctx.close_path()
    ctx.set_source(lin(ctx, x-40, 0, x+40, 0, [(0, '#ffe04a'), (1, '#d8a818')])); ctx.fill_preserve(); outline(ctx, 2, 0.5)
    ctx.move_to(x - 12, y - 92); ctx.line_to(x, y - 112); ctx.line_to(x + 12, y - 92); ctx.close_path(); ctx.set_source_rgba(0.1, 0.1, 0.1, 1); ctx.set_line_width(3); ctx.stroke()
    text(ctx, 'WET', x, y - 58, 20, '#1a1a1a'); text(ctx, 'FLOOR', x, y - 36, 15, '#1a1a1a')

def footprint(ctx, x, y, s=1.0, a=1.0, ang=-0.25, col=(0.12, 0.05, 0.04)):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.move_to(0, -60); ctx.curve_to(26, -60, 30, -30, 28, -5); ctx.curve_to(26, 12, 18, 22, 10, 26); ctx.line_to(-10, 26)
    ctx.curve_to(-20, 20, -26, 8, -26, -10); ctx.curve_to(-26, -40, -18, -60, 0, -60); ctx.close_path()
    ctx.set_source_rgba(*col, 0.55*a); ctx.fill()
    rrect(ctx, -17, 44, 34, 28, 8); ctx.set_source_rgba(*col, 0.6*a); ctx.fill()
    ctx.restore()

def marker(ctx, x, y, n, label=None, p=1.0, side=1):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = back(clamp(p)); ctx.scale(sc, sc)
    ctx.arc(0, 0, 30, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#1e6ae8')); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(5); ctx.stroke()
    text(ctx, str(n), 0, 12, 34, '#ffffff')
    if label:
        w = text_w(ctx, label, 28) + 30
        bx = 40 if side > 0 else -40 - w
        rrect(ctx, bx, -24, w, 48, 10); ctx.set_source_rgba(0.04, 0.08, 0.2, 0.85); ctx.fill()
        text(ctx, label, bx + w/2, 10, 28, '#ffffff')
    ctx.restore()

def xmark(ctx, x, y, r, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(back(clamp(p)), back(clamp(p)))
    ctx.set_source_rgba(*hexc('#e8283a')); ctx.set_line_width(r*0.28); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(-r, -r); ctx.line_to(r, r); ctx.move_to(r, -r); ctx.line_to(-r, r); ctx.stroke(); ctx.restore()

def green_box(ctx, x, y, w, h, p):
    if p <= 0: return
    ctx.save(); ctx.set_source_rgba(*hexc('#2ad06a', clamp(p))); ctx.set_line_width(10); rrect(ctx, x, y, w, h, 18); ctx.stroke(); ctx.restore()

BLACK = dict(ARJUN, name='SHADOW', skin='#0c0a14', hair='#0c0a14', top_col='#0c0a14', shirt='#0c0a14', bot_col='#0c0a14', hat=None, hat_col='#0c0a14', stache=None, h=1.04, top='blazer', tie='#0c0a14', shoe='leather_black')

# ------------------------------------------------------------------ world scenes
PEOPLE_INTRO = {'M': (430, MEENU, -0.0), 'A': (640, ARJUN, 0), 'R': (1290, RAVI, 0), 'V': (1490, VELU, 0)}

def gallery_world(ctx, t, b, lit=True, who=('A', 'M'), has_sword=False, poses=None, extra=None, pos=None, alarm=False):
    bgs.paint(ctx, 'gal_lit' if lit else 'gal_dark')
    cctv(ctx, t)
    if extra and 'wet' in extra: wet_sign(ctx, 1180, 990)
    if extra and 'print' in extra: footprint(ctx, 1080, 1010, 0.45, 1.0, -0.2)
    case(ctx, t, has_sword, lit, glint=has_sword)
    poses = poses or {}
    pos = pos or {}
    order = sorted(who, key=lambda k: {'M': 0, 'A': 1, 'R': 2, 'V': 3, 'S': 4, 'F': 5}[k])
    specs = {'A': ARJUN, 'M': MEENU, 'R': RAVI, 'V': VELU, 'S': SHANTHA, 'F': FAIZAL}
    base = {'M': 470, 'A': 690, 'R': 1290, 'V': 1490, 'S': 1250, 'F': 1450}
    for k in order:
        x = pos.get(k, base[k]); po = dict(face=1 if x < 960 else -1, expr='neutral'); po.update(poses.get(k, {}))
        po['talk'] = talk_of(b, k, t)
        human(ctx, x, FLOOR + (8 if k in 'MA' else 0), SW, specs[k], po, t)
    if alarm:
        a = 0.5 + 0.5*math.sin(t*9)
        ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(0.9, 0.05, 0.08, 0.25*a); ctx.fill()

def face_cam(k, x, z=3.0, dy=40):
    spec = {'A': ARJUN, 'M': MEENU, 'R': RAVI, 'V': VELU, 'S': SHANTHA, 'F': FAIZAL}[k]
    g = geo(spec); return (x, FLOOR + g['hc']*SW + dy*(3.0/z), z)

# ------------------------------------------------------------------ inserts (screen-space cards)
def title_card(ctx, t, lt_):
    bgs.paint(ctx, 'card_red')
    glow(ctx, W/2, 600, 520, (1, 0.8, 0.3), 0.25)
    sword(ctx, W/2 - 170, 610, 2.0, 0.0, glint=t*0.5)
    text(ctx, 'DETECTIVE ARJUN', W/2, 190, 46, '#f0c860', alpha=prog(lt_, 0.1, 0.4))
    s = 1 + 0.03*sprog(lt_, 0, 3)
    ctx.save(); ctx.translate(W/2, 360); ctx.scale(s, s)
    text(ctx, 'WHO STOLE THE', 0, 0, 96, '#ffffff', alpha=prog(lt_, 0.2, 0.3))
    text(ctx, 'PALACE SWORD?', 0, 110, 120, '#ffd23f', alpha=prog(lt_, 0.5, 0.3)); ctx.restore()
    text(ctx, 'A Malayalam detective riddle', W/2, 900, 38, '#d0c8e8', alpha=prog(lt_, 1.0, 0.5))

def timeline_card(ctx, t, lt_):
    bgs.paint(ctx, 'card_blue')
    y = 560; ctx.rectangle(260, y - 5, 1400, 10); ctx.set_source_rgba(1, 1, 1, 0.5); ctx.fill()
    p = sprog(lt_, 0.3, 1.5)
    ctx.rectangle(560, y - 9, 800*p, 18); ctx.set_source_rgba(*hexc('#e8283a')); ctx.fill()
    for x, lab, sub in ((560, '10:30 PM', 'SWORD SEEN'), (1360, '11:00 PM', 'ALARM')):
        ctx.arc(x, y, 26, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#ffd23f')); ctx.fill()
        text(ctx, lab, x, y - 70, 60, '#ffffff'); text(ctx, sub, x, y + 90, 40, '#9ec4ff')
    if lt_ > 1.6:
        q = prog(lt_, 1.6, 0.4)
        rrect(ctx, 760, 640, 400, 80, 16); ctx.set_source_rgba(*hexc('#e8283a', q)); ctx.fill()
        text(ctx, 'THEFT HAPPENED', 960, 694, 40, '#ffffff', alpha=q)
    text(ctx, 'CASE TIMELINE', W/2, 200, 56, '#ffd23f')

SUS4 = [('V', VELU, 'VELAYUDHAN', 'WATCHMAN', 0.05), ('S', SHANTHA, 'SHANTHA', 'CLEANER', 0.22), ('F', FAIZAL, 'FAIZAL', 'ELECTRICIAN', 0.42), ('R', RAVI, 'DR. RAVI MENON', 'CURATOR', 0.68)]
def four_card(ctx, t, lt_, b, reveal):
    bgs.paint(ctx, 'card')
    dur = b['t1'] - b['t0']
    for i, (k, spec, nm, role, at) in enumerate(SUS4):
        x = 330 + i*420
        on = reveal and lt_ > at*dur
        q = prog(lt_, at*dur, 0.5) if reveal else 0
        glow(ctx, x, 560, 260, (1, 0.9, 0.6), 0.18*q)
        sp = spec if on else dict(BLACK, h=spec['h'], sex=spec['sex'], hairstyle=spec['hairstyle'], top=spec['top'] if spec['top'] != 'trench' else 'blazer', bottom=spec['bottom'], shoe=spec['shoe'], dupatta='#0c0a14', bag='#0c0a14', border='#0c0a14', glasses=None)
        human(ctx, x, 930, 0.78, sp, dict(face=1 if i < 2 else -1, expr='neutral' if k != 'R' else 'smug'), t, shadow=True)
        if not on: text(ctx, '?', x, 330, 120, '#ffd23f', alpha=0.9)
        else:
            rrect(ctx, x - 190, 950, 380, 96, 14); ctx.set_source_rgba(0.05, 0.05, 0.12, 0.9*q); ctx.fill()
            text(ctx, nm, x, 992, 34 if len(nm) < 12 else 30, '#ffffff', alpha=q); text(ctx, role, x, 1030, 28, '#ffd23f', alpha=q)
    text(ctx, '4 PEOPLE. 1 THIEF.', W/2, 120, 60, '#ffffff')

def lock_card(ctx, t, lt_, mode):
    bgs.paint(ctx, 'card_blue')
    # big glass panel corner with brass frame and lock plate
    ctx.rectangle(260, 120, 1400, 760); ctx.set_source_rgba(0.7, 0.85, 1, 0.08); ctx.fill()
    for (x, y, w, h) in ((260, 120, 1400, 24), (260, 856, 1400, 24), (260, 120, 24, 760), (1636, 120, 24, 760)):
        ctx.rectangle(x, y, w, h); ctx.set_source(lin(ctx, x, y, x + w, y + h, [(0, '#f0d080'), (0.5, '#a87a2a'), (1, '#e0b850')])); ctx.fill()
    for k in range(3):
        ctx.move_to(420 + k*90, 150); ctx.line_to(470 + k*90, 150); ctx.line_to(330 + k*90, 850); ctx.line_to(280 + k*90, 850); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.05 + 0.03*k); ctx.fill()
    ctx.move_to(1300, 150); ctx.line_to(1330, 150); ctx.line_to(1200, 850); ctx.line_to(1170, 850); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.1); ctx.fill()
    # lock plate
    rrect(ctx, 840, 660, 240, 200, 24); ctx.set_source(lin(ctx, 840, 660, 1080, 860, [(0, '#ffe08a'), (0.5, '#c8962a'), (1, '#8a5a14')])); ctx.fill_preserve(); outline(ctx, 3, 0.6)
    for (x, y) in ((870, 690), (1050, 690), (870, 830), (1050, 830)): ctx.arc(x, y, 9, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#6a4a10')); ctx.fill()
    ctx.arc(960, 735, 26, 0, 2*math.pi); ctx.set_source_rgba(0.08, 0.04, 0.0, 1); ctx.fill()
    ctx.move_to(948, 750); ctx.line_to(972, 750); ctx.line_to(966, 805); ctx.line_to(954, 805); ctx.close_path(); ctx.fill()
    ctx.move_to(880, 700); ctx.curve_to(920, 680, 1000, 680, 1040, 700); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(4); ctx.stroke()
    if mode in ('cu', 'mag'):
        marker(ctx, 560, 400, 1, 'NO CRACK', prog(lt_, 0.5, 0.3))
        marker(ctx, 1110, 700, 2, 'NO SCRATCH', prog(lt_, 1.3, 0.3))
    if mode == 'mag':
        mx, my = 960 + 30*math.sin(t), 750
        ctx.arc(mx, my, 170, 0, 2*math.pi); ctx.set_source_rgba(0.85, 0.95, 1, 0.12); ctx.fill_preserve(); ctx.set_source_rgba(*hexc('#2a2a30')); ctx.set_line_width(22); ctx.stroke()
        ctx.save(); ctx.translate(mx, my); ctx.rotate(0.7); rrect(ctx, 170, -22, 210, 44, 18); ctx.set_source_rgba(*hexc('#4a2a14')); ctx.fill(); ctx.restore()
    if mode == 'key':
        p = sprog(lt_, 0.4, 1.2)
        ctx.save(); ctx.translate(960, 760 + 220*(1 - p)); ctx.rotate(-math.pi/2 + (0.6*sprog(lt_, 1.8, 0.6)))
        ctx.arc(-150, 0, 50, 0, 2*math.pi); ctx.set_source(lin(ctx, -200, -50, -100, 50, [(0, '#ffe08a'), (1, '#9a6a14')])); ctx.set_line_width(22); ctx.stroke()
        ctx.rectangle(-100, -14, 190, 28); ctx.set_source(lin(ctx, 0, -14, 0, 14, [(0, '#ffe08a'), (1, '#9a6a14')])); ctx.fill()
        for k in range(3): ctx.rectangle(30 + k*22, 14, 14, 22 + k*6); ctx.fill()
        ctx.restore()

def keys_card(ctx, t, lt_, b, hl=None):
    bgs.paint(ctx, 'card_blue')
    text(ctx, 'ONLY 2 KEYS', W/2, 170, 72, '#ffd23f')
    dur = b['t1'] - b['t0'] if b else 4
    for i, (lab, who) in enumerate((('KEY 1', 'CURATOR'), ('KEY 2', 'WATCHMAN'))):
        x = 620 + i*680; q = prog(lt_, 0.3 + i*dur*0.45, 0.4) if hl is None else 1
        ctx.save(); ctx.translate(x, 520); ctx.scale(back(q) if q < 1 else 1, back(q) if q < 1 else 1); ctx.rotate(-0.3)
        ctx.arc(-150, 0, 70, 0, 2*math.pi); ctx.set_source(lin(ctx, -220, -70, -80, 70, [(0, '#ffe08a'), (1, '#9a6a14')])); ctx.set_line_width(30); ctx.stroke()
        ctx.rectangle(-82, -20, 280, 40); ctx.fill()
        for k in range(3): ctx.rectangle(110 + k*30, 20, 20, 34 + k*8); ctx.fill()
        ctx.restore()
        if q > 0:
            col = '#2ad06a' if hl == i else ('#ffffff' if hl is None else '#8890a8')
            text(ctx, lab, x, 760, 56, col, alpha=q); text(ctx, who, x, 830, 64, col, alpha=q)
            if hl == i: green_box(ctx, x - 300, 330, 600, 560, prog(lt_, 0.3, 0.3))

def sole(ctx, kind, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    def foot():
        ctx.move_to(0, -150); ctx.curve_to(62, -150, 70, -80, 64, -20); ctx.curve_to(60, 30, 48, 60, 44, 100); ctx.curve_to(40, 150, 20, 165, 0, 165)
        ctx.curve_to(-22, 165, -40, 150, -44, 100); ctx.curve_to(-50, 50, -66, 10, -62, -40); ctx.curve_to(-58, -110, -40, -150, 0, -150); ctx.close_path()
    if kind == 'leather':
        ctx.move_to(0, -150); ctx.curve_to(62, -150, 70, -80, 64, -20); ctx.curve_to(60, 20, 48, 40, 38, 56); ctx.line_to(-38, 56); ctx.curve_to(-50, 30, -66, 0, -62, -40); ctx.curve_to(-58, -110, -40, -150, 0, -150); ctx.close_path()
        ctx.set_source(lin(ctx, -60, 0, 60, 0, [(0, '#b08a6a'), (1, '#6a4a34')])); ctx.fill()
        rrect(ctx, -42, 94, 84, 72, 16); ctx.set_source(lin(ctx, -42, 0, 42, 0, [(0, '#8a6a52'), (1, '#4a3424')])); ctx.fill()
    else:
        foot(); ctx.set_source(lin(ctx, -60, 0, 60, 0, [(0, '#3a3a44' if kind == 'boot' else '#6a5a4a' if kind == 'sandal' else '#2a5ac8'), (1, '#1a1a22' if kind == 'boot' else '#4a3a2a' if kind == 'sandal' else '#1a3a8a')])); ctx.fill()
        if kind == 'boot':
            ctx.save(); foot(); ctx.clip()
            for k in range(14):
                yy = -150 + k*24; ctx.move_to(-70, yy)
                for j in range(8): ctx.line_to(-70 + j*20 + 10, yy + (12 if j % 2 == 0 else 0))
            ctx.set_source_rgba(0.75, 0.7, 0.6, 0.9); ctx.set_line_width(5); ctx.stroke(); ctx.restore()
        elif kind == 'chappal':
            for (dx, dy) in ((-8, -105), (-40, 40), (36, 40)): ctx.arc(dx, dy, 9, 0, 2*math.pi); ctx.set_source_rgba(0.9, 0.9, 1, 0.9); ctx.fill()
        elif kind == 'sandal':
            foot(); ctx.set_source_rgba(1, 1, 1, 0.25); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()

SOLES = [('chappal', 'RUBBER CHAPPAL'), ('boot', 'WORK BOOT'), ('sandal', 'FLAT SANDAL'), ('leather', 'LEATHER SHOE')]
def print_card(ctx, t, lt_, mode):
    # wet red-oxide floor close-up with the print
    ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, '#6a2a24'), (1, '#3a120e')])); ctx.paint()
    for k in range(-3, 6): ctx.move_to(k*400, 0); ctx.line_to(k*400 + 200, H); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(4); ctx.stroke()
    for k in range(4): ctx.move_to(0, k*300 + 60); ctx.line_to(W, k*300 + 20); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(4); ctx.stroke()
    for k in range(9):
        ellipse(ctx, 200 + k*200, 300 + 200*math.sin(k), 160, 30); ctx.set_source_rgba(1, 0.9, 0.85, 0.06); ctx.fill()
    glow(ctx, 700, 200, 600, (1, 0.85, 0.7), 0.12)
    if mode in ('q', 'x', 'ans'):
        footprint(ctx, 360, 560, 3.4, 1.0, -0.15)
        text(ctx, 'THE PRINT', 360, 1000, 40, '#ffffff')
        rrect(ctx, 680, 150, 1180, 820, 30); ctx.set_source_rgba(0.04, 0.04, 0.1, 0.8); ctx.fill()
        for i, (k, lab) in enumerate(SOLES):
            x = 830 + i*290; y = 520
            q = prog(lt_, 0.2 + i*0.25, 0.3) if mode == 'q' else 1
            ctx.save(); ctx.translate(x, y); ctx.scale(back(q), back(q)); sole(ctx, k, 0, 0, 1.0); ctx.restore()
            text(ctx, 'ABCD'[i], x, 270, 56, '#ffd23f', alpha=q); text(ctx, lab, x, 790, 26, '#ffffff', alpha=q)
            if mode in ('x', 'ans') and i < 3: xmark(ctx, x, y, 90, prog(lt_, 0.4 + i*1.4, 0.3) if mode == 'x' else 1)
        if mode == 'ans': green_box(ctx, 830 + 3*290 - 130, 220, 260, 620, prog(lt_, 0.2, 0.3))
    else:
        footprint(ctx, W/2, 560, 5.0, 1.0, -0.15)
        if mode in ('cu', 'explain'):
            marker(ctx, W/2 + 260, 330, 1, 'SMOOTH SOLE', prog(lt_, 0.6 if mode == 'cu' else 0.2, 0.3))
        if mode == 'explain':
            marker(ctx, W/2 + 220, 860, 2, 'SEPARATE HEEL', prog(lt_, 2.0, 0.3))

def monitor_card(ctx, t, lt_):
    ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, '#2a2018'), (1, '#120c08')])); ctx.paint()
    glow(ctx, 960, 480, 700, (0.5, 0.7, 1), 0.18)
    ctx.rectangle(0, 860, W, 220); ctx.set_source(lin(ctx, 0, 860, 0, H, [(0, '#6a4a2a'), (1, '#3a2414')])); ctx.fill()
    rrect(ctx, 420, 110, 1080, 700, 30); ctx.set_source(lin(ctx, 0, 110, 0, 810, [(0, '#3a3a44'), (1, '#1a1a20')])); ctx.fill()
    ctx.rectangle(470, 160, 980, 600); ctx.set_source(lin(ctx, 0, 160, 0, 760, [(0, '#3a2a20'), (1, '#20160e')])); ctx.fill()
    ctx.save(); ctx.rectangle(470, 160, 980, 600); ctx.clip()
    for k in range(9): ctx.move_to(470 + k*130, 160); ctx.line_to(470 + k*130 - 60, 760); ctx.set_source_rgba(*hexc('#120a06')); ctx.set_line_width(26); ctx.stroke()
    for y in (300, 520): ctx.move_to(470, y); ctx.line_to(1450, y + 40); ctx.set_source_rgba(*hexc('#120a06')); ctx.set_line_width(20); ctx.stroke()
    for k in range(60): ctx.rectangle(470, 160 + k*10 + (t*40) % 10, 980, 2); ctx.set_source_rgba(1, 1, 1, 0.04); ctx.fill()
    ctx.rectangle(470, 160, 980, 600); ctx.set_source_rgba(0.3, 0.5, 0.4, 0.18); ctx.fill()
    ctx.restore()
    ss = int(12 + lt_) % 60
    text(ctx, 'CAM 03  GALLERY', 500, 210, 30, '#ffffff', align='l')
    text(ctx, f'27/11/2026  22:45:{ss:02d}', 1420, 740, 34, '#ffffff', align='r')
    ctx.arc(1400, 200, 12, 0, 2*math.pi); ctx.set_source_rgba(1, 0.1, 0.1, 0.4 + 0.6*(int(t*2) % 2)); ctx.fill(); text(ctx, 'REC', 1380, 212, 28, '#ff4040', align='r')
    # logbook + tea glass on desk
    ctx.save(); ctx.translate(300, 960); ctx.rotate(-0.08); rrect(ctx, -170, -60, 340, 120, 6); ctx.set_source_rgba(*hexc('#f2ead6')); ctx.fill()
    ctx.move_to(0, -60); ctx.line_to(0, 60); ctx.set_source_rgba(0.5, 0.4, 0.3, 1); ctx.set_line_width(3); ctx.stroke(); ctx.restore()
    ctx.move_to(1560, 900); ctx.line_to(1640, 900); ctx.line_to(1630, 1010); ctx.line_to(1570, 1010); ctx.close_path(); ctx.set_source_rgba(0.85, 0.9, 1, 0.35); ctx.fill()
    ctx.rectangle(1572, 940, 56, 66); ctx.set_source_rgba(*hexc('#a8682a', 0.85)); ctx.fill()

def receipt_card(ctx, t, lt_, mode):
    bgs.paint(ctx, 'card')
    ctx.save(); ctx.translate(W/2, 540); ctx.rotate(-0.03)
    w, h = 520, 900
    ctx.move_to(-w/2, -h/2)
    for k in range(14): ctx.line_to(-w/2 + (k + 0.5)*w/14, -h/2 + (10 if k % 2 == 0 else 0))
    ctx.line_to(w/2, -h/2); ctx.line_to(w/2, h/2)
    for k in range(14): ctx.line_to(w/2 - (k + 0.5)*w/14, h/2 - (10 if k % 2 == 0 else 0))
    ctx.line_to(-w/2, h/2); ctx.close_path()
    ctx.set_source(lin(ctx, -w/2, 0, w/2, 0, [(0, '#fbfaf4'), (1, '#e4e0d4')])); ctx.fill()
    rows = [('BHARAT FUELS', 44, 'c'), ('KAZHAKOOTTAM', 32, 'c'), ('-' * 22, 28, 'c'), ('DATE: 26/11/2026', 36, 'l'), ('TIME: 22:45', 36, 'l'),
            ('PETROL  20.00 L', 32, 'l'), ('AMOUNT  RS 2100.00', 32, 'l'), ('-' * 22, 28, 'c'), ('THANK YOU', 34, 'c'), ('VISIT AGAIN', 28, 'c')]
    y = -h/2 + 110
    for (s, sz, al) in rows:
        text(ctx, s, 0 if al == 'c' else -w/2 + 50, y, sz, '#2a2a2a', align=al); y += sz*1.9
    ctx.restore()
    if mode in ('date', 'stamp'):
        p = prog(lt_, 0.6, 0.6)
        ctx.save(); ctx.translate(W/2 - 50, 540 - 142 - 12); ctx.rotate(-0.03)
        ctx.set_source_rgba(*hexc('#e8283a')); ctx.set_line_width(9); ctx.save(); ctx.scale(1.0, 0.3); ctx.arc(0, 0, 230, -math.pi/2, -math.pi/2 + 2*math.pi*p); ctx.restore(); ctx.stroke(); ctx.restore()
        q = prog(lt_, 1.6, 0.4)
        rrect(ctx, 1330, 380, 470, 200, 20); ctx.set_source_rgba(*hexc('#e8283a', 0.92*q)); ctx.fill()
        text(ctx, 'TODAY IS', 1565, 455, 40, '#ffffff', alpha=q); text(ctx, '27/11/2026', 1565, 535, 60, '#ffffff', alpha=q)
    if mode == 'stamp':
        q = prog(lt_, 0.3, 0.3)
        ctx.save(); ctx.translate(W/2, 640); ctx.rotate(-0.25); sc = 1 + 1.5*(1 - q); ctx.scale(sc, sc)
        rrect(ctx, -330, -80, 660, 160, 20); ctx.set_source_rgba(*hexc('#e8283a', q)); ctx.set_line_width(12); ctx.stroke()
        text(ctx, 'FAKE ALIBI', 0, 36, 100, '#e8283a', alpha=q); ctx.restore()
    if mode == 'cu':
        marker(ctx, W/2 - 330, 540 - 142 - 12, 1, None, prog(lt_, 0.8, 0.3))

def recap_card(ctx, t, lt_, b):
    bgs.paint(ctx, 'card')
    text(ctx, 'THE CLUES', W/2, 150, 70, '#ffd23f')
    dur = b['t1'] - b['t0']
    for i, lab in enumerate(('A KEY', 'LEATHER SHOE + HEEL', 'OVER 6 FT TALL', "YESTERDAY'S RECEIPT")):
        x = 270 + i*460
        q = prog(lt_, 0.2 + i*0.5, 0.35)
        ctx.save(); ctx.translate(x, 540); ctx.scale(back(q), back(q))
        rrect(ctx, -200, -260, 400, 520, 30); ctx.set_source(lin(ctx, 0, -260, 0, 260, [(0, '#24305a'), (1, '#121a36')])); ctx.fill_preserve(); ctx.set_source_rgba(*hexc('#1e6ae8')); ctx.set_line_width(5); ctx.stroke()
        ctx.arc(-150, -210, 30, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#1e6ae8')); ctx.fill(); text(ctx, str(i + 1), -150, -198, 34, '#ffffff')
        if i == 0:
            ctx.save(); ctx.rotate(-0.4); ctx.arc(-70, 0, 40, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#e8b84a')); ctx.set_line_width(18); ctx.stroke(); ctx.rectangle(-30, -12, 140, 24); ctx.fill(); ctx.rectangle(80, 12, 14, 26); ctx.fill(); ctx.restore()
        elif i == 1: sole(ctx, 'leather', 0, -10, 1.05)
        elif i == 2:
            ctx.rectangle(-120, -40, 240, 6); ctx.set_source_rgba(*hexc('#ffd23f')); ctx.fill(); text(ctx, '6 FT', 110, -60, 34, '#ffd23f', align='r')
            human(ctx, 0, 170, 0.3, dict(BLACK, skin='#8a90b0', top_col='#8a90b0', bot_col='#8a90b0', hair='#8a90b0', shirt='#8a90b0', tie='#8a90b0'), dict(arm_r='up'), t, shadow=False)
        else:
            ctx.rectangle(-90, -150, 180, 250); ctx.set_source_rgba(0.97, 0.96, 0.9, 1); ctx.fill()
            text(ctx, '26/11', 0, -40, 50, '#e8283a')
            for k in range(4): ctx.rectangle(-60, 0 + k*22, 120, 6); ctx.set_source_rgba(0.4, 0.4, 0.4, 1); ctx.fill()
        text(ctx, lab, 0, 220, 30 if len(lab) < 16 else 24, '#ffffff')
        ctx.restore()

def end_card(ctx, t, lt_):
    bgs.paint(ctx, 'card_blue')
    human(ctx, 230, 1040, 0.95, ARJUN, dict(face=1, expr='smile', arm_r='wave'), t)
    human(ctx, 1600, 1040, 0.95, MEENU, dict(face=-1, expr='laugh', arm_l='chips', arm_r='eat'), t)
    text(ctx, 'DID YOU CATCH THE CULPRIT?', W/2, 300, 64, '#ffffff', alpha=prog(lt_, 0.1, 0.4))
    text(ctx, 'Comment your answer!', W/2, 400, 56, '#ffd23f', alpha=prog(lt_, 0.6, 0.4))
    q = prog(lt_, 2.5, 0.4); pp = 1 + 0.05*math.sin(t*6)
    ctx.save(); ctx.translate(W/2, 620); ctx.scale(back(q)*pp, back(q)*pp)
    rrect(ctx, -330, -70, 660, 140, 70); ctx.set_source_rgba(*hexc('#e62117')); ctx.fill()
    text(ctx, 'SUBSCRIBE', 0, 22, 66, '#ffffff'); ctx.restore()
    text(ctx, 'for more mysteries!', W/2, 780, 48, '#ffffff', alpha=q)

# ------------------------------------------------------------------ shots
def sub_index(lt_, dur, n_sub): return min(n_sub - 1, int(lt_/(dur/n_sub)))

def store_world(ctx, t, b, who=('A', 'M'), poses=None, web=True):
    bgs.paint(ctx, 'store')
    # padlock on the door frame (open)
    ctx.save(); ctx.translate(370, 560)
    ctx.arc(0, -26, 22, math.pi, 0); ctx.set_source_rgba(*hexc('#b8b8c0')); ctx.set_line_width(8); ctx.stroke()
    rrect(ctx, -30, -26, 60, 56, 8); ctx.set_source(lin(ctx, 0, -26, 0, 30, [(0, '#f0c860'), (1, '#9a7020')])); ctx.fill(); ctx.restore()
    # aluminium ladder leaning on the wall with dust + an unbroken cobweb
    lx0, lx1 = 560, 720
    for x0, x1 in ((lx0, lx0 + 60), (lx1, lx1 - 60)):
        ctx.move_to(x0, 980); ctx.line_to(x1, 300); ctx.set_source(lin(ctx, x0 - 10, 0, x0 + 10, 0, [(0, '#e8eaf0'), (1, '#8a8e9a')])); ctx.set_line_width(20); ctx.stroke()
    for k in range(1, 10):
        f = k/10; y = 980 - 680*f; xa = lx0 + 60*f; xb = lx1 - 60*f
        ctx.move_to(xa, y); ctx.line_to(xb, y); ctx.set_source_rgba(*hexc('#b8bcc8')); ctx.set_line_width(11); ctx.stroke()
        ctx.move_to(xa, y - 5); ctx.line_to(xb, y - 5); ctx.set_source_rgba(0.75, 0.7, 0.6, 0.7); ctx.set_line_width(3); ctx.stroke()  # dust
    if web:
        cx, cy = 640, 640; ctx.set_source_rgba(1, 1, 1, 0.55); ctx.set_line_width(1.4)
        pts = [(lx0 + 60*((980-560)/680) + 6, 560), (lx1 - 60*((980-560)/680) - 6, 560), (lx1 - 60*((980-700)/680) - 6, 700), (lx0 + 60*((980-700)/680) + 6, 700)]
        for (px, py) in pts: ctx.move_to(cx, cy); ctx.line_to(px, py)
        for k in range(1, 7):
            f = k/7; ctx.move_to(cx + (pts[0][0]-cx)*f, cy + (pts[0][1]-cy)*f)
            for (px, py) in pts[1:] + pts[:1]: ctx.line_to(cx + (px-cx)*f, cy + (py-cy)*f)
        ctx.stroke()
        ctx.arc(cx + 10, cy - 30, 5, 0, 2*math.pi); ctx.set_source_rgba(0.1, 0.1, 0.1, 1); ctx.fill()
    poses = poses or {}
    for k, x, spec in (('M', 1180, MEENU), ('A', 980, ARJUN)):
        if k not in who: continue
        po = dict(face=-1, expr='neutral'); po.update(poses.get(k, {})); po['talk'] = talk_of(b, k, t)
        human(ctx, x, 1000, 0.66, spec, po, t)

LX = {'V': 330, 'S': 750, 'F': 1170, 'R': 1590}
LSPEC = {'V': VELU, 'S': SHANTHA, 'F': FAIZAL, 'R': RAVI}
LLAB = {'V': ('VELAYUDHAN', 'WATCHMAN', "5'5\""), 'S': ('SHANTHA', 'CLEANER', "5'0\""), 'F': ('FAIZAL', 'ELECTRICIAN', "5'8\""), 'R': ('DR. RAVI MENON', 'CURATOR', "6'1\"")}
def lineup_world(ctx, t, b, focus=None, poses=None, labels=True, hl6=False):
    bgs.paint(ctx, 'lineup')
    ft = 900*bgs.LINE_S/6.0
    for k in range(4, 8): text(ctx, f'{k} FT', 70, bgs.LINE_FLOOR - k*ft - 10, 26, '#ffffff', align='l', alpha=0.7)
    if hl6:
        y = bgs.LINE_FLOOR - 6*ft; ctx.rectangle(0, y - 5, W, 10); ctx.set_source_rgba(*hexc('#ffd23f', 0.6 + 0.4*math.sin(t*5))); ctx.fill()
    poses = poses or {}
    for k in ('V', 'S', 'F', 'R'):
        x = LX[k]
        po = dict(face=1 if x < 960 else -1, expr='neutral'); po.update(poses.get(k, {})); po['talk'] = talk_of(b, k, t)
        if focus and k != focus:
            ctx.push_group(); human(ctx, x, bgs.LINE_FLOOR, bgs.LINE_S, LSPEC[k], po, t); ctx.pop_group_to_source(); ctx.paint_with_alpha(0.55)
        else:
            if focus: glow(ctx, x, 600, 300, (1, 0.95, 0.75), 0.2)
            human(ctx, x, bgs.LINE_FLOOR, bgs.LINE_S, LSPEC[k], po, t)
        if labels:
            nm, role, ht = LLAB[k]
            rrect(ctx, x - 175, bgs.LINE_FLOOR + 14, 350, 62, 12); ctx.set_source_rgba(0.03, 0.03, 0.08, 0.9); ctx.fill()
            text(ctx, f'{role}', x, bgs.LINE_FLOOR + 56, 32, '#ffd23f')

def lineup_head_cam(k, z=2.6):
    g = geo(LSPEC[k]); return (LX[k], bgs.LINE_FLOOR + g['hc']*bgs.LINE_S + 80, z)

def parking_world(ctx, t, b, mode):
    bgs.paint(ctx, 'parking')
    # car (maroon sedan, side view, boot open toward camera-right)
    cx, cy = 700, 900
    ctx.move_to(cx - 420, cy); ctx.line_to(cx - 400, cy - 120); ctx.curve_to(cx - 300, cy - 140, cx - 250, cy - 150, cx - 200, cy - 230); ctx.line_to(cx + 120, cy - 230)
    ctx.curve_to(cx + 180, cy - 170, cx + 230, cy - 140, cx + 380, cy - 130); ctx.line_to(cx + 420, cy - 60); ctx.line_to(cx + 420, cy); ctx.close_path()
    ctx.set_source(lin(ctx, 0, cy - 230, 0, cy, [(0, '#9a2a34'), (0.6, '#6a1420'), (1, '#3a0a10')])); ctx.fill_preserve(); outline(ctx, 3, 0.6)
    ctx.move_to(cx - 190, cy - 215); ctx.line_to(cx - 20, cy - 215); ctx.line_to(cx - 20, cy - 145); ctx.line_to(cx - 260, cy - 145); ctx.close_path()
    ctx.move_to(cx, cy - 215); ctx.line_to(cx + 110, cy - 215); ctx.line_to(cx + 165, cy - 145); ctx.line_to(cx, cy - 145); ctx.close_path()
    ctx.set_source(lin(ctx, 0, cy - 215, 0, cy - 145, [(0, '#8aa0c8'), (1, '#2a3450')])); ctx.fill()
    for wx in (cx - 250, cx + 250):
        ctx.arc(wx, cy, 68, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#121216')); ctx.fill(); ctx.arc(wx, cy, 34, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#9a9aa8')); ctx.fill()
    ctx.rectangle(cx + 395, cy - 110, 22, 30); ctx.set_source_rgba(1, 0.2, 0.2, 1); ctx.fill()
    # open boot lid
    ctx.move_to(cx + 260, cy - 135); ctx.line_to(cx + 400, cy - 300); ctx.line_to(cx + 440, cy - 280); ctx.line_to(cx + 380, cy - 130); ctx.close_path()
    ctx.set_source_rgba(*hexc('#5a1018')); ctx.fill_preserve(); outline(ctx, 2, 0.6)
    ctx.rectangle(cx + 250, cy - 135, 150, 40); ctx.set_source_rgba(*hexc('#140608')); ctx.fill()
    glow(ctx, cx + 330, cy - 120, 140, (1, 0.85, 0.5), 0.35)
    ctx.move_to(cx + 240, cy - 120); ctx.curve_to(cx + 300, cy - 160, cx + 380, cy - 150, cx + 420, cy - 110); ctx.line_to(cx + 410, cy - 95); ctx.line_to(cx + 250, cy - 95); ctx.close_path()
    ctx.set_source(lin(ctx, 0, cy - 160, 0, cy - 95, [(0, '#d8283a'), (1, '#7a0a18')])); ctx.fill()
    sword(ctx, cx + 265, cy - 125, 0.75, -0.05, glint=t*0.6)
    # police jeep at right
    jx, jy = 1480, 930
    rrect(ctx, jx - 260, jy - 240, 520, 200, 20); ctx.set_source(lin(ctx, 0, jy - 240, 0, jy - 40, [(0, '#f4f4f8'), (1, '#a8acb8')])); ctx.fill()
    ctx.rectangle(jx - 260, jy - 120, 520, 50); ctx.set_source_rgba(*hexc('#1a3a8a')); ctx.fill()
    text(ctx, 'POLICE', jx, jy - 82, 40, '#ffffff')
    ctx.rectangle(jx - 210, jy - 220, 160, 80); ctx.rectangle(jx - 20, jy - 220, 160, 80); ctx.set_source_rgba(*hexc('#3a4a6a')); ctx.fill()
    for wx in (jx - 170, jx + 170):
        ctx.arc(wx, jy - 30, 55, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#121216')); ctx.fill(); ctx.arc(wx, jy - 30, 26, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#9a9aa8')); ctx.fill()
    on = int(t*4) % 2
    rrect(ctx, jx - 70, jy - 270, 140, 32, 8); ctx.set_source_rgba(0.2, 0.2, 0.25, 1); ctx.fill()
    ctx.rectangle(jx - 64, jy - 266, 62, 24); ctx.set_source_rgba(1, 0.1, 0.1, 1 if on else 0.3); ctx.fill()
    ctx.rectangle(jx + 2, jy - 266, 62, 24); ctx.set_source_rgba(0.2, 0.4, 1, 0.3 if on else 1); ctx.fill()
    glow(ctx, jx - 33 if on else jx + 33, jy - 254, 520, (1, 0.1, 0.1) if on else (0.2, 0.4, 1), 0.28)
    # people
    walk = 0.0; rx_ = 1170
    if mode == 'away':
        p = prog(t - b['t0'], 0.2, 4.0); rx_ = lerp(1080, 1300, p); walk = 0.6 if p < 1 else 0
    human(ctx, rx_ - 170 if mode == 'away' else 1240, 1050, 0.62, POLICE, dict(face=1 if mode == 'away' else -1, walk=walk, expr='neutral'), t)
    human(ctx, rx_ if mode == 'away' else 1080, 1050, 0.62, RAVI, dict(face=1 if mode == 'away' else -1, expr='sad', arm_l='cuffed', arm_r='cuffed', walk=walk, tilt=0.12, look=(0, 0.8), talk=talk_of(b, 'R', t)), t)
    if mode != 'away':
        human(ctx, 230, 1060, 0.62, ARJUN, dict(face=1, expr='neutral', arm_l='hip'), t)

def gal(b, t, lt_, **kw):
    return lambda ctx: gallery_world(ctx, t, b, **kw)

def shot(name, b, t, lt_, dur):
    """returns (draw_fn(ctx), camera list) ; camera None = screen-space card."""
    sec = b['sec']; meet = dict(who=('A', 'M', 'R', 'V'))
    inv_pos = {'A': 760, 'M': 540}
    pose_meet = {'A': dict(arm_l='notebook', arm_r='write' if b['spk'] != 'A' else 'down', expr='think' if b['spk'] != 'A' else 'neutral'),
                 'M': dict(arm_l='chips', arm_r='eat' if b.get('meenu_eat') else 'down', expr='smile' if b['spk'] == 'M' else 'neutral'),
                 'R': dict(expr='sad' if b['spk'] == 'R' else 'neutral', arm_r='hip'), 'V': dict(expr='scared', arm_l='hold', hold_prop='torch')}
    inv_pose = {'A': dict(arm_l='notebook', arm_r='chin' if b['spk'] != 'A' else 'write', expr='think'),
                'M': dict(arm_l='chips', arm_r='eat' if b.get('meenu_eat') else 'down', expr='shock' if 'magic' in b['ml'] else 'smile')}
    fw = (960, 540, 1.0)
    # ----- exterior
    if name.startswith('ext'):
        def d(ctx):
            bgs.paint(ctx, 'ext'); text(ctx, 'PALACE MUSEUM', 1310, 928, 36, '#f0d070')
            if name in ('ext_arrive', 'ext_arrive_two') or sec == 'intro' and b['spk'] == 'M':
                p = clamp((t - SEC_START['intro'] - (b['t0'] - SEC_START['intro']))/4.0)
                bx = lerp(260, 560, p) if name == 'ext_arrive' else 560
                human(ctx, bx, 1050, 0.42, ARJUN, dict(face=1, walk=0.6 if (name == 'ext_arrive' and p < 1) else 0, expr='neutral', talk=talk_of(b, 'A', t)), t)
                human(ctx, bx - 120, 1055, 0.42, MEENU, dict(face=1, walk=0.6 if (name == 'ext_arrive' and p < 1) else 0, expr='scared' if b['spk'] == 'M' else 'smile',
                                                          arm_l='chips', arm_r='eat', talk=talk_of(b, 'M', t)), t)
        cams = {'ext_wide': [(960, 540, 1.0)], 'ext_moon': [(1450, 260, 2.2)], 'ext_gate': [(1310, 860, 2.4), (960, 600, 1.4)],
                'ext_arrive': [(700, 760, 1.5)], 'ext_arrive_two': [(490, 900, 2.6), (700, 760, 1.5)]}[name]
        return d, cams
    # ----- gallery
    if name.startswith('gal_dark') or name in ('gal_alarm', 'gal_alarm_case', 'gal_torch_run', 'gal_torch_face', 'gal_empty_case', 'gal_torch_shock'):
        pre = name.startswith('gal_dark')
        def d(ctx):
            gallery_world(ctx, t, b, lit=False, who=(), has_sword=pre, alarm=name.startswith('gal_alarm'))
            if name.startswith('gal_torch') or name == 'gal_empty_case':
                p = prog(t - b['t0'], 0, 1.6) if name == 'gal_torch_run' else 1
                vx = lerp(1850, 1330, p)
                ctx.move_to(vx - 120, 690); ctx.line_to(1000, 560); ctx.line_to(1000, 820); ctx.close_path()
                ctx.set_source(lin(ctx, vx, 0, 1000, 0, [(0, (1, 0.95, 0.7, 0.5)), (1, (1, 0.95, 0.7, 0.12))])); ctx.fill()
                human(ctx, vx, FLOOR, SW, VELU, dict(face=-1, arm_r='torch', arm_l='down', walk=0.8 if p < 1 else 0, expr='shock' if name in ('gal_torch_shock', 'gal_empty_case') else 'scared'), t)
                glow(ctx, 960, 680, 160, (1, 0.95, 0.7), 0.3)
        cams = {'gal_dark_wide': [(960, 540, 1.0)], 'gal_dark_pillars': [(560, 420, 1.7)], 'gal_dark_portrait': [(1215, 340, 2.6), (960, 680, 2.4)],
                'gal_alarm': [(960, 560, 1.15)], 'gal_alarm_case': [(960, 680, 2.6)], 'gal_torch_run': [(1250, 600, 1.4)],
                'gal_torch_face': [face_cam('V', 1330, 3.0)], 'gal_empty_case': [(960, 690, 3.2), (1100, 640, 1.8)], 'gal_torch_shock': [face_cam('V', 1330, 3.2)]}[name]
        return d, cams
    if name in ('gal_meet_wide', 'gal_meet_two', 'gal_empty_case_lit', 'ravi_cu', 'velu_cu', 'point_wide', 'ravi_shock', 'ravi_down') or (sec == 'intro' and name in ('arjun_cu', 'arjun_note', 'arjun_stroke', 'meenu_cu', 'meenu_chips')) or (sec == 'rev' and name in ('arjun_cu',)):
        po = {k: dict(v) for k, v in pose_meet.items()}
        if name == 'arjun_stroke': po['A'] = dict(arm_l='hip', arm_r='chin', expr='think')
        if name == 'arjun_note': po['A'] = dict(arm_l='notebook', arm_r='write', expr='think')
        if sec == 'rev':
            po['A'] = dict(arm_r='point', arm_l='hip', expr='smug' if b['spk'] == 'A' else 'neutral'); po['R'] = dict(expr='shock' if name != 'ravi_down' else 'sad', arm_l='up' if name == 'ravi_shock' else 'down', arm_r='down', tilt=0.15 if name == 'ravi_down' else 0, look=(0, 0.9) if name == 'ravi_down' else (-0.35, 0))
            po['M'] = dict(expr='shock', arm_l='chips', arm_r='down'); po['V'] = dict(expr='shock', arm_l='hold', hold_prop='torch')
        def d(ctx): gallery_world(ctx, t, b, lit=True, who=('A', 'M', 'R', 'V'), poses=po)
        cams = {'gal_meet_wide': [(960, 560, 1.0), (960, 620, 1.3)], 'gal_meet_two': [(1000, 640, 1.6), (520, 640, 1.8)], 'gal_empty_case_lit': [(960, 680, 2.6)],
                'ravi_cu': [face_cam('R', 1290, 3.0), face_cam('R', 1290, 2.2)], 'velu_cu': [face_cam('V', 1490, 3.0), face_cam('V', 1490, 2.2)],
                'arjun_cu': [face_cam('A', 690, 3.0), face_cam('A', 690, 2.3)], 'arjun_note': [face_cam('A', 690, 2.2)], 'arjun_stroke': [face_cam('A', 690, 3.1)],
                'meenu_cu': [face_cam('M', 470, 3.0), face_cam('M', 470, 2.3)], 'meenu_chips': [face_cam('M', 470, 2.4)],
                'point_wide': [(960, 600, 1.05), (1000, 560, 1.5)], 'ravi_shock': [face_cam('R', 1290, 3.2)], 'ravi_down': [face_cam('R', 1290, 2.8)]}[name]
        return d, cams
    if name in ('gal_lit_wide', 'gal_lit_walk', 'arjun_case', 'arjun_cu', 'arjun_stroke', 'arjun_note', 'meenu_cu', 'meenu_chips', 'meenu_note', 'two_case',
                                                             'gal_lit_floor', 'wet_sign', 'arjun_look_up', 'cam_wide', 'cam_cu', 'cam_measure', 'two_cam', 'reach_demo', 'flash_mop', 'flash_mop_cu',
                                                             'sword_back', 'sword_back_cu', 'end_two', 'arjun_smile'):
        po = {k: dict(v) for k, v in inv_pose.items()}; pos = dict(inv_pos); who = ['A', 'M']; extra = ()
        if sec == 'c2' or name in ('wet_sign', 'gal_lit_floor'): extra = ('wet', 'print')
        if name == 'arjun_stroke': po['A'] = dict(arm_l='hip', arm_r='chin', expr='think')
        if name == 'meenu_note': po['M'] = dict(arm_l='notebook', arm_r='write', expr='smile')
        if name == 'gal_lit_walk':
            p = prog(t - b['t0'], 0.2, 2.5); pos['A'] = lerp(640, 760, p); po['A'] = dict(walk=0.6 if p < 1 else 0, expr='think')
        if name == 'gal_lit_floor': po['A'] = dict(arm_l='hip', arm_r='chin', expr='think', look=(0.3, 1.0), tilt=0.12)
        if name in ('arjun_look_up', 'cam_wide', 'two_cam', 'cam_measure'): po['A'] = dict(arm_l='hip', arm_r='chin', expr='think', look=(0.5, -1.0), tilt=-0.15); po['M']['look'] = (0.5, -1.0)
        if sec == 'c3' and b['spk'] == 'V': who.append('V')
        if name in ('end_two', 'arjun_smile', 'sword_back', 'sword_back_cu'):
            po['A'] = dict(arm_l='hip', arm_r='down', expr='smile' if name != 'arjun_smile' else 'laugh'); po['M'] = dict(arm_l='chips', arm_r='eat', expr='laugh')
        flash = name.startswith('flash')
        if flash: who = ['S']; pos = {'S': 1180 + 60*math.sin(t*1.5)}; po = {'S': dict(face=-1, arm_r='mop', arm_l='down', expr='neutral')}
        reach = name == 'reach_demo'
        def d(ctx):
            gallery_world(ctx, t, b, lit=True, who=tuple(who) if not reach else ('A', 'M'), has_sword=name.startswith('sword_back') or name in ('end_two', 'arjun_smile'), poses=po, pos=pos, extra=extra)
            if flash:
                ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(0.55, 0.4, 0.2, 0.35); ctx.fill()
            if name == 'cam_measure' or reach:
                x = 1560; ctx.set_source_rgba(*hexc('#ffd23f')); ctx.set_line_width(6); ctx.set_dash([18, 12]); ctx.move_to(x, FLOOR); ctx.line_to(x, 250); ctx.stroke(); ctx.set_dash([])
                for yy in (FLOOR, 250): ctx.move_to(x - 25, yy); ctx.line_to(x + 25, yy); ctx.stroke()
                rrect(ctx, x - 180, 560, 150, 70, 12); ctx.set_source_rgba(0.04, 0.04, 0.1, 0.9); ctx.fill(); text(ctx, '8 FT', x - 105, 610, 44, '#ffd23f')
            if reach:
                human(ctx, 1660, FLOOR, SW, BLACK, dict(face=1, arm_r='up', arm_l='down'), t)
                text(ctx, '?', 1640, 400, 90, '#ffd23f')
            if name == 'cam_cu' and b.get('markers') == 'cam':
                marker(ctx, 1620, 200, 1, 'TURNED UP', prog(t - b['t0'], 1.5, 0.3), side=-1)
        cams = {'gal_lit_wide': [(960, 560, 1.0), (900, 640, 1.35)], 'gal_lit_walk': [(860, 640, 1.5)], 'arjun_case': [(860, 600, 1.9), face_cam('A', 760, 2.6)],
                'arjun_cu': [face_cam('A', 760, 3.0), face_cam('A', 760, 2.3)], 'arjun_stroke': [face_cam('A', 760, 3.1)], 'arjun_note': [face_cam('A', 760, 2.3)],
                'meenu_cu': [face_cam('M', 540, 3.0), face_cam('M', 540, 2.3)], 'meenu_chips': [face_cam('M', 540, 2.4)], 'meenu_note': [face_cam('M', 540, 2.3)],
                'two_case': [(780, 640, 1.6)], 'gal_lit_floor': [(1000, 860, 2.0)], 'wet_sign': [(1150, 900, 3.0)], 'arjun_look_up': [face_cam('A', 760, 2.6)],
                'cam_wide': [(1400, 450, 1.6)], 'cam_cu': [(1690, 260, 4.2), (1650, 300, 3.0)], 'cam_measure': [(1500, 600, 1.5)], 'two_cam': [(900, 560, 1.3)],
                'reach_demo': [(1500, 600, 1.45)], 'flash_mop': [(1150, 700, 1.5)], 'flash_mop_cu': [face_cam('S', 1180, 2.6) if False else (1180, 760, 2.4)],
                'sword_back': [(960, 600, 1.4)], 'sword_back_cu': [(960, 690, 3.4)], 'end_two': [(700, 640, 1.6)], 'arjun_smile': [face_cam('A', 760, 3.0)]}[name]
        return d, cams
    # ----- store
    if name in ('store_door', 'store_wide', 'ladder_cu', 'web_cu', 'two_store', 'store_arjun'):
        po = {'A': dict(arm_l='notebook', arm_r='chin', expr='think'), 'M': dict(arm_l='chips', arm_r='eat', expr='smile')}
        def d(ctx):
            store_world(ctx, t, b, poses=po)
            if name == 'web_cu':
                marker(ctx, 720, 600, 1, 'UNBROKEN WEB', prog(t - b['t0'], 0.6, 0.3)); marker(ctx, 720, 700, 2, 'DUST, NO HANDPRINTS', prog(t - b['t0'], 2.6, 0.3))
            if name == 'ladder_cu': marker(ctx, 760, 520, 1, None, prog(t - b['t0'], 1.0, 0.3))
        cams = {'store_door': [(330, 560, 2.4)], 'store_wide': [(960, 560, 1.0), (800, 600, 1.4)], 'ladder_cu': [(660, 620, 2.4)], 'web_cu': [(680, 640, 3.6)],
                'two_store': [(1080, 640, 1.6)], 'store_arjun': [(980, 1000 + geo(ARJUN)['hc']*0.66 + 60, 2.6), (980, 1000 + geo(ARJUN)['hc']*0.66 + 120, 2.0)]}[name]
        return d, cams
    # ----- line-up
    if name.startswith('lineup') or name.startswith('sus_') or name in ('hand_receipt', 'who_card', 'replay_shoes', 'replay_height'):
        po = {}
        foc = b.get('focus')
        if name == 'hand_receipt' or (foc == 'R'): po['R'] = dict(arm_r='give' if name != 'sus_r' or t - b['t0'] > b['d']*0.6 else 'hip', give_prop='receipt', expr='smug')
        if foc == 'V': po['V'] = dict(expr='scared')
        if foc == 'S': po['S'] = dict(expr='neutral', arm_l='down')
        if foc == 'F': po['F'] = dict(expr='neutral', arm_l='hip')
        if name == 'replay_height': po['R'] = dict(expr='scared')
        if name == 'hand_receipt': po['R'] = dict(arm_l='give', give_prop='receipt', expr='smug', face=-1)
        def d(ctx):
            lineup_world(ctx, t, b, focus=foc if name.startswith('sus_') else ('R' if name == 'replay_height' else None), poses=po, hl6=(name == 'replay_height'))
            if name == 'replay_shoes':
                for i, k in enumerate(('V', 'S', 'F')): xmark(ctx, LX[k], bgs.LINE_FLOOR - 30, 60, prog(t - b['t0'], 1.5 + i*1.6, 0.3))
                green_box(ctx, LX['R'] - 120, bgs.LINE_FLOOR - 110, 240, 150, prog(t - b['t0'], b['d']*0.8, 0.3))
            if name == 'replay_height':
                text(ctx, "6'1\"", LX['R'] + 160, 260, 50, '#2ad06a')
        cams = {'lineup_wide': [(960, 560, 1.0)], 'lineup_pan': [(500, 600, 1.6), (1400, 600, 1.6)],
                'sus_v': [lineup_head_cam('V', 2.4), lineup_head_cam('V', 1.6)], 'sus_s': [lineup_head_cam('S', 2.4), lineup_head_cam('S', 1.6)],
                'sus_f': [lineup_head_cam('F', 2.4), lineup_head_cam('F', 1.6)], 'sus_r': [lineup_head_cam('R', 2.4), lineup_head_cam('R', 1.6)],
                'sus_v_feet': [(LX['V'], 960, 3.0)], 'sus_s_feet': [(LX['S'], 960, 3.0)], 'sus_f_feet': [(LX['F'], 960, 3.0)], 'sus_r_feet': [(LX['R'], 960, 3.0)],
                'hand_receipt': [(1450, 560, 2.0)], 'who_card': [(960, 560, 1.0)], 'replay_shoes': [(960, 960, 1.7)], 'replay_height': [(1300, 520, 1.3)]}[name]
        return d, cams
    if name in ('car_wide', 'car_boot', 'ravi_sad_cu', 'police_away'):
        mode = 'away' if name == 'police_away' else 'stand'
        def d(ctx): parking_world(ctx, t, b, mode)
        g = geo(RAVI)
        cams = {'car_wide': [(960, 600, 1.0)], 'car_boot': [(1030, 790, 3.2)], 'ravi_sad_cu': [(1080, 1050 + g['hc']*0.62 + 40, 3.0)], 'police_away': [(1150, 700, 1.4)]}[name]
        return d, cams
    # ----- screen-space inserts
    cards = {
        'title': lambda ctx: title_card(ctx, t, lt_), 'timeline': lambda ctx: timeline_card(ctx, t, lt_),
        'four_sil': lambda ctx: four_card(ctx, t, lt_, b, False), 'four_reveal': lambda ctx: four_card(ctx, t, lt_, b, True),
        'case_cu': lambda ctx: gallery_world(ctx, t, b, lit=True, who=()), 'lock_cu': lambda ctx: lock_card(ctx, t, lt_, 'cu'),
        'lock_cu_mag': lambda ctx: lock_card(ctx, t, lt_, 'mag'), 'q_lock': lambda ctx: lock_card(ctx, t, lt_, 'plain'), 'lock_key': lambda ctx: lock_card(ctx, t, lt_, 'key'),
        'keys_card': lambda ctx: keys_card(ctx, t, lt_, b), 'replay_key': lambda ctx: keys_card(ctx, t, lt_, None, hl=0),
        'print_cu': lambda ctx: print_card(ctx, t, lt_, 'cu'), 'q_print': lambda ctx: print_card(ctx, t, lt_, 'q'), 'print_explain': lambda ctx: print_card(ctx, t, lt_, 'explain'),
        'soles_x': lambda ctx: print_card(ctx, t, lt_, 'x'), 'soles_ans': lambda ctx: print_card(ctx, t, lt_, 'ans'),
        'monitor': lambda ctx: monitor_card(ctx, t, lt_), 'q_ladder': lambda ctx: store_world(ctx, t, b, who=()),
        'receipt_cu': lambda ctx: receipt_card(ctx, t, lt_, 'cu'), 'q_receipt': lambda ctx: receipt_card(ctx, t, lt_, 'plain'),
        'receipt_date': lambda ctx: receipt_card(ctx, t, lt_, 'date'), 'replay_receipt': lambda ctx: receipt_card(ctx, t, lt_, 'stamp'),
        'recap': lambda ctx: recap_card(ctx, t, lt_, b), 'end_card': lambda ctx: end_card(ctx, t, lt_),
    }
    camz = {'case_cu': [(960, 680, 2.8)], 'q_ladder': [(660, 640, 2.6)]}
    return cards[name], camz.get(name)

# ------------------------------------------------------------------ overlays
BADGE = {'c1': 'CLUE 1/4', 'c2': 'CLUE 2/4', 'c3': 'CLUE 3/4', 'sus': 'SUSPECTS', 'c4': 'CLUE 4/4', 'who': 'WHO DID IT?', 'rev': 'THE REVEAL'}
def overlays(ctx, t, b):
    sec = b['sec']
    if sec in BADGE and sec != 'intro':
        q = prog(t, SEC_START[sec] + 0.3, 0.4)
        lab = BADGE[sec]; w = text_w(ctx, lab, 30) + 50
        rrect(ctx, 40, 40, w, 58, 14); ctx.set_source_rgba(0.03, 0.06, 0.18, 0.82*q); ctx.fill()
        rrect(ctx, 40, 40, 10, 58, 4); ctx.set_source_rgba(*hexc('#ffd23f', q)); ctx.fill()
        text(ctx, lab, 40 + w/2 + 5, 80, 30, '#ffffff', alpha=q)
    if b.get('card') and t >= b['t0']:
        q = prog(t, b['t0'] + 0.1, 0.35)
        lab = b['card']; w = text_w(ctx, lab, 58) + 80
        ctx.save(); ctx.translate(W/2, 170 if b.get('timer') else 140); ctx.scale(back(q), back(q))
        rrect(ctx, -w/2, -55, w, 110, 22); ctx.set_source_rgba(0.02, 0.02, 0.06, 0.88); ctx.fill()
        text(ctx, lab, 0, 22, 58, '#ffd23f'); ctx.restore()
    if b.get('timer') and t >= b['tt0'] - 0.25:
        p = clamp((t - b['tt0'])/(b['tt1'] - b['tt0']))
        ctx.rectangle(0, 0, W, 18); ctx.set_source_rgba(0, 0, 0, 0.6); ctx.fill()
        ctx.rectangle(0, 0, W*p, 18); ctx.set_source_rgba(*hexc('#ffd23f')); ctx.fill()
        q = prog(t, b['tt0'] - 0.25, 0.3)
        ctx.save(); ctx.translate(W/2, H - 110); ctx.scale(back(q), back(q))
        rrect(ctx, -360, -48, 720, 96, 48); ctx.set_source_rgba(0.9, 0.12, 0.1, 0.92); ctx.fill()
        for dx in (-300, -278): ctx.rectangle(dx, -20, 12, 40); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        text(ctx, 'PAUSE THE VIDEO AND THINK', 22, 15, 38, '#ffffff'); ctx.restore()
    if b.get('ans'):
        q = prog(t, b['t0'] + b['d']*0.45, 0.35)
        if q > 0:
            lab = b['ans']; w = text_w(ctx, lab, 52) + 90
            ctx.save(); ctx.translate(W/2, H - 120); ctx.scale(back(q), back(q))
            rrect(ctx, -w/2, -52, w, 104, 22); ctx.set_source_rgba(0.04, 0.24, 0.12, 0.92); ctx.fill()
            ctx.set_source_rgba(*hexc('#2ad06a')); ctx.set_line_width(7); rrect(ctx, -w/2, -52, w, 104, 22); ctx.stroke()
            text(ctx, lab, 0, 18, 52, '#ffffff'); ctx.restore()
    if b['id'] == B[-1]['id'] or b['sec'] == 'who' and b.get('timer'):
        pass

# ------------------------------------------------------------------ frame draw
def beat_at(t):
    i = 0
    for j, b in enumerate(B):
        if t >= b['t0'] - 0.05: i = j
    return i

def plan(b):
    """shot boundaries inside a beat: [(name, s0, s1, n_sub)]"""
    s0 = b['t0'] - (0.05 if b is not B[0] else b['t0']); s1 = b['end']
    n = len(b['shots']); seg = (s1 - s0)/n; out = []
    for k, nm in enumerate(b['shots']):
        a = s0 + k*seg; dur = seg
        out.append((nm, a, a + seg, max(1, int(dur/2.1))))
    return out

def draw_frame(ctx, t, bi=None):
    i = beat_at(t) if bi is None else bi
    b = B[i]
    for (nm, a, z, nsub) in plan(b):
        if a <= t < z or (nm, a, z, nsub) == plan(b)[-1]: break
    lt_ = t - a; dur = z - a
    k = sub_index(lt_, dur, nsub); sd = dur/nsub; slt = lt_ - k*sd
    fn, cams = shot(nm, b, t, lt_, dur)
    ctx.save()
    if cams:
        c = cams[k % len(cams)]
        p = clamp(slt/sd)
        drift = ((-1)**(k + i))*14
        cx, cy, z_ = kb(c, p, (drift, 0, 0.05))
        cam(ctx, cx, cy, z_)
    else:
        s = 1 + 0.035*clamp(lt_/max(dur, 0.1)); ctx.translate(W/2, H/2); ctx.scale(s, s); ctx.translate(-W/2, -H/2)
    fn(ctx)
    ctx.restore()
    overlays(ctx, t, b)

def frame(ctx, t):
    i = beat_at(t); b = B[i]
    draw_frame(ctx, t, i)
    # cross-dissolve at section starts
    if i > 0 and B[i-1]['sec'] != b['sec'] and t < b['t0'] + 0.45 and t >= b['t0'] - 0.05:
        a = 1 - clamp((t - b['t0'] + 0.05)/0.5)
        ctx.push_group(); draw_frame(ctx, min(t, B[i-1]['end'] - 0.01), i - 1); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    # vignette + subtle film grain line
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 500, 1150, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.35))])); ctx.fill()
    # fade in / out
    if t < 0.6: ctx.set_source_rgba(0, 0, 0, 1 - t/0.6); ctx.paint()
    if t > TOTAL - 0.8: ctx.set_source_rgba(0, 0, 0, clamp((t - (TOTAL - 0.8))/0.8)); ctx.paint()

# ------------------------------------------------------------------ audio
def alarm(dur=2.2):
    n = int(dur*SR); tt = np.arange(n)/SR
    f = np.where((tt*2.5) % 1 < 0.5, 880, 660)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*0.25*np.minimum(1, (dur - tt)*3)
def sting():
    out = np.zeros(int(2.2*SR))
    for f in (146.8, 174.6, 220.0, 293.7): A.add(out, A.pluck(f, 2.0, dec=1.2)*0.5, 0)
    A.add(out, A.bell(587.3, 1.8, 2.0)*0.3, int(0.05*SR))
    n = int(1.0*SR); tt = np.arange(n)/SR; A.add(out, A.lp(np.random.default_rng(1).standard_normal(n), 200)*np.exp(-tt*4)*0.8, 0)
    return out
def softtick():
    n = int(0.05*SR); tt = np.arange(n)/SR; return np.sin(2*np.pi*1500*tt)*np.exp(-tt*90)*0.35

def mystery_bed(dur):
    n = int(dur*SR); y = np.zeros(n)
    # D minor pizzicato ostinato + soft piano-like bells + pad
    prog_ = [(50, [62, 65, 69]), (46, [62, 65, 70]), (48, [60, 64, 67]), (45, [61, 64, 69])]
    pat = [0, 2, 1, 2, 0, 2, 1, 2]
    step = 0.42; k = 0
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
            pd = A.pad([A.mtof(c - 12) for c in ch], 16*step + 0.6)*0.18
            A.add(y, pd, int(st*SR))
    return y

def build_audio(path):
    n = int((TOTAL + 1)*SR); v = np.zeros(n); fx = np.zeros(n)
    for b in B:
        y, sr = sf.read(b['wav']); y = y if y.ndim == 1 else y.mean(1); A.add(v, y, int(b['t0']*SR))
    for i, b in enumerate(B):
        if i and B[i-1]['sec'] != b['sec']: A.add(fx, sfx2('whoosh')*0.45, int((b['t0'] - 0.25)*SR))
        for (nm, a, z, nsub) in plan(b):
            if a > b['t0'] + 0.3: A.add(fx, sfx2('whoosh')*0.12, int((a - 0.1)*SR))
        if b.get('sfx') == 'alarm': A.add(fx, alarm()*0.9, int(b['t0']*SR))
        if b.get('sfx') == 'sting': A.add(fx, sting()*0.6, int((b['t0'] + 0.05)*SR))
        if b.get('timer'):
            tt = b['tt0']
            while tt < b['tt1']: A.add(fx, softtick(), int(tt*SR)); tt += 0.5
            A.add(fx, sfx2('right')*0.25, int(b['tt1']*SR))
        if b.get('ans'): A.add(fx, sfx2('right')*0.3, int((b['t0'] + b['d']*0.45)*SR))
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
        if sid == 'rev': continue
        s = SEC_START[sid]; ch.append(('%02d:%02d' % (int(s)//60, int(s) % 60), lab))
    return dict(total=TOTAL, chapters=ch)

# ------------------------------------------------------------------ render
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
