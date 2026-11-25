import sys
sys.path.insert(0, '/home/claude/pz')
from wd import build

CASE = dict(
    suspects=[
        dict(name='Mathew', robe='#2f6fd6', stmt=('did', 'Sindhu'), short='"Sindhu did it!"', mood='sus', cap='bald'),
        dict(name='Kunjali', robe='#27a85a', stmt=('liar', 'Mathew'), short='"Mathew is lying."', mood='sus', cap='kufi'),
        dict(name='Sindhu', robe='#c2407a', stmt=('not', 'Sindhu'), short='"I didn\'t do it."', mood='sus', stache=False, cap='bun'),
    ],
    beats=[
        dict(id='h1', scene='lineup', fail='99% FAIL', ml='ട്രെയിനിലെ കൊലയാളി ആരാണ്? തൊണ്ണൂറ്റൊമ്പത് ശതമാനം പേരും തോൽക്കും!',
             en='Who is the *KILLER* on the train? *99%* fail!'),
        dict(id='h2', scene='place', place='train', ml='രാത്രി, മലബാർ എക്സ്പ്രസ്സിന്റെ സ്ലീപ്പർ കോച്ചിൽ, ഒരു ബിസിനസ്സുകാരനെ മരിച്ച നിലയിൽ കണ്ടെത്തി.',
             en='A businessman was found *dead* in a sleeper coach of the *night train.*'),
        dict(id='h3', scene='police', talking=True, ml='റെയിൽവേ പോലീസ് മൂന്നു പേരെ ചോദ്യം ചെയ്തു.', en='Railway police questioned *three* people.'),
        dict(id='h4', scene='rule', ml='പോലീസിന് ഒരു കാര്യം മാത്രം ഉറപ്പാണ്.', en='Police are sure of just *one* thing...'),
        dict(id='h5', scene='rule', truth=True, truth_dt=0.5, lies=True, lies_dt=2.0,
             ml='ഇവരിൽ ഒരാൾ മാത്രമേ സത്യം പറയുന്നുള്ളൂ. ബാക്കി രണ്ടുപേരും കള്ളം പറയുന്നു.',
             en='Only *ONE* of them tells the *truth.* The other two are *LYING.*'),
        dict(id='h6', scene='solo', who=0, pose='point', mood='angry', bubble='SINDHU DID IT!', bubble_col='#e8283c',
             ml='ടിക്കറ്റ് പരിശോധകൻ മാത്യു പറഞ്ഞു, സിന്ധുവാണ് കൊന്നത്.', en='Ticket checker *Mathew* said: "*Sindhu* did it!"'),
        dict(id='h7', scene='solo', who=1, pose='shrug', mood='sus', bubble='MATHEW IS LYING!',
             ml='ചായക്കാരൻ കുഞ്ഞാലി പറഞ്ഞു, മാത്യു കള്ളം പറയുകയാണ്.', en='Tea seller *Kunjali* said: "*Mathew* is lying."'),
        dict(id='h8', scene='solo', who=2, pose='chest', mood='scared', bubble='NOT ME!',
             ml='അടുത്ത ബർത്തിലെ യാത്രക്കാരി സിന്ധു പറഞ്ഞു, ഞാനല്ല കൊന്നത്.', en='Passenger *Sindhu* said: "I *didn\'t* do it."'),
        dict(id='h9', scene='summary', ml='ഒരാൾ മാത്രം സത്യം. ഒരാൾ മാത്രം കൊലയാളി. ആരാണത്?', en='Only one tells the *truth.* Who is the *killer?*'),
        dict(id='h10', scene='summary', typing=True, follow=True, type_dt=0.3,
             ml='ഉത്തരം കമന്റിൽ ടൈപ്പ് ചെയ്യൂ. ഉത്തരം അറിയാൻ ഫോളോ ചെയ്യൂ!',
             en='Type *ANSWER* in the comments! *Follow* for the answer!', post=1.5),
    ])

if __name__ == '__main__':
    tl, ans = build(CASE, '/home/claude/pz/out', 'Train_Mystery_Short', stills='stills' in sys.argv)
    print('TOTAL', round(tl.end, 1), 'ANSWER', ans)
