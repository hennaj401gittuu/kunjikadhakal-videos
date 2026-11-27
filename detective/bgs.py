"""Detective Arjun episode backgrounds (pycairo, 1920x1080 world, cached at 2x for camera zooms).
Kerala palace museum exterior (night), gallery interior (dark / lit), store room, line-up room, parking."""
import math, random, cairo
from chars import hexc, mix, lt, dk, shade, vshade, ellipse, rrect, outline
W, H = 1920, 1080
SC = 2
FLOOR = 980   # gallery floor line used by characters

def lin(ctx, x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, c in stops: g.add_color_stop_rgba(o, *(hexc(c) if isinstance(c, str) else c))
    return g
def rad(x, y, r0, r1, stops):
    g = cairo.RadialGradient(x, y, r0, x, y, r1)
    for o, c in stops: g.add_color_stop_rgba(o, *c)
    return g

def glow(ctx, x, y, r, col=(1, 0.8, 0.45), a=0.55):
    ctx.set_source(rad(x, y, 0, r, [(0, (*col, a)), (0.4, (*col, a*0.35)), (1, (*col, 0))])); ctx.arc(x, y, r, 0, 2*math.pi); ctx.fill()

def palm(ctx, x, y, s, col='#0b1020', sway=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgba(*hexc(col)); ctx.set_line_width(20); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0, 0); ctx.curve_to(15, -160, 40, -320, 70, -470); ctx.stroke()
    ctx.translate(70, -470)
    for k in range(9):
        a = -math.pi/2 + (k-4)*0.42 + sway
        ctx.move_to(0, 0); ctx.curve_to(math.cos(a)*100, math.sin(a)*80-25, math.cos(a)*190, math.sin(a)*100+20, math.cos(a)*235, math.sin(a)*90+110)
        ctx.curve_to(math.cos(a)*170, math.sin(a)*90+25, math.cos(a)*90, math.sin(a)*55, 0, 12); ctx.close_path(); ctx.fill()
    ctx.restore()

def tiles_roof(ctx, pts, col, lines=14):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ys = [p[1] for p in pts]; xs = [p[0] for p in pts]
    ctx.set_source(lin(ctx, 0, min(ys), 0, max(ys), [(0, lt(col, 0.08)), (1, dk(col, 0.35))])); ctx.fill_preserve()
    ctx.save(); ctx.clip()
    for k in range(lines+1):
        y = min(ys) + (max(ys)-min(ys))*k/lines
        ctx.move_to(min(xs), y); ctx.line_to(max(xs), y); ctx.set_source_rgba(0, 0, 0, 0.22); ctx.set_line_width(2.5); ctx.stroke()
    for k in range(int((max(xs)-min(xs))/22)):
        x = min(xs) + k*22; ctx.move_to(x, min(ys)); ctx.line_to(x, max(ys)); ctx.set_source_rgba(1, 1, 1, 0.04); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); outline(ctx, 2.5, 0.5)

def gable(ctx, cx, y, w, h, col='#6a3a22'):
    ctx.move_to(cx - w/2, y); ctx.line_to(cx, y - h); ctx.line_to(cx + w/2, y); ctx.close_path()
    ctx.set_source(lin(ctx, 0, y-h, 0, y, [(0, lt(col, 0.1)), (1, dk(col, 0.3))])); ctx.fill_preserve(); outline(ctx, 2, 0.5)
    ctx.save(); ctx.move_to(cx - w/2 + 14, y - 6); ctx.line_to(cx, y - h + 16); ctx.line_to(cx + w/2 - 14, y - 6); ctx.close_path(); ctx.clip()
    for k in range(-12, 13):
        ctx.move_to(cx + k*14, y); ctx.line_to(cx + k*14 + 60, y - h); ctx.move_to(cx + k*14, y); ctx.line_to(cx + k*14 - 60, y - h)
    ctx.set_source_rgba(1, 0.85, 0.55, 0.25); ctx.set_line_width(2); ctx.stroke(); ctx.restore()
    ctx.arc(cx, y - h + 6, 8, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#d8a83a')); ctx.fill()

def window_lit(ctx, x, y, w, h, lit=True):
    rrect(ctx, x-6, y-6, w+12, h+12, 4); ctx.set_source_rgba(*hexc('#3a2216')); ctx.fill()
    ctx.rectangle(x, y, w, h)
    ctx.set_source(lin(ctx, 0, y, 0, y+h, [(0, '#ffd890' if lit else '#1a2040'), (1, '#e89a40' if lit else '#10142a')])); ctx.fill()
    for k in range(1, 4): ctx.rectangle(x + w*k/4 - 2, y, 4, h); ctx.set_source_rgba(*hexc('#3a2216')); ctx.fill()
    ctx.rectangle(x, y + h/2 - 2, w, 4); ctx.fill()
    if lit: glow(ctx, x + w/2, y + h/2, w*1.3, a=0.25)

def ext_night():
    def d(ctx):
        ctx.set_source(lin(ctx, 0, 0, 0, 760, [(0, '#070b26'), (0.55, '#1d1f52'), (1, '#4a3170')])); ctx.paint()
        rnd = random.Random(7)
        for k in range(160):
            x, y = rnd.uniform(0, W), rnd.uniform(0, 520); r = rnd.uniform(0.6, 2.0)
            ctx.arc(x, y, r, 0, 2*math.pi); ctx.set_source_rgba(1, 1, 0.95, rnd.uniform(0.25, 0.9)); ctx.fill()
        glow(ctx, 1560, 190, 260, (0.85, 0.9, 1.0), 0.35)
        ctx.arc(1560, 190, 62, 0, 2*math.pi); ctx.set_source(rad(1545, 175, 5, 70, [(0, (1, 1, 0.96, 1)), (1, (0.86, 0.88, 0.95, 1))])); ctx.fill()
        for (cx, cy, r) in ((1540, 170, 10), (1580, 205, 7), (1565, 225, 5)): ctx.arc(cx, cy, r, 0, 2*math.pi); ctx.set_source_rgba(0.7, 0.72, 0.82, 0.5); ctx.fill()
        # wispy clouds
        for (cx, cy, w_) in ((400, 160, 380), (1180, 110, 300), (1700, 300, 260)):
            for k in range(5): ellipse(ctx, cx + (k-2)*w_*0.18, cy + (k % 2)*10, w_*0.22, 22); ctx.set_source_rgba(0.6, 0.6, 0.85, 0.08); ctx.fill()
        # hills
        for (y0, col, amp) in ((560, '#1b1a44', 60), (610, '#14143a', 40)):
            ctx.move_to(0, H)
            for x in range(0, W+40, 40): ctx.line_to(x, y0 - amp*math.sin(x/260 + y0) - 20*math.sin(x/90))
            ctx.line_to(W, H); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
        for x in (80, 240, 1760, 1880, 1650): palm(ctx, x, 640, 0.55, '#11123a', 0.05)
        # palace
        bx0, bx1, by = 330, 1590, 820
        ctx.rectangle(bx0 - 30, by - 30, bx1 - bx0 + 60, 60); ctx.set_source(lin(ctx, 0, by-30, 0, by+30, [(0, '#8a4a30'), (1, '#4a2418')])); ctx.fill()
        ctx.rectangle(bx0, 480, bx1 - bx0, by - 480 - 30); ctx.set_source(lin(ctx, bx0, 0, bx1, 0, [(0, '#c9c4d8'), (0.5, '#e2dcea'), (1, '#a9a4c4')])); ctx.fill()
        for k in range(13):  # verandah pillars
            x = bx0 + 40 + k*((bx1 - bx0 - 80)/12)
            ctx.rectangle(x - 11, 600, 22, by - 630); ctx.set_source(lin(ctx, x-11, 0, x+11, 0, [(0, '#7a4a2e'), (1, '#3a2014')])); ctx.fill()
            ctx.rectangle(x - 18, 596, 36, 12); ctx.rectangle(x - 18, by - 44, 36, 14); ctx.set_source_rgba(*hexc('#5a3220')); ctx.fill()
        ctx.rectangle(bx0, 600, bx1 - bx0, by - 630); ctx.set_source_rgba(0.05, 0.03, 0.12, 0.35); ctx.fill()
        for k in range(12):
            x = bx0 + 62 + k*((bx1 - bx0 - 80)/12)
            if k in (5, 6): continue
            window_lit(ctx, x, 650, 54, 110, lit=(k % 3 != 1))
        # main door glow
        ctx.move_to(900, by - 30); ctx.line_to(900, 680); ctx.arc(960, 680, 60, math.pi, 0); ctx.line_to(1020, by - 30); ctx.close_path()
        ctx.set_source(lin(ctx, 0, 620, 0, by, [(0, '#ffcc78'), (1, '#d88a3a')])); ctx.fill(); glow(ctx, 960, 720, 220, a=0.3)
        # upper floor
        ctx.rectangle(520, 360, 880, 130); ctx.set_source(lin(ctx, 520, 0, 1400, 0, [(0, '#c4bfd6'), (1, '#9c98bc')])); ctx.fill()
        for k in range(8): window_lit(ctx, 560 + k*104, 385, 50, 80, lit=(k % 2 == 0))
        tiles_roof(ctx, [(bx0 - 90, 600), (bx0 + 60, 470), (bx1 - 60, 470), (bx1 + 90, 600)], '#5a2620')
        tiles_roof(ctx, [(470, 380), (600, 270), (1320, 270), (1450, 380)], '#5e2a22')
        gable(ctx, 960, 300, 300, 150); gable(ctx, bx0 + 120, 500, 150, 80); gable(ctx, bx1 - 120, 500, 150, 80)
        tiles_roof(ctx, [(820, 300), (960, 160), (1100, 300)], '#62302a', 10)
        for (x, y) in ((600, 270), (1320, 270), (bx0 + 60, 470), (bx1 - 60, 470)):
            ctx.move_to(x, y); ctx.line_to(x, y - 26); ctx.set_source_rgba(*hexc('#d8a83a')); ctx.set_line_width(5); ctx.stroke()
        # moonlight rim on roofs
        ctx.move_to(600, 270); ctx.line_to(1320, 270); ctx.set_source_rgba(0.75, 0.8, 1, 0.45); ctx.set_line_width(3); ctx.stroke()
        # lawn + path
        ctx.rectangle(0, by + 30, W, H); ctx.set_source(lin(ctx, 0, by, 0, H, [(0, '#16301e'), (1, '#0a1a10')])); ctx.fill()
        ctx.move_to(890, by + 30); ctx.line_to(1030, by + 30); ctx.line_to(1300, H); ctx.line_to(620, H); ctx.close_path()
        ctx.set_source(lin(ctx, 0, by, 0, H, [(0, '#5a5068'), (1, '#2a2434')])); ctx.fill()
        for k in range(7):
            y = by + 50 + k*k*6 + k*20
            ctx.move_to(900 - k*40, y); ctx.line_to(1020 + k*40, y); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(3); ctx.stroke()
        # gate pillars + board + lamps
        for x in (560, 1360):
            ctx.rectangle(x - 34, 760, 68, 230); ctx.set_source(lin(ctx, x-34, 0, x+34, 0, [(0, '#d8d0e0'), (1, '#8a86a8')])); ctx.fill()
            ctx.rectangle(x - 44, 750, 88, 20); ctx.set_source_rgba(*hexc('#6a3a28')); ctx.fill()
            ctx.move_to(x - 30, 750); ctx.line_to(x, 712); ctx.line_to(x + 30, 750); ctx.close_path(); ctx.fill()
            ctx.arc(x, 700, 18, 0, 2*math.pi); ctx.set_source_rgba(1, 0.86, 0.55, 1); ctx.fill(); glow(ctx, x, 700, 170, a=0.5)
        rrect(ctx, 1160, 870, 300, 92, 8); ctx.set_source(lin(ctx, 0, 870, 0, 962, [(0, '#2a1a10'), (1, '#160c06')])); ctx.fill()
        ctx.set_source_rgba(*hexc('#d8a83a')); ctx.set_line_width(3); rrect(ctx, 1166, 876, 288, 80, 6); ctx.stroke()
        for x in (1200, 1420): ctx.rectangle(x, 962, 8, 60); ctx.set_source_rgba(*hexc('#2a1a10')); ctx.fill()
        # foreground palms + bushes
        palm(ctx, -40, H + 30, 1.25, '#05060f', 0.08); palm(ctx, 1930, H + 40, 1.15, '#05060f', -0.1)
        for (x, y, r) in ((300, 1010, 90), (420, 1040, 70), (1580, 1020, 95), (1720, 1050, 80)):
            ellipse(ctx, x, y, r*1.4, r); ctx.set_source_rgba(*hexc('#0a1a12')); ctx.fill()
    return d


def gallery(lit):
    def d(ctx):
        # back wall
        top, bot = ('#3a2f5a', '#241c44') if not lit else ('#6a4a3e', '#4a3028')
        ctx.set_source(lin(ctx, 0, 0, 0, 760, [(0, top), (1, bot)])); ctx.paint()
        # ceiling with beams (perspective)
        ctx.move_to(0, 0); ctx.line_to(W, 0); ctx.line_to(W - 240, 150); ctx.line_to(240, 150); ctx.close_path()
        ctx.set_source(lin(ctx, 0, 0, 0, 150, [(0, '#1a100c' if not lit else '#2e1c14'), (1, '#2e1e16' if not lit else '#4a2e20')])); ctx.fill()
        for k in range(9):
            x0 = k*W/8; x1 = 240 + k*(W-480)/8
            ctx.move_to(x0, 0); ctx.line_to(x1, 150); ctx.set_source_rgba(*hexc('#120a06')); ctx.set_line_width(14); ctx.stroke()
        for y in (40, 95):
            ctx.move_to(y*1.6, y); ctx.line_to(W - y*1.6, y); ctx.set_source_rgba(*hexc('#140c08')); ctx.set_line_width(12); ctx.stroke()
        ctx.rectangle(240, 150, W - 480, 18); ctx.set_source_rgba(*hexc('#3a2418')); ctx.fill()
        # wainscot
        ctx.rectangle(0, 600, W, 160); ctx.set_source(lin(ctx, 0, 600, 0, 760, [(0, '#4a2c1e'), (1, '#2a180e')])); ctx.fill()
        for k in range(12):
            rrect(ctx, 30 + k*160, 625, 130, 110, 6); ctx.set_source_rgba(0, 0, 0, 0.22); ctx.set_line_width(3); ctx.stroke()
        ctx.rectangle(0, 596, W, 10); ctx.set_source_rgba(*hexc('#c99a4a')); ctx.fill()
        # lattice window with moonlight
        wx, wy = 250, 230
        ctx.rectangle(wx, wy, 220, 280); ctx.set_source(lin(ctx, 0, wy, 0, wy+280, [(0, '#3a4a8a'), (1, '#1a2450')])); ctx.fill()
        ctx.save(); ctx.rectangle(wx, wy, 220, 280); ctx.clip()
        for k in range(-10, 12):
            ctx.move_to(wx + k*28, wy); ctx.line_to(wx + k*28 + 280, wy + 280); ctx.move_to(wx + k*28, wy); ctx.line_to(wx + k*28 - 280, wy + 280)
        ctx.set_source_rgba(*hexc('#2a1810')); ctx.set_line_width(7); ctx.stroke(); ctx.restore()
        rrect(ctx, wx - 12, wy - 12, 244, 304, 6); ctx.set_source_rgba(*hexc('#4a2a18')); ctx.set_line_width(18); ctx.stroke()
        # portraits in gold frames
        for i, (px, py, pw, ph) in enumerate(((620, 230, 170, 220), (1130, 230, 170, 220), (1460, 250, 140, 180))):
            rrect(ctx, px - 14, py - 14, pw + 28, ph + 28, 6); ctx.set_source(lin(ctx, px, py, px + pw, py + ph, [(0, '#f0c860'), (0.5, '#a8782a'), (1, '#e8c058')])); ctx.fill()
            ctx.rectangle(px, py, pw, ph); ctx.set_source(lin(ctx, 0, py, 0, py + ph, [(0, '#3a2a20'), (1, '#1a120c')])); ctx.fill()
            ellipse(ctx, px + pw/2, py + ph*0.38, pw*0.17, ph*0.16); ctx.set_source_rgba(*hexc('#8a5a3a')); ctx.fill()
            ctx.move_to(px + pw*0.15, py + ph); ctx.curve_to(px + pw*0.2, py + ph*0.6, px + pw*0.8, py + ph*0.6, px + pw*0.85, py + ph)
            ctx.set_source_rgba(*hexc(('#7a1a22', '#1a3a6a', '#2a5a3a')[i])); ctx.fill()
            ctx.move_to(px + pw*0.32, py + ph*0.24); ctx.line_to(px + pw*0.5, py + ph*0.1); ctx.line_to(px + pw*0.68, py + ph*0.24); ctx.close_path(); ctx.set_source_rgba(*hexc('#e0b040')); ctx.fill()
            if lit: glow(ctx, px + pw/2, py - 30, 140, a=0.18)
        # floor (red oxide, polished, perspective)
        ctx.rectangle(0, 760, W, H - 760); ctx.set_source(lin(ctx, 0, 760, 0, H, [(0, '#5a2420' if lit else '#3a1a20'), (1, '#2a0e0c' if lit else '#180a12')])); ctx.fill()
        vx = W/2
        for k in range(-14, 15):
            ctx.move_to(vx + k*60, 760); ctx.line_to(vx + k*260, H); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.set_line_width(2); ctx.stroke()
        for k in range(8):
            y = 760 + (k**1.7)*9
            ctx.move_to(0, y); ctx.line_to(W, y); ctx.set_source_rgba(0, 0, 0, 0.15); ctx.set_line_width(2); ctx.stroke()
        ctx.rectangle(0, 760, W, 120); ctx.set_source(lin(ctx, 0, 760, 0, 880, [(0, (1, 0.85, 0.7, 0.10 if lit else 0.05)), (1, (1, 1, 1, 0))])); ctx.fill()
        # side display cases with artefacts
        for (cx, kind) in ((150, 'urn'), (1780, 'shield')):
            ctx.rectangle(cx - 80, 640, 160, 330); ctx.set_source(lin(ctx, cx-80, 0, cx+80, 0, [(0, '#5a3a2a'), (1, '#2a1810')])); ctx.fill()
            ctx.rectangle(cx - 90, 460, 180, 180); ctx.set_source_rgba(0.7, 0.85, 1, 0.12); ctx.fill()
            ctx.rectangle(cx - 90, 460, 180, 180); ctx.set_source_rgba(0.8, 0.9, 1, 0.4); ctx.set_line_width(3); ctx.stroke()
            if kind == 'urn':
                ctx.move_to(cx - 30, 630); ctx.curve_to(cx - 70, 580, cx - 50, 520, cx - 22, 500); ctx.line_to(cx + 22, 500); ctx.curve_to(cx + 50, 520, cx + 70, 580, cx + 30, 630); ctx.close_path()
                ctx.set_source(lin(ctx, cx-60, 0, cx+60, 0, [(0, '#f0c060'), (1, '#8a5a1a')])); ctx.fill()
            else:
                ctx.arc(cx, 550, 60, 0, 2*math.pi); ctx.set_source(rad(cx-15, 535, 5, 64, [(0, (0.95, 0.8, 0.45, 1)), (1, (0.5, 0.32, 0.1, 1))])); ctx.fill()
                ctx.arc(cx, 550, 18, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#6a4210')); ctx.fill()
            ctx.move_to(cx - 70, 470); ctx.line_to(cx - 40, 470); ctx.line_to(cx - 85, 620); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.12); ctx.fill()
        # carved wooden pillars (mid + foreground)
        for (x, w_, y0) in ((520, 46, 168), (1400, 46, 168)):
            ctx.rectangle(x - w_/2, y0, w_, 760 - y0 + 30); ctx.set_source(lin(ctx, x - w_/2, 0, x + w_/2, 0, [(0, '#8a5a36'), (0.4, '#6a3e22'), (1, '#2a160a')])); ctx.fill()
            for yy in (y0 + 10, 740): rrect(ctx, x - w_/2 - 10, yy, w_ + 20, 24, 6); ctx.set_source_rgba(*hexc('#4a2a16')); ctx.fill()
            for k in range(5): ctx.arc(x, y0 + 120 + k*120, 7, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#c99a4a')); ctx.fill()
        # hanging brass lamps
        for x in (760, 1160):
            ctx.move_to(x, 150); ctx.line_to(x, 250); ctx.set_source_rgba(*hexc('#6a4a2a')); ctx.set_line_width(3); ctx.stroke()
            ctx.move_to(x - 40, 250); ctx.curve_to(x - 30, 285, x + 30, 285, x + 40, 250); ctx.close_path(); ctx.set_source(lin(ctx, x-40, 0, x+40, 0, [(0, '#f0c060'), (1, '#8a5a1a')])); ctx.fill()
            if lit:
                for k in range(5): ctx.arc(x - 32 + k*16, 246, 5, 0, 2*math.pi); ctx.set_source_rgba(1, 0.85, 0.4, 1); ctx.fill()
                glow(ctx, x, 250, 260, a=0.45)
        # CCTV bracket (camera drawn live) at right wall
        ctx.rectangle(1660, 228, 60, 14); ctx.set_source_rgba(*hexc('#c8c8d0')); ctx.fill()
        if not lit:
            # moon shaft through the lattice window
            ctx.move_to(250, 230); ctx.line_to(470, 230); ctx.line_to(1120, 980); ctx.line_to(640, 1000); ctx.close_path()
            ctx.set_source(lin(ctx, 250, 230, 900, 980, [(0, (0.55, 0.65, 1, 0.20)), (1, (0.55, 0.65, 1, 0.0))])); ctx.fill()
            ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, 560, 200, 1200, [(0, (0, 0, 0, 0)), (1, (0.02, 0.0, 0.08, 0.55))])); ctx.fill()
        else:
            ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, 560, 300, 1200, [(0, (0, 0, 0, 0)), (1, (0.05, 0.02, 0.0, 0.45))])); ctx.fill()
    return d

def store():
    def d(ctx):
        ctx.set_source(lin(ctx, 0, 0, 0, 760, [(0, '#3a3440'), (1, '#24202a')])); ctx.paint()
        for k in range(14): ctx.rectangle(0, k*58, W, 3); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.fill()   # brick courses
        rnd = random.Random(3)
        for k in range(120):
            x, y = rnd.uniform(0, W), rnd.uniform(0, 740); ctx.rectangle(x, y, rnd.uniform(40, 90), 3); ctx.set_source_rgba(0, 0, 0, 0.1); ctx.fill()
        # shelves with boxes + paint cans
        for sy in (300, 480, 660):
            ctx.rectangle(1050, sy, 760, 18); ctx.set_source(lin(ctx, 0, sy, 0, sy+18, [(0, '#8a6a4a'), (1, '#4a3420')])); ctx.fill()
            x = 1070
            while x < 1780:
                w_ = rnd.uniform(70, 150); h_ = rnd.uniform(60, 140)
                kind = rnd.random()
                if kind < 0.6:
                    ctx.rectangle(x, sy - h_, w_, h_); ctx.set_source(lin(ctx, x, 0, x + w_, 0, [(0, '#b08a5a'), (1, '#7a5a34')])); ctx.fill()
                    ctx.rectangle(x, sy - h_ + h_*0.3, w_, 8); ctx.set_source_rgba(0.9, 0.85, 0.7, 0.6); ctx.fill()
                else:
                    ctx.rectangle(x, sy - 90, 70, 90); ctx.set_source(lin(ctx, x, 0, x+70, 0, [(0, '#c8ccd4'), (1, '#7a7e88')])); ctx.fill()
                    ctx.rectangle(x, sy - 70, 70, 30); ctx.set_source_rgba(*hexc(rnd.choice(['#d23a2a', '#2a6ad8', '#2a9a4a']))); ctx.fill(); w_ = 70
                x += w_ + 16
        ctx.rectangle(1050, 300, 14, 680); ctx.rectangle(1796, 300, 14, 680); ctx.set_source_rgba(*hexc('#4a3420')); ctx.fill()
        # brooms + bucket
        for k in range(3):
            ctx.move_to(880 + k*40, 980); ctx.line_to(860 + k*50, 560); ctx.set_source_rgba(*hexc('#b08a5a')); ctx.set_line_width(10); ctx.stroke()
            ctx.move_to(880 + k*40, 980); ctx.line_to(860 + k*40 - 30, 920 - 0); ctx.line_to(860 + k*40 + 40, 920); ctx.close_path(); ctx.set_source_rgba(*hexc('#c8a050')); ctx.fill()
        # door at left (open) with padlock hanging
        ctx.rectangle(60, 230, 300, 750); ctx.set_source_rgba(*hexc('#0e0c14')); ctx.fill()
        ctx.move_to(60, 230); ctx.line_to(-40, 200); ctx.line_to(-40, 1010); ctx.line_to(60, 980); ctx.close_path(); ctx.set_source(lin(ctx, -40, 0, 60, 0, [(0, '#5a3a24'), (1, '#3a2414')])); ctx.fill()
        ctx.rectangle(60, 230, 300, 750); ctx.set_source_rgba(*hexc('#2a1a10')); ctx.set_line_width(14); ctx.stroke()
        # floor
        ctx.rectangle(0, 760, W, H - 760); ctx.set_source(lin(ctx, 0, 760, 0, H, [(0, '#4a4650'), (1, '#24222a')])); ctx.fill()
        for k in range(-12, 13): ctx.move_to(W/2 + k*70, 760); ctx.line_to(W/2 + k*240, H); ctx.set_source_rgba(0, 0, 0, 0.15); ctx.set_line_width(2); ctx.stroke()
        # hanging bulb + light cone
        ctx.move_to(700, 0); ctx.line_to(700, 120); ctx.set_source_rgba(0.1, 0.1, 0.1, 1); ctx.set_line_width(3); ctx.stroke()
        ctx.arc(700, 140, 22, 0, 2*math.pi); ctx.set_source_rgba(1, 0.9, 0.6, 1); ctx.fill(); glow(ctx, 700, 140, 380, a=0.5)
        ctx.move_to(670, 150); ctx.line_to(730, 150); ctx.line_to(1150, 1000); ctx.line_to(250, 1000); ctx.close_path()
        ctx.set_source(lin(ctx, 0, 150, 0, 1000, [(0, (1, 0.9, 0.6, 0.20)), (1, (1, 0.9, 0.6, 0.02))])); ctx.fill()
        ctx.rectangle(0, 0, W, H); ctx.set_source(rad(700, 520, 250, 1250, [(0, (0, 0, 0, 0)), (1, (0, 0, 0.03, 0.6))])); ctx.fill()
    return d

LINE_FLOOR = 1000; LINE_S = 0.75
def lineup():
    def d(ctx):
        ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, '#1a2244'), (1, '#0c1024')])); ctx.paint()
        ft = 900*LINE_S/6.0
        for k in range(3, 8):
            y = LINE_FLOOR - k*ft
            ctx.rectangle(0, y - 2, W, 4); ctx.set_source_rgba(1, 1, 1, 0.35 if k != 6 else 0.6); ctx.fill()
            for j in range(4):
                yy = y + j*ft/4
                if j: ctx.rectangle(0, yy - 1, 60, 2); ctx.rectangle(W - 60, yy - 1, 60, 2); ctx.set_source_rgba(1, 1, 1, 0.25); ctx.fill()
        ctx.rectangle(0, LINE_FLOOR, W, H - LINE_FLOOR); ctx.set_source(lin(ctx, 0, LINE_FLOOR, 0, H, [(0, '#2a2a38'), (1, '#121218')])); ctx.fill()
        for x in (330, 750, 1170, 1590):
            ctx.move_to(x - 60, 0); ctx.line_to(x + 60, 0); ctx.line_to(x + 230, LINE_FLOOR + 30); ctx.line_to(x - 230, LINE_FLOOR + 30); ctx.close_path()
            ctx.set_source(lin(ctx, 0, 0, 0, LINE_FLOOR, [(0, (1, 0.95, 0.8, 0.16)), (1, (1, 0.95, 0.8, 0.04))])); ctx.fill()
            ellipse(ctx, x, LINE_FLOOR + 14, 230, 34); ctx.set_source_rgba(1, 0.95, 0.8, 0.10); ctx.fill()
        ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, 540, 400, 1200, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.5))])); ctx.fill()
    return d

def parking():
    def d(ctx):
        ctx.set_source(lin(ctx, 0, 0, 0, 700, [(0, '#080a22'), (1, '#2a2050')])); ctx.paint()
        rnd = random.Random(11)
        for k in range(90): ctx.arc(rnd.uniform(0, W), rnd.uniform(0, 400), rnd.uniform(0.6, 1.8), 0, 2*math.pi); ctx.set_source_rgba(1, 1, 1, rnd.uniform(0.3, 0.8)); ctx.fill()
        # museum compound wall + roof silhouette behind
        tiles_roof(ctx, [(-50, 420), (200, 300), (1500, 300), (1800, 420)], '#3a1a1a', 8)
        ctx.rectangle(0, 420, W, 280); ctx.set_source(lin(ctx, 0, 0, W, 0, [(0, '#8a86a8'), (1, '#5a5678')])); ctx.fill()
        for k in range(9): window_lit(ctx, 120 + k*200, 470, 60, 100, lit=(k % 3 == 0))
        ctx.rectangle(0, 640, W, 60); ctx.set_source_rgba(*hexc('#3a2a30')); ctx.fill()
        # ground
        ctx.rectangle(0, 700, W, H); ctx.set_source(lin(ctx, 0, 700, 0, H, [(0, '#3a3644'), (1, '#16141c')])); ctx.fill()
        for k in range(5): ctx.move_to(200 + k*380, 1080); ctx.line_to(300 + k*330, 720); ctx.set_source_rgba(1, 1, 1, 0.25); ctx.set_line_width(6); ctx.stroke()
        # street lamp (sodium)
        ctx.rectangle(1700, 260, 16, 720); ctx.set_source_rgba(*hexc('#2a2a30')); ctx.fill()
        ctx.move_to(1708, 270); ctx.curve_to(1700, 220, 1640, 220, 1600, 250); ctx.set_source_rgba(*hexc('#2a2a30')); ctx.set_line_width(10); ctx.stroke()
        ctx.arc(1600, 262, 20, 0, 2*math.pi); ctx.set_source_rgba(1, 0.75, 0.35, 1); ctx.fill(); glow(ctx, 1600, 262, 420, (1, 0.7, 0.3), 0.45)
        ctx.move_to(1580, 270); ctx.line_to(1620, 270); ctx.line_to(1900, 1000); ctx.line_to(1250, 1000); ctx.close_path()
        ctx.set_source(lin(ctx, 0, 270, 0, 1000, [(0, (1, 0.7, 0.3, 0.16)), (1, (1, 0.7, 0.3, 0.03))])); ctx.fill()
        palm(ctx, 60, 720, 0.8, '#0a0c1a', 0.05)
    return d

def card_bg(top='#1a1638', bot='#07061a'):
    def d(ctx):
        ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, top), (1, bot)])); ctx.paint()
        rnd = random.Random(5)
        for k in range(40):
            ctx.arc(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(20, 70), 0, 2*math.pi); ctx.set_source_rgba(0.6, 0.6, 1, rnd.uniform(0.02, 0.06)); ctx.fill()
        ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 300, 1100, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.55))])); ctx.fill()
    return d

BUILDERS = {'ext': ext_night, 'gal_dark': lambda: gallery(False), 'gal_lit': lambda: gallery(True), 'store': store,
            'lineup': lineup, 'parking': parking, 'card': card_bg, 'card_red': lambda: card_bg('#3a0e18', '#10040a'),
            'card_blue': lambda: card_bg('#0e2a4a', '#040c1a')}
_cache = {}
def get(name):
    if name not in _cache:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W*SC, H*SC); ctx = cairo.Context(surf); ctx.scale(SC, SC)
        BUILDERS[name]()(ctx); surf.flush(); _cache[name] = surf
    return _cache[name]

def paint(ctx, name):
    ctx.save(); ctx.scale(1/SC, 1/SC); ctx.set_source_surface(get(name), 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BILINEAR); ctx.paint(); ctx.restore()

if __name__ == '__main__':
    import sys
    for n in BUILDERS:
        s = get(n); small = cairo.ImageSurface(cairo.FORMAT_ARGB32, 960, 540); c = cairo.Context(small); c.scale(0.25, 0.25); c.set_source_surface(s); c.paint()
        small.write_to_png(f'/home/claude/det/bg_{n}.png')
