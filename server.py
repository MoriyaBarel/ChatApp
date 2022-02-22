import socket
from threading import Thread

# server's IP address
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 55000 # port we want to use
separator_token = "<SEP>" # we will use this to separate the client name & message

# initialize list/set of all connected client's sockets
client_sockets = set()
users = {}
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """

    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()
            if msg.startswith('^.^'):
                client_name = msg[3:]
                if not users.keys().__contains__(client_name):
                    cs.send('sababa'.encode())
                    users[client_name] = cs
            nekudotaim = msg.index(':')
            actual_msg = msg[nekudotaim:]
            if actual_msg.startswith('@all'):
                for sock in client_sockets:
                    sock.send(actual_msg.encode())
            if actual_msg.startswith('@@'):
                nekudotaim2 = actual_msg.index(':')
                name = actual_msg[2:nekudotaim2]
                users[name].send(actual_msg[nekudotaim2+1:])

        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)

while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")

    # add the new connected client to connected sockets
    client_sockets.add(client_socket)
    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()