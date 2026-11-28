# Kunjikadhakal mystery engine

Engine for the Kunjikadhakal mystery/riddle Shorts and long videos.

## Setup (cloud session)
1. Copy files: `pz/*` -> /home/claude/pz/, `ml/audio.py` -> /home/claude/ml/audio.py, `mltts.py` -> /home/claude/mltts.py
2. Malayalam TTS model (AI4Bharat): download https://github.com/AI4Bharat/Indic-TTS/releases/download/v1-checkpoints-release/ml.zip, unzip to /home/claude/tts/ (so /home/claude/tts/ml/fastpitch/best_model.pth exists); in ml/fastpitch/config.json set the speakers_file path to the absolute /home/claude/tts/ml/fastpitch/speakers.pth.
   pip install --break-system-packages torch torchaudio coqui-tts torchcodec pycairo soundfile scipy pillow
3. Fonts: copy Poppins-Bold.ttf / Poppins-ExtraBold.ttf (and Baloo Chettan 2) to ~/.fonts and run `fc-cache -f`.
4. Example: `python3 pz/case_houseboat.py stills` (contact-sheet stills) then `python3 pz/case_houseboat.py` (renders a 1080x1920 Short).

## wd.py
- `solve(names, stmts)` checks a whodunit has exactly ONE answer (statements: ('did',X), ('not',X), ('liar',X), ('honest',X)). `build()` asserts it.
- Scenes: lineup (99% FAIL), place (crime location card), police, rule (1 TRUTH / 2 LIES), solo (suspect in spotlight + bubble), summary (+ typing ANSWER box + Follow).
- Narrator: male, pitch 1.15, tempo 1.20 (matches the reference, ~155 Hz, fast, almost no pauses). All on-screen text English; narration Malayalam.
- Extend with new scene functions for logic riddles (countdown clock, eye-line arrows) and door/choice riddles (timer bar, reveal).

## long/ (16:9 whodunit marathon, added 24 Nov 2026)
- `long/longvid.py`: 1920x1080 scenes (teaser, case title card, 3-suspect line-up with bubbles, rule pill, 5 s pause clock, per-suspect truth table test, reveal + "+1 POINT", score/subscribe end). Copy long/* to /home/claude/long/.
- `long/cases.py`: case list (each verified with solve()); `fix.py` brute-forces unique statement sets.
- `python3 run.py stills` -> contact stills; `run.py audio` -> long.wav + meta.json (chapters, answers); `run.py video 0 2` and `run.py video 1 2` render halves in parallel, then concat + mux.
- wd.py `flat()` now has a 'tea' (Munnar tea estate) location.

## Logic riddle + Which Door (added 24 Nov 2026)
- `pz/riddle_bridge.py`: logic-riddle Short pattern (jail yard at sunset, striped prisoners with ball-and-chain, red LED countdown clock on a pole, paper signs, dashed orange arrows, thought bubbles, 5 s think clock, typing ANSWER + Follow). BFS check of the answer.
- `long/doors.py` (+ doors_data.py, doors_beats.py, dthumb.py): 16:9 "Which Door?" marathon — corridor with circled-number doors, orange trench-coat detective host, ~30 hazard rooms (`hazard(kind)`), red timer bar, 5 s pause clock, wrong-door X, reveal walk-in, reason card + "+1 POINT". `python3 doors.py stills|audio|video 0 2`.

## Money brain-teaser marathon + Kovalam case (added 24 Nov 2026, run C)
- `money/money.py` (+ stories.py, verify.py, thumb.py): 16:9 "Money Brain Teasers Marathon" in paper-cut style (peach sky, pale sun, paper clouds, teal hills, Kerala shop row with name boards, mundu/saree figures, ₹ notes passed hand to hand, price bubbles, paper signs, deep-blue caption band, 5→1 think clock, ruled answer card + red stamp, +1 POINT, halfway card, comment-box end + Subscribe). Copy money/* to /home/claude/money/. `python3 verify.py` checks every answer; `python3 money.py stills|audio|video 0 2`.
- Narration numbers must be spelled in Malayalam words (the TTS has no digits).
- wd.py: new `flat()` location 'beach' (Kovalam lighthouse + resort cottage) and suspect cap 'bun' (woman's hair bun with jasmine).

## Money-story Short (9:16, added 25 Nov 2026, Kandupidi run B)
- `money/money_short.py` (+ `ledger_thief.py`): 1080x1920 paper-cut money Short (two-shop street, Pappan/thief-in-cap/Leela, night scene, pen-mark note close-up, rice sack, flying notes, STOLEN NOTE stamp, 5→1 clock, comment box ANSWER, +Follow→Following). Deep storyteller voice ('male', 0.88, 1.27) ≈ 123 Hz median; plucked-string bed + coin/register sfx. Copy to /home/claude/money/ next to money.py; `python3 money_short.py stills|render`. For a new story, replace BEATS (pos/pay/pay2/bub/rice/sign/stampit keys).

## Story-riddle Short (9:16, added 25 Nov 2026, Kandupidi run C)
- `money/riddle_short.py`: lateral-thinking story riddle in flat vector style (sunset road with palms + bokeh, Thrissur bank interior + loan form with typed fields, value chips, sunburst shock zoom with sweat drop, red no-sign over LYING/FORGOT, count-up bubbles, night scene with glowing ?, 5→1 clock, brain mascot + comment box ANSWER + Follow→Following). Captions lower-middle (y 1200) with dark outline. Reuses money.py person/bubble/clock5 and money_short.py bulb/comment_box/follow_btn/build_mix. Storyteller voice ('male', 0.88, 1.27) ≈ 125 Hz. Copy next to money.py; `python3 riddle_short.py stills|render`. Replace BEATS for a new riddle.

## Debt-chain money Short (9:16, added 26 Nov 2026, Kandupidi run A)
- `money/debt_short.py` (+ `ledger_debt.py`): variant of money_short.py with 4 characters (Jose/Hamsa/Leela/Traveller), walk=(who, x_from, x_to) entrances/exits, and a `circle` scene (three paper-circle portraits with OWES/PAID arrows and a note travelling round the chain). Storyteller voice ('male', 0.88, 1.33) ≈ 123 Hz.

## Beard story-riddle Short (9:16, added 26 Nov 2026, Kandupidi run B)
- `money/beard_short.py`: riddle_short.py variant (Best Beard contest stage instead of bank, entry card, `beard()` overlay for M.person, 1-20 count bubbles, stacked chips). Riddle: 20+ shaves a day but a long uncut beard (ANSWER: barber). Storyteller voice ('male', 0.88, 1.27) ≈ 111-129 Hz. `python3 beard_short.py stills|render`.

## TRY IT Short (9:16, added 26 Nov 2026, Kandupidi run C)
- `tryit/tryit_short.py`: brain/body trick done along with the video (floating arm / Kohnstamm effect). Soft pseudo-3D kid (yellow T-shirt, jeans; `kid()` with arm angles, moods smile/effort/wow) in a cosy room with a centre doorway, two-line top captions (white + coloured, outlined Poppins ExtraBold), STEP badges, 30 s circular countdown (`countdown()`), x-ray scene with glowing brain + yellow signal line to the shoulder muscle, effect-name card, comment box / share / Follow end. Beats with `at` are pinned to the countdown start. Soft female voice ('female', 0.95, 1.08) ≈ 223-240 Hz; ambient pad + bell bed. Copy to /home/claude/tryit/; `python3 tryit_short.py stills|render`. Replace BEATS/scenes for a new trick.

## Ladder story-riddle Short (9:16, added 27 Nov 2026, Kandupidi run A)
- `money/ladder_short.py`: beard_short.py variant (church wall + 30 ft ladder, measure arrow, SLIP/THUD fall scene that never shows the fall height, SAFETY CHECK card, Dr. Mini with stethoscope). Riddle: painter falls off a 30-foot ladder, not a scratch (ANSWER: bottom step). Captions/CTA never name a channel. `python3 ladder_short.py stills|render`.

## Detective Arjun episodes (16:9 long, added 27 Nov 2026) — `detective/`
- `chars.py`: RECURRING CHARACTERS, always reuse so they look identical: `ARJUN` (olive-khaki trench coat, dark belt, brass buttons, brown flat cap, moustache, notebook) and `MEENU` (round black glasses, side ponytail + yellow clip, teal kurta, white dupatta, mustard sling bag, banana chips). `human(ctx, x, y, s, spec, pose, t)` draws shaded full-body characters with realistic proportions (feet at x,y; s=1 -> 6 ft man ~900 px). Pose: face ±1, expr (neutral/smile/shock/scared/smug/think/sad/angry/laugh), talk 0-1, arm modes (down, hip, point, chin, notebook, write, chips, eat, up, wave, cuffed, give, torch, mop, hold) via 2-bone IK, walk, tilt, look. Guest specs: RAVI, VELU, SHANTHA, FAIZAL, POLICE. `python3 chars.py` writes a character test sheet.
- `bgs.py`: cached 2x backgrounds: Kerala palace museum exterior at night, gallery (dark/lit), store room, line-up room with feet height chart, parking lot, card backgrounds.
- `script.py`: beats (sec, speaker, Malayalam line, shot list, timer/card/ans/markers). Voices: narrator ('male',1.05,1.0) ≈148 Hz, Arjun ('male',0.97,0.98), Meenu ('female',0.92,1.0) ≈230 Hz.
- `ep.py`: shot system (each listed shot split into ~2 s sub-shots with Ken Burns, camera clamped to the world), clue inserts (lock, footprint + 4 sole options, CCTV monitor with date, ladder cobweb, receipt with date circle, recap tiles, who-did-it line-up), overlays (section badge, yellow timer bar + PAUSE pill, green answer box, blue numbered markers), cross-dissolves between sections, mystery pizzicato bed + ticks/stings/alarm, -14 LUFS. `python3 ep.py stills|audio|video <i> <n>|final <n>`; `case_check.py` proves exactly one culprit; `thumb.py` makes the black-bar thumbnail.
- For a new episode: write a new script.py + case_check.py and add/replace scene branches in `shot()`; keep chars.py specs unchanged.

## Ring-finger TRY IT Short (9:16, added 27 Nov 2026, Kandupidi run B)
- `tryit/ring_short.py`: ring finger that won't lift (hand flat, middle finger folded under). Reuses tryit_short.py (room, kid, caption2, badge, tag, comment box, follow). New: wooden `table()` background, top-down pseudo-3D `hand()` (per-finger lift 0-1, middle `fold`, ring `tremble`, `glow`, `xray`), x-ray `tendons()` with pink juncturae-tendinum bridges + PULLED TIGHT arrow, 10 s `countdown()`, OWN MUSCLE / NO EXTRA MUSCLE labels, JUNCTURAE TENDINUM name card. Female voice ≈ 230 Hz. `python3 ring_short.py stills|render`.

## Theatre whodunit (9:16, added 27 Nov 2026, Kandupidi run C)
- `pz/case_theatre.py`: "ONLY 1 IS LYING" variant (`n_true=2`; rule beats take `truth_label`/`lies_label`, summary takes `rule_label`). New wd.py `flat()` location 'theatre' (Star Cinemas single-screen hall at night: marquee bulbs, NIGHT SHOW poster, ticket counter, red projection-room window). End card no longer names a channel ("Follow for more mysteries!"). ANSWER: Jithin.

## Two-noses TRY IT Short (9:16, added 28 Nov 2026, Kandupidi run A)
- `tryit/nose_short.py`: Aristotle's illusion (cross middle over index, eyes closed, rub the nose tip: feels like two noses). New front-view hand `vhand()` (fingers up, crossing 0-1, glowing OUTER sides), `hand_at_nose()`, face close-up `face()` (kid at 2.2x, ghost noses). tryit_short.kid() now takes `nose=True` and mood 'closed' (eyes shut). Reuses ring_short countdown/table. Female voice ≈ 235 Hz. `python3 nose_short.py stills|render`.

## Hard Malayalam Riddles long video (16:9, added 28 Nov 2026) — `riddles/`
- `rbgs.py`: cached 2x backgrounds: studio (Arjun's office, chalkboard), Palakkad coconut market, Kottayam church clock tower (evening), Alappuzha backwater, Ammini Bakery (Kozhikode), paddy fields + 2 parallel tracks with STATION A/B, Jose Jewellery (Thrissur) + card backgrounds.
- `rv.py`: renderer (same shot system as detective/ep.py: ~2 s sub-shots, Ken Burns, cross-dissolves, RIDDLE n/6 badge, big RIDDLE n intro, question card + yellow timer bar + PAUSE pill, green ANS box). Props: clock_face (with angle arc), boat, dog, hen, rice sack, laddoo jar, digital scale, train, parrot, gold coin, brass balance. Answer cards per riddle + 'why people get it wrong' red cards + score/subscribe end.
- `script.py`: beats for #1 (coconut profit 30; clock 3:15 = 7.5°; dog/hen/rice boat 7 trips; heavy laddoo jar = jar 4 via 1..5 laddoos; trains 150 km at 40/35 + parrot 60 = 120 km; 9 coins 1 lighter = 2 weighings). `verify.py` checks every answer (BFS/brute force).
- `chars.py` (detective/) gained bottom='mundu' (white kasavu mundu) and guest specs RAJU, KUTTAN, AMMINI, JOSE. ARJUN/MEENU unchanged.
- For #N: write a new script.py (6 riddles, ~8:00-8:30; keep speech ~420 s + 6×7 s timers), add any new scenes in rv.py `shot()`, update verify.py. `python3 rv.py stills|audio|video i n|final n`; `thumb.py` makes the black-bar thumbnail.
- Voice note: Malayalam TTS ~2.3 words/s; the first draft of #1 was 10:12 and had to be cut to 8:14 — write tight lines.
