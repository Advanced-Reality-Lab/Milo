# main with notifier that can register to sentence completions

from utils.edit_bar_service1 import main, set_stop

import os

from flask import Flask, request, abort, jsonify, send_from_directory
from threading import Thread
from utils import files_handler
from utils.config_helpers import read_config_file
from utils.files_handler import directory_creation
import argparse

UPLOAD_DIRECTORY = "WorkingDir"
root_dir = os.getcwd()
full_dir = os.path.join(root_dir,UPLOAD_DIRECTORY)

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

if __name__ == '__main__':
    global participant_id
    participant_id = input("please enter the participants id:")


api = Flask(__name__)
started = False

@api.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(full_dir):
        path = os.path.join(full_dir, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route("/files/<path:path>")
def get_file(path):
    """Download a file."""
    print(f"sending file {full_dir}\\{path}")
    return send_from_directory(full_dir, path, as_attachment=True)


@api.route("/files/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a file."""

    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories allowed")

    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)

    # Return 201 CREATED
    return "", 201



@api.route("/start_speak")
def start_speak():
    global config
    audio_dir, txt_dir, gpt_dir, session_dir = directory_creation(config.run_name,path_rel="data",exist_ok=True)
    print(audio_dir, txt_dir, gpt_dir, session_dir)
    params = {
        "headset_ip":request.remote_addr,
        "port":config.return_port,
        "intro_length":config.intro_length,
        #"WorkingDir": UPLOAD_DIRECTORY,
        "participant_id":config.run_name,
        "dirs":{"audio_dir":audio_dir,"txt_dir":txt_dir},
        "voice_name": config.voice_name,
        "personality_prompt": open(config.personality_prompt).read(),
        "notifier": notifier,
    }
    print(params)
    start_new_conv(params)
    return "", 200

def start_new_conv(params):
    global t
    global started
    if not started:
        started=True
        t = Thread(target=main,kwargs=params)
        t.start()

@api.route("/stop_speak")
def stop_speak():
    global t
    global started
    set_stop()
    started = False
    t.join()

    return "", 200



if __name__ == "__main__":
    global config
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_name", help="the name of the run")
    parser.add_argument("--intro_length", help="the length of the intro")
    parser.add_argument("--return_port",type=int ,help="the port to return the data")
    parser.add_argument("--host_url", help="the host url")
    parser.add_argument("--host_port", help="the host port")
    parser.add_argument("--voice_name", help="the voice name")
    parser.add_argument("--personality_prompt", help="the personality prompt")
    args = parser.parse_args()
    print(args)
    config = read_config_file("conf.json")
    if args.run_name:
        config.run_name = args.run_name
    if args.intro_length:
        config.intro_length = args.intro_length
    if args.return_port:
        config.return_port = args.return_port
    if args.host_url:
        config.host_url = args.host_url
    if args.host_port:
        config.host_port = args.host_port
    if args.voice_name:
        config.voice_name = args.voice_name
    if args.personality_prompt:
        config.personality_prompt = args.personality_prompt
    if not os.path.exists(config.personality_prompt):
        raise Exception(f"the personality prompt file {config.personality_prompt} does not exist")
    # t.start()
    # files_handler.directory_creation(participant_id,'BAR_EXP_DATA',exist_ok=True)
    api.run(debug=True, host=config.host_url, port=config.host_port)
    # main()


def set_notifier(_notifier):
    global notifier
    notifier = _notifier

