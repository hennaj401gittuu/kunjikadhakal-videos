# Money/logic brain-teaser stories (all ORIGINAL; answers verified in verify.py)
# chars: (name, shirt, lower, female)
S = []
S.append(dict(key='goat', title='The Goat Deal', shops=('RAVI FARM', 'CATTLE MARKET', 'TEA SHOP'),
  chars=[('Ravi', '#e0702a', '#f4f1e8', False), ('Kuttan', '#2f6fd6', '#f4f1e8', False)], item='goat',
  setup=[
    dict(ml='രവി ചന്തയിൽ നിന്ന് ഒരു ആടിനെ ആറായിരം രൂപയ്ക്ക് വാങ്ങി.', en='Ravi buys a goat for *₹6000.*', pay=(0, 1, '₹6000'), item_at=1),
    dict(ml='പിന്നെ കുട്ടന് അത് ഏഴായിരം രൂപയ്ക്ക് വിറ്റു.', en='Then he sells it to Kuttan for *₹7000.*', pay=(1, 0, '₹7000'), item_at=1, bub=(0, '+₹1000?')),
    dict(ml='അടുത്ത ആഴ്ച അതേ ആടിനെ എണ്ണായിരം രൂപയ്ക്ക് തിരികെ വാങ്ങി.', en='Next week he buys it *back* for *₹8000.*', pay=(0, 1, '₹8000'), item_at=0),
    dict(ml='അവസാനം ഒൻപതിനായിരം രൂപയ്ക്ക് വീണ്ടും വിറ്റു.', en='Finally he sells it *again* for *₹9000.*', pay=(1, 0, '₹9000'), item_at=1),
  ],
  wrong=dict(ml='മിക്കവരും പറയും ആയിരം രൂപ എന്ന്.', en='Most people say *₹1000...*'),
  q=dict(ml='രവിക്ക് ആകെ എത്ര രൂപ ലാഭം കിട്ടി?', en='How much *profit* did Ravi make in total?', box='Total profit = ₹?'),
  ans=[dict(ml='ആദ്യത്തെ കച്ചവടം, ആറായിരത്തിന് വാങ്ങി ഏഴായിരത്തിന് വിറ്റു. ലാഭം ആയിരം.', en='Deal 1: buy 6000, sell 7000 = *+₹1000*', line='Deal 1:  7000 - 6000 = +1000'),
       dict(ml='രണ്ടാമത്തെ കച്ചവടം, എണ്ണായിരത്തിന് വാങ്ങി ഒൻപതിനായിരത്തിന് വിറ്റു. ലാഭം വീണ്ടും ആയിരം.', en='Deal 2: buy 8000, sell 9000 = *+₹1000*', line='Deal 2:  9000 - 8000 = +1000'),
       dict(ml='അപ്പോൾ ആകെ ലാഭം രണ്ടായിരം രൂപ!', en='Total profit: *₹2000!*', line='Total = +₹2000')],
  stamp='₹2000', short='₹2000 profit (two deals of +1000)'))

S.append(dict(key='tea', title='Tea and Vada', shops=('PAPPAN TEA SHOP', 'BAKERY', 'STORES'),
  chars=[('Pappan', '#f4f1e8', '#f4f1e8', False), ('Sunil', '#2fa86a', '#f4f1e8', False)], item='tea',
  setup=[
    dict(ml='പപ്പന്റെ ചായക്കടയിൽ സുനിൽ ഒരു ചായയും ഒരു വടയും വാങ്ങി.', en='At Pappan\'s tea shop, Sunil orders *tea* and a *vada.*', item_at=0),
    dict(ml='രണ്ടും കൂടി ഇരുപത്തിരണ്ട് രൂപ.', en='Together they cost *₹22.*', bub=(0, '₹22'), item_at=0),
    dict(ml='ചായക്ക് വടയെക്കാൾ ഇരുപത് രൂപ കൂടുതലാണ്.', en='The tea costs *₹20 MORE* than the vada.', sign='TEA = VADA + ₹20', item_at=0),
  ],
  wrong=dict(ml='മിക്കവരും പെട്ടെന്ന് പറയും രണ്ടു രൂപ എന്ന്.', en='Most people quickly say *₹2...*'),
  q=dict(ml='വടയുടെ വില എത്ര? വേഗം പറയൂ!', en='How much is the *vada?* Quick!', box='Vada = ₹?'),
  ans=[dict(ml='വട രണ്ടു രൂപ എങ്കിൽ, ചായ ഇരുപത്തിരണ്ട്. ആകെ ഇരുപത്തിനാല്. തെറ്റ്!', en='If vada is 2, tea is 22. Total *24.* Wrong!', line='2 + 22 = 24   WRONG'),
       dict(ml='വട ഒരു രൂപ എങ്കിൽ, ചായ ഇരുപത്തിയൊന്ന്. ആകെ ഇരുപത്തിരണ്ട്. ശരി!', en='Vada *₹1*, tea *₹21.* Total *₹22.* Right!', line='1 + 21 = 22   RIGHT')],
  stamp='VADA ₹1', short='vada ₹1, tea ₹21'))

S.append(dict(key='saree', title='The Saree Sale', shops=('SILK HOUSE', 'SAREE PALACE', 'JEWELLERY'),
  chars=[('Meena', '#d23a7a', '#d23a7a', True)], item='saree',
  setup=[
    dict(ml='മീന ആയിരം രൂപയുടെ ഒരു സാരി വാങ്ങാൻ തൃശ്ശൂരിൽ എത്തി.', en='Meena wants a *₹1000* saree in *Thrissur.*', item_at=0, bub=(0, '₹1000')),
    dict(ml='ഒന്നാമത്തെ കടയിൽ നാല്പത് ശതമാനം കിഴിവ്.', en='Shop 1 says: *40% OFF.*', sign='SHOP 1: 40% OFF'),
    dict(ml='രണ്ടാമത്തെ കടയിൽ ഇരുപത് ശതമാനം കിഴിവ്. അതിനു മുകളിൽ വീണ്ടും ഇരുപത് ശതമാനം!', en='Shop 2 says: *20% OFF*, then *another 20% OFF!*', sign='SHOP 2: 20% + 20% OFF'),
  ],
  wrong=dict(ml='രണ്ടും ഒന്നു തന്നെ എന്ന് തോന്നും, അല്ലേ?', en='Looks the *same*, right?'),
  q=dict(ml='ഏതു കടയിലാണ് വില കുറവ്? എത്ര രൂപ വ്യത്യാസം?', en='Which shop is *cheaper*, and by how much?', box='Shop 1 or 2? By ₹?'),
  ans=[dict(ml='ഒന്നാമത്തെ കട, ആയിരത്തിൽ നിന്ന് നാനൂറ് കുറച്ചാൽ അറുനൂറ്.', en='Shop 1: 1000 - 400 = *₹600*', line='Shop 1:  1000 - 400 = 600'),
       dict(ml='രണ്ടാമത്തെ കട, ആദ്യം എണ്ണൂറ്. പിന്നെ എണ്ണൂറിന്റെ ഇരുപത് ശതമാനം, നൂറ്റി അറുപത് കുറഞ്ഞ് അറുനൂറ്റി നാല്പത്.', en='Shop 2: 800, then 800 - 160 = *₹640*', line='Shop 2:  800 - 160 = 640'),
       dict(ml='അപ്പോൾ ഒന്നാമത്തെ കടയിൽ നാല്പത് രൂപ കുറവ്!', en='Shop 1 is cheaper by *₹40!*', line='Shop 1 saves ₹40')],
  stamp='SHOP 1, ₹40', short='Shop 1 (40% off) by ₹40: 600 vs 640'))

S.append(dict(key='soda', title='The Soda Offer', shops=('NASEER SODA', 'BEACH SNACKS', 'ICE CREAM'),
  chars=[('Naseer', '#2a9fd6', '#f4f1e8', False), ('Anu', '#f2b632', '#f2b632', True)], item='soda',
  setup=[
    dict(ml='കോഴിക്കോട് ബീച്ചിലെ നസീറിന്റെ സോഡാ കടയിൽ ഒരു ഓഫർ ഉണ്ട്.', en='Naseer\'s soda shop at *Kozhikode beach* has an *offer.*', item_at=0),
    dict(ml='മൂന്നു കാലി കുപ്പി തിരികെ കൊടുത്താൽ, ഒരു സോഡ ഫ്രീ!', en='Return *3 empty* bottles, get *1 soda FREE!*', sign='3 EMPTY = 1 FREE'),
    dict(ml='അനു ഒൻപത് സോഡ വാങ്ങി.', en='Anu buys *9* sodas.', pay=(1, 0, '₹90'), item_at=1, bub=(1, '9 SODAS')),
  ],
  wrong=dict(ml='മിക്കവരും പറയും പന്ത്രണ്ട് എന്ന്.', en='Most people say *12...*'),
  q=dict(ml='കടം വാങ്ങാതെ, അനുവിന് ആകെ എത്ര സോഡ കുടിക്കാം?', en='Without borrowing, how many sodas can Anu *drink* in total?', box='Total sodas = ?'),
  ans=[dict(ml='ഒൻപതും കുടിച്ചു. ഒൻപത് കാലിക്കുപ്പിക്ക് മൂന്നു സോഡ ഫ്രീ.', en='Drink 9: 9 empties = *3 free*', line='9 empties  =  3 free'),
       dict(ml='ആ മൂന്നും കുടിച്ചു. മൂന്നു കാലിക്കുപ്പിക്ക് ഒന്നു കൂടി ഫ്രീ.', en='Drink 3: 3 empties = *1 more*', line='3 empties  =  1 free'),
       dict(ml='ഒൻപതും മൂന്നും ഒന്നും. ആകെ പതിമൂന്ന് സോഡ!', en='9 + 3 + 1 = *13* sodas!', line='9 + 3 + 1 = 13')],
  stamp='13 SODAS', short='13 sodas (9 + 3 + 1)'))

S.append(dict(key='puttu', title='Sharing the Puttu', shops=('BUS STOP', 'HOTEL', 'STORES'),
  chars=[('Babu', '#c0392b', '#f4f1e8', False), ('Shaji', '#16a085', '#f4f1e8', False), ('Joseph', '#8e44ad', '#2c3e50', False)], item='puttu',
  setup=[
    dict(ml='ബസ് സ്റ്റോപ്പിൽ ബാബുവിന്റെ കയ്യിൽ അഞ്ചു പുട്ട്. ഷാജിയുടെ കയ്യിൽ മൂന്നു പുട്ട്.', en='At the bus stop, *Babu* has *5* puttu. *Shaji* has *3.*', bub=(0, '5'), bub2=(1, '3')),
    dict(ml='ഭക്ഷണം ഇല്ലാത്ത യാത്രക്കാരൻ ജോസഫ് വന്നു. എട്ടു പുട്ടും മൂന്നു പേരും തുല്യമായി പങ്കിട്ടു കഴിച്ചു.', en='Traveller *Joseph* has none. All *8* are shared *equally* by the three.', item_at=-1),
    dict(ml='പോകുമ്പോൾ ജോസഫ് എൺപത് രൂപ കൊടുത്തു.', en='Joseph pays *₹80* and leaves.', pay=(2, 0, '₹80')),
    dict(ml='ബാബു പറഞ്ഞു, എനിക്ക് അമ്പത്, ഷാജിക്ക് മുപ്പത്.', en='Babu says: "*₹50* for me, *₹30* for Shaji."', bub=(0, '50 + 30')),
  ],
  wrong=None,
  q=dict(ml='ഇത് ന്യായമാണോ? ശരിക്കും ബാബുവിന് എത്ര കിട്ടണം?', en='Is that *fair?* How much should *Babu* really get?', box='Babu gets ₹?'),
  ans=[dict(ml='ഓരോ പുട്ടും മൂന്നു കഷ്ണമാക്കിയാൽ, ആകെ ഇരുപത്തിനാല് കഷ്ണം. ഓരോരുത്തരും എട്ടു കഷ്ണം വീതം കഴിച്ചു.', en='Cut each in 3: *24* pieces. Each person ate *8.*', line='8 x 3 = 24 pieces, 8 each'),
       dict(ml='ബാബുവിന് പതിനഞ്ചു കഷ്ണം. എട്ടു കഴിച്ചു, ഏഴു കഷ്ണം ജോസഫിന് കൊടുത്തു.', en='Babu had *15*, ate 8, gave Joseph *7.*', line='Babu:  15 - 8 = 7 given'),
       dict(ml='ഷാജിക്ക് ഒൻപത് കഷ്ണം. എട്ടു കഴിച്ചു, ഒരു കഷ്ണം മാത്രം കൊടുത്തു.', en='Shaji had *9*, ate 8, gave just *1.*', line='Shaji:  9 - 8 = 1 given'),
       dict(ml='ഒരു കഷ്ണത്തിന് പത്തു രൂപ. അപ്പോൾ ബാബുവിന് എഴുപത്, ഷാജിക്ക് പത്ത്!', en='₹10 a piece: Babu *₹70*, Shaji *₹10!*', line='Babu ₹70, Shaji ₹10')],
  stamp='BABU ₹70', short='Babu ₹70, Shaji ₹10'))

S.append(dict(key='chips', title='The Chips Machines', shops=('SHIBU CHIPS', 'FACTORY', 'WAREHOUSE'),
  chars=[('Shibu', '#e67e22', '#f4f1e8', False)], item='chips',
  setup=[
    dict(ml='ഷിബുവിന്റെ ഏത്തക്ക ചിപ്സ് ഫാക്ടറി.', en='Shibu\'s *banana chips* factory.', item_at=0),
    dict(ml='അഞ്ചു മെഷീനുകൾ, അഞ്ചു മിനിറ്റിൽ, അഞ്ചു പാക്കറ്റ് ഉണ്ടാക്കുന്നു.', en='*5* machines make *5* packets in *5* minutes.', sign='5 MACHINES, 5 PACKETS, 5 MIN'),
    dict(ml='ഷിബു നൂറു മെഷീനുകൾ വാങ്ങി.', en='Shibu buys *100* machines.', bub=(0, '100 MACHINES')),
  ],
  wrong=dict(ml='മിക്കവരും പറയും നൂറു മിനിറ്റ് എന്ന്.', en='Most people say *100 minutes...*'),
  q=dict(ml='നൂറു മെഷീനുകൾക്ക് നൂറു പാക്കറ്റ് ഉണ്ടാക്കാൻ എത്ര മിനിറ്റ് വേണം?', en='How many minutes for *100* machines to make *100* packets?', box='? minutes'),
  ans=[dict(ml='ഒരു മെഷീൻ ഒരു പാക്കറ്റ് ഉണ്ടാക്കാൻ അഞ്ചു മിനിറ്റ് എടുക്കുന്നു.', en='*1* machine makes *1* packet in *5* minutes.', line='1 machine: 1 packet / 5 min'),
       dict(ml='നൂറു മെഷീനുകൾ ഒരുമിച്ച് ഓടിയാൽ, നൂറു പാക്കറ്റ്, അതേ അഞ്ചു മിനിറ്റിൽ!', en='100 machines together: 100 packets in the same *5 minutes!*', line='100 machines: 100 packets / 5 min')],
  stamp='5 MINUTES', short='5 minutes'))

S.append(dict(key='age', title='Brother\'s Age', shops=('AMMU HOUSE', 'ONAM SADYA', 'FLOWERS'),
  chars=[('Grandma', '#f4f1e8', '#f4f1e8', True), ('Ammu', '#f06292', '#f06292', True), ('Kannan', '#42a5f5', '#f4f1e8', False)], item='onam',
  setup=[
    dict(ml='ഓണത്തിന് അമ്മൂമ്മ ഒരു ചോദ്യം ചോദിച്ചു.', en='At *Onam*, Grandma asks a question.', item_at=-1),
    dict(ml='അമ്മുവിന് ആറു വയസ്സ്. അനിയൻ കണ്ണന് അവളുടെ പകുതി പ്രായം.', en='Ammu is *6.* Her brother *Kannan* is *half* her age.', bub=(1, 'AGE 6'), bub2=(2, 'HALF')),
  ],
  wrong=dict(ml='മിക്കവരും പറയും ഇരുപത് എന്ന്.', en='Most people say *20...*'),
  q=dict(ml='അമ്മുവിന് നാല്പതു വയസ്സാകുമ്പോൾ, കണ്ണന് എത്ര വയസ്സ്?', en='When Ammu is *40*, how old is *Kannan?*', box='Kannan = ?'),
  ans=[dict(ml='ഇപ്പോൾ കണ്ണന് മൂന്നു വയസ്സ്. രണ്ടുപേരും തമ്മിൽ മൂന്നു വയസ്സ് വ്യത്യാസം.', en='Now Kannan is *3.* The gap is *3 years.*', line='6 - 3 = 3 years gap'),
       dict(ml='ആ വ്യത്യാസം എന്നും ഒന്നു തന്നെ. നാല്പതിൽ നിന്ന് മൂന്ന് കുറച്ചാൽ, മുപ്പത്തിയേഴ്!', en='The gap never changes: 40 - 3 = *37!*', line='40 - 3 = 37')],
  stamp='37', short='37 (the 3-year gap never changes)'))

S.append(dict(key='exam', title='The Exam Day', shops=('SCHOOL', 'BOOK STALL', 'STATIONERY'),
  chars=[('Rahul', '#5c6bc0', '#f4f1e8', False)], item='calendar',
  setup=[
    dict(ml='ഇന്ന് ചൊവ്വാഴ്ച.', en='Today is *Tuesday.*', item_at=0),
    dict(ml='രാഹുലിന്റെ പരീക്ഷ കൃത്യം നൂറു ദിവസം കഴിഞ്ഞാണ്.', en='Rahul\'s exam is exactly *100 days* from today.', bub=(0, '100 DAYS?')),
  ],
  wrong=None,
  q=dict(ml='പരീക്ഷ ഏതു ദിവസമാണ്?', en='On which *day* is the exam?', box='Which day?'),
  ans=[dict(ml='ഓരോ ഏഴു ദിവസത്തിലും അതേ ദിവസം വരും. പതിനാല് ആഴ്ച, തൊണ്ണൂറ്റെട്ട് ദിവസം, വീണ്ടും ചൊവ്വാഴ്ച.', en='14 weeks = *98 days:* Tuesday again.', line='14 x 7 = 98 days: Tuesday'),
       dict(ml='ബാക്കി രണ്ടു ദിവസം. ബുധൻ, വ്യാഴം. ഉത്തരം വ്യാഴാഴ്ച!', en='2 more days: Wed, *Thursday!*', line='+2 days = Thursday')],
  stamp='THURSDAY', short='Thursday'))

S.append(dict(key='lodge', title='The Missing ₹100', shops=('HOTEL LODGE', 'RECEPTION', 'TEA STALL'),
  chars=[('Manager', '#34495e', '#f4f1e8', False), ('Boy', '#e74c3c', '#2c3e50', False), ('Friends', '#27ae60', '#f4f1e8', False)], item='key',
  setup=[
    dict(ml='മൂന്നു കൂട്ടുകാർ കോഴിക്കോട്ടെ ഒരു ലോഡ്ജിൽ മുറി എടുത്തു. വാടക മൂവായിരം രൂപ. ഓരോരുത്തരും ആയിരം വീതം കൊടുത്തു.', en='3 friends take a lodge room for *₹3000.* Each pays *₹1000.*', pay=(2, 0, '₹3000'), item_at=2),
    dict(ml='പിന്നെ മാനേജർ ഓർത്തു, ഇന്ന് വാടക രണ്ടായിരത്തി അഞ്ഞൂറ് മാത്രം. അഞ്ഞൂറ് രൂപ തിരികെ കൊടുക്കാൻ റൂം ബോയിയുടെ കയ്യിൽ കൊടുത്തു.', en='Today\'s rent is only *₹2500.* The manager gives the boy *₹500* to return.', pay=(0, 1, '₹500')),
    dict(ml='റൂം ബോയ് ഇരുനൂറ് രൂപ സ്വന്തം പോക്കറ്റിലിട്ടു. ഓരോരുത്തർക്കും നൂറു രൂപ വീതം തിരികെ കൊടുത്തു.', en='The boy *keeps ₹200* and gives each friend *₹100* back.', pay=(1, 2, '₹300'), bub=(1, '₹200 MINE')),
    dict(ml='ഓരോരുത്തരും കൊടുത്തത് തൊള്ളായിരം. മൂന്നു പേർ കൂടി രണ്ടായിരത്തി എഴുനൂറ്. ബോയിയുടെ കയ്യിൽ ഇരുനൂറ്. ആകെ രണ്ടായിരത്തി തൊള്ളായിരം.', en='Each paid *₹900.* 900 x 3 = 2700. Plus boy\'s 200 = *₹2900.*', sign='2700 + 200 = 2900 ?'),
  ],
  wrong=None,
  q=dict(ml='ബാക്കി നൂറു രൂപ എവിടെ പോയി?', en='Where did the missing *₹100* go?', box='Missing ₹100?'),
  ans=[dict(ml='ഇതൊരു ട്രിക്ക് ആണ്. ഇരുനൂറ് കൂട്ടാൻ പാടില്ല. അത് രണ്ടായിരത്തി എഴുനൂറിന്റെ ഉള്ളിൽ തന്നെയുണ്ട്.', en='A *trick!* The boy\'s 200 is already *inside* the 2700.', line='Friends paid: 2700'),
       dict(ml='രണ്ടായിരത്തി എഴുനൂറ് എന്നാൽ, മുറി വാടക രണ്ടായിരത്തി അഞ്ഞൂറ്, പിന്നെ ബോയിയുടെ ഇരുനൂറ്.', en='2700 = room *2500* + boy *200*', line='2700 = 2500 room + 200 boy'),
       dict(ml='തിരികെ കിട്ടിയ മുന്നൂറ് കൂടി കൂട്ടിയാൽ, കൃത്യം മൂവായിരം. ഒരു രൂപ പോലും കാണാതായിട്ടില്ല!', en='2700 + 300 returned = *₹3000.* Nothing is *missing!*', line='2700 + 300 back = 3000')],
  stamp='NOTHING MISSING', short='nothing is missing: 2700 = 2500 room + 200 boy, +300 returned = 3000'))
