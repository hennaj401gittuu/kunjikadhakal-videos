"""Cover image = frame 0 (title card over the complete opening scene). Run after render.py+audio.py -> cover.jpg"""
import subprocess
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0", "-i", "short.mp4", "-frames:v", "1", "-q:v", "2", "cover.jpg"], check=True)
print("COVER_DONE cover.jpg")
