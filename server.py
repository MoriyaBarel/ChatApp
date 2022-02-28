import os
import time
from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
from threading import Thread

clients = {}
addresses = {}
files = ["Holla", "aaa", "dog"]

HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(ADDR)
udp_socket = socket(AF_INET, SOCK_DGRAM)


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SOCK.accept()
        print("%s:%s has connected." % client_address)
        client.send("Greetings from the ChatRoom! ".encode("utf8"))
        client.send("Now type your name and press enter!".encode("utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(conn, addr):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = conn.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type #quit to exit.' % name
    conn.send(bytes(welcome, "utf8"))
    msg = "%s from [%s] has joined the chat!" % (name, "{}:{}".format(addr[0], addr[1]))
    broadcast(bytes(msg, "utf8"))
    clients[conn] = name
    while True:
        msg = conn.recv(BUFSIZ)
        if msg == bytes("!request", "utf8"):
            Thread(target=request_file(conn, msg))
        elif msg.startswith("##".encode()):
            Thread(target=send_file(conn, msg))
        elif msg == bytes("#getusers", "utf8"):
            get_users(conn, msg, "connected users: ")
        elif msg != bytes("#quit", "utf8"):
            broadcast(msg, name + ": ")
        else:
            del clients[conn]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            conn.close()
            break


def send_file(conn, msg):
    file_name_and_type, file_name, file_type, save_as = get_filename_and_filetype(msg)
    if not files.__contains__(file_name):
        conn.send('error: no file was requested'.encode())
    else:
        path = os.path.abspath(file_name_and_type)
        file_size = os.path.getsize(file_name_and_type)
        conn.send(f'##download{"#"}{save_as}{"#"}{file_type}{"#"}{file_size}'.encode())
        sent = 0
        file = open(path, 'rb')
        while True:
            bytes_read = file.read(2048)
            udp_socket.sendto(bytes_read, ('127.0.0.1', 55003))
            time.sleep(1)
            sent = sent + len(bytes_read)
            conn.send(f'sent: {sent} / {file_size}'.encode())
            print(f'sent: {sent} / {file_size} bytes to {conn}')
            if not bytes_read:
                break
        file.close()


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
    if msg == '!request'.encode():
        message = "To continue the download, enter the file name with # , eg #dog"
        conn.send(message.encode())
        time.sleep(1)


def get_users(conn, msg, prefix=""):
    if msg == '#getusers'.encode():
        # for name in clients.values():
        #     sock = get_key(name)
        connected = str(clients.values())
        connected_users = connected[11:]
        conn.send(bytes(prefix, "utf8") + connected_users.encode())
        # for activity in clients.values():
        #     if activity != name:
        #         print("type activity is : ")
        #         sock.send(bytes(prefix, "utf8") + activity.encode())


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    if msg.startswith('@'.encode()):
        for name in clients.values():
            sock = get_key(name)
            name_len = len(name)
            if msg[1:name_len+1].decode() == name:
                actual_message = msg[name_len+1:]
                sock.send(bytes(prefix, "utf8") + actual_message)
    else:
        for sock in clients:
            sock.send(bytes(prefix, "utf8") + msg)


def get_key(val):
    for key, value in clients.items():
        if val == value:
            return key


if __name__ == "__main__":
    SOCK.listen(5)  # Listens for 5 connections at max.
    print("Chat Server has Started !!")
    print("Waiting for connections...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SOCK.close()
