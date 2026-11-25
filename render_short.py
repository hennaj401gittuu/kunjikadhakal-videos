"""Vertical 1080x1920 Shorts/Reels renderer for Midnight Witness.
Run inside a working folder containing script.py (with S list and HOOK = ["LINE 1", "LINE 2"]) and vo/ from tts_all.py.
Usage: python3 ENGINE/render_short.py  -> writes short.mp4 (video+audio)"""
import cairo, json, os, subprocess, sys, math
ENG = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ENG)
from gfx import W, H, RED, PAPER, text, ease, font
import scenes2 as s2
exec(open("script.py").read())
VW, VH, FPS, LEAD = 1080, 1920, 30, 0.25
FONTS = os.path.expanduser("~/.fonts")

def seg_dur(i):
    m = json.load(open(f"vo/{i:03d}.wav.json"))
    return round(max(2.0, LEAD + m["dur"] + 0.1), 3)

def ass_time(x):
    x = max(0, x); return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"

def make_ass(path, starts):
    hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Poppins Bold,68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,5,2,2,80,80,425,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for i, st0 in enumerate(starts):
        m = json.load(open(f"vo/{i:03d}.wav.json"))
        for st, en, txt in m["sents"]:
            words = txt.split(); nch = max(1, (len(words) + 4) // 5); per = len(words) / nch
            chunks = [" ".join(words[int(k * per):int((k + 1) * per)]) for k in range(nch)]
            tot = sum(len(c) for c in chunks); cur = st
            for c in chunks:
                d = (en - st) * len(c) / tot
                ev.append(f"Dialogue: 0,{ass_time(st0 + LEAD + cur)},{ass_time(st0 + LEAD + cur + d)},Sub,,0,0,0,,{c.upper()}")
                cur += d
    open(path, "w").write(hdr + "\n".join(ev) + "\n")

def main():
    durs = [round(round(seg_dur(i) * FPS) / FPS, 6) for i in range(len(S))]
    starts = [sum(durs[:i]) for i in range(len(S))]
    T = sum(durs)
    make_ass("short.ass", starts)
    vf = (f"format=yuv420p,eq=contrast=1.06:saturation=0.9,noise=alls=4:allf=t,vignette=PI/5,"
          f"ass=short.ass:fontsdir={FONTS}")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-",
           "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p", "short_v.mp4"]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    scene = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); sc = cairo.Context(scene)
    small = cairo.ImageSurface(cairo.FORMAT_ARGB32, 120, 68); smc = cairo.Context(small)
    out = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH); oc = cairo.Context(out)
    hook = HOOK
    for i, (scn, p, t) in enumerate(S):
        D = durs[i]; obj = s2.make(scn, p, D, i, 0)
        for f in range(int(round(D * FPS))):
            tt = f / FPS; gt = starts[i] + tt
            sc.save(); sc.set_source_rgb(0, 0, 0); sc.paint(); obj.frame(sc, tt + (0.9 if i == 0 else 0)); sc.restore(); scene.flush()
            # blurred cover background
            smc.save(); smc.scale(120 / W, 68 / H); smc.set_source_surface(scene, 0, 0); smc.paint(); smc.restore(); small.flush()
            oc.save(); s = VH / 68 * 1.05; oc.translate(VW / 2, VH / 2); oc.scale(s, s); oc.translate(-60, -34)
            oc.set_source_surface(small, 0, 0); oc.get_source().set_filter(cairo.FILTER_BILINEAR); oc.paint(); oc.restore()
            oc.set_source_rgba(0, 0, 0, 0.62); oc.paint()
            # main 16:9 panel, slightly cropped sides for size
            pw = 1400; ph = pw * 9 / 16; py = 545
            oc.save(); oc.rectangle(0, py, VW, ph); oc.clip()
            pz = 1.0 + 0.22 * (1 - ease(gt / 0.45)) if gt < 0.45 else 1.0
            oc.translate(VW / 2, py + ph / 2); oc.scale(pz, pz); oc.translate(-pw / 2, -ph / 2)
            oc.scale(pw / W, ph / H); oc.set_source_surface(scene, 0, 0); oc.paint(); oc.restore()
            if gt < 0.12:
                oc.set_source_rgba(1, 1, 1, 0.55 * (1 - gt / 0.12)); oc.paint()
            oc.set_source_rgba(*RED, 1); oc.rectangle(0, py - 6, VW, 6); oc.fill(); oc.rectangle(0, py + ph, VW, 6); oc.fill()
            # hook title (stays whole video, pops in first 0.4 s)
            a = 1.0
            sz = [118, 104]
            for k, ln in enumerate(hook[:2]):
                font(oc, "Bebas Neue", sz[k]); tw = oc.text_extents(ln).x_advance
                fs = sz[k] if tw < VW - 120 else sz[k] * (VW - 120) / tw
                font(oc, "Bebas Neue", fs); tw = oc.text_extents(ln).x_advance
                y = 290 + k * 118
                oc.move_to(VW / 2 - tw / 2, y); oc.text_path(ln)
                oc.set_source_rgba(0, 0, 0, a); oc.set_line_width(12); oc.stroke_preserve()
                oc.set_source_rgba(*((0.97, 0.2, 0.22) if k == 0 else (1, 1, 1)), a); oc.fill()
            text(oc, "MIDNIGHT WITNESS", VW / 2, 490, "Inter", 30, (0.85, 0.85, 0.88), 0.8, "c", bold=True, spacing=10)
            # progress bar
            oc.set_source_rgba(1, 1, 1, 0.9); oc.rectangle(0, py + ph, VW * gt / T, 6); oc.fill()
            out.flush(); pr.stdin.write(out.get_data())
    pr.stdin.close(); assert pr.wait() == 0
    # audio: narration + light score
    sys.argv = ["audio"]
    import numpy as np, soundfile as sf
    from scipy.signal import resample_poly
    SR = 44100; N = int(T * SR) + 1
    voice = np.zeros(N, np.float32)
    for i in range(len(S)):
        a_, sr = sf.read(f"vo/{i:03d}.wav", dtype="float32"); a_ = resample_poly(a_, 147, 80).astype(np.float32)
        o = int((starts[i] + LEAD) * SR); voice[o:o + len(a_)] += a_[:max(0, N - o)]
    voice /= np.abs(voice).max() + 1e-6
    tt = np.arange(N) / SR
    MOOD = globals().get("MOOD", "dark")
    base = (55.0, 82.41, 110.0, 130.81) if MOOD != "curious" else (65.41, 130.81, 164.81, 196.0)
    mus = sum(np.sin(2 * np.pi * f * tt) for f in base) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * tt))
    if MOOD == "curious":
        pl = np.zeros(N, np.float32)
        for k, s0 in enumerate(np.arange(0, T, 0.29)):
            o = int(s0 * SR); L = min(int(0.5 * SR), N - o)
            if L <= 0: break
            x = np.arange(L) / SR; f = base[1 + k % 3] * 2
            pl[o:o + L] += np.sin(2 * np.pi * f * x) * np.exp(-x * 8)
        mus = mus / (np.abs(mus).max() + 1e-6) + 1.2 * pl
    pulse = np.zeros(N, np.float32)
    for s0 in np.arange(0, T, 0.9):
        o = int(s0 * SR); L = min(int(0.2 * SR), N - o)
        if L <= 0: break
        x = np.arange(L) / SR; pulse[o:o + L] += np.sin(2 * np.pi * 50 * x) * np.exp(-x * 20)
    if MOOD != "curious": mus = mus / np.abs(mus).max() + 0.6 * pulse
    hit = np.zeros(N, np.float32); L = min(int(0.9 * SR), N); x = np.arange(L) / SR
    hit[:L] = (np.sin(2 * np.pi * (60 * np.exp(-x * 2) + 35) * x) * np.exp(-x * 4) + 0.3 * np.random.default_rng(1).standard_normal(L) * np.exp(-x * 18)).astype(np.float32)
    mix = voice * 0.9 + 0.12 * mus / (np.abs(mus).max() + 1e-6) + 0.35 * hit
    mix /= np.abs(mix).max() + 1e-6
    sf.write("short_a.wav", np.stack([mix, mix], 1).astype(np.float32), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "short_v.mp4", "-i", "short_a.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", "short.mp4"], check=True)
    print("SHORT", round(T, 1))

if __name__ == "__main__":
    main()
