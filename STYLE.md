# Tiny Meadow Tales house style: "cozy craft" (from 25 Nov 2026)

The owner loved "Mama Ant's Cookie Day" (Short, 25 Nov 2026) and chose it as the channel's
visual and story style from now on. Reference video: `Mama_Ant_Cookie_Day.mp4` on branch
`tmt-20261125-ant-cookies`. Reference code in this branch:

- `draw.py`: helpers (ease/seg/lerp, ell, rr, radial/linear gradients, text with outline in Fredoka/Pacifico,
  gingham pattern, sparkle, heart, steam), the ant character (`draw_ant` with `Pose`, two-bone IK arms
  `arm_path` so hands can hold props at world positions, `part='body'|'arms'` so props sit between
  body and arms), babies (`draw_baby` with `hold`/`hold_cb`), cat, props (glass `Bowl` with
  back/contents/front layers, egg, shells, butter, whisk, spoon, knife, board, tray, dough balls,
  cookies, canisters with script labels, plate, table with cloth), cached backgrounds
  (`kitchen_bg`, `counter_fg`, `room_bg`, `home_bg`), `warm_glow`, `vignette`.
- `scenes.py`: one function per scene `(ctx, t, d)` + the `SCENES` list with fade in/out; shows how
  each step is timed with `seg()` and eased hand paths.
- `render.py` (pipes BGRA frames to ffmpeg, one file per scene, concat -c copy), `audio.py`
  (numpy plucked-ukulele tune 112 bpm I-vi-IV-V + SFX).
- Fonts: Fredoka (titles, sound words) from google/fonts `ofl/fredoka/Fredoka[wdth,wght].ttf`,
  Pacifico for jar/bag labels. Install into ~/.fonts and `fc-cache -f`.

Copy `draw.py` into your run and build the new story's characters and props in the same way.
Do NOT reuse the ant mother/babies as the main characters of a new story (new characters every story).

## The look
- Soft 3D-ish flat 2D: every shape filled with a radial gradient (light top-left, darker edge),
  no hard black outlines on bodies (thin darker strokes only on eyes, joints, props).
- Warm, golden, cozy light everywhere: cream and peach walls, honey wood, sunlight through an
  arched window, potted and hanging plants, ceramic canisters with green leaf marks, wooden
  utensils on the wall. Finish every frame with `warm_glow()` + `vignette()`.
- Pink gingham is the signature accent (apron, towel, oven mitts, tablecloth trims).
- Characters: big round heads (head ~40% of body height), huge glossy brown eyes with two white
  highlights, lashes for mums/girls, rosy cheek glow, small nose, simple smile or open mouth,
  antennae/ears with gentle sway, blink every ~3.4 s, idle bob. Mums wear an apron; babies wear bibs.
  Happy moments = closed "^ ^" eyes.
- Hands actually hold and use things (IK arms): pick up, pour, crack, stir, whisk, chop, carry.
- Props are big, clear and satisfying: glass bowls showing what is inside and how it changes,
  pouring streams, falling chips, puffs of flour, steam, sparkles, things growing in the oven.
- Sound words pop with an ease-out-back bounce in Fredoka with a thick white outline:
  "crack!", "whisk whisk!", "DING!", "Mmm!", "Yummy!". Hearts float up at happy endings.
- Camera: slow push-ins (3-6% per shot), close medium shot for the "making" steps
  (character behind a counter, props in front), wider shots for arrivals and the ending.

## The stories
Cozy "making something" stories of a little animal family:
1. a small, funny, slightly sneaky start (tiptoeing past a sleeping giant pet to fetch an ingredient,
   a freeze moment when it stirs),
2. coming home to excited babies,
3. a satisfying step-by-step making montage (baking, cooking, building, sewing, gardening, painting,
   wrapping presents, making a snowman...), one clear step per shot,
4. the reveal (oven DING, finished thing) and
5. sharing it with family or friends, with happy munching or playing, hearts and "Yummy!"/"Hooray!".
Keep the lesson gentle (sharing, love, patience, helping, trying, saying thank you).
For the 16:9 long videos, re-lay out the same sets for 1920x1080 (counter across the bottom
third, window left, shelves right) and keep the same look.
