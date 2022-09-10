import math
import os
import sys
import threading
import time
import tkinter
import tkinter.messagebox
from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
from tkinter import scrolledtext


def receive():
    """ Handles receiving of messages. """
    while True:
        try:
            msg = tcp_sock.recv(BUF_SIZE).decode("utf8")
            MSG_LIST.insert(tkinter.END, msg)
            if msg == "quit":
                tcp_sock.close()
                TOP.quit()
            elif msg.startswith('##download'):
                details = msg[DOWNLOAD_PREFIX:]
                save_as, file_type, file_size, recv_port, mgmt_port = details.split('#')
                all_data = {}
                download_thread = threading.Thread(target=download_file(all_data, save_as, file_type, file_size, recv_port, mgmt_port))
                download_thread.start()
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):
    """ Handles sending of messages. """
    msg = MY_MSG.get()
    MY_MSG.set("")  # Clears input field.
    tcp_sock.send(bytes(msg, "utf8"))
    if msg == "#quit":
        tcp_sock.close()
        TOP.quit()


def request(event=None):
    MY_MSG.set("!request")
    send()


def closing(event=None):
    """ This function is to be called when the window is closed. """
    MY_MSG.set("#quit")
    send()


def get_users_button(event=None):
    MY_MSG.set("#getusers")
    send()


def get_file_list(event=None):
    MY_MSG.set("#getfilelist")
    send()


def download_file(all_data, save_as, file_type, file_size, recv_port, mgmt_port):
    udp_sock_mgmt = socket(AF_INET, SOCK_DGRAM)
    udp_sock_receive = socket(AF_INET, SOCK_DGRAM)
    address = tcp_sock.getsockname()[0]
    udp_sock_receive.bind((address, int(recv_port)))
    packets_num = math.ceil(float(file_size)/CHUNK_SIZE)
    mgmt_thread = threading.Thread(target=mgmt_loop, args=(all_data, packets_num, udp_sock_mgmt, mgmt_port))
    mgmt_thread.start()
    while True:
        packet_counter = len(all_data)
        if packet_counter == packets_num:
            break
        else:
            bytes_read = udp_sock_receive.recv(BUF_SIZE)
            if not bytes_read:
                continue
            bytes_to_write, seq = bytes_read.split('seq:'.encode())
            all_data[int(seq.decode("utf8"))] = bytes_to_write
    write_to_file(all_data, save_as, file_type)
    mgmt_thread.join()
    udp_sock_mgmt.close()
    udp_sock_receive.close()
    MSG_LIST.insert(tkinter.END, "File download completed successfully")


def mgmt_loop(all_data, packets_num, udp_sock_mgmt, mgmt_port):
    while True:
        packet_counter = len(all_data)
        if packet_counter == packets_num:
            udp_sock_mgmt.sendto('done'.encode(), (HOST, int(mgmt_port)))
            print('download finished')
            break
        handle_missing_packets(all_data, packets_num, udp_sock_mgmt, mgmt_port)
        time.sleep(0.2)


def handle_missing_packets(all_data, packets_num, udp_sock_mgmt, mgmt_port):
    missing_packets = ''
    for i in range(0, packets_num):
        if i not in all_data.keys():
            packet_num = str(i)
            missing_packets = missing_packets + packet_num + ','
    missing_packets = missing_packets[:-1]
    udp_sock_mgmt.sendto(missing_packets.encode(), (HOST, int(mgmt_port)))


def write_to_file(all_data, save_as, file_type):
    name = save_as + '.' + file_type
    file_path = os.path.join('download', name)
    file = open(file_path, 'wb')
    for index in sorted(all_data.keys()):
        file.write(all_data[index])
    file.close()


# ------------------------------Gui----------------------------------
def init_gui():
    top = tkinter.Tk()
    top.title("ChatApp")
    messages_frame = tkinter.Frame(top)

    my_msg = tkinter.StringVar()  # For the messages to be sent.
    my_msg.set("")
    scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
    msg_list = tkinter.Listbox(messages_frame, height=15, width=75, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msg_list.pack()
    st = scrolledtext.ScrolledText(top)

    messages_frame.pack()

    lines = ["• To send a private message type @user_name and the message contents.",
             "• To broadcast to everyone, just type the message.",
             "• The download process begins with requesting permission",
             "   by pressing the request button, than follow the instructions."]
    msg_list.insert(tkinter.END, 'User guide:')
    msg_list.insert(tkinter.END, lines[0])
    msg_list.insert(tkinter.END, lines[1])
    msg_list.insert(tkinter.END, lines[2])
    msg_list.insert(tkinter.END, lines[3])

    button_label = tkinter.Label(top, text="Enter Message:")
    button_label.pack()
    entry_field = tkinter.Entry(top, textvariable=my_msg, foreground="Red")
    entry_field.bind("<Return>", send)
    entry_field.pack()
    send_button = tkinter.Button(top, text="Send", command=send)
    send_button.pack()
    users_button = tkinter.Button(top, text="Online users", command=get_users_button)
    users_button.pack()
    request_button = tkinter.Button(top, text="Request download", command=request)
    request_button.pack()
    file_list_button = tkinter.Button(top, text="File list", command=get_file_list)
    file_list_button.pack()

    quit_button = tkinter.Button(top, text="Quit", command=closing)
    quit_button.pack()

    top.protocol("WM_DELETE_WINDOW", closing)

    return my_msg, msg_list, top

# -------------------------------------------------------------------


if __name__ == '__main__':
    MY_MSG, MSG_LIST, TOP = init_gui()
    HOST = sys.argv[1]
    PORT = 55000
    # BUF_SIZE is the total size of the packet
    BUF_SIZE = 2048
    # CHUNK SIZE is the data size, must be smaller than BUF_SIZE
    CHUNK_SIZE = 2000
    DOWNLOAD_PREFIX = 11
    ADDR = (HOST, PORT)

    tcp_sock = socket(AF_INET, SOCK_STREAM)
    tcp_sock.connect(ADDR)

    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()  # GUI Starts
