import cairo, math, random

W, H = 1920, 1080
RED = (0.82, 0.13, 0.16)
PAPER = (0.91, 0.88, 0.80)
INK = (0.13, 0.12, 0.11)
MOON = (0.80, 0.86, 0.95)
BG = (0.03, 0.035, 0.05)

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def font(ctx, fam, size, bold=False, italic=False):
    ctx.select_font_face(fam, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def text(ctx, s, x, y, fam="Inter", size=40, color=(1, 1, 1), a=1.0, align="l", bold=False, spacing=0):
    font(ctx, fam, size, bold)
    if spacing:
        widths = [ctx.text_extents(c).x_advance + spacing for c in s]
        tw = sum(widths) - spacing
    else:
        tw = ctx.text_extents(s).x_advance
    if align == "c": x -= tw / 2
    elif align == "r": x -= tw
    ctx.set_source_rgba(*color, a)
    if spacing:
        cx = x
        for c, w in zip(s, widths):
            ctx.move_to(cx, y); ctx.show_text(c); cx += w
    else:
        ctx.move_to(x, y); ctx.show_text(s)
    return tw

def twidth(ctx, s, fam, size, bold=False):
    font(ctx, fam, size, bold); return ctx.text_extents(s).x_advance

def wrap(ctx, s, maxw, fam, size, bold=False):
    font(ctx, fam, size, bold)
    words = s.split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if ctx.text_extents(t).x_advance > maxw and cur:
            lines.append(cur); cur = w_
        else:
            cur = t
    if cur: lines.append(cur)
    return lines

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()

def radial_bg(ctx, c0, c1, cx=W / 2, cy=H / 2, r=1300):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
    g.add_color_stop_rgb(0, *c0); g.add_color_stop_rgb(1, *c1)
    ctx.set_source(g); ctx.paint()

def glow(ctx, x, y, r, col, a=0.5):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()

def surface(w=W, h=H):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    return s, cairo.Context(s)

def blit(ctx, surf, zoom=1.0, cx=None, cy=None, ox=0, oy=0, alpha=1.0):
    """draw cached surface (size sw x sh) centred, scaled so it covers frame * zoom"""
    sw, sh = surf.get_width(), surf.get_height()
    sc = max(W / sw, H / sh) * zoom
    ctx.save()
    ctx.translate(W / 2 + ox, H / 2 + oy)
    ctx.scale(sc, sc)
    ctx.translate(-(cx if cx is not None else sw / 2), -(cy if cy is not None else sh / 2))
    ctx.set_source_surface(surf, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
    ctx.paint_with_alpha(alpha)
    ctx.restore()

def noise_dots(ctx, n, w, h, col, amin, amax, rmax, seed=1):
    rnd = random.Random(seed)
    for _ in range(n):
        ctx.set_source_rgba(*col, rnd.uniform(amin, amax))
        ctx.arc(rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.5, rmax), 0, 2 * math.pi); ctx.fill()

def typed(s, u):
    n = int(len(s) * clamp(u)); return s[:n]

def stamp(ctx, s, x, y, size, ang, a, col=RED, scale=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(scale, scale)
    font(ctx, "Bebas Neue", size)
    tw = ctx.text_extents(s).x_advance
    ctx.set_line_width(6); ctx.set_source_rgba(*col, a)
    rrect(ctx, -tw / 2 - 24, -size * 0.85, tw + 48, size * 1.05, 8); ctx.stroke()
    ctx.move_to(-tw / 2, 0); ctx.show_text(s)
    ctx.restore()

def caption_bar(ctx, s, u, x=90, y=H - 190):
    if not s: return
    a = ease(u * 4)
    font(ctx, "Special Elite", 34)
    shown = typed(s, u * 2.2)
    tw = ctx.text_extents(s).x_advance
    ctx.set_source_rgba(0, 0, 0, 0.55 * a); ctx.rectangle(x - 20, y - 46, tw + 40, 66); ctx.fill()
    ctx.set_source_rgba(*RED, a); ctx.rectangle(x - 20, y - 46, 6, 66); ctx.fill()
    ctx.set_source_rgba(0.95, 0.93, 0.88, a); ctx.move_to(x, y); ctx.show_text(shown)
