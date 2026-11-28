"""Hard Malayalam Riddles backgrounds (pycairo, 1920x1080 world, cached at 2x for camera zooms).
studio (Arjun's office), market (Palakkad coconut market), church (Kottayam clock tower, evening), river (Alappuzha backwater),
bakery (Kozhikode), rail (paddy fields + parallel tracks), jewel (Thrissur jewellery shop). Dynamic props are drawn in rv.py."""
import math, random, cairo, sys
sys.path.append('/home/claude/detective')
from chars import hexc, mix, lt, dk, shade, vshade, ellipse, rrect, outline
from bgs import lin, rad, glow, palm, tiles_roof, card_bg
W, H = 1920, 1080
SC = 2

def hills(ctx, base, amp, col, seed, step=160):
    rnd = random.Random(seed); ctx.move_to(0, H); ctx.line_to(0, base)
    x = 0
    while x < W + step:
        x += step; ctx.curve_to(x - step*0.6, base - rnd.uniform(0.3, 1)*amp, x - step*0.3, base - rnd.uniform(0.3, 1)*amp, x, base - rnd.uniform(0, 0.6)*amp)
    ctx.line_to(W, H); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()

def cloud(ctx, x, y, s, a=0.9, col=(1, 1, 1)):
    for dx, dy, r in ((0, 0, 60), (60, -20, 70), (130, 0, 55), (60, 20, 60), (-50, 10, 45)):
        ctx.new_sub_path(); ctx.arc(x + dx*s, y + dy*s, r*s, 0, 2*math.pi)
    ctx.set_source_rgba(*col, a); ctx.fill()

def green_palm(ctx, x, y, s, sway=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-12, 0); ctx.curve_to(5, -160, 30, -320, 62, -470); ctx.line_to(78, -470); ctx.curve_to(50, -320, 25, -160, 14, 0); ctx.close_path()
    shade(ctx, '#7a5a3a', -12, 20); ctx.fill()
    for k in range(10): ctx.move_to(-10 + k*4.5, -k*47); ctx.line_to(14 + k*4.5, -k*47 - 4); ctx.set_source_rgba(0, 0, 0, 0.15); ctx.set_line_width(3); ctx.stroke()
    ctx.translate(70, -470)
    for k in range(10):
        a = -math.pi/2 + (k - 4.5)*0.38 + sway
        col = '#2f7a3a' if k % 2 else '#3f9a48'
        ctx.move_to(0, 0); ctx.curve_to(math.cos(a)*100, math.sin(a)*80 - 25, math.cos(a)*190, math.sin(a)*100 + 20, math.cos(a)*240, math.sin(a)*90 + 120)
        ctx.curve_to(math.cos(a)*170, math.sin(a)*90 + 28, math.cos(a)*90, math.sin(a)*55, 0, 12); ctx.close_path()
        ctx.set_source_rgba(*hexc(col)); ctx.fill()
    for k in range(3): ctx.arc(-14 + k*14, 14, 13, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#6a4a1a')); ctx.fill()
    ctx.restore()

def floor_planks(ctx, y0, col, n=14):
    ctx.rectangle(0, y0, W, H - y0); ctx.set_source(lin(ctx, 0, y0, 0, H, [(0, col), (1, dk(col, 0.35))])); ctx.fill()
    for k in range(n):
        x = k*W/n; ctx.move_to(W/2 + (x - W/2)*0.55, y0); ctx.line_to(W/2 + (x - W/2)*1.6, H)
        ctx.set_source_rgba(0, 0, 0, 0.18); ctx.set_line_width(3); ctx.stroke()

# ------------------------------------------------------------------ studio
def studio(ctx):
    ctx.set_source(lin(ctx, 0, 0, 0, 1000, [(0, '#5a3a2a'), (1, '#3a2418')])); ctx.paint()
    for k in range(13):  # wood panels
        x = k*160; ctx.rectangle(x, 520, 150, 480); ctx.set_source_rgba(0.25, 0.14, 0.08, 0.5); ctx.fill()
        ctx.rectangle(x + 10, 535, 130, 450); ctx.set_source(lin(ctx, x, 0, x + 130, 0, [(0, '#6a422a'), (1, '#4a2c1a')])); ctx.fill()
    ctx.rectangle(0, 505, W, 22); ctx.set_source_rgba(*hexc('#2a160c')); ctx.fill()
    # window with evening backwater view (right)
    wx, wy, ww, wh = 1380, 120, 420, 340
    ctx.rectangle(wx - 18, wy - 18, ww + 36, wh + 36); ctx.set_source_rgba(*hexc('#2a160c')); ctx.fill()
    ctx.rectangle(wx, wy, ww, wh); ctx.set_source(lin(ctx, 0, wy, 0, wy + wh, [(0, '#2a2a6a'), (0.6, '#c86a5a'), (1, '#f0a060')])); ctx.fill()
    ctx.save(); ctx.rectangle(wx, wy, ww, wh); ctx.clip()
    hills(ctx, wy + 260, 50, '#2a2040', 3, 90); palm(ctx, wx + 80, wy + wh, 0.5, '#1a1428'); palm(ctx, wx + 330, wy + wh + 10, 0.6, '#1a1428', 0.1)
    ctx.restore()
    ctx.rectangle(wx + ww/2 - 6, wy, 12, wh); ctx.rectangle(wx, wy + wh/2 - 6, ww, 12); ctx.set_source_rgba(*hexc('#2a160c')); ctx.fill()
    # bookshelf (left)
    bx = 90; ctx.rectangle(bx, 110, 430, 820); shade(ctx, '#4a2a18', bx, bx + 430); ctx.fill()
    rnd = random.Random(7)
    for r in range(5):
        y = 150 + r*160; ctx.rectangle(bx + 20, y + 120, 390, 18); ctx.set_source_rgba(*hexc('#2a160c')); ctx.fill()
        x = bx + 30
        while x < bx + 390:
            w = rnd.uniform(18, 34); h = rnd.uniform(80, 115); col = rnd.choice(['#a8322a', '#2a5a8a', '#d8a83a', '#3a7a4a', '#7a3a7a', '#c86a2a'])
            rrect(ctx, x, y + 120 - h, w, h, 3); shade(ctx, col, x, x + w); ctx.fill()
            ctx.rectangle(x + 3, y + 120 - h + 12, w - 6, 4); ctx.set_source_rgba(1, 0.9, 0.6, 0.6); ctx.fill()
            x += w + 3
    # chalkboard
    cx_, cy_ = 680, 140
    rrect(ctx, cx_ - 14, cy_ - 14, 628, 348, 10); ctx.set_source_rgba(*hexc('#6a4220')); ctx.fill()
    ctx.rectangle(cx_, cy_, 600, 320); ctx.set_source(lin(ctx, 0, cy_, 0, cy_ + 320, [(0, '#24403a'), (1, '#18302a')])); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.08)
    for k in range(6): ctx.arc(cx_ + 80 + k*90, cy_ + 60 + (k % 3)*80, 50, 0, 2*math.pi); ctx.fill()
    # desk
    ctx.rectangle(0, 1000, W, 80); ctx.set_source_rgba(*hexc('#24140a')); ctx.fill()
    floor_planks(ctx, 1000, '#7a4a2a')
    ctx.rectangle(560, 760, 800, 40); shade(ctx, '#6a3a1c', 560, 1360); ctx.fill()
    ctx.rectangle(580, 800, 760, 210); ctx.set_source(lin(ctx, 0, 800, 0, 1010, [(0, '#5a3018'), (1, '#3a1e0e')])); ctx.fill()
    for k in range(2): rrect(ctx, 640 + k*500, 840, 140, 60, 6); ctx.set_source_rgba(0.2, 0.1, 0.05, 0.5); ctx.fill()
    # desk lamp + magnifier + papers
    ctx.move_to(1250, 760); ctx.line_to(1230, 640); ctx.line_to(1300, 590); ctx.set_source_rgba(*hexc('#2a3a2a')); ctx.set_line_width(10); ctx.stroke()
    ctx.move_to(1260, 560); ctx.line_to(1350, 600); ctx.line_to(1320, 640); ctx.line_to(1240, 600); ctx.close_path(); ctx.set_source_rgba(*hexc('#2a5a3a')); ctx.fill()
    glow(ctx, 1290, 650, 380, (1, 0.85, 0.5), 0.35)
    ctx.save(); ctx.translate(700, 745); ctx.rotate(-0.08); ctx.rectangle(0, 0, 170, 20); ctx.set_source_rgba(0.95, 0.92, 0.82, 1); ctx.fill(); ctx.restore()
    ctx.arc(960, 748, 26, 0, 2*math.pi); ctx.set_source_rgba(0.75, 0.85, 1, 0.5); ctx.fill(); ctx.arc(960, 748, 26, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#b8862a')); ctx.set_line_width(6); ctx.stroke()
    # plant
    rrect(ctx, 1640, 880, 120, 120, 14); shade(ctx, '#a8582a', 1640, 1760); ctx.fill()
    for k in range(8):
        a = -math.pi/2 + (k - 3.5)*0.32
        ctx.move_to(1700, 890); ctx.curve_to(1700 + math.cos(a)*90, 890 + math.sin(a)*120, 1700 + math.cos(a)*150, 890 + math.sin(a)*180, 1700 + math.cos(a)*190, 890 + math.sin(a)*230)
        ctx.set_source_rgba(*hexc('#3a8a4a' if k % 2 else '#2a6a3a')); ctx.set_line_width(26); ctx.stroke()
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(1200, 500, 200, 1300, [(0, (1, 0.8, 0.5, 0.12)), (1, (0, 0, 0, 0.45))])); ctx.fill()

# ------------------------------------------------------------------ market
def coconut(ctx, x, y, r, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(1, 0.86)
    g = cairo.RadialGradient(-r*0.35, -r*0.4, r*0.1, 0, 0, r); g.add_color_stop_rgba(0, *hexc('#a87a4a')); g.add_color_stop_rgba(0.6, *hexc('#6a4424')); g.add_color_stop_rgba(1, *hexc('#3a220e'))
    ctx.set_source(g); ctx.arc(0, 0, r, 0, 2*math.pi); ctx.fill()
    for k in range(5):
        a = k*1.3; ctx.move_to(math.cos(a)*r*0.2, math.sin(a)*r*0.2); ctx.line_to(math.cos(a)*r*0.9, math.sin(a)*r*0.9)
        ctx.set_source_rgba(0.2, 0.1, 0.03, 0.35); ctx.set_line_width(max(1, r*0.05)); ctx.stroke()
    ctx.restore()

def heap(ctx, cx, base, rows, r, seed):
    rnd = random.Random(seed)
    for row in range(rows):
        n = rows - row + 2
        for k in range(n):
            x = cx + (k - (n - 1)/2)*r*1.7 + rnd.uniform(-4, 4); y = base - row*r*1.25
            coconut(ctx, x, y, r, rnd.uniform(-0.5, 0.5))

def market(ctx):
    ctx.set_source(lin(ctx, 0, 0, 0, 600, [(0, '#5aa8e8'), (1, '#f4e0b0')])); ctx.paint()
    cloud(ctx, 300, 120, 1.0, 0.85); cloud(ctx, 1300, 90, 1.2, 0.8); cloud(ctx, 1700, 200, 0.7, 0.7)
    hills(ctx, 520, 160, '#7a9ab8', 11, 220); hills(ctx, 590, 110, '#5a8a6a', 12, 180)
    for x, s in ((120, 0.9), (430, 0.75), (1500, 0.85), (1800, 1.0)): green_palm(ctx, x, 690, s, 0.05*(x % 3))
    # back row of stalls with striped tarps
    for k, (x, c1, c2) in enumerate(((60, '#d8382a', '#f4f1e8'), (520, '#2a6ab8', '#f4f1e8'), (1080, '#e8a82a', '#f4f1e8'), (1520, '#3a9a5a', '#f4f1e8'))):
        ctx.rectangle(x, 600, 380, 220); ctx.set_source(lin(ctx, 0, 600, 0, 820, [(0, '#8a6a4a'), (1, '#5a3a22')])); ctx.fill()
        for j in range(8):
            ctx.move_to(x - 20 + j*52, 560); ctx.line_to(x + 32 + j*52, 560); ctx.line_to(x + 36 + j*52, 620); ctx.line_to(x - 16 + j*52, 620); ctx.close_path()
            ctx.set_source_rgba(*hexc(c1 if j % 2 else c2)); ctx.fill()
        for j in range(6):  # goods
            ctx.arc(x + 40 + j*60, 760, 26, 0, 2*math.pi); ctx.set_source_rgba(*hexc(['#e84a2a', '#f0c02a', '#5aa83a', '#c86a2a', '#8a3a8a', '#e8e0c0'][j])); ctx.fill()
    ctx.rectangle(0, 815, W, 265); ctx.set_source(lin(ctx, 0, 815, 0, H, [(0, '#c8a878'), (1, '#8a6a48')])); ctx.fill()
    rnd = random.Random(4)
    for k in range(70):
        ctx.arc(rnd.uniform(0, W), rnd.uniform(830, H), rnd.uniform(2, 6), 0, 2*math.pi); ctx.set_source_rgba(0.3, 0.2, 0.1, 0.25); ctx.fill()
    # Raju's stall (front, left-centre): poles, tarp, table, heaps, board
    for x in (230, 1010): ctx.rectangle(x, 470, 18, 560); shade(ctx, '#6a4424', x, x + 18); ctx.fill()
    for j in range(16):
        ctx.move_to(200 + j*52, 440); ctx.line_to(252 + j*52, 440); ctx.line_to(256 + j*52, 520); ctx.line_to(196 + j*52, 520); ctx.close_path()
        ctx.set_source_rgba(*hexc('#c8302a' if j % 2 else '#f6f2e6')); ctx.fill()
    ctx.rectangle(195, 518, 870, 10); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.fill()
    rrect(ctx, 430, 390, 420, 80, 10); shade(ctx, '#1a5a3a', 430, 850); ctx.fill()
    ctx.set_source_rgba(*hexc('#f0d070')); ctx.set_line_width(4); rrect(ctx, 438, 398, 404, 64, 8); ctx.stroke()
    ctx.select_font_face('Poppins ExtraBold'); ctx.set_font_size(40); ctx.move_to(468, 445); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text('RAJU COCONUTS')
    ctx.rectangle(250, 880, 760, 30); shade(ctx, '#8a5a2a', 250, 1010); ctx.fill()
    ctx.rectangle(270, 910, 720, 140); ctx.set_source(lin(ctx, 0, 910, 0, 1050, [(0, '#6a4020'), (1, '#3a220e')])); ctx.fill()
    heap(ctx, 470, 860, 4, 34, 1); heap(ctx, 820, 860, 3, 34, 2)
    heap(ctx, 1500, 1040, 3, 40, 3)
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 500, 1200, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.28))])); ctx.fill()

# ------------------------------------------------------------------ church
CLOCK = (960, 330, 92)
def church(ctx):
    ctx.set_source(lin(ctx, 0, 0, 0, 800, [(0, '#3a2a6a'), (0.55, '#d8705a'), (1, '#f8c070')])); ctx.paint()
    glow(ctx, 1500, 640, 400, (1, 0.8, 0.5), 0.5)
    cloud(ctx, 250, 160, 1.0, 0.25, (1, 0.8, 0.8)); cloud(ctx, 1450, 120, 1.1, 0.25, (1, 0.8, 0.8))
    hills(ctx, 760, 90, '#5a3a5a', 21, 200)
    for x, s in ((80, 0.9), (330, 0.7), (1640, 0.8), (1860, 1.0)): palm(ctx, x, 880, s, '#2a1a30', 0.05)
    # church: nave + tower
    ctx.rectangle(560, 520, 800, 380); shade(ctx, '#f2ecdc', 560, 1360, 0.05, 0.2); ctx.fill()
    tiles_roof(ctx, [(520, 530), (960, 380), (1400, 530)], '#8a3a2a')
    ctx.rectangle(840, 120, 240, 780); shade(ctx, '#faf4e6', 840, 1080, 0.05, 0.18); ctx.fill()
    ctx.move_to(820, 130); ctx.line_to(960, 20); ctx.line_to(1100, 130); ctx.close_path(); shade(ctx, '#8a3a2a', 820, 1100); ctx.fill()
    ctx.rectangle(955, -40, 10, 70); ctx.rectangle(938, -20, 44, 10); ctx.set_source_rgba(*hexc('#e8c050')); ctx.fill()
    cx, cy, r = CLOCK
    ctx.arc(cx, cy, r + 20, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#c8a040')); ctx.fill()
    for (x0, x1) in ((600, 820), (1100, 1320)):
        for k in range(3):
            wx = x0 + k*75; rrect(ctx, wx, 640, 44, 120, 22); ctx.set_source(lin(ctx, 0, 640, 0, 760, [(0, '#f0c060'), (1, '#a85a2a')])); ctx.fill()
    ctx.move_to(890, 900); ctx.line_to(890, 700); ctx.arc(960, 700, 70, math.pi, 2*math.pi); ctx.line_to(1030, 900); ctx.close_path(); ctx.set_source(lin(ctx, 0, 640, 0, 900, [(0, '#6a3a1a'), (1, '#3a1e0a')])); ctx.fill()
    ctx.arc(960, 520, 34, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#f0c060')); ctx.fill()
    for k in range(4): ctx.rectangle(820 - k*30, 900 + k*20, 280 + k*60, 20); ctx.set_source_rgba(*hexc(mix('#d8d0c0', '#8a8070', k*0.2))); ctx.fill()
    ctx.rectangle(0, 980, W, 100); ctx.set_source(lin(ctx, 0, 980, 0, H, [(0, '#a89070'), (1, '#6a5a48')])); ctx.fill()
    for x in (420, 1500):
        ctx.rectangle(x, 720, 12, 270); ctx.set_source_rgba(*hexc('#2a2a30')); ctx.fill(); glow(ctx, x + 6, 715, 90, (1, 0.85, 0.5), 0.7)
        ctx.arc(x + 6, 715, 16, 0, 2*math.pi); ctx.set_source_rgba(1, 0.95, 0.75, 1); ctx.fill()
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 500, 1200, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.35))])); ctx.fill()

# ------------------------------------------------------------------ river
WATER = 640
def river(ctx):
    ctx.set_source(lin(ctx, 0, 0, 0, WATER, [(0, '#78b8e8'), (1, '#f6e6c0')])); ctx.paint()
    cloud(ctx, 400, 140, 1.1, 0.85); cloud(ctx, 1400, 110, 0.9, 0.8)
    # far bank (right) with palms and a house
    ctx.move_to(900, WATER); ctx.curve_to(1200, 560, 1500, 570, W, 545); ctx.line_to(W, WATER); ctx.close_path(); ctx.set_source_rgba(*hexc('#4a8a3a')); ctx.fill()
    for x, s in ((1100, 0.55), (1250, 0.7), (1420, 0.6), (1600, 0.75), (1780, 0.62)): green_palm(ctx, x, 600, s, 0.04)
    ctx.rectangle(1480, 500, 140, 90); ctx.set_source_rgba(*hexc('#f2e6c8')); ctx.fill(); tiles_roof(ctx, [(1460, 505), (1550, 445), (1640, 505)], '#a84a2a', 8)
    ctx.rectangle(1530, 540, 30, 50); ctx.set_source_rgba(*hexc('#5a3a1a')); ctx.fill()
    for x, s in ((60, 0.5), (300, 0.42), (520, 0.5)): green_palm(ctx, x, 625, s)
    # water
    ctx.rectangle(0, WATER - 10, W, H - WATER + 10); ctx.set_source(lin(ctx, 0, WATER, 0, H, [(0, '#5aa0b8'), (1, '#1f5a70')])); ctx.fill()
    rnd = random.Random(9)
    for k in range(120):
        y = rnd.uniform(WATER + 10, H); w = rnd.uniform(30, 140)*(0.4 + (y - WATER)/400); x = rnd.uniform(0, W)
        ctx.move_to(x, y); ctx.line_to(x + w, y); ctx.set_source_rgba(1, 1, 1, rnd.uniform(0.08, 0.25)); ctx.set_line_width(2 + (y - WATER)/200); ctx.stroke()
    # near bank (left) with jetty steps
    ctx.move_to(0, 760); ctx.curve_to(200, 760, 380, 800, 520, H); ctx.line_to(0, H); ctx.close_path(); ctx.set_source(lin(ctx, 0, 760, 0, H, [(0, '#5a9a3a'), (1, '#2a5a1a')])); ctx.fill()
    ctx.move_to(0, 800); ctx.curve_to(180, 800, 330, 840, 450, H); ctx.line_to(0, H); ctx.close_path(); ctx.set_source(lin(ctx, 0, 800, 0, H, [(0, '#b89a6a'), (1, '#7a6040')])); ctx.fill()
    ctx.rectangle(300, 880, 260, 22); shade(ctx, '#7a5a3a', 300, 560); ctx.fill()
    for x in (310, 540): ctx.rectangle(x, 880, 14, 160); ctx.set_source_rgba(*hexc('#4a3420')); ctx.fill()
    green_palm(ctx, 120, 860, 1.1, -0.05)
    # far-side landing (right) small jetty
    ctx.rectangle(1560, 640, 200, 16); shade(ctx, '#7a5a3a', 1560, 1760); ctx.fill()
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 500, 1200, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.25))])); ctx.fill()

# ------------------------------------------------------------------ bakery
SHELF_Y = 470
def bakery(ctx):
    ctx.set_source(lin(ctx, 0, 0, 0, 800, [(0, '#f4e2c4'), (1, '#e0c49a')])); ctx.paint()
    for y in range(0, 800, 60):
        for x in range(0 if (y//60) % 2 else -30, W, 60):
            ctx.rectangle(x + 2, y + 2, 56, 56); ctx.set_source_rgba(1, 1, 1, 0.12); ctx.fill()
    # name board
    rrect(ctx, 610, 40, 700, 110, 16); shade(ctx, '#a83a2a', 610, 1310); ctx.fill()
    ctx.set_source_rgba(*hexc('#f8d870')); ctx.set_line_width(5); rrect(ctx, 620, 50, 680, 90, 12); ctx.stroke()
    ctx.select_font_face('Poppins ExtraBold'); ctx.set_font_size(56); ext = ctx.text_extents('AMMINI BAKERY')
    ctx.move_to(960 - ext[2]/2 - ext[0], 118); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text('AMMINI BAKERY')
    # shelves
    for y in (SHELF_Y, 300):
        ctx.rectangle(180, y, 1560, 26); shade(ctx, '#8a5a2a', 180, 1740); ctx.fill()
        ctx.rectangle(180, y + 26, 1560, 10); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.fill()
    rnd = random.Random(2)
    for k in range(14):  # biscuit tins top shelf
        x = 210 + k*108; h = rnd.uniform(90, 120)
        rrect(ctx, x, 300 - h, 80, h, 8); shade(ctx, rnd.choice(['#d84a3a', '#3a7ab8', '#e8b83a', '#4a9a5a', '#c86aa8']), x, x + 80); ctx.fill()
        ctx.rectangle(x + 10, 300 - h + 25, 60, 22); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
    # counter
    ctx.rectangle(0, 800, W, 280); ctx.set_source(lin(ctx, 0, 800, 0, H, [(0, '#8a5a3a'), (1, '#4a2a18')])); ctx.fill()
    ctx.rectangle(0, 770, W, 40); shade(ctx, '#c8a070', 0, W, 0.2, 0.2); ctx.fill()
    ctx.rectangle(120, 840, 1680, 200); ctx.set_source_rgba(0.75, 0.9, 1, 0.25); ctx.fill()
    for k in range(10):  # sweets in display
        x = 180 + k*165
        for j in range(4):
            ctx.arc(x + j*32, 990 - (j % 2)*20, 22, 0, 2*math.pi); ctx.set_source_rgba(*hexc(['#f0a030', '#e8d0a0', '#c86a3a', '#f4e8d0'][k % 4])); ctx.fill()
    ctx.rectangle(120, 840, 1680, 200); ctx.set_source_rgba(1, 1, 1, 0.08); ctx.fill()
    ctx.move_to(160, 850); ctx.line_to(260, 1030); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(10); ctx.stroke()
    glow(ctx, 960, 200, 700, (1, 0.9, 0.7), 0.25)
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 500, 1200, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.3))])); ctx.fill()

# ------------------------------------------------------------------ rail
TRACK_Y = (760, 840)
def rail(ctx):
    ctx.set_source(lin(ctx, 0, 0, 0, 600, [(0, '#58a8f0'), (1, '#e8f0e0')])); ctx.paint()
    cloud(ctx, 260, 130, 1.2, 0.9); cloud(ctx, 980, 90, 1.0, 0.85); cloud(ctx, 1600, 160, 1.3, 0.9)
    hills(ctx, 520, 170, '#6a90b0', 31, 240); hills(ctx, 600, 120, '#4a8a5a', 32, 200)
    ctx.rectangle(0, 600, W, H - 600); ctx.set_source(lin(ctx, 0, 600, 0, H, [(0, '#7ac84a'), (1, '#3a8a2a')])); ctx.fill()
    for k in range(40):  # paddy rows
        y = 610 + k*12 + (k*k)*0.15
        ctx.move_to(0, y); ctx.line_to(W, y); ctx.set_source_rgba(0.2, 0.45, 0.1, 0.25); ctx.set_line_width(2 + k*0.08); ctx.stroke()
    for x, s in ((300, 0.45), (520, 0.38), (760, 0.5), (1180, 0.42), (1420, 0.48), (1650, 0.4)): green_palm(ctx, x, 640, s, 0.03)
    # embankment + 2 tracks
    ctx.rectangle(0, TRACK_Y[0] - 40, W, TRACK_Y[1] - TRACK_Y[0] + 90); ctx.set_source(lin(ctx, 0, TRACK_Y[0] - 40, 0, TRACK_Y[1] + 50, [(0, '#8a7a6a'), (1, '#5a4a3a')])); ctx.fill()
    for ty in TRACK_Y:
        for x in range(0, W, 34): ctx.rectangle(x, ty - 4, 18, 22); ctx.set_source_rgba(*hexc('#4a3424')); ctx.fill()
        for dy in (0, 12): ctx.rectangle(0, ty + dy, W, 5); ctx.set_source_rgba(*hexc('#c8c8d0')); ctx.fill()
    # stations at both ends
    for x0, lab in ((0, 'STATION A'), (1640, 'STATION B')):
        ctx.rectangle(x0 + 30, 560, 250, 150); ctx.set_source_rgba(*hexc('#f0d8a8')); ctx.fill()
        tiles_roof(ctx, [(x0 + 10, 565), (x0 + 155, 500), (x0 + 300, 565)], '#a84a2a', 8)
        rrect(ctx, x0 + 50, 590, 210, 50, 6); ctx.set_source_rgba(*hexc('#f2d230')); ctx.fill()
        ctx.select_font_face('Poppins ExtraBold'); ctx.set_font_size(30); e = ctx.text_extents(lab)
        ctx.move_to(x0 + 155 - e[2]/2 - e[0], 627); ctx.set_source_rgba(0.1, 0.1, 0.1, 1); ctx.show_text(lab)
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 500, 1200, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.22))])); ctx.fill()

# ------------------------------------------------------------------ jewellery
def jewel(ctx):
    ctx.set_source(lin(ctx, 0, 0, 0, 800, [(0, '#5a0e1a'), (1, '#2a060c')])); ctx.paint()
    for k in range(10):  # gold arches on wall
        x = 100 + k*190
        ctx.move_to(x, 760); ctx.line_to(x, 330); ctx.arc(x + 70, 330, 70, math.pi, 2*math.pi); ctx.line_to(x + 140, 760)
        ctx.set_source_rgba(*hexc('#d8a83a', 0.55)); ctx.set_line_width(5); ctx.stroke()
        for j in range(3):  # necklaces on busts
            ctx.arc(x + 70, 420 + j*110, 30, 0.2, math.pi - 0.2); ctx.set_source_rgba(*hexc('#f2c84a')); ctx.set_line_width(5); ctx.stroke()
            ctx.arc(x + 70, 452 + j*110, 7, 0, 2*math.pi); ctx.set_source_rgba(*hexc('#e8344a' if (k + j) % 2 else '#2ac0a0')); ctx.fill()
    for x in (300, 960, 1620): glow(ctx, x, 120, 420, (1, 0.85, 0.5), 0.35)
    rrect(ctx, 660, 40, 600, 100, 14); ctx.set_source(lin(ctx, 0, 40, 0, 140, [(0, '#f8d870'), (1, '#b8862a')])); ctx.fill()
    ctx.select_font_face('Poppins ExtraBold'); ctx.set_font_size(52); e = ctx.text_extents('JOSE JEWELLERY')
    ctx.move_to(960 - e[2]/2 - e[0], 110); ctx.set_source_rgba(*hexc('#3a0a10')); ctx.show_text('JOSE JEWELLERY')
    # counter with velvet top + glass front
    ctx.rectangle(0, 780, W, 300); ctx.set_source(lin(ctx, 0, 780, 0, H, [(0, '#3a0a12'), (1, '#1a0408')])); ctx.fill()
    ctx.rectangle(0, 760, W, 40); ctx.set_source(lin(ctx, 0, 760, 0, 800, [(0, '#8a1a2a'), (1, '#4a0a14')])); ctx.fill()
    ctx.rectangle(100, 830, 1720, 210); ctx.set_source_rgba(0.9, 0.8, 0.6, 0.12); ctx.fill()
    for k in range(9):
        x = 180 + k*190; ctx.arc(x, 960, 40, 0.1, math.pi - 0.1); ctx.set_source_rgba(*hexc('#f2c84a')); ctx.set_line_width(6); ctx.stroke()
    ctx.move_to(140, 840); ctx.line_to(240, 1030); ctx.set_source_rgba(1, 1, 1, 0.25); ctx.set_line_width(12); ctx.stroke()
    ctx.rectangle(0, 0, W, H); ctx.set_source(rad(W/2, H/2, 500, 1200, [(0, (0, 0, 0, 0)), (1, (0, 0, 0, 0.35))])); ctx.fill()

BUILDERS = {'studio': studio, 'market': market, 'church': church, 'river': river, 'bakery': bakery, 'rail': rail, 'jewel': jewel,
            'card': card_bg(), 'card_blue': card_bg('#0e2a4a', '#040c1a'), 'card_green': card_bg('#0e3a2a', '#03140c'), 'card_red': card_bg('#3a0e18', '#10040a')}
_cache = {}
def get(name):
    if name not in _cache:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W*SC, H*SC); ctx = cairo.Context(surf); ctx.scale(SC, SC)
        BUILDERS[name](ctx); surf.flush(); _cache[name] = surf
    return _cache[name]

def paint(ctx, name):
    ctx.save(); ctx.scale(1/SC, 1/SC); ctx.set_source_surface(get(name), 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BILINEAR); ctx.paint(); ctx.restore()

if __name__ == '__main__':
    for n in ('studio', 'market', 'church', 'river', 'bakery', 'rail', 'jewel'):
        s = get(n); small = cairo.ImageSurface(cairo.FORMAT_ARGB32, 960, 540); c = cairo.Context(small); c.scale(0.25, 0.25); c.set_source_surface(s); c.paint()
        small.write_to_png(f'/home/claude/riddles/bg_{n}.png')
