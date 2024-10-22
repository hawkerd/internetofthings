import socket
import threading

# dictionary to track subscribers for each topic
topics = {
    "WEATHER": [],
    "NEWS": []
}

# dictionary to map client names to connections
client_connections = {}

# initialize the server, bind it to port 5555, and start listening for connection requests
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 5555))
server.listen()
print("[STARTING] Server is listening on localhost:5555")

# handle messages from each client
def handle_client(conn, addr):
    connected = True
    client_name = None

    while connected:
        try:
            message = conn.recv(1024).decode('utf-8')
            if message:
                print(f"[RECEIVED] {message} from {addr}")

                # extract the type and details of the message
                parts = message.split(',')

                # Handle CONNECT
                if len(parts) == 2 and parts[1].strip() == "CONN":
                    client_name = parts[0].strip()
                    handle_connect(client_name, conn)

                # Handle SUBSCRIBE
                elif len(parts) == 3 and parts[1].strip() == "SUB":
                    handle_sub(parts[0].strip(), parts[2].strip(), conn)
                
                # Handle PUBLISH
                elif len(parts) == 4 and parts[1].strip() == "PUB":
                    handle_publish(parts[0].strip(), parts[2].strip(), parts[3].strip(), conn)
                
                # Handle DISCONNECT
                elif message.strip() == "DISC":
                    handle_disconnect(client_name, conn)
                    connected = False
                
            else:
                connected = False
        except:
            connected = False

    conn.close()

# handle message format <CLIENT_NAME, PUB, SUBJECT, MSG>
def handle_publish(client_name, subject, msg, conn):
    # make sure client is connected
    if client_connections.get(client_name) is None:
        conn.send(f"ERROR: Subscription Failed - Client Not Connected\n".encode('utf-8'))
        print(f"[ERROR] {client_name} tried to subscribe before logging in")
        return

    # make sure the subject exists
    if subject not in topics:
        conn.send(f"ERROR: Publish Failed - Subject {subject} Not Found\n".encode('utf-8'))
        print(f"[ERROR] {client_name} tried to publish to non-existent subject: {subject}")
        return
    
    # forward the message to all subscribers
    for subscriber in topics[subject]:
        subscriber_conn = client_connections[subscriber]
        if subscriber_conn is not None:
            subscriber_conn.send(f"{subject} - {client_name}: {msg}\n".encode('utf-8'))
    
    print(f"[PUBLISH] {client_name} published to {subject}: {msg}")

# handle message format <NAME, SUB, SUBJECT>
def handle_sub(client_name, subject, conn):
    # make sure client is connected
    if client_connections.get(client_name) is None:
        conn.send(f"ERROR: Subscribe Failed - Client Not Connected\n".encode('utf-8'))
        print(f"[ERROR] {client_name} tried to subscrtibe before logging in")
        return

    # add the client to the subscriber list if it exists
    if subject in topics:
        if client_name not in topics[subject]:
            topics[subject].append(client_name)
        conn.send(f"SUB_ACK: Subscribed to {subject}\n".encode('utf-8'))
        print(f"[SUBSCRIPTION] {client_name} subscribed to {subject}")
    else:
        conn.send(f"ERROR: Subscription Failed - Subject {subject} Not Found\n".encode('utf-8'))
        print(f"[ERROR] {client_name} tried to subscribe to non-existent subject: {subject}")
            
# handle message format <NAME, CONN>
def handle_connect(client_name, conn):
    # associate the connection with the name
    client_connections[client_name] = conn

    # respond to the client
    print(f"[CONNECT] {client_name} connected.")
    conn.send("CONN_ACK\n".encode('utf-8'))

# handle message format <DISC>
def handle_disconnect(client_name, conn):
    # respond to client
    conn.send("DISC_ACK\n".encode('utf-8'))

    # wipe the connection from the dictionery
    if client_name == None:
        print("[DISCONNECT] Client disconnected.")
    else:
        client_connections[client_name] = None
        print(f"[DISCONNECT] {client_name} disconnected.")



# repeatedly create new threads for new connections
try:
    while True:
        # accept a new connection
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")

        # create a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
except KeyboardInterrupt:
    print("\n[SHUTTING DOWN] Server is shutting down.")
    server.close()