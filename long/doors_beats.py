import sys; sys.path.insert(0, '/home/claude/long')
from doors_data import R, TITLES
NUM = ['ഒന്ന്', 'രണ്ട്', 'മൂന്ന്', 'നാല്', 'അഞ്ച്', 'ആറ്', 'ഏഴ്', 'എട്ട്', 'ഒൻപത്', 'പത്ത്']
TIPS = [('ഓരോ വാക്കും ശ്രദ്ധിക്കൂ. ഒരു വഴി മാത്രം സുരക്ഷിതം.', 'Listen to *every word.* Only *one* way is safe.'),
        ('ചിത്രം നന്നായി നോക്കൂ. ഉത്തരം അവിടെയുണ്ട്.', 'Look at the pictures *carefully.* The answer is *there.*'),
        ('ഒരു ഡിറ്റക്ടീവിനെ പോലെ ചിന്തിക്കൂ.', 'Think like a *detective.*'),
        ('തിരക്കു കൂട്ടരുത്. ഓരോ വാതിലും ഓർത്തു നോക്കൂ.', 'Don\'t *rush.* Remember *each* door.'),
        ('ഇത് എളുപ്പമാണെന്ന് തോന്നും. പക്ഷേ സൂക്ഷിക്കണം!', 'It looks *easy.* But be *careful!*')]
DNUM = ['ഒന്ന്', 'രണ്ട്', 'മൂന്ന്']

def make_beats():
    N = len(R); B = []
    B.append(dict(id='t1', sc='teaser', i=3, ml='പത്തു മരണ വാതിലുകൾ. എല്ലാം ശരിയാക്കുന്നത് ഒരു ശതമാനം പേർ മാത്രം! നിങ്ങൾക്കു പറ്റുമോ?',
                  en='*10* deadly door riddles. Only *1%* get all of them! Can you?'))
    B.append(dict(id='t2', sc='teaser2', i=3, ml='ഓരോ ശരിയുത്തരത്തിനും ഒരു പോയിന്റ്. തുടങ്ങാം!', en='*1 point* for each right answer. Let\'s *go!*'))
    for i, r in enumerate(R):
        p = f'r{i}_'; way = r['rooms'][0][2].startswith('Way') or r['rooms'][0][2].startswith('Choice')
        B.append(dict(id=p+'a', sc='title', i=i, ml=f'കടങ്കഥ നമ്പർ {NUM[i]}. ' + r['setup'][0], en=f'Riddle {i+1}: ' + r['setup'][1]))
        for j, (kind, ml, en, lab) in enumerate(r['rooms']):
            B.append(dict(id=p+f'd{j}', sc='room', i=i, j=j, ml=ml, en=en))
        tip = TIPS[i % len(TIPS)]
        B.append(dict(id=p+'k', sc='corr', i=i, ml=tip[0], en=tip[1]))
        B.append(dict(id=p+'q', sc='corr', i=i, timer=True, ml='ഏതു വഴിയാണ് സുരക്ഷിതം?' if way else 'ഏതു വാതിലാണ് സുരക്ഷിതം?',
                      en='Which choice is *SAFE?*' if way else 'Which door is *SAFE?*'))
        B.append(dict(id=p+'p', sc='pause', i=i, ml='ഇവിടെ നിർത്തി ആലോചിക്കൂ!', en='*Pause* and think!', post=5.0))
        B.append(dict(id=p+'x', sc='wrong', i=i, ml=r['wrong'][0], en=r['wrong'][1]))
        s = r['safe']
        B.append(dict(id=p+'r', sc='reveal', i=i, ml=f'ഉത്തരം, {"വഴി" if way else "വാതിൽ"} നമ്പർ {DNUM[s]}!', en=f'The answer: *{"Way" if way else "Door"} {s+1}!*'))
        B.append(dict(id=p+'w', sc='why', i=i, ml=r['why'][0] + ' ശരിയാണെങ്കിൽ ഒരു പോയിന്റ്!', en=r['why'][1] + ' *+1 point!*', post=0.6))
        if i == 4:
            B.append(dict(id='half', sc='half', i=-1, ml='പകുതി കഴിഞ്ഞു! അഞ്ചിൽ എത്ര ശരിയായി? ഓർത്തു വെക്കൂ!', en='*Halfway!* How many out of *5* so far? Keep count!'))
    B.append(dict(id='e1', sc='end', i=-1, ml='നിങ്ങൾക്ക് പത്തിൽ എത്ര കിട്ടി? കമന്റിൽ സ്കോർ എഴുതൂ!', en='How many did you get? Comment your *score* out of *10!*'))
    B.append(dict(id='e2', sc='end', i=-1, ml='എല്ലാ ദിവസവും പുതിയ കടങ്കഥകൾക്ക് സബ്സ്ക്രൈബ് ചെയ്യൂ!', en='*Subscribe* for new riddles *every day!*', post=1.5))
    return B

if __name__ == '__main__':
    sys.path.insert(0, '/home/claude/pz')
    from pz import voice
    from wd import NARR
    for b in make_beats(): voice(b['ml'], NARR)
    print('voiced')
