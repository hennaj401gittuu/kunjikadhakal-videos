import sys; sys.path.insert(0,'/home/claude/pz'); sys.path.insert(0,'/home/claude')
from pz import voice, wav_dur
from script import B, SPK
tot=0
for x in B:
    p=voice(x['ml'], SPK[x['spk']]); d=wav_dur(p); tot+=d+0.22+x.get('timer',0)+x.get('post',0)+(0.6 if x.get('timer') or x.get('ans') else 0)
    print(x['id'], x['spk'], round(d,1), flush=True)
print('EST TOTAL', round(tot,1), len(B))
