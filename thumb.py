"""Long-video thumbnail 1280x720: a riddle scene from the video + huge 2-line text + a tag.
python3 ENGINE/thumb.py <seconds> "LINE 1" "LINE 2" "TAG"    (run after audio.py)  -> thumb.jpg
Pick <seconds> inside a riddle's question beat (characters/options visible, no card)."""
import cairo, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw as D
t, l1, l2 = sys.argv[1], sys.argv[2], sys.argv[3]
tag = sys.argv[4] if len(sys.argv) > 4 else ""
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", "short.mp4", "-frames:v", "1", "-vf", "scale=1280:720", "thumb_bg.png"], check=True)
bg = cairo.ImageSurface.create_from_png("thumb_bg.png")
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 720); cr = cairo.Context(s)
cr.save(); cr.translate(-120, -100); cr.scale(1.22, 1.22); cr.set_source_surface(bg, 0, 0); cr.paint(); cr.restore()
g = cairo.LinearGradient(0, 0, 760, 0)
g.add_color_stop_rgba(0, 0.07, 0.2, 0.29, 0.92); g.add_color_stop_rgba(0.7, 0.07, 0.2, 0.29, 0.55); g.add_color_stop_rgba(1, 0.07, 0.2, 0.29, 0)
cr.rectangle(0, 0, 760, 720); cr.set_source(g); cr.fill()
def fit(txt, size, maxw):
    w, _ = D.text_size(cr, txt, D.FONT_BIG, size)
    return size * min(1, maxw / w)
s1 = fit(l1, 120, 620); s2 = fit(l2, 150, 640)
D.outlined_text(cr, l1, 350, 250, s1, fill="#FFFFFF", ow=16, shadow=10)
D.outlined_text(cr, l2, 350, 400, s2, fill=D.YEL, ow=18, shadow=12)
if tag:
    D.pill(cr, tag, 350, 545, size=46, bg="#E53935", fg="#FFFFFF", font=D.FONT_BIG)
s.write_to_png("thumb.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "thumb.png", "-q:v", "2", "thumb.jpg"], check=True)
os.remove("thumb_bg.png")
print("THUMB_DONE thumb.jpg")
