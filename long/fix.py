import itertools, sys; sys.path.insert(0,'/home/claude/pz')
from wd import solve, evaluate
from cases import CASES, SHORT
def opts(me, names):
    o=[]
    for n in names: o+= [('did',n),('not',n)]
    for n in names:
        if n!=me: o+=[('liar',n),('honest',n)]
    return o
for c in CASES:
    names=[s[0] for s in c['sus']]; cur=[s[6] for s in c['sus']]
    if len(solve(names,dict(zip(names,cur)),c['n_true']))==1: print(c['place'],'OK',cur); continue
    best=None
    for combo in itertools.product(*[opts(n,names) for n in names]):
        st=dict(zip(names,combo))
        if any(None in evaluate(names,st,k) for k in names): continue
        if len(solve(names,st,c['n_true']))!=1: continue
        if len(set(x[0] for x in combo))<2 or len(set(combo))<3 or any(x==('did',n) for x,n in zip(combo,names)): continue
        d=sum(a!=b for a,b in zip(combo,cur))
        if best is None or d<best[0]: best=(d,combo)
    print(c['place'],'FIX',best, solve(names,dict(zip(names,best[1])),c['n_true']))
