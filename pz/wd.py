"""Whodunit Shorts engine (Kunjikadhakal mystery format): dark spotlight stage, 3 suspects, 1 truth / 2 lies."""
import sys, math, random, itertools, cairo
sys.path.insert(0, '/home/claude/pz')
from pz import (Timeline, voice, wav_dur, clamp, smooth, lerp, prog, sprog, back, hexc, rrect, fill_stroke, OUT,
                build_audio, sfx2, SR, A)
import numpy as np, soundfile as sf, subprocess, os

W, H = 1080, 1920
FONT = 'Poppins'
NARR = ('male', 1.15, 1.20)   # matches the reference narrator (~155 Hz, fast)
FLOOR = 1500                  # stage floor line (feet)

# ------------------------------------------------------------------ logic
def truth(stmt, killer, truths):
    k = stmt[0]
    if k == 'did': return killer == stmt[1]
    if k == 'not': return killer != stmt[1]
    if k == 'liar': return not truths.get(stmt[1], None) if stmt[1] in truths else None
    if k == 'honest': return truths.get(stmt[1]) if stmt[1] in truths else None
    raise ValueError(k)

def evaluate(names, stmts, killer):
    """returns list of truth values; resolves 'liar'/'honest' statements about others (iterates to a fixpoint)"""
    tv = {}
    for n in names:
        if stmts[n][0] in ('did', 'not'): tv[n] = truth(stmts[n], killer, {})
    for _ in range(5):
        for n in names:
            if stmts[n][0] in ('liar', 'honest') and stmts[n][1] in tv:
                tv[n] = truth(stmts[n], killer, tv)
    return [tv.get(n) for n in names]

def solve(names, stmts, n_true=1):
    sols = []
    for k in names:
        tv = evaluate(names, stmts, k)
        if None in tv: continue
        if sum(tv) == n_true: sols.append(k)
    return sols

# ------------------------------------------------------------------ text
def text(ctx, s, x, y, size, col='#ffffff', align='c', weight=cairo.FONT_WEIGHT_BOLD, alpha=1.0, font=FONT):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, weight); ctx.set_font_size(size)
    xb, yb, w, h, xa, ya = ctx.text_extents(s)
    if align == 'c': x0 = x - (w/2 + xb)
    elif align == 'r': x0 = x - (w + xb)
    else: x0 = x - xb
    ctx.move_to(x0, y); ctx.set_source_rgba(*hexc(col, alpha)); ctx.show_text(s); ctx.new_path()
    return w

def text_w(ctx, s, size, font=FONT):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
    return ctx.text_extents(s)[4]

def caption(ctx, s, t, t0, t1, y=230, size=60, maxw=940):
    """top caption, *word* = yellow; words reveal progressively while spoken"""
    if not s: return
    words = s.split(); out = []
    for w_ in words:
        hl = '*' in w_
        out.append((w_.replace('*', ''), hl))
    # wrap
    lines, cur, cw = [], [], 0
    sp = text_w(ctx, ' ', size)
    for wd, hl in out:
        ww = text_w(ctx, wd, size)
        if cur and cw + sp + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((wd, hl, ww)); cw += (sp if cw else 0) + ww
    if cur: lines.append(cur)
    n = len(out); i = 0
    dur = max(0.4, (t1 - t0)*0.85)
    for li, line in enumerate(lines):
        tw = sum(w for _, _, w in line) + sp*(len(line)-1)
        x = W/2 - tw/2; yy = y + li*size*1.22
        for wd, hl, ww in line:
            rev = clamp((t - t0 - dur*i/n)/0.12)
            a = 0.25 + 0.75*rev
            text(ctx, wd, x, yy, size, '#ffd23f' if hl else '#ffffff', align='l', alpha=a)
            x += ww + sp; i += 1

# ------------------------------------------------------------------ backdrop
def backdrop(ctx, t, police=True, lamp_x=W/2, cone=True, floor=True, cone_w=380):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#1b2033')); g.add_color_stop_rgba(1, *hexc('#0c0e18'))
    ctx.set_source(g); ctx.paint()
    if police:
        for (cx, cy, col, ph) in ((140, 560, '#ff2d55', 0), (940, 520, '#2d6bff', math.pi)):
            a = 0.30 + 0.18*math.sin(t*5 + ph)
            rg = cairo.RadialGradient(cx, cy, 10, cx, cy, 420); rg.add_color_stop_rgba(0, *hexc(col, a)); rg.add_color_stop_rgba(1, *hexc(col, 0))
            ctx.set_source(rg); ctx.paint()
    if floor:
        ctx.rectangle(0, FLOOR-40, W, H-FLOOR+40); ctx.set_source_rgba(*hexc('#3a2a1e')); ctx.fill()
        ctx.set_source_rgba(0, 0, 0, 0.35); ctx.set_line_width(3)
        for k in range(1, 9): ctx.move_to(0, FLOOR-40+k*58); ctx.line_to(W, FLOOR-40+k*58); ctx.stroke()
        for k in range(0, 12):
            x = (k*137) % W; row = k % 8
            ctx.move_to(x, FLOOR-40+row*58); ctx.line_to(x, FLOOR-40+(row+1)*58); ctx.stroke()
        fg = cairo.LinearGradient(0, FLOOR-40, 0, H); fg.add_color_stop_rgba(0, 0, 0, 0, 0); fg.add_color_stop_rgba(1, 0, 0, 0, 0.7)
        ctx.set_source(fg); ctx.rectangle(0, FLOOR-40, W, H); ctx.fill()
    if cone:
        spot(ctx, lamp_x, cone_w)

def spot(ctx, x, w=380, top=330, a=0.16):
    lg = cairo.LinearGradient(0, top, 0, FLOOR+60); lg.add_color_stop_rgba(0, 1, 0.96, 0.82, a); lg.add_color_stop_rgba(1, 1, 0.96, 0.82, a*0.45)
    ctx.move_to(x-70, top); ctx.line_to(x+70, top); ctx.line_to(x+w, FLOOR+60); ctx.line_to(x-w, FLOOR+60); ctx.close_path()
    ctx.set_source(lg); ctx.fill()
    rg = cairo.RadialGradient(x, top-20, 5, x, top-20, 140); rg.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.9); rg.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
    ctx.set_source(rg); ctx.arc(x, top-20, 140, 0, 2*math.pi); ctx.fill()
    ctx.save(); ctx.translate(x, FLOOR+40); ctx.scale(1, 0.16)
    rg = cairo.RadialGradient(0, 0, 10, 0, 0, w*0.9); rg.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.35); rg.add_color_stop_rgba(1, 1, 0.95, 0.8, 0)
    ctx.set_source(rg); ctx.arc(0, 0, w*0.9, 0, 2*math.pi); ctx.fill(); ctx.restore()

def tape(ctx, y, ang=-0.05, t=0.0, label='CRIME SCENE'):
    ctx.save(); ctx.translate(W/2, y); ctx.rotate(ang)
    ctx.rectangle(-W, -30, 2*W, 60); ctx.set_source_rgba(*hexc('#ffd400')); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.85); ctx.rectangle(-W, -30, 2*W, 4); ctx.fill(); ctx.rectangle(-W, 26, 2*W, 4); ctx.fill()
    off = (t*40) % 330
    x = -W - 330 + off
    while x < W:
        text(ctx, label + '  ×', x, 13, 30, '#111111', align='l'); x += 330
    ctx.restore()

def qmark(ctx, x, y, s=1.0, t=0.0, col='#ffd23f'):
    ctx.save(); ctx.translate(x, y + 8*math.sin(t*4 + x)); ctx.scale(s, s)
    text(ctx, '?', 0, 0, 120, col); ctx.restore()

def pill(ctx, x, y, w, h, col, label, tcol='#ffffff', size=44, p=1.0):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); s = back(p); ctx.scale(s, s)
    rrect(ctx, -w/2, -h/2, w, h, 14); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    icon = None
    if label.endswith(' ✓') or label.endswith(' ✕'): icon = label[-1]; label = label[:-2]
    tw = text_w(ctx, label, size); off = -(size*0.45) if icon else 0
    text(ctx, label, off, size*0.36, size, tcol)
    if icon:
        ix = off + tw/2 + size*0.55; ctx.set_source_rgba(*hexc(tcol)); ctx.set_line_width(size*0.13); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        r = size*0.28
        if icon == '✓': ctx.move_to(ix-r, 0); ctx.line_to(ix-r*0.25, r*0.75); ctx.line_to(ix+r, -r*0.8)
        else: ctx.move_to(ix-r*0.75, -r*0.75); ctx.line_to(ix+r*0.75, r*0.75); ctx.move_to(ix+r*0.75, -r*0.75); ctx.line_to(ix-r*0.75, r*0.75)
        ctx.stroke()
    ctx.restore()

def namebox(ctx, x, y, name, size=36, w=None):
    w = w or text_w(ctx, name, size) + 50
    rrect(ctx, x-w/2, y-30, w, 60, 12); ctx.set_source_rgba(*hexc('#141826')); ctx.fill_preserve()
    ctx.set_source_rgba(*hexc('#ffd23f')); ctx.set_line_width(4); ctx.stroke()
    text(ctx, name, x, y+13, size, '#ffffff')

def bubble(ctx, x, y, s, col='#1a1a1a', size=46, p=1.0, tail=-1):
    if p <= 0: return
    w = text_w(ctx, s, size) + 70; h = size + 46
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    rrect(ctx, -w/2, -h/2, w, h, 22); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.move_to(tail*30, h/2-2); ctx.line_to(tail*60, h/2+34); ctx.line_to(tail*70, h/2-2); ctx.close_path(); ctx.fill()
    text(ctx, s, 0, size*0.36, size, col); ctx.restore()

# ------------------------------------------------------------------ characters
SKIN = '#9a5b34'
def suspect(ctx, x, y, s, robe, t=0.0, pose='down', talk=0.0, cap=None, stache=True, mood='neutral', look=0.0, badge=True, hair='#1b1410'):
    """flat robed figure like the reference. y = feet."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    bob = 3*math.sin(t*2.2 + x*0.01)
    ctx.translate(0, bob)
    # robe
    ctx.move_to(-62, -330); ctx.curve_to(-70, -250, -82, -120, -88, 0); ctx.line_to(88, 0); ctx.curve_to(82, -120, 70, -250, 62, -330)
    ctx.curve_to(40, -350, -40, -350, -62, -330); ctx.close_path()
    ctx.set_source_rgba(*hexc(robe)); ctx.fill_preserve(); ctx.set_source_rgba(*OUT); ctx.set_line_width(5); ctx.stroke()
    ctx.set_source_rgba(0, 0, 0, 0.14); ctx.move_to(20, -330); ctx.curve_to(40, -200, 48, -100, 50, 0); ctx.line_to(88, 0); ctx.curve_to(82, -120, 70, -250, 62, -330); ctx.close_path(); ctx.fill()
    # collar V + badge
    ctx.move_to(-22, -340); ctx.line_to(0, -305); ctx.line_to(22, -340); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(7); ctx.stroke()
    if badge:
        rrect(ctx, -30, -270, 60, 26, 4); ctx.set_source_rgba(*hexc('#111111')); ctx.fill()
    # arms
    def arm(side, pts):
        ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]
        ctx.set_source_rgba(*OUT); ctx.set_line_width(36); ctx.stroke_preserve()
        ctx.set_source_rgba(*hexc(robe)); ctx.set_line_width(28); ctx.stroke()
        hx, hy = pts[-1]; ctx.arc(hx, hy, 15, 0, 2*math.pi); fill_stroke(ctx, SKIN, 4)
    sh = -300
    if pose == 'down':
        arm(-1, [(-58, sh), (-74, -200), (-70, -130)]); arm(1, [(58, sh), (74, -200), (70, -130)])
    elif pose == 'point':
        arm(-1, [(-58, sh), (-74, -200), (-70, -130)]); arm(1, [(58, sh), (170, sh-10), (250, sh-20)])
    elif pose == 'up':
        w_ = 12*math.sin(t*10)
        arm(-1, [(-58, sh), (-120, sh-80+w_), (-108, sh-170+w_)]); arm(1, [(58, sh), (120, sh-80-w_), (108, sh-170-w_)])
    elif pose == 'chest':
        arm(-1, [(-58, sh), (-60, -230), (-16, -230)]); arm(1, [(58, sh), (60, -230), (16, -230)])
    elif pose == 'shrug':
        arm(-1, [(-58, sh), (-130, -230), (-150, -280)]); arm(1, [(58, sh), (130, -230), (150, -280)])
    # head
    hy = -400
    ctx.arc(0, hy, 62, 0, 2*math.pi); fill_stroke(ctx, SKIN, 5)
    for sx in (-60, 60): ctx.arc(sx, hy+6, 13, 0, 2*math.pi); fill_stroke(ctx, SKIN, 4)
    # hair / caps
    if cap == 'police':
        ctx.move_to(-66, hy-28); ctx.curve_to(-60, hy-92, 60, hy-92, 66, hy-28); ctx.close_path(); fill_stroke(ctx, '#2c3e66', 5)
        rrect(ctx, -76, hy-36, 152, 22, 8); fill_stroke(ctx, '#1d2a48', 4)
        ctx.arc(0, hy-58, 11, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#ffd23f')); ctx.fill()
    elif cap == 'kufi':
        ctx.move_to(-56, hy-30); ctx.curve_to(-50, hy-80, 50, hy-80, 56, hy-30); ctx.close_path(); fill_stroke(ctx, '#f2f2f2', 5)
    elif cap == 'bun':
        ctx.set_source_rgba(*hexc(hair)); ctx.arc(0, hy-70, 30, 0, 2*math.pi); ctx.fill()
        for k in range(5): ctx.set_source_rgba(1, 1, 1, 1); ctx.arc(-28+k*14, hy-96+abs(k-2)*4, 6, 0, 2*math.pi); ctx.fill()
        ctx.move_to(-66, hy+30); ctx.curve_to(-76, hy-80, 76, hy-80, 66, hy+30); ctx.curve_to(50, hy-30, -50, hy-30, -66, hy+30); ctx.close_path()
        ctx.set_source_rgba(*hexc(hair)); ctx.fill_preserve(); ctx.set_source_rgba(*OUT); ctx.set_line_width(4); ctx.stroke()
    elif cap == 'bald':
        ctx.set_source_rgba(*hexc(hair)); ctx.arc(-50, hy-6, 16, 0, 2*math.pi); ctx.arc(50, hy-6, 16, 0, 2*math.pi); ctx.fill()
    else:
        ctx.move_to(-63, hy-4); ctx.curve_to(-70, hy-75, 60, hy-90, 64, hy-8); ctx.curve_to(40, hy-40, -20, hy-44, -63, hy-4); ctx.close_path()
        ctx.set_source_rgba(*hexc(hair)); ctx.fill_preserve(); ctx.set_source_rgba(*OUT); ctx.set_line_width(4); ctx.stroke()
    # eyes
    blink = (t + x*0.003) % 3.3 < 0.12
    for ex in (-22, 22):
        if blink:
            ctx.set_source_rgba(*OUT); ctx.set_line_width(5); ctx.move_to(ex-13, hy-4); ctx.line_to(ex+13, hy-4); ctx.stroke(); continue
        ctx.arc(ex, hy-4, 17, 0, 2*math.pi); fill_stroke(ctx, '#ffffff', 4)
        ctx.set_source_rgba(*hexc('#111111')); ctx.arc(ex+look*6, hy-2, 8, 0, 2*math.pi); ctx.fill()
    ctx.set_source_rgba(*OUT); ctx.set_line_width(6)
    if mood in ('angry', 'sus'):
        ctx.move_to(-38, hy-34); ctx.line_to(-10, hy-26); ctx.move_to(38, hy-34); ctx.line_to(10, hy-26); ctx.stroke()
    elif mood == 'scared':
        ctx.move_to(-36, hy-26); ctx.line_to(-10, hy-34); ctx.move_to(36, hy-26); ctx.line_to(10, hy-34); ctx.stroke()
    else:
        ctx.move_to(-36, hy-30); ctx.line_to(-10, hy-32); ctx.move_to(36, hy-30); ctx.line_to(10, hy-32); ctx.stroke()
    if stache:
        ctx.move_to(-30, hy+30); ctx.curve_to(-20, hy+18, -4, hy+18, 0, hy+26); ctx.curve_to(4, hy+18, 20, hy+18, 30, hy+30)
        ctx.curve_to(14, hy+30, 6, hy+32, 0, hy+30); ctx.curve_to(-6, hy+32, -14, hy+30, -30, hy+30); ctx.close_path()
        ctx.set_source_rgba(*hexc('#1b1410')); ctx.fill()
    o = talk
    my = hy + 42
    if o > 0.05:
        ctx.save(); ctx.translate(0, my); ctx.scale(1, 0.35 + o); ctx.arc(0, 0, 12, 0, 2*math.pi); ctx.restore()
        ctx.set_source_rgba(*hexc('#4a1616')); ctx.fill()
    else:
        ctx.set_source_rgba(*OUT); ctx.set_line_width(5)
        if mood == 'scared': ctx.arc(0, my+8, 10, math.pi+0.4, -0.4)
        else: ctx.move_to(-12, my); ctx.line_to(12, my)
        ctx.stroke()
    ctx.restore()

def mini_icon(ctx, x, y, robe, cap=None, s=0.18):
    suspect(ctx, x, y, s, robe, pose='down', cap=cap, badge=False)

def avatar(ctx, x, y, r=62, name='', p=1.0, t=0.0):
    if p <= 0: return
    ctx.new_path()
    ctx.save(); ctx.translate(x, y); sc = back(p); ctx.scale(sc, sc)
    ctx.arc(0, 0, r, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#2a3145')); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(5); ctx.stroke()
    ctx.save(); ctx.arc(0, 0, r-5, 0, 2*math.pi); ctx.clip()
    ctx.set_source_rgba(*hexc('#8b93a8')); ctx.arc(0, -14, r*0.36, 0, 2*math.pi); ctx.fill()
    ctx.save(); ctx.translate(0, r*0.85); ctx.scale(1, 0.75); ctx.arc(0, 0, r*0.72, 0, 2*math.pi); ctx.restore(); ctx.fill()
    ctx.restore()
    text(ctx, '?', 0, -r-26 + 5*math.sin(t*4+x), 60, '#ffd23f')
    text(ctx, name.upper(), 0, r+48, 30, '#ffffff')
    ctx.restore()

# ------------------------------------------------------------------ scenes
def flat(ctx, t, s):
    """houseboat on the backwater at night with one red window (generic 'crime location' card)"""
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc('#0a0f24')); g.add_color_stop_rgba(1, *hexc('#1b2550'))
    ctx.set_source(g); ctx.paint()
    rnd = random.Random(3)
    for k in range(90):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 1100); a = 0.4 + 0.4*math.sin(t*3 + k)
        ctx.set_source_rgba(1, 1, 1, a); ctx.arc(x, y, rnd.uniform(1.5, 3.5), 0, 2*math.pi); ctx.fill()
    ctx.set_source_rgba(1, 0.97, 0.85, 0.95); ctx.arc(880, 520, 70, 0, 2*math.pi); ctx.fill()
    ctx.set_source_rgba(*hexc('#0a0f24')); ctx.arc(850, 505, 62, 0, 2*math.pi); ctx.fill()
    scene = s.get('place', 'houseboat')
    if scene == 'houseboat':
        # palms on the far bank
        ctx.set_source_rgba(*hexc('#08101e'))
        ctx.rectangle(0, 1180, W, 40); ctx.fill()
        for px in (80, 260, 700, 980):
            ctx.move_to(px, 1190); ctx.curve_to(px+10, 1050, px+30, 980, px+40, 900); ctx.set_line_width(14); ctx.stroke()
            for kk in range(6):
                a = -math.pi/2 + (kk-2.5)*0.6; ctx.move_to(px+40, 900); ctx.line_to(px+40+math.cos(a)*110, 900+math.sin(a)*110+40); ctx.set_line_width(12); ctx.stroke()
        ctx.rectangle(0, 1220, W, H); ctx.set_source_rgba(*hexc('#0d1838')); ctx.fill()
        for k in range(14):
            yy = 1260 + k*45; xx = (k*97 + t*30) % W
            ctx.set_source_rgba(0.6, 0.7, 1, 0.18); ctx.rectangle(xx, yy, 140, 4); ctx.fill()
        # boat
        bx, by = W/2, 1240 + 6*math.sin(t*1.5)
        ctx.move_to(bx-430, by-40); ctx.curve_to(bx-380, by+60, bx+380, by+60, bx+430, by-40); ctx.close_path(); fill_stroke(ctx, '#5a3a22', 6)
        ctx.move_to(bx-360, by-40); ctx.curve_to(bx-340, by-260, bx+340, by-260, bx+360, by-40); ctx.close_path(); fill_stroke(ctx, '#c79a55', 6)
        ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(4)
        for k in range(-6, 7): ctx.move_to(bx+k*55, by-40); ctx.line_to(bx+k*52, by-190+abs(k)*12); ctx.stroke()
        for k, wx in enumerate((-250, -110, 30, 170)):
            red = (k == 2)
            a = 1.0 if not red else 0.75 + 0.25*math.sin(t*6)
            rrect(ctx, bx+wx, by-150, 90, 70, 10)
            ctx.set_source_rgba(*(hexc('#ff2a2a', a) if red else hexc('#ffb84a'))); ctx.fill()
            if red:
                rg = cairo.RadialGradient(bx+wx+45, by-115, 10, bx+wx+45, by-115, 260); rg.add_color_stop_rgba(0, 1, 0.1, 0.1, 0.45*a); rg.add_color_stop_rgba(1, 1, 0, 0, 0)
                ctx.set_source(rg); ctx.paint()
    if scene == 'tea':
        # Munnar tea hills at night: layered hills with tea-row stripes and a bungalow with one red window
        for k, (y0, col) in enumerate(((1000, '#0f2a24'), (1150, '#143a30'), (1320, '#1a4a3a'))):
            ctx.move_to(0, y0+80)
            for xx in range(0, W+60, 60): ctx.line_to(xx, y0 + 60*math.sin(xx/260 + k*1.7))
            ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
            ctx.set_source_rgba(0.5, 0.9, 0.6, 0.10); ctx.set_line_width(6)
            for r in range(1, 8):
                ctx.move_to(0, y0+r*34+80)
                for xx in range(0, W+60, 60): ctx.line_to(xx, y0 + r*34 + 60*math.sin(xx/260 + k*1.7) + 10)
                ctx.stroke()
        bx, by = 300, 1060
        ctx.rectangle(bx-130, by-110, 260, 120); fill_stroke(ctx, '#e8dcc0', 5)
        ctx.move_to(bx-160, by-110); ctx.line_to(bx, by-200); ctx.line_to(bx+160, by-110); ctx.close_path(); fill_stroke(ctx, '#7a2e22', 5)
        a = 0.75 + 0.25*math.sin(t*6)
        for k, wx in enumerate((-90, 30)):
            rrect(ctx, bx+wx, by-85, 60, 50, 6); ctx.set_source_rgba(*(hexc('#ff2a2a', a) if k == 1 else hexc('#ffb84a'))); ctx.fill()
        rg = cairo.RadialGradient(bx+60, by-60, 10, bx+60, by-60, 260); rg.add_color_stop_rgba(0, 1, 0.1, 0.1, 0.4*a); rg.add_color_stop_rgba(1, 1, 0, 0, 0)
        ctx.set_source(rg); ctx.paint()
        for k in range(5):
            mx = (k*260 + t*25) % (W+300) - 150
            ctx.set_source_rgba(0.85, 0.9, 1, 0.07); ctx.save(); ctx.translate(mx, 960+k*40); ctx.scale(3, 0.5); ctx.arc(0, 0, 90, 0, 2*math.pi); ctx.restore(); ctx.fill()
    if scene == 'beach':
        # Kovalam: sea, lighthouse with sweeping beam, palms, resort cottage with one red window
        ctx.rectangle(0, 1150, W, 300); ctx.set_source_rgba(*hexc('#0c1a3e')); ctx.fill()
        for k in range(10):
            yy = 1170 + k*28; xx = (k*131 + t*40) % W
            ctx.set_source_rgba(0.6, 0.75, 1, 0.20); ctx.rectangle(xx, yy, 160, 4); ctx.fill()
        ctx.move_to(0, 1450); ctx.curve_to(300, 1400, 700, 1420, W, 1380); ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path()
        ctx.set_source_rgba(*hexc('#3a3046')); ctx.fill()
        # headland + lighthouse
        ctx.move_to(620, 1160); ctx.curve_to(720, 1020, 900, 1000, W, 1010); ctx.line_to(W, 1160); ctx.close_path(); ctx.set_source_rgba(*hexc('#101a2c')); ctx.fill()
        lx, ly = 700, 1040
        ang = math.sin(t*1.2)*0.9
        ctx.save(); ctx.translate(lx, ly-330); ctx.rotate(ang)
        lg = cairo.LinearGradient(0, 0, -900, 0); lg.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.45); lg.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
        ctx.move_to(0, 0); ctx.line_to(-900, -110); ctx.line_to(-900, 110); ctx.close_path(); ctx.set_source(lg); ctx.fill(); ctx.restore()
        for k in range(6):
            y0 = ly - k*50; w0 = 60 - k*4
            ctx.move_to(lx-w0, y0); ctx.line_to(lx+w0, y0); ctx.line_to(lx+w0-4, y0-50); ctx.line_to(lx-w0+4, y0-50); ctx.close_path()
            fill_stroke(ctx, '#e8283c' if k % 2 else '#f4f1e8', 4)
        rrect(ctx, lx-40, ly-350, 80, 50, 8); fill_stroke(ctx, '#ffe9a8', 4)
        ctx.move_to(lx-48, ly-350); ctx.line_to(lx, ly-400); ctx.line_to(lx+48, ly-350); ctx.close_path(); fill_stroke(ctx, '#2a2a3a', 4)
        # palms
        ctx.set_source_rgba(*hexc('#060b16'))
        for px, h0 in ((90, 560), (980, 480)):
            ctx.move_to(px, 1470); ctx.curve_to(px+20, 1300, px+60, 1100, px+80, 1470-h0); ctx.set_line_width(16); ctx.stroke()
            for kk in range(7):
                a = -math.pi/2 + (kk-3)*0.55 + 0.05*math.sin(t*2+kk); ctx.move_to(px+80, 1470-h0)
                ctx.curve_to(px+80+math.cos(a)*80, 1470-h0+math.sin(a)*80, px+80+math.cos(a)*150, 1470-h0+math.sin(a)*120+30, px+80+math.cos(a)*170, 1470-h0+math.sin(a)*110+80)
                ctx.set_line_width(11); ctx.stroke()
        # cottage
        bx, by = 330, 1430
        ctx.rectangle(bx-140, by-150, 280, 150); fill_stroke(ctx, '#d9c79c', 5)
        ctx.move_to(bx-180, by-150); ctx.line_to(bx, by-260); ctx.line_to(bx+180, by-150); ctx.close_path(); fill_stroke(ctx, '#6b4a2a', 5)
        a = 0.75 + 0.25*math.sin(t*6)
        for k, wx in enumerate((-100, 30)):
            rrect(ctx, bx+wx, by-120, 70, 60, 6); ctx.set_source_rgba(*(hexc('#ff2a2a', a) if k == 1 else hexc('#ffb84a'))); ctx.fill()
        rg = cairo.RadialGradient(bx+65, by-90, 10, bx+65, by-90, 280); rg.add_color_stop_rgba(0, 1, 0.1, 0.1, 0.4*a); rg.add_color_stop_rgba(1, 1, 0, 0, 0)
        ctx.set_source(rg); ctx.paint()
    if scene == 'train':
        # night train on a river bridge (Bharathapuzha), coaches with lit windows, one red window
        ctx.set_source_rgba(*hexc('#08101e'))
        ctx.move_to(0, 1080)
        for xx in range(0, W+60, 60): ctx.line_to(xx, 1060 + 40*math.sin(xx/180))
        ctx.line_to(W, 1200); ctx.line_to(0, 1200); ctx.close_path(); ctx.fill()
        ctx.rectangle(0, 1200, W, H); ctx.set_source_rgba(*hexc('#0d1838')); ctx.fill()
        for k in range(14):
            yy = 1330 + k*30; xx = (k*97 + t*25) % W
            ctx.set_source_rgba(0.6, 0.7, 1, 0.16); ctx.rectangle(xx, yy, 140, 4); ctx.fill()
        # bridge deck + truss + pillars
        ctx.set_source_rgba(*hexc('#2a2f40')); ctx.rectangle(0, 1250, W, 26); ctx.fill()
        for px in range(60, W, 240):
            ctx.rectangle(px, 1276, 50, 300); ctx.set_source_rgba(*hexc('#1d2232')); ctx.fill()
        ctx.set_source_rgba(*hexc('#3a4058')); ctx.set_line_width(6)
        for k in range(0, W+120, 120):
            ctx.move_to(k, 1250); ctx.line_to(k+60, 1070); ctx.line_to(k+120, 1250); ctx.stroke()
        ctx.move_to(0, 1070); ctx.line_to(W, 1070); ctx.stroke()
        # coaches sliding slowly
        off = -(t*60) % 520
        for c in range(-1, 4):
            cx = off + c*520 - 260
            rrect(ctx, cx, 1100, 500, 145, 16); fill_stroke(ctx, '#7a2228', 5)
            ctx.set_source_rgba(*hexc('#d8c070')); ctx.rectangle(cx, 1200, 500, 10); ctx.fill()
            for wi in range(5):
                red = (c == 1 and wi == 2)
                a = 0.75 + 0.25*math.sin(t*6) if red else 1.0
                rrect(ctx, cx+30+wi*92, 1125, 64, 55, 6)
                ctx.set_source_rgba(*(hexc('#ff2a2a', a) if red else hexc('#ffc65a'))); ctx.fill()
                if red:
                    rg = cairo.RadialGradient(cx+62+wi*92, 1150, 10, cx+62+wi*92, 1150, 280); rg.add_color_stop_rgba(0, 1, 0.1, 0.1, 0.45*a); rg.add_color_stop_rgba(1, 1, 0, 0, 0)
                    ctx.set_source(rg); ctx.paint()
            for wx in (90, 410):
                ctx.set_source_rgba(0.05, 0.05, 0.08, 1); ctx.arc(cx+wx, 1250, 22, 0, 2*math.pi); ctx.fill()
    tape(ctx, 1640, -0.04, t)

def lineup(ctx, t, s, sus, beat_t0):
    backdrop(ctx, t, cone=False)
    for x in (200, 540, 880): spot(ctx, x, 230, a=0.12)
    xs = (200, 540, 880)
    for i, (x, c) in enumerate(zip(xs, sus)):
        p = back(prog(t, beat_t0 + i*0.12, 0.35))
        ctx.save(); ctx.translate(x, FLOOR); ctx.scale(1, p); ctx.translate(-x, -FLOOR)
        suspect(ctx, x, FLOOR, 0.95, c['robe'], t, cap=c.get('cap'), stache=c.get('stache', True), mood=c.get('mood', 'sus'), look=math.sin(t*1.5+i))
        ctx.restore()
        namebox(ctx, x, FLOOR+70, c['name'].upper(), 32)
        qmark(ctx, x, 760, 1.0, t)
    tape(ctx, FLOOR+170, -0.05, t)
    if s.get('fail'):
        p = prog(t, beat_t0 + 0.6, 0.35)
        ctx.save(); ctx.translate(W/2, FLOOR+330); ctx.rotate(-0.06); pill(ctx, 0, 0, 380, 110, '#e8283c', s['fail'], size=58, p=p); ctx.restore()
        ctx.set_source_rgba(1, 1, 1, 0.6); ctx.set_line_width(4); ctx.set_dash([18, 12])
        ctx.save(); ctx.translate(W/2, FLOOR+470); ctx.scale(1, 0.28); ctx.arc(0, 0, 240, 0, 2*math.pi); ctx.restore(); ctx.stroke(); ctx.set_dash([])

def police(ctx, t, s, sus, beat_t0):
    backdrop(ctx, t, cone=True, lamp_x=W/2, cone_w=330)
    for i, (x, sc) in enumerate(((190, 0.62), (890, 0.62))):
        c = sus[0] if i == 0 else sus[2]
        suspect(ctx, x, FLOOR-10, sc, c['robe'], t, cap=c.get('cap'), mood='scared')
        namebox(ctx, x, FLOOR+40, c['name'].upper(), 24)
    rrect(ctx, 210, FLOOR-90, 660, 40, 8); ctx.set_source_rgba(*hexc('#4a3424')); ctx.fill()
    suspect(ctx, W/2, FLOOR-90, 0.85, '#c8b07a', t, cap='police', mood='angry', talk=abs(math.sin(t*14))*0.6 if s.get('talking') else 0)
    c = sus[1]; suspect(ctx, W/2, FLOOR+170, 0.55, c['robe'], t, cap=c.get('cap'), mood='scared')

def rule(ctx, t, s, sus, beat_t0, show_truth, show_lies):
    backdrop(ctx, t, police=False, cone=False, floor=False)
    rg = cairo.RadialGradient(W/2, 900, 50, W/2, 900, 620); rg.add_color_stop_rgba(0, 1, 0.92, 0.7, 0.16); rg.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(rg); ctx.paint()
    for i, x in enumerate((240, 540, 840)):
        avatar(ctx, x, 1000, 92, sus[i]['name'], back(prog(t, beat_t0 + i*0.1, 0.35)), t)
    pill(ctx, W/2, 760, 330, 92, '#2fbf4f', '1 TRUTH ✓', size=48, p=show_truth)
    pill(ctx, W/2, 1260, 330, 92, '#e8283c', '2 LIES ✕', size=48, p=show_lies)

def solo(ctx, t, s, c, beat_t0, t1, idx):
    backdrop(ctx, t, cone=True, lamp_x=W/2)
    talk = 0.0
    if beat_t0 + 0.2 < t < t1 - 0.1: talk = clamp(abs(math.sin(t*13))*0.9)
    pose = s.get('pose', 'point')
    suspect(ctx, W/2-20, FLOOR+20, 1.25, c['robe'], t, pose=pose, talk=talk, cap=c.get('cap'), stache=c.get('stache', True),
            mood=s.get('mood', 'angry'), look=0.6 if pose == 'point' else 0)
    namebox(ctx, W/2-20, FLOOR+100, c['name'].upper(), 40)
    bubble(ctx, W/2+90, 830, s['bubble'], col=s.get('bubble_col', '#1a1a1a'), size=52, p=prog(t, beat_t0+0.35, 0.3), tail=-1)

def summary(ctx, t, s, sus, beat_t0, typing=None, follow=False):
    backdrop(ctx, t, police=False, cone=False, floor=False)
    rg = cairo.RadialGradient(W/2, 1000, 50, W/2, 1000, 800); rg.add_color_stop_rgba(0, *hexc('#3a2a7a', 0.45)); rg.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(rg); ctx.paint()
    pill(ctx, W/2, 640, 720, 84, '#ffd23f', s.get('rule_label', 'ONLY 1 TELLS THE TRUTH'), tcol='#141414', size=40, p=prog(t, beat_t0, 0.3))
    for i, c in enumerate(sus):
        p = back(prog(t, beat_t0 + 0.15 + i*0.12, 0.3))
        y = 790 + i*170
        ctx.save(); ctx.translate(W/2, y+65); ctx.scale(p, p); ctx.translate(-W/2, -(y+65))
        rrect(ctx, 150, y, 780, 130, 18); ctx.set_source_rgba(*hexc('#1d2236')); ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, 0.18); ctx.set_line_width(3); ctx.stroke()
        mini_icon(ctx, 215, y+122, c['robe'], c.get('cap'))
        text(ctx, c['name'].upper(), 275, y+52, 30, '#ffd23f', align='l')
        text(ctx, c['short'], 275, y+100, 38, '#ffffff', align='l')
        ctx.restore()
    if typing is not None:
        rrect(ctx, 250, 1360, 580, 110, 55); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        word = 'ANSWER'; n = int(clamp((t - typing)/1.0)*len(word)) if t >= typing else 0
        w_ = text(ctx, word[:n], W/2 - (text_w(ctx, word, 56)/2 if n else 0), 1436, 56, '#141414', align='l' if n else 'c') if n else 0
        cx = W/2 - text_w(ctx, word, 56)/2 + (text_w(ctx, word[:n], 56) if n else 0) + (6 if n else text_w(ctx, word, 56)/2)
        if (t*2) % 1 < 0.6:
            ctx.rectangle(cx, 1380, 8, 70); ctx.set_source_rgba(*hexc('#e8283c')); ctx.fill()
    if follow:
        p = 1 + 0.06*math.sin(t*8)
        ctx.save(); ctx.translate(W/2, 1550); ctx.scale(p, p)
        rrect(ctx, -170, -50, 340, 100, 50); ctx.set_source_rgba(*hexc('#2d6bff')); ctx.fill()
        text(ctx, '+ Follow', 0, 16, 46, '#ffffff'); ctx.restore()
        text(ctx, '@Kandupidii', W/2, 1660, 30, '#9aa3bd')

# ------------------------------------------------------------------ build
def build(case, out_dir, name, stills=False):
    sus = case['suspects']
    names = [c['name'] for c in sus]
    stmts = {c['name']: tuple(c['stmt']) for c in sus}
    sol = solve(names, stmts, case.get('n_true', 1))
    assert len(sol) == 1, f'puzzle must have exactly one answer, got {sol}'
    print('ANSWER:', sol[0])
    beats = []
    for b in case['beats']:
        d = dict(b); beats.append(d)
    tl = Timeline(beats, lead=0.15, gap=0.12, think=1.5, spk=NARR)
    total = tl.end + 0.8
    by = tl.by

    def draw(ctx, t):
        cur = None
        for b in tl.beats:
            if t >= b['t0'] - 0.12: cur = b
        b = cur or tl.beats[0]
        sc = b.get('scene', 'lineup'); t0 = b['t0']; t1 = b['t1']
        # quick punch-in on every cut
        z = 1.0 + 0.05*(1 - sprog(t, t0-0.12, 0.35)) + 0.02*prog(t, t0, t1-t0+0.5)
        ctx.save(); ctx.translate(W/2, H/2); ctx.scale(z, z); ctx.translate(-W/2, -H/2)
        if sc == 'lineup': lineup(ctx, t, b, sus, t0)
        elif sc == 'place': flat(ctx, t, b)
        elif sc == 'police': police(ctx, t, b, sus, t0)
        elif sc == 'rule':
            first = [x for x in tl.beats if x.get('scene') == 'rule'][0]
            lies_t = b['t0'] + b.get('lies_dt', 99) if b.get('lies') else 99
            rule(ctx, t, b, sus, first['t0'], prog(t, b['t0'] + b.get('truth_dt', 0.6), 0.3) if b.get('truth') or b is not first else 0,
                 prog(t, lies_t, 0.3))
        elif sc == 'solo':
            i = b['who']; solo(ctx, t, b, sus[i], t0, t1, i)
        elif sc == 'summary':
            summary(ctx, t, b, sus, [x for x in tl.beats if x.get('scene') == 'summary'][0]['t0'],
                    typing=(t0 + b.get('type_dt', 0.8)) if b.get('typing') else None, follow=b.get('follow', False))
        ctx.restore()
        # flash on cuts
        fl = 1 - prog(t, t0 - 0.12, 0.12)
        if 0 < fl < 1 and b is not tl.beats[0]:
            ctx.set_source_rgba(1, 1, 1, 0.25*fl); ctx.paint()
        cap_y = b.get('cap_y', 230)
        caption(ctx, b.get('en'), t, t0, t1, y=cap_y)

    os.makedirs(out_dir, exist_ok=True)
    if stills:
        pts = [b['t0'] + (b['t1']-b['t0'])*0.8 for b in tl.beats]
        for i, tt in enumerate(pts):
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt)
            surf.write_to_png(f'{out_dir}/{name}.still{i:02d}.png')
        return tl, sol[0]
    sfx = []
    for i, b in enumerate(tl.beats):
        if i: sfx.append((b['t0']-0.12, 'whoosh', 0.55))
        sc = b.get('scene')
        if sc == 'lineup' and b.get('fail'): sfx.append((b['t0']+0.6, 'thud', 0.7))
        if sc == 'rule' and b.get('truth'): sfx.append((b['t0']+b.get('truth_dt', 0.6), 'right', 0.6))
        if sc == 'rule' and b.get('lies'): sfx.append((b['t0']+b.get('lies_dt', 2.0), 'wrong', 0.6))
        if sc == 'solo': sfx.append((b['t0']+0.35, 'pop', 0.7))
        if b.get('typing'):
            for k in range(6): sfx.append((b['t0']+b.get('type_dt', 0.8)+k*0.17, 'tick', 0.25))
    music = [(0, total, 'suspense')]
    aud = f'{out_dir}/{name}.wav'
    build_mix(aud, tl, sfx, total)
    render_raw(f'{out_dir}/{name}.mp4', total, draw, aud)
    return tl, sol[0]

def suspense_bed(dur):
    """dark ticking suspense bed: low drone + pulsing bass + clock ticks"""
    n = int(dur*SR); t = np.arange(n)/SR
    drone = 0.25*np.sin(2*np.pi*55*t) + 0.15*np.sin(2*np.pi*82.4*t) + 0.08*np.sin(2*np.pi*110*t*(1+0.002*np.sin(t)))
    pulse = np.sin(2*np.pi*55*t) * (np.mod(t, 0.6) < 0.18) * np.exp(-np.mod(t, 0.6)*10) * 0.9
    tick = np.zeros(n)
    for k in range(int(dur/0.3)):
        i0 = int(k*0.3*SR); m = int(0.02*SR)
        if i0+m < n: tick[i0:i0+m] += np.sin(2*np.pi*(2400 if k % 2 else 1800)*np.arange(m)/SR)*np.exp(-np.arange(m)/SR*200)*0.25
    hi = A.lp(np.random.default_rng(1).standard_normal(n), 900)*0.05
    return drone + pulse + tick + hi

def build_mix(path, tl, sfx, total):
    n = int((total+1)*SR); v = np.zeros(n); fx = np.zeros(n)
    for b in tl.beats:
        if b['wav']:
            y, sr = sf.read(b['wav']); y = y if y.ndim == 1 else y.mean(1); A.add(v, y, int(b['t0']*SR))
    for (t, kind, g) in sfx:
        s_ = sfx2(kind)*g; A.add(fx, s_ if kind != 'tick' else s_[:int(0.05*SR)], int(t*SR))
    bed = suspense_bed(total+1); bed = bed/np.abs(bed).max()
    env = np.convolve(np.abs(v), np.ones(int(0.2*SR))/int(0.2*SR), mode='same'); duck = 1 - 0.5*np.clip(env/0.05, 0, 1)
    mix = (v*1.0 + bed[:n]*0.22*duck + fx*0.7)[:int(total*SR)]
    tmp = path + '.tmp.wav'; sf.write(tmp, mix.astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '44100', path], check=True); os.remove(tmp)

def render_raw(out, total, draw, audio, fps=30):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-i', audio,
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    for i in range(int(total*fps)):
        ctx.save(); draw(ctx, i/fps); ctx.restore(); surf.flush(); p.stdin.write(surf.get_data())
    p.stdin.close(); p.wait()
