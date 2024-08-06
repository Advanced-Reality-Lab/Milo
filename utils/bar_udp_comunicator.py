import socket
import threading

from time import sleep

from utils.pyrtp import DecodeRTPpacket

hit=0

barSockets = None
def run(soc,on_meg_recived):
    global should_run
    while should_run:
        try:
            data, addr = soc.recvfrom(4*1024)  # buffer size is 1024 bytes
            on_meg_recived(data,addr)
        except socket.timeout as to:
            pass


def get_bar_sockets(on_data_received, send_audio, data_received_UDP_PORT, send_audio_UDP_PORT,
                 data_received_UDP_IP, send_audio_UDP_IP):
    global barSockets
    if barSockets is None:
        barSockets = BarSockets(on_data_received, send_audio, data_received_UDP_PORT, send_audio_UDP_PORT,
                 data_received_UDP_IP, send_audio_UDP_IP)
    else:
        barSockets.register_callback(on_data_received)
    return barSockets


class BarSockets(object):
    # def __init__(self, on_record, on_record_stop, on_chat, on_close):
    def __init__(self, on_data_received, send_audio, data_received_UDP_PORT, send_audio_UDP_PORT,
                 data_received_UDP_IP, send_audio_UDP_IP):
        self.data_received_UDP_IP = data_received_UDP_IP
        self.data_received_UDP_PORT = data_received_UDP_PORT

        self.send_audio_UDP_IP = send_audio_UDP_IP
        self.send_audio_UDP_PORT = send_audio_UDP_PORT

        self.send_audio = send_audio
        self.on_data_received = on_data_received
        self.socs_initialized = False

    def register_callback(self, on_data_received):
        self.on_data_received = on_data_received

    def init_sockets_receivers(self):
        if not self.socs_initialized:
            self.socs_initialized = True
            self.data_received_sock = socket.socket(socket.AF_INET,  # Internet
                                             socket.SOCK_DGRAM)  # UDP
            self.data_received_sock.bind((self.data_received_UDP_IP, self.data_received_UDP_PORT))

            self.send_audio_sock = socket.socket(socket.AF_INET,  # Internet
                                                  socket.SOCK_DGRAM)  # UDP
            self.send_audio_sock.bind((self.send_audio_UDP_IP, self.send_audio_UDP_PORT))

    def close_recv_sock(self):
        pass

    def init_run(self):
        global should_run
        global hit
        hit+=1
        self.init_sockets_receivers()
        self.init_threads()
        should_run = True
        self.run_data_received.start()

    def send_msg(self, message, UDP_IP, UDP_PORT):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print(f"sending stop signal to {UDP_IP}:{UDP_PORT}")
        sock.sendto(message, (UDP_IP, UDP_PORT))
        print("stop signal sent")
        sock.close()

    def send_tcp_msg(self,message,TCP_IP,TCP_PORT):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"send_tcp_msg - {TCP_IP}:{TCP_PORT}, message: {message}")
        s.connect((TCP_IP,TCP_PORT))
        s.send(message)
        s.close()

    def init_threads(self):
        self.run_data_received = threading.Thread(target=run, args=[self.data_received_sock,self.on_data_received])

    def close(self):
        global should_run
        should_run = False
        self.run_data_received.join(timeout=1)

        if self.run_data_received.isAlive():
            pass



def t_Bar():
    pass
    soc = BarSockets(on_data_received=lambda x, y:print(DecodeRTPpacket(x.hex())),
                     send_audio=lambda x,y: print(x," ",y),
                     send_audio_UDP_IP='', data_received_UDP_IP='0.0.0.0',
                     send_audio_UDP_PORT=3030, data_received_UDP_PORT=7456)
    soc.init_run()
    sleep(5)
    soc.close()

if __name__ == '__main__':
    t_Bar()
