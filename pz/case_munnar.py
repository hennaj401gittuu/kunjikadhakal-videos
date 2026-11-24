import sys
sys.path.insert(0, '/home/claude/pz')
from wd import build
CASE = dict(
    suspects=[
        dict(name='Joseph', robe='#2f6fd6', stmt=('did', 'Lakshmi'), short='"Lakshmi did it!"', mood='sus'),
        dict(name='Lakshmi', robe='#c2417a', stmt=('liar', 'Joseph'), short='"Joseph is lying."', mood='sus', stache=False, hair='#0d0a08'),
        dict(name='Sabu', robe='#27a85a', stmt=('not', 'Sabu'), short='"I didn\'t do it."', mood='sus'),
    ],
    beats=[
        dict(id='h1', scene='lineup', fail='99% FAIL', ml='കൊലയാളി ആരാണ്? തൊണ്ണൂറ്റൊമ്പത് ശതമാനം പേരും ഇത് തെറ്റിക്കും!',
             en='Who is the *KILLER?* *99%* get this wrong!'),
        dict(id='h2', scene='place', place='tea', ml='മൂന്നാറിലെ ഒരു തേയിലത്തോട്ടത്തിൽ, ബംഗ്ലാവിൽ, തോട്ടമുടമയെ മരിച്ച നിലയിൽ കണ്ടെത്തി.',
             en='A planter was found *dead* in his bungalow on a *Munnar* tea estate.'),
        dict(id='h3', scene='police', talking=True, ml='പോലീസ് മൂന്നു പേരെ ചോദ്യം ചെയ്തു.', en='Police questioned *three* people.'),
        dict(id='h4', scene='rule', ml='പോലീസിന് ഒരു കാര്യം ഉറപ്പാണ്.', en='Police are sure of *one* thing,'),
        dict(id='h5', scene='rule', truth=True, truth_dt=0.5, lies=True, lies_dt=2.0,
             ml='ഇവരിൽ ഒരാൾ മാത്രമേ സത്യം പറയുന്നുള്ളൂ. ബാക്കി രണ്ടുപേരും കള്ളം പറയുന്നു.',
             en='Only *ONE* of them tells the *truth.* The other two are *LYING.*'),
        dict(id='h6', scene='solo', who=0, pose='point', mood='angry', bubble='LAKSHMI DID IT!', bubble_col='#e8283c',
             ml='എസ്റ്റേറ്റ് മാനേജർ ജോസഫ് പറഞ്ഞു, ലക്ഷ്മി ആണ് കൊന്നത്.', en='Estate manager *Joseph* said: "*Lakshmi* did it!"'),
        dict(id='h7', scene='solo', who=1, pose='shrug', mood='sus', bubble='JOSEPH IS LYING!',
             ml='തേയിലത്തൊഴിലാളി ലക്ഷ്മി പറഞ്ഞു, ജോസഫ് കള്ളം പറയുകയാണ്.', en='Tea picker *Lakshmi* said: "*Joseph* is lying!"'),
        dict(id='h8', scene='solo', who=2, pose='chest', mood='scared', bubble='NOT ME', ml='ജീപ്പ് ഡ്രൈവർ സാബു പറഞ്ഞു, ഞാനല്ല കൊന്നത്.',
             en='Jeep driver *Sabu* said: "I didn\'t do it."'),
        dict(id='h9', scene='summary', ml='ഒരാൾ മാത്രം സത്യം. ഒരാൾ മാത്രം കൊലയാളി. ആരാണ് അത്?', en='Only one tells the *truth.* Only one is the *killer.* Who?'),
        dict(id='h10', scene='summary', typing=True, follow=True, type_dt=0.3,
             ml='അറിയാമെങ്കിൽ കമന്റ് ചെയ്യൂ. അറിയില്ലെങ്കിൽ ഫോളോ ചെയ്ത് ഉത്തരം കാണൂ!',
             en='Know it? *Comment* the answer. Not sure? *Follow* to see it!', post=1.5),
    ])
if __name__ == '__main__':
    tl, ans = build(CASE, '/home/claude/pz/out', 'Munnar_Mystery_Short', stills='stills' in sys.argv)
    print('TOTAL', round(tl.end, 1), 'ANSWER', ans)
