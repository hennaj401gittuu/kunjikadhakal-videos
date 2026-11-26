"""Vertical 1080x1920 Shorts/Reels renderer for Midnight Witness.
Run inside a working folder containing script.py (with S list and HOOK = ["LINE 1", "LINE 2"]) and vo/ from tts_all.py.
Usage: python3 ENGINE/render_short.py  -> writes short.mp4 (video+audio)"""
import cairo, json, os, subprocess, sys, math
import numpy as _np
ENG = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ENG)
from gfx import W, H, RED, PAPER, text, ease, font
import scenes2 as s2, stickscene as ss3
ss3.XSQ = 0.5
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
Style: Sub,Poppins Bold,68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,6,2,2,70,70,330,1

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
    out = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH); oc = cairo.Context(out)
    hook = HOOK
    for i, (scn, p, t) in enumerate(S):
        D = durs[i]; obj = s2.make(scn, p, D, i, 0)
        for f in range(int(round(D * FPS))):
            tt = f / FPS; gt = starts[i] + tt
            sc.save(); sc.set_source_rgb(0, 0, 0); sc.paint(); obj.frame(sc, tt + (0.9 if i == 0 else 0)); sc.restore(); scene.flush()
            # FULL-BLEED vertical: scene fills the frame, its top/bottom edges are extended (sky above, ground below)
            full = scn == "stick"
            k = 1.12 if full else 0.74          # stick scenes zoom in (characters are squeezed to the centre); text scenes fit wider
            cy = 1010 if full else 1000          # vertical centre of the scene in the frame
            pz = 1.0 + 0.22 * (1 - ease(gt / 0.45)) if gt < 0.45 else 1.0
            oc.save(); oc.translate(VW / 2, cy); oc.scale(k * pz, k * pz); oc.translate(-W / 2, -H / 2)
            oc.set_source_surface(scene, 0, 0); pat = oc.get_source(); pat.set_extend(cairo.EXTEND_PAD); pat.set_filter(cairo.FILTER_GOOD)
            oc.paint(); oc.restore()
            # replace the stretched edges with one clean averaged colour, blended into the scene
            buf = _np.frombuffer(scene.get_data(), _np.uint8).reshape(H, scene.get_stride() // 4, 4)[:, :W, :3]
            for edge in ("top", "bot"):
                rows = buf[:12] if edge == "top" else buf[-12:]
                bgr = rows.reshape(-1, 3).mean(0) / 255.0; col = (bgr[2] * 0.85, bgr[1] * 0.85, bgr[0] * 0.85)
                ys = cy + (-H / 2 if edge == "top" else H / 2) * k * pz
                if edge == "top":
                    g = cairo.LinearGradient(0, ys, 0, ys + 90); g.add_color_stop_rgba(0, *col, 1); g.add_color_stop_rgba(1, *col, 0)
                    oc.set_source_rgb(*col); oc.rectangle(0, 0, VW, ys); oc.fill(); oc.set_source(g); oc.rectangle(0, ys, VW, 90); oc.fill()
                else:
                    g = cairo.LinearGradient(0, ys - 90, 0, ys); g.add_color_stop_rgba(0, *col, 0); g.add_color_stop_rgba(1, *col, 1)
                    oc.set_source_rgb(*col); oc.rectangle(0, ys, VW, VH - ys); oc.fill(); oc.set_source(g); oc.rectangle(0, ys - 90, VW, 90); oc.fill()
            # soft shade behind the hook (top) and the subtitles (bottom) so text always reads
            g = cairo.LinearGradient(0, 0, 0, 560); g.add_color_stop_rgba(0, 0, 0, 0, 0.55); g.add_color_stop_rgba(1, 0, 0, 0, 0)
            oc.set_source(g); oc.rectangle(0, 0, VW, 560); oc.fill()
            g = cairo.LinearGradient(0, 1300, 0, VH); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.55)
            oc.set_source(g); oc.rectangle(0, 1300, VW, VH - 1300); oc.fill()
            if gt < 0.12:
                oc.set_source_rgba(1, 1, 1, 0.55 * (1 - gt / 0.12)); oc.paint()
            # hook title (stays whole video, pops in first 0.4 s)
            a = 1.0
            sz = [118, 104]
            for k, ln in enumerate(hook[:2]):
                font(oc, "Bebas Neue", sz[k]); tw = oc.text_extents(ln).x_advance
                fs = sz[k] if tw < VW - 120 else sz[k] * (VW - 120) / tw
                font(oc, "Bebas Neue", fs); tw = oc.text_extents(ln).x_advance
                y = 210 + k * 118
                oc.move_to(VW / 2 - tw / 2, y); oc.text_path(ln)
                oc.set_source_rgba(0, 0, 0, a); oc.set_line_width(12); oc.stroke_preserve()
                oc.set_source_rgba(*((0.97, 0.2, 0.22) if k == 0 else (1, 1, 1)), a); oc.fill()
            text(oc, "MIDNIGHT WITNESS", VW / 2, 410, "Inter", 30, (0.85, 0.85, 0.88), 0.8, "c", bold=True, spacing=10)
            # progress bar
            oc.set_source_rgba(0.97, 0.2, 0.22, 0.95); oc.rectangle(0, VH - 10, VW * gt / T, 10); oc.fill()
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
