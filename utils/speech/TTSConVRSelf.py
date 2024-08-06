import os.path
from io import BytesIO

from gtts import gTTS


class TTSConVRSelf:

    def tts_from_file(self, file_name,out_file=None):
        # define variables
        data = open(file_name, 'r').read().replace('\n', ', ')
        if out_file is None:
            out_file = os.path.join(os.path.dirname(file_name),'Output.mp3')
        if os.path.exists(out_file):
            os.remove(out_file)

        # initialize tts, create mp3 and play
        tts = gTTS(data, lang = 'en', slow = False)
        tts.save(out_file)
        return out_file

    def tts_from_text(self, text, out_file):
        pass

        tts = gTTS(text, lang='en', slow=False)
        tts.save(out_file)
        return out_file




if __name__ == '__main__':
    TTSConVRSelf().tts_from_text("Hi, I am a virtual therapist based on artificial intelligence. Please note that I am not a professional counselor. However, sometimes my comments can be useful in helping you get new perspectives for discussion.",
                                 "../../service/initial message.mp3")