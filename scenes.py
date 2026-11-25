from draw import *

_cache = {}
def C(name, fn):
    if name not in _cache:
        _cache[name] = fn()
    return _cache[name]

KP = Pose(540, 1000, 2.0)          # kitchen ant pose
REST_L, REST_R = (400, 1190), (680, 1190)

def paint(ctx, surf):
    ctx.set_source_surface(surf, 0, 0); ctx.paint()

def zoom(ctx, t, d, amt=0.04, cx=540, cy=1000, base=1.0):
    z = base * (1 + amt * t / d)
    ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy)

def kitchen_start(ctx, t, d, amt=0.04):
    ctx.save(); zoom(ctx, t, d, amt, base=1.1)
    paint(ctx, C('kbg', kitchen_bg))

def kitchen_end(ctx):
    ctx.restore()
    warm_glow(ctx); vignette(ctx, 0.3)

def counter(ctx):
    paint(ctx, C('kfg', counter_fg))

def wobble(t, f=6, a=6):
    return math.sin(t * f) * a

def bob(t):
    return math.sin(t * 2.2) * 4

# ------------------------------------------------------------------ S1 living room
def s_room(ctx, t, d):
    ctx.save(); zoom(ctx, t, d, 0.05, 500, 1500, base=1.6)
    paint(ctx, C('room', room_bg))
    twitch = math.sin(seg(t, 3.7, 4.1) * math.pi)
    draw_cat(ctx, 700, 1360, 0.85, t, twitch=twitch)
    # zzz
    for i in range(3):
        ph = (t * 0.35 + i / 3) % 1
        a = math.sin(ph * math.pi)
        text(ctx, 'z', 470 + ph * 40 + math.sin(ph * 6) * 15, 1330 - ph * 200, 40 + ph * 40, '#7E8597', alpha=a * 0.9)
    # bag of chips + spilled chips
    ctx.save(); ctx.translate(250, 1560); ctx.rotate(-0.25)
    rr(ctx, -110, -150, 220, 200, 24)
    ctx.set_source(linear(-110, 0, 110, 0, [(0, '#E14B5A'), (1, '#B92F44')])); ctx.fill()
    rr(ctx, -70, -110, 140, 90, 16); setc(ctx, '#FFF4E0'); ctx.fill()
    text(ctx, 'CHOCO', 0, -72, 32, '#5B2C12'); text(ctx, 'CHIPS', 0, -36, 32, '#5B2C12')
    ctx.restore()
    rnd = random.Random(7)
    spots = [(330 + rnd.uniform(0, 110), 1630 + rnd.uniform(0, 50), rnd.uniform(-0.6, 0.6)) for _ in range(6)]
    for x, y, r in spots:
        chip_shape(ctx, x, y, 20, r)
    # ant
    s = 0.58; feet = 1700
    ty = feet - 262 * s
    if t < 2.8:
        x = lerp(-120, 470, ease(seg(t, 0.2, 2.8))); flip = False; walk = 1.0 if t < 2.7 else 0
        ph = t * 9; carry = 0
    elif t < 4.6:
        x = 470; flip = False; walk = 0; ph = 0; carry = ease(seg(t, 3.0, 3.5))
    else:
        x = lerp(470, -250, ease(seg(t, 4.7, 7.0)) ** 1.2); flip = True; walk = 1.0; ph = t * 11; carry = 1
    pose = Pose(x, ty + (-abs(math.sin(ph)) * 8 if walk else 0), s, flip)
    look = (0.6 if not flip else -0.6, 0.6) if t < 3.6 else ((0, 0.1) if t < 4.6 else (-0.5, 0))
    mouth = 0.0
    if 3.8 < t < 4.6:
        look = (0.1, 0.0); mouth = 0.35
    # chip in hands
    pick = seg(t, 2.6, 3.0)
    if carry == 0 and t > 2.6:
        hy_ = lerp(110, 230, ease(pick))
        lh = pose.world((-45, hy_)); rh = pose.world((45, hy_))
    elif carry > 0:
        hy_ = lerp(230, -330, eob(carry)); hx_ = lerp(48, 112, ease(carry))
        lh = pose.world((-hx_, hy_)); rh = pose.world((hx_, hy_))
    else:
        sw = math.sin(ph) * 20
        lh = pose.world((-80, 80 + sw)); rh = pose.world((80, 80 - sw))
    big = (530, 1670)
    if t > 3.0:
        big = ((lh[0] + rh[0]) / 2, (lh[1] + rh[1]) / 2 - 28 * carry - 10 * (1 - carry))
    lean = 0.0
    if 2.4 < t < 3.2:
        lean = math.sin(seg(t, 2.4, 3.2) * math.pi) * 0.15
    draw_ant(ctx, pose, t, lh=lh, rh=rh, look=look, mouth=mouth, legs=True, walk=walk, phase=ph, part='body',
             tilt=lean)
    chip_shape(ctx, big[0], big[1], 52, 0.1 if t > 3 else 0.5)
    draw_ant(ctx, pose, t, lh=lh, rh=rh, part='arms')
    if 3.8 < t < 4.6:
        a = math.sin(seg(t, 3.8, 4.6) * math.pi)
        text(ctx, '!', x + 90, ty - 220, 90, '#E14B5A', outline='#FFFFFF', alpha=a)
    ctx.restore()
    warm_glow(ctx); vignette(ctx, 0.35)
    # title
    if t < 3.0:
        a = clamp(seg(t, 0.2, 0.7)) * (1 - seg(t, 2.5, 3.0))
        sc = eob(seg(t, 0.2, 0.8))
        ctx.save(); ctx.translate(540, 330); ctx.scale(sc, sc)
        text(ctx, "Mama Ant's", 0, -20, 92, '#E2577F', outline='#FFFFFF', ow=18, alpha=a)
        text(ctx, 'Cookie Day', 0, 90, 120, '#8A4A1A', outline='#FFFFFF', ow=20, alpha=a)
        ctx.restore()

# ------------------------------------------------------------------ S2 home arrival
def s_home(ctx, t, d):
    ctx.save(); zoom(ctx, t, d, 0.04, 600, 1300, base=1.5)
    paint(ctx, C('home', home_bg))
    cheer = seg(t, 1.4, 1.8)
    for i, (bx, by) in enumerate(((680, 1185), (870, 1195))):
        b = abs(math.sin(t * 8 + i)) * 26 * cheer
        draw_baby(ctx, bx, by, 0.72, t, look=(-0.7, 0.1), mouth=0.8 * cheer, bounce=b, arms_up=cheer, seed=i + 1,
                  happy=cheer > 0.5 and (int(t * 3) % 2 == 0))
    table(ctx, 775, 1270, 520)
    s = 0.75; ty = 1560 - 262 * s
    x = lerp(240, 470, ease(seg(t, 0.1, 1.8)))
    walk = 1.0 if t < 1.8 else 0.0
    ph = t * 10
    pose = Pose(x, ty - (abs(math.sin(ph)) * 8 if walk else 0), s)
    lift = math.sin(seg(t, 2.0, 2.6) * math.pi) * 30
    lh = pose.world((-112, -330 - lift)); rh = pose.world((112, -330 - lift))
    draw_ant(ctx, pose, t, lh=lh, rh=rh, look=(0.7, 0.1), legs=True, walk=walk, phase=ph, part='body',
             mouth=0.5 if t > 1.8 else 0.0)
    chip_shape(ctx, (lh[0] + rh[0]) / 2, (lh[1] + rh[1]) / 2 - 35, 66, 0.05)
    draw_ant(ctx, pose, t, lh=lh, rh=rh, part='arms')
    # hearts
    rnd = random.Random(2)
    for k in range(7):
        st = 1.6 + k * 0.25
        p = seg(t, st, st + 1.6)
        if 0 < p < 1:
            hx = rnd.uniform(560, 960); hy = 1000 - p * 400
            heart(ctx, hx + math.sin(p * 8) * 20, hy, 26 + 10 * rnd.random(), '#FF5C8A', math.sin(p * math.pi))
            ctx.fill()
    ctx.restore()
    warm_glow(ctx); vignette(ctx, 0.3)

# ------------------------------------------------------------------ K1 chop chip
def k_chop(ctx, t, d):
    kitchen_start(ctx, t, d)
    draw_ant(ctx, KP, t, part='body', look=(0, 0.75), mouth=0.0)
    counter(ctx)
    board(ctx, 540, 1290, 560, 120)
    chops = clamp((t - 0.6) / 2.8) * 8
    n = int(chops)
    big_s = lerp(62, 0, clamp(chops / 8))
    rnd = random.Random(11)
    pieces = [(rnd.uniform(400, 700), rnd.uniform(1255, 1300), rnd.uniform(-1, 1)) for _ in range(30)]
    shown = min(30, int(chops * 3.8))
    for i in range(shown):
        x, y, r = pieces[i]
        jump = 0
        chop_ph = (chops - int(chops))
        if i >= shown - 4:
            jump = math.sin(clamp(chop_ph * 2) * math.pi) * 25
        chip_shape(ctx, x, y - jump, 13, r)
    if big_s > 2:
        chip_shape(ctx, 450, 1265, big_s, -1.4)
    # knife motion
    if 0.6 < t < 3.4:
        ph = (chops - n)
        up = abs(math.cos(ph * math.pi))
        kx = lerp(620, 470, clamp(chops / 8))
        rh = (kx + 40, 1150 + (1 - up) * 85)
    else:
        rh = (700, 1200)
    lh = (370, 1250) if t < 3.4 else REST_L
    draw_ant(ctx, KP, t, lh=lh, rh=rh, part='arms')
    knife(ctx, rh[0], rh[1], 1.0, 2.6 if 0.6 < t < 3.4 else 2.9)
    kitchen_end(ctx)

# ------------------------------------------------------------------ bowl contents helpers
BOWL = Bowl()
def egg_extra(yolk=1.0):
    def f(ctx, cx, level, w, hh):
        if yolk > 0:
            ctx.set_source(radial(cx - 20, level - 12, 2, 50, [(0, '#FFE27A'), (0.7, '#FFB21E'), (1, '#E58A0B')]))
            ell(ctx, cx + 10, level, 46 * yolk, 30 * yolk); ctx.fill()
            setc(ctx, '#FFFFFF', 0.6); ell(ctx, cx - 6, level - 10, 12 * yolk, 7 * yolk); ctx.fill()
    return f

def mound(col, r):
    def f(ctx, cx, level, w, hh):
        if r <= 0: return
        ctx.set_source(radial(cx - r * 0.3, level - r * 0.5, 2, r * 1.3, [(0, '#FFFFFF'), (1, col)]))
        ctx.move_to(cx - r * 1.3, level + 4)
        ctx.curve_to(cx - r * 0.8, level - r * 0.7, cx + r * 0.8, level - r * 0.7, cx + r * 1.3, level + 4)
        ctx.curve_to(cx + r * 0.4, level + r * 0.25, cx - r * 0.4, level + r * 0.25, cx - r * 1.3, level + 4)
        ctx.fill()
    return f

def combo(*fs):
    def f(*a):
        for g in fs:
            g(*a)
    return f

# ------------------------------------------------------------------ K2 egg
def k_egg(ctx, t, d):
    kitchen_start(ctx, t, d)
    happy = 2.2 < t < 2.9
    draw_ant(ctx, KP, t, part='body', look=(0, 0.6), happy=happy, mouth=0.4 if happy else 0)
    counter(ctx)
    # shells on counter afterwards
    BOWL.back(ctx)
    yolk_in = seg(t, 1.85, 2.15)
    if yolk_in > 0:
        BOWL.contents(ctx, 0.17, '#FFF1D2', '#FFF7E4', extra=egg_extra(eob(yolk_in)))
    # hands
    if t < 1.0:
        p = ease(seg(t, 0.1, 0.8))
        lh = lerp2((360, 1220), (450, 1100), p); rh = lerp2(REST_R, (600, 1090), p)
    elif t < 1.35:
        k = seg(t, 1.0, 1.35); tap = math.sin(k * math.pi * 2) * 25
        lh = (450 + tap, 1110); rh = (600, 1090)
    else:
        p = ease(seg(t, 1.35, 1.7))
        lh = lerp2((470, 1080), (470, 1020), p); rh = lerp2((610, 1080), (610, 1020), p)
        if t > 2.5:
            q = ease(seg(t, 2.5, 3.2))
            lh = lerp2(lh, (300, 1260), q); rh = lerp2(rh, (780, 1260), q)
    draw_ant(ctx, KP, t, lh=lh, rh=rh, part='arms')
    if t < 1.35:
        egg(ctx, lh[0] + 30, lh[1] - 10, 1.0, 0.2, crack=1 if t > 1.15 else 0)
    elif t < 3.0:
        sp = ease(seg(t, 1.35, 1.75)) * 0.9
        shell_half(ctx, lh[0] + 20, lh[1] + 10, 1.0, -sp, top=False)
        shell_half(ctx, rh[0] - 20, rh[1] + 10, 1.0, sp, top=True)
        # falling yolk
        fall = seg(t, 1.6, 1.9)
        if 0 < fall < 1:
            y = lerp(1060, 1235, fall ** 2)
            ctx.set_source(radial(540, y - 8, 2, 40, [(0, '#FFE27A'), (1, '#F29A0E')])); ell(ctx, 540, y, 32, 38); ctx.fill()
            setc(ctx, '#FFF7E4', 0.7); ell(ctx, 540, y - 30, 24, 30); ctx.fill()
    if t > 3.0:
        shell_half(ctx, 240, 1365, 0.9, 0.3, top=False); shell_half(ctx, 300, 1368, 0.9, 2.8, top=False)
    if 1.1 < t < 1.6:
        a = math.sin(seg(t, 1.1, 1.6) * math.pi)
        text(ctx, 'crack!', 300, 1000, 56, '#8A4A1A', outline='#FFFFFF', alpha=a)
    BOWL.front(ctx)
    egg(ctx, 870, 1365, 1.0, 0.1)
    kitchen_end(ctx)

# ------------------------------------------------------------------ K3 sugar
def jar_held(ctx, hx, hy, rot, w=150, h=190, label='Sugar'):
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(rot)
    canister(ctx, 0, h / 2, w, h, label)
    ctx.restore()
    mx = hx + (h / 2 + 20) * math.sin(rot); my = hy - (h / 2 + 20) * math.cos(rot)
    return mx, my

def pour_stream(ctx, x0, y0, y1, t, col='#FFFFFF', n=70, width=26, seed=1, amt=1.0):
    if amt <= 0: return
    rnd = random.Random(seed)
    setc(ctx, col, 0.75 * amt); ctx.set_line_width(width * 0.45 * amt); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x0, y0); ctx.curve_to(x0 - 10, y0 + 40, x0 - 14, y0 + 60, x0 - 14, y1); ctx.stroke()
    for i in range(n):
        ph = (t * 1.8 + i / n) % 1
        xx = x0 - 14 * min(1, ph * 3) + rnd.uniform(-width / 2, width / 2) * (0.5 + ph)
        yy = lerp(y0, y1, ph)
        setc(ctx, col, 0.9 * amt); ell(ctx, xx, yy, 4, 4); ctx.fill()

def k_sugar(ctx, t, d):
    kitchen_start(ctx, t, d)
    draw_ant(ctx, KP, t, part='body', look=(0.2, 0.6), mouth=0.15)
    counter(ctx)
    BOWL.back(ctx)
    pour = seg(t, 1.3, 2.8)
    level = BOWL.contents(ctx, 0.17, '#FFF1D2', '#FFF7E4', extra=combo(egg_extra(), mound('#F3EEE6', 60 * pour)))
    lift = ease(seg(t, 0.3, 1.0)); back = ease(seg(t, 2.9, 3.4))
    tilt = ease(seg(t, 1.0, 1.4)) * (1 - back)
    base = (890, 1295)
    hp = lerp2(base, (720, 1060), lift)
    hp = lerp2(hp, base, back)
    rot = -1.75 * tilt
    lh = REST_L
    draw_ant(ctx, KP, t, lh=lh, rh=hp if t > 0.25 else lerp2(REST_R, base, ease(seg(t, 0, 0.25))), part='arms')
    mx, my = jar_held(ctx, hp[0], hp[1], rot)
    if 1.3 < t < 2.85:
        pour_stream(ctx, mx, my, level or 1230, t, '#FFFFFF', amt=min(1, seg(t, 1.3, 1.45) * (1 - seg(t, 2.7, 2.85)) * 3))
    BOWL.front(ctx)
    kitchen_end(ctx)

# ------------------------------------------------------------------ K4 butter + whisk
def k_whisk(ctx, t, d):
    kitchen_start(ctx, t, d)
    happy = 3.0 < t < 3.6
    draw_ant(ctx, KP, t, part='body', look=(0, 0.7), mouth=0.35 if t > 1.2 else 0, happy=happy)
    counter(ctx)
    BOWL.back(ctx)
    mix = ease(seg(t, 1.4, 3.8))
    butter_in = seg(t, 0.5, 0.85)
    def ext(ctx, cx, level, w, hh):
        if mix < 0.6:
            egg_extra(1 - mix / 0.6)(ctx, cx, level, w, hh)
            mound('#F3EEE6', 60 * (1 - mix / 0.6))(ctx, cx, level, w, hh)
        if butter_in >= 1:
            bs = 1.0 - mix
            if bs > 0.05:
                butter(ctx, cx - 50 + math.sin(t * 4) * 20, level - 15, bs)
    col = lerp_hex('#FFF1D2', '#F9DC86', mix); top = lerp_hex('#FFF7E4', '#FCEAAE', mix)
    BOWL.contents(ctx, lerp(0.17, 0.26, mix), col, top, extra=ext, swirl=mix, t=t)
    # butter falling
    if t < 0.5:
        lh = lerp2(REST_L, (450, 1060), ease(seg(t, 0, 0.4)))
        butter(ctx, lh[0] + 10, lh[1] - 20, 1.0)
    elif butter_in < 1:
        lh = (450, 1060)
        butter(ctx, 490, lerp(1060, 1215, butter_in ** 2), 1.0)
    else:
        lh = lerp2((450, 1060), (360, 1200), ease(seg(t, 0.9, 1.3)))
    if t < 1.2:
        rh = lerp2(REST_R, (700, 1100), ease(seg(t, 0.4, 1.1)))
        wr = 0.4
    else:
        a = (t - 1.2) * 11
        rh = (560 + math.cos(a) * 85, 1105 + math.sin(a) * 22)
        wr = 0.25 + math.cos(a) * 0.25
    draw_ant(ctx, KP, t, lh=lh, rh=rh, part='arms')
    whisk(ctx, rh[0], rh[1], 1.0, wr)
    BOWL.front(ctx)
    if 1.6 < t < 3.8:
        text(ctx, 'whisk whisk!', 540, 560 - math.sin(t * 6) * 6, 54, '#E2577F', outline='#FFFFFF',
             alpha=math.sin(seg(t, 1.6, 3.8) * math.pi))
    kitchen_end(ctx)

# ------------------------------------------------------------------ K5 flour
def flour_bag(ctx, hx, hy, rot):
    w, h = 170, 210
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(rot)
    ctx.move_to(-w / 2, h / 2); ctx.line_to(-w / 2 + 6, -h / 2 + 20); ctx.line_to(-w / 2 + 20, -h / 2)
    for k in range(6):
        ctx.line_to(-w / 2 + 20 + (k + 0.5) * (w - 40) / 6, -h / 2 - 12); ctx.line_to(-w / 2 + 20 + (k + 1) * (w - 40) / 6, -h / 2)
    ctx.line_to(w / 2 - 6, -h / 2 + 20); ctx.line_to(w / 2, h / 2); ctx.close_path()
    ctx.set_source(linear(-w / 2, 0, w / 2, 0, [(0, '#F4E6CB'), (1, '#D8C29C')])); ctx.fill()
    text(ctx, 'Flour', 0, 30, 46, '#8A5A2A', font='Pacifico', weight=cairo.FONT_WEIGHT_NORMAL)
    setc(ctx, '#C9A061'); ctx.set_line_width(4)
    ctx.move_to(0, 50); ctx.line_to(0, 85); ctx.stroke()
    for k in range(3):
        ell(ctx, -7, 55 + k * 10, 6, 4); ctx.fill(); ell(ctx, 7, 55 + k * 10, 6, 4); ctx.fill()
    ctx.restore()
    return hx + (h / 2 + 10) * math.sin(rot), hy - (h / 2 + 10) * math.cos(rot)

def puff(ctx, x, y, p, seed=3):
    if p <= 0 or p >= 1: return
    rnd = random.Random(seed)
    for k in range(10):
        a = rnd.uniform(math.pi, TAU); r = rnd.uniform(40, 140) * ease(p)
        setc(ctx, '#FFFFFF', 0.55 * (1 - p)); ell(ctx, x + math.cos(a) * r * 1.4, y + math.sin(a) * r * 0.8, 30 + 40 * p, 30 + 40 * p); ctx.fill()

def k_flour(ctx, t, d):
    kitchen_start(ctx, t, d)
    happy = 2.2 < t < 3.1
    draw_ant(ctx, KP, t, part='body', look=(-0.2, 0.6), happy=happy, mouth=0.5 if happy else 0.1)
    counter(ctx)
    BOWL.back(ctx)
    pour = seg(t, 1.2, 2.6)
    level = BOWL.contents(ctx, 0.26, '#F9DC86', '#FCEAAE', extra=mound('#F7F1E8', 75 * pour), swirl=0.3, t=t)
    lift = ease(seg(t, 0.2, 0.9)); back = ease(seg(t, 2.8, 3.4))
    tilt = ease(seg(t, 0.9, 1.25)) * (1 - back)
    base = (200, 1260)
    hp = lerp2(lerp2(base, (360, 1030), lift), base, back)
    draw_ant(ctx, KP, t, lh=hp, rh=REST_R, part='arms')
    mx, my = flour_bag(ctx, hp[0], hp[1], 1.9 * tilt)
    if 1.2 < t < 2.7:
        pour_stream(ctx, mx, my, level or 1230, t, '#FBF7F0', width=34, amt=min(1, seg(t, 1.2, 1.35) * (1 - seg(t, 2.55, 2.7)) * 3))
    puff(ctx, 540, (level or 1230) - 20, seg(t, 1.5, 3.2))
    BOWL.front(ctx)
    kitchen_end(ctx)

# ------------------------------------------------------------------ K6 chips + stir
def ramekin(ctx, x, y, rot=0.0, chips=1.0, seed=4):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    rnd = random.Random(seed)
    for i in range(int(14 * chips)):
        chip_shape(ctx, rnd.uniform(-60, 60), rnd.uniform(-40, -20), 13, rnd.uniform(-1, 1))
    ctx.move_to(-80, -30); ctx.curve_to(-78, 40, 78, 40, 80, -30); ctx.close_path()
    ctx.set_source(linear(-80, 0, 80, 0, [(0, '#FFFFFF'), (1, '#E6DCCB')])); ctx.fill()
    setc(ctx, '#6FA06A'); ctx.set_line_width(5); ctx.move_to(-76, -18); ctx.curve_to(-40, -10, 40, -10, 76, -18); ctx.stroke()
    ctx.restore()

def dots_extra(t, n, rot_speed=2.0, mix=1.0, seed=9):
    def f(ctx, cx, level, w, hh):
        rnd = random.Random(seed)
        for i in range(n):
            a = rnd.uniform(0, TAU) + t * rot_speed * mix; r = rnd.uniform(0.1, 0.85)
            chip_shape(ctx, cx + math.cos(a) * w * r, level + math.sin(a) * hh * r - 4, 11, a)
    return f

def k_stir(ctx, t, d):
    kitchen_start(ctx, t, d)
    draw_ant(ctx, KP, t, part='body', look=(0.1, 0.65), mouth=0.3 if t > 2 else 0, happy=3.6 < t < 4.2)
    counter(ctx)
    BOWL.back(ctx)
    tilt = ease(seg(t, 0.6, 0.9)) * (1 - ease(seg(t, 1.6, 1.9)))
    drop = seg(t, 0.75, 1.6)
    mix = ease(seg(t, 1.9, 4.0))
    ndots = int(22 * drop)
    def ext(ctx, cx, level, w, hh):
        if mix < 0.5:
            mound('#F7F1E8', 75 * (1 - mix * 2))(ctx, cx, level, w, hh)
        dots_extra(t, ndots, 2.2, mix)(ctx, cx, level, w, hh)
    col = lerp_hex('#F9DC86', '#E8C48A', mix); top = lerp_hex('#FCEAAE', '#F0D3A0', mix)
    level = BOWL.contents(ctx, lerp(0.26, 0.36, mix), col, top, extra=ext, swirl=mix * 0.6, t=t)
    # ramekin in left hand
    lift = ease(seg(t, 0.0, 0.6)); back = ease(seg(t, 1.7, 2.2))
    base = (200, 1290)
    lh = lerp2(lerp2(base, (380, 1050), lift), (300, 1290), back)
    if t > 1.9:
        rh = (540 + math.cos((t - 1.9) * 7) * 90, 1110 + math.sin((t - 1.9) * 7) * 20)
        srot = 0.3 + math.cos((t - 1.9) * 7) * 0.3
    else:
        rh = lerp2(REST_R, (720, 1080), ease(seg(t, 1.2, 1.9))); srot = 0.4
    draw_ant(ctx, KP, t, lh=lh, rh=rh, part='arms')
    ramekin(ctx, lh[0] + 20, lh[1] - 10, 1.2 * tilt, chips=1 - drop)
    if 0 < drop < 1:
        rnd = random.Random(5)
        for i in range(14):
            st = i / 14 * 0.8; p = seg(drop, st, st + 0.25)
            if 0 < p < 1:
                chip_shape(ctx, lh[0] + 90 + rnd.uniform(-20, 30), lerp(lh[1] + 20, level, p * p), 13, i)
    spoon(ctx, rh[0], rh[1], 1.0, srot)
    BOWL.front(ctx)
    kitchen_end(ctx)

# ------------------------------------------------------------------ K7 scoop onto tray
BOWL2 = Bowl(cx=300, rimy=1170, rx=200, ry=46, by=1385, brx=120)
TRAY = (790, 1310, 440, 130)
SLOTS = tray_slots(*TRAY, cols=3, rows=2)

def k_scoop(ctx, t, d):
    kitchen_start(ctx, t, d)
    per = 0.55; start = 0.4
    i_now = int((t - start) / per) if t > start else -1
    ph = ((t - start) / per) % 1 if t > start else 0
    look_x = -0.5 if ph < 0.4 else 0.6
    draw_ant(ctx, KP, t, part='body', look=(look_x, 0.6), mouth=0.2, happy=t > 3.7)
    counter(ctx)
    tray(ctx, *TRAY)
    placed = min(6, max(0, i_now))
    BOWL2.back(ctx)
    level = BOWL2.contents(ctx, 0.36 - placed * 0.03, '#E8C48A', '#F0D3A0', extra=dots_extra(0, 16, seed=12))
    for k in range(placed):
        x, y, s = SLOTS[k]
        pop = eob(seg(t, start + (k + 1) * per - 0.05, start + (k + 1) * per + 0.2))
        dough_ball(ctx, x, y, s * 0.95 * max(pop, 0.01), 0, seed=k)
    if 0 <= i_now < 6:
        x, y, s = SLOTS[i_now]
        if ph < 0.4:
            hp = lerp2((420, 1120), (300, 1150), ease(ph / 0.4))
            carrying = ph > 0.25
        else:
            hp = lerp2((300, 1150), (x - 20, y - 120), ease((ph - 0.4) / 0.6)); carrying = True
    else:
        hp = REST_R if t > 3.8 else (420, 1120); carrying = False
    lh = (230, 1250)
    draw_ant(ctx, KP, t, lh=lh, rh=hp, part='arms')
    spoon(ctx, hp[0], hp[1], 0.9, 0.35)
    if carrying:
        tip = (hp[0] - math.sin(0.35) * 112, hp[1] + math.cos(0.35) * 112)
        dough_ball(ctx, tip[0], tip[1] - 6, 0.6, 0, seed=99)
    BOWL2.front(ctx)
    kitchen_end(ctx)

# ------------------------------------------------------------------ K8 oven
def k_oven(ctx, t, d):
    ctx.save(); zoom(ctx, t, d, 0.06, 540, 900)
    ctx.set_source(linear(0, 0, 0, H, [(0, '#F4C8B8'), (1, '#E0A894')])); ctx.paint()
    # oven body
    rr(ctx, 60, 260, 960, 1500, 60); ctx.set_source(linear(60, 0, 1020, 0, [(0, '#FFE3DA'), (0.5, '#FFD1C3'), (1, '#E9AFA0')])); ctx.fill()
    # control panel
    rr(ctx, 110, 300, 860, 220, 40); setc(ctx, '#F7EFE6'); ctx.fill()
    for k, x in enumerate((240, 420, 660, 840)):
        setc(ctx, '#D7CBBE'); ell(ctx, x, 410, 58, 58); ctx.fill()
        setc(ctx, '#FFFFFF'); ell(ctx, x, 404, 50, 50); ctx.fill()
        ang = -math.pi / 2 + (t * 1.3 if k == 3 else k * 0.8)
        setc(ctx, '#E2577F'); ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(x, 404); ctx.line_to(x + math.cos(ang) * 36, 404 + math.sin(ang) * 36); ctx.stroke()
    # handle
    rr(ctx, 200, 590, 680, 40, 20); ctx.set_source(linear(0, 590, 0, 630, [(0, '#FFFFFF'), (1, '#B8BEC8')])); ctx.fill()
    # window
    wx, wy, ww, wh = 150, 680, 780, 820
    rr(ctx, wx - 20, wy - 20, ww + 40, wh + 40, 50); setc(ctx, '#3A2620'); ctx.fill()
    ctx.save(); rr(ctx, wx, wy, ww, wh, 36); ctx.clip()
    glow = 0.85 + math.sin(t * 5) * 0.08
    ctx.set_source(radial(540, 950, 40, 700, [(0, '#FFC06A'), (0.5, '#E4782C'), (1, '#4A1D0C')])); ctx.paint()
    setc(ctx, '#FFF1B8', 0.35 * glow); ell(ctx, 540, 760, 300, 90); ctx.fill()
    # elements
    setc(ctx, '#FF5A1F', 0.8 * glow); ctx.set_line_width(10)
    ctx.move_to(wx + 60, wy + 60);
    for k in range(7):
        ctx.line_to(wx + 60 + k * 110 + 55, wy + 90 if k % 2 == 0 else wy + 60)
    ctx.stroke()
    # rack
    setc(ctx, '#9A8478'); ctx.set_line_width(6)
    for k in range(9):
        ctx.move_to(wx + 40 + k * 88, 1200); ctx.line_to(wx + 20 + k * 92, 1300); ctx.stroke()
    ctx.move_to(wx, 1200); ctx.line_to(wx + ww, 1200); ctx.stroke()
    bake = ease(seg(t, 0.4, 4.0))
    tr = (540, 1150, 620, 180)
    tray(ctx, *tr)
    for k, (x, y, s) in enumerate(tray_slots(*tr, cols=3, rows=2)):
        dough_ball(ctx, x, y, s * 1.15 * (1 + bake * 0.15), bake, seed=k)
    # heat shimmer
    for k in range(5):
        ph = (t * 0.5 + k / 5) % 1
        setc(ctx, '#FFE8B0', 0.15 * math.sin(ph * math.pi)); ell(ctx, 240 + k * 150, 1100 - ph * 300, 60, 20); ctx.fill()
    ctx.restore()
    # glass reflection
    ctx.save(); rr(ctx, wx, wy, ww, wh, 36); ctx.clip()
    ctx.move_to(wx + 80, wy); ctx.line_to(wx + 260, wy); ctx.line_to(wx + 60, wy + wh); ctx.line_to(wx - 120, wy + wh); ctx.close_path()
    setc(ctx, '#FFFFFF', 0.12); ctx.fill(); ctx.restore()
    # ant peeking
    pk = eob(seg(t, 0.6, 1.3))
    pose = Pose(930, lerp(2300, 1880, pk), 1.6)
    draw_ant(ctx, pose, t, look=(-0.6, -0.5), mouth=0.5 if t > 4.2 else 0.0, part='body', happy=t > 4.3)
    draw_ant(ctx, pose, t, lh=pose.world((-90, -170)), rh=pose.world((70, 60)), part='arms')
    ctx.restore()
    if t > 4.1:
        p = seg(t, 4.1, 4.5)
        ctx.save(); ctx.translate(540, 240); ctx.scale(eob(p), eob(p)); ctx.rotate(math.sin(t * 20) * 0.05)
        text(ctx, 'DING!', 0, 40, 120, '#E2577F', outline='#FFFFFF', ow=20)
        ctx.restore()
        for k in range(6):
            a = k * TAU / 6 + t
            sparkle(ctx, 540 + math.cos(a) * 280 * p, 220 + math.sin(a) * 100 * p, 26, p)
    warm_glow(ctx, 0.15); vignette(ctx, 0.35)

# ------------------------------------------------------------------ K9 out of oven
def k_out(ctx, t, d):
    kitchen_start(ctx, t, d, 0.05)
    up = eob(seg(t, 0.1, 1.0))
    sniff = t > 1.3
    draw_ant(ctx, KP, t, part='body', look=(0, 0.5), happy=sniff, mouth=0.6 if sniff else 0.3,
             tilt=math.sin(t * 3) * 0.05 if sniff else 0)
    counter(ctx)
    cy = lerp(1700, 1230, up)
    tr = (540, cy, 560, 170)
    lh = (540 - 300, cy + 40); rh = (540 + 300, cy + 40)
    tray(ctx, *tr)
    for k, (x, y, s) in enumerate(tray_slots(*tr, cols=3, rows=2)):
        dough_ball(ctx, x, y, s * 1.3, 1.0, seed=k)
    draw_ant(ctx, KP, t, lh=lh, rh=rh, part='arms', mitt=True)
    steam(ctx, 540, cy - 60, t, n=4, h=260, a=0.55, spread=110)
    for k in range(5):
        p = (t * 0.7 + k / 5) % 1
        sparkle(ctx, 300 + k * 120, cy - 40 - p * 200, 18 * math.sin(p * math.pi), math.sin(p * math.pi))
    if t > 1.4:
        a = seg(t, 1.4, 1.8)
        text(ctx, 'Mmm!', 820, 420, 90, '#8A4A1A', outline='#FFFFFF', ow=18, alpha=a)
    kitchen_end(ctx)

# ------------------------------------------------------------------ S3 serving
def s_serve(ctx, t, d):
    ctx.save(); zoom(ctx, t, d, 0.05, 560, 1300, base=1.45)
    paint(ctx, C('home', home_bg))
    tbl = (700, 1290, 600)
    babies = [(620, 1200), (830, 1210)]
    plate_c = (700, 1300)
    grab = [seg(t, 2.9 + i * 0.25, 3.5 + i * 0.25) for i in range(2)]
    eat = [clamp((t - 3.6 - i * 0.25)) for i in range(2)]
    bites = [min(3, int(max(0, t - 3.8 - i * 0.25) / 0.9) + (1 if t > 3.8 + i * 0.25 else 0)) for i in range(2)]
    for i, (bx, by) in enumerate(babies):
        s = 0.74
        excite = seg(t, 1.6, 2.0)
        chew = abs(math.sin((t - 3.6) * 9)) * 0.6 if eat[i] > 0 and t < d - 1.0 else 0
        b = abs(math.sin(t * 7 + i)) * 14 * excite * (1 - grab[i])
        if grab[i] > 0:
            src = (plate_c[0] + (i - 0.5) * 120, plate_c[1] - 30)
            mouth_w = (bx, by - 95 * s)
            cpos_w = lerp2(src, mouth_w, ease(grab[i]))
            hold_l = ((cpos_w[0] - bx) / s, (cpos_w[1] - by) / s)
            seed = 30 + i
            nb = bites[i]
            def cb(c, hold, seed=seed, nb=nb):
                cookie(c, hold[0], hold[1], 0.85, seed=seed, bite=nb)
            draw_baby(ctx, bx, by, s, t, look=(0, 0.4) if grab[i] < 1 else (0, 0), mouth=0 if chew else 0.6 * excite,
                      chew=chew, happy=eat[i] > 0, seed=i + 1, hold=hold_l, hold_cb=cb)
        else:
            draw_baby(ctx, bx, by, s, t, look=(-0.6, 0.2) if t < 2.2 else (0, 0.6), mouth=0.7 * excite,
                      bounce=b, arms_up=excite, seed=i + 1)
    table(ctx, *tbl)
    # mama
    s = 0.8; ty = 1600 - 262 * s
    x = lerp(-150, 330, ease(seg(t, 0.0, 1.8)))
    walk = 1.0 if t < 1.8 else 0.0
    ph = t * 10
    pose = Pose(x, ty - (abs(math.sin(ph)) * 8 if walk else 0), s)
    put = ease(seg(t, 1.9, 2.6))
    carry_w = pose.world((95, -60))
    pc = lerp2(carry_w, plate_c, put)
    remaining = [grab[i] <= 0 for i in range(2)]
    if put < 1:
        lh = (pc[0] - 120, pc[1] + 5); rh = (pc[0] + 30, pc[1] + 10)
    else:
        back = ease(seg(t, 2.6, 3.0))
        lh = lerp2((pc[0] - 120, pc[1] + 5), pose.world((-70, 60)), back)
        rh = lerp2((pc[0] + 30, pc[1] + 10), pose.world((70, -110)) if t > 3.6 else pose.world((70, 60)), back)
        if t > 3.6:
            rh = lerp2(pose.world((70, 60)), pose.world((60, -150)), ease(seg(t, 3.6, 4.0)))
    happy = t > 3.8
    draw_ant(ctx, pose, t, lh=lh, rh=rh, look=(0.7, 0.2), legs=True, walk=walk, phase=ph, part='body',
             happy=happy, mouth=0.4 if happy else 0.1)
    plate(ctx, pc[0], pc[1], 300)
    rnd_c = [(-0.5, 32), (0.5, 33), (-0.2, 34), (0.25, 35), (0, 36)]
    for j, (dx, sd) in enumerate(rnd_c):
        if j < 2 and not remaining[j]:
            continue
        oy = -30 if j < 2 else (-10 if j < 4 else -50)
        cookie(ctx, pc[0] + dx * 120 if j < 2 else pc[0] + dx * 160, pc[1] + oy, 0.85, seed=sd if j >= 2 else 30 + j)
    draw_ant(ctx, pose, t, lh=lh, rh=rh, part='arms')
    # crumbs + hearts
    rnd = random.Random(8)
    if t > 3.9:
        for k in range(14):
            st = 3.9 + k * 0.22
            p = seg(t, st, st + 1.8)
            if 0 < p < 1:
                bx, by = babies[k % 2]
                hx = bx + rnd.uniform(-90, 90); hy = by - 300 - p * 320
                heart(ctx, hx + math.sin(p * 7) * 18, hy, 22 + rnd.random() * 14, rnd.choice(['#FF5C8A', '#FF8FB0', '#E2577F']), math.sin(p * math.pi))
                ctx.fill()
    ctx.restore()
    warm_glow(ctx); vignette(ctx, 0.3)
    if t > 4.4:
        p = seg(t, 4.4, 4.8)
        ctx.save(); ctx.translate(540, 380); ctx.scale(eob(p), eob(p)); ctx.rotate(math.sin(t * 3) * 0.04)
        text(ctx, 'Yummy!', 0, 40, 150, '#E2577F', outline='#FFFFFF', ow=22)
        ctx.restore()
    if t > d - 2.0:
        p = seg(t, d - 2.0, d - 1.5)
        text(ctx, 'The End', 540, 1760, 110, '#8A4A1A', outline='#FFFFFF', ow=20, alpha=p)

SCENES = [
    ('room', s_room, 7.5, 0.5, 0.3),
    ('home', s_home, 4.5, 0.3, 0.3),
    ('chop', k_chop, 4.0, 0.3, 0.0),
    ('egg', k_egg, 4.0, 0.0, 0.0),
    ('sugar', k_sugar, 3.5, 0.0, 0.0),
    ('whisk', k_whisk, 4.3, 0.0, 0.0),
    ('flour', k_flour, 3.5, 0.0, 0.0),
    ('stir', k_stir, 4.5, 0.0, 0.0),
    ('scoop', k_scoop, 4.2, 0.0, 0.25),
    ('oven', k_oven, 5.2, 0.25, 0.25),
    ('out', k_out, 3.6, 0.25, 0.3),
    ('serve', s_serve, 8.2, 0.3, 0.9),
]

def frame(ctx, name, fn, t, d, fin, fout):
    fn(ctx, t, d)
    a = 0.0
    if fin > 0 and t < fin:
        a = 1 - t / fin
    if fout > 0 and t > d - fout:
        a = max(a, (t - (d - fout)) / fout)
    if a > 0:
        setc(ctx, '#FFF3E0', a); ctx.paint()
