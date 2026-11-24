"""Which Door? marathon (16:9). Scenes: corridor with numbered doors + detective host, room hazards, timer bar, pause clock, reveal."""
import sys, math, os, random, subprocess, cairo
sys.path.insert(0, '/home/claude/pz'); sys.path.insert(0, '/home/claude/long')
import wd
wd.W, wd.H, wd.FLOOR = 1920, 1080, 930
from wd import text, text_w, caption, pill, namebox, bubble, suspect, build_mix, NARR
from pz import Timeline, clamp, prog, sprog, back, hexc, rrect, fill_stroke, OUT
from doors_data import R, TITLES
from doors_beats import make_beats
W, H = 1920, 1080
DX = (560, 960, 1360); DW, DH, DT = 270, 430, 430   # door centers, size, top
FLY = 900  # floor line

def P(ctx, col, a=1.0): ctx.set_source_rgba(*hexc(col, a))

# ------------------------------------------------------------------ base
def stage(ctx, t, glow=True):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#161b2e')); g.add_color_stop_rgba(1, *hexc('#090b14')); ctx.set_source(g); ctx.paint()
    if glow:
        for (cx, cy, col, ph) in ((180, 420, '#ff2d55', 0), (1740, 400, '#2d6bff', math.pi)):
            a = 0.25 + 0.15*math.sin(t*5 + ph)
            rg = cairo.RadialGradient(cx, cy, 10, cx, cy, 520); rg.add_color_stop_rgba(0, *hexc(col, a)); rg.add_color_stop_rgba(1, *hexc(col, 0))
            ctx.set_source(rg); ctx.paint()

def cnum(ctx, x, y, n, r=44, col='#ffffff', tcol='#111111'):
    ctx.arc(x, y, r, 0, 2*math.pi); P(ctx, col); ctx.fill_preserve(); P(ctx, '#111111'); ctx.set_line_width(5); ctx.stroke()
    text(ctx, str(n), x, y + r*0.42, r*1.25, tcol)

def detective(ctx, x, y, s, t, pose='chest', talk=0.0, look=0.0):
    suspect(ctx, x, y, s, '#d9731f', t, pose=pose, mood='neutral', talk=talk, stache=True, badge=False, look=look)
    ctx.save(); ctx.translate(x, y + 3*math.sin(t*2.2 + x*0.01)*s); ctx.scale(s, s)
    hy = -400
    ctx.save(); ctx.scale(1, 0.25); ctx.arc(0, (hy-40)*4, 110, 0, 2*math.pi); ctx.restore(); fill_stroke(ctx, '#8a4a12', 5)
    ctx.move_to(-62, hy-44); ctx.curve_to(-60, hy-120, 60, hy-120, 62, hy-44); ctx.close_path(); fill_stroke(ctx, '#a85a18', 5)
    ctx.rectangle(-62, hy-62, 124, 16); P(ctx, '#3a2412'); ctx.fill()
    # coat lapels
    ctx.move_to(-40, -335); ctx.line_to(0, -250); ctx.line_to(40, -335); P(ctx, '#8a4a12'); ctx.set_line_width(8); ctx.stroke()
    ctx.restore()

def door(ctx, x, n, t, state='closed', p=1.0, light='#fff6d8'):
    x0, y0 = x - DW/2, DT
    ctx.rectangle(x0-18, y0-18, DW+36, DH+18); P(ctx, '#3b2a20'); ctx.fill()
    if state in ('open', 'safe'):
        rg = cairo.LinearGradient(0, y0, 0, y0+DH); rg.add_color_stop_rgba(0, *hexc(light)); rg.add_color_stop_rgba(1, *hexc('#ffd27a'))
        ctx.rectangle(x0, y0, DW, DH); ctx.set_source(rg); ctx.fill()
        rg = cairo.RadialGradient(x, y0+DH, 10, x, y0+DH, 420); rg.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.45*p); rg.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        ctx.set_source(rg); ctx.paint()
        # door leaf swung open
        ctx.move_to(x0, y0); ctx.line_to(x0 - 90*p, y0 + 30*p); ctx.line_to(x0 - 90*p, y0 + DH - 30*p); ctx.line_to(x0, y0 + DH); ctx.close_path(); fill_stroke(ctx, '#7a4a2a', 4)
    else:
        ctx.rectangle(x0, y0, DW, DH); fill_stroke(ctx, '#7a4a2a', 5)
        for (yy, hh) in ((y0+30, 160), (y0+220, 180)):
            rrect(ctx, x0+30, yy, DW-60, hh, 8); P(ctx, '#000000', 0.18); ctx.fill()
        ctx.arc(x0+DW-40, y0+DH/2+20, 13, 0, 2*math.pi); fill_stroke(ctx, '#e0b040', 3)
    cnum(ctx, x, DT - 70, n)
    if state == 'wrong':
        ctx.save(); ctx.translate(x, y0 + DH/2); sc = back(p); ctx.scale(sc, sc)
        P(ctx, '#e8283c'); ctx.set_line_width(36); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(-100, -100); ctx.line_to(100, 100); ctx.move_to(100, -100); ctx.line_to(-100, 100); ctx.stroke(); ctx.restore()

def corridor(ctx, t, states=('closed',)*3, ps=(1, 1, 1), host=True, host_x=190, host_s=0.78, dim=0.0, labels=None):
    stage(ctx, t)
    # back wall + floor
    ctx.rectangle(0, 300, W, FLY-300); P(ctx, '#232a42'); ctx.fill()
    P(ctx, '#000000', 0.18); ctx.set_line_width(3)
    for k in range(0, W, 120): ctx.move_to(k, 300); ctx.line_to(k, FLY); ctx.stroke()
    ctx.rectangle(0, FLY, W, H-FLY); P(ctx, '#1a1410'); ctx.fill()
    P(ctx, '#ffffff', 0.05); ctx.set_line_width(3)
    for k in range(-10, 30): ctx.move_to(960 + k*40, FLY); ctx.line_to(960 + k*160, H); ctx.stroke()
    for i, x in enumerate(DX):
        rg = cairo.RadialGradient(x, 300, 10, x, 300, 300); rg.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.18); rg.add_color_stop_rgba(1, 1, 0.95, 0.8, 0)
        ctx.set_source(rg); ctx.paint()
        door(ctx, x, i+1, t, states[i], ps[i])
        if labels: pill(ctx, x, FLY + 60, 360, 56, '#141826', labels[i], size=26)
    if dim: P(ctx, '#000000', dim); ctx.paint()
    if host: detective(ctx, host_x, H - 40, host_s, t)

def timerbar(ctx, frac, t):
    x0, x1, y = 260, 1660, 225
    rrect(ctx, x0, y, x1-x0, 26, 13); P(ctx, '#2a2f45'); ctx.fill()
    w = (x1-x0)*clamp(frac)
    if w > 2: rrect(ctx, x0, y, w, 26, 13); P(ctx, '#ff2a2a', 0.85 + 0.15*math.sin(t*10)); ctx.fill()

def bigclock(ctx, x, y, r, n, frac):
    ctx.arc(x, y, r, 0, 2*math.pi); fill_stroke(ctx, '#ffffff', 10)
    ctx.move_to(x, y); ctx.arc(x, y, r-14, -math.pi/2, -math.pi/2 + 2*math.pi*frac); ctx.close_path(); P(ctx, '#e8283c', 0.85); ctx.fill()
    text(ctx, str(n), x, y + r*0.32, r*0.95, '#111111')

# ------------------------------------------------------------------ hazard art
def flame(ctx, x, y, s, t, ph=0.0):
    f = 1 + 0.12*math.sin(t*13 + ph)
    ctx.save(); ctx.translate(x, y); ctx.scale(s*f, s/f)
    for col, k in (('#e8401c', 1.0), ('#ff9a1e', 0.7), ('#ffe27a', 0.4)):
        ctx.move_to(0, -120*k); ctx.curve_to(60*k, -50*k, 50*k, 20*k, 0, 22*k); ctx.curve_to(-50*k, 20*k, -60*k, -50*k, 0, -120*k); P(ctx, col); ctx.fill()
    ctx.restore()

def eye(ctx, x, y, r=8, col='#ffd23f'):
    ctx.arc(x, y, r, 0, 2*math.pi); P(ctx, col); ctx.fill(); ctx.arc(x, y, r*0.45, 0, 2*math.pi); P(ctx, '#111111'); ctx.fill()

def quad(ctx, x, y, s, t, body, head_r=50, ears='round', stripes=False, mane=None, face=1, skinny=False):
    ctx.save(); ctx.translate(x, y); ctx.scale(s*face, s)
    for lx in (-90, -50, 50, 90):
        ctx.rectangle(lx-13, -70, 26, 70 + 4*math.sin(t*3+lx)); fill_stroke(ctx, body, 4)
    ctx.save(); ctx.scale(1, 0.55 if not skinny else 0.45); ctx.arc(0, -150/(0.55 if not skinny else 0.45)*0.55, 140, 0, 2*math.pi); ctx.restore(); fill_stroke(ctx, body, 5)
    if skinny:
        P(ctx, '#000000', 0.3); ctx.set_line_width(4)
        for k in range(-2, 3): ctx.move_to(k*22-10, -170); ctx.curve_to(k*22, -150, k*22, -130, k*22+10, -115); ctx.stroke()
    if stripes:
        P(ctx, '#1a1a1a'); ctx.set_line_width(9)
        for k in range(-3, 4): ctx.move_to(k*32, -205); ctx.line_to(k*32+10, -160); ctx.stroke()
    ctx.move_to(-130, -160); ctx.curve_to(-200, -200, -210, -120, -180, -100); P(ctx, body); ctx.set_line_width(12); ctx.stroke()
    hx, hy = 150, -210
    if mane: ctx.arc(hx, hy, head_r*1.6, 0, 2*math.pi); fill_stroke(ctx, mane, 5)
    if ears == 'round':
        for ex in (-30, 30): ctx.arc(hx+ex, hy-head_r*0.8, 16, 0, 2*math.pi); fill_stroke(ctx, body, 4)
    else:
        for ex in (-28, 28): ctx.move_to(hx+ex-16, hy-head_r*0.6); ctx.line_to(hx+ex, hy-head_r*1.5); ctx.line_to(hx+ex+16, hy-head_r*0.6); ctx.close_path(); fill_stroke(ctx, body, 4)
    ctx.arc(hx, hy, head_r, 0, 2*math.pi); fill_stroke(ctx, body, 5)
    eye(ctx, hx-18, hy-10); eye(ctx, hx+18, hy-10)
    ctx.arc(hx+head_r*0.55, hy+14, 9, 0, 2*math.pi); P(ctx, '#222222'); ctx.fill()
    ctx.restore()

def snake(ctx, x, y, s, t, col='#3f7a2a', hood=False, bulge=False, L=520):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    pts = [(-L/2 + k*L/40, 20*math.sin(k*0.5 + t*3)) for k in range(41)]
    for w, c in ((44, '#1a1a1a'), (36, col)):
        ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]
        ctx.set_line_width(w); ctx.set_line_cap(cairo.LINE_CAP_ROUND); P(ctx, c); ctx.stroke()
    if bulge:
        ctx.save(); ctx.translate(0, 0); ctx.scale(1.5, 1); ctx.arc(0, 0, 50, 0, 2*math.pi); ctx.restore(); fill_stroke(ctx, col, 5)
        P(ctx, '#000000', 0.2); ctx.set_line_width(4)
        for k in (-40, -20, 0, 20, 40): ctx.move_to(k, -40); ctx.line_to(k+6, 40); ctx.stroke()
    hx, hy = pts[-1]
    if hood:
        ctx.move_to(hx, hy); ctx.line_to(hx+20, hy-150)
        P(ctx, '#1a1a1a'); ctx.set_line_width(44); ctx.stroke(); ctx.move_to(hx, hy); ctx.line_to(hx+20, hy-150); P(ctx, col); ctx.set_line_width(36); ctx.stroke()
        ctx.save(); ctx.translate(hx+20, hy-170); ctx.scale(1, 1.3); ctx.arc(0, 0, 48, 0, 2*math.pi); ctx.restore(); fill_stroke(ctx, col, 5)
        eye(ctx, hx+6, hy-190, 7, '#ff3b30'); eye(ctx, hx+34, hy-190, 7, '#ff3b30')
        ctx.move_to(hx+20, hy-140); ctx.line_to(hx+20, hy-110 + 6*math.sin(t*20)); P(ctx, '#e8283c'); ctx.set_line_width(4); ctx.stroke()
    else:
        ctx.save(); ctx.translate(hx+20, hy); ctx.scale(1.4, 1); ctx.arc(0, 0, 32, 0, 2*math.pi); ctx.restore(); fill_stroke(ctx, col, 5)
        eye(ctx, hx+34, hy-12, 7)
    ctx.restore()

def croc(ctx, x, y, s, t, face=1):
    ctx.save(); ctx.translate(x, y + 6*math.sin(t*2 + x)); ctx.scale(s*face, s)
    ctx.move_to(-260, 0); ctx.curve_to(-160, -50, 120, -60, 200, -30); ctx.line_to(320, -20); ctx.line_to(320, 10); ctx.line_to(200, 15); ctx.curve_to(100, 30, -150, 30, -260, 0)
    fill_stroke(ctx, '#3f7a3a', 5)
    P(ctx, '#ffffff')
    for k in range(8): ctx.move_to(210 + k*14, 10); ctx.line_to(217 + k*14, 24); ctx.line_to(224 + k*14, 10); ctx.close_path(); ctx.fill()
    for k in range(7): ctx.move_to(-150 + k*45, -38); ctx.line_to(-135 + k*45, -62); ctx.line_to(-120 + k*45, -40); P(ctx, '#2c5a28'); ctx.fill()
    ctx.arc(190, -48, 16, 0, 2*math.pi); fill_stroke(ctx, '#3f7a3a', 4); eye(ctx, 192, -50, 8)
    ctx.restore()

def fish(ctx, x, y, s, col, t=0, face=1, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s*face, s)
    ctx.save(); ctx.scale(1.6, 1); ctx.arc(0, 0, 40, 0, 2*math.pi); ctx.restore(); ctx.set_source_rgba(*hexc(col, a)); ctx.fill_preserve(); ctx.set_source_rgba(0.1, 0.1, 0.1, a); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(-60, 0); ctx.line_to(-100, -30); ctx.line_to(-100, 30); ctx.close_path(); ctx.set_source_rgba(*hexc(col, a)); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, a)
    for k in range(4): ctx.move_to(40 + k*7, 12); ctx.line_to(44 + k*7, 22); ctx.line_to(48 + k*7, 12); ctx.fill()
    eye(ctx, 38, -10, 7, '#ffffff')
    ctx.restore()

def skull(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.arc(0, 0, 50, 0, 2*math.pi); fill_stroke(ctx, '#f2f2f2', 5); rrect(ctx, -30, 30, 60, 40, 8); fill_stroke(ctx, '#f2f2f2', 5)
    for ex in (-20, 20): ctx.arc(ex, 0, 13, 0, 2*math.pi); P(ctx, '#111111'); ctx.fill()
    ctx.restore()

def gascloud(ctx, t, x0, x1, y0, y1, seed=1):
    rnd = random.Random(seed)
    for k in range(26):
        x = rnd.uniform(x0, x1) + 30*math.sin(t*0.8 + k); y = rnd.uniform(y0, y1) + 20*math.cos(t*0.7 + k)
        ctx.arc(x, y, rnd.uniform(50, 110), 0, 2*math.pi); P(ctx, '#7dff4a', 0.16); ctx.fill()

def room_bg(ctx, wall='#2e3550', floor='#1d1a18', fy=820):
    ctx.rectangle(0, 0, W, H); P(ctx, wall); ctx.fill()
    ctx.rectangle(0, fy, W, H-fy); P(ctx, floor); ctx.fill()
    g = cairo.RadialGradient(960, 520, 50, 960, 520, 1100); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.6); ctx.set_source(g); ctx.paint()

def sky_storm(ctx, t, flash=True):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#1c2233')); g.add_color_stop_rgba(1, *hexc('#3a4257')); ctx.set_source(g); ctx.paint()
    if flash and (t % 2.6) < 0.12: P(ctx, '#ffffff', 0.35); ctx.paint()
    ctx.rectangle(0, 820, W, H); P(ctx, '#2f5a2a'); ctx.fill()
    rnd = random.Random(4); P(ctx, '#a8c4ff', 0.35); ctx.set_line_width(3)
    for k in range(90):
        x = (rnd.uniform(0, W) + t*200) % W; y = (rnd.uniform(0, H) + t*900) % H
        ctx.move_to(x, y); ctx.line_to(x-10, y+40); ctx.stroke()
    bx = 1500; P(ctx, '#fff27a', 0.9 if (t % 2.6) < 0.25 else 0.0)
    ctx.move_to(bx, 0); ctx.line_to(bx-60, 160); ctx.line_to(bx-10, 160); ctx.line_to(bx-90, 360); ctx.line_to(bx+20, 140); ctx.line_to(bx-30, 140); ctx.line_to(bx+30, 0); ctx.fill()

def building_bg(ctx, t):
    room_bg(ctx, '#3a3340', '#2a2522')
    rnd = random.Random(2)
    for k in range(10):
        x = rnd.uniform(0, W); y = rnd.uniform(200, 700)
        ctx.arc(x + 20*math.sin(t+k), y - (t*30 % 200), rnd.uniform(60, 130), 0, 2*math.pi); P(ctx, '#555555', 0.22); ctx.fill()

def hazard(ctx, kind, t):
    if kind == 'fire':
        room_bg(ctx, '#3a1c14', '#2a120c')
        for k in range(9): flame(ctx, 330 + k*160, 820, 1.3 + 0.3*(k % 2), t, k)
    elif kind == 'oilfire':
        room_bg(ctx, '#3a2a24', '#221814')
        ctx.rectangle(760, 470, 400, 350); fill_stroke(ctx, '#6a6f78', 6)
        for yy in (540, 650, 760): ctx.rectangle(760, yy, 400, 14); P(ctx, '#4a4f58'); ctx.fill()
        text(ctx, 'OIL', 960, 690, 80, '#ffd23f')
        for k in range(6): flame(ctx, 780 + k*72, 470, 1.0, t, k)
        for k in range(4): flame(ctx, 400 + k*370 if k < 2 else 1250 + (k-2)*250, 830, 0.9, t, k+3)
    elif kind == 'lions':
        room_bg(ctx, '#4a3a28', '#3a2a18')
        for k, (x, s, f) in enumerate(((560, 0.9, 1), (1320, 0.95, -1), (950, 0.7, 1))):
            quad(ctx, x, 830 if k < 2 else 640, s, t, '#d9a441', head_r=52, mane='#8a4a18', face=f, skinny=True)
    elif kind == 'crocs':
        room_bg(ctx, '#24343a', '#1a2224', fy=560)
        ctx.rectangle(0, 560, W, H); P(ctx, '#2a6a6a'); ctx.fill()
        for k in range(8):
            xx = (k*260 + t*40) % W; P(ctx, '#ffffff', 0.18); ctx.rectangle(xx, 600 + (k % 4)*90, 120, 5); ctx.fill()
        for k, (x, y, f) in enumerate(((560, 680, 1), (1300, 790, -1), (900, 920, 1))): croc(ctx, x, y, 0.95, t, f)
    elif kind in ('gaslong', 'gasshort'):
        room_bg(ctx, '#2a3424', '#1a2018')
        if kind == 'gaslong':
            P(ctx, '#ffffff', 0.08); ctx.set_line_width(3)
            for k in range(12): ctx.move_to(960 + (k-6)*30, 300); ctx.line_to(960 + (k-6)*170, 820); ctx.stroke()
            rrect(ctx, 930, 300, 60, 90, 4); P(ctx, '#ffffff', 0.35); ctx.fill()
            pill(ctx, 960, 470, 300, 80, '#141826', '100 METRES', size=40)
            gascloud(ctx, t, 200, 1720, 260, 860)
            skull(ctx, 960, 640, 1.2)
        else:
            rrect(ctx, 1500, 360, 240, 460, 6); P(ctx, '#fff6d8'); ctx.fill(); text(ctx, 'EXIT', 1620, 330, 46, '#2fbf4f')
            gascloud(ctx, t, 300, 1450, 260, 860)
            skull(ctx, 900, 520, 1.1)
            for k in range(2):
                ctx.save(); ctx.translate(820 + k*320, 860); ctx.scale(1.4, 0.6); ctx.arc(0, 0, 40, 0, 2*math.pi); ctx.restore(); P(ctx, '#ffffff', 0.7); ctx.fill()
    elif kind == 'electric':
        room_bg(ctx, '#2a2e3a', '#4a4f5a', fy=700)
        for k in range(16):
            ctx.rectangle(k*120, 700, 120, 380); P(ctx, '#5a606c' if k % 2 else '#4a505c'); ctx.fill()
        ctx.move_to(960, 230); ctx.line_to(1080, 430); ctx.line_to(840, 430); ctx.close_path(); fill_stroke(ctx, '#ffd23f', 6)
        text(ctx, '!', 960, 410, 120, '#111111')
        pill(ctx, 960, 500, 380, 80, '#e8283c', '10,000 V', size=50)
        # cable from floor box to an unplugged plug lying on the floor, socket on wall
        rrect(ctx, 320, 640, 120, 80, 8); fill_stroke(ctx, '#2a2a2a', 4)
        ctx.move_to(440, 690); ctx.curve_to(700, 760, 1100, 640, 1380, 760); P(ctx, '#111111'); ctx.set_line_width(14); ctx.stroke()
        rrect(ctx, 1380, 735, 70, 50, 8); fill_stroke(ctx, '#e8e8e8', 4)
        for py in (748, 772): ctx.rectangle(1450, py-4, 34, 8); P(ctx, '#c0a040'); ctx.fill()
        rrect(ctx, 1640, 560, 110, 140, 12); fill_stroke(ctx, '#f2f2f2', 4)
        for px in (1675, 1715): ctx.rectangle(px-6, 610, 12, 30); P(ctx, '#222222'); ctx.fill()
    elif kind == 'scorpions':
        room_bg(ctx, '#4a3a28', '#5a4428', fy=640)
        rnd = random.Random(7)
        for k in range(26):
            x, y = rnd.uniform(150, 1770), rnd.uniform(680, 1040); s = rnd.uniform(0.5, 0.9); f = rnd.choice((-1, 1))
            ctx.save(); ctx.translate(x + 6*math.sin(t*4+k), y); ctx.scale(s*f, s)
            P(ctx, '#3a1a10'); ctx.set_line_width(6)
            for lx in (-20, -5, 10): ctx.move_to(lx, 0); ctx.line_to(lx-10, 22); ctx.move_to(lx, 0); ctx.line_to(lx-10, -22); ctx.stroke()
            ctx.save(); ctx.scale(1.6, 1); ctx.arc(0, 0, 16, 0, 2*math.pi); ctx.restore(); ctx.fill()
            ctx.move_to(-24, 0); ctx.curve_to(-60, -10, -70, -60, -40, -70); ctx.set_line_width(9); ctx.stroke()
            ctx.move_to(-40, -70); ctx.line_to(-28, -60); ctx.set_line_width(6); P(ctx, '#e8283c'); ctx.stroke()
            for cy in (-14, 14): P(ctx, '#3a1a10'); ctx.arc(34, cy, 9, 0, 2*math.pi); ctx.fill()
            ctx.restore()
    elif kind == 'sharks':
        room_bg(ctx, '#1c2a3a', '#141c24')
        ctx.rectangle(360, 330, 1200, 500); P(ctx, '#bfe6ff', 0.10); ctx.fill_preserve(); P(ctx, '#9ad0ff'); ctx.set_line_width(10); ctx.stroke()
        ctx.rectangle(366, 760, 1188, 64); P(ctx, '#8a7a5a'); ctx.fill()
        for k, (x, f) in enumerate(((700, 1), (1180, -1))):
            ctx.save(); ctx.translate(x, 740); ctx.scale(f, 1)
            ctx.move_to(-150, 0); ctx.curve_to(-60, -60, 100, -60, 160, -10); ctx.line_to(160, 10); ctx.curve_to(60, 30, -80, 30, -150, 0); fill_stroke(ctx, '#7a8a96', 5)
            ctx.move_to(-10, -42); ctx.line_to(30, -100); ctx.line_to(50, -40); fill_stroke(ctx, '#7a8a96', 4)
            ctx.move_to(-150, 0); ctx.line_to(-200, -40); ctx.line_to(-190, 30); ctx.close_path(); fill_stroke(ctx, '#7a8a96', 4)
            ctx.restore()
        P(ctx, '#ffffff', 0.25); ctx.set_line_width(8); ctx.move_to(420, 360); ctx.line_to(520, 360); ctx.stroke()
        ctx.save(); ctx.translate(1380, 420); ctx.rotate(0.06); pill(ctx, 0, 0, 260, 76, '#f4ead2', 'EMPTY', tcol='#c0392b', size=44); ctx.restore()
    elif kind == 'flood':
        room_bg(ctx, '#2a3440', '#1a2028')
        lvl = 820 - 180*((t*0.25) % 1)
        ctx.move_to(0, lvl)
        for x in range(0, W+40, 40): ctx.line_to(x, lvl + 10*math.sin(x/60 + t*4))
        ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path(); P(ctx, '#2d7ad6', 0.8); ctx.fill()
        for px in (400, 1520):
            rrect(ctx, px-40, 220, 80, 60, 10); fill_stroke(ctx, '#6a6f78', 4)
            ctx.rectangle(px-30, 280, 60, lvl-280); P(ctx, '#5aa8ff', 0.6); ctx.fill()
        pill(ctx, 960, 400, 260, 90, '#e8283c', '1:00', size=56)
    elif kind == 'spikes':
        room_bg(ctx, '#2e2e36', '#1e1e24')
        drop = 120 + 60*math.sin(t*1.2)
        ctx.rectangle(0, 0, W, 180 + drop); P(ctx, '#4a4a54'); ctx.fill()
        for k in range(24):
            x = 40 + k*80; ctx.move_to(x-30, 180+drop); ctx.line_to(x, 290+drop); ctx.line_to(x+30, 180+drop); ctx.close_path(); fill_stroke(ctx, '#c8ccd4', 3)
        for x in (700, 1220):
            P(ctx, '#ff3b30'); ctx.move_to(x, 600); ctx.line_to(x, 720); ctx.set_line_width(14); ctx.stroke()
            ctx.move_to(x-36, 700); ctx.line_to(x, 760); ctx.line_to(x+36, 700); ctx.close_path(); ctx.fill()
    elif kind == 'lens':
        room_bg(ctx, '#5a4430', '#7a5a38')
        ctx.save(); ctx.translate(960, 290); ctx.scale(1, 0.25); ctx.arc(0, 0, 640, 0, 2*math.pi); ctx.restore()
        P(ctx, '#bfe6ff', 0.55); ctx.fill_preserve(); P(ctx, '#d4a840'); ctx.set_line_width(18); ctx.stroke()
        P(ctx, '#ffffff', 0.6); ctx.set_line_width(10); ctx.move_to(560, 250); ctx.curve_to(700, 220, 900, 210, 1020, 215); ctx.stroke()
        for k in range(5):
            ctx.save(); ctx.translate(500 + k*230, 900); ctx.scale(2, 0.5); ctx.arc(0, 0, 36, 0, 2*math.pi); ctx.restore(); P(ctx, '#1a1a1a', 0.7); ctx.fill()
        P(ctx, '#ffffff', 0.08)
        ctx.move_to(400, 330); ctx.line_to(1520, 330); ctx.line_to(1000, 880); ctx.line_to(920, 880); ctx.close_path(); ctx.fill()
    elif kind == 'ice':
        room_bg(ctx, '#bcd8ee', '#e6f2fb')
        for k in range(26):
            x = 30 + k*74; L = 60 + 50*((k*7) % 3)
            ctx.move_to(x-18, 0); ctx.line_to(x, L); ctx.line_to(x+18, 0); ctx.close_path(); fill_stroke(ctx, '#e8f6ff', 3)
        rnd = random.Random(5)
        for k in range(40):
            x = rnd.uniform(0, W); y = (rnd.uniform(0, H) + t*60) % H
            ctx.arc(x, y, rnd.uniform(3, 7), 0, 2*math.pi); P(ctx, '#ffffff', 0.9); ctx.fill()
        rrect(ctx, 920, 260, 80, 460, 40); fill_stroke(ctx, '#ffffff', 6)
        ctx.arc(960, 740, 70, 0, 2*math.pi); fill_stroke(ctx, '#2d6bff', 6); ctx.rectangle(945, 640, 30, 80); P(ctx, '#2d6bff'); ctx.fill()
        pill(ctx, 1230, 500, 220, 90, '#2d6bff', '-60', size=60)
        pill(ctx, 700, 500, 260, 80, '#141826', '1 HOUR', size=44)
    elif kind == 'bees':
        room_bg(ctx, '#4a3a1c', '#3a2a14')
        ctx.save(); ctx.translate(960, 380); ctx.scale(1, 1.2)
        for k in range(5): ctx.save(); ctx.scale(1 - k*0.12, 1); ctx.arc(0, -60 + k*50, 120, 0, math.pi); ctx.restore(); fill_stroke(ctx, '#d9a441', 4)
        ctx.restore()
        rnd = random.Random(3)
        for k in range(60):
            cx, cy = rnd.uniform(200, 1720), rnd.uniform(250, 980); ph = rnd.uniform(0, 6)
            x = cx + 40*math.sin(t*3 + ph); y = cy + 30*math.cos(t*4 + ph)
            ctx.save(); ctx.translate(x, y)
            for wx in (-8, 8): ctx.arc(wx, -14, 10, 0, 2*math.pi); P(ctx, '#ffffff', 0.7); ctx.fill()
            ctx.save(); ctx.scale(1.4, 1); ctx.arc(0, 0, 13, 0, 2*math.pi); ctx.restore(); P(ctx, '#ffd23f'); ctx.fill()
            P(ctx, '#111111'); ctx.rectangle(-6, -12, 5, 24); ctx.fill(); ctx.rectangle(6, -12, 5, 24); ctx.fill()
            ctx.restore()
    elif kind == 'quicksand':
        room_bg(ctx, '#4a3a28', '#c9a26b', fy=560)
        for k in range(7):
            ctx.save(); ctx.translate(960, 820); ctx.scale(1, 0.3); ctx.arc(0, 0, 120 + k*120 + 20*math.sin(t*2+k), 0, 2*math.pi); ctx.restore()
            P(ctx, '#8a6a3a', 0.5); ctx.set_line_width(8); ctx.stroke()
        for k in range(6):
            r = (t*0.8 + k*0.17) % 1; x = 600 + k*140
            ctx.arc(x, 760 + k*25 - r*30, 12*(1-r) + 4, 0, 2*math.pi); P(ctx, '#e2c38a', 1-r); ctx.fill()
        # a stick sinking
        ctx.save(); ctx.translate(1300, 760 + 20*((t*0.3) % 1)); ctx.rotate(0.3); ctx.rectangle(-8, -160, 16, 160); fill_stroke(ctx, '#6a4426', 3); ctx.restore()
    elif kind == 'cobras':
        room_bg(ctx, '#2a3424', '#3a3020', fy=700)
        for k, (x, y, s) in enumerate(((420, 900, 0.8), (900, 960, 0.9), (1400, 900, 0.8), (680, 780, 0.6), (1180, 780, 0.6))):
            snake(ctx, x, y, s, t + k, col='#3a3a2a', hood=True, L=360)
    elif kind == 'tiger':
        room_bg(ctx, '#2e3a2a', '#2a2418')
        quad(ctx, 960, 860, 1.1, t, '#e8822a', head_r=56, stripes=True, face=1)
        ctx.rectangle(560, 300, 800, 580); P(ctx, '#bfe6ff', 0.18); ctx.fill_preserve(); P(ctx, '#d8f0ff', 0.9); ctx.set_line_width(12); ctx.stroke()
        P(ctx, '#ffffff', 0.5); ctx.set_line_width(14)
        ctx.move_to(620, 360); ctx.line_to(760, 360); ctx.move_to(620, 400); ctx.line_to(700, 400); ctx.move_to(1200, 800); ctx.line_to(1320, 800); ctx.stroke()
    elif kind == 'lava':
        room_bg(ctx, '#2a1c1c', '#1a1212', fy=600)
        ctx.move_to(0, 640)
        for x in range(0, W+40, 40): ctx.line_to(x, 640 + 12*math.sin(x/90 + t*2))
        ctx.line_to(W, 900); ctx.line_to(0, 900); ctx.close_path()
        g = cairo.LinearGradient(0, 640, 0, 900); g.add_color_stop_rgba(0, *hexc('#ffb21e')); g.add_color_stop_rgba(1, *hexc('#d8280c')); ctx.set_source(g); ctx.fill()
        for k in range(8):
            r = (t*0.7 + k*0.13) % 1; ctx.arc(150 + k*230, 720 - r*40, 18*(1-r) + 5, 0, 2*math.pi); P(ctx, '#ffe27a', 1-r); ctx.fill()
        rg = cairo.RadialGradient(960, 760, 50, 960, 760, 900); rg.add_color_stop_rgba(0, 1, 0.4, 0.1, 0.35); rg.add_color_stop_rgba(1, 1, 0.2, 0, 0); ctx.set_source(rg); ctx.paint()
    elif kind == 'piranha':
        room_bg(ctx, '#7a90a8', '#dfeef8', fy=560)
        ctx.rectangle(100, 600, 1720, 380); P(ctx, '#9fd0f0', 0.9); ctx.fill()
        rnd = random.Random(9)
        for k in range(9):
            fish(ctx, rnd.uniform(250, 1700), rnd.uniform(700, 940), 0.6, '#d8402c', face=rnd.choice((-1, 1)), a=0.55)
        ctx.rectangle(100, 600, 1720, 380); P(ctx, '#ffffff', 0.35); ctx.fill()
        P(ctx, '#ffffff', 0.9); ctx.set_line_width(4)
        for (a, b, c, d) in ((300, 640, 420, 720), (420, 720, 380, 800), (1300, 620, 1420, 700), (1420, 700, 1520, 690)):
            ctx.move_to(a, b); ctx.line_to(c, d); ctx.stroke()
        pill(ctx, 1600, 540, 260, 70, '#2d6bff', 'ICE: 1 M', size=36)
    elif kind == 'wolves':
        room_bg(ctx, '#1e2436', '#e6eef6', fy=760)
        for k, (x, s, f) in enumerate(((480, 0.75, 1), (980, 0.85, -1), (1440, 0.75, -1))):
            quad(ctx, x, 920, s, t + k, '#7a808c', head_r=46, ears='point', face=f)
    elif kind == 'rocks':
        room_bg(ctx, '#3a3430', '#2a2420')
        rnd = random.Random(11)
        for k in range(12):
            x = rnd.uniform(200, 1720); ph = rnd.uniform(0, 1); y = ((t*0.9 + ph) % 1)*900 - 80
            r = rnd.uniform(30, 60)
            ctx.save(); ctx.translate(x, y); ctx.rotate(t*2 + k)
            ctx.move_to(-r, 0); ctx.line_to(-r*0.4, -r); ctx.line_to(r*0.7, -r*0.8); ctx.line_to(r, r*0.2); ctx.line_to(r*0.2, r); ctx.line_to(-r*0.8, r*0.6); ctx.close_path(); fill_stroke(ctx, '#8a8e96', 4)
            ctx.restore()
        for k in range(8): ctx.save(); ctx.translate(200 + k*220, 830); ctx.scale(1.4, 0.6); ctx.arc(0, 0, 50, 0, 2*math.pi); ctx.restore(); fill_stroke(ctx, '#6a6e76', 4)
    elif kind == 'python':
        room_bg(ctx, '#2e3424', '#3a2e20')
        snake(ctx, 960, 760, 1.6, t*0.3, col='#8a9a2a', bulge=True, L=700)
    elif kind == 'bear':
        room_bg(ctx, '#2e2a24', '#3a2e20')
        quad(ctx, 960, 900, 1.25, t, '#6a4426', head_r=60, face=1)
        quad(ctx, 500, 900, 0.5, t, '#7a5436', head_r=56, face=1); quad(ctx, 1450, 900, 0.5, t, '#7a5436', head_r=56, face=-1)
    elif kind == 'spiders':
        room_bg(ctx, '#1e1e26', '#16161c')
        for (cx, cy, R_) in ((480, 380, 300), (1440, 420, 320), (960, 760, 260)):
            P(ctx, '#ffffff', 0.4); ctx.set_line_width(3)
            for k in range(10): a = k*math.pi/5; ctx.move_to(cx, cy); ctx.line_to(cx + R_*math.cos(a), cy + R_*math.sin(a)); ctx.stroke()
            for rr in range(40, R_, 50): ctx.arc(cx, cy, rr, 0, 2*math.pi); ctx.stroke()
            for k in range(3):
                a = k*2.1 + t*0.3; sx, sy = cx + (80 + k*60)*math.cos(a), cy + (80 + k*60)*math.sin(a)
                P(ctx, '#111111'); ctx.set_line_width(5)
                for l in range(4):
                    for sgn in (-1, 1): ctx.move_to(sx, sy); ctx.line_to(sx + sgn*34, sy - 20 + l*14); ctx.line_to(sx + sgn*46, sy - 4 + l*14); ctx.stroke()
                ctx.arc(sx, sy, 18, 0, 2*math.pi); ctx.fill(); ctx.arc(sx, sy - 6, 6, 0, 2*math.pi); P(ctx, '#e8283c'); ctx.fill()
    elif kind == 'lift':
        building_bg(ctx, t)
        ctx.rectangle(700, 260, 520, 600); fill_stroke(ctx, '#9aa0a8', 6)
        ctx.rectangle(710, 270, 245, 580); fill_stroke(ctx, '#c0c6ce', 3); ctx.rectangle(965, 270, 245, 580); fill_stroke(ctx, '#c0c6ce', 3)
        for k, y in enumerate((480, 560)):
            ctx.arc(1300, y, 30, 0, 2*math.pi); fill_stroke(ctx, '#2a2a2a', 4)
            ctx.move_to(1285, y + (8 if k == 0 else -8)); ctx.line_to(1300, y + (-12 if k == 0 else 12)); ctx.line_to(1315, y + (8 if k == 0 else -8)); P(ctx, '#ffd23f'); ctx.fill()
        rrect(ctx, 880, 190, 160, 56, 8); P(ctx, '#111111'); ctx.fill(); text(ctx, '10', 960, 234, 40, '#ff2a2a')
    elif kind == 'window':
        building_bg(ctx, t)
        ctx.rectangle(640, 220, 640, 560); fill_stroke(ctx, '#d8e6f0', 10)
        g = cairo.LinearGradient(0, 230, 0, 770); g.add_color_stop_rgba(0, *hexc('#ff9a3c')); g.add_color_stop_rgba(1, *hexc('#3a2a4a')); ctx.rectangle(650, 230, 620, 540); ctx.set_source(g); ctx.fill()
        for k in range(5): ctx.rectangle(690 + k*120, 560 - (k % 3)*70, 80, 220 + (k % 3)*70); P(ctx, '#1a1a2a'); ctx.fill()
        ctx.move_to(960, 230); ctx.line_to(960, 770); ctx.move_to(650, 500); ctx.line_to(1270, 500); P(ctx, '#d8e6f0'); ctx.set_line_width(10); ctx.stroke()
        pill(ctx, 960, 860, 300, 70, '#e8283c', '10TH FLOOR', size=36)
    elif kind == 'stairs':
        building_bg(ctx, t)
        for k in range(8):
            ctx.rectangle(500 + k*110, 860 - (8-k)*60, 110, (8-k)*60 + 20); fill_stroke(ctx, '#7a6a5a', 4)
        ctx.move_to(500, 300); ctx.line_to(1380, 820); P(ctx, '#c8a040'); ctx.set_line_width(10); ctx.stroke()
        rrect(ctx, 1450, 280, 240, 100, 10); P(ctx, '#2fbf4f'); ctx.fill(); text(ctx, 'EXIT', 1570, 350, 56, '#ffffff')
        suspect(ctx, 760, 620, 0.42, '#2d6bff', t, pose='down', mood='scared', badge=False)
    elif kind in ('tree', 'umbrella', 'car'):
        sky_storm(ctx, t)
        if kind == 'tree':
            ctx.rectangle(920, 420, 80, 420); fill_stroke(ctx, '#5a3a22', 5)
            for (cx, cy, r) in ((960, 360, 170), (860, 440, 120), (1060, 440, 120), (960, 250, 120)): ctx.arc(cx, cy, r, 0, 2*math.pi); fill_stroke(ctx, '#2a5a2a', 5)
            suspect(ctx, 1080, 860, 0.42, '#2d6bff', t, pose='down', mood='scared', badge=False)
        elif kind == 'umbrella':
            suspect(ctx, 960, 860, 0.62, '#2d6bff', t, pose='up', mood='scared', badge=False)
            ctx.move_to(960, 560); ctx.line_to(960, 300); P(ctx, '#9aa0a8'); ctx.set_line_width(10); ctx.stroke()
            ctx.move_to(760, 340); ctx.curve_to(800, 180, 1120, 180, 1160, 340); ctx.close_path(); fill_stroke(ctx, '#9aa0a8', 6)
            ctx.arc(960, 210, 12, 0, 2*math.pi); P(ctx, '#d8dde4'); ctx.fill()
        else:
            ctx.move_to(620, 820); ctx.line_to(620, 700); ctx.line_to(760, 690); ctx.line_to(840, 580); ctx.line_to(1120, 580); ctx.line_to(1220, 690); ctx.line_to(1320, 700); ctx.line_to(1320, 820); ctx.close_path(); fill_stroke(ctx, '#c8283c', 6)
            for (a, b) in ((860, 990), (1010, 1150)): ctx.move_to(a, 600); ctx.line_to(b if b < 1100 else 1110, 600); ctx.line_to(b + 40 if b > 1100 else b, 685); ctx.line_to(a - 20 if a < 900 else a, 685); ctx.close_path(); fill_stroke(ctx, '#bfe6ff', 4)
            for wx in (760, 1180): ctx.arc(wx, 830, 56, 0, 2*math.pi); fill_stroke(ctx, '#222222', 5); ctx.arc(wx, 830, 22, 0, 2*math.pi); P(ctx, '#aaaaaa'); ctx.fill()
            suspect(ctx, 930, 690, 0.22, '#2d6bff', t, pose='down', mood='neutral', badge=False)

def room(ctx, t, i, j, t0):
    kind, ml, en, lab = R[i]['rooms'][j]
    hazard(ctx, kind, t)
    # door frame vignette
    ctx.set_source_rgba(*hexc('#3b2a20')); ctx.rectangle(0, 0, W, H); ctx.rectangle(W-60, 40, -(W-120), H-40); ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); ctx.fill(); ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    cnum(ctx, 140, 290, j+1, r=62)
    pill(ctx, W/2, 1010, max(380, text_w(ctx, lab, 40) + 90), 76, '#e8283c', lab, size=40, p=prog(t, t0 + 0.3, 0.3))

# ------------------------------------------------------------------ timeline + draw
def build():
    beats = make_beats()
    tl = Timeline(beats, lead=0.15, gap=0.3, think=0, spk=NARR)
    return tl, beats

def draw_factory(tl):
    T = tl.by; N = len(R)
    def draw(ctx, t):
        cur = tl.beats[0]
        for b in tl.beats:
            if t >= b['t0'] - 0.12: cur = b
        b = cur; t0, t1 = b['t0'], b['t1']; sc = b['sc']; i = b['i']
        z = 1.0 + 0.05*(1 - sprog(t, t0-0.12, 0.3)) + 0.02*prog(t, t0, t1-t0+0.5)
        ctx.save(); ctx.translate(W/2, H/2); ctx.scale(z, z); ctx.translate(-W/2, -H/2)
        if sc in ('teaser', 'teaser2'):
            if sc == 'teaser': hazard(ctx, 'lens', t)
            else: corridor(ctx, t)
            P(ctx, '#000000', 0.45); ctx.paint()
            ctx.save(); ctx.translate(W/2, 560); s_ = back(prog(t, t0, 0.35)); ctx.scale(s_, s_)
            ctx.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(190)
            e = ctx.text_extents('WHICH DOOR?'); ctx.move_to(-e[2]/2 - e[0], 60); ctx.text_path('WHICH DOOR?')
            P(ctx, '#0a0a10'); ctx.set_line_width(26); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve(); P(ctx, '#ffd23f'); ctx.fill(); ctx.restore()
            ctx.save(); ctx.translate(W/2, 790); ctx.rotate(-0.04); pill(ctx, 0, 0, 640, 110, '#e8283c', '99% FAIL', size=64, p=prog(t, t0+0.5, 0.3)); ctx.restore()
        elif sc == 'title':
            corridor(ctx, t, host_x=200 + 0*t)
            pill(ctx, W/2, 255, 420, 90, '#ffd23f', f'RIDDLE {i+1}/{N}', tcol='#141414', size=52, p=prog(t, t0, 0.3))
        elif sc == 'room':
            room(ctx, t, i, b['j'], t0)
        elif sc in ('corr', 'pause'):
            corridor(ctx, t, labels=[r[3] for r in R[i]['rooms']], dim=0.25 if sc == 'pause' else 0)
            q0 = T[f'r{i}_q']['t0']; q1 = T[f'r{i}_p']['t1'] + 5.0
            timerbar(ctx, 1 - (t - q0)/(q1 - q0), t)
            if sc == 'corr':
                detective(ctx, 190, H - 40, 0.78, t)
                bubble(ctx, 330, 330, '?', size=80, p=prog(t, t0 + 0.2, 0.3), tail=-1)
            else:
                left = 5 - (t - t1)
                if t > t1: bigclock(ctx, W/2, 640, 170, max(1, math.ceil(left)), clamp(1 - left/5))
                else: bigclock(ctx, W/2, 640, 170, 5, 0)
        elif sc == 'wrong':
            s = R[i]['safe']; st = ['wrong' if k != s else 'closed' for k in range(3)]
            corridor(ctx, t, states=st, ps=[prog(t, t0 + 0.3 + 0.9*k, 0.3) for k in range(3)], labels=[r[3] for r in R[i]['rooms']])
        elif sc == 'reveal':
            s = R[i]['safe']; st = ['wrong' if k != s else 'safe' for k in range(3)]
            walk = sprog(t, t0 + 0.4, 1.6)
            hx = 190 + (DX[s] - 190)*walk; hs = 0.78 - 0.35*walk
            corridor(ctx, t, states=st, ps=[1 if k != s else prog(t, t0, 0.4) for k in range(3)], host=False, labels=[r[3] for r in R[i]['rooms']])
            detective(ctx, hx, H - 40 - (H - 40 - (DT + DH))*walk, hs, t, pose='down')
            pill(ctx, DX[s], DT - 150, 220, 70, '#2fbf4f', 'SAFE ✓', size=40, p=prog(t, t0 + 0.3, 0.3))
        elif sc == 'why':
            s = R[i]['safe']; kind = R[i]['rooms'][s][0]
            hazard(ctx, kind, t)
            if kind == 'lens':
                P(ctx, '#0a0f24', 0.55); ctx.paint(); ctx.arc(260, 330, 70, 0, 2*math.pi); P(ctx, '#fff6d8'); ctx.fill(); ctx.arc(235, 315, 62, 0, 2*math.pi); P(ctx, '#2a2f4a'); ctx.fill()
            P(ctx, '#000000', 0.25); ctx.paint()
            wl = R[i]['wl']
            ctx.save(); ctx.translate(W/2, 960); ctx.rotate(-0.015); sc_ = back(prog(t, t0 + 0.2, 0.35)); ctx.scale(sc_, sc_)
            w_ = text_w(ctx, wl, 46) + 120; ctx.rectangle(-w_/2, -60, w_, 120); fill_stroke(ctx, '#f4ead2', 5); text(ctx, wl, 0, 16, 46, '#1a1a1a'); ctx.restore()
            ctx.save(); ctx.translate(1660, 330); ctx.rotate(0.12); pill(ctx, 0, 0, 280, 100, '#2fbf4f', '+1 POINT', size=48, p=prog(t, t1 - 1.2, 0.3)); ctx.restore()
        elif sc == 'half':
            stage(ctx, t)
            rrect(ctx, 560, 330, 800, 330, 30); fill_stroke(ctx, '#f4ead2', 6)
            text(ctx, 'HALFWAY SCORE', W/2, 430, 64, '#1a1a1a'); text(ctx, '__ / 5', W/2, 590, 130, '#e8283c')
            detective(ctx, 220, H - 30, 0.7, t, pose='point')
        elif sc == 'end':
            stage(ctx, t)
            rrect(ctx, 560, 300, 800, 330, 30); fill_stroke(ctx, '#f4ead2', 6)
            text(ctx, 'YOUR SCORE', W/2, 400, 64, '#1a1a1a'); text(ctx, '__ / 10', W/2, 560, 130, '#e8283c')
            p_ = 1 + 0.06*math.sin(t*8)
            ctx.save(); ctx.translate(W/2 - 260, 780); rrect(ctx, -230, -60, 460, 120, 60); P(ctx, '#ffffff'); ctx.fill(); text(ctx, 'COMMENT', 0, 20, 52, '#141414'); ctx.restore()
            ctx.save(); ctx.translate(W/2 + 260, 780); ctx.scale(p_, p_); rrect(ctx, -230, -60, 460, 120, 60); P(ctx, '#e8283c'); ctx.fill(); text(ctx, 'SUBSCRIBE', 0, 20, 52, '#ffffff'); ctx.restore()
            detective(ctx, 220, H - 30, 0.7, t, pose='up')
        ctx.restore()
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and b is not tl.beats[0]: P(ctx, '#ffffff', 0.22*fl); ctx.paint()
        if i >= 0 and sc not in ('half',) and sc not in ('teaser', 'teaser2'):
            pill(ctx, 150, 1040, 200, 50, '#141826', f'RIDDLE {i+1}/{N}', size=24)
        # caption plate
        g = cairo.LinearGradient(0, 0, 0, 220); g.add_color_stop_rgba(0, 0, 0, 0, 0.55); g.add_color_stop_rgba(1, 0, 0, 0, 0); ctx.set_source(g); ctx.rectangle(0, 0, W, 220); ctx.fill()
        caption(ctx, b.get('en'), t, t0, t1, y=110, size=54, maxw=1500)
    return draw

def sfx_list(tl):
    sfx = []
    for k, b in enumerate(tl.beats):
        if k: sfx.append((b['t0'] - 0.12, 'whoosh', 0.5))
        sc = b['sc']
        if sc == 'teaser': sfx.append((b['t0'] + 0.5, 'thud', 0.7))
        if sc == 'room': sfx.append((b['t0'] + 0.3, 'creak', 0.6))
        if sc == 'pause':
            for s in range(5): sfx.append((b['t1'] + s, 'tick', 0.5))
        if sc == 'wrong':
            for s in range(2): sfx.append((b['t0'] + 0.3 + 0.9*s, 'wrong', 0.45))
        if sc == 'reveal': sfx.append((b['t0'] + 0.3, 'right', 0.6))
        if sc == 'why': sfx.append((b['t1'] - 1.2, 'pop', 0.6))
    return sfx

if __name__ == '__main__':
    mode = sys.argv[1]
    OUT = '/home/claude/long/out'; os.makedirs(OUT, exist_ok=True)
    tl, beats = build(); total = tl.end + 0.5; draw = draw_factory(tl)
    print('TOTAL', round(total, 1))
    if mode == 'stills':
        ids = sys.argv[2].split(',') if len(sys.argv) > 2 else ['t1', 'r0_a', 'r0_d0', 'r0_d1', 'r0_d2', 'r0_q', 'r0_p', 'r0_x', 'r0_r', 'r0_w', 'r1_d1', 'r2_d0', 'r3_d0', 'r4_d2', 'r5_d1', 'e1']
        for k, bid in enumerate(ids):
            b = tl.by[bid]; tt = b['t1'] - 0.1 if b['sc'] != 'pause' else b['t1'] + 2.3
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt); surf.write_to_png(f'{OUT}/s{k:02d}.png')
    elif mode == 'audio':
        build_mix(f'{OUT}/long.wav', tl, sfx_list(tl), total)
        import json
        ch = [(0, 'Intro')] + [(tl.by[f'r{k}_a']['t0'], f'Riddle {k+1}: {TITLES[k]}') for k in range(len(R))] + [(tl.by['e1']['t0'], 'Your score')]
        json.dump(dict(total=total, ch=ch), open(f'{OUT}/meta.json', 'w'))
    elif mode == 'video':
        part, nparts = int(sys.argv[2]), int(sys.argv[3])
        nf = int(total*30); a = nf*part//nparts; z = nf*(part+1)//nparts
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
               '-b:v', '1000k', '-maxrate', '1600k', '-bufsize', '3200k', '-pix_fmt', 'yuv420p', f'{OUT}/part{part}.mp4']
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
        for fi in range(a, z):
            ctx.save(); draw(ctx, fi/30); ctx.restore(); surf.flush(); p.stdin.write(surf.get_data())
            if fi % 600 == 0: print(part, fi, z, flush=True)
        p.stdin.close(); p.wait()
