import soundfile as sf, numpy as np, re, json, subprocess, os, sys
from kokoro_onnx import Kokoro
exec(open("script.py").read())
import os
MD=os.environ.get("MW_MODELS", os.path.expanduser("~/mwmodels"))
k=Kokoro(f"{MD}/kokoro-v1.0.onnx",f"{MD}/voices-v1.0.bin")
os.makedirs("vo",exist_ok=True)
SR=24000; P=0.93
def lower(a):
    # pitch down via resample trick with ffmpeg
    sf.write("/tmp/x.wav",a,SR)
    subprocess.run(["ffmpeg","-v","error","-y","-i","/tmp/x.wav","-af",f"asetrate={int(SR*P)},aresample={SR},atempo={1/P:.5f}","/tmp/y.wav"],check=True)
    b,_=sf.read("/tmp/y.wav"); return b
meta=[]
for i,(sc,p,t) in enumerate(S):
    out=f"vo/{i:03d}.wav"
    if not t: meta.append({"i":i,"dur":0,"sents":[]}); continue
    if os.path.exists(out+".json"):
        meta.append(json.load(open(out+".json"))); continue
    sents=[x.strip() for x in re.split(r'(?<=[.!?:])\s+(?=[A-Z0-9])',t) if x.strip()]
    pieces=[];cur=0.0;st=[]
    for s_ in sents:
        a,sr=k.create(s_,voice="am_michael",speed=0.9,lang="en-us")
        a=np.asarray(a,dtype=np.float32)
        # trim silence
        nz=np.where(np.abs(a)>0.01)[0]
        if len(nz): a=a[max(0,nz[0]-240):nz[-1]+2400]
        a=lower(a)
        st.append([round(cur,3),round(cur+len(a)/SR,3),s_])
        pieces.append(a); gap=np.zeros(int(SR*0.38)); pieces.append(gap); cur+=len(a)/SR+0.38
    aud=np.concatenate(pieces)
    sf.write(out,aud,SR)
    m={"i":i,"dur":round(len(aud)/SR,3),"sents":st}
    json.dump(m,open(out+".json","w")); meta.append(m)
    print(i,m["dur"],flush=True)
json.dump(meta,open("vo/meta.json","w"))
print("DONE",sum(m["dur"] for m in meta)/60)
