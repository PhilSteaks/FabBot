from abc import ABCMeta, abstractmethod
class AudioGenerator(metaclass=ABCMeta):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def prefix(self):
        pass

    @abstractmethod
    def set_voice(self, voice):
        pass

    @abstractmethod
    def generate_audio(self, text, filename, voice=""):
        pass
