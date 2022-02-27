""" Script for TCP chat server - relays messages to all clients """
import os
import threading
import time
from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
from threading import Thread

clients = {}
addresses = {}
files = ["holla", "aaa", "dog"]

HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(ADDR)
udp_socket = socket(AF_INET, SOCK_DGRAM)


# UDP_SOCK = socket(AF_INET, SOCK_DGRAM)


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
    print(clients)

    while True:
        msg = conn.recv(BUFSIZ)
        if msg == bytes("!request", "utf8"):
            Thread(target=requestfile(conn, msg))

        elif msg.startswith("##".encode()):
            Thread(target=sendf(conn, msg))


        elif msg == bytes("#getusers", "utf8"):
            getusers(conn, msg, "connected users: ")

        elif msg != bytes("#quit", "utf8"):
            broadcast(msg, name + ": ")
        # elif msg == bytes("#quit", "utf8"):
        #     quitchat(conn)
        #     break
        else:
            # conn.send(bytes("#quit", "utf8"))
            del clients[conn]
            broadcast2(bytes("%s has left the chat." % name, "utf8"))
            # for sock in clients:
            #     sock.send(bytes("%s has left the chat." % name, "utf8"))
            conn.close()
            break


def sendf(conn, msg):
    #msg_str = msg.decode()
    filenameandfiletypetemp, filenametemptemp, file_typetemp, savetemp = get_filename_and_filetype(msg)
    filename2=str(filenametemptemp)
    file_type=str(file_typetemp)
    final_save = str(savetemp)
    save=final_save[1:-1]
    print("save: ", save)
    print(type(save))
    filename = filename2[2:]
    filenameandfiletype = filenameandfiletypetemp[2:]



    # print("filename is :", filename)
    # print("the type is:", type(filename))
    if not files.__contains__(filename):
        conn.send('error: no file was requested'.encode())
    else:
        # print("what we need:",filenameandfiletype)
        path = os.path.abspath("dog.jpg")
        file_size = os.path.getsize("dog.jpg")
        conn.send(f'##download{"#"}{save}{"#"}{file_type}{"#"}{file_size}'.encode())
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


def get_filename_and_filetype(msg_str: str):
    actual_msg = msg_str[2:]
    mstr = actual_msg.split('#'.encode())
    filenameandfiletype = mstr[0]
    save = mstr[1]
    file = str(filenameandfiletype).split('.')
    filename = file[0]
    file_type = file[1]
    return filenameandfiletype, filename, file_type, save


# def quitchat(conn):
#     name = conn.recv(BUFSIZ).decode("utf8")
#     del clients[conn]
#     broadcast2(bytes("%s has left the chat." % name, "utf8"))
#     conn.close()


def requestfile(conn, msg):
    if msg == '!request'.encode():
        message = "To continue the download, enter the file name with # , eg #dog"
        conn.send(message.encode())
        time.sleep(1)


def broadcast2(msg, prefix=""):
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


def getusers(conn, msg, prefix=""):
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
            print(msg[1:5], name)
            if msg[1:len(name) + 1].decode() == name:
                actual_message = msg[len(name) + 1:]
                print("actual: ", actual_message)
                print("type actual message is :", type(actual_message))
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
