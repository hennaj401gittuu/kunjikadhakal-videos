import sys; sys.path.insert(0,'/home/claude/pz')
# each suspect: (EnglishName, MalayalamName, role_en, role_ml, robe, cap, stmt)
CASES = [
 dict(place='Kochi flat', kind='murder', victim_en='A businessman was found *dead* in his *Kochi* flat.',
      victim_ml='കൊച്ചിയിലെ ഒരു ഫ്ലാറ്റിൽ ഒരു ബിസിനസുകാരനെ മരിച്ച നിലയിൽ കണ്ടെത്തി.', bg='city',
      sus=[('Anil','അനിൽ','security guard','സെക്യൂരിറ്റി','#2f6fd6',None,('did','Reena')),
           ('Reena','റീന','maid','വേലക്കാരി','#c2417a',None,('not','Reena')),
           ('Vinod','വിനോദ്','neighbour','അയൽക്കാരൻ','#27a85a',None,('did','Anil'))], n_true=1),
 dict(place='Toddy shop', kind='murder', victim_en='The owner of a *toddy shop* was found *dead* at closing time.',
      victim_ml='രാത്രി ഷാപ്പ് അടയ്ക്കുന്ന സമയത്ത്, കള്ളുഷാപ്പ് മുതലാളിയെ മരിച്ച നിലയിൽ കണ്ടെത്തി.', bg='toddy',
      sus=[('Kuttan','കുട്ടൻ','toddy tapper','ചെത്തുകാരൻ','#d9822b',None,('not','Babu')),
           ('Babu','ബാബു','cook','പാചകക്കാരൻ','#7a4fd0',None,('liar','Kuttan')),
           ('Salim','സലിം','customer','ഒരു കസ്റ്റമർ','#2a9d8f','kufi',('did','Kuttan'))], n_true=1),
 dict(place='Wedding hall', kind='theft', victim_en='The bride\'s *gold chain* went missing at a *wedding hall.*',
      victim_ml='ഒരു കല്യാണമണ്ഡപത്തിൽ നിന്ന്, വധുവിന്റെ സ്വർണ്ണമാല കാണാതായി.', bg='wedding',
      sus=[('Priya','പ്രിയ','cousin','കസിൻ','#e05a9b',None,('did','Manoj')),
           ('Manoj','മനോജ്','photographer','ഫോട്ടോഗ്രാഫർ','#3b7dd8',None,('did','Ammini')),
           ('Ammini','അമ്മിണി','cook','പാചകക്കാരി','#c9a227',None,('not','Ammini'))], n_true=1),
 dict(place='KSRTC bus', kind='theft', victim_en='A passenger\'s *phone* was stolen on a *KSRTC* bus.',
      victim_ml='ഒരു കെ എസ് ആർ ടി സി ബസ്സിൽ, ഒരു യാത്രക്കാരന്റെ ഫോൺ മോഷണം പോയി.', bg='bus',
      sus=[('Raju','രാജു','conductor','കണ്ടക്ടർ','#4b6cb7',None,('not','Arun')),
           ('Arun','അരുൺ','student','വിദ്യാർത്ഥി','#e76f51',None,('not','Hamsa')),
           ('Hamsa','ഹംസ','shopkeeper','കടക്കാരൻ','#2a9d8f','kufi',('did','Arun'))], n_true=1),
 dict(place='Temple festival', kind='theft', victim_en='The *temple jewels* vanished during the *festival* night.',
      victim_ml='ഉത്സവരാത്രിയിൽ, അമ്പലത്തിലെ തിരുവാഭരണം കാണാതായി.', bg='temple',
      sus=[('Gopi','ഗോപി','mahout','പാപ്പാൻ','#8d6e63',None,('honest','Sreedharan')),
           ('Unni','ഉണ്ണി','drummer','ചെണ്ടക്കാരൻ','#c0392b',None,('did','Gopi')),
           ('Sreedharan','ശ്രീധരൻ','temple helper','ശാന്തിക്കാരന്റെ സഹായി','#e0a526','bald',('not','Unni'))], n_true=1),
 dict(place='Wayanad homestay', kind='murder', victim_en='A guest was found *dead* in a *Wayanad* homestay.',
      victim_ml='വയനാട്ടിലെ ഒരു ഹോംസ്റ്റേയിൽ, ഒരു അതിഥിയെ മരിച്ച നിലയിൽ കണ്ടെത്തി.', bg='hills',
      sus=[('Thomas','തോമസ്','owner','ഉടമസ്ഥൻ','#355c7d',None,('not','Thomas')),
           ('Sajitha','സജിത','cook','പാചകക്കാരി','#c06c84',None,('liar','Thomas')),
           ('Biju','ബിജു','trek guide','ഗൈഡ്','#6c8a3b',None,('did','Sajitha'))], n_true=2),
 dict(place='School office', kind='theft', victim_en='The *exam question paper* went missing from the *school office.*',
      victim_ml='സ്കൂൾ ഓഫീസിൽ നിന്ന്, പരീക്ഷയുടെ ചോദ്യപേപ്പർ കാണാതായി.', bg='school',
      sus=[('Rajeev','രാജീവ്','clerk','ക്ലർക്ക്','#5d6d7e',None,('did','Kunjumon')),
           ('Kunjumon','കുഞ്ഞുമോൻ','peon','പ്യൂൺ','#a04000','bald',('not','Kunjumon')),
           ('Sheela','ഷീല','teacher','ടീച്ചർ','#7d3c98',None,('not','Rajeev'))], n_true=2),
 dict(place='Spice shop', kind='theft', victim_en='The cash box was stolen from a *spice shop* in *Mattancherry.*',
      victim_ml='മട്ടാഞ്ചേരിയിലെ ഒരു സുഗന്ധവ്യഞ്ജനക്കടയിൽ നിന്ന്, പണപ്പെട്ടി മോഷണം പോയി.', bg='city',
      sus=[('Shaji','ഷാജി','loader','ചുമട്ടുകാരൻ','#7b241c',None,('did','Leela')),
           ('Leela','ലീല','sweeper','തൂപ്പുകാരി','#1abc9c',None,('liar','Shaji')),
           ('Pradeep','പ്രദീപ്','accountant','കണക്കപ്പിള്ള','#34495e',None,('not','Leela'))], n_true=1),
 dict(place='Fishing harbour', kind='murder', victim_en='A boat owner was found *dead* at the *fishing harbour* at dawn.',
      victim_ml='പുലർച്ചെ, മത്സ്യബന്ധന തുറമുഖത്ത് ഒരു ബോട്ടുടമയെ മരിച്ച നിലയിൽ കണ്ടെത്തി.', bg='harbour',
      sus=[('Antony','ആന്റണി','fisherman','മീൻപിടുത്തക്കാരൻ','#1f618d',None,('liar','Dasan')),
           ('Rafeeq','റഫീഖ്','ice seller','ഐസ് കച്ചവടക്കാരൻ','#16a085','kufi',('did','Antony')),
           ('Dasan','ദാസൻ','auctioneer','ലേലക്കാരൻ','#b9770e',None,('liar','Rafeeq'))], n_true=1),
]
SHORT = dict(place='Munnar tea estate', kind='murder',
      sus=[('Joseph','ജോസഫ്','estate manager','എസ്റ്റേറ്റ് മാനേജർ','#2f6fd6',None,('did','Lakshmi')),
           ('Lakshmi','ലക്ഷ്മി','tea picker','തേയിലത്തൊഴിലാളി','#c2417a',None,('liar','Joseph')),
           ('Sabu','സാബു','jeep driver','ജീപ്പ് ഡ്രൈവർ','#27a85a',None,('not','Sabu'))], n_true=1)
if __name__=='__main__':
    from wd import solve, evaluate
    for c in CASES+[SHORT]:
        names=[s[0] for s in c['sus']]; st={s[0]:s[6] for s in c['sus']}
        sol=solve(names,st,c['n_true'])
        print(c['place'], sol, {k:evaluate(names,st,k) for k in names})
from fixes import FIXES
for c in CASES:
    if c['place'] in FIXES:
        c['sus']=[s[:6]+(f,) for s,f in zip(c['sus'],FIXES[c['place']])]
