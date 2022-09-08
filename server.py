import os
import time
from socket import *
from threading import Thread

all_ports = {55001: True, 55002: True, 55003: True, 55004: True, 55005: True, 55006: True, 55007: True, 55008: True,
             55009: True, 55010: True, 55011: True, 55012: True, 55013: True, 55014: True, 55015: True}
clients = {}
addresses = {}
files = ["random", "messi", "text"]
PORT = 55000
BUF_SIZE = 2048
CHUNK_SIZE = 2000
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(('', PORT))
SOCK.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# Check if a request has been sent
check = {}
for i in range(len(clients.values())):
    check[i] = False


def accept_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SOCK.accept()
        print(str(client_address) + " has connected.")
        client.send(f' Greetings!\nNow type your name and press enter !'.encode("utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(conn, addr):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = conn.recv(BUF_SIZE).decode("utf8")
    for nick in clients.values():
        if nick == name:
            name = name + str(1)
    welcome = 'Welcome %s! If you ever want to quit, press quit button to exit.' % name
    conn.send(bytes(welcome, "utf8"))
    msg = "%s from [%s] has joined the chat!" % (name, "{}:{}".format(addr[0], addr[1]))
    broadcast(bytes(msg, "utf8"))
    clients[conn] = name
    while True:
        msg = conn.recv(BUF_SIZE)
        if msg == bytes("!request", "utf8"):
            request_file(conn, msg)
        elif msg.startswith("##".encode()):
            Thread(target=send_file(conn, msg, addr[0]))
        elif msg == bytes("#getusers", "utf8"):
            get_users(conn, msg, "connected users: ")
        elif msg == bytes("#getfilelist", "utf8"):
            get_file_list(conn, msg, " file list->")
        elif msg.startswith('@'.encode()):
            private_message(conn, msg, name + ":")
        elif msg != bytes("#quit", "utf8"):
            broadcast(msg, name + ":")
        else:
            del clients[conn]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            conn.close()
            break


def send_file(conn, msg, client_address):
    if check[clients[conn]]:
        file_name_and_type, file_name, file_type, save_as = get_filename_and_filetype(msg)
        if file_name not in files:
            conn.send('error: file not found'.encode())
        else:
            path = os.path.abspath(file_name_and_type)
            file_size = os.path.getsize(file_name_and_type)
            send_port = get_port(conn)
            management_port = get_port(conn)
            all_data = prep_data_for_sending(path)
            conn.send(f'##download{"#"}{save_as}{"#"}{file_type}{"#"}{file_size}{"#"}{send_port}{"#"}{management_port}'.encode())
            sending(conn, client_address, send_port, management_port, all_data)
    else:
        conn.send(bytes("request before download", "utf8"))


def prep_data_for_sending(path):
    file = open(path, 'rb')
    seq = 0
    all_data = {}
    while True:
        bytes_read = file.read(CHUNK_SIZE)
        if not bytes_read:
            break
        seq_num = str(seq).encode()
        bytes_to_send = bytes_read + 'seq:'.encode() + seq_num
        all_data[seq] = bytes_to_send
        seq += 1
    file.close()
    return all_data


def sending(conn, client_address, send_port, management_port, all_data):
    udp_sock_send = socket(AF_INET, SOCK_DGRAM)
    udp_sock_management = socket(AF_INET, SOCK_DGRAM)
    udp_sock_management.bind((client_address, management_port))
    while True:
        # nack means negative acknowledge
        nack = udp_sock_management.recv(BUF_SIZE).decode("utf-8")
        print("nack", nack)
        if 'done' in nack:
            conn.send('File download completed successfully'.encode())
            all_ports[send_port] = True
            all_ports[management_port] = True
            check[clients[conn]] = False
            print('done')
            break
        else:
            packets_to_send = nack.split(',')
            for packet_num in set(packets_to_send):
                udp_sock_send.sendto(all_data[int(packet_num)], (client_address, send_port))
    udp_sock_management.close()
    udp_sock_send.close()


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
        message = "To continue the download, enter the file name with ##file_name.file_type#save_as\n"
        conn.send(message.encode())
        time.sleep(1)
        check[clients[conn]] = True


def get_users(conn, msg, prefix=""):
    if msg == '#getusers'.encode():
        connected = str(clients.values())
        connected_users = connected[11:]
        conn.send(bytes(prefix, "utf8") + connected_users.encode())


def get_file_list(conn, msg, prefix=""):
    if msg == '#getfilelist'.encode():
        file_list_str = str(files)
        conn.send(bytes(prefix, "utf8") + file_list_str.encode())


def private_message(conn, msg, prefix=""):
    check_name = False
    for name in clients.values():
        sock = get_key(name)
        name_len = len(name)
        if msg[1:name_len + 1].decode() == name:
            check_name = True
            actual_message = msg[name_len + 1:]
            sock.send(bytes(prefix, "utf8") + actual_message)
            conn.send(bytes(prefix, "utf8") + actual_message)
            break
    if not check_name:
        conn.send(f"user not found".encode())


def broadcast(msg, prefix=""):
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


def get_port(conn):
    for key in all_ports:
        if all_ports[key]:
            all_ports[key] = False
            return key
    conn.send('there is no available ports, please try again later:)'.encode())


def get_key(val):
    for key, value in clients.items():
        if val == value:
            return key


if __name__ == "__main__":
    SOCK.listen(5)
    print("Chat Server has Started !!")
    print("Waiting for incoming connections...")
    ACCEPT_THREAD = Thread(target=accept_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SOCK.close()
