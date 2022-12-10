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
        self._map_voices()
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
        return "uk male 1"

    def available_voices(self):
        return list(self._voice_map.keys())

    def _map_voices(self):
        self._voice_map = {
            "movie recap": "movie recap aka default not found voice",
            "male 1": "en-US-Wavenet-A",
            "male 2": "en-US-Wavenet-B",
            "male 3": "en-US-Wavenet-D",
            "male 4": "en-US-Wavenet-J",
            "female 1": "en-US-Wavenet-E",
            "female 2": "en-US-Wavenet-F",
            "female 3": "en-US-Wavenet-G",
            "female 4": "en-US-Wavenet-H",
            "female 5": "en-US-Standard-H",
            "uk male 1": "en-GB-Wavenet-B",
            "uk male 2": "en-GB-Standard-B",
            "uk male 3": "en-GB-Wavenet-D",
            "uk male 4": "en-GB-Standard-D",
            "uk female 1": "en-GB-Wavenet-A",
            "uk female 2": "en-GB-Wavenet-C",
            "uk female 3": "en-GB-Standard-C",
            "uk female 4": "en-GB-Wavenet-F",
            "indi male 1": "en-IN-Wavenet-B",
            "indi male 2": "en-IN-Standard-B",
            "indi male 3": "en-IN-Wavenet-C",
            "indi male 4": "en-IN-Standard-C",
            "indi female 1": "en-IN-Wavenet-A",
            "indi female 2": "en-IN-Standard-A",
            "indi female 3": "en-IN-Wavenet-D",
            "indi female 4": "en-IN-Standard-D",
            "aussie male 1": "en-AU-Wavenet-D",
            "aussie male 2": "en-AU-Wavenet-B",
            "aussie female 1": "en-AU-Neural2-A",
            "aussie female 2": "en-AU-Neural2-C",
            "viet male 1": "vi-VN-Wavenet-D",
            "viet male 2": "vi-VN-Wavenet-B",
            "viet female 1": "vi-VN-Wavenet-A",
            "viet female 2": "vi-VN-Wavenet-C",
            "chinese test 1": "cmn-CN-Wavenet-B",
            "jp female 1": "ja-JP-Wavenet-B",
            "jp male 1": "ja-JP-Wavenet-D",
            "spanish male 1": "es-US-Wavenet-C",
            "spanish female 1": "es-US-Wavenet-A",
            "spanish male 2": "es-US-Neural2-A",
            "cantonese male 1": "yue-HK-Standard-B",
            "cantonese female 1": "yue-HK-Standard-C",
            "filipino male 1": "fil-PH-Wavenet-C",
            "filipino female 1": "fil-PH-Wavenet-B",
            "quebecois male 1": "fr-CA-Wavenet-D",
            "quebecois female 1": "fr-CA-Wavenet-C",
            "french male 1": "fr-FR-Wavenet-D",
            "french female 1": "fr-FR-Wavenet-C",
        }

    def set_voice(self, voice):
        self._voice = self._voice_map[voice]

    def _synth_audio(self, text):
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
            audio = self._synth_audio(text)
            with open(file_path, "wb") as out:
                out.write(audio.audio_content)
                print("Generated new audio file {0}".format(file_path))
        return file_path

    def generate_direct_audio(self, text):
        audio = self._synth_audio(text)
        return audio.audio_content
