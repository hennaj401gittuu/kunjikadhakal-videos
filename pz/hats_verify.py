# 3 prisoners in a line facing a wall: Ravi (back) sees Sunil+Kunjan, Sunil sees Kunjan, Kunjan sees nothing.
# 5 hats: 3 White, 2 Black; 1 on each head, 2 hidden. Ravi: don't know. Sunil: don't know. Kunjan: knows.
import itertools
worlds = set()
for c in itertools.permutations('WWWBB', 3): worlds.add(c)  # (ravi, sunil, kunjan)
def knows(worlds, i, sees, w):
    cand = {v[i] for v in worlds if all(v[j] == w[j] for j in sees)}
    return len(cand) == 1
w1 = {w for w in worlds if not knows(worlds, 0, (1, 2), w)}   # Ravi doesn't know
w2 = {w for w in w1 if not knows(w1, 1, (2,), w)}             # Sunil doesn't know
w3 = {w for w in w2 if knows(w2, 2, (), w)}                    # Kunjan knows
ans = {w[2] for w in w3}
print(sorted(worlds), sorted(w1), sorted(w2), ans)
assert w3 == w2 and ans == {'W'}, ans
# without Sunil's statement, Kunjan could not know (both statements are needed)
assert not all(knows(w1, 2, (), w) for w in w1)
print('ANSWER: WHITE (unique)')
