# gcloud_tts_audio.py

import os
import pathlib
import logging

from google.cloud import texttospeech
from lib.tts.audio_generator import AudioGenerator

from utils import logger


class GcloudAudio(AudioGenerator):
    """ Abstract base class for defining our tts interface """
    def __init__(self):
        self._inited = False
        self._tts_client = texttospeech.TextToSpeechClient()
        self._voice_map = dict()
        self._locale_map = dict()
        self._gender_map = dict()
        self._map_voices()
        self._voice = self._voice_map[self.default_voice]
        self._locale = self._locale_map[self.default_voice]
        self._gender = self._gender_map[self.default_voice]

    @property
    def default_voice(self):
        return "uk male 1"

    def available_voices(self):
        return list(self._voice_map.keys())

    def _map_voices(self):
        self._voice_map = {
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
            "spanish female 2": "es-US-Neural2-A",
            "cantonese male 1": "yue-HK-Standard-B",
            "cantonese female 1": "yue-HK-Standard-C",
            "filipino male 1": "fil-PH-Wavenet-C",
            "filipino female 1": "fil-PH-Wavenet-B",
            "quebecois male 1": "fr-CA-Wavenet-D",
            "quebecois female 1": "fr-CA-Wavenet-C",
            "french male 1": "fr-FR-Wavenet-D",
            "french female 1": "fr-FR-Wavenet-C",
        }

        self._locale_map = {
            "male 1": "en-US",
            "male 2": "en-US",
            "male 3": "en-US",
            "male 4": "en-USJ",
            "female 1": "en-US",
            "female 2": "en-US",
            "female 3": "en-US",
            "female 4": "en-US",
            "female 5": "en-US",
            "uk male 1": "en-GB",
            "uk male 2": "en-GB",
            "uk male 3": "en-GB",
            "uk male 4": "en-GB",
            "uk female 1": "en-GB",
            "uk female 2": "en-GB",
            "uk female 3": "en-GB",
            "uk female 4": "en-GB",
            "indi male 1": "en-IN",
            "indi male 2": "en-IN",
            "indi male 3": "en-IN",
            "indi male 4": "en-IN",
            "indi female 1": "en-IN",
            "indi female 2": "en-IN",
            "indi female 3": "en-IN",
            "indi female 4": "en-IN",
            "aussie male 1": "en-AU",
            "aussie male 2": "en-AU",
            "aussie female 1": "en-AU",
            "aussie female 2": "en-AU",
            "viet male 1": "vi-VN",
            "viet male 2": "vi-VN",
            "viet female 1": "vi-VN",
            "viet female 2": "vi-VN",
            "chinese test 1": "cmn-CN",
            "jp female 1": "ja-JP",
            "jp male 1": "ja-JP",
            "spanish male 1": "es-US",
            "spanish female 1": "es-US",
            "spanish female 2": "es-US",
            "cantonese male 1": "yue-HK",
            "cantonese female 1": "yue-HK",
            "filipino male 1": "fil-PH",
            "filipino female 1": "fil-PH",
            "quebecois male 1": "fr-CA",
            "quebecois female 1": "fr-CA",
            "french male 1": "fr-FR",
            "french female 1": "fr-FR",
        }

        self._gender_map = {
            "male 1": texttospeech.SsmlVoiceGender.MALE,
            "male 2": texttospeech.SsmlVoiceGender.MALE,
            "male 3": texttospeech.SsmlVoiceGender.MALE,
            "male 4": texttospeech.SsmlVoiceGender.MALE,
            "female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "female 2": texttospeech.SsmlVoiceGender.FEMALE,
            "female 3": texttospeech.SsmlVoiceGender.FEMALE,
            "female 4": texttospeech.SsmlVoiceGender.FEMALE,
            "female 5": texttospeech.SsmlVoiceGender.FEMALE,
            "uk male 1": texttospeech.SsmlVoiceGender.MALE,
            "uk male 2": texttospeech.SsmlVoiceGender.MALE,
            "uk male 3": texttospeech.SsmlVoiceGender.MALE,
            "uk male 4": texttospeech.SsmlVoiceGender.MALE,
            "uk female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "uk female 2": texttospeech.SsmlVoiceGender.FEMALE,
            "uk female 3": texttospeech.SsmlVoiceGender.FEMALE,
            "uk female 4": texttospeech.SsmlVoiceGender.FEMALE,
            "indi male 1": texttospeech.SsmlVoiceGender.MALE,
            "indi male 2": texttospeech.SsmlVoiceGender.MALE,
            "indi male 3": texttospeech.SsmlVoiceGender.MALE,
            "indi male 4": texttospeech.SsmlVoiceGender.MALE,
            "indi female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "indi female 2": texttospeech.SsmlVoiceGender.FEMALE,
            "indi female 3": texttospeech.SsmlVoiceGender.FEMALE,
            "indi female 4": texttospeech.SsmlVoiceGender.FEMALE,
            "aussie male 1": texttospeech.SsmlVoiceGender.MALE,
            "aussie male 2": texttospeech.SsmlVoiceGender.MALE,
            "aussie female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "aussie female 2": texttospeech.SsmlVoiceGender.FEMALE,
            "viet male 1": texttospeech.SsmlVoiceGender.MALE,
            "viet male 2": texttospeech.SsmlVoiceGender.MALE,
            "viet female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "viet female 2": texttospeech.SsmlVoiceGender.FEMALE,
            "chinese test 1": texttospeech.SsmlVoiceGender.FEMALE,
            "jp female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "jp male 1": texttospeech.SsmlVoiceGender.MALE,
            "spanish male 1": texttospeech.SsmlVoiceGender.MALE,
            "spanish female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "spanish female 2": texttospeech.SsmlVoiceGender.FEMALE,
            "cantonese male 1": texttospeech.SsmlVoiceGender.MALE,
            "cantonese female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "filipino male 1": texttospeech.SsmlVoiceGender.MALE,
            "filipino female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "quebecois male 1": texttospeech.SsmlVoiceGender.MALE,
            "quebecois female 1": texttospeech.SsmlVoiceGender.FEMALE,
            "french male 1": texttospeech.SsmlVoiceGender.MALE,
            "french female 1": texttospeech.SsmlVoiceGender.FEMALE,
        }


    def set_voice(self, voice):
        self._voice = self._voice_map[voice]
        self._locale = self._locale_map[voice]
        self._gender = self._gender_map[voice]

    def _synth_audio(self, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=self._locale,
            name=self._voice,
            ssml_gender=self._gender)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3)
        logger.debug("generating voice for " + self._voice)
        response = self._tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config)
        logger.debug("generating voice done")
        return response

    def generate_direct_audio(self, text):
        audio = self._synth_audio(text)
        return audio.audio_content
