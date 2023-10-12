import os
from video import Video
from Voice import CoquiVoice, VoiceType
from diarize import diarize_audio
from synth import synthesize_audio
from vocal_isolation import isolate_vocals
from tabs import ListStreamsTab, ConfigureVoiceTab, SubtitlesTab
from app_state import AppState
from utils import create_output_dir
from spleeter.separator import Separator
from pydub import AudioSegment

# Altri import e definizioni rimossi per brevità

def main():
    # Crea un'istanza di CoquiVoice utilizzando VoiceType.COQUI
    coqui_voice_instance = CoquiVoice(VoiceType.COQUI, name="Coqui Voice Instance")

    # Creazione di una istanza di AppState
    app_state = AppState()

    # Inizializza il video
    local_video_path = "C:\\dubber\\dat\\a.mp4"  # Sostituisci con il tuo percorso
    app_state.video = Video(local_video_path)

    # Diarizzazione audio
    audio_diarization_result = diarize_audio("C:\\dubber\\dat\\a.wav")

    # Sintesi vocale
    synthesized_audio = synthesize_audio("C:\\dubber\\dat\\a.srt")

    # Esegui l'isolamento vocale
    audio_path = 'C:\\dubber\\dat\\a.wav'  # Sostituisci con il tuo percorso
    isolate_vocals(audio_path)

    # Esegui il mixing
    isolated_audio_path = 'C:\\dubber\\dat\\output\\vocals.wav'  # Sostituisci con il percorso effettivo
    background_audio_path = 'C:\\dubber\\dat\\output\\background_audio.wav'  # Sostituisci con il percorso effettivo
    output_path = 'C:\\dubber\\dat\\output\\mixed_audio.wav'  # Sostituisci con il percorso effettivo
    mix_audio(isolated_audio_path, background_audio_path, output_path)

    # Utilizzo dei moduli delle tabs
    list_streams_tab = ListStreamsTab(app_state)
    configure_voice_tab = ConfigureVoiceTab(app_state)
    subtitles_tab = SubtitlesTab(app_state)

if __name__ == "__main__":
    # Creazione della directory di output
    create_output_dir()

    # Inizializza il video
    local_video_path = "C:\\dubber\\dat\\a.mp4"
    app_state.video = Video(local_video_path)

    # Esegui la diarizzazione sul video
    run_diarization(app_state.video.file)
