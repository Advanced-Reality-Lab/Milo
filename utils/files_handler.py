### this python file was made in order to help create the session folder and to manipulate the audio name files

import os, datetime
import logging
import sys
logger = logging.getLogger(__name__)


# directoryCreation creates a directory with the current folder name to store the wav files in.
def directory_creation(id='',path_rel='Data',exist_ok=False):
    path = os.getcwd()
    try:
        path = os.path.join(path, path_rel)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=exist_ok)

        my_data_dir = os.path.join(
            path, 'Session_Files_' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M'))

        if id != '':
            my_data_dir = os.path.join(
                path, f"ID_{id}_Session_Files_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M')}")

        # Setting the name of the new directory
        my_audio_dir = os.path.join(
            path,
            my_data_dir+'/Audio_Data')

        my_text_dir = os.path.join(
            path,
            my_data_dir+'/Text_Data')

        my_gpt_data = os.path.join(
            path,
            my_data_dir+'/GPT_DATA')

        os.makedirs(my_audio_dir,exist_ok=exist_ok)
        os.makedirs(my_text_dir,exist_ok=exist_ok)
        os.makedirs(my_gpt_data,exist_ok=exist_ok)

        return my_audio_dir, my_text_dir, my_gpt_data, my_data_dir

    except OSError as e:
        logger.error('unable to create the repository',e)
        raise e
        # return 'unable to create the repository',

def create_dir_for_bar(participant_id,data_folder):
    # create audio
    path = os.getcwd()
    try:
        path = os.path.join(path, data_folder)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

        my_data_dir = os.path.join(
            path, 'Session_Files_' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M'))

        if id != '':
            my_data_dir = os.path.join(
                path, f"ID_{id}_Session_Files_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M')}")

        # Setting the name of the new directory
        my_audio_dir = os.path.join(
            path,
            my_data_dir+'/Audio_Data')

        my_text_dir = os.path.join(
            path,
            my_data_dir+'/Text_Data')

        my_gpt_data = os.path.join(
            path,
            my_data_dir+'/GPT_DATA')

        os.makedirs(my_audio_dir)
        os.makedirs(my_text_dir)
        os.mkdir(my_gpt_data)

        return my_audio_dir, my_text_dir, my_gpt_data, my_data_dir

    except OSError as e:
        logger.error('unable to create the repository',e)
        raise e


    #create text

class FilesHandler:
    def __init__(self,id,path_rel='Data'):
        self.path_rel = path_rel
        self.id = id
        self.current_index = 0
        self.audio_dir, self.txt_dir, self.gpt_dir, self.session_dir = directory_creation(id,path_rel)

    def get_dirs(self):
        return self.audio_dir, self.txt_dir, self.gpt_dir, self.session_dir

    def next_available_file_name(self,dirname, side):
        i = self.current_index = self.current_index +1
        if side == '0':
            return 'ConvrSelf_Side_0_Record_%s.wav' % i
        return 'ConvrSelf_Side_1_Record_%s.wav' % i

    def save_audio(self,audio,file_name):
        pass



