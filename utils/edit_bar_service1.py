## /////////////////////
## notifier version
## //////////////////
from __future__ import division

import datetime
import os
import sys
import time

from google.cloud import speech

from six.moves import queue

# Audio recording parameters
from testers_and_tools.scripts import InputSentenceUpdater
from utils.audio.send_audio import send_audio, read_and_send_audio_file
from utils.bar_udp_comunicator import get_bar_sockets
from utils.bot.GPT3 import GPT3
from utils.pyrtp import DecodeRTPpacket
from utils.speech.gcloud_tts import text_to_wav

import asyncio

STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms of audio in each request.
STOP = False

def set_stop():
    global STOP
    STOP = True

def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))

class BarSocketStream(object):

    def __init__(self, rate, chunk, save_to_file="file_name.raw", save_audio_to_file=True):
        self.final_request_end_time = 0
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
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self.start_time = get_current_time()


    def __enter__(self):
        if self.save_to_file:
            self.out_file = open(self.save_to_file,'wb')
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self.closed = True
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
            data = []

            if self.new_stream and self.last_audio_input:

                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:

                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round(
                        (self.final_request_end_time - self.bridging_offset)
                        / chunk_time
                    )

                    self.bridging_offset = round(
                        (len(self.last_audio_input) - chunks_from_ms) * chunk_time
                    )

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

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


def listen_print_loop(responses, bar_stream, ip, port, workingDir,notifier,
                      voice_name="en-GB-Wavenet-B", personality_prompt=''):


    num_chars_printed = 0
    file_name = os.path.join(workingDir, f"transcript_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M')}.txt")
    fn = open(file_name, 'w')
    try:
        for response in responses:
            if STOP:
                print("Exiting..")
                bar_stream._buff.put(None)
                break

            if get_current_time() - bar_stream.start_time > STREAMING_LIMIT:
                bar_stream.start_time = get_current_time()
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
                print(transcript + overwrite_chars)
                notifier.update_notify(new_text=transcript + overwrite_chars)
                num_chars_printed = 0
    except Exception as e:
        print(e)
    finally:
        fn.close()


def main(headset_ip="192.168.1.15",language_code = "en-US",port = 6547,intro_length=3, dirs=None,
         participant_id='',voice_name="en-GB-Wavenet-B",personality_prompt='',notifier=InputSentenceUpdater()):
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
      # a BCP-47 language tag
    # ip = "192.168.1.15"
    # ip = "127.0.0.1"
    # ip = "192.168.0.211"
    # ip = '0.0.0.0'
    # ip = '255.255.255.255''
    if dirs is None:
        dirs = {"audio_dir":"audio_dir","txt_dir":"txt_dir"}
    for k,v in dirs.items():
        if not os.path.isdir(v):
            os.makedirs(v)

    ip = headset_ip
    #time.sleep(intro_length)
    #time.sleep(intro_length)
    print("after wait starting ASR client")

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=language_code,


    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    audio_file_name = os.path.join(dirs['audio_dir'],"audio_content.raw")
    with BarSocketStream(SAMPLE_RATE, CHUNK_SIZE, save_to_file=audio_file_name) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses,stream,ip,port,dirs['txt_dir'],voice_name=voice_name,personality_prompt=personality_prompt,notifier=notifier)


if __name__ == "__main__":
    main()
