import sys; sys.path.insert(0,'/home/claude/long')
from longvid import *
clist = cases.CASES; N = len(clist)
beats = make_beats(clist)
tl = Timeline(beats, lead=0.15, gap=0.12, think=0, spk=NARR)
total = tl.end + 0.5
draw = draw_factory(tl, clist, N)
mode = sys.argv[1]
OUT = '/home/claude/long/out'; os.makedirs(OUT, exist_ok=True)
if mode == 'stills':
    ids = ['t1','t2','c0_a','c0_s0','c0_s2','c0_r','c0_p','c0_x0','c0_x2','c0_z','c3_a','c4_s1','c7_x2','c8_z','e1','c5_r']
    for i, k in enumerate(ids):
        b = tl.by[k]; tt = b['t1'] - 0.1 if b['scene'] != 'pause' else b['t1'] + 2.3
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); draw(ctx, tt); surf.write_to_png(f'{OUT}/s{i:02d}.png')
elif mode == 'audio':
    build_mix(f'{OUT}/long.wav', tl, sfx_list(tl), total)
    import json
    ch = [(0, 'Intro')] + [(tl.by[f'c{i}_a']['t0'], f"Case {i+1}: {c['place']} ({'murder' if c['kind']=='murder' else c['kind']})") for i, c in enumerate(clist)] + [(tl.by['e1']['t0'], 'Your score')]
    json.dump(dict(total=total, ch=ch, ans=[(c['place'], c['ans'], c['why_en']) for c in clist]), open(f'{OUT}/meta.json','w'))
elif mode == 'video':
    part, nparts = int(sys.argv[2]), int(sys.argv[3])
    nf = int(total*30); a = nf*part//nparts; z = nf*(part+1)//nparts
    cmd = ['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgra','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-preset','veryfast',
           '-b:v','1000k','-maxrate','1600k','-bufsize','3200k','-pix_fmt','yuv420p',f'{OUT}/part{part}.mp4']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    for i in range(a, z):
        ctx.save(); draw(ctx, i/30); ctx.restore(); surf.flush(); p.stdin.write(surf.get_data())
        if i % 300 == 0: print(part, i, z, flush=True)
    p.stdin.close(); p.wait()
