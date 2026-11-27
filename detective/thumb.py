import sys, cairo, math
sys.path.insert(0,'/home/claude/det'); sys.path.insert(0,'/home/claude/pz')
from chars import human, ARJUN, RAVI, VELU, hexc
import bgs
from bgs import glow
from wd import text
W,H=1920,1080
s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s)
c.save(); c.translate(W/2,H/2); c.scale(1.35,1.35); c.translate(-960,-600); bgs.paint(c,'gal_lit')
import ep
ep.case(c, 0, has_sword=False, lit=True)
ep.footprint(c, 1090, 1010, 0.6, 1.0, -0.2)
c.restore()
glow(c, 960, 640, 700, (1,0.75,0.35), 0.25)
human(c, 250, 1330, 1.05, VELU, dict(face=1, expr='scared', arm_l='up', arm_r='up'), 0.3)
human(c, 1480, 1330, 1.12, RAVI, dict(face=-1, expr='smug', arm_l='hip', arm_r='hip'), 0.3)
human(c, 700, 1380, 1.2, ARJUN, dict(face=1, expr='shock', arm_r='point', arm_l='hip'), 0.3)
c.rectangle(0,0,W,250); c.set_source_rgba(0,0,0,1); c.fill()
text(c,'WHO STOLE THE SWORD?', W/2, 175, 132, '#ffffff')
s.write_to_png('/home/claude/det/out/thumb_full.png')
