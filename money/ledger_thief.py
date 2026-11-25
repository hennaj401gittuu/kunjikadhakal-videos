# Ledger for "The Thief Came Back" (Pappan's shop). Values in rupees; rice valued at its price 600.
P = dict(cash=5000, rice=600); L = dict(cash=3000); T = dict(cash=0, rice=0)
start = {k: dict(v) for k, v in (('P', P), ('L', L), ('T', T))}
def worth(x): return x['cash'] + x.get('rice', 0)
# night: thief steals a 1000 note from Pappan's cash box
P['cash'] -= 1000; T['cash'] += 1000
# morning: thief buys rice worth 600 with the same 1000 note
T['cash'] -= 1000; P['cash'] += 1000
# Pappan has no change: gives the 1000 note to Leela, gets ten 100s
P['cash'] -= 1000; L['cash'] += 1000; L['cash'] -= 1000; P['cash'] += 1000
# Pappan gives rice + 400 change
P['rice'] -= 600; T['rice'] += 600; P['cash'] -= 400; T['cash'] += 400
# Leela spots the pen mark: it's the stolen note (a real note, so Leela is fine). Thief gone.
lossP = worth(start['P']) - worth(P); dL = worth(L) - worth(start['L']); gT = worth(T) - worth(start['T'])
print('Pappan loss', lossP, 'Leela change', dL, 'thief gain', gT)
assert lossP == 1000 and dL == 0 and gT == 1000
