import sys
sys.path.insert(0, '/home/claude/pz')
from wd import build

CASE = dict(
    suspects=[
        dict(name='Vasu', robe='#e08a1e', stmt=('not', 'Vasu'), short='"I didn\'t do it."', mood='sus', cap='bald'),
        dict(name='Divya', robe='#8e3fc9', stmt=('did', 'Vasu'), short='"Vasu did it!"', mood='sus', stache=False, cap='bun'),
        dict(name='Nazar', robe='#d23a3a', stmt=('not', 'Divya'), short='"It wasn\'t Divya."', mood='sus'),
    ],
    beats=[
        dict(id='h1', scene='lineup', fail='99% FAIL', ml='ഈ കൊലയാളിയെ കണ്ടുപിടിക്കാമോ? തൊണ്ണൂറ്റൊമ്പത് ശതമാനം പേരും തോൽക്കും!',
             en='Can you find the *KILLER?* *99%* fail!'),
        dict(id='h2', scene='place', place='beach', ml='കോവളത്തെ ഒരു ആയുർവേദ റിസോർട്ടിൽ, ഒരു വിദേശ ടൂറിസ്റ്റിനെ രാവിലെ മരിച്ച നിലയിൽ കണ്ടെത്തി.',
             en='A foreign tourist was found *dead* at an Ayurveda resort in *Kovalam.*'),
        dict(id='h3', scene='police', talking=True, ml='പോലീസ് മൂന്നു പേരെ ചോദ്യം ചെയ്തു.', en='Police questioned *three* people.'),
        dict(id='h4', scene='rule', ml='പക്ഷേ ഒരു കാര്യം ഉറപ്പാണ്.', en='But one thing is *certain...*'),
        dict(id='h5', scene='rule', truth=True, truth_dt=0.5, lies=True, lies_dt=2.0,
             ml='ഇവരിൽ ഒരാൾ മാത്രമേ സത്യം പറയുന്നുള്ളൂ. ബാക്കി രണ്ടുപേരും കള്ളം പറയുന്നു.',
             en='Only *ONE* of them tells the *truth.* The other two are *LYING.*'),
        dict(id='h6', scene='solo', who=0, pose='chest', mood='scared', bubble='NOT ME!', ml='മസാജ് ചെയ്യുന്ന വാസു പറഞ്ഞു, ഞാനല്ല കൊന്നത്.',
             en='Therapist *Vasu* said: "I didn\'t do it."'),
        dict(id='h7', scene='solo', who=1, pose='point', mood='angry', bubble='VASU DID IT!', bubble_col='#e8283c',
             ml='റിസപ്ഷനിസ്റ്റ് ദിവ്യ പറഞ്ഞു, വാസു ആണ് കൊന്നത്!', en='Receptionist *Divya* said: "*Vasu* did it!"'),
        dict(id='h8', scene='solo', who=2, pose='shrug', mood='sus', bubble='NOT DIVYA!', ml='ലൈഫ്ഗാർഡ് നസർ പറഞ്ഞു, ദിവ്യ അല്ല കൊന്നത്.',
             en='Lifeguard *Nazar* said: "It wasn\'t *Divya.*"'),
        dict(id='h9', scene='summary', ml='ഒരാൾ മാത്രം സത്യം. ഒരാൾ മാത്രം കൊലയാളി. ആരാണ് അത്?', en='Only one tells the *truth.* Only one is the *killer.* Who?'),
        dict(id='h10', scene='summary', typing=True, follow=True, type_dt=0.3,
             ml='അറിയാമെങ്കിൽ കമന്റ് ചെയ്യൂ. അറിയില്ലെങ്കിൽ ഫോളോ ചെയ്ത് ഉത്തരം കാണൂ!',
             en='Know it? *Comment* the answer. Not sure? *Follow* to see it!', post=1.2),
    ])

if __name__ == '__main__':
    tl, ans = build(CASE, '/home/claude/pz/out', 'Kovalam_Short', stills='stills' in sys.argv)
    print('TOTAL', round(tl.end, 1), 'ANSWER', ans)
