from enum import Enum
import abc
from Voice import CoquiVoice, VoiceType  # Aggiungi questa riga per importare la classe Voice

class VoiceType(Enum):
    COQUI = "coqui"
    ESPEAK = "espeak"
    SYSTEM = "system"

class AppState:
    def __init__(self):
        self.video = None
        self.speakers = []
        self.current_speaker = None

    def add_speaker(self, voice_type, name):
        new_speaker = Voice(voice_type, name)
        self.speakers.append(new_speaker)
        return new_speaker

# Creazione di un'istanza di Voice per un campione
sample_speaker = AppState().add_speaker(VoiceType.COQUI, name="Sample")
sample_speaker.set_voice_params('tts_models/en/vctk/vits', 'p326')
