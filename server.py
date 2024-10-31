import socket
import threading
import queue
import time

# ANSI color codes
PURPLE = "\033[35m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
RESET = "\033[0m"

# list of topics and updates
topics: dict[str, list[str]] = {
    "WEATHER": [],
    "NEWS": []
}

# client object
class Client:
    def __init__(self):
        self.connection = None
        self.subscriptions: list[str] = []
        self.messages_queue = queue.Queue()

# dictionary mapping client names to client info
clients: dict[str, Client] = {}


# handle messages from each client
def handle_client(conn, addr):
    connected : bool = True
    registered : bool = False
    client_name : str | None = None

    # handle outgoing messages
    def send_messages_from_queue(client_name : str):
        while connected:
            time.sleep(2)
            while not clients[client_name].messages_queue.empty():
                clients[client_name].connection.send(clients[client_name].messages_queue.get())
                time.sleep(0.5)

    # handle incoming messages
    while connected:
        try:
            message = conn.recv(1024).decode()
            if message:
                print(f"{CYAN}[RECEIVED]{RESET} {message} from {addr.}")

                # extract the type and details of the message
                parts = message.split(',')

                if not registered:
                    if len(parts) == 2 and ((parts[1].strip() == "CONN") or (parts[1].strip() == "RECONNECT")):
                        client_name = parts[0].strip()
                        handle_connect(client_name, conn)

                        # begin thread to handle notifying client
                        threading.Thread(target=send_messages_from_queue, args=(client_name,), daemon=True).start()

                        # mark connection as registered
                        registered = True
                    else:
                        conn.send(f"ERROR: Client Not Connected - Must Register First\n".encode())
                        print(f"{RED}[ERROR]{RESET} Client tried to operate without registering")
                        return
                else:
                    # Handle SUBSCRIBE
                    if len(parts) == 3 and parts[1].strip() == "SUB":
                        handle_sub(parts[0].strip(), parts[2].strip(), conn)
                    
                    # Handle PUBLISH
                    elif len(parts) == 4 and parts[1].strip() == "PUB":
                        handle_publish(parts[0].strip(), parts[2].strip(), parts[3].strip(), conn)
                    
                    # Handle DISCONNECT
                    elif message.strip() == "DISC":
                        handle_disconnect(client_name, conn)
                        connected = False

                    else:
                        conn.send(f"ERROR: Invalid Request\n".encode())
                        print(f"{RED}[ERROR]{RESET} {client_name} made invalid request")
                        return
            else:
                connected = False
        except:
            connected = False

    conn.close()

# handle message format <CLIENT_NAME, PUB, SUBJECT, MSG>
def handle_publish(client_name, subject, msg, conn):

    # make sure client is connected
    if clients[client_name].connection is None:
        conn.send(f"ERROR: Publish Failed - Client Not Connected\n".encode())
        print(f"{RED}[ERROR]{RESET} {client_name} tried to subscribe before logging in")
        return

    # make sure the subject exists
    if subject not in topics:
        conn.send(f"ERROR: Publish Failed - Subject {subject} Not Found\n".encode())
        print(f"{RED}[ERROR]{RESET} {client_name} tried to publish to non-existent subject: {subject}")
        return

    # add the message to the history
    topics[subject].append(f"NOTIFY: {subject} - {client_name}: {msg}\n")

    # forward the message to all subscribers
    for name, client in clients.items():
        if subject in client.subscriptions:
            client.messages_queue.put(f"NOTIFY: {subject} - {client_name}: {msg}\n".encode())
            print(f"{PURPLE}[ENQUEUE]{RESET} Message enqueued for {name}")

    # respond to the publishing client
    conn.send(f"PUBLISH: Published to {subject}\n".encode())
    print(f"{PURPLE}[PUBLISH]{RESET} {client_name} published to {subject}: {msg}")

# handle message format <NAME, SUB, SUBJECT>
def handle_sub(client_name, subject, conn):
    if (client_name not in clients) or (clients[client_name].connection is None):
        conn.send(f"ERROR: Subscribe Failed - Client Not Registered\n".encode())
        print(f"{RED}[ERROR]{RESET} {client_name} tried to subscribe before logging in")
        return

    # add the client to the subscriber list if it exists
    if subject in topics:
        if subject not in clients[client_name].subscriptions:
            clients[client_name].subscriptions.append(subject)

            # enqueue all past updates
            for past_message in topics[subject]:
                clients[client_name].messages_queue.put(past_message.encode())

            conn.send(f"SUB_ACK: Subscribed to {subject}\n".encode())
            print(f"{PURPLE}[SUBSCRIPTION]{RESET} {client_name} subscribed to {subject}")
        else:
            conn.send(f"SUB_ACK: Already subscribed to {subject}\n".encode())
    else:
        conn.send(f"ERROR: Subscription Failed - Subject {subject} Not Found\n".encode())
        print(f"{RED}[ERROR]{RESET} {client_name} tried to subscribe to non-existent subject: {subject}")
            
# handle message format <NAME, CONN>
def handle_connect(client_name, conn):
    # if client is already registered, reconnect
    if client_name in clients:
        clients[client_name].connection = conn

        print(f"{PURPLE}[RECONNECT]{RESET} {client_name} connected.")
        conn.send("RECONNECT_ACK\n".encode())
        return
    
    # create a new client
    client = Client()
    client.connection = conn

    # add the client to the dictionary
    clients[client_name] = client

    # respond to the client
    print(f"{PURPLE}[CONNECT]{RESET} {client_name} connected.")
    conn.send("CONN_ACK\n".encode())

# handle message format <DISC>
def handle_disconnect(client_name, conn):
    # respond to client
    conn.send("DISC_ACK\n".encode())

    # wipe the connection from the dictionery
    if client_name == None:
        print(f"{PURPLE}[DISCONNECT]{RESET} Client disconnected.")
    else:
        if client_name in clients:
            clients[client_name].connection = None
        print(f"{PURPLE}[DISCONNECT]{RESET} {client_name} disconnected.")



# initialize the server, bind it to port 5555, and start listening for connection requests
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 5555))
server.listen()
print(f"{CYAN}[STARTING]{RESET} Server is listening on localhost:5555")

# repeatedly create new threads for new connections
try:
    while True:
        # accept a new connection-
        conn, addr = server.accept()
        print(f"{CYAN}[NEW CONNECTION]{RESET} {addr} connected. Active connections: {threading.active_count()}")

        # create a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
except KeyboardInterrupt:
    print(f"\n{CYAN}[SHUTTING DOWN]{RESET} Server is shutting down.")
    server.close()
    quit()
    exit()