import app_state
import vocal_isolation

def on_audio_selection(self, event):
    app_state.video.change_audio(self.rb_audio.GetSelection())
    
def on_subtitle_selection(self, event, streams):
    app_state.video.change_subs(stream_index=self.rb_subs.GetSelection())
    self.context.tab_subtitles.create_entries()

def remove_vocals(self, event):
    vocal_isolation.separate_file(app_state.video)
