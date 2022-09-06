import sys
import threading
import tkinter
import tkinter.messagebox
from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
from tkinter import scrolledtext


def receive():
    """ Handles receiving of messages. """
    while True:
        try:
            msg = sock.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
            if msg == "quit":
                sock.close()
                top.quit()
            elif msg.startswith('##download'):
                details = msg[11:]
                save_as, file_type, file_size, port = details.split('#')
                download_thread = threading.Thread(target=download_file(save_as, file_type, file_size, port))
                download_thread.start()
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):
    """ Handles sending of messages. """
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    sock.send(bytes(msg, "utf8"))
    if msg == "#quit":
        sock.close()
        top.quit()


def request(event=None):
    my_msg.set("!request")
    send()


def closing(event=None):
    """ This function is to be called when the window is closed. """
    my_msg.set("#quit")
    send()


def get_users_button(event=None):
    my_msg.set("#getusers")
    send()


def get_file_list(event=None):
    my_msg.set("#getfilelist")
    send()


def download_file(save_as, file_type, file_size, port):
    udp_socket_receive = socket(AF_INET, SOCK_DGRAM)
    address = sock.getsockname()[0]
    udp_socket_receive.bind((address, int(port)))
    all_data = {}
    packets_num = int(int(file_size)/(BUFSIZ*2))+1
    while True:
        packet_counter = len(all_data)
        if packet_counter == packets_num:
            sock.send('done'.encode())
            print('download finished')
            break
        else:
            handle_missing_packets(all_data, packets_num)
            bytes_read = udp_socket_receive.recv(2050)
            if not bytes_read:
                continue
            bytes_to_write = bytes_read[:len(bytes_read)-2]
            seq = bytes_read[len(bytes_read)-2:]
            all_data[seq] = bytes_to_write
    write_to_file(all_data, save_as, file_type)
    udp_socket_receive.close()
    return


def handle_missing_packets(all_data, packets_num):
    missing_packets = ''
    for i in range(0, packets_num):
        if not all_data.keys().__contains__(i):
            if i <= 9:
                packet_num = '0' + str(i)
            else:
                packet_num = str(i)
            missing_packets = missing_packets + packet_num + ','
    sock.send(missing_packets.encode())


def write_to_file(all_data, save_as, file_type):
    name = save_as + '.' + file_type
    file = open(name, 'wb')
    for index in sorted(all_data.keys()):
        file.write(all_data[index])
    file.close()


# ------------------------------Gui----------------------------------
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

# -------------------------------------------------------------------

if __name__ == '__main__':
    HOST = sys.argv[1]
    PORT = 55000
    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(ADDR)

    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()  # GUI Starts
