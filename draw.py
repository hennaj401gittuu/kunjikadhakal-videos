"""Drawing for Build to Survive (pycairo). Used by render.py and cover.py."""
import cairo, math, random
from iso import C, hexrgb, shade, GROUNDS

VW, VH = 1080, 1920
U = 100.0  # px per world unit at zoom 1
FONT_BIG = "Archivo Black"
FONT_UI = "Poppins"
YEL = "#F5B83D"
INK = "#1E2A33"
NAVY = "#12324A"


def rgb(c):
    return hexrgb(c) if isinstance(c, str) else c


class Cam:
    def __init__(self, cx=0, cy=0, zoom=1.0, ox=540, oy=930):
        self.cx, self.cy, self.zoom, self.ox, self.oy = cx, cy, zoom, ox, oy

    def base(self, x, y, z):
        return ((x - y) * C * U, (x + y) * 0.5 * U - z * U)

    def P(self, x, y, z):
        bx, by = self.base(x, y, z)
        return ((bx - self.cx) * self.zoom + self.ox, (by - self.cy) * self.zoom + self.oy)


def fillpoly(cr, pts, col, alpha=1.0, outline=None, lw=2):
    if not pts:
        return
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.close_path()
    r, g, b = rgb(col)
    cr.set_source_rgba(r, g, b, alpha)
    if outline:
        cr.fill_preserve()
        r, g, b = rgb(outline)
        cr.set_source_rgba(r, g, b, alpha * 0.6)
        cr.set_line_width(lw)
        cr.stroke()
    else:
        cr.fill()


def circle(cr, x, y, r, col, alpha=1.0):
    cr.arc(x, y, max(0.1, r), 0, 2 * math.pi)
    cr.set_source_rgba(*rgb(col), alpha)
    cr.fill()


def ellipse(cr, x, y, rx, ry, col, alpha=1.0):
    cr.save()
    cr.translate(x, y)
    cr.scale(max(rx, 0.1), max(ry, 0.1))
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.restore()
    cr.set_source_rgba(*rgb(col), alpha)
    cr.fill()


def stroke_path(cr, pts, col, w, alpha=1.0, cap=cairo.LINE_CAP_ROUND, dash=None, offset=0):
    if len(pts) < 2:
        return
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.set_source_rgba(*rgb(col), alpha)
    cr.set_line_width(max(1, w))
    cr.set_line_cap(cap)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    if dash:
        cr.set_dash(dash, offset)
    cr.stroke()
    cr.set_dash([])


def text_size(cr, s, font, size, bold=False):
    cr.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size)
    e = cr.text_extents(s)
    return e.x_advance, e


def outlined_text(cr, s, cx, cy, size, fill="#FFFFFF", font=FONT_BIG, outline=NAVY, ow=10, shadow=6, alpha=1.0, bold=False):
    """Centered text with thick outline + drop shadow."""
    cr.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size)
    e = cr.text_extents(s)
    x = cx - e.x_advance / 2
    y = cy + size * 0.36
    if shadow:
        cr.move_to(x, y + shadow)
        cr.text_path(s)
        cr.set_source_rgba(*rgb(outline), 0.55 * alpha)
        cr.set_line_width(ow)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.stroke_preserve()
        cr.fill()
    cr.move_to(x, y)
    cr.text_path(s)
    cr.set_source_rgba(*rgb(outline), alpha)
    cr.set_line_width(ow)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.stroke_preserve()
    cr.set_source_rgba(*rgb(fill), alpha)
    cr.fill()
    return e.x_advance


def pill(cr, s, cx, cy, size=34, bg=YEL, fg=INK, font=FONT_UI, alpha=1.0, padx=None, pady=None):
    w, e = text_size(cr, s, font, size, bold=True)
    padx = padx if padx is not None else size * 0.7
    pady = pady if pady is not None else size * 0.42
    bw, bh = w + 2 * padx, size + 2 * pady
    x0, y0 = cx - bw / 2, cy - bh / 2
    r = bh / 2
    cr.new_sub_path()
    cr.arc(x0 + r, y0 + r, r, math.pi / 2, 3 * math.pi / 2)
    cr.arc(x0 + bw - r, y0 + r, r, -math.pi / 2, math.pi / 2)
    cr.close_path()
    cr.set_source_rgba(0, 0, 0, 0.22 * alpha)
    cr.save(); cr.translate(0, 5); cr.fill_preserve(); cr.restore()
    cr.new_path()
    cr.new_sub_path()
    cr.arc(x0 + r, y0 + r, r, math.pi / 2, 3 * math.pi / 2)
    cr.arc(x0 + bw - r, y0 + r, r, -math.pi / 2, math.pi / 2)
    cr.close_path()
    cr.set_source_rgba(*rgb(bg), alpha)
    cr.fill()
    cr.move_to(cx - w / 2, cy + size * 0.36)
    cr.set_source_rgba(*rgb(fg), alpha)
    cr.show_text(s)
    return bw, bh


# ---------------- world objects ----------------

def obj_points(o, scene):
    """3D points used for camera framing."""
    k = o["kind"]
    if k in ("ground", "box", "room", "water", "roof"):
        x, y, z, w, d = o["x"], o["y"], o.get("z", 0), o["w"], o["d"]
        h = o.get("h", 0)
        zb = -o["depth"] * 0.55 if k == "ground" else z
        return [(x, y, zb), (x + w, y, zb), (x, y + d, zb), (x + w, y + d, zb), (x, y, z + h), (x + w, y + d, z + h), (x + w, y, z + h), (x, y + d, z + h)]
    if k in ("cyl", "cone"):
        x, y, z, r, h = o["x"], o["y"], o["z"], o["r"], o["h"]
        return [(x - r, y - r, z), (x + r, y + r, z), (x, y, z + h), (x + r, y - r, z), (x - r, y + r, z)]
    if k in ("poly", "line3", "arrow"):
        return list(o["pts"])
    if k == "tree":
        s = o["size"]
        hh = {"bamboo": 4.5, "palm": 3.6, "pine": 3.2, "fig": 4.0, "bush": 1.0}.get(o["tkind"], 2.8) * s
        return [(o["x"], o["y"], o["z"]), (o["x"], o["y"], o["z"] + hh)]
    if k == "figure":
        return [(o["x"], o["y"], o["z"]), (o["x"], o["y"], o["z"] + 1.8 * o["size"])]
    if k in ("critter", "rock"):
        sp = o.get("spread", 0) if o.get("n", 1) > 1 else 0
        return [(o["x"] - sp, o["y"] - sp, o["z"]), (o["x"] + sp, o["y"] + sp, o["z"] + 0.4 * o["size"])]
    if k == "patch":
        g = scene.get(o.get("g") or "ground")
        return []
    if k == "measure":
        return [(o["x"], o["y"], o["z0"]), (o["x"], o["y"], o["z1"])]
    return []


def depth_key(o, scene):
    k = o["kind"]
    if "zi" in o:
        return o["zi"]
    if k == "ground":
        return -1e6
    if k == "patch":
        return -1e5
    if k in ("sun", "clouds"):
        return -1e7
    if k in ("label", "measure", "fx", "counter"):
        return 1e7
    if k in ("box", "room", "water", "roof"):
        z = o.get("z", 0)
        base = o["x"] + o["w"] * 0.5 + o["y"] + o["d"] * 0.5
        if k == "water":
            return base - 0.5 + z * 0.01
        if k == "roof":
            return base + 0.02 + z * 0.01
        if k == "room":
            return base - 0.3
        return base + z * 0.01
    if k in ("cyl", "cone", "tree", "figure", "critter", "rock"):
        return o["x"] + o["y"] + o.get("z", 0) * 0.01 + 0.01
    if k in ("poly", "line3", "arrow"):
        pts = o["pts"]
        mx = max(p[0] + p[1] for p in pts)
        mn = min(p[0] + p[1] for p in pts)
        return (mx + mn) / 2 + (0.5 if k == "arrow" else 0)
    return 0


def draw_box(cr, cam, x, y, z, w, d, h, color, top=None, alpha=1.0, outline=True):
    P = cam.P
    top = top or shade(color, 1.18)
    oc = shade(color, 0.55) if outline else None
    # left face (+y)
    fillpoly(cr, [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)], shade(color, 0.95), alpha)
    # right face (+x)
    fillpoly(cr, [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)], shade(color, 0.76), alpha)
    fillpoly(cr, [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)], top, alpha)
    if outline and h > 0:
        stroke_path(cr, [P(x + w, y + d, z), P(x + w, y + d, z + h)], shade(color, 0.6), 1.5 * cam.zoom, alpha * 0.5)


def draw_ground(cr, cam, o, t, alpha):
    P = cam.P
    x, y, w, d = o["x"], o["y"], o["w"], o["d"]
    topc, strata = GROUNDS.get(o["style"], GROUNDS["grass"])
    depth = o["depth"]
    z = 0.0
    bands = []
    for th, col in strata:
        if z <= -depth:
            break
        z1 = max(-depth, z - th)
        bands.append((z, z1, col))
        z = z1
    if z > -depth:
        bands.append((z, -depth, strata[-1][1]))
    # shadow
    ellipse_pts = P(x + w, y + d, -depth)
    for z0, z1, col in bands:
        fillpoly(cr, [P(x, y + d, z0), P(x + w, y + d, z0), P(x + w, y + d, z1), P(x, y + d, z1)], shade(col, 1.0), alpha)
        fillpoly(cr, [P(x + w, y, z0), P(x + w, y + d, z0), P(x + w, y + d, z1), P(x + w, y, z1)], shade(col, 0.8), alpha)
    fillpoly(cr, [P(x, y, 0), P(x + w, y, 0), P(x + w, y + d, 0), P(x, y + d, 0)], topc, alpha)
    # soft texture specks on top
    rnd = random.Random(7)
    for i in range(int(w * d * 1.2)):
        px, py = x + rnd.random() * w, y + rnd.random() * d
        sx, sy = P(px, py, 0)
        ellipse(cr, sx, sy, 7 * cam.zoom, 3 * cam.zoom, shade(topc, 0.9), alpha * 0.5)
    # front edge highlight
    stroke_path(cr, [P(x, y + d, 0), P(x + w, y + d, 0), P(x + w, y, 0)], shade(topc, 1.25), 3 * cam.zoom, alpha * 0.6)


def draw_patch(cr, cam, o, scene, t, alpha):
    g = scene.get(o.get("g") or "ground")
    if not g:
        return
    P = cam.P
    a, b, z0, z1 = o["a"], o["b"], o["z0"], o["z1"]
    if o["face"] == "y":
        Y = g["y"] + g["d"] + 0.001
        pts = [P(a, Y, z0), P(b, Y, z0), P(b, Y, z1), P(a, Y, z1)]
        f = 1.0
    else:
        X = g["x"] + g["w"] + 0.001
        pts = [P(X, a, z0), P(X, b, z0), P(X, b, z1), P(X, a, z1)]
        f = 0.82
    fillpoly(cr, pts, shade(o["color"], f), alpha)
    if o["color"].upper() in ("#3FA7E0", "#4FC3F7", "#2E86C1") or o.get("wet"):
        # shimmer line on water patches
        k = (t * 0.6) % 1
        hp = [((pts[0][0] * (1 - s) + pts[1][0] * s), (pts[3][1] * 0.75 + pts[0][1] * 0.25) + 0) for s in (0.05, 0.95)]
        mid = [(pts[3][0] * (1 - s) + pts[2][0] * s, pts[3][1] * (1 - s) + pts[2][1] * s + 6 * cam.zoom) for s in (0.05, 0.95)]
        stroke_path(cr, mid, "#9ED8F5", 4 * cam.zoom, alpha * 0.9)


def draw_room(cr, cam, o, alpha):
    x, y, z, w, d, h, th = o["x"], o["y"], o["z"], o["w"], o["d"], o["h"], o["thick"]
    draw_box(cr, cam, x, y, z, w, d, th, o["floor"], alpha=alpha)
    draw_box(cr, cam, x, y, z, th, d, h, o["wall"], alpha=alpha)
    draw_box(cr, cam, x, y, z, w, th, h, o["wall"], alpha=alpha)


def draw_roof(cr, cam, o, alpha):
    P = cam.P
    ov = o["over"]
    x0, y0, x1, y1 = o["x"] - ov, o["y"] - ov, o["x"] + o["w"] + ov, o["y"] + o["d"] + ov
    z, h, col = o["z"], o["h"], o["color"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    st = o["style"]
    if st == "flat":
        draw_box(cr, cam, x0, y0, z, x1 - x0, y1 - y0, h, col, alpha=alpha)
        return
    if st == "pyramid":
        A = P(cx, cy, z + h)
        fillpoly(cr, [P(x0, y0, z), P(x1, y0, z), A], shade(col, 1.1), alpha)
        fillpoly(cr, [P(x0, y0, z), P(x0, y1, z), A], shade(col, 1.05), alpha)
        fillpoly(cr, [P(x1, y0, z), P(x1, y1, z), A], shade(col, 0.78), alpha)
        fillpoly(cr, [P(x0, y1, z), P(x1, y1, z), A], shade(col, 0.98), alpha)
        return
    if st == "gable_x":  # ridge along x
        fillpoly(cr, [P(x0, y0, z), P(x1, y0, z), P(x1, cy, z + h), P(x0, cy, z + h)], shade(col, 1.12), alpha)
        fillpoly(cr, [P(x0, y1, z), P(x1, y1, z), P(x1, cy, z + h), P(x0, cy, z + h)], shade(col, 0.96), alpha)
        fillpoly(cr, [P(x1, y0, z), P(x1, y1, z), P(x1, cy, z + h)], shade(col, 0.74), alpha)
        return
    # gable_y: ridge along y
    fillpoly(cr, [P(x0, y0, z), P(x0, y1, z), P(cx, y1, z + h), P(cx, y0, z + h)], shade(col, 1.12), alpha)
    fillpoly(cr, [P(x1, y0, z), P(x1, y1, z), P(cx, y1, z + h), P(cx, y0, z + h)], shade(col, 0.8), alpha)
    fillpoly(cr, [P(x0, y1, z), P(x1, y1, z), P(cx, y1, z + h)], shade(col, 0.98), alpha)


def draw_cyl(cr, cam, o, alpha, cone=False):
    x, y, z, r, h = o["x"], o["y"], o["z"], o["r"], o["h"]
    bx, by = cam.P(x, y, z)
    tx, ty = cam.P(x, y, z + h)
    rx, ry = r * 1.2247 * U * cam.zoom, r * 0.7071 * U * cam.zoom
    col = o["color"]
    if cone:
        g = cairo.LinearGradient(bx - rx, 0, bx + rx, 0)
        g.add_color_stop_rgba(0, *shade(col, 1.12), alpha)
        g.add_color_stop_rgba(0.45, *shade(col, 0.98), alpha)
        g.add_color_stop_rgba(1, *shade(col, 0.7), alpha)
        cr.save(); cr.translate(bx, by); cr.scale(rx, ry); cr.arc(0, 0, 1, 0, math.pi); cr.restore()
        cr.line_to(tx, ty)
        cr.close_path()
        cr.set_source(g); cr.fill()
        return
    g = cairo.LinearGradient(bx - rx, 0, bx + rx, 0)
    g.add_color_stop_rgba(0, *shade(col, 1.08), alpha)
    g.add_color_stop_rgba(0.5, *shade(col, 0.95), alpha)
    g.add_color_stop_rgba(1, *shade(col, 0.68), alpha)
    cr.move_to(bx - rx, by)
    cr.save(); cr.translate(bx, by); cr.scale(rx, ry); cr.arc_negative(0, 0, 1, math.pi, 0); cr.restore()
    cr.line_to(tx + rx, ty)
    cr.save(); cr.translate(tx, ty); cr.scale(rx, ry); cr.arc(0, 0, 1, 0, math.pi); cr.restore()
    cr.close_path()
    cr.set_source(g); cr.fill()
    ellipse(cr, tx, ty, rx, ry, o.get("top") or shade(col, 1.15), alpha)


def draw_water(cr, cam, o, t, alpha):
    P = cam.P
    x, y, z, w, d = o["x"], o["y"], o["z"], o["w"], o["d"]
    col = o["color"]
    fillpoly(cr, [P(x, y, z), P(x + w, y, z), P(x + w, y + d, z), P(x, y + d, z)], col, alpha * 0.95)
    rnd = random.Random(hash(o["id"]) & 0xffff)
    for i in range(max(2, int(w * d * 0.8))):
        px = x + rnd.random() * w
        py = y + rnd.random() * d
        ph = rnd.random() * 6.28
        s = 0.5 + 0.5 * math.sin(t * 2 + ph)
        sx, sy = P(px, py, z)
        L = 18 * cam.zoom * (0.6 + s)
        stroke_path(cr, [(sx - L, sy), (sx + L, sy)], "#CDEFFF", 3 * cam.zoom, alpha * (0.3 + 0.5 * s))


def smooth(pts, n=6):
    if len(pts) < 3:
        return pts
    out = []
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(len(pts) - 1, i + 2)]
        for k in range(n):
            s = k / n
            s2, s3 = s * s, s * s * s
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * s + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * s2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * s3) for j in range(2)))
    out.append(pts[-1])
    return out


def draw_arrow(cr, cam, o, t, alpha, grow=1.0):
    pts = [cam.P(*p) for p in o["pts"]]
    pts = smooth(pts)
    if grow < 1:
        n = max(2, int(len(pts) * grow))
        pts = pts[:n]
    w = o["width"] * max(cam.zoom, 0.95)
    col = o["color"]
    stroke_path(cr, pts, col, w + 6 * cam.zoom, alpha * 0.25)
    if o.get("flow", True):
        stroke_path(cr, pts, col, w, alpha, dash=[w * 2.6, w * 1.6], offset=-t * 90 * cam.zoom)
    else:
        stroke_path(cr, pts, col, w, alpha)
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    ang = math.atan2(by - ay, bx - ax)
    L = w * 2.6
    tip = (bx + math.cos(ang) * w * 0.8, by + math.sin(ang) * w * 0.8)
    fillpoly(cr, [tip, (tip[0] - L * math.cos(ang - 0.55), tip[1] - L * math.sin(ang - 0.55)),
                  (tip[0] - L * math.cos(ang + 0.55), tip[1] - L * math.sin(ang + 0.55))], col, alpha)


def draw_tree(cr, cam, o, t, alpha):
    bx, by = cam.P(o["x"], o["y"], o["z"])
    s = o["size"] * U * cam.zoom
    k = o["tkind"]
    sway = math.sin(t * 1.3 + o["x"]) * 0.03 * s
    green = o.get("color") or {"pine": "#2E7D4F", "palm": "#4CAF50", "bamboo": "#7CB342", "bush": "#5DAA45", "fig": "#3E8E3A"}.get(k, "#4E9F3D")
    ellipse(cr, bx, by, 0.55 * s, 0.18 * s, "#000000", alpha * 0.15)
    if k == "pine":
        fillpoly(cr, [(bx - 0.08 * s, by), (bx + 0.08 * s, by), (bx + 0.08 * s, by - 0.6 * s), (bx - 0.08 * s, by - 0.6 * s)], "#6B4226", alpha)
        for i, (w_, y0) in enumerate(((0.75, 0.4), (0.6, 1.1), (0.45, 1.8))):
            fillpoly(cr, [(bx - w_ * s, by - y0 * s), (bx + w_ * s, by - y0 * s), (bx + sway, by - (y0 + 1.2) * s)], shade(green, 1 + i * 0.07), alpha)
        return
    if k == "palm":
        top = (bx + 0.35 * s + sway, by - 3.1 * s)
        stroke_path(cr, [(bx, by), (bx + 0.1 * s, by - 1.5 * s), top], "#8D6E4A", 0.18 * s, alpha)
        for a in range(7):
            ang = -math.pi / 2 + (a - 3) * 0.55
            ex, ey = top[0] + math.cos(ang) * 1.1 * s, top[1] + math.sin(ang) * 0.6 * s + 0.35 * s
            stroke_path(cr, [top, ((top[0] + ex) / 2, top[1] - 0.25 * s), (ex, ey)], green, 0.16 * s, alpha)
        return
    if k == "bamboo":
        for i in range(5):
            dx = (i - 2) * 0.16 * s
            hh = (3.6 + (i % 3) * 0.4) * s
            pts = [(bx + dx, by), (bx + dx + sway * (1 + i * 0.3), by - hh)]
            stroke_path(cr, pts, "#9CCC65" if i % 2 else "#8BC34A", 0.09 * s, alpha)
            for j in range(1, 6):
                yy = by - hh * j / 6
                stroke_path(cr, [(bx + dx - 0.05 * s, yy), (bx + dx + 0.05 * s, yy)], "#558B2F", 0.03 * s, alpha)
            for j in range(3):
                yy = by - hh * (0.55 + j * 0.15)
                stroke_path(cr, [(bx + dx, yy), (bx + dx + (0.35 if j % 2 else -0.35) * s, yy - 0.15 * s)], "#689F38", 0.07 * s, alpha)
        return
    if k == "bush":
        for dx, dy, r in ((-0.3, -0.35, 0.4), (0.3, -0.35, 0.4), (0, -0.6, 0.45)):
            circle(cr, bx + dx * s, by + dy * s, r * s, green, alpha)
        circle(cr, bx - 0.1 * s, by - 0.75 * s, 0.15 * s, shade(green, 1.2), alpha * 0.8)
        return
    if k == "fig":
        fillpoly(cr, [(bx - 0.35 * s, by), (bx + 0.35 * s, by), (bx + 0.2 * s, by - 1.8 * s), (bx - 0.2 * s, by - 1.8 * s)], "#7B5B3E", alpha)
        for dx in (-1.1, -0.7, 0.7, 1.1):
            stroke_path(cr, [(bx + dx * s, by - 2.2 * s), (bx + dx * s * 1.05, by - 0.4 * s + abs(dx) * 0.2 * s)], "#8D6E4A", 0.05 * s, alpha)
        for dx, dy, r in ((-1.0, -2.6, 0.8), (1.0, -2.6, 0.8), (0, -3.1, 1.0), (-0.5, -2.4, 0.7), (0.5, -2.4, 0.7)):
            circle(cr, bx + dx * s + sway, by + dy * s, r * s, green, alpha)
        circle(cr, bx - 0.3 * s, by - 3.4 * s, 0.35 * s, shade(green, 1.2), alpha * 0.7)
        return
    # round
    fillpoly(cr, [(bx - 0.1 * s, by), (bx + 0.1 * s, by), (bx + 0.07 * s, by - 1.2 * s), (bx - 0.07 * s, by - 1.2 * s)], "#7B5B3E", alpha)
    for dx, dy, r in ((-0.35, -1.5, 0.55), (0.35, -1.5, 0.55), (0, -2.0, 0.65)):
        circle(cr, bx + dx * s + sway, by + dy * s, r * s, green, alpha)
    circle(cr, bx - 0.2 * s + sway, by - 2.25 * s, 0.25 * s, shade(green, 1.2), alpha * 0.7)


def draw_figure(cr, cam, o, t, alpha):
    bx, by = cam.P(o["x"], o["y"], o["z"])
    s = o["size"] * U * cam.zoom
    pose = o["pose"]
    bob = math.sin(t * 3 + o["x"]) * 0.015 * s if pose != "sit" else 0
    pants, jacket, skin, hair = "#33414F", "#E8A317", "#F1C27D", "#3A2A20"
    ellipse(cr, bx, by, 0.3 * s, 0.1 * s, "#000000", alpha * 0.18)
    hip = (bx, by - 0.85 * s + bob)
    if pose == "sit":
        hip = (bx, by - 0.45 * s)
        stroke_path(cr, [hip, (bx + 0.3 * s, hip[1]), (bx + 0.32 * s, by)], pants, 0.13 * s, alpha)
        stroke_path(cr, [(hip[0] - 0.05 * s, hip[1]), (bx + 0.22 * s, hip[1] + 0.02 * s), (bx + 0.2 * s, by)], shade(pants, 0.85), 0.13 * s, alpha)
    else:
        step = math.sin(t * 8) * 0.12 * s if pose == "walk" else 0
        stroke_path(cr, [hip, (bx - 0.1 * s - step, by)], shade(pants, 0.85), 0.14 * s, alpha)
        stroke_path(cr, [hip, (bx + 0.1 * s + step, by)], pants, 0.14 * s, alpha)
    sh = (hip[0], hip[1] - 0.55 * s)
    # torso
    cr.save()
    w = 0.42 * s
    x0, y0 = sh[0] - w / 2, sh[1] - 0.05 * s
    cr.new_sub_path()
    r = 0.12 * s
    cr.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi)
    cr.arc(x0 + w - r, y0 + r, r, 1.5 * math.pi, 2 * math.pi)
    cr.line_to(x0 + w, hip[1] + 0.05 * s)
    cr.line_to(x0, hip[1] + 0.05 * s)
    cr.close_path()
    cr.set_source_rgba(*rgb(jacket), alpha)
    cr.fill()
    cr.restore()
    fillpoly(cr, [(sh[0] + 0.05 * s, y0 + 0.05 * s), (sh[0] + w / 2, y0 + 0.1 * s), (sh[0] + w / 2, hip[1] + 0.05 * s), (sh[0] + 0.05 * s, hip[1] + 0.05 * s)], shade(jacket, 0.85), alpha)
    # arms
    ls, rs = (sh[0] - w / 2 + 0.03 * s, sh[1] + 0.05 * s), (sh[0] + w / 2 - 0.03 * s, sh[1] + 0.05 * s)
    wave = math.sin(t * 6) * 0.08 * s
    if pose == "cheer":
        la, ra = (ls[0] - 0.25 * s, ls[1] - 0.45 * s + wave), (rs[0] + 0.25 * s, rs[1] - 0.45 * s - wave)
    elif pose == "scared":
        la, ra = (ls[0] - 0.2 * s, ls[1] - 0.35 * s), (rs[0] + 0.2 * s, rs[1] - 0.35 * s)
    elif pose == "work":
        la, ra = (ls[0] - 0.05 * s, ls[1] + 0.4 * s), (rs[0] + 0.4 * s, rs[1] + 0.1 * s + wave)
    elif pose == "sweat":
        la, ra = (ls[0] - 0.05 * s, ls[1] + 0.4 * s), (rs[0] + 0.15 * s, rs[1] - 0.25 * s + wave * 1.5)
    else:
        la, ra = (ls[0] - 0.08 * s, ls[1] + 0.42 * s), (rs[0] + 0.08 * s, rs[1] + 0.42 * s)
    for a, b, c in ((ls, la, shade(jacket, 0.9)), (rs, ra, jacket)):
        stroke_path(cr, [a, b], c, 0.12 * s, alpha)
        circle(cr, b[0], b[1], 0.065 * s, skin, alpha)
    # head (faceless)
    hc = (sh[0], sh[1] - 0.2 * s)
    circle(cr, hc[0], hc[1], 0.19 * s, skin, alpha)
    cr.save()
    cr.arc(hc[0], hc[1], 0.195 * s, math.pi * 1.0, math.pi * 2.0)
    cr.close_path()
    cr.set_source_rgba(*rgb(hair), alpha)
    cr.fill()
    cr.restore()
    if pose == "sweat":
        for i, (dx, dy) in enumerate(((-0.28, -0.05), (0.27, 0.02))):
            ph = (t * 1.5 + i * 0.5) % 1
            fx_, fy = hc[0] + dx * s, hc[1] + dy * s + ph * 0.25 * s
            fillpoly(cr, [(fx_, fy - 0.07 * s), (fx_ + 0.04 * s, fy), (fx_ - 0.04 * s, fy)], "#4FC3F7", alpha * (1 - ph))
            circle(cr, fx_, fy, 0.04 * s, "#4FC3F7", alpha * (1 - ph))
    if pose == "scared":
        for k in range(3):
            a = -math.pi / 2 + (k - 1) * 0.5
            stroke_path(cr, [(hc[0] + math.cos(a) * 0.28 * s, hc[1] + math.sin(a) * 0.28 * s), (hc[0] + math.cos(a) * 0.4 * s, hc[1] + math.sin(a) * 0.4 * s)], "#FFFFFF", 0.04 * s, alpha)


def draw_critter_one(cr, x, y, s, kind, col, face, t, alpha, seed):
    f = face
    wig = math.sin(t * 10 + seed) * 0.04 * s
    if kind in ("insect", "ant"):
        for i, dx in enumerate((-0.32, 0, 0.3)):
            ellipse(cr, x + dx * s * f, y - 0.12 * s, (0.17 if i != 1 else 0.11) * s, (0.12 if i != 1 else 0.09) * s, shade(col, 1 - 0.1 * i), alpha)
        for k in (-0.12, 0, 0.12):
            stroke_path(cr, [(x + k * s, y - 0.1 * s), (x + k * s - 0.1 * s, y + 0.02 * s + wig)], shade(col, 0.6), 0.03 * s, alpha)
            stroke_path(cr, [(x + k * s, y - 0.1 * s), (x + k * s + 0.1 * s, y + 0.02 * s - wig)], shade(col, 0.6), 0.03 * s, alpha)
        hx = x + 0.42 * s * f
        stroke_path(cr, [(hx, y - 0.18 * s), (hx + 0.12 * s * f, y - 0.32 * s + wig)], shade(col, 0.6), 0.025 * s, alpha)
        circle(cr, hx + 0.03 * s * f, y - 0.15 * s, 0.02 * s, "#111111", alpha)
        return
    if kind == "fish":
        ellipse(cr, x, y - 0.15 * s, 0.32 * s, 0.15 * s, col, alpha)
        fillpoly(cr, [(x - 0.28 * s * f, y - 0.15 * s), (x - 0.5 * s * f, y - 0.32 * s + wig), (x - 0.5 * s * f, y + 0.02 * s - wig)], shade(col, 0.85), alpha)
        circle(cr, x + 0.18 * s * f, y - 0.18 * s, 0.035 * s, "#111111", alpha)
        return
    if kind == "bird":
        ellipse(cr, x, y - 0.3 * s, 0.25 * s, 0.17 * s, col, alpha)
        circle(cr, x + 0.22 * s * f, y - 0.45 * s, 0.11 * s, col, alpha)
        fillpoly(cr, [(x + 0.31 * s * f, y - 0.47 * s), (x + 0.45 * s * f, y - 0.43 * s), (x + 0.31 * s * f, y - 0.4 * s)], "#F5A623", alpha)
        fillpoly(cr, [(x - 0.1 * s * f, y - 0.35 * s), (x + 0.1 * s * f, y - 0.32 * s), (x - 0.25 * s * f, y - 0.55 * s + wig * 3)], shade(col, 0.8), alpha)
        circle(cr, x + 0.25 * s * f, y - 0.48 * s, 0.025 * s, "#111111", alpha)
        stroke_path(cr, [(x, y - 0.15 * s), (x, y)], "#F5A623", 0.03 * s, alpha)
        return
    if kind == "crab":
        ellipse(cr, x, y - 0.15 * s, 0.3 * s, 0.17 * s, col, alpha)
        for k in (-1, 1):
            for j in range(3):
                stroke_path(cr, [(x + k * 0.2 * s, y - 0.12 * s), (x + k * (0.4 + j * 0.05) * s, y + (0.02 - j * 0.04) * s + wig)], shade(col, 0.8), 0.035 * s, alpha)
            circle(cr, x + k * 0.38 * s, y - 0.38 * s + wig, 0.09 * s, shade(col, 1.05), alpha)
        circle(cr, x - 0.08 * s, y - 0.32 * s, 0.03 * s, "#111111", alpha)
        circle(cr, x + 0.08 * s, y - 0.32 * s, 0.03 * s, "#111111", alpha)
        return
    if kind == "rodent":
        ellipse(cr, x, y - 0.22 * s, 0.3 * s, 0.22 * s, col, alpha)
        circle(cr, x + 0.25 * s * f, y - 0.33 * s, 0.15 * s, col, alpha)
        circle(cr, x + 0.2 * s * f, y - 0.47 * s, 0.05 * s, shade(col, 0.8), alpha)
        circle(cr, x + 0.33 * s * f, y - 0.36 * s, 0.025 * s, "#111111", alpha)
        stroke_path(cr, [(x - 0.28 * s * f, y - 0.15 * s), (x - 0.5 * s * f, y - 0.25 * s + wig)], shade(col, 0.7), 0.03 * s, alpha)
        return
    # quadruped
    for k, dx in enumerate((-0.28, -0.12, 0.12, 0.28)):
        stroke_path(cr, [(x + dx * s, y - 0.3 * s), (x + dx * s + (wig if k % 2 else -wig), y)], shade(col, 0.75), 0.07 * s, alpha)
    ellipse(cr, x, y - 0.42 * s, 0.4 * s, 0.2 * s, col, alpha)
    circle(cr, x + 0.42 * s * f, y - 0.6 * s, 0.15 * s, col, alpha)
    fillpoly(cr, [(x + 0.36 * s * f, y - 0.72 * s), (x + 0.42 * s * f, y - 0.88 * s), (x + 0.47 * s * f, y - 0.72 * s)], shade(col, 0.8), alpha)
    circle(cr, x + 0.5 * s * f, y - 0.62 * s, 0.025 * s, "#111111", alpha)
    stroke_path(cr, [(x - 0.4 * s * f, y - 0.45 * s), (x - 0.55 * s * f, y - 0.6 * s + wig)], shade(col, 0.75), 0.05 * s, alpha)


def draw_critter(cr, cam, o, t, alpha):
    s = o["size"] * U * cam.zoom * 0.6
    n = o.get("n", 1)
    rnd = random.Random(hash(o["id"]) & 0xffff)
    for i in range(n):
        if n > 1:
            dx, dy = (rnd.random() * 2 - 1) * o["spread"], (rnd.random() * 2 - 1) * o["spread"]
            jit = math.sin(t * 2 + i) * 0.08
        else:
            dx = dy = jit = 0
        x, y = cam.P(o["x"] + dx + jit, o["y"] + dy, o["z"])
        face = o["face"] if n == 1 else (1 if rnd.random() > 0.5 else -1)
        draw_critter_one(cr, x, y, s, o["ckind"], o["color"], face, t, alpha, i)


def draw_rock(cr, cam, o, alpha):
    x, y = cam.P(o["x"], o["y"], o["z"])
    s = o["size"] * U * cam.zoom * 0.5
    rnd = random.Random(hash(o["id"]) & 0xffff)
    pts = []
    for k in range(8):
        a = math.pi + k * math.pi / 7
        rr = s * (0.8 + rnd.random() * 0.35)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.7))
    fillpoly(cr, pts, o["color"], alpha)
    fillpoly(cr, pts[3:7] + [(x, y - s * 0.2)], shade(o["color"], 1.15), alpha * 0.7)


def draw_label(cr, cam, o, alpha, pop=1.0):
    ax, ay = cam.P(o["x"], o["y"], o["z"])
    tx, ty = ax + o["dx"], ay + o["dy"]
    tx = min(max(tx, 170), VW - 170)
    ty = min(max(ty, 520), 1290)
    stroke_path(cr, [(ax, ay), (tx, ty)], "#FFFFFF", 4, alpha)
    circle(cr, ax, ay, 9, "#FFFFFF", alpha)
    circle(cr, ax, ay, 5, YEL, alpha)
    cr.save()
    cr.translate(tx, ty)
    cr.scale(pop, pop)
    pill(cr, o["text"], 0, 0, size=38, alpha=alpha)
    cr.restore()


def draw_measure(cr, cam, o, alpha, grow=1.0):
    a = cam.P(o["x"], o["y"], o["z0"])
    b = cam.P(o["x"], o["y"], o["z1"])
    b = (a[0] + (b[0] - a[0]) * grow, a[1] + (b[1] - a[1]) * grow)
    stroke_path(cr, [a, b], "#FFFFFF", 6, alpha)
    for p in (a, b):
        stroke_path(cr, [(p[0] - 22, p[1]), (p[0] + 22, p[1])], "#FFFFFF", 6, alpha)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    side = o.get("side", 1)
    outlined_text(cr, o["text"], mx + side * 120, my, 72, fill=YEL, alpha=alpha, ow=12)


def draw_sun(cr, t, alpha):
    x, y = 900, 560
    for k, r in enumerate((150, 115, 85)):
        circle(cr, x, y, r + math.sin(t * 1.2) * 4, "#FFE9A6" if k < 2 else "#FFD66B", alpha * (0.25 if k == 0 else 0.45 if k == 1 else 1))


def draw_clouds(cr, t, alpha, n=3):
    rnd = random.Random(3)
    for i in range(n):
        x = (rnd.random() * VW + t * (12 + i * 5)) % (VW + 400) - 200
        y = 520 + rnd.random() * 380
        s = 0.8 + rnd.random() * 0.6
        for dx, dy, r in ((-60, 0, 50), (0, -25, 65), (65, 0, 50), (0, 10, 55)):
            circle(cr, x + dx * s, y + dy * s, r * s, "#FFFFFF", alpha * 0.85)


def draw_fx(cr, kind, t, alpha):
    rnd = random.Random(11)
    if kind == "night":
        cr.rectangle(0, 0, VW, VH)
        cr.set_source_rgba(0.04, 0.07, 0.2, 0.5 * alpha)
        cr.fill()
        for i in range(40):
            x, y = rnd.random() * VW, 480 + rnd.random() * 500
            circle(cr, x, y, 2 + rnd.random() * 2, "#FFFFFF", alpha * (0.4 + 0.6 * abs(math.sin(t * 2 + i))))
        return
    if kind == "rain":
        for i in range(140):
            x0 = rnd.random() * (VW + 300)
            sp = 1400 + rnd.random() * 400
            y = (rnd.random() * VH + t * sp) % (VH + 100) - 50
            x = x0 - (y * 0.25)
            stroke_path(cr, [(x, y), (x - 10, y + 38)], "#DDEFFF", 3, alpha * 0.6)
        return
    if kind == "snow":
        for i in range(120):
            x0 = rnd.random() * VW
            sp = 80 + rnd.random() * 90
            y = (rnd.random() * VH + t * sp) % VH
            x = x0 + math.sin(t + i) * 20
            circle(cr, x, y, 3 + rnd.random() * 4, "#FFFFFF", alpha * 0.85)
        return
    if kind == "wind":
        for i in range(16):
            y = 500 + rnd.random() * 800
            sp = 700 + rnd.random() * 500
            x = (rnd.random() * VW * 2 + t * sp) % (VW + 600) - 300
            L = 120 + rnd.random() * 160
            stroke_path(cr, [(x, y), (x + L * 0.5, y - 6), (x + L, y)], "#FFFFFF", 5, alpha * 0.55)
        return
    if kind == "heat":
        for i in range(12):
            x0 = 80 + i * 85 + rnd.random() * 30
            ph = (t * 0.5 + rnd.random()) % 1
            y0 = 1250 - ph * 700
            pts = [(x0 + math.sin(k * 0.8 + t * 3 + i) * 12, y0 - k * 22) for k in range(8)]
            stroke_path(cr, pts, "#FF8A3D", 5, alpha * 0.45 * math.sin(ph * math.pi))
        cr.rectangle(0, 0, VW, VH)
        cr.set_source_rgba(1.0, 0.55, 0.15, 0.08 * alpha)
        cr.fill()
        return
    if kind == "sparkle":
        for i in range(14):
            x, y = 150 + rnd.random() * 780, 550 + rnd.random() * 700
            s = abs(math.sin(t * 3 + i * 1.7))
            L = 22 * s
            stroke_path(cr, [(x - L, y), (x + L, y)], "#FFFFFF", 4, alpha * s)
            stroke_path(cr, [(x, y - L), (x, y + L)], "#FFFFFF", 4, alpha * s)
        return
    if kind == "dust":
        for i in range(60):
            x = (rnd.random() * VW + t * (40 + rnd.random() * 60)) % VW
            y = 700 + rnd.random() * 600 + math.sin(t + i) * 15
            circle(cr, x, y, 2 + rnd.random() * 4, "#C8A46A", alpha * 0.5)


def draw_counter(cr, text, alpha, pop=1.0):
    cr.save()
    cr.translate(540, 600)
    cr.scale(pop, pop)
    pill(cr, text, 0, 0, size=84, font=FONT_BIG, alpha=alpha, bg=YEL, fg=INK)
    cr.restore()


def draw_obj(cr, cam, o, scene, t, alpha, prog=1.0):
    k = o["kind"]
    if k == "ground":
        draw_ground(cr, cam, o, t, alpha)
    elif k == "box":
        draw_box(cr, cam, o["x"], o["y"], o["z"], o["w"], o["d"], o["h"], o["color"], o.get("top"), alpha)
    elif k == "room":
        draw_room(cr, cam, o, alpha)
    elif k == "roof":
        draw_roof(cr, cam, o, alpha)
    elif k == "cyl":
        draw_cyl(cr, cam, o, alpha)
    elif k == "cone":
        draw_cyl(cr, cam, o, alpha, cone=True)
    elif k == "water":
        draw_water(cr, cam, o, t, alpha)
    elif k == "patch":
        draw_patch(cr, cam, o, scene, t, alpha)
    elif k == "poly":
        fillpoly(cr, [cam.P(*p) for p in o["pts"]], o["color"], alpha, outline=o.get("outline"), lw=2 * cam.zoom)
    elif k == "line3":
        stroke_path(cr, smooth([cam.P(*p) for p in o["pts"]]), o["color"], o["width"] * max(cam.zoom, 0.8), alpha)
    elif k == "arrow":
        draw_arrow(cr, cam, o, t, alpha, grow=min(1.0, prog * 1.6))
    elif k == "tree":
        draw_tree(cr, cam, o, t, alpha)
    elif k == "figure":
        draw_figure(cr, cam, o, t, alpha)
    elif k == "critter":
        draw_critter(cr, cam, o, t, alpha)
    elif k == "rock":
        draw_rock(cr, cam, o, alpha)
    elif k == "label":
        draw_label(cr, cam, o, alpha, pop=0.6 + 0.4 * min(1, prog * 2.5))
    elif k == "measure":
        draw_measure(cr, cam, o, alpha, grow=min(1.0, prog * 2))
    elif k == "counter":
        draw_counter(cr, o["text"], alpha, pop=0.7 + 0.3 * min(1, prog * 3))


def anchor(o, cam):
    pts = obj_points(o, {})
    if not pts:
        return None
    sx = [cam.P(*p) for p in pts]
    xs = [p[0] for p in sx]; ys = [p[1] for p in sx]
    return ((min(xs) + max(xs)) / 2, max(ys))
