## ///////////////////
## This is the main file for the assist mode
## This includes a GUI for the operator to use in assist mode
## without automatic LLM response generation
## ///////////////////

import os
import time
import pathlib
import shutil
from pydub import AudioSegment
from playsound import playsound
from utils import udp_comunicator, recorder
from utils.files_handler import FilesHandler
from utils.speech import STTConVRSelf_gcloud as STTConVRSelf
import logging
import sys

from tkinter import *

from utils.speech.stt_stream import StreamAsyncSender
from utils.UI.GUI_noGPT import No_GPT_screen, get_green_signal
from utils.config_helpers import read_config_file,load_model

new_file_name = None
start_spliting_file = None
end_spliting_f0ile = None
start_record_time = None
side = None
UPLOAD_FOLDER = None
audio_dir = None
txt_dir = None
model = None
tokenizer = None
audio_name = None
audio_name = ''


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler(sys.stdout)
f_handler = logging.FileHandler('files/file.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

logger.info('completes initializing global variables')


stt = STTConVRSelf.STTConVRSelf()




# Set the download folder
UPLOAD_FOLDER = str(pathlib.Path().absolute())

# Set the allowd formats
ALLOWED_EXTENSIONS = {'opus', 'wav', 'txt'}

audiofile = 1


# chaeck if the input file in the acceptable format

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def record(data, addr):
    logger.info('Started detecting new file')
    global fh
    global double_recording_checker
    global start_record_time
    global side
    global threading_counter
    global new_file_name
    global start_spliting_file
    global recording

    logger.debug(addr)
    str_data = data.decode("utf-8")

    # getting the next available name file
    side, start_spliting_file = str_data.split('$')
    recording.should_send_audio_to_stt = True
    stt_stream.start(recording.generator())
    if start_spliting_file == '':
        start_spliting_file = str(time.time())

    start_spliting_file = float(start_spliting_file)

    #fh is getting the name of the new file
    new_file_name = fh.next_available_file_name(audio_dir, side)

    logger.info(f'completed recording func, start time of the session was set to {start_record_time} and the side is {side}')
    return 'Completed recording func'


def stop_record(data, addr):
    logger.info('stop record - creating a file started')
    try:
        global end_time
        global start_time
        global start_spliting_file
        global end_spliting_file
        global start_record_time
        global sentence
        global recording

        str_data = data.decode("utf-8")
        side, end_spliting_file = str_data.split('$')

        if end_spliting_file == '':
            end_spliting_file = str(time.time())

        end_spliting_file = float(end_spliting_file)

        recording.should_send_audio_to_stt = False
        stt_stream.stop()
        sentence = stt_stream.get_transcription()
        stt_stream.save_to_file_and_clear_transcription(os.path.join(session_dir,f"{new_file_name[:-4]}.txt"))
        starting_recording_point_ms = (start_spliting_file - start_record_time) * 1000 #pydub works in millisec
        end_recording_point_ms = (end_spliting_file - start_record_time) * 1000


        #duplicating the file that we are contantly record to, in order to easy work and cut him.
        shutil.copy(os.path.join(session_dir,'record.wav'), os.path.join(session_dir,new_file_name))

        #initiating AudioSegment Object
        audio = AudioSegment.from_wav(os.path.join(session_dir,new_file_name))

        logger.info(f'split at [{starting_recording_point_ms}:{end_recording_point_ms}] ms')

        newAudio = audio[starting_recording_point_ms:end_recording_point_ms]
        newAudio.export(os.path.join(session_dir,new_file_name), format="wav")  # Exports to a wav file in the current

        logger.debug('Exports to a wav file in the current')

        audio_chunk=audio[starting_recording_point_ms:end_recording_point_ms]
        audio_chunk.export(os.path.join(session_dir,new_file_name), format="wav")

        logger.info(f'the sentence detected from stt is {sentence}')

        shutil.move(os.path.join(session_dir,f"{new_file_name[:-4]}.txt"),
                    os.path.join(txt_dir, f"{new_file_name[:-4]}.txt"))
        shutil.move(os.path.join(session_dir,new_file_name), os.path.join(audio_dir , new_file_name))

        logger.info('completed stop record')
        return 'finish Stopped recording'
    except Exception as e:
        return "error in stop_recording"


def close(data, addr):
    soc.close()
    recording.stoprecord()
    logger.info('closed socket, good to go')


def chat(data, addr):
    global gpt_dir
    logger.info('started GPT response func')

    green_signal = get_green_signal()
    green_signal.configure(bg='green')


def init(config):
    global gpt
    global side
    global audio_dir
    global txt_dir
    global session_dir
    global gpt_dir
    global fh
    global stt_stream

    stt_stream = StreamAsyncSender()

    # Init_model_and_tokenizer
    logger.info('starts initializing GPT Dialog')
    chat_model = config['CHAT_MODEL_NAME']
    gpt = load_model(chat_model)

    logger.info('completed initializing GPT Dialog, can start and use the record')

    logger.info('initializing communications')
    udp_comunicator.set_ip_and_ports(config['IN_UDP_IP'],**config['IN_UDP_PORTs'])

    # initializing variables that will use as global
    logger.info('initializing new directories')
    fh = FilesHandler(label_txt,path_rel=config['saving_path'])
    audio_dir, txt_dir, gpt_dir, session_dir = fh.get_dirs()

    audio_name = session_dir + '/record.wav'

    logger.info(f'directory names are {audio_dir} for audio, \n{txt_dir} for the text')

    side = '0'  # By default we will use the first side


    return audio_name


def id_func(event=None):
    global label_txt
    global audio_name
    label_txt = str(e1.get())
    root.destroy()






def initialize_session_id():
    global e1
    global root
    root = Tk(className='Milo')
    # set window size
    root.geometry("400x200")

    # set window color
    label_exp = Label(root, text="\nPlease enter ID and submit to continue\n\n")
    label = Label(root, text="ID:\n ")

    e1 = Entry(root)

    set_id = Button(root, text="Submit", command=id_func)
    root.bind('<Return>',id_func) # for convinance (enable <enter> key)
    label_exp.pack()
    label.pack()
    e1.pack()
    set_id.pack()

    root.mainloop()



if __name__ == '__main__':
    global to_init
    global root
    global soc
    logger.info(f'starting gui aplication')
    initialize_session_id()
    print(os.getcwd())
    config = read_config_file()

    logger.info(f'completed main functions')
    audio_name = init(config)

    start_record_time = time.time()
    recording = recorder.Recorder(audio_name)
    recording.start()
    logger.info('starts recording constantly')

    soc = udp_comunicator.SocratesSockets(record, stop_record, chat, close)
    soc.init_run()
    No_GPT_screen()  # blocking
    logger.info('closing utils')
    soc.close()
    logger.info('closed socket')
    recording.stoprecord()
    recording.join()
    logger.info('closed recording')
    logger.info('good to go')
