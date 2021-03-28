# gtts_audio.py


# Standard library
from io import BytesIO
import os
import pathlib

# Third party libaries
from gtts import gTTS

# Our libraries
from tts_lib.audio_generator import AudioGenerator


class GTTSAudio(AudioGenerator):
    def __init__(self, audio_directory):
        self._audio_dir = audio_directory
        self._suffix = ".mp3"

    @property
    def prefix(self):
        return "gtts_"

    def set_voice(self, voice):
        pass

    def generate_audio_file(self, text, file_hint):
        file_name = self.prefix + file_hint + self._suffix
        file_path = pathlib.Path(os.path.join(str(self._audio_dir), file_name))

        if not file_path.exists():
            tts = gTTS(text)
            tts.save(str(file_path))
            print("Generated new audio file {0}".format(file_path.name))

        return file_path

    def generate_direct_audio(self, text):
        file_pointer = BytesIO()
        gTTS(text).write_to_fp(file_pointer)
        file_pointer.seek(0)
        return file_pointer.read()
