import cairo, json, os, subprocess, sys, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import W, H
exec(open("script.py").read())
import scenes as sc
import scenes2 as s2

FPS = 30
LEAD = 0.35  # silence before narration in each segment

def seg_dur(i):
    scn, p, t = S[i]
    if scn == "chapter": return 4.0
    m = json.load(open(f"vo/{i:03d}.wav.json"))
    return round(max(3.0, LEAD + m["dur"] + 0.25), 3)

def ass_time(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def make_ass(i, path):
    hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Poppins SemiBold,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,3,1,2,160,160,62,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if S[i][0] != "chapter":
        m = json.load(open(f"vo/{i:03d}.wav.json"))
        for st, en, txt in m["sents"]:
            words = txt.split()
            nch = max(1, (len(words) + 8) // 9)
            per = len(words) / nch
            chunks = [" ".join(words[int(k * per):int((k + 1) * per)]) for k in range(nch)]
            tot = sum(len(c) for c in chunks); cur = st
            for c in chunks:
                d = (en - st) * len(c) / tot
                ev.append(f"Dialogue: 0,{ass_time(LEAD + cur)},{ass_time(LEAD + cur + d)},Sub,,0,0,0,,{c}")
                cur += d
    open(path, "w").write(hdr + "\n".join(ev) + "\n")

def booknum(i): return sum(1 for j in range(i) if S[j][0] == "book")

def render(i):
    out = f"segs/{i:03d}.mp4"
    if os.path.exists(out): return
    D = seg_dur(i); n = int(round(D * FPS))
    scn, p, t = S[i]
    obj = s2.make(scn, p, D, i, booknum(i))
    ass = f"segs/{i:03d}.ass"; make_ass(i, ass)
    vf = (f"format=yuv420p,eq=contrast=1.06:saturation=0.88,colorbalance=rs=0.03:bs=0.04:rh=0.04:bh=-0.02,noise=alls=5:allf=t,vignette=PI/4.5,"
          f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(0, D - 0.25):.3f}:d=0.25,"
          f"ass={ass}:fontsdir={os.path.expanduser('~/.fonts')}")
    tmp = f"segs/{i:03d}.tmp.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "4M", "-bufsize", "8M",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "60", tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    for f in range(n):
        ctx.save(); ctx.set_source_rgb(0, 0, 0); ctx.paint()
        obj.frame(ctx, f / FPS)
        ctx.restore()
        surf.flush()
        pr.stdin.write(surf.get_data())
    pr.stdin.close(); rc = pr.wait()
    if rc == 0: os.rename(tmp, out)
    else: print("FAIL", i, flush=True)

if __name__ == "__main__":
    os.makedirs("segs", exist_ok=True)
    mode = sys.argv[1]
    if mode == "one":
        t0 = time.time(); render(int(sys.argv[2])); print("t", time.time() - t0)
    else:
        # worker k of n: process indices i % n == k, waiting for narration
        k, n = int(sys.argv[2]), int(sys.argv[3])
        for i in range(len(S)):
            if i % n != k: continue
            while S[i][0] != "chapter" and not os.path.exists(f"vo/{i:03d}.wav.json"):
                time.sleep(5)
            t0 = time.time(); render(i); print(i, round(time.time() - t0, 1), flush=True)
        print("WORKER DONE", flush=True)
