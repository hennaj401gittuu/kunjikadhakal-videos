"""Render a Build to Survive Short. Run in a folder holding script.py and vo/ (from tts.py).
python3 ENGINE/render.py [--frames 0,5.5,30]   -> short_v.mp4 + events.json   (with --frames: PNG stills only)
"""
import cairo, json, math, os, subprocess, sys, re
ENG = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ENG)
import iso
from iso import *  # noqa  (script uses the helpers)
import draw as D

exec(open("script.py").read())
LONG = globals().get("FORMAT", "short") == "long"
D.setup(LONG)
CAPTIONS = globals().get("CAPTIONS", not LONG)
FPS, LEAD, TAIL, END_HOLD = 30, 0.2, 0.25, 1.8
OVER = ("label", "measure", "counter", "qbar", "option", "timer", "reveal", "card", "score")
SKY = globals().get("SKY", "#2F8FCB")
KEYWORDS = [k.lower() for k in globals().get("KEYWORDS", [])]


def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def back(x):
    x = min(1, max(0, x)); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


# ---------- timeline ----------
meta = [json.load(open(f"vo/{i:03d}.json")) for i in range(len(B))]
starts, durs = [], []
t = 0.0
for i, b in enumerate(B):
    d = LEAD + meta[i]["dur"] + TAIL + b.get("hold", 0)
    if i == len(B) - 1:
        d += END_HOLD
    starts.append(t); durs.append(d); t += d
T = t
NF = int(math.ceil(T * FPS))

life = {}      # id -> list of [obj, t_on, t_off, order]
cams = []      # (t_start, kind, data)
events = []
order = 0
for i, b in enumerate(B):
    t0 = starts[i]
    k = 0
    if b.get("cut"):
        for vs in life.values():
            for v in vs:
                if v[2] > t0:
                    v[2] = t0; v.append("hard")
    for o in b["objs"]:
        if o["kind"] == "remove":
            for rid in o["ids"]:
                for v in life.get(rid, []):
                    if v[2] > t0:
                        v[2] = t0
            continue
        if o["kind"] in ("focus", "overview"):
            cams.append((i, o)); continue
        late = 0.35 if o["kind"] in ("label", "measure", "counter", "reveal") else 0
        ton = t0 + 0.05 + k * 0.14 + late
        instant = False
        if (i == 0 or b.get("cut")) and o["kind"] not in ("label", "measure", "counter", "reveal", "timer"):
            ton = t0; instant = True  # a new scene is complete at once (beat 0 = the cover)
        if o["kind"] == "timer":
            ton = t0 + LEAD + meta[i]["dur"] + 0.1
            for sct in range(int(o["seconds"])):
                events.append((ton + sct, "tick"))
            events.append((ton + o["seconds"], "buzz"))
        k += 1
        for v in life.get(o["id"], []):
            if v[2] > ton:
                v[2] = ton
        order += 1
        life.setdefault(o["id"], []).append([o, ton, 1e9, order, "inst" if instant else ""])
        if ton > 0.05 and not instant:
            if o["kind"] in ("label", "measure", "counter", "reveal", "option"):
                events.append((ton, "ding"))
            elif o["kind"] not in ("fx", "sun", "clouds", "timer", "qbar", "score"):
                events.append((ton, "pop"))
        if o["kind"] == "card":
            events.append((ton, "whoosh"))
fin = starts[-1] + 0.15
events.append((fin, "chime"))


def active(tt):
    out = []
    for oid, vs in life.items():
        for v in vs:
            o, ton, toff, od = v[0], v[1], v[2], v[3]
            hard = "hard" in v[4:]
            inst = "inst" in v[4:]
            if ton <= tt < toff + (0 if hard else 0.3):
                a_in = 1.0 if (ton == 0.0 or inst) else ease((tt - ton) / 0.4)
                a_out = 1 - ease((tt - toff) / 0.3) if tt >= toff else 1
                out.append((o, ton if not inst else -1.0, min(a_in, a_out), od))
    return out


# ---------- cinematography: one planned shot per beat ----------
# A shot = (world point, zoom, yaw, elev) at its start and end; the camera moves start->end through the beat.
# Auto rules: close-ups on whatever is new, alternating angles, cuts with a zoom punch, orbit reveals.
WORLD_SKIP = ("label", "fx", "sun", "clouds", "counter", "measure", "qbar", "option", "timer", "reveal", "card", "score")


def pts_of(objs, scene):
    out = []
    for o in objs:
        if o["kind"] in WORLD_SKIP:
            continue
        out += D.obj_points(o, scene)
    return out


def frame_pts(pts, yaw, elev, fill_w=None, fill_h=None):
    """World centre + zoom that frames these points under this view."""
    fill_w = fill_w or (1500 if LONG else 1000)
    fill_h = fill_h or (720 if LONG else 900)
    if not pts:
        return (5, 5, 0), 1.0
    cam = D.Cam(yaw=yaw, elev=elev)
    sp = [cam.base(*p) for p in pts]
    xs = [p[0] for p in sp]; ys = [p[1] for p in sp]
    bw, bh = max(xs) - min(xs) + 60, max(ys) - min(ys) + 60
    z = max(0.35, min(4.0, min(fill_w / bw, fill_h / bh)))
    cx = (min(xs) + max(xs)) / 2; cy = (min(ys) + max(ys)) / 2
    # convert screen-base centre back to a world point on the plane through the points' mean height
    zm = sum(p[2] for p in pts) / len(pts)
    u = cx / cam.S; vv = (cy + zm * cam.S * cam.cf) / (cam.S * cam.sf)
    wx = u * cam.ct + vv * cam.st; wy = -u * cam.st + vv * cam.ct
    return (wx, wy, zm), z


# (yaw, elev) presets. yaw ~10 = looking straight at the left (+y) cut face; ~80 = at the right (+x) face.
SIDE_Y, SIDE_X = (11, 7), (79, 7)          # side cross-section (stepwell-style underground view)
EYE = [(30, 11), (60, 13)]                 # eye level, close to the character
TOP = (45, 62)                             # high, almost top-down
ANG = [(38, 30), (58, 44), (30, 18), (52, 24), TOP]   # rotating variety for other beats


def pick_angle(i, new, scene):
    """Choose the view that shows this beat's new parts best."""
    under = [o for o in new if o["kind"] == "patch" or min((p[2] for p in D.obj_points(o, scene)), default=0) < -0.2]
    if under:
        faces = [o.get("face") for o in under if o["kind"] == "patch"]
        return SIDE_X if faces and all(f == "x" for f in faces) else SIDE_Y
    if any(o["kind"] in ("figure", "critter") for o in new):
        return EYE[i % 2]
    return ANG[i % len(ANG)]
def lerp(a, b, e):
    return a + (b - a) * e


def shot_at(sh, e):
    p = tuple(lerp(sh["p0"][k], sh["p1"][k], e) for k in range(3))
    return p, lerp(sh["z0"], sh["z1"], e), lerp(sh["y0"], sh["y1"], e), lerp(sh["e0"], sh["e1"], e)


shots = []
prev_kind = None
for i, b in enumerate(B):
    tmid = starts[i] + 0.6
    objs = [o for o, ton, a, od in active(tmid + 0.5)]
    scene = {o["id"]: o for o in objs}
    new = [o for o in b["objs"] if o.get("kind") not in WORLD_SKIP + ("remove", "focus", "overview")]
    camcmd = [c for (bi, c) in cams if bi == i]
    yaw, elev = pick_angle(i, new, scene)
    allpts = pts_of(objs, scene)
    last = i == len(B) - 1
    kinds = [o.get("kind") for o in b["objs"]]
    rev = [o for o in b["objs"] if o.get("kind") == "reveal"]
    if "card" in kinds and shots:
        e = shots[-1]; p_, z_, y_, el_ = shot_at(e, 1.0)
        shot = dict(p0=p_, p1=p_, z0=z_, z1=z_, y0=y_, y1=y_, e0=el_, e1=el_, cut=True, kind="card")
    elif b.get("cut") and not rev:
        # new riddle scene: a steady establishing view where every option is visible
        # frame the riddle's objects + option markers tightly (not the whole ground block)
        core = [o for o in objs if o["kind"] not in ("ground",) + WORLD_SKIP]
        opt_pts = [(o["x"], o["y"], o["z"]) for o in objs if o["kind"] == "option"]
        c_all, z_all = frame_pts(allpts, 40, 32)
        c, z = frame_pts(pts_of(core, scene) + opt_pts, 40, 32, 1380, 700)
        z = min(z, z_all * 2.6)
        shot = dict(p0=c, p1=c, z0=z * 1.06, z1=z * 1.0, y0=37, y1=43, e0=30, e1=32, cut=True, kind="riddle")
    elif "timer" in kinds and shots:
        e = shots[-1]; p_, z_, y_, el_ = shot_at(e, 1.0)
        shot = dict(p0=p_, p1=p_, z0=z_, z1=z_ * 1.07, y0=y_, y1=y_ + 2, e0=el_, e1=el_, cut=False, kind="timer")
    elif rev:
        r = rev[-1]
        c, z = frame_pts(allpts, 40, 26)
        p = (r["x"], r["y"], r["z"])
        shot = dict(p0=p, p1=p, z0=z * 1.55, z1=z * 1.7, y0=38, y1=44, e0=24, e1=26, cut=True, kind="close")
    elif last or (camcmd and camcmd[-1]["kind"] == "overview"):
        zm = (camcmd[-1].get("zoom") if camcmd else None) or 1.0
        c, z = frame_pts(allpts, 45, 34)
        ys, ye = (30, 60) if i % 2 else (60, 30)
        shot = dict(p0=c, p1=c, z0=z * zm * 1.12, z1=z * zm * 0.92, y0=ys, y1=ye, e0=30, e1=40, cut=False, kind="wide")
    elif camcmd and camcmd[-1]["kind"] == "focus":
        f = camcmd[-1]
        elev = min(elev, 22)  # details read best from a low angle
        c, z = frame_pts(allpts, yaw, elev)
        p = (f["x"], f["y"], f["z"])
        shot = dict(p0=p, p1=p, z0=z * f["zoom"], z1=z * f["zoom"] * 1.1, y0=yaw - 4, y1=yaw + 4, e0=elev, e1=elev + 3, cut=True, kind="close")
    elif i == 0:
        figs = [o for o in objs if o["kind"] == "figure"]
        c_all, z_all = frame_pts(allpts, 40, 30)
        if figs:
            c, z = frame_pts(D.obj_points(figs[0], scene), 34, 12)
            z = min(z * 0.5, z_all * 2.4)
        else:
            c, z = c_all, z_all * 1.3
        shot = dict(p0=c, p1=c_all, z0=z, z1=z_all * 1.05, y0=34, y1=44, e0=12, e1=30, cut=True, kind="hook")
    elif new:
        npts = pts_of(new, scene)
        c_all, z_all = frame_pts(allpts, yaw, elev)
        c, z = frame_pts(npts, yaw, elev, 1100 if LONG else 760, 560 if LONG else 700)
        z = min(z, z_all * 2.3)
        z = max(z, z_all * 1.25)
        pull = 0.82 if i % 2 else 0.9
        dy = 2 if elev < 10 else 5
        shot = dict(p0=c, p1=c, z0=z, z1=z * pull, y0=yaw - dy, y1=yaw + dy, e0=elev, e1=elev + 2,
                    cut=(prev_kind in ("close", "hook")), kind="close")
    else:
        c, z = frame_pts(allpts, yaw, elev)
        shot = dict(p0=c, p1=c, z0=z * 1.05, z1=z * 1.22, y0=yaw + 4, y1=yaw - 4, e0=elev, e1=elev, cut=False, kind="medium")
    shots.append(shot)
    prev_kind = shot["kind"]


def camera(tt):
    i = max(k for k in range(len(B)) if starts[k] <= tt + 1e-9)
    sh = shots[i]
    local = tt - starts[i]
    e = ease(local / max(0.5, durs[i])) if sh["kind"] != "hook" else ease(local / max(0.5, durs[i]))
    p, z, yw, el = shot_at(sh, e)
    punch = 1.0
    if i > 0 and not sh["cut"] and local < 0.55:
        # quick eased move from where the previous shot ended
        pp, pz, py, pe = shot_at(shots[i - 1], 1.0)
        k = ease(local / 0.55)
        p = tuple(lerp(pp[j], p[j], k) for j in range(3)); z = lerp(pz, z, k); yw = lerp(py, yw, k); el = lerp(pe, el, k)
    elif sh["cut"] and i > 0 and local < 0.25:
        punch = 1 + 0.07 * (1 - ease(local / 0.25))
    cam = D.Cam(yaw=yw, elev=el, zoom=z * punch, ox=D.VW / 2, oy=(D.VH * 0.56 if LONG else 930))
    bx, by = cam.base(*p)
    cam.cx, cam.cy = bx, by
    return cam


# ---------- captions ----------
label_words = set()
for b in B:
    for o in b["objs"]:
        if o.get("kind") == "label":
            for w in o["text"].lower().split():
                if len(w) > 3:
                    label_words.add(w)
HOT = set(KEYWORDS) | label_words
chunks = []
for i, m in enumerate(meta):
    for st, en, txt in m["sents"]:
        words = txt.split()
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 3 or re.search(r"[,.!?;:]$", w):
                groups.append(cur); cur = []
        if cur:
            groups.append(cur)
        tot = sum(len(" ".join(g)) for g in groups) or 1
        c0 = st
        for g in groups:
            d = (en - st) * len(" ".join(g)) / tot
            chunks.append((starts[i] + LEAD + c0, starts[i] + LEAD + c0 + d, g))
            c0 += d


def is_hot(w):
    w2 = re.sub(r"[^a-z0-9°%']", "", w.lower())
    return w2 in HOT or any(w2 == k or (len(k) > 4 and w2.startswith(k)) for k in HOT) or bool(re.search(r"\d", w2))


def draw_caption(cr, tt):
    cur = [c for c in chunks if c[0] <= tt < c[1] + 0.05]
    if not cur:
        return
    c0, c1, g = cur[-1]
    pop = 1 + 0.12 * (1 - ease((tt - c0) / 0.12))
    words = [re.sub(r"[,;:]$", "", w).upper() for w in g]
    size = 86
    cr.select_font_face(D.FONT_BIG); cr.set_font_size(size)
    space = cr.text_extents(" ").x_advance
    ws = [cr.text_extents(w).x_advance for w in words]
    total = sum(ws) + space * (len(ws) - 1)
    if total > 960:
        size *= 960 / total; ws = [x * 960 / total for x in ws]; space *= 960 / total; total = 960
    cr.save()
    cr.translate(540, 1430); cr.scale(pop, pop)
    x = -total / 2
    for w, wd, raw in zip(words, ws, g):
        D.outlined_text(cr, w, x + wd / 2, 0, size, fill=(D.YEL if is_hot(raw) else "#FFFFFF"), ow=14, shadow=7)
        x += wd + space
    cr.restore()


def draw_hook(cr, tt):
    if "TITLE" not in globals():
        return
    end = starts[1] if len(B) > 1 else 3
    if tt > end + 0.3:
        return
    a = 1 - ease((tt - end) / 0.3) if tt > end else 1
    pop = 1  # title fully visible from frame 0 (cover)
    cr.save(); cr.translate(540, 0)
    D.pill(cr, "BUILD TO SURVIVE", 0, 190, size=30, bg="#FFFFFF", fg="#1B5E86", alpha=a)
    cr.translate(0, 300); cr.scale(pop, pop)
    l1, l2 = TITLE[0], TITLE[1] if len(TITLE) > 1 else ""
    D.outlined_text(cr, l1, 0, 0, 84, fill="#FFFFFF", ow=14, shadow=8, alpha=a)
    if l2:
        sz = 112
        cr.select_font_face(D.FONT_BIG); cr.set_font_size(sz)
        wd = cr.text_extents(l2).x_advance
        if wd > 980:
            sz *= 980 / wd
        D.outlined_text(cr, l2, 0, 118, sz, fill=D.YEL, ow=16, shadow=9, alpha=a)
    cr.restore()


def frame(cr, tt):
    g = cairo.LinearGradient(0, 0, 0, D.VH)
    g.add_color_stop_rgb(0, *D.shade(SKY, 0.85)); g.add_color_stop_rgb(1, *D.shade(SKY, 1.25))
    cr.set_source(g); cr.paint()
    act = active(tt)
    cam = camera(tt)
    D.YAWW[0], D.YAWW[1] = cam.st, cam.ct
    scene = {o["id"]: o for o, *_ in act}
    bg = [x for x in act if x[0]["kind"] in ("sun", "clouds")]
    for o, ton, a, od in bg:
        if o["kind"] == "sun":
            D.draw_sun(cr, tt, a)
        else:
            D.draw_clouds(cr, tt, a, o.get("n", 3))
    world = [x for x in act if x[0]["kind"] not in ("sun", "clouds", "fx") + OVER]
    world.sort(key=lambda x: (D.depth_key(x[0], scene), x[3]))
    for o, ton, a, od in world:
        prog = (tt - ton) / 0.45
        if prog < 1 and ton > 0 and o["kind"] not in ("ground", "arrow", "patch", "water"):
            anc = D.anchor(o, cam)
            if anc:
                s = 0.55 + 0.45 * back(prog)
                cr.save(); cr.translate(anc[0], anc[1] - 50 * (1 - ease(prog))); cr.scale(s, s); cr.translate(-anc[0], -anc[1])
                D.draw_obj(cr, cam, o, scene, tt, a, prog)
                cr.restore(); continue
        D.draw_obj(cr, cam, o, scene, tt, a, (tt - ton) / 1.0)
    for o, ton, a, od in act:
        if o["kind"] == "fx":
            D.draw_fx(cr, o["fx"], tt, a)
    for o, ton, a, od in act:
        if o["kind"] in ("label", "measure", "counter", "option", "reveal"):
            D.draw_obj(cr, cam, o, scene, tt, a, (tt - ton) / 0.6)
    for o, ton, a, od in act:
        if o["kind"] == "qbar":
            D.draw_qbar(cr, o["text"], a, (tt - ton) / 0.6 if ton >= 0 else 1)
        elif o["kind"] == "score":
            D.draw_score(cr, o["text"], a)
        elif o["kind"] == "timer":
            D.draw_timer(cr, o, tt - ton, a)
    for o, ton, a, od in act:
        if o["kind"] == "card":
            D.draw_card(cr, o, a, (tt - ton) / 0.6 if ton >= 0 else 1)
    if not LONG:
        draw_hook(cr, tt)
    if CAPTIONS:
        draw_caption(cr, tt)


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, D.VW, D.VH)
    cr = cairo.Context(surf)
    if "--frames" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        for x in ts:
            frame(cr, min(x, T - 0.01)); surf.write_to_png(f"frame_{x:05.1f}.png")
        print("T", round(T, 2), "beats", [round(s, 2) for s in starts]); return
    part, nparts = 0, 1
    if "--part" in sys.argv:
        part, nparts = [int(x) for x in sys.argv[sys.argv.index("--part") + 1].split("/")]
    elif "--workers" in sys.argv or LONG:
        nw = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else min(4, os.cpu_count() or 2)
        if nw > 1:
            procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), "--part", f"{k}/{nw}"]) for k in range(nw)]
            if any(p_.wait() != 0 for p_ in procs):
                sys.exit("RENDER_FAIL")
            open("parts.txt", "w").write("".join(f"file 'part_{k}.mp4'\n" for k in range(nw)))
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "parts.txt", "-c", "copy", "short_v.tmp.mp4"], check=True)
            os.replace("short_v.tmp.mp4", "short_v.mp4")
            for k in range(nw):
                os.remove(f"part_{k}.mp4")
            json.dump({"T": T, "starts": starts, "lead": LEAD, "events": sorted(events)}, open("events.json", "w"))
            print("RENDER_DONE", round(T, 2), "s"); return
    f0, f1 = NF * part // nparts, NF * (part + 1) // nparts
    outp = "short_v.tmp.mp4" if nparts == 1 else f"part_{part}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{D.VW}x{D.VH}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20" if not LONG else "21", "-pix_fmt", "yuv420p", outp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(f0, f1):
        frame(cr, n / FPS)
        surf.flush()
        pr.stdin.write(bytes(surf.get_data()))
    pr.stdin.close(); pr.wait()
    if nparts > 1:
        if pr.returncode != 0:
            sys.exit(1)
        return
    if pr.returncode == 0:
        os.replace("short_v.tmp.mp4", "short_v.mp4")
    json.dump({"T": T, "starts": starts, "lead": LEAD, "events": sorted(events)}, open("events.json", "w"))
    print("RENDER_DONE", round(T, 2), "s")


if __name__ == "__main__":
    main()
