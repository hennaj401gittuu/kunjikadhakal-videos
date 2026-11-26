"""Voice for each beat line (Kokoro). Run in the folder holding script.py -> vo/NNN.wav + vo/NNN.json"""
import soundfile as sf, numpy as np, re, json, os, sys
ENG = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ENG)
from iso import *  # noqa
from kokoro_onnx import Kokoro
exec(open("script.py").read())
MD = os.environ.get("MW_MODELS", os.path.expanduser("~/mwmodels") )
VOICE = globals().get("VOICE", "am_michael")
SPEED = globals().get("SPEED", 1.08)
k = Kokoro(f"{MD}/kokoro-v1.0.onnx", f"{MD}/voices-v1.0.bin")
os.makedirs("vo", exist_ok=True)
SR = 24000
for i, b in enumerate(B):
    out = f"vo/{i:03d}.wav"
    if os.path.exists(f"vo/{i:03d}.json"):
        continue
    sents = [x.strip() for x in re.split(r'(?<=[.!?])\s+', b["line"]) if x.strip()]
    pieces, st, cur = [], [], 0.0
    for s in sents:
        spoken = s.replace("°C", " degrees").replace("%", " percent")
        a, sr = k.create(spoken, voice=VOICE, speed=SPEED, lang="en-us")
        a = np.asarray(a, dtype=np.float32)
        nz = np.where(np.abs(a) > 0.01)[0]
        if len(nz):
            a = a[max(0, nz[0] - 240):nz[-1] + 1800]
        st.append([round(cur, 3), round(cur + len(a) / SR, 3), s])
        pieces.append(a)
        gap = np.zeros(int(SR * 0.22), np.float32); pieces.append(gap)
        cur += len(a) / SR + 0.22
    aud = np.concatenate(pieces)
    sf.write(out, aud, SR)
    json.dump({"dur": round(len(aud) / SR, 3), "sents": st}, open(f"vo/{i:03d}.json", "w"))
    print(i, round(len(aud) / SR, 2), flush=True)
tot = sum(json.load(open(f"vo/{i:03d}.json"))["dur"] for i in range(len(B)))
print("TTS_DONE", round(tot, 1), "s of speech")
