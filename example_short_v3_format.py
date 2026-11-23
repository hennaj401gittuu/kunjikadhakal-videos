# FORMAT EXAMPLE ONLY (test narration, not a real story). See README_v3.md.
MOOD = "curious"
HOOK = ["A CARPENTER LOST EVERYTHING", "THEN BUILT AN EMPIRE"]
COVER = {"lines": ["HIS FACTORY", "BURNED", "TWICE"], "kicker": "TEST", "obj": "figure", "tag": "TEST", "accent": 2}
S = []
def seg(scene, text, **p): S.append((scene, p, text.strip()))
seg("stick", "This is a test of the new illustrated style.", bg="workshop", year=1932, chars=[{"x": 0.42, "pose": "present", "face": "smile", "mustache": True, "outfit": "grey", "apron": True, "hair": "dark", "name": "THE CARPENTER"}], props=[["duck", 0.72, 600, 1.1]])
seg("words", "Not just a toy. An empire.", lines=["NOT JUST A TOY.", "AN EMPIRE."], strike=0)
seg("stick", "Then, disaster struck.", bg="street", sign="TOY SHOP", chars=[{"x": 0.3, "pose": "walk", "face": "smile", "hat": "bowler", "outfit": "navy"}, {"x": 0.62, "pose": "shock", "face": "shock", "outfit": "red", "bubble": "WHAT?!"}], fx="rain")
seg("stick", "And then the crowd went wild.", bg="stage", chars=[{"x": 0.5, "pose": "cheer", "face": "grin", "outfit": "navy", "glasses": True, "hair": "grey", "prop": "trophy"}], crowd="cheer", fx="confetti")
