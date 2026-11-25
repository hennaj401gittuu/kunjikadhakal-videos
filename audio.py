import numpy as np, wave
from scenes import SCENES
SR=44100
starts={}; t0=0
for n,fn,d,fi,fo in SCENES: starts[n]=t0; t0+=d
TOT=t0; N=int(TOT*SR)+SR
mus=np.zeros(N); fx=np.zeros(N)
rng=np.random.default_rng(1)
def mtof(m): return 440*2**((m-69)/12)
def add(buf,t,sig,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); 
    if i<N: buf[i:j]+=sig[:j-i]*g
def pluck(f,dur=0.6,bright=0.5):
    n=int(dur*SR); L=int(SR/f); b=rng.uniform(-1,1,L); out=np.zeros(n)
    for i in range(n):
        out[i]=b[i%L]; b[i%L]=0.5*(b[i%L]+b[(i+1)%L])*(0.996)
    return out
_pc={}
def pl(m,dur=0.5):
    k=(m,dur)
    if k not in _pc: _pc[k]=pluck(mtof(m),dur)
    return _pc[k]
def bell(f,dur=1.2):
    t=np.arange(int(dur*SR))/SR
    return (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*6)+0.2*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*10))*np.exp(-t*3.5)
def bassn(f,dur):
    t=np.arange(int(dur*SR))/SR; e=np.minimum(1,t*80)*np.exp(-t*3)
    return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*e
def noise(dur,decay=20,lp=0.0):
    n=int(dur*SR); x=rng.uniform(-1,1,n)
    if lp>0:
        y=np.zeros(n); a=lp
        for i in range(1,n): y[i]=y[i-1]+(1-a)*(x[i]-y[i-1])
        x=y*3
    t=np.arange(n)/SR; return x*np.exp(-t*decay)
# --- music: 112 bpm, C major I-vi-IV-V
bpm=112; beat=60/bpm
chords=[(48,[60,64,67]),(45,[57,60,64]),(41,[53,57,60]),(43,[55,59,62])]
mel=[72,74,76,79, 76,74,72,74, 76,76,74,72, 74,72,67,69,  72,74,76,79, 81,79,76,74, 72,74,76,74, 72,71,72,-1]
nb=int(TOT/beat)+1
for b in range(nb):
    t=b*beat; bar=b//4; ch=chords[bar%4]
    if t>TOT-0.5: break
    if b%2==0: add(mus,t,bassn(mtof(ch[0]-12),beat*1.8),0.35)
    # off-beat chord plucks
    for k,m in enumerate(ch[1]): add(mus,t+beat/2+k*0.012,pl(m,0.4),0.10)
    # melody in eighths for first half of phrase
    mi=(b*2)%len(mel)
    for h in range(2):
        m=mel[(b*2+h)%len(mel)]
        if m>0 and (bar%8)<8: add(mus,t+h*beat/2,pl(m,0.45),0.22 if h==0 else 0.16)
    if b%8==0: add(mus,t,bell(mtof(ch[1][2]+12)),0.06)
    # soft shaker
    for h in range(2): add(mus,t+h*beat/2,noise(0.05,90),0.035 if h else 0.02)
# --- sfx
s=starts
for k in range(14): add(fx,s['room']+0.3+k*0.18,pl(84+(k%2)*3,0.15),0.12)   # tiptoe
for k in range(8): add(fx,s['room']+4.8+k*0.15,pl(86-(k%2)*2,0.12),0.12)
add(fx,s['room']+3.8,bell(1046,0.5)*0.5,0.25)
add(fx,s['room']+3.0,pl(91,0.3),0.25)
for k in range(5): add(fx,s['home']+1.6+k*0.12,bell(mtof(76+[0,4,7,12,16][k]),0.6),0.12)
for k in range(8): add(fx,s['chop']+0.6+(k+0.5)*0.35,noise(0.08,60,0.3),0.6)
add(fx,s['egg']+1.15,noise(0.12,40,0.0),0.5); add(fx,s['egg']+2.1,noise(0.15,25,0.7),0.4)
def pour(t,d,lp=0.85,g=0.25):
    n=noise(d,0,lp); env=np.minimum(1,np.arange(len(n))/(0.1*SR))*np.minimum(1,(len(n)-np.arange(len(n)))/(0.15*SR)); add(fx,t,n*env,g)
pour(s['sugar']+1.35,1.4); pour(s['flour']+1.25,1.3,0.9,0.3); add(fx,s['flour']+1.6,noise(0.6,4,0.95),0.4)
for k in range(int(2.4/0.29)): add(fx,s['whisk']+1.3+k*0.29,noise(0.12,25,0.5),0.25)
add(fx,s['whisk']+0.85,noise(0.1,30,0.8),0.5)
for k in range(14): add(fx,s['stir']+0.8+k*0.06,pl(96+(k%3),0.08),0.08)
for k in range(6): add(fx,s['scoop']+0.4+(k+1)*0.55,pl(79+k*2,0.25),0.2)
add(fx,s['oven']+4.1,bell(1568,2.0),0.35); add(fx,s['oven']+4.1,bell(2093,2.0),0.2)
for k in range(5): add(fx,s['out']+0.3+k*0.4,bell(mtof(84+[0,4,7,4,12][k]),0.5),0.06)
for k in range(12):
    for i in range(2): add(fx,s['serve']+3.9+i*0.25+k*0.35,noise(0.07,50,0.4),0.3)
for k in range(4): add(fx,s['serve']+4.4+k*0.1,bell(mtof(79+[0,4,7,12][k]),0.8),0.12)
for k in range(4): add(fx,s['serve']+6.4+k*0.18,bell(mtof(72+[0,4,7,12][k]),1.5),0.12)
out=mus*0.9+fx
# fade end
fe=int(1.2*SR); e=int(TOT*SR); out[e-fe:e]*=np.linspace(1,0,fe); out[e:]=0
out=out[:e]; out/=np.max(np.abs(out))*1.12
st=np.stack([out,out],1)
with wave.open('audio.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())
print('ok',TOT)
