# gcloud_tts_audio.py

import os
import pathlib

from google.cloud import texttospeech
from tts_lib.audio_generator import AudioGenerator


class GcloudAudio(AudioGenerator):
    """ Abstract base class for defining our tts interface """
    def __init__(self, audio_directory):
        self._inited = False
        self._audio_dir = audio_directory
        self._suffix = ".mp3"
        self._tts_client = texttospeech.TextToSpeechClient()
        self._gcloud_prefix = "gcloud_"
        self._voice_map = dict()
        self.__map_voices()
        self._voice = self._voice_map[self.default_voice]
        self._inited = True

    @property
    def init_success(self):
        return self._inited

    @property
    def prefix(self):
        return self._gcloud_prefix + self._voice

    @property
    def default_voice(self):
        return "female 3"

    def available_voices(self):
        return list(self._voice_map.keys())

    def __map_voices(self):
        self._voice_map = {
            "male 1": "en-US-Wavenet-A",
            "male 2": "en-US-Standard-B",
            "male 3": "en-US-Wavenet-B",
            "male 4": "en-US-Standard-D",
            "male 5": "en-US-Wavenet-D",
            "male 6": "en-US-Standard-I",
            "male 7": "en-US-Wavenet-I",
            "male 8": "en-US-Standard-J",
            "male 9": "en-US-Wavenet-J",
            "female 1": "en-US-Wavenet-C",
            "female 2": "en-US-Standard-C",
            "female 3": "en-US-Wavenet-E",
            "female 4": "en-US-Standard-E",
            "female 5": "en-US-Wavenet-F",
            "female 6": "en-US-Wavenet-G",
            "female 7": "en-US-Standard-G",
            "female 8": "en-US-Wavenet-H",
            "female 9": "en-US-Standard-H",
            "uk male 1": "en-GB-Wavenet-B",
            "uk male 2": "en-GB-Standard-B",
            "uk male 3": "en-GB-Wavenet-D",
            "uk male 4": "en-GB-Standard-D",
            "uk female 1": "en-GB-Wavenet-A",
            "uk female 2": "en-GB-Standard-A",
            "uk female 3": "en-GB-Wavenet-C",
            "uk female 4": "en-GB-Standard-C",
            "uk female 5": "en-GB-Wavenet-F",
            "uk female 6": "en-GB-Wavenet-F",
            "in male 1": "en-IN-Wavenet-B",
            "in male 2": "en-IN-Standard-B",
            "in male 3": "en-IN-Wavenet-C",
            "in male 4": "en-IN-Standard-C",
            "in female 1": "en-IN-Wavenet-A",
            "in female 2": "en-IN-Standard-A",
            "in female 3": "en-IN-Wavenet-D",
            "in female 4": "en-IN-Standard-D",
        }

    def set_voice(self, voice):
        self._voice = self._voice_map[voice]

    def __synth_audio(self, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=self._voice,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3)
        response = self._tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config)
        return response

    def generate_audio_file(self, text, file_hint):
        file_name = self.prefix + "_" + file_hint + self._suffix
        file_path = pathlib.Path(os.path.join(str(self._audio_dir), file_name))
        if not file_path.exists():
            audio = self.__synth_audio(text)
            with open(file_path, "wb") as out:
                out.write(audio.audio_content)
                print("Generated new audio file {0}".format(file_path))
        return file_path

    def generate_direct_audio(self, text):
        pass
