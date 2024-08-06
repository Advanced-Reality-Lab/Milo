import time
from tkinter import *
import threading
import socket
from tkinter import messagebox


should_run = True
UDP_IP = "127.0.0.1" # this should be read from config
record_UDP_PORT = 5005
stop_record_UDP_PORT = 5007
chat_UDP_PORT = 5009
close_UDP_PORT = 5011
socket.setdefaulttimeout(10.)
a = time.time()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)


def startzero():
    a = '0' + '$' + str(time.time())
    sock.sendto(a.encode(), (UDP_IP, record_UDP_PORT))

def stopzero():
    a = '0' + '$' + str(time.time())
    sock.sendto(a.encode(), (UDP_IP, stop_record_UDP_PORT))


def startone():
    a = '1' + '$' + str(time.time())
    sock.sendto(a.encode(), (UDP_IP, record_UDP_PORT))

def stopone():
    a = '1' + '$' + str(time.time())
    sock.sendto(a.encode(), (UDP_IP, stop_record_UDP_PORT))


def gpt():
    sock.sendto(b"$", (UDP_IP, chat_UDP_PORT))


def playMessage():
    sock.sendto(b"$initial message", (UDP_IP, chat_UDP_PORT))


def closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root2.destroy()





def GPT_screen():
    global root2
    global green_signal

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 2)

    root2 = Tk(className='MiloUI')
    root2.geometry("800x450")


    side0Start = Button(root2, text="side one start speak", command=startzero)
    side0Stop = Button(root2, text="side one stop speak",command=stopzero)

    side1Start = Button(root2, text="side two start speak", command=startone)
    side1Stop = Button(root2, text="side two stop speak",command=stopone)

    gpt1 = Button(root2, text="gpt",command=gpt)
    play_message = Button(root2, text="play message",command=playMessage)
    green_signal = Canvas(root2, bg="red", width=100, height=50)
    close = Button(root2, text="Close",command=closing)



    label = Label(root2,text='Welcom To Milo')

    label0 = Label(root2)
    label1 = Label(root2)
    label2 = Label(root2)
    label3 = Label(root2)
    label4 = Label(root2)
    label5 = Label(root2)
    label6 = Label(root2)




    label5.pack()
    label.pack()
    label6.pack()

    side0Start.pack()
    label0.pack()

    side0Stop.pack()
    label1.pack()

    side1Start.pack()
    label2.pack()
    side1Stop.pack()
    label3.pack()

    gpt1.pack()
    label4.pack()
    play_message.pack()
    green_signal.pack()
    close.pack()

    root2.mainloop()

def get_green_signal():
    global green_signal
    return green_signal

# used for testing purposes.
if __name__ == '__main__':
    pass
    GPT_screen()
