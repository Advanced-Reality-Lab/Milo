import queue
import threading
import pyaudio
import wave




class Recorder(threading.Thread):
    def __init__(self, audiofile = 'record.wav',should_send_audio_to_stt=False):

        threading.Thread.__init__(self)
        self._should_send_audio_to_stt = should_send_audio_to_stt
        self.bRecord = True
        self.audiofile = audiofile
        self.chunk = 160 #100 ms
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.stream = None
        self._buff = queue.Queue()


    @property
    def should_send_audio_to_stt(self):
        # print("Getting value...")
        return self._should_send_audio_to_stt

    @should_send_audio_to_stt.setter
    def should_send_audio_to_stt(self, value):
        print(f"Setting value...,{value}")
        # self._buff.open()
        if not value:
            self._buff.put(None)
            self._buff.task_done()
            # raise ValueError("Temperature below -273 is not possible")
        # else:
        self._should_send_audio_to_stt = value


    def run(self):
        audio = pyaudio.PyAudio()
        wavfile = wave.open(self.audiofile, 'wb')
        wavfile.setnchannels(self.channels)
        wavfile.setsampwidth(audio.get_sample_size(self.format))
        wavfile.setframerate(self.rate)
        wavstream = audio.open(format=self.format,
                               channels=self.channels,
                               rate=self.rate,
                               input=True,
                               frames_per_buffer=self.chunk)
        c=0
        while self.bRecord:
            wavstream_read = wavstream.read(self.chunk,exception_on_overflow=False)
            wavfile.writeframes(wavstream_read)
            if self.should_send_audio_to_stt: #and callable(self.stt_callback):
                self._buff.put(wavstream_read)
                # print("in self.should_send_audio_to_stt")

                # c+=1

        wavstream.stop_stream()
        wavstream.close()
        self._buff.put(None)
        audio.terminate()

    def stoprecord(self):
        self.bRecord = False

    def startrecord(self):
        self.bRecord = True

# this is a generator that holds some of the data for sending to stt
    def generator(self):
        while self.should_send_audio_to_stt:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                continue
            data = [chunk]

            # Now consume whatever other data's still buffered.
            # c = 0
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)
        # raise StopIteration