import threading
import tkinter
from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
from tkinter import scrolledtext
from tkinter.scrolledtext import ScrolledText


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
                details = msg[12:]
                save_as, file_type2, file_size = details.split('#')
                print("namefile: ", save_as)

                file_type = file_type2[:-1]
                print(type(save_as), ":type")

                t3 = threading.Thread(target=downloadf(save_as, file_type, file_size))
                t3.start()
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


def on_closing(event=None):
    """ This function is to be called when the window is closed. """
    my_msg.set("#quit")
    send()


def get_users_button(event=None):
    my_msg.set("#getusers")
    send()


def downloadf(save_as, file_type, file_size):
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    udp_socket.bind(('127.0.0.1', 55003))
    name = str((save_as + '.' + file_type))
    file = open(name, 'wb')
    rec = 0
    while True:
        bytes_read = udp_socket.recv(2048)

        file.write(bytes_read)
        rec = rec + len(bytes_read)
        print(f'rec: {rec} / {int(file_size)} bytes')

        if not bytes_read:
            break


    file.close()
    udp_socket.close()

    return


# def smiley_button_tieup(event=None):
#     """ Function for smiley button action """
#     my_msg.set(":)")    # A common smiley character
#     send()


# def sad_button_tieup(event=None):
#     """ Function for smiley button action """
#     my_msg.set(":(")    # A common smiley character
#     send()


top = tkinter.Tk()
top.title("Simple Chat Client v1.0")
messages_frame = tkinter.Frame(top)

my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=70, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
# st = scrolledtext.ScrolledText(top)

messages_frame.pack()

button_label = tkinter.Label(top, text="Enter Message:")
button_label.pack()
entry_field = tkinter.Entry(top, textvariable=my_msg, foreground="Red")
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()
users_button = tkinter.Button(top, text="online users", command=get_users_button)
users_button.pack()
request_button = tkinter.Button(top, text="request", command=request)
request_button.pack()
# smiley_button = tkinter.Button(top, text=":)", command=smiley_button_tieup)
# smiley_button.pack()
# sad_button = tkinter.Button(top, text=":(", command=sad_button_tieup)
# sad_button.pack()

quit_button = tkinter.Button(top, text="Quit", command=on_closing)
quit_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.
