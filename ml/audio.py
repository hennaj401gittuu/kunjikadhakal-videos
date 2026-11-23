import numpy as np
from scipy.signal import lfilter, butter
SR = 44100

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)

def env_ad(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t * d)
    na = max(1, int(a * SR)); e[:na] *= np.linspace(0, 1, na)
    return e

def pluck(f, dur, dec=4.0, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for k, a in ((1, 1), (2, .45*bright), (3, .2*bright), (4, .1*bright)):
        y += a * np.sin(2*np.pi*f*k*t) * np.exp(-t*dec*k*0.8)
    return y * env_ad(n, 0.004, 0.2)

def bell(f, dur, dec=2.5):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*f*4.01*t)*np.exp(-t*6) + 0.2*np.sin(2*np.pi*f*2*t)
    return y * env_ad(n, 0.003, dec)

def bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2*np.pi*f*t) + 0.3*np.sin(4*np.pi*f*t)) * env_ad(n, 0.01, 3.0)

def pad(fs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f in fs:
        for det in (0.997, 1.003):
            y += np.sin(2*np.pi*f*det*t)
    y /= (2*len(fs))
    e = np.minimum(1, np.minimum(t / 0.6, (dur - t) / 0.6)).clip(0, 1)
    return y * e * (1 + 0.15*np.sin(2*np.pi*0.5*t))

def noise(n, rng): return rng.standard_normal(n)

def hp(x, fc):
    b, a = butter(2, fc/(SR/2), 'high'); return lfilter(b, a, x)
def lp(x, fc):
    b, a = butter(2, fc/(SR/2), 'low'); return lfilter(b, a, x)
def bp(x, lo, hi):
    b, a = butter(2, [lo/(SR/2), hi/(SR/2)], 'band'); return lfilter(b, a, x)

def add(buf, x, i):
    if i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i+len(x)] += x

CH = {'M': [0, 4, 7], 'm': [0, 3, 7]}
MOODS = {
    #        bpm  root progression(semitone offsets from root, quality)   scale        inst    perc
    'happy':   (104, 60, [(0,'M'),(7,'M'),(9,'m'),(5,'M')], [0,2,4,7,9], 'pluck', 'shaker'),
    'busy':    (122, 65, [(0,'M'),(5,'M'),(7,'M'),(0,'M')], [0,2,4,7,9], 'pluck', 'tick'),
    'night':   (66, 57, [(0,'m'),(8,'M'),(3,'M'),(10,'M')], [0,3,5,7,10], 'bell', None),
    'sad':     (70, 62, [(0,'m'),(8,'M'),(3,'M'),(7,'M')], [0,3,5,7,10], 'bell', None),
    'storm':   (60, 52, [(0,'m'),(0,'m'),(8,'M'),(7,'m')], [0,3,7], 'storm', None),
    'warm':    (78, 65, [(0,'M'),(9,'m'),(5,'M'),(7,'M')], [0,2,4,7,9], 'bell', None),
    'hope':    (92, 67, [(0,'M'),(7,'M'),(9,'m'),(5,'M')], [0,2,4,7,9], 'pluck', 'shaker'),
    'festive': (128, 60, [(0,'M'),(5,'M'),(7,'M'),(0,'M')], [0,2,4,7,9], 'pluck', 'party'),
}

def music(mood, dur, seed=1):
    bpm, root, prog, scale, inst, perc = MOODS[mood]
    rng = np.random.default_rng(seed + hash(mood) % 1000)
    n = int(dur * SR) + SR
    y = np.zeros(n)
    beat = 60.0 / bpm; bar = beat * 4
    nbars = int(dur / bar) + 2
    # melody motif per 2 bars, repeated with variation
    motif = [int(rng.integers(0, len(scale))) for _ in range(8)]
    for b in range(nbars):
        r, q = prog[b % len(prog)]
        t0 = b * bar; i0 = int(t0 * SR)
        chord = [mtof(root - 12 + r + c) for c in CH[q]]
        if inst == 'storm':
            add(y, 0.5*pad([mtof(root - 24 + r), mtof(root - 12 + r + 7)], bar + 0.6), i0)
        else:
            add(y, 0.22*pad(chord, bar + 0.6), i0)
            add(y, 0.5*bass(mtof(root - 24 + r), beat*1.8), i0)
            add(y, 0.4*bass(mtof(root - 24 + r + 7), beat*1.8), int((t0 + beat*2) * SR))
        # melody
        steps = 8 if inst != 'bell' else 4
        for s in range(steps):
            if inst == 'storm':
                if rng.random() < 0.25:
                    f = mtof(root - 12 + scale[int(rng.integers(0, len(scale)))])
                    add(y, 0.25*bell(f, 3.0, 1.2), int((t0 + s*bar/steps) * SR))
                continue
            if rng.random() < (0.28 if mood in ('night', 'sad') else 0.18):
                continue
            idx = (motif[(s + (b % 2)*4) % 8] + (1 if (b // 4) % 2 and s % 3 == 0 else 0)) % len(scale)
            octv = 12 if rng.random() < 0.3 else 0
            f = mtof(root + scale[idx] + octv + (12 if inst == 'bell' else 0))
            ts = t0 + s * bar / steps
            if inst == 'pluck':
                add(y, 0.32*pluck(f, 0.8, 5.0 if mood != 'happy' else 4.0), int(ts*SR))
            else:
                add(y, 0.28*bell(f, 2.2, 2.0), int(ts*SR))
        # percussion
        if perc:
            for s in range(8):
                ts = t0 + s*beat/2; i = int(ts*SR)
                if perc in ('shaker', 'party'):
                    nz = hp(noise(int(0.05*SR), rng), 6000) * env_ad(int(0.05*SR), 0.002, 60)
                    add(y, (0.12 if s % 2 else 0.07)*nz, i)
                if perc == 'tick':
                    add(y, 0.12*bell(mtof(96), 0.08, 50), i)
                if perc == 'party' and s in (2, 6):
                    nz = bp(noise(int(0.12*SR), rng), 900, 3000) * env_ad(int(0.12*SR), 0.002, 30)
                    add(y, 0.25*nz, i)
                if perc == 'party' and s in (0, 4):
                    m = int(0.15*SR); tt = np.arange(m)/SR
                    add(y, 0.5*np.sin(2*np.pi*(50 + 90*np.exp(-tt*30))*tt)*np.exp(-tt*18), i)
    if mood == 'storm':
        rn = lp(noise(n, rng), 1800) * 0.25
        y += rn
    return y[:int(dur*SR)]

# ---------------- SFX ----------------
def sfx(kind, rng=None):
    rng = rng or np.random.default_rng(7)
    if kind == 'pop':
        m = int(0.18*SR); t = np.arange(m)/SR
        return 0.6*np.sin(2*np.pi*(300 + 900*t/0.18)*t)*np.exp(-t*25)
    if kind == 'hop':
        m = int(0.35*SR); t = np.arange(m)/SR
        return 0.45*np.sin(2*np.pi*(200*t + 1800*t*t))*np.exp(-t*7)
    if kind == 'flap':
        out = np.zeros(int(0.6*SR))
        for k in range(4):
            nz = bp(noise(int(0.07*SR), rng), 300, 1500)*env_ad(int(0.07*SR), 0.01, 40)
            add(out, 0.5*nz, int(k*0.13*SR))
        return out
    if kind == 'buzz':
        m = int(2.0*SR); t = np.arange(m)/SR
        f = 230 + 25*np.sin(2*np.pi*7*t)
        s = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))
        return 0.08*lp(s, 1500)*np.minimum(1, np.minimum(t/0.2, (2.0 - t)/0.3))
    if kind == 'thunder':
        m = int(3.0*SR); t = np.arange(m)/SR
        return 0.9*lp(noise(m, rng), 300)*np.exp(-t*1.2)*(1 + 0.6*np.sin(2*np.pi*3*t))
    if kind == 'chirp':
        out = np.zeros(int(1.2*SR))
        for k in range(5):
            m = int(0.09*SR); t = np.arange(m)/SR
            add(out, 0.25*np.sin(2*np.pi*(2800*t + 9000*t*t))*np.exp(-t*20), int((k*0.2 + rng.random()*0.05)*SR))
        return out
    if kind == 'chime':
        out = np.zeros(int(2.5*SR))
        for k, mm in enumerate((84, 88, 91, 96)):
            add(out, 0.22*bell(mtof(mm), 2.0, 2.5), int(k*0.12*SR))
        return out
    if kind == 'growl':
        m = int(1.0*SR); t = np.arange(m)/SR
        return 0.5*lp(np.sin(2*np.pi*70*t)*(1 + np.sin(2*np.pi*9*t)), 400)*np.minimum(1, (1 - t)*3)
    if kind == 'hoot':
        out = np.zeros(int(1.4*SR))
        for k in range(2):
            m = int(0.45*SR); t = np.arange(m)/SR
            add(out, 0.35*np.sin(2*np.pi*(380 + 15*np.sin(2*np.pi*6*t))*t)*np.sin(np.pi*t/0.45), int(k*0.6*SR))
        return out
    if kind in ('pick', 'plant'):
        m = int(0.2*SR); t = np.arange(m)/SR
        return 0.5*np.sin(2*np.pi*(180 if kind == 'plant' else 520)*t)*np.exp(-t*30)
    if kind in ('push', 'rollback', 'teampush'):
        m = int(1.4*SR); t = np.arange(m)/SR
        return 0.5*lp(noise(m, rng), 200)*np.minimum(1, np.minimum(t/0.2, (1.4 - t)/0.4))
    if kind == 'climb':
        out = np.zeros(int(1.5*SR))
        for k in range(10):
            add(out, 0.2*bell(mtof(80 + (k % 3)), 0.05, 60), int(k*0.13*SR))
        return out
    if kind == 'swoosh':
        m = int(0.5*SR); t = np.arange(m)/SR
        return 0.35*bp(noise(m, rng), 500, 4000)*np.sin(np.pi*t/0.5)
    return None
