import sys; sys.path.insert(0,'/home/claude/pz'); sys.path.insert(0,'/home/claude')
from pz import voice, wav_dur
from script import B, SPK
tot = 0.6
for b in B:
    w = voice(b['ml'], SPK[b['spk']]); d = wav_dur(w)
    tot += d + b.get('timer', 0) + b.get('post', 0) + (0.95 if (b.get('timer') or b.get('ans')) else 0.18)
print('EST TOTAL', round(tot, 1), len(B))
