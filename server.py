import socket
import threading

# initialize the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to localhost IP address on port 5555
server.bind(("localhost", 5555))

# start listening for connection requests on the server
server.listen()
print("[STARTING] Server is listening on localhost:5555")

# handle messages from each client
def handle_client(conn, addr) :
    print(f"[HANDLING CLIENT] {addr}")
    connected = True

    while connected:
        try:
            message = conn.recv(1024).decode('utf-8') #
            if message:
                print(f"[RECEIVED] {message} from {addr}")
            else:
                connected = False
        except:
            connected = False

    conn.close()
            

# repeatedly create new threads for new connections
while True:
    # accept a new connection
    conn, addr = server.accept()
    print(f"[NEW CONNECTION] {addr} connected.")

    # create a new thread to handle the client
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")