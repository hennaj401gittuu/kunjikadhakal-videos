import sys, torch
from TTS.utils.synthesizer import Synthesizer
torch.set_num_threads(2)
_s=None
def get():
    global _s
    if _s is None:
        _s=Synthesizer(tts_checkpoint='/home/claude/tts/ml/fastpitch/best_model.pth',tts_config_path='/home/claude/tts/ml/fastpitch/config.json',
          tts_speakers_file='/home/claude/tts/ml/fastpitch/speakers.pth',vocoder_checkpoint='/home/claude/tts/ml/hifigan/best_model.pth',vocoder_config='/home/claude/tts/ml/hifigan/config.json',use_cuda=False)
    return _s
def say(text, speaker, out):
    s=get(); wav=s.tts(text, speaker_name=speaker); s.save_wav(wav, out)
if __name__=='__main__':
    import time;t=time.time()
    say('ഒരിടത്ത് ഒരു കുഞ്ഞു മുയൽ ഉണ്ടായിരുന്നു. അവന്റെ പേര് ചിന്നു എന്നായിരുന്നു!','female','/home/claude/t_f.wav')
    say('ഹലോ കൂട്ടുകാരേ, ഇന്ന് നമുക്ക് ഒരു പുതിയ കഥ കേൾക്കാം.','male','/home/claude/t_m.wav')
    print('took',time.time()-t)
