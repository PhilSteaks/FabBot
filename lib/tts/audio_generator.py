# audio_generator.py

from abc import ABCMeta, abstractmethod


class AudioGenerator(metaclass=ABCMeta):
    """ Abstract base class for defining our tts interface """
    def __init__(self):
        pass

    @abstractmethod
    def set_voice(self, voice):
        pass

    @abstractmethod
    def generate_direct_audio(self, text):
        """ Generates a bytes object containing the audio
        """
