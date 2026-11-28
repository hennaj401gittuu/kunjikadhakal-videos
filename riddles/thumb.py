"""Thumbnail for Hard Malayalam Riddles #1: black top bar + jewel-shop scene with 3 expressive characters."""
import sys, math, cairo
sys.argv = ['thumb', 'x']
import importlib.util
spec = importlib.util.spec_from_file_location('rv', '/home/claude/riddles/rv.py'); rv = importlib.util.module_from_spec(spec); spec.loader.exec_module(rv)
from chars import human, ARJUN, MEENU, JOSE
W, H = 1920, 1080
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
ctx.save(); ctx.translate(-80, 60); ctx.scale(1.08, 1.08)
rv.rbgs.paint(ctx, 'jewel')
human(ctx, 1180, 1180, 0.95, JOSE, dict(face=-1, expr='smug', arm_l='hip', arm_r='down'), 1.0)
rv.paint_clip(ctx, 'jewel', 762)
rv.balance(ctx, 760, 790, 0.95, 0.8, 3, 3)
for k in range(3): rv.coin(ctx, 960 + k*70, 770, 34, glint=1.6 + k)
rv.glow(ctx, 520, 500, 160, (1, 0.9, 0.3), 0.7)
ctx.restore()
human(ctx, 270, 1200, 0.88, ARJUN, dict(face=1, expr='think', arm_l='chin', arm_r='down'), 1.0)
human(ctx, 1420, 1200, 0.92, MEENU, dict(face=-1, expr='shock', arm_l='chips', arm_r='up'), 1.0)
rv.ftext(ctx, '?', 1720, 760, 260, '#ffd23f')
# top black bar
ctx.rectangle(0, 0, W, 300); ctx.set_source_rgba(0, 0, 0, 1); ctx.fill()
rv.ftext(ctx, 'HARD RIDDLES #1', W/2, 215, 190, '#ffffff', outline_=False)
rv.tagb(ctx, 1220, 390, 'ONLY 6% SOLVE', 1.0, '#1a1a1a', bg='#ffd23f', size=84)
surf.write_to_png('/home/claude/riddles/out/thumb.png')
from PIL import Image
im = Image.open('/home/claude/riddles/out/thumb.png').convert('RGB').resize((1280, 720), Image.LANCZOS)
im.save('/home/claude/riddles/out/KP_Hard_Malayalam_Riddles_1_thumb.jpg', quality=90)
im.resize((320, 180), Image.LANCZOS).save('/home/claude/riddles/out/thumb_small.png')
