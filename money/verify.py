from fractions import Fraction as F
# 1 goat: track cash
cash=0; cash-=6000; cash+=7000; cash-=8000; cash+=9000; assert cash==2000
# 2 lodge: every rupee
paid=3000; room=2500; boy=200; ret=300; assert paid==room+boy+ret; assert 3*900==room+boy  # nothing missing
# 3 saree
s1=1000*0.6; s2=1000*0.8*0.8; assert (s1,s2)==(600,640) and s2-s1==40
# 4 puttu: Babu 5, Shaji 3, 8 shared by 3, Joseph pays 80
each=F(8,3); gb=5-each; gs=3-each; rate=F(80)/each
sols=[(gb*rate,gs*rate)]; assert sols==[(70,10)]
# 5 tea & vada (in paise): v + t = 2200, t - v = 2000
sol=[(v,2200-v) for v in range(0,2201) if (2200-v)-v==2000]; assert sol==[(100,2100)]
# 6 soda: 9 bought, 3 empties -> 1 soda, no borrowing
full,empty,drunk=9,0,0
while full:
    drunk+=full; empty+=full; full=empty//3; empty%=3
assert drunk==13
# 7 machines: rate 1 packet per machine per 5 min
rate=F(5,5*5); t=F(100)/(100*rate); assert t==5
# 8 age
a,k=6,3; assert 40-(a-k)==37
# 9 calendar
days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']; assert days[(1+100)%7]=='Thu'
print('all unique answers verified')
