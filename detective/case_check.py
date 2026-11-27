"""Detective Arjun ep: The Palace Sword - check the clues leave exactly ONE suspect."""
SUS = {
 'Velayudhan (WATCHMAN)':  dict(key=True,  shoe='rubber chappal', heel=False, height_in=65, alibi_ok=True),
 'Shantha (CLEANER)':      dict(key=False, shoe='flat sandal',    heel=False, height_in=60, alibi_ok=True),
 'Faizal (ELECTRICIAN)':   dict(key=False, shoe='zigzag work boot', heel=False, height_in=68, alibi_ok=True),
 'Dr. Ravi Menon (CURATOR)': dict(key=True, shoe='leather shoe', heel=True, height_in=73, alibi_ok=False),
}
# reach ~ 1.33 x height; camera at 8 ft = 96 in, unreachable without ladder unless reach >= 96 -> height >= 72 in
CLUES = {
 'C1 lock opened with key (no damage)': lambda s: s['key'],
 'C2 footprint: smooth leather sole + separate heel': lambda s: s['shoe'] == 'leather shoe' and s['heel'],
 'C3 camera at 8 ft turned by hand, ladder untouched': lambda s: s['height_in']*1.33 >= 96,
 'C4 alibi receipt dated 26/11 (yesterday)': lambda s: not s['alibi_ok'],
}
left = [n for n, s in SUS.items() if all(f(s) for f in CLUES.values())]
for c, f in CLUES.items(): print(c, '->', [n for n, s in SUS.items() if f(s)])
print('FITS ALL:', left); assert len(left) == 1
# shoe + height alone must also be unique (core physical clues)
assert len([n for n, s in SUS.items() if CLUES['C2 footprint: smooth leather sole + separate heel'](s) and CLUES['C3 camera at 8 ft turned by hand, ladder untouched'](s)]) == 1
