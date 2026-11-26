# Ledger for "The ₹1000 That Paid Everyone" (Hotel Jose street). Net worth = cash + money owed to you - money you owe.
cash = dict(J=2000, H=2000, L=2000, T=1000)
debt = {('J','H'):1000, ('H','L'):1000, ('L','J'):1000}   # (debtor, creditor)
def worth(p): return cash[p] + sum(v for (d,c),v in debt.items() if c==p) - sum(v for (d,c),v in debt.items() if d==p)
start = {p: worth(p) for p in cash}; cash0 = dict(cash)
def pay(a,b,x): cash[a]-=x; cash[b]+=x
pay('T','J',1000)                      # traveller's advance (Jose now holds it for him)
adv = 1000                              # Jose owes the traveller his advance back until he keeps the room
pay('J','H',1000); debt[('J','H')]=0   # Jose clears his debt to Hamsa
pay('H','L',1000); debt[('H','L')]=0   # Hamsa clears his debt to Leela
pay('L','J',1000); debt[('L','J')]=0   # Leela clears her meal bill with Jose
pay('J','T',1000); adv = 0              # traveller dislikes the room, takes advance back
earned = sum(worth(p)-start[p] for p in 'JHL')
print('worth change', {p: worth(p)-start[p] for p in cash}, 'cash change', {p: cash[p]-cash0[p] for p in cash}, 'debts', debt)
assert earned == 0 and all(cash[p]==cash0[p] for p in cash) and all(v==0 for v in debt.values())
print('ANSWER: earned ₹0 (all three debts cleared)')
