import cairo, sys
from gfx import W, H
exec(open("script.py").read())
import scenes as sc
def booknum(i): return sum(1 for j in range(i) if S[j][0] == "book")
sel = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else None
frac = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7
seen = set(); out = []
for i, (scn, p, t) in enumerate(S):
    if sel is not None:
        if i not in sel: continue
    elif scn in seen: continue
    seen.add(scn)
    D = 8.0
    sc._book[0] = booknum(i)
    obj = sc.make(scn, p, D, i)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    obj.frame(c, D * frac)
    fn = f"prev/{i:03d}_{scn}.png"; s.write_to_png(fn); out.append(fn)
print(len(out))
