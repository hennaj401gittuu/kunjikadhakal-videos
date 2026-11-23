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
