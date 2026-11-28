"""Checks every answer in Hard Malayalam Riddles #1."""
from fractions import Fraction as F
from itertools import product
from collections import deque
# R1 coconuts: buy 3 for 100, sell 2 for 100 -> how many to sell for 500 profit
cost, sell = F(100, 3), F(100, 2); n = 500/(sell - cost); assert n == 30, n
# R2 clock angle at 3:15
h = 3*30 + 15*0.5; m = 15*6; assert abs(h - m) == 7.5
# R3 boat: man + dog, hen, rice; dog eats hen, hen eats rice when man absent; boat holds man + 1
items = ('dog', 'hen', 'rice')
def safe(side):
    return not ({'dog', 'hen'} <= side or {'hen', 'rice'} <= side)
start = (frozenset(items), 0); goal = (frozenset(), 1)
dist = {start: 0}; q = deque([start])
while q:
    left, man = q.popleft()
    here = left if man == 0 else frozenset(items) - left
    for take in [None] + list(here):
        nl = set(left)
        if take:
            if man == 0: nl.discard(take)
            else: nl.add(take)
        nl = frozenset(nl); nm = 1 - man
        unattended = nl if nm == 1 else frozenset(items) - nl
        if not safe(set(unattended)): continue
        s = (nl, nm)
        if s not in dist: dist[s] = dist[(left, man)] + 1; q.append(s)
assert dist[goal] == 7, dist[goal]
# R4 laddoo jars: jars 1..5, take k from jar k, normal 50 g, heavy 60 g -> scale 790 -> jar 4; every jar gives a unique reading
reads = {sum(k*(60 if k == j else 50) for k in range(1, 6)): j for j in range(1, 6)}
assert len(reads) == 5 and reads[790] == 4
# R5 trains: 150 km apart, 40 and 35 km/h, parrot 60 km/h
tmeet = F(150, 40 + 35); assert tmeet == 2 and 60*tmeet == 120
# R6 9 coins, one lighter, balance: 2 weighings suffice, 1 does not
def solvable(cands, k):
    if len(cands) <= 1: return True
    if k == 0: return False
    coins = range(9)
    # try all splits: choose left set and right set of equal size
    from itertools import combinations
    for sz in range(1, 5):
        for L in combinations(coins, sz):
            rest = [c for c in coins if c not in L]
            for R in combinations(rest, sz):
                out = {'<': [], '>': [], '=': []}
                for c in cands:
                    out['<' if c in L else '>' if c in R else '='].append(c)  # left lighter if fake on left
                if max(len(v) for v in out.values()) == len(cands): continue
                if all(solvable(v, k - 1) for v in out.values()): return True
    return False
assert not solvable(list(range(9)), 1)
assert solvable(list(range(9)), 2)
print('ALL ANSWERS VERIFIED: 30 coconuts; 7.5 deg; 7 trips; jar 4 (790 g); 120 km; 2 weighings')
