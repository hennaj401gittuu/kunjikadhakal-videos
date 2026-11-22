"""Real-geography map rendering for Midnight Witness (Natural Earth 10m data)."""
import json, math, os, pickle
GEO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geo")
CACHE = os.path.join(GEO, "na_cache.pkl")
SRC = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"

def _rings(geom):
    t = geom["type"]; c = geom["coordinates"]
    if t == "Polygon": return [c]
    if t == "MultiPolygon": return c
    if t == "LineString": return [[c]]
    if t == "MultiLineString": return [[x] for x in c]
    return []

def _bbox(polys):
    xs = [p[0] for poly in polys for ring in poly for p in ring]; ys = [p[1] for poly in polys for ring in poly for p in ring]
    return (min(xs), min(ys), max(xs), max(ys))

def build_cache(region=(-170, 5, -50, 75)):
    """region = lon0, lat0, lon1, lat1 to keep (default: North America)."""
    def inb(bb):
        return not (bb[2] < region[0] or bb[0] > region[2] or bb[3] < region[1] or bb[1] > region[3])
    out = {"states": [], "lakes": [], "roads": [], "coast": [], "places": []}
    d = json.load(open(os.path.join(GEO, "ne_10m_admin_1_states_provinces_lakes.geojson")))
    for f in d["features"]:
        polys = _rings(f["geometry"]);
        if not polys: continue
        bb = _bbox(polys)
        if inb(bb):
            p = f["properties"]
            out["states"].append({"name": p.get("name"), "postal": p.get("postal"), "iso": p.get("iso_a2"), "bb": bb, "polys": polys,
                                  "lab": (p.get("longitude"), p.get("latitude"))})
    d = json.load(open(os.path.join(GEO, "ne_10m_lakes.geojson")))
    for f in d["features"]:
        polys = _rings(f["geometry"]); bb = _bbox(polys)
        if inb(bb): out["lakes"].append({"bb": bb, "polys": polys})
    d = json.load(open(os.path.join(GEO, "ne_10m_roads.geojson")))
    for f in d["features"]:
        p = f["properties"]
        if p.get("type") not in ("Major Highway", "Secondary Highway", "Beltway", "Road"): continue
        polys = _rings(f["geometry"])
        if not polys: continue
        bb = _bbox(polys)
        if inb(bb): out["roads"].append({"bb": bb, "polys": polys, "major": p.get("type") in ("Major Highway", "Beltway"), "label": p.get("label") or ""})
    d = json.load(open(os.path.join(GEO, "ne_10m_populated_places_simple.geojson")))
    for f in d["features"]:
        p = f["properties"]
        out["places"].append((p["name"], p.get("adm1name"), p.get("iso_a2"), p["latitude"], p["longitude"], p.get("pop_max") or 0))
    pickle.dump(out, open(CACHE, "wb"))
    return out

_D = None
def data():
    global _D
    if _D is None:
        _D = pickle.load(open(CACHE, "rb")) if os.path.exists(CACHE) else build_cache()
    return _D

def find_place(name, state=None):
    """Look up a place by name (optionally 'Name, ST'); returns (lat, lon) or None."""
    nm = name.split(",")[0].strip().lower()
    cands = [p for p in data()["places"] if p[0].lower() == nm]
    if state:
        cands = [p for p in cands if (p[1] or "").lower().startswith(state.lower()) or (p[2] or "").lower() == state.lower()]
    if not cands: return None
    cands.sort(key=lambda p: -p[5])
    return (cands[0][3], cands[0][4])

def state_bbox(code):
    for s in data()["states"]:
        if s["postal"] == code and s["iso"] == "US": return s["bb"]
    return None

class Proj:
    """Equirectangular with cos(lat) correction, fitted so that bbox fills the frame."""
    def __init__(self, bb, W, H, fill=0.82):
        lon0, lat0, lon1, lat1 = bb
        self.k = math.cos(math.radians((lat0 + lat1) / 2))
        self.cx, self.cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
        w = (lon1 - lon0) * self.k; h = (lat1 - lat0)
        self.s = min(W * fill / max(w, 1e-6), H * fill / max(h, 1e-6))
        self.W, self.H = W, H
    def __call__(self, lon, lat):
        return (self.W / 2 + (lon - self.cx) * self.k * self.s, self.H / 2 - (lat - self.cy) * self.s)

def lerp_bb(a, b, u):
    # interpolate in log-size space for a smooth zoom
    ca = ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2); cb = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    wa, ha = a[2] - a[0], a[3] - a[1]; wb, hb = b[2] - b[0], b[3] - b[1]
    w = math.exp(math.log(wa) * (1 - u) + math.log(wb) * u); h = math.exp(math.log(ha) * (1 - u) + math.log(hb) * u)
    cx = ca[0] + (cb[0] - ca[0]) * u; cy = ca[1] + (cb[1] - ca[1]) * u
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

def visible(bb, view):
    return not (bb[2] < view[0] or bb[0] > view[2] or bb[3] < view[1] or bb[1] > view[3])

def draw_base(ctx, view, W, H, hi_states=(), roads=True):
    """Draw land, states, lakes, roads for current view. Returns projection."""
    import cairo
    P = Proj(view, W, H, 1.0)
    vw = view[2] - view[0]
    ctx.set_source_rgb(0.015, 0.03, 0.05); ctx.paint()   # ocean
    D = data()
    tol = vw / 2500.0   # simplification step in degrees
    def path(poly):
        for ring in poly:
            last = None
            for i, (lo, la) in enumerate(ring):
                if last and abs(lo - last[0]) < tol and abs(la - last[1]) < tol and i != len(ring) - 1: continue
                x, y = P(lo, la)
                if last is None: ctx.move_to(x, y)
                else: ctx.line_to(x, y)
                last = (lo, la)
            ctx.close_path()
    pad = (view[0] - vw * 0.2, view[1] - vw * 0.2, view[2] + vw * 0.2, view[3] + vw * 0.2)
    for s in D["states"]:
        if not visible(s["bb"], pad): continue
        hi = s["postal"] in hi_states and s["iso"] == "US"
        us = s["iso"] == "US"
        for poly in s["polys"]: path(poly)
        if hi: ctx.set_source_rgb(0.11, 0.13, 0.17)
        elif us: ctx.set_source_rgb(0.065, 0.075, 0.095)
        else: ctx.set_source_rgb(0.045, 0.05, 0.06)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.55, 0.65, 0.78, 0.35 if us else 0.18); ctx.set_line_width(1.3); ctx.stroke()
    for l in D["lakes"]:
        if not visible(l["bb"], pad): continue
        for poly in l["polys"]: path(poly)
        ctx.set_source_rgb(0.015, 0.03, 0.05); ctx.fill()
    if roads:
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        for r in D["roads"]:
            if not visible(r["bb"], pad): continue
            if not r["major"] and vw > 9: continue
            for poly in r["polys"]:
                for ring in poly:
                    last = None
                    for lo, la in ring:
                        if last and abs(lo - last[0]) < tol and abs(la - last[1]) < tol: continue
                        x, y = P(lo, la)
                        if last is None: ctx.move_to(x, y)
                        else: ctx.line_to(x, y)
                        last = (lo, la)
            if r["major"]: ctx.set_source_rgba(0.95, 0.62, 0.25, 0.42); ctx.set_line_width(2.0)
            else: ctx.set_source_rgba(0.8, 0.7, 0.55, 0.18); ctx.set_line_width(1.0)
            ctx.stroke()
    # highlighted state glow border
    for s in D["states"]:
        if s["postal"] in hi_states and s["iso"] == "US":
            for poly in s["polys"]: path(poly)
            ctx.set_source_rgba(0.85, 0.2, 0.22, 0.25); ctx.set_line_width(9); ctx.stroke_preserve()
            ctx.set_source_rgba(0.95, 0.35, 0.35, 0.9); ctx.set_line_width(2.2); ctx.stroke()
    return P

def state_labels(ctx, P, view, text_fn, min_area_deg=0):
    vw = view[2] - view[0]
    if vw < 2.5: return
    for s in data()["states"]:
        if s["iso"] != "US" or not s["lab"][0]: continue
        lo, la = s["lab"]
        if not (view[0] < lo < view[2] and view[1] < la < view[3]): continue
        x, y = P(lo, la)
        text_fn(s["name"].upper(), x, y)
