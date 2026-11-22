---
name: midnight-witness-channel
description: Use when making, scheduling or posting videos, Shorts or Reels for the English true-crime documentary channel Midnight Witness (YouTube + Instagram).
---

# Midnight Witness – solved true-crime documentaries

English true-crime channel. One REAL, SOLVED case per long video (conviction, guilty plea or official closure), told start to finish by a deep male narrator over original illustrated "case-file" visuals. No real footage, no news clips, no photos of real people (the owner chose this so the channel stays safe for monetization).

## Schedule (India time, IST)
- Long video (YouTube, 16:9): 8:00 PM daily.
- Short + Instagram Reel (9:16, 45-60 s): 9:00 PM daily, a DIFFERENT angle or a different solved case, never a cut-down of the long video.
- Post without waiting for the owner's approval; they review after posting.

## Never repeat
Check the never-repeat case list in memory (Midnight Witness project file areas/youtube-channel.md) and the channel's scheduled/published posts in Metricool before choosing a case. Log every case used.

## Choosing a case
- Solved: a court conviction, guilty plea, or officially closed case. Never an open case or a suspect who was never convicted.
- Strong hook or twist (caught decades later, DNA/genealogy, a confession, a mistake that gave them away, a hidden double life).
- Enough public reporting for 25 minutes: court coverage, AP/major outlets, official DA/police statements, Wikipedia as a map of sources only.
- Avoid cases whose main victims are children in sexual crimes; describe sexual violence only in general, non-graphic words; never name surviving rape victims unless they went public themselves.

## Research and accuracy (most important)
- 8-15 web searches/fetches per case. Every date, number, place, quote and name in the script must come from a source you read in this run. If a detail can't be confirmed, leave it out or soften it ("about", "reportedly", "prosecutors said").
- Attribute contested claims ("prosecutors said", "according to court records").
- Quotes: only short, real, sourced quotes (said in court, at arrest, in an interview). Never invent dialogue.
- Keep a sources list; put "Based on court proceedings and public reporting." in the description.

## Script (engine DSL in script.py)
- 25-30 min: ~3,100-3,500 words, ~110-120 segments of 1-3 sentences.
- Structure: cold open on the most dramatic moment (arrest, confession, the twist), a title card, then 7-9 chapters ("Chapter One" + short title), an epilogue, then the end card asking viewers which case to cover next.
- Something new on screen every segment; vary scene types, never the same type 3 times in a row.
- Scene types: house (caption, rain, figure, beam, day), surveil (stamp), quote (q, who), stats (items), sketch, dna, title (big, small), chapter (title, sub), map (pins [[name, lat, lon, hl]], focus [lon0,lat0,lon1,lat1] or state code, title, hi [state codes], route), file (head, lines, fields, stamp, hl), evidence (items [[kind, label]] kinds: hammer can swab tissue phone letter key shoe flashlight mask rope photo car), photos (photos [[kind, caption]] kinds: house street car door window road field), board (cards), phone (txt), newspaper (head, sub), badge, timeline (marks [[date, label]]), truck, lab (a, b), tree (stage 0-4), reveal (name, info), interrogation, court (caption), cell (txt), end.
- Map pins for small towns: give exact lat/lon from your research (the built-in lookup only knows bigger cities).

## Production (engine on the GitHub repo, branch mw-engine)
- Voice: Kokoro am_michael, speed 0.9, pitch x0.93; per-sentence synthesis with 0.38 s gaps.
- Visuals: pycairo 1920x1080 30 fps, real Natural Earth maps, fog/dust atmosphere, film grain, vignette, burned-in Poppins subtitles (max ~9 words per line).
- Audio: dark ambient score ducked under speech, sfx on chapter cards/stamps/phone; -14 LUFS.
- Thumbnail 1280x720: masked silhouette left, 3 short lines of huge Bebas text right (red line 1, white lines 2-3), a red tag (≤10 chars).

## Title, description, tags
- Title (≤100 chars): "<Killer/case name>: <the twist in plain words> | True Crime Documentary".
- Description: 2-line hook; one line on what the video covers; chapters from real start times (00:00 first); "Visuals are illustrations and reconstructions, not real footage. Based on court proceedings and public reporting."; "New solved case every night – subscribe to Midnight Witness."; #truecrime + 2 case hashtags.
- 12-15 tags: true crime, true crime documentary, cold case solved, serial killer documentary (if fitting), crime documentary, + case names, places, method.
- YouTube: NOT made for kids, category People & Blogs / Education-like, public.

## Posting
- Metricool brand "Midnight Witness" (blogId 8274193) ONLY. YouTube and Instagram @midnight.witness_ are connected.
- Upload files to a NEW branch or release on the owner's GitHub video repo and give Metricool the public links; never touch other channels' branches.
