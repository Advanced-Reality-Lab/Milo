
import google.cloud.speech as speech
import threading
import time


from google.api_core import exceptions
from google.api_core import retry

# Could include other retriable exception types
from google.api_core.exceptions import DeadlineExceeded


predicate_504 = retry.if_exception_type(exceptions.DeadlineExceeded)

# Could configure deadline, etc.
retry_504 = retry.Retry(predicate_504)



def gen_run(generator):
    for i,g in enumerate(generator):
        print("in gen run  --",i)
        # if g is None:
            # raise StopIteration
        yield speech.StreamingRecognizeRequest(audio_content=g)

class StreamAsyncSender:
    def __init__(self):
        self.client = speech.SpeechClient()
        self.stream = None
        self.transcription = []
        self.thread = None
        self.should_run = True

    def send_to_stt(self, generator):
        while self.should_run:
            client = speech.SpeechClient()
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code='en-US',
                enable_automatic_punctuation=True,
                model='phone_call'

            )

            streaming_config = speech.StreamingRecognitionConfig(
                config=config, interim_results=True
            )
            requests = gen_run(generator)
           

            responses = client.streaming_recognize(streaming_config, requests,timeout=15)
            try:
                for response in responses:
                    if not response.results:
                        continue

                    result = response.results[0]
                    if not result.alternatives:
                        continue
                    transcript = result.alternatives[0].transcript
                    if result.is_final:
                        self.transcription.append(transcript)

            except DeadlineExceeded:
                # pass
                print("long pause, the transcript until now:")
                print(transcript)
                if transcript != self.transcription[-1]:
                    self.transcription.append(transcript)
            except Exception as e:
                print(f"error: {e}")



    def start(self, generator):
        self.should_run = True
        self.thread = threading.Thread(target=self.send_to_stt, args=(generator,))
        self.thread.start()

    def get_transcription(self):
        return ' '.join(self.transcription)

        # return self.transcription
    def save_to_file_and_clear_transcription(self,file_name):
        with open(file_name, 'w') as f:
            f.write(self.get_transcription())
        self.transcription = []

    def stop(self):
        self.should_run = False
        self.thread.join()
        print(f"stoped recoring the full trinscription is:\n{self.get_transcription()}")
