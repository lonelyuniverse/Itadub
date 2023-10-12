"""
The Video class represents a reference to a video from either a file or web link. This class should implement the ncessary info to dub a video.
"""

from io import StringIO
import time
import ffmpeg
import utils
from pydub import AudioSegment
from dub_line import load_subs, isnt_target_language
import json
import numpy as np
import librosa
import soundfile as sf

local_video_path = "C:\\dubber\\dat\\a.mp4"


class Video:
    def __init__(self, video_path, loading_progress_hook=print):
        self.start_time = self.end_time = 0
        self.downloaded = False
        self.subs = self.subs_adjusted = []
        self.background_track = self.vocal_track = None
        self.speech_diary = self.speech_diary_adjusted = None
        self.load_video(video_path, loading_progress_hook)

    def load_video(self, video_path, progress_hook=print):
        self.downloaded = False
        self.file = video_path

    def update_time(self, start, end):
        self.start_time = start
        self.end_time = end
        # clamp the subs to the crop time specified
        start_line = utils.find_nearest([sub.start for sub in self.subs], start)
        end_line = utils.find_nearest([sub.start for sub in self.subs], end)
        self.subs_adjusted = self.subs[start_line:end_line]
        if self.speech_diary:
            self.update_diary_timing()

# Creare un'istanza di Video con il percorso del file locale
video = Video(local_video_path)

def list_streams(self):
    probe = ffmpeg.probe(self.file)["streams"]
    if self.downloaded:
        subs = [{"name": stream[-1]['name'], "stream": stream[-1]['filepath']} for stream in self.yt_sub_streams.values()]
    else:
        subs = [{"name": stream['tags'].get('language', 'unknown'), "stream": stream['index']} for stream in probe if stream["codec_type"] == "subtitle"]
    return {
        "audio": [stream for stream in probe if stream["codec_type"] == "audio"],
        "subs": subs
    }

def get_snippet(self, start, end):
    return self.audio[start*1000:end*1000]

# Crops the video's audio segment to reduce memory size
def crop_audio(self, isolated_vocals):
    # ffmpeg -i .\saiki.mkv -vn -ss 84 -to 1325 crop.wav
    source_file = self.vocal_track if isolated_vocals and self.vocal_track else self.file
    output = utils.get_output_path(source_file, "-crop.wav")
    (
        ffmpeg
        .input(self.file, ss=self.start_time, to=self.end_time)
        .output(output)
        .global_args('-loglevel', 'error')
        .global_args('-vn')
        .run(overwrite_output=True)
    )
    return output

def filter_multilingual_subtitles(self, progress_hook=None):
    multi_lingual_subs = []
    for i, sub in enumerate(self.subs_adjusted):
        snippet = self.get_snippet(sub.start, sub.end).export(utils.get_output_path('video_snippet', '.wav'), format="wav").name
        if isnt_target_language(snippet):
            multi_lingual_subs.append(sub)
        progress_hook(i, f"{i}/{len(self.subs_adjusted)}: {sub.text}")
    self.subs_adjusted = multi_lingual_subs
    progress_hook(-1, "done")
	# This funxion is is used to only get the snippets of the audio that appear in subs_adjusted after language filtration or cropping, irregardless of the vocal splitting.
	# This should be called AFTER filter multilingual and BEFORE vocal isolation
	# OKAY THERE HAS TO BE A FASTER WAY TO DO THIS X_X

# def isolate_subs(self):
#     base = AudioSegment.silent(duration=self.duration*1000, frame_rate=self.audio.frame_rate, channels=self.audio.channels, frame_width=self.audio.frame_width)
#     samples = np.array(base.get_array_of_samples())
#     frame_rate = base.frame_rate
#
#     for sub in self.subs_adjusted:
#         copy = np.array(self.get_snippet(sub.start, sub.end).get_array_of_samples())
#         start_sample = int(sub.start * frame_rate)
#         end_sample = int(sub.end * frame_rate)
#
#         # Ensure that the copy array has the same length as the region to replace
#         copy = copy[:end_sample - start_sample]  # Trim if necessary
#
#         samples[start_sample:end_sample] = copy
#
#     return AudioSegment(
#         samples.tobytes(),
#         frame_rate=frame_rate,
#         sample_width=base.sample_width,  # Adjust sample_width as needed (2 bytes for int16)
#         channels=base.channels
#     )

def isolate_subs(self, subs):
    # empty_audio = AudioSegment.silent(self.duration * 1000, frame_rate=self.audio.frame_rate)
    empty_audio = self.audio
    first_sub = subs[0]
    empty_audio = empty_audio[0:first_sub.start].silent((first_sub.end-first_sub.start)*1000)
    for i, sub in enumerate(subs[:-1]):
        print(sub.text)
        empty_audio = empty_audio[sub.end:subs[i+1].start].silent((subs[i+1].start-sub.end)*1000, frame_rate=empty_audio.frame_rate, channels=empty_audio.channels, sample_width=empty_audio.sample_width, frame_width=empty_audio.frame_width)

    return empty_audio

def run_dubbing(self, progress_hook=None):
    total_errors = 0
    operation_start_time = time.process_time()
    empty_audio = AudioSegment.silent(self.duration * 1000, frame_rate=22050)
    status = ""
    # with concurrent.futures.ThreadPoolExecutor(max_workers=100) as pool:
    #     tasks = [pool.submit(dub_task, sub, i) for i, sub in enumerate(subs_adjusted)]
    #     for future in concurrent.futures.as_completed(tasks):
    #         pass
    for i, sub in enumerate(self.subs_adjusted):
        status = f"{i}/{len(self.subs_adjusted)}"
        progress_hook(i, f"{status}: {sub.text}")
        try:
            line = sub.dub_line_file(False)
            empty_audio = empty_audio.overlay(line, sub.start*1000)
        except Exception as e:
            print(e)
            total_errors += 1
    self.dub_track = empty_audio.export(utils.get_output_path(self.file, '-dubtrack.wav'), format="wav").name
    progress_hook(i+1, "Mixing New Audio")
    self.mix_av(mixing_ratio=1)
    progress_hook(-1)
    print(f"TOTAL TIME TAKEN: {time.process_time() - operation_start_time}")
    # print(total_errors)

def mix_av(self, mixing_ratio=1, dubtrack=None, output_path=None):
    # i hate python, plz let me use self in func def
    if not dubtrack:
        dubtrack = self.dub_track
    if not output_path:
        output_path = utils.get_output_path(self.file, '-dubbed.mkv')

    input_video = ffmpeg.input(self.file)
    input_audio = input_video.audio
    if self.background_track:
        input_audio = ffmpeg.input(self.background_track)
    input_dub = ffmpeg.input(dubtrack).audio

    mixed_audio = ffmpeg.filter([input_audio, input_dub], 'amix', duration='first', weights=f"1 {mixing_ratio}")

    output = (
        ffmpeg.output(input_video['v'], mixed_audio, output_path, vcodec="copy", acodec="aac")
        .global_args('-loglevel', 'error')
        .global_args('-shortest')
    )
    ffmpeg.run(output, overwrite_output=True)

def change_subs(self, stream_index=-1):
    if self.downloaded:
        sub_path = list(self.yt_sub_streams.values())[stream_index][-1]['filepath']
        self.subs = self.subs_adjusted = load_subs(utils.get_output_path(sub_path, '.srt'), sub_path)
    else:
        sub_path = utils.get_output_path(self.file, '.srt')
        ffmpeg.input(self.file).output(sub_path, map=f"0:s:{stream_index}").run(overwrite_output=True)
        self.subs = self.subs_adjusted = load_subs(sub_path)

def change_audio(self, stream_index=-1):
    audio_path = utils.get_output_path(self.file, f"-${stream_index}.wav")
    ffmpeg.input(self.file).output(audio_path, map=f"0:a:{stream_index}").run(overwrite_output=True)
    self.audio = AudioSegment.from_file(audio_path)

if __name__ == "__main__":
    # Qui puoi eseguire le operazioni desiderate sul video
    # Ad esempio, puoi aggiornare i tempi e avviare il doppiaggio
    video.update_time(10, 30)  # Esempio: aggiorna il tempo di inizio e fine
    video.run_dubbing()  # Esempio: avvia il processo di doppiaggio