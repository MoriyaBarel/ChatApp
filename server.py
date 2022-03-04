import os
import time
from _socket import *
from socket import *
from threading import Thread


clients = {}
addresses = {}
global flag
flag = False
files = ["random", "dog", "text"]
HOST = "127.0.1.1"
PORT = 5001
BUFSIZ = 1024
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(('', PORT))
SOCK.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
udp_socket = socket(AF_INET, SOCK_DGRAM)


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SOCK.accept()
        print("%s:%s has connected." % client_address)
        client.send("Greetings from the ChatRoom!\nNow type your name and press enter !".encode("utf8"))

        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(conn, addr):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = conn.recv(BUFSIZ).decode("utf8")
    for nick in clients.values():
        if nick == name:
            name = name + str(1)
    welcome = 'Welcome %s! If you ever want to quit, type #quit to exit.' % name
    conn.send(bytes(welcome, "utf8"))
    msg = "%s from [%s] has joined the chat!" % (name, "{}:{}".format(addr[0], addr[1]))
    broadcast(bytes(msg, "utf8"))
    clients[conn] = name
    while True:
        msg = conn.recv(BUFSIZ)
        if msg == bytes("!request", "utf8"):
            request_file(conn, msg)
        elif msg.startswith("##".encode()):
            send_file(conn, msg)
        elif msg == bytes("#getusers", "utf8"):
            get_users(conn, msg, "connected users: ")
        elif msg == bytes("#getfilelist", "utf8"):
            get_file_list(conn, msg, " file list->")
        elif msg.startswith('@'.encode()):
            c2c(conn, msg, name + ":")
        elif msg != bytes("#quit", "utf8"):
            broadcast(msg, name + ":")
        else:
            del clients[conn]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            conn.close()
            break


def send_file(conn, msg):
    global flag
    if flag:
        file_name_and_type, file_name, file_type, save_as = get_filename_and_filetype(msg)
        if not files.__contains__(file_name):
            conn.send('error: no file was requested'.encode())
        else:
            path = os.path.abspath(file_name_and_type)
            file_size = os.path.getsize(file_name_and_type)
            conn.send(f'##download{"#"}{save_as}{"#"}{file_type}{"#"}{file_size}'.encode())
            file = open(path, 'rb')
            seq = 0
            all_data = {}
            addr = conn.getsockname()[0]
            while True:
                bytes_read = file.read(2 * BUFSIZ)
                if not bytes_read:
                    break
                if seq <= 9:
                    seq_num = ('0' + str(seq)).encode()
                else:
                    seq_num = str(seq).encode()
                bytes_to_send = bytes_read + seq_num
                all_data[seq] = bytes_to_send
                seq += 1
            print(seq)
            while True:
                acknowledge = conn.recv(BUFSIZ).decode("utf-8")
                if acknowledge.__contains__('done'):
                    print('done??')
                    udp_socket.close()
                    break
                else:
                    packets_to_send = acknowledge.split(',')
                    for packet_num in packets_to_send:
                        if packet_num != '':
                            udp_socket.sendto(all_data[int(packet_num)], (addr, 55003))
                            print('sent ', packet_num)
            file.close()
    else:
        conn.send(bytes("request before download", "utf8"))


def get_filename_and_filetype(msg: bytes):
    actual_msg = msg[2:]
    msg_str = actual_msg.decode("utf-8").split("#")
    file_name_and_type = msg_str[0]
    save_as = msg_str[1]
    file = file_name_and_type.split('.')
    filename = file[0]
    file_type = file[1]
    return file_name_and_type, filename, file_type, save_as


def request_file(conn, msg):
    global flag
    flag = True
    if msg == '!request'.encode():
        message = "To continue the download, enter the file name with # , eg ##dog.jpg#save_as"
        conn.send(message.encode())
        flag = True
        time.sleep(1)


def get_users(conn, msg, prefix=""):
    if msg == '#getusers'.encode():
        connected = str(clients.values())
        connected_users = connected[11:]
        conn.send(bytes(prefix, "utf8") + connected_users.encode())


def get_file_list(conn, msg, prefix=""):
    if msg == '#getfilelist'.encode():
        file_list_str = str(files)
        conn.send(bytes(prefix, "utf8") + file_list_str.encode())


def c2c(conn, msg, prefix=""):
    check = False
    for name in clients.values():
        sock = get_key(name)
        name_len = len(name)
        if msg[1:name_len + 1].decode() == name:
            check = True
            actual_message = msg[name_len + 1:]
            sock.send(bytes(prefix, "utf8") + actual_message)
            conn.send(bytes(prefix, "utf8") + actual_message)
            break
    if not check:
        conn.send(f"user not found".encode())


def broadcast(msg, prefix=""):
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


def get_key(val):
    for key, value in clients.items():
        if val == value:
            return key


if __name__ == "__main__":
    SOCK.listen(5)
    print("Chat Server has Started !!")
    print("Waiting for connections...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SOCK.close()
