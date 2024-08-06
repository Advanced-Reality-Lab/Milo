import speech_recognition as sr

class STTConVRSelf:

    def __init__(self):
        # Creating a Recognizer instance
        print("in sr recognition")
        self.r = sr.Recognizer()

    def stt(self, audio_file_name,new_file_name='newFile'):

        # Creating a Audio file instance pip install SpeechRecognition
        # This class can be initialized with the path to an audio file and provides
        # a context manager interface for reading and working with the file’s contents.
        audio_wav = sr.AudioFile(audio_file_name)

        with audio_wav as source:
            # Cleaning the audio source from beckround noise
            self.r.adjust_for_ambient_noise(source)

            # Using record() to Capture Data From a File
            audio = self.r.record(source)

            # Crating a new txt file in the relevent Path
            try:
                new_file_name = new_file_name + '.txt'
                myText = open(new_file_name, 'w')
                sentence = self.r.recognize_google(audio)

                myText.write(sentence)
                myText.close()
                return sentence
            except sr.UnknownValueError:
                return "Google Speech Recognition could not understand audio"
            except sr.RequestError as e:
                return "Could not request results from Google Speech Recognition service; {0}".format(e)
