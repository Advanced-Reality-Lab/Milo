##
# based on the gcloude microphone streaming service example
# https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-infinite-streaming
#

from __future__ import division

import datetime
import os
import re
import sys
import time



from google.cloud import speech

import pyaudio
from six.moves import queue

# Audio recording parameters
from utils.bar_udp_comunicator import BarSockets, get_bar_sockets
from utils.bot.GPT3 import GPT3
from utils.pyrtp import DecodeRTPpacket
from utils.speech.gcloud_tts import text_to_wav

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
STOP = False

def set_stop():
    global STOP
    STOP = True

class BarSocketStream(object):

    def __init__(self, rate, chunk, save_to_file="file_name.raw", save_audio_to_file=True):
        global STOP
        self._rate = rate
        self._chunk = chunk
        STOP = False
        self.soc = get_bar_sockets(on_data_received=self._fill_soc_buffer,
                         send_audio=lambda x, y: print(x, " ", y),
                         send_audio_UDP_IP='', data_received_UDP_IP='0.0.0.0',
                         send_audio_UDP_PORT=3030, data_received_UDP_PORT=7456)
        self.soc.init_run()

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        self.save_audio_to_file = save_audio_to_file
        self.save_to_file = save_to_file


    def __enter__(self):
        if self.save_to_file:
            self.out_file = open(self.save_to_file,'wb')
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        if self.save_to_file:
            self.out_file.close()

    def _fill_soc_buffer(self,data,addr):
        packet = DecodeRTPpacket(data.hex())
        if STOP:
            self._buff.put(None)
        self._buff.put(bytes.fromhex(packet['payload']))
        return None

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        break
                    data.append(chunk)
                except queue.Empty:
                    break
            if self.save_to_file:
                self.out_file.write(b"".join(data))
            yield b"".join(data)


def dummy_response(param):
    return param,""


def listen_print_loop(responses, bar_stream, ip, port, workingDir, voice_name="en-GB-Wavenet-B"):
    gpt = GPT3()
    num_chars_printed = 0
    file_name = os.path.join(workingDir, f"transcript_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M')}.txt")
    fn = open(file_name, 'w')
    try:
        for response in responses:
            if STOP:
                print("Exiting..")
                bar_stream._buff.put(None)
                break

            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            overwrite_chars = " " * (num_chars_printed - len(transcript))



            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + "\r")
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.


                print(transcript + overwrite_chars)
                # send_to_GPT
                chat_response,_ = gpt.predict_sentence(transcript + overwrite_chars)
                print(f"chat_response={chat_response}")
                # add TTS + send signal to unity
                text_ = chat_response
                text_to_wav(voice_name, text_, "./WorkingDir/output.wav")

                # TODO: save transcript and responses to file.
                fn.write(f"[transcript]\n{transcript}\n\n[response]{text_}\n\n")
                fn.flush()
                msg = {'transcript':transcript,"response":text_}
                bar_stream.soc.send_tcp_msg(str(msg).encode("utf-8"),ip,port)
                num_chars_printed = 0
    except Exception as e:
        print(e)
    finally:
        fn.close()


async def listen_print_loop2(responses, bar_stream, workingDir, voice_name="en-GB-Wavenet-B"):
    gpt = GPT3()
    num_chars_printed = 0
    file_name = os.path.join(workingDir, f"transcript_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M')}.txt")
    fn = open(file_name, 'w')
    try:
        for response in responses:
            if STOP:
                print("Exiting..")
                bar_stream._buff.put(None)
                break

            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            overwrite_chars = " " * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + "\r")
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(f"final transcript {transcript} \noverwrite_chars {overwrite_chars}")
                # send_to_GPT
                chat_response, _ = gpt.predict_sentence(transcript + overwrite_chars)
                print(f"chat_response={chat_response}")
                # add TTS + send signal to unity
                text_ = chat_response
                text_to_wav(voice_name, text_, "./WorkingDir/output.wav")
                yield text_
                # TODO: save transcript and responses to file.
                fn.write(f"[transcript]\n{transcript}\n\n[response]{text_}\n\n")
                fn.flush()
                msg = {'transcript': transcript, "response": text_}
                bar_stream.soc.send_tcp_msg(str(msg).encode("utf-8"), ip, port)
                num_chars_printed = 0
    except Exception as e:
        print(e)
    finally:
        fn.close()


async def main_grpc(language_code = "en-US", dirs=None, participant_id='',
              voice_name="en-GB-Wavenet-B", personality_prompt='', name=''):
    print("pre init stt")
    client, streaming_config = initialize_stt_client(language_code)
    print("pre init stt")
    audio_file_name = os.path.join(dirs['audio_dir'], "audio_content.raw")
    with BarSocketStream(RATE, CHUNK, save_to_file=audio_file_name) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        yield await listen_print_loop2(responses, stream, dirs['txt_dir'], voice_name=voice_name)

def main(headset_ip="192.168.1.15",language_code = "en-US",port = 6547,intro_length=3, dirs=None,
         participant_id='',voice_name="en-GB-Wavenet-B",personality_prompt=''):
    # See http://g.co/cloud/speech/docs/languages

    dirs, ip = initialize_directories(dirs, headset_ip)

    client, streaming_config = initialize_stt_client(language_code)

    start_run(client, dirs, ip, port, streaming_config, voice_name)


def start_run(client, dirs, ip, port, streaming_config, voice_name):
    audio_file_name = os.path.join(dirs['audio_dir'], "audio_content.raw")
    with BarSocketStream(RATE, CHUNK, save_to_file=audio_file_name) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses, stream, ip, port, dirs['txt_dir'], voice_name=voice_name)


def initialize_stt_client(language_code):
    print("after wait starting ASR client")
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,

    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )
    return client, streaming_config


def initialize_directories(dirs, headset_ip):
    if dirs is None:
        dirs = {"audio_dir": "audio_dir", "txt_dir": "txt_dir"}
    for k, v in dirs.items():
        if not os.path.isdir(v):
            os.makedirs(v)
    ip = headset_ip
    return dirs, ip


if __name__ == "__main__":
    main()


