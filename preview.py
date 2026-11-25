import sys
from scenes import *
times = {'room':[1.2,3.3,4.2,5.5],'home':[2.5],'chop':[1.5],'egg':[1.2,1.8],'sugar':[2.0],'whisk':[2.5],'flour':[1.9],'stir':[1.2,3.0],'scoop':[2.3],'oven':[2.0,4.6],'out':[2.0],'serve':[1.0,2.3,4.6,6.5]}
sel = sys.argv[1:] or list(times)
shots=[]
for name,fn,d,fi,fo in SCENES:
    if name not in sel: continue
    for t in times[name]:
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); frame(c,name,fn,t,d,fi,fo); shots.append(s)
cols=4; sc=0.25; rows=(len(shots)+cols-1)//cols
g=cairo.ImageSurface(cairo.FORMAT_ARGB32,int(W*sc*cols),int(H*sc*rows)); c=cairo.Context(g)
for i,s in enumerate(shots):
    c.save(); c.translate((i%cols)*W*sc,(i//cols)*H*sc); c.scale(sc,sc); c.set_source_surface(s); c.paint(); c.restore()
g.write_to_png('preview.png')
