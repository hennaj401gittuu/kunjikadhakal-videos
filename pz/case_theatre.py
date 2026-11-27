import sys
sys.path.insert(0, '/home/claude/pz')
from wd import build

TL, LL = '2 TRUTHS ✓', '1 LIE ✕'
CASE = dict(
    n_true=2,
    suspects=[
        dict(name='Prakashan', robe='#2f6fd6', stmt=('honest', 'Jithin'), short='"Jithin is telling the truth."', mood='sus', cap='bald'),
        dict(name='Fathima', robe='#c2407a', stmt=('did', 'Prakashan'), short='"Prakashan did it!"', mood='sus', stache=False, cap='bun'),
        dict(name='Jithin', robe='#27a85a', stmt=('not', 'Fathima'), short='"Fathima didn\'t do it."', mood='sus', stache=False),
    ],
    beats=[
        dict(id='h1', scene='lineup', fail='99% FAIL', ml='തിയേറ്ററിലെ കൊലയാളി ആരാണ്? തൊണ്ണൂറ്റൊമ്പത് ശതമാനം പേരും ഇത് തെറ്റിക്കും!',
             en='Who is the *KILLER* in the theatre? *99%* get this wrong!'),
        dict(id='h2', scene='place', place='theatre', ml='സെക്കൻഡ് ഷോ കഴിഞ്ഞപ്പോൾ, സ്റ്റാർ സിനിമാസിൽ ഒരു സിനിമാ നിർമ്മാതാവിനെ മരിച്ച നിലയിൽ കണ്ടെത്തി.',
             en='After the *night show,* a film *producer* was found *dead* at Star Cinemas.'),
        dict(id='h3', scene='police', talking=True, ml='പോലീസ് മൂന്നു പേരെ ചോദ്യം ചെയ്തു.', en='Police questioned *three* people.'),
        dict(id='h4', scene='rule', truth_label=TL, lies_label=LL, ml='പോലീസിന് ഒരു കാര്യം മാത്രം ഉറപ്പാണ്.', en='Police are sure of just *one* thing...'),
        dict(id='h5', scene='rule', truth_label=TL, lies_label=LL, truth=True, truth_dt=0.5, lies=True, lies_dt=1.4,
             ml='ഇവരിൽ ഒരാൾ മാത്രമേ കള്ളം പറയുന്നുള്ളൂ. ബാക്കി രണ്ടുപേരും സത്യം പറയുന്നു.',
             en='Only *ONE* of them is *LYING.* The other two tell the *truth.*'),
        dict(id='h6', scene='solo', who=0, pose='chest', mood='sus', bubble='JITHIN TELLS THE TRUTH!', bubble_col='#1a1a1a',
             ml='പ്രൊജക്ടർ ഓപ്പറേറ്റർ പ്രകാശൻ പറഞ്ഞു, ജിതിൻ പറയുന്നത് സത്യമാണ്.', en='Projector operator *Prakashan* said: "*Jithin* is telling the truth."'),
        dict(id='h7', scene='solo', who=1, pose='point', mood='angry', bubble='PRAKASHAN DID IT!', bubble_col='#e8283c',
             ml='ടിക്കറ്റ് കൗണ്ടറിലെ ഫാത്തിമ പറഞ്ഞു, പ്രകാശനാണ് കൊന്നത്.', en='Ticket clerk *Fathima* said: "*Prakashan* did it!"'),
        dict(id='h8', scene='solo', who=2, pose='shrug', mood='sus', bubble="IT WASN'T FATHIMA!",
             ml='പുതിയ നടൻ ജിതിൻ പറഞ്ഞു, ഫാത്തിമയല്ല കൊന്നത്.', en='Young actor *Jithin* said: "*Fathima* didn\'t do it."'),
        dict(id='h9', scene='summary', rule_label='ONLY 1 IS LYING', ml='ഒരാൾ മാത്രം കള്ളം. ഒരാൾ മാത്രം കൊലയാളി. ആരാണത്?', en='Only one is *lying.* Who is the *killer?*'),
        dict(id='h10', scene='summary', rule_label='ONLY 1 IS LYING', typing=True, follow=True, type_dt=0.3,
             ml='ഉത്തരം കമന്റിൽ ടൈപ്പ് ചെയ്യൂ. ഉത്തരം അറിയാൻ ഫോളോ ചെയ്യൂ!',
             en='Type *ANSWER* in the comments! *Follow* for the answer!', post=1.5),
    ])

if __name__ == '__main__':
    tl, ans = build(CASE, '/home/claude/pz/out', 'Theatre_Mystery_Short', stills='stills' in sys.argv)
    print('TOTAL', round(tl.end, 1), 'ANSWER', ans)
