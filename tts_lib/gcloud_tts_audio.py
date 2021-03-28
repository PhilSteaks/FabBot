# gcloud_tts_audio.py

import os
import pathlib

from google.cloud import texttospeech
from tts_lib.audio_generator import AudioGenerator

k_default_voice = "female 3"


class GcloudAudio(AudioGenerator):
    """ Abstract base class for defining our tts interface """
    def __init__(self, audio_directory):
        self._audio_dir = audio_directory
        self._suffix = ".mp3"
        self._tts_client = texttospeech.TextToSpeechClient()
        self._gcloud_prefix = "gcloud_"
        self._voice_map = dict()
        self.__map_voices()
        self._voice = self._voice_map[k_default_voice]

    @property
    def prefix(self):
        return self._gcloud_prefix + self._voice

    def available_voices(self):
        return list(self._voice_map.keys())

    def __map_voices(self):
        self._voice_map = {
            "male 1": "en-US-Standard-B",
            "male 2": "en-US-Standard-D",
            "male 3": "en-US-Standard-I",
            "male 4": "en-US-Standard-J",
            "female 1": "en-US-Standard-C",
            "female 2": "en-US-Standard-E",
            "female 3": "en-US-Standard-G",
            "female 4": "en-US-Standard-H",
        }

    def set_voice(self, voice):
        self._voice = self._voice_map[voice]

    def generate_audio_file(self, text, file_hint):
        file_name = self.prefix + "_" + file_hint + self._suffix
        file_path = pathlib.Path(os.path.join(str(self._audio_dir), file_name))
        if not file_path.exists():
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=self._voice,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3)
            response = self._tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config)

            with open(file_path, "wb") as out:
                out.write(response.audio_content)
                print("Generated new audio file {0}".format(file_path))
        return file_path

    def generate_direct_audio(self, text):
        pass
