"""Build to Survive - isometric 2.5D scene kit.
A script builds a list of BEATS; each beat = one narration line + objects that pop in.
Objects persist (the build grows layer by layer) until removed.

World axes: x runs to the screen's lower-right, y to the lower-left, z is up. 1 unit ~ 1 metre-ish tile.
Every helper returns a dict; give it id="..." if you want to remove/replace it later
(an object with the same id as an existing one REPLACES it, e.g. red arrows -> blue arrows).
"""
import math

C = 0.8660254  # cos 30
_auto = [0]


def _o(kind, **kw):
    _auto[0] += 1
    kw.setdefault("id", f"{kind}{_auto[0]}")
    kw["kind"] = kind
    return kw


# ---------- colour helpers ----------
def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def shade(col, f):
    r, g, b = hexrgb(col) if isinstance(col, str) else col
    if f < 1:
        return (r * f, g * f, b * f)
    return (r + (1 - r) * (f - 1), g + (1 - g) * (f - 1), b + (1 - b) * (f - 1))


# ---------- palettes for ground blocks ----------
GROUNDS = {
    # top colour, then strata from top: (thickness, colour)
    "grass":   ("#6BBF4E", [(0.35, "#4E9A3A"), (1.2, "#9A6340"), (0.5, "#8A5636"), (2.0, "#B07A52")]),
    "desert":  ("#E8CC8E", [(0.35, "#D9B77A"), (1.0, "#C79A5E"), (0.5, "#B4874E"), (2.0, "#9A6340")]),
    "savanna": ("#D9C06A", [(0.3, "#C2A24E"), (1.2, "#B5743F"), (0.5, "#A0623A"), (2.0, "#8A5636")]),
    "jungle":  ("#4FA83D", [(0.4, "#3B8A2E"), (1.2, "#7A4A2E"), (0.5, "#6B3F26"), (2.0, "#8E5E3C")]),
    "snow":    ("#F4F8FB", [(0.5, "#DCE7EF"), (1.0, "#C3D3DF"), (0.6, "#8A99A6"), (2.0, "#6F7C88")]),
    "rock":    ("#9AA3A8", [(0.4, "#858E94"), (1.5, "#737B80"), (2.0, "#60676B")]),
    "beach":   ("#F2DDA4", [(0.3, "#E6CB86"), (1.0, "#D4B470"), (2.0, "#B9965A")]),
}


# ---------- primitives ----------
def ground(x=0, y=0, w=10, d=10, style="grass", depth=4.0, id="ground", **kw):
    """Cut-away block of earth: grass/sand top and coloured strata on the two visible sides."""
    return _o("ground", x=x, y=y, w=w, d=d, style=style, depth=depth, id=id, z=0, h=0, **kw)


def box(x, y, z, w, d, h, color="#F0D9A8", top=None, **kw):
    """Solid box. color = side colour; top defaults to a lighter shade."""
    return _o("box", x=x, y=y, z=z, w=w, d=d, h=h, color=color, top=top, **kw)


def room(x, y, z, w, d, h, wall="#F0D9A8", floor="#C9A66C", thick=0.15, **kw):
    """Cut-away building: floor + the two BACK walls only, so you see inside."""
    return _o("room", x=x, y=y, z=z, w=w, d=d, h=h, wall=wall, floor=floor, thick=thick, **kw)


def roof(x, y, z, w, d, h, color="#F2B233", style="pyramid", over=0.2, **kw):
    """Roof on top of a box at height z. style: pyramid | gable_x | gable_y | flat."""
    return _o("roof", x=x, y=y, z=z, w=w, d=d, h=h, color=color, style=style, over=over, **kw)


def cyl(x, y, z, r, h, color="#C9A66C", top=None, **kw):
    """Vertical cylinder centred on (x,y). Towers, trunks, tanks, wells."""
    return _o("cyl", x=x, y=y, z=z, r=r, h=h, color=color, top=top, **kw)


def cone(x, y, z, r, h, color="#C2A24E", **kw):
    """Cone / mound centred on (x,y)."""
    return _o("cone", x=x, y=y, z=z, r=r, h=h, color=color, **kw)


def water(x, y, z, w, d, color="#3FA7E0", **kw):
    """Flat water surface with animated ripples."""
    return _o("water", x=x, y=y, z=z, w=w, d=d, h=0, color=color, **kw)


def side_patch(face, a, b, z0, z1, color="#3FA7E0", g=None, **kw):
    """Paint a rectangle on a visible side face of the ground block (shows tunnels, water channels,
    burrows, roots underground). face 'x' = right side face (plane x=ground.x+w), runs along y from a to b;
    face 'y' = left side face (plane y=ground.y+d), runs along x from a to b. z0<z1 (negative = underground)."""
    return _o("patch", face=face, a=a, b=b, z0=z0, z1=z1, color=color, **kw)


def poly(pts, color="#888888", outline=None, **kw):
    """Free 3D polygon: pts = [(x,y,z), ...]. Escape hatch for custom shapes (boats, bridges, ramps)."""
    return _o("poly", pts=pts, color=color, outline=outline, **kw)


def line3(pts, color="#5A3A22", width=6, **kw):
    """Thick 3D polyline (ropes, roots, poles, cables). width in px at zoom 1."""
    return _o("line3", pts=pts, color=color, width=width, **kw)


def arrows(pts, color="#FFFFFF", width=10, flow=True, **kw):
    """Flow arrow along 3D points (wind, water, air, path). Animated dashes when flow=True.
    Use red '#E74C3C' for hot air, blue '#4FC3F7' for cool air."""
    return _o("arrow", pts=pts, color=color, width=width, flow=flow, **kw)


def tree(x, y, z=0, size=1.0, kind="round", color=None, **kw):
    """kind: round | pine | palm | bamboo | bush | fig (big spreading tree)."""
    return _o("tree", x=x, y=y, z=z, size=size, tkind=kind, color=color, **kw)


def figure(x, y, z=0, size=1.0, pose="stand", **kw):
    """Our mascot: faceless figure in a mustard-yellow jacket.
    pose: stand | sweat | cheer | work | sit | scared | walk."""
    return _o("figure", x=x, y=y, z=z, size=size, pose=pose, **kw)


def critter(x, y, z=0, size=1.0, kind="insect", color="#8B5A2B", n=1, spread=1.0, face=1, **kw):
    """Simple animal drawn at a 3D point. kind: insect | ant | quadruped | bird | fish | rodent | crab.
    n>1 scatters a group within `spread` units (a swarm, a herd). face 1 = looks right, -1 = left."""
    return _o("critter", x=x, y=y, z=z, size=size, ckind=kind, color=color, n=n, spread=spread, face=face, **kw)


def rock(x, y, z=0, size=1.0, color="#8E979C", **kw):
    return _o("rock", x=x, y=y, z=z, size=size, color=color, **kw)


def label(text, x, y, z, dx=160, dy=-90, **kw):
    """Yellow rounded tag with a white leader line pointing at a 3D point. dx/dy = tag offset in px."""
    return _o("label", text=text.upper(), x=x, y=y, z=z, dx=dx, dy=dy, **kw)


def measure(x, y, z0, z1, text, side=1, **kw):
    """White vertical measuring line from z0 to z1 at (x,y) with a big number tag, e.g. '28 M'."""
    return _o("measure", x=x, y=y, z0=z0, z1=z1, text=text.upper(), side=side, **kw)


def sun(color="#FFD66B", **kw):
    return _o("sun", color=color, id=kw.pop("id", "sun"), **kw)


def clouds(n=3, **kw):
    return _o("clouds", n=n, id=kw.pop("id", "clouds"), **kw)


def fx(kind, **kw):
    """Screen effect that stays until removed: heat | rain | snow | wind | night | sparkle | dust.
    Default id = 'fx_<kind>' so remove('fx_rain') stops the rain."""
    return _o("fx", fx=kind, id=kw.pop("id", f"fx_{kind}"), **kw)


def remove(*ids):
    return {"kind": "remove", "ids": list(ids), "id": "_rm"}


def focus(x, y, z, zoom=1.6):
    """Camera instruction for this beat: push in on a 3D point."""
    return {"kind": "focus", "x": x, "y": y, "z": z, "zoom": zoom, "id": "_focus"}


def overview(zoom=None):
    """Camera instruction: back to auto-fit of everything (optionally scaled)."""
    return {"kind": "overview", "zoom": zoom, "id": "_ov"}


def counter(text, **kw):
    """Big centred number/time card that stays for the beat (e.g. '15 YEARS', '45°C')."""
    return _o("counter", text=text.upper(), **kw)


def beat(line, *objs, hold=0.0):
    """One narration line + the objects that appear while it is spoken. hold = extra seconds after the line."""
    return {"line": line, "objs": list(objs), "hold": hold}
