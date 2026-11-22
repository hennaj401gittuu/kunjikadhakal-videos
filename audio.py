import numpy as np, soundfile as sf, json, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scipy.signal import resample_poly, lfilter, butter
exec(open("script.py").read())
from render_seg import seg_dur, LEAD
SR = 44100
durs = [seg_dur(i) for i in range(len(S))]
# actual encoded frame counts -> exact durations
durs = [round(round(d * 30) / 30, 6) for d in durs]
starts = np.concatenate([[0], np.cumsum(durs)[:-1]])
T = float(sum(durs)); N = int(T * SR) + SR
voice = np.zeros(N, np.float32)
for i, (scn, p, t) in enumerate(S):
    if scn == "chapter": continue
    a, sr = sf.read(f"vo/{i:03d}.wav", dtype="float32")
    a = resample_poly(a, 147, 80).astype(np.float32)
    o = int((starts[i] + LEAD) * SR)
    voice[o:o + len(a)] += a[:N - o]
voice /= (np.abs(voice).max() + 1e-6); voice *= 0.89

# ---- music: dark drone pads ----
rng = np.random.default_rng(1)
tt = np.arange(N) / SR
chords = [[55.0, 82.41, 130.81, 164.81], [43.65, 87.31, 130.81, 174.61], [36.71, 73.42, 110.0, 174.61], [41.2, 82.41, 123.47, 196.0]]
music = np.zeros(N, np.float32)
seglen = 16.0
for k in range(int(T / seglen) + 2):
    ch = chords[k % 4]
    s0 = int(max(0, (k * seglen - 2) * SR)); s1 = min(N, int(((k + 1) * seglen + 2) * SR))
    if s0 >= N: break
    x = tt[s0:s1]
    env = np.clip(np.minimum((x - (k * seglen - 2)) / 3.0, ((k + 1) * seglen + 2 - x) / 3.0), 0, 1)
    sig = np.zeros_like(x)
    for f in ch:
        for det in (-0.6, 0.0, 0.7):
            sig += np.sin(2 * np.pi * (f + det) * x) * 0.5 + 0.12 * np.sin(2 * np.pi * 2 * (f + det) * x)
    sig *= (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * x + k))
    music[s0:s1] += (sig * env).astype(np.float32)
b, a = butter(2, 900 / (SR / 2)); music = lfilter(b, a, music).astype(np.float32)
# wind noise
wn = rng.standard_normal(N).astype(np.float32)
b, a = butter(2, [200 / (SR / 2), 700 / (SR / 2)], btype="band"); wn = lfilter(b, a, wn).astype(np.float32)
wn *= (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * tt)).astype(np.float32)
music = music / (np.abs(music).max() + 1e-6) + 0.25 * wn / (np.abs(wn).max() + 1e-6)
# slow heartbeat-ish pulse under it
pulse = np.zeros(N, np.float32)
for s0 in np.arange(0, T, 1.6):
    for off, amp in ((0, 1.0), (0.28, 0.6)):
        o = int((s0 + off) * SR); L = int(0.25 * SR)
        if o + L >= N: break
        x = np.arange(L) / SR
        pulse[o:o + L] += amp * np.sin(2 * np.pi * 48 * x) * np.exp(-x * 18)
music += 0.35 * pulse
music /= np.abs(music).max() + 1e-6

# ---- sfx ----
sfx = np.zeros(N, np.float32)
def boom(t0, amp=1.0):
    o = int(t0 * SR); L = int(3.0 * SR)
    if o + L >= N: return
    x = np.arange(L) / SR
    f = 70 * np.exp(-x * 1.5) + 30
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 1.6)
    nz = rng.standard_normal(L) * np.exp(-x * 6) * 0.25
    sfx[o:o + L] += amp * (s + nz).astype(np.float32)
def ring(t0, dur):
    o = int(t0 * SR); L = int(dur * SR)
    x = np.arange(L) / SR
    gate = ((x % 1.6) < 0.8).astype(np.float32)
    s = (np.sin(2 * np.pi * 440 * x) + np.sin(2 * np.pi * 480 * x)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 20 * x)))
    sfx[o:o + L] += 0.12 * (s * gate).astype(np.float32)
def stampfx(t0):
    o = int(t0 * SR); L = int(0.3 * SR); x = np.arange(L) / SR
    sfx[o:o + L] += (0.6 * rng.standard_normal(L) * np.exp(-x * 30) + np.sin(2 * np.pi * 90 * x) * np.exp(-x * 20)).astype(np.float32)
for i, (scn, p, t) in enumerate(S):
    st = starts[i]
    if scn in ("chapter",): boom(st + 0.05, 1.0)
    if scn == "title": boom(st + 0.1, 0.8)
    if scn == "phone": ring(st + 0.0, min(2.4, durs[i]))
    if scn == "lab": stampfx(st + 0.3 + 0.8 + 16 * 0.08 + 0.6)
    if scn == "reveal": stampfx(st + 4.0)
    if scn == "sketch": stampfx(st + 1.2)
    if scn == "file": stampfx(st + durs[i] * 0.55)
    if scn == "end": boom(st + 0.05, 0.6)
# ---- ducking ----
env = np.abs(voice)
k = int(0.3 * SR); env = np.convolve(env, np.ones(k) / k, mode="same")
duck = np.where(env > 0.01, 0.10, 0.22).astype(np.float32)
k2 = int(0.5 * SR); duck = np.convolve(duck, np.ones(k2) / k2, mode="same").astype(np.float32)
mix = voice + music * duck + sfx * 0.35
mix /= np.abs(mix).max() + 1e-6
mix = mix[:int(T * SR)]
sf.write("mix_raw.wav", np.stack([mix, mix], 1), SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "mix_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", "-c:a", "aac", "-b:a", "160k", "mix.m4a"], check=True)
# chapters
ch = []
for i, (scn, p, t) in enumerate(S):
    if scn == "chapter": ch.append((starts[i], f"{p['title']}: {p['sub']}"))
json.dump({"T": T, "starts": [float(x) for x in starts], "chapters": ch}, open("timeline.json", "w"))
print("audio", T / 60)
