import sys
sys.path.insert(0, '/home/claude/pz')
from wd import build

CASE = dict(
    suspects=[
        dict(name='Rajan', robe='#2f6fd6', stmt=('not', 'Shibu'), short='"It wasn\'t Shibu."', mood='sus'),
        dict(name='Shibu', robe='#27a85a', stmt=('did', 'Faizal'), short='"Faizal did it!"', mood='sus', stache=False),
        dict(name='Faizal', robe='#b3263f', stmt=('not', 'Faizal'), short='"I didn\'t do it."', cap='kufi', mood='sus'),
    ],
    beats=[
        dict(id='h1', scene='lineup', fail='99% FAIL', ml='കൊലയാളി ആരാണ്? തൊണ്ണൂറ്റൊമ്പത് ശതമാനം പേരും ഇത് തെറ്റിക്കും!',
             en='Who is the *KILLER?* *99%* get this wrong!'),
        dict(id='h2', scene='place', place='houseboat', ml='ആലപ്പുഴയിലെ ഒരു ഹൗസ്ബോട്ടിൽ, ഒരു ടൂറിസ്റ്റിനെ മരിച്ച നിലയിൽ കണ്ടെത്തി.',
             en='A tourist was found *dead* on a houseboat in *Alappuzha.*'),
        dict(id='h3', scene='police', talking=True, ml='പോലീസ് മൂന്നു പേരെ ചോദ്യം ചെയ്തു.', en='Police questioned *three* people.'),
        dict(id='h4', scene='rule', ml='പോലീസിന് ഒരു കാര്യം ഉറപ്പാണ്.', en='Police are sure of *one* thing...'),
        dict(id='h5', scene='rule', truth=True, truth_dt=0.5, lies=True, lies_dt=2.0,
             ml='ഇവരിൽ ഒരാൾ മാത്രമേ സത്യം പറയുന്നുള്ളൂ. ബാക്കി രണ്ടുപേരും കള്ളം പറയുന്നു.',
             en='Only *ONE* of them tells the *truth.* The other two are *LYING.*'),
        dict(id='h6', scene='solo', who=0, pose='shrug', mood='sus', bubble='NOT SHIBU!', ml='പാചകക്കാരൻ രാജൻ പറഞ്ഞു, ഷിബു അല്ല കൊന്നത്.',
             en='The cook *Rajan* said: "It wasn\'t *Shibu.*"'),
        dict(id='h7', scene='solo', who=1, pose='point', mood='angry', bubble='FAIZAL DID IT!', bubble_col='#e8283c',
             ml='ബോട്ട് ഡ്രൈവർ ഷിബു പറഞ്ഞു, ഫൈസൽ ആണ് കൊന്നത്.', en='Boat driver *Shibu* said: "*Faizal* did it!"'),
        dict(id='h8', scene='solo', who=2, pose='chest', mood='scared', bubble='NOT ME', ml='ഗൈഡ് ഫൈസൽ പറഞ്ഞു, ഞാനല്ല കൊന്നത്.',
             en='The guide *Faizal* said: "I didn\'t do it."'),
        dict(id='h9', scene='summary', ml='ഒരാൾ മാത്രം സത്യം. ഒരാൾ മാത്രം കൊലയാളി.', en='Only one tells the *truth.* Only one is the *killer.*'),
        dict(id='h10', scene='summary', typing=True, follow=True, type_dt=0.3,
             ml='അറിയാമെങ്കിൽ കമന്റ് ചെയ്യൂ. അറിയില്ലെങ്കിൽ ഫോളോ ചെയ്ത് ഉത്തരം കാണൂ!',
             en='Know it? *Comment* the answer. Not sure? *Follow* to see it!', post=1.2),
    ])

if __name__ == '__main__':
    tl, ans = build(CASE, '/home/claude/pz/out', 'Houseboat_Mystery_Short', stills='stills' in sys.argv)
    print('TOTAL', round(tl.end, 1), 'ANSWER', ans)
