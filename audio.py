"""Mix voice + light upbeat music + pop/ding/chime SFX, mux with short_v.mp4 -> short.mp4 (-14 LUFS)."""
import numpy as np, soundfile as sf, json, subprocess, os
from scipy.signal import resample_poly, butter, lfilter
ev = json.load(open("events.json"))
T, starts, LEAD = ev["T"], ev["starts"], ev["lead"]
SR = 44100
N = int(T * SR) + SR
voice = np.zeros(N, np.float32)
for i, s in enumerate(starts):
    a, sr = sf.read(f"vo/{i:03d}.wav", dtype="float32")
    a = resample_poly(a, 147, 80).astype(np.float32)
    o = int((s + LEAD) * SR)
    voice[o:o + len(a)] += a[:max(0, N - o)]
voice /= np.abs(voice).max() + 1e-6
tt = np.arange(N) / SR
rng = np.random.default_rng(2)

# music: bright plucky arpeggio over soft pad, 100 BPM, C - Am - F - G
chords = [[261.63, 329.63, 392.0], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66]]
beat = 60 / 100
music = np.zeros(N, np.float32)
bar = beat * 4
for k, s0 in enumerate(np.arange(0, T + bar, beat / 2)):
    ch = chords[int(s0 / bar) % 4]
    f = ch[k % 3] * (2 if k % 4 == 3 else 1)
    o = int(s0 * SR); L = min(int(0.5 * SR), N - o)
    if L <= 0: break
    x = np.arange(L) / SR
    music[o:o + L] += (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(4 * np.pi * f * x) + 0.1 * np.sin(6 * np.pi * f * x)) * np.exp(-x * 9) * 0.5
pad = np.zeros(N, np.float32)
for b0 in np.arange(0, T + bar, bar):
    ch = chords[int(b0 / bar) % 4]
    o = int(b0 * SR); L = min(int((bar + 0.3) * SR), N - o)
    if L <= 0: break
    x = np.arange(L) / SR
    env = np.minimum(1, x / 0.3) * np.minimum(1, (bar + 0.3 - x) / 0.3)
    pad[o:o + L] += sum(np.sin(2 * np.pi * f / 2 * x) for f in ch) * env * 0.18
bass = np.zeros(N, np.float32)
for b0 in np.arange(0, T + bar, beat):
    ch = chords[int(b0 / bar) % 4]
    o = int(b0 * SR); L = min(int(0.3 * SR), N - o)
    if L <= 0: break
    x = np.arange(L) / SR
    bass[o:o + L] += np.sin(2 * np.pi * ch[0] / 4 * x) * np.exp(-x * 8) * 0.5
hat = np.zeros(N, np.float32)
for s0 in np.arange(beat / 2, T, beat):
    o = int(s0 * SR); L = min(int(0.05 * SR), N - o)
    if L <= 0: break
    hat[o:o + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / SR * 80) * 0.12
b, a = butter(2, 6000 / (SR / 2), "high"); hat = lfilter(b, a, hat).astype(np.float32)
music = music + pad + bass + hat
music /= np.abs(music).max() + 1e-6

sfx = np.zeros(N, np.float32)
def add(o, sig):
    o = int(o * SR); L = min(len(sig), N - o)
    if L > 0: sfx[o:o + L] += sig[:L]
x = np.arange(int(0.35 * SR)) / SR
nz = rng.standard_normal(len(x)).astype(np.float32)
b1, a1 = butter(2, [400 / (SR / 2), 3000 / (SR / 2)], "band")
whoosh = lfilter(b1, a1, nz) * np.sin(np.pi * x / x[-1]) ** 2 * 0.6
popc = np.sin(2 * np.pi * (300 + 500 * x) * x) * np.exp(-x * 30) * 0.5
ding = (np.sin(2 * np.pi * 1318.5 * x) + 0.5 * np.sin(2 * np.pi * 1975.5 * x)) * np.exp(-x * 9) * 0.35
xc = np.arange(int(1.6 * SR)) / SR
chime = sum(np.sin(2 * np.pi * f * xc) * np.exp(-xc * 3) * 0.3 for f in (1046.5, 1318.5, 1568.0, 2093.0))
last = -1
for t0, kind in ev["events"]:
    if kind == "pop":
        if t0 - last < 0.09: continue
        last = t0; add(t0, whoosh * 0.7 + popc)
    elif kind == "ding":
        add(t0, ding)
    elif kind == "tick":
        xt = np.arange(int(0.08 * SR)) / SR
        add(t0, (np.sin(2 * np.pi * 2200 * xt) * np.exp(-xt * 80) * 0.5).astype(np.float32))
        add(t0 + 0.5, (np.sin(2 * np.pi * 1600 * xt) * np.exp(-xt * 80) * 0.3).astype(np.float32))
    elif kind == "buzz":
        xb = np.arange(int(0.9 * SR)) / SR
        add(t0, (sum(np.sin(2 * np.pi * f * xb) for f in (523.25, 659.25, 783.99)) * np.exp(-xb * 4) * 0.3).astype(np.float32))
    elif kind == "whoosh":
        add(t0, whoosh * 1.2)
    elif kind == "chime":
        for j, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
            add(t0 + j * 0.09, np.sin(2 * np.pi * f * xc) * np.exp(-xc * 3) * 0.3)

# duck music under voice
env = np.abs(voice)
b2, a2 = butter(1, 4 / (SR / 2)); env = lfilter(b2, a2, env)
env = env / (env.max() + 1e-6)
duck = 1 - 0.55 * np.clip(env * 4, 0, 1)
mix = voice * 1.0 + music * 0.16 * duck + sfx * 0.45
fade = np.ones(N, np.float32); fl = int(0.6 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix *= fade
mix /= np.abs(mix).max() + 1e-6
sf.write("mix.wav", (mix * 0.9).astype(np.float32), SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", "-c:a", "aac", "-b:a", "160k", "mix.m4a"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "short_v.mp4", "-i", "mix.m4a", "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest",
                "-map_metadata", "-1", "-movflags", "+faststart", "short.mp4"], check=True)
print("AUDIO_DONE short.mp4")
