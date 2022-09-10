import os
from socket import *
from threading import Thread


all_ports = {n: True for n in range(55001, 55016)}
clients = {}
addresses = {}
files = os.listdir('files')
PORT = 55000
BUF_SIZE = 2048
CHUNK_SIZE = 2000
SOCK = socket(AF_INET, SOCK_STREAM)
# Check if a request has been sent
check = {}
MAX_CLIENTS = 15


def accept_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SOCK.accept()
        print(str(client_address) + " has connected.")
        client.send(b'Greetings!Now type your name and press enter.')
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(tcp_sock, addr):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = tcp_sock.recv(BUF_SIZE).decode("utf8")
    for nick in clients.values():
        if nick == name:
            name = name + "1"
    welcome = f'Welcome {name}! If you ever want to quit, press quit button to exit.'
    tcp_sock.send(bytes(welcome, "utf8"))
    msg = f'{name} from [{addr[0], addr[1]}] has joined the chat!'
    broadcast(bytes(msg, "utf8"))
    clients[name] = tcp_sock
    check[name] = False
    while True:
        msg = tcp_sock.recv(BUF_SIZE)
        if msg == b'!request':
            request_file(tcp_sock, name, msg)
        elif msg.startswith(b'##'):
            Thread(target=pre_sending(tcp_sock, name, msg, addr[0]))
        elif msg == b'#getusers':
            get_users(tcp_sock, msg, "connected users: ")
        elif msg == b'#getfilelist':
            get_file_list(tcp_sock, msg, "file list->")
        elif msg.startswith(b'@'):
            private_message(tcp_sock, msg, name + ":")
        elif msg != b'#quit':
            broadcast(msg, name + ":")
        else:
            del clients[name]
            broadcast(bytes(f'{name} has left the chat.', "utf8"))
            tcp_sock.close()
            break


def pre_sending(tcp_sock, name, msg, client_address):
    if check[name]:
        file_name_and_type, file_name, file_type, save_as = get_filename_and_filetype(msg)
        if file_name_and_type not in files:
            tcp_sock.send(b'error: file not found')
        else:
            file_path = os.path.join('files', file_name_and_type)
            abs_path = os.path.abspath(file_path)
            file_size = os.path.getsize(file_path)
            send_port = get_port(tcp_sock)
            mgmt_port = get_port(tcp_sock)
            all_data = prep_data_for_sending(abs_path)
            tcp_sock.send(f'##download{"#"}{save_as}{"#"}{file_type}{"#"}{file_size}{"#"}{send_port}{"#"}{mgmt_port}'.encode())
            send_file(name, client_address, send_port, mgmt_port, all_data)
    else:
        tcp_sock.send(b'request before download')


def prep_data_for_sending(path):
    file = open(path, 'rb')
    seq = 0
    all_data = {}
    while True:
        bytes_read = file.read(CHUNK_SIZE)
        if not bytes_read:
            break
        seq_num = str(seq).encode()
        bytes_to_send = bytes_read + b'seq:' + seq_num
        all_data[seq] = bytes_to_send
        seq += 1
    file.close()
    return all_data


def send_file(name, client_address, send_port, mgmt_port, all_data):
    udp_sock_send = socket(AF_INET, SOCK_DGRAM)
    udp_sock_mgmt = socket(AF_INET, SOCK_DGRAM)
    udp_sock_mgmt.bind((client_address, mgmt_port))
    while True:
        # nack means negative acknowledge
        nack = udp_sock_mgmt.recv(BUF_SIZE).decode("utf-8")
        if 'done' in nack:
            all_ports[send_port] = True
            all_ports[mgmt_port] = True
            check[name] = False
            print('done')
            break
        else:
            packets_to_send = nack.split(',')
            for packet_num in set(packets_to_send):
                udp_sock_send.sendto(all_data[int(packet_num)], (client_address, send_port))
    udp_sock_mgmt.close()
    udp_sock_send.close()


def get_filename_and_filetype(msg: bytes):
    MSG_PREFIX = 2
    actual_msg = msg[MSG_PREFIX:]
    file_name_and_type, save_as = actual_msg.decode("utf-8").split("#")
    filename, file_type = file_name_and_type.split('.')
    return file_name_and_type, filename, file_type, save_as


def request_file(tcp_sock, name, msg):
    if msg == b'!request':
        message = "To continue the download, enter the file name with ##file_name.file_type#save_as"
        tcp_sock.send(message.encode())
        check[name] = True


def get_users(tcp_sock, msg, prefix=""):
    if msg == b'#getusers':
        connected = str(clients.keys())
        MSG_PREFIX = 10
        connected_users = connected[MSG_PREFIX:-1]
        tcp_sock.send(bytes(prefix, "utf8") + connected_users.encode())


def get_file_list(tcp_sock, msg, prefix=""):
    if msg == b'#getfilelist':
        file_list_str = str(files)
        tcp_sock.send(bytes(prefix, "utf8") + file_list_str.encode())


def private_message(tcp_sock, msg, prefix=""):
    check_name = False
    for name in clients:
        sock = clients[name]
        name_len = len(name)
        if msg[1:name_len + 1].decode() == name:
            check_name = True
            actual_message = msg[name_len + 1:]
            sock.send(bytes(prefix, "utf8") + actual_message)
            tcp_sock.send(bytes(prefix, "utf8") + actual_message)
            break
    if not check_name:
        tcp_sock.send(b'user not found')


def broadcast(msg, prefix=""):
    for sock in clients.values():
        sock.send(bytes(prefix, "utf8") + msg)


def get_port(tcp_sock):
    for key in all_ports:
        if all_ports[key]:
            all_ports[key] = False
            return key
    tcp_sock.send(b'there is no available ports, please try again later:)')


if __name__ == "__main__":
    SOCK.bind(('', PORT))
    SOCK.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    SOCK.listen(MAX_CLIENTS)
    print("Chat Server has Started !!")
    print("Waiting for incoming connections...")
    ACCEPT_THREAD = Thread(target=accept_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SOCK.close()
