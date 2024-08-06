import socket
import threading
import time
import logging

from utils.bar_udp_comunicator import BarSockets

should_run = True
initialized=False
socket.setdefaulttimeout(10.)
logger = logging.getLogger(__name__)

def set_ip_and_ports(ip,start_record_port,stop_record_port,chat_port,close_port):
    global initialized
    global UDP_IP
    global record_UDP_PORT
    global stop_record_UDP_PORT
    global chat_UDP_PORT
    global close_UDP_PORT
    logger.info(f"initializing ports with {ip},{start_record_port},{stop_record_port},{chat_port},{close_port}")
    UDP_IP = ip
    record_UDP_PORT = start_record_port
    stop_record_UDP_PORT= stop_record_port
    chat_UDP_PORT = chat_port
    close_UDP_PORT = close_port
    initialized = True

def run(soc,on_meg_recived):
    global should_run
    while should_run:
        try:
            data, addr = soc.recvfrom(1024)  # buffer size is 1024 bytes

            on_meg_recived(data,addr)
        except socket.timeout as to:
            pass

class SocratesSockets(object):
    def __init__(self,on_record,on_record_stop,on_chat, on_close):
        self.on_chat = on_chat
        self.on_record_stop = on_record_stop
        self.on_record = on_record
        self.on_close = on_close
        


    def init_sockets_receivers(self):

        self.record_sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        self.record_sock.bind((UDP_IP, record_UDP_PORT))

        self.stop_record_sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        self.stop_record_sock.bind((UDP_IP, stop_record_UDP_PORT))

        self.chat_sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        self.chat_sock.bind((UDP_IP, chat_UDP_PORT))

        self.close_sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        self.close_sock.bind((UDP_IP, close_UDP_PORT))


    def init_run(self):
        self.init_sockets_receivers()
        self.init_threads()

        self.run_record.start()
        self.run_stop_record.start()
        self.run_chat.start()
        self.run_close.start()

    def send_msg(self,message,UDP_IP,UDP_PORT):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        print(f"sending stop signal to {UDP_IP}:{UDP_PORT}")
        sock.sendto(message, (UDP_IP, UDP_PORT))
        print("stop signal sent")
        sock.close()


    def init_threads(self):
        self.run_record = threading.Thread(target=run, args=[self.record_sock, self.on_record])
        self.run_stop_record = threading.Thread(target=run, args=[self.stop_record_sock, self.on_record_stop])
        self.run_chat = threading.Thread(target=run, args=[self.chat_sock, self.on_chat])
        self.run_close = threading.Thread(target=run, args=[self.chat_sock, self.on_chat])

    def close(self):
        global should_run
        should_run = False
        self.run_record.join()
        self.run_chat.join()
        self.run_stop_record.join()
        self.run_close.join()


def t_Socrates():
    set_ip_and_ports('', 5005, 5007, 5009, 5011)
    soc = SocratesSockets(lambda x, y: print(x, y), lambda x, y: print(x, y), lambda x, y: print(x, y),
                          lambda x, y: print(x, y))
    soc.init_run()
    time.sleep(5)  # send
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 2)
    print("sending")
    soc.send_msg(b"robot", '255.255.255.255', 5005)
    soc.send_msg(b"robot123", '255.255.255.255', 5007)
    soc.send_msg(b"robot", '255.255.255.255', 5009)
    # sock.sendto(b"robot", (UDP_IP, record_UDP_PORT))
    # sock.sendto(b"robot123", (UDP_IP, stop_record_UDP_PORT))
    # sock.sendto(b"robot321", (UDP_IP, chat_UDP_PORT))
    # sock.close()
    print("sent")
    time.sleep(5)  # send
    soc.close()


def t_Bar():
    pass
    soc = BarSockets(on_data_received=lambda x, y:print(x, " ", y),
                     send_audio=lambda x,y: print(x," ",y),
                     send_audio_UDP_IP='', data_received_UDP_IP='',
                     send_audio_UDP_PORT=3030, data_received_UDP_PORT=3032)
    soc.init_run()


if __name__ == '__main__':
    # t_Socrates()
    t_Bar()

