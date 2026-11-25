import sys, subprocess, os
from scenes import *
FPS=30
def render(name):
    for n,fn,d,fi,fo in SCENES:
        if n==name: break
    nf=int(round(d*FPS)); tmp=f'parts/{name}.tmp.mp4'
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgra','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-crf','18','-preset','veryfast','-pix_fmt','yuv420p','-r',str(FPS),tmp],stdin=subprocess.PIPE)
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s)
    for i in range(nf):
        c.save(); c.set_operator(cairo.OPERATOR_SOURCE); c.set_source_rgb(0,0,0); c.paint(); c.restore()
        c.save(); frame(c,n,fn,i/FPS,d,fi,fo); c.restore()
        s.flush(); p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    if p.wait()==0: os.replace(tmp,f'parts/{name}.mp4'); print('done',name,flush=True)
os.makedirs('parts',exist_ok=True)
for n in sys.argv[1:]: render(n)
