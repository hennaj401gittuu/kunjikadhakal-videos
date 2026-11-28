import sys
sys.path.insert(0, '/home/claude/pz')
from wd import build

CASE = dict(
    suspects=[
        dict(name='Thankachan', robe='#2f6fd6', stmt=('did', 'Shibu'), short='"Shibu did it!"', mood='sus', cap='bald'),
        dict(name='Remya', robe='#c2407a', stmt=('liar', 'Thankachan'), short='"Thankachan is lying!"', mood='sus', stache=False, cap='bun'),
        dict(name='Shibu', robe='#e08a1e', stmt=('not', 'Remya'), short='"Remya didn\'t do it."', mood='sus', stache=False),
    ],
    beats=[
        dict(id='h1', scene='lineup', fail='99% FAIL', ml='വള്ളംകളിയിലെ കൊലയാളി ആരാണ്? തൊണ്ണൂറ്റൊമ്പത് ശതമാനം പേരും ഇത് തെറ്റിക്കും!',
             en='Who is the *KILLER* at the boat race? *99%* get this wrong!'),
        dict(id='h2', scene='place', place='boatrace', ml='വള്ളംകളിയുടെ തലേന്ന് രാത്രി, ബോട്ട് ക്ലബ്ബിൽ ചുണ്ടൻ വള്ളത്തിന്റെ ക്യാപ്റ്റനെ മരിച്ച നിലയിൽ കണ്ടെത്തി.',
             en='The night before the *boat race,* the snake-boat *captain* was found *dead.*'),
        dict(id='h3', scene='police', talking=True, ml='പോലീസ് മൂന്നു പേരെ ചോദ്യം ചെയ്തു.', en='Police questioned *three* people.'),
        dict(id='h4', scene='rule', ml='പോലീസിന് ഒരു കാര്യം മാത്രം ഉറപ്പാണ്.', en='Police are sure of just *one* thing...'),
        dict(id='h5', scene='rule', truth=True, truth_dt=0.5, lies=True, lies_dt=1.4,
             ml='ഇവരിൽ ഒരാൾ മാത്രമേ സത്യം പറയുന്നുള്ളൂ. ബാക്കി രണ്ടുപേരും കള്ളം പറയുന്നു.',
             en='Only *ONE* of them tells the *TRUTH.* The other two are *lying.*'),
        dict(id='h6', scene='solo', who=0, pose='point', mood='angry', bubble='SHIBU DID IT!', bubble_col='#e8283c',
             ml='വള്ളത്തിന്റെ ഉടമ തങ്കച്ചൻ പറഞ്ഞു, ഷിബുവാണ് കൊന്നത്.', en='Boat owner *Thankachan* said: "*Shibu* did it!"'),
        dict(id='h7', scene='solo', who=1, pose='chest', mood='sus', bubble='THANKACHAN IS LYING!', bubble_col='#1a1a1a',
             ml='ടീമിന്റെ പാചകക്കാരി രമ്യ പറഞ്ഞു, തങ്കച്ചൻ കള്ളം പറയുകയാണ്.', en='Team cook *Remya* said: "*Thankachan* is lying!"'),
        dict(id='h8', scene='solo', who=2, pose='shrug', mood='sus', bubble="IT WASN'T REMYA!",
             ml='എതിർ ടീമിലെ തുഴക്കാരൻ ഷിബു പറഞ്ഞു, രമ്യയല്ല കൊന്നത്.', en='Rival rower *Shibu* said: "*Remya* didn\'t do it."'),
        dict(id='h9', scene='summary', ml='ഒരാൾ മാത്രം സത്യം. ഒരാൾ മാത്രം കൊലയാളി. ആരാണത്?', en='Only one tells the *truth.* Who is the *killer?*'),
        dict(id='h10', scene='summary', typing=True, follow=True, type_dt=0.3,
             ml='ഉത്തരം കമന്റിൽ ടൈപ്പ് ചെയ്യൂ. ഉത്തരം അറിയാൻ ഫോളോ ചെയ്യൂ!',
             en='Type *ANSWER* in the comments! *Follow* for the answer!', post=1.5),
    ])

if __name__ == '__main__':
    tl, ans = build(CASE, '/home/claude/pz/out', 'Boat_Race_Mystery_Short', stills='stills' in sys.argv)
    print('TOTAL', round(tl.end, 1), 'ANSWER', ans)
