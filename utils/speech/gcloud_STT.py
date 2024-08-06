# import speech_recognition as sr
from google.cloud import speech


def transcribe_file(speech_file):
    """Transcribe the given audio file asynchronously."""
    from google.cloud import speech

    client = speech.SpeechClient()

    with open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    """
     Note that transcription is limited to a 60 seconds audio file.
     Use a GCS file for audio longer than 1 minute.
    """
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )


    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    sentence = []
    for result in response.results:
        sentence.append(result.alternatives[0].transcript)
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))
    return " ".join(sentence)


def transcribe_streaming(stream_file):
    """Streams transcription of the given audio file."""
    import io
    from google.cloud import speech

    client = speech.SpeechClient()

    with io.open(stream_file, "rb") as audio_file:
        content = audio_file.read()

    # # In practice, stream should be a generator yielding chunks of audio data.
    stream = [content]

    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )
    ful_trans = []
    for response in responses:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        for result in response.results:
            if result.is_final:
                ful_trans.append(result.alternatives[0].transcript)
            # print("Finished: {}".format(result.is_final))
            # print("Stability: {}".format(result.stability))
            # alternatives = result.alternatives
            # The alternatives are ordered from most likely to least.
            # for alternative in alternatives:
            #     print("Confidence: {}".format(alternative.confidence))
            #     print(u"Transcript: {}".format(alternative.transcript))
        return "".join(ful_trans)


class STTConVRSelf:

    def __init__(self):
        # Creating a Recognizer instance
        print("in gcloud recognition")
        with open('./config/speechToText-18aa7780e149.json') as file:
            self.cred = file.read()

        # self.r = sr.Recognizer()

    def stt(self, audio_file_name,new_file_name='newFile'):

        # Creating a Audio file instance pip install SpeechRecognition
        # This class can be initialized with the path to an audio file and provides
        # a context manager interface for reading and working with the file’s contents.
        # audio_wav = sr.AudioFile(audio_file_name)

        # with audio_wav as source:
            # Cleaning the audio source from beckround noise
            # self.r.adjust_for_ambient_noise(source)

            # Using record() to Capture Data From a File
            # audio = self.r.record(source)

            # Crating a new txt file in the relevent Path
            # try:
                new_file_name = new_file_name + '.txt'
                myText = open(new_file_name, 'w')
                # sentence = self.r.recognize_google_cloud(audio,credentials_json=self.cred)

                sentence = transcribe_streaming(audio_file_name)
                myText.write(sentence)
                myText.close()
                return sentence
            # except sr.UnknownValueError:
            #     return "Google Speech Recognition could not understand audio"
            # except sr.RequestError as e:
            #     return "Could not request results from Google Speech Recognition service; {0}".format(e)
