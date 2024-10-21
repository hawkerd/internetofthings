import socket
import threading

# dictionary to track subscribers for each topic
topics = {
    "WEATHER": [],
    "NEWS": []
}

# initialize the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to localhost IP address on port 5555
server.bind(("localhost", 5555))

# start listening for connection requests on the server
server.listen()
print("[STARTING] Server is listening on localhost:5555")

# handle messages from each client
def handle_client(conn, addr):
    print(f"[HANDLING CLIENT] {addr}")
    connected = True

    while connected:
        try:
            message = conn.recv(1024).decode('utf-8')
            if message:
                print(f"[RECEIVED] {message} from {addr}")

                # extract the type and details of the message
                parts = message.split(',')

                if len(parts) == 3 and parts[1].strip() == "SUB":
                    handle_sub(parts, conn)
                
            else:
                connected = False
        except:
            connected = False

    conn.close()

# handle message format <NAME, SUB, SUBJECT>
def handle_sub(parts, conn):
    # extract details
    client_name = parts[0].strip()
    subject = parts[2].strip()

    # add the client to the subscriber list if it exists
    if subject in topics:
        if conn not in topics[subject]:
            topics[subject].append(conn)
        conn.send(f"<SUB_ACK: Subscribed to {subject}>".encode('utf-8'))
        print(f"[SUBSCRIPTION] {client_name} subscribed to {subject}")
    else:
        conn.send(f"<ERROR: Subscription Failed - Subject {subject} Not Found>".encode('utf-8'))
        print(f"[ERROR] {client_name} tried to subscribe to non-existent subject: {subject}")
            

# repeatedly create new threads for new connections
while True:
    # accept a new connection
    conn, addr = server.accept()
    print(f"[NEW CONNECTION] {addr} connected.")

    # create a new thread to handle the client
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")