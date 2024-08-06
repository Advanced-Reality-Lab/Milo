import json
import os
import signal
from asyncio import sleep

from utils.bar_udp_comunicator import BarSockets
from utils.pyrtp import DecodeRTPpacket


def receive_audio_test():
    soc = BarSockets(on_data_received=lambda x, y:print(x.hex()),
                     send_audio=lambda x,y: print(x," ",y),
                     send_audio_UDP_IP='', data_received_UDP_IP='0.0.0.0',
                     send_audio_UDP_PORT=3030, data_received_UDP_PORT=7654)
    soc.init_run()
    os.system('pause')
    soc.close()

if __name__ == '__main__':
    receive_audio_test()