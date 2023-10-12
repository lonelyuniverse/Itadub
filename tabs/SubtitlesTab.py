import utils
import app_state
import diarize

def process_subtitles():
    # Run diarization
    diarize.run_diarization(app_state.video)

if __name__ == "__main__":
    # Esegui il processo di elaborazione dei sottotitoli
    process_subtitles()
