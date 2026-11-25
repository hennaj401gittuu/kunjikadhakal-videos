# Midnight Witness v3 – illustrated "ENTIRE story" videos (from 24 Nov 2026)

The channel switched from true crime to **illustrated story documentaries**: the incredible, twisting true stories behind brands, inventions, companies, famous people, empires, disasters, heists, scams and historical turning points. Style reference: "The ENTIRE History of Coca-Cola in 11 Minutes" (stick-figure mascot in hand-drawn scenes, a new picture every few seconds) + a dark documentary look (framed portraits with typed name labels, red circles, serif text reveals, old maps).

## 1. Choosing the subject (the most important step)
Pick stories a curious viewer cannot stop watching. A good subject has ALL of:
- **A famous name or thing people use/know** (Coca-Cola, LEGO, Nintendo, McDonald's, Titanic, the Eiffel Tower, Monopoly, Rolex...) or a jaw-dropping event/person.
- **A huge twist or contrast**: started as something totally different (Nintendo sold playing cards; Coca-Cola was a "medicine"), founder lost everything, a rival stole the idea, a mistake created the product, a scandal nearly killed it, the real inventor was forgotten.
- **Rises and falls**: at least 3 dramatic turns (success -> disaster -> comeback).
- **Concrete details**: dates, places, numbers, names, quotes that can be verified.
Avoid: politics/elections, religion, ongoing wars, living private people, tragedies told for laughs, anything mainly about children being harmed.
Vary subjects day to day (brand, then person, then invention, then historical event...). Never repeat a subject (see the never-repeat list in memory).

### 1b. Mysteries & conspiracy theories (about 2 days a week, and often as Shorts)
Famous mysteries and conspiracy theories get huge curiosity (e.g. "Was Princess Diana's crash really an accident?", the Mary Celeste, the Dyatlov Pass incident, D.B. Cooper, "Paul is dead", the Moon-landing hoax claims). Structure them as an investigation:
1. Hook with the question ("Was it really an accident?"), 2. what actually happened (sourced facts), 3. the theories, each clearly ATTRIBUTED ("some claimed...", "Mohamed Al-Fayed alleged..."), 4. what the evidence and official investigations found (inquests, inquiries, scientists), 5. the verdict, keeping genuine unknowns honest ("to this day nobody knows who D.B. Cooper was").
Rules: never present a debunked theory as true; never say a real person or organisation committed a crime unless a court found it; say "theory", "claim", "alleged". Prefer old, well-documented cases. AVOID: health/vaccine/medical conspiracies, election or political-fraud claims, anything blaming an ethnic or religious group, recent mass-casualty tragedies (under ~20 years) and cases where living private people are accused. Title style: "What REALLY Happened to <X>?" / "<Mystery>: The Theory vs The Truth". MOOD "dark" suits these.

## 2. Narration that hooks
- **First 10 seconds**: the most surprising fact or moment, as a cold open. E.g. "In 1886, a wounded war veteran addicted to morphine invented a 'medicine'. Today, people drink it 2 billion times a day." Then: "This is the ENTIRE story of ..." 
- **Open loops**: tease what is coming ("But that was nothing compared to what happened in 1985.") at least once per chapter.
- **Short punchy sentences**, conversational, a little playful humour, vivid concrete detail. No filler, no "in this video we will".
- **Every 45-60 s a turn**: a twist, a setback, a reveal, a number that shocks.
- End with the payoff + a reflective last line, then "Subscribe for more untold stories" and ask which story to tell next.
- Accuracy still matters: every name, date, number and quote must come from sources read in this run; soften anything uncertain ("reportedly", "legend says"). Mark legends as legends.

## 3. Lengths
- Long video: 10-15 minutes, ~1,500-2,100 words, ~140-190 segments of ONE sentence (or two very short ones) so the picture changes every ~4-5 s. 5-7 chapters (chapter cards optional; use "bigdate" or "words" scenes as section breaks).
- Shorts: 45-60 s, 110-145 words, 6-9 segments, ONE amazing twist from a story (can be a different subject from the long video).

## 4. Script DSL (script.py)
```
MOOD = "curious"          # light music-box score (use "dark" only for grim stories)
TITLE = "The ENTIRE History of LEGO"
S = []
def seg(scene, text, **p): S.append((scene, p, text.strip()))
def chapter(title, sub): S.append(("chapter", {"title": title, "sub": sub}, ""))
```
Shorts also define HOOK = [red line, white line] and COVER (see cover.py).

### Scene catalogue (new, use these most)
- **stick**: illustrated scene. params: bg (workshop | shop | lab | office | boardroom | home | bank | street | town | city | factory | field | farm | war | sea | space | stage | court | plain), sign (text on a shop sign / factory), year (corner date card), trend ("up"/"down" for wall charts in office/boardroom), caption (red top banner, 2-4 words), fx (fire | rain | money | confetti), crowd (true | "cheer"),
  chars = list of {x 0-1, pose (stand point wave cheer think shrug hold sad shock walk present), face (smile grin sad shock smirk angry think neutral), hat (top bowler cap hard crown), outfit (grey navy black red green brown blue white yellow purple khaki orange), mustache, beard, glasses, hair (dark grey bald), apron, facing (1/-1), s (scale, default 1.5), name (typed name tag), bubble (speech bubble, 1-3 words), prop (held: bottle moneybag trophy lightbulb box phone document brick ...)},
  props = list of [kind, x 0-1, y px ground (~800), scale, text] with kind: bottle moneybag cash trophy lightbulb box laptop tv car document gear brick duck phone rocket ship crown sign warning cloud fire.
  Max 3 characters per scene; put the key action/object centre-left so captions (bottom) don't hide it.
- **words**: serif text reveal on dark. lines=["NOT JUST A TOY.", "AN EMPIRE."], strike=0 (strike through a line), small="kicker above".
- **portrait**: framed sepia portrait of a stick character + typed name tags. name, role, year, char={mustache, beard, glasses, hair, hat, outfit, face}, circle=True (red circle on the face).
- **bigdate**: small (e.g. "28 JANUARY"), date ("1958"), place.
- **versus**: left={name, char}, right={name, char}, mid="VS".
### Older scenes still available
map (real borders/roads: pins [[name, lat, lon, hl]], focus [lon0,lat0,lon1,lat1] or state code, title, hi=[] outside the US), timeline (marks [[date, label]]), newspaper (head, sub; no real outlet names), file (head, lines, stamp), board (cards), stats (items [[num, label]]), quote (q, who), photos, evidence, lab, dna, title (big, small), chapter (title, sub), end.
Mix: ~70% stick, ~30% words/portrait/bigdate/map/timeline/newspaper/stats/versus. Never the same non-stick type twice in a row. Change bg often; reuse the same character look (same outfit/mustache/hat) for the same person throughout the video.
No emoji or arrow characters in on-screen text.

## 5. Build
Long: tts_all.py -> render_seg.py (2 workers) -> audio.py -> concat + mux -> two-pass encode < 100 MB -> thumb.json + thumb_stick.py (+ ffmpeg to jpg).
Short: tts_all.py -> render_short.py -> cover.py (COVER obj can be "figure" with a "figure" dict, or any prop/evidence kind).
thumb.json: {"l1": red hook, "l2", "l3", "tag", "face", "pose", "outfit", "hat", "mustache", "glasses", "hair", "prop", "bg": [r,g,b]}.

## 6. Titles
- Long: "The ENTIRE History of <X> in <N> Minutes" or "How <X> went from <A> to <B>" / "The <Person> Who <twist>" (<= 100 chars). Description: 2-line hook, chapters, "Illustrated retelling based on historical sources.", "Subscribe to Midnight Witness for more untold stories.", 3 hashtags (#history #<subject> #documentary). 12-15 tags.
- Shorts: curiosity question/statement + 1 emoji + " #Shorts".
