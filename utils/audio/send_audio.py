import os
import socket
import asyncio
import soundfile as sf


async def send_audio_stream(audio_stream,return_addr,return_port):
    # create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to the server
    await s.connect((return_addr,return_port))
    # send the audio stream
    await s.send(audio_stream)
    # close the socket
    await s.close()

async def read_and_send_audio_file(file_path,return_addr,return_port):
    # read the audio file
    audio_stream, sample_rate = sf.read(file_path)
    # send the audio stream
    await send_audio_stream(audio_stream,return_addr,return_port)


def send_audio(param, soc, ip, port):
    pass