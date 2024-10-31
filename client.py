import socket
import threading
import queue

# data structure to messages to/from the server
in_messages = queue.Queue()
out_messages = queue.Queue()

# global variables
client_name = None

# ANSI color codes
PURPLE = "\033[35m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
RESET = "\033[0m"

def receive_messages(client_socket):
    while True:
        try:
            # listen for messages
            message = client_socket.recv(1024).decode()
            if message:
                if message.startswith("NOTIFY: "):
                    print(f"\n{YELLOW}[NOTIFICATION]{RESET} {message[len('NOTIFY: '):]}")
                else:
                    in_messages.put(message)
            else:
                break
        except:
            # error handling
            print("{RED}[ERROR]{RESET} Connection closed or error in receiving messages.")
            break

def send_messages(client_socket):
    while True:
        try:
            # send messages from the queue
            message = out_messages.get()
            if message:
                client_socket.send(message.encode())
            else:
                break
        except:
            # error handling
            print(f"{RED}[ERROR]{RESET} Connection closed or error in sending messages.")
            break

def wait_for_response():
    # add new message to the queue
    while True:
        message = in_messages.get()
        if message:
            return message

def reconnect():
    # send reconnect command, print server output
    out_messages.put(f"{client_name}, RECONNECT\n")
    print(f"\n{PURPLE}[SERVER]{RESET} {wait_for_response()}")  

def connect():
    # send connect command, print server output
    out_messages.put(f"{client_name}, CONN\n")
    print(f"\n{PURPLE}[SERVER]{RESET} {wait_for_response()}")

def subscribe(subject):
    # send subscribe command, print server output
    out_messages.put(f"{client_name}, SUB, {subject}\n")
    print(f"\n{PURPLE}[SERVER]{RESET} {wait_for_response()}")

def publish(subject, message):
    # send publish command, print server output
    out_messages.put(f"{client_name}, PUB, {subject}, {message}\n")
    print(f"\n{PURPLE}[SERVER]{RESET} {wait_for_response()}")

def disconnect():
    # send disconnect command, print server output
    out_messages.put("DISC\n")
    print(f"\n{PURPLE}[SERVER]{RESET} {wait_for_response()}")

if __name__ == "__main__":
    try:
        # get user input for client name
        client_name = input(f"{CYAN}Enter your client name: {RESET}")

        # connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 5555))
        
        # start threads for listening and sending messages to the server
        listen_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        listen_thread.daemon = True
        listen_thread.start()
        send_thread = threading.Thread(target=send_messages, args=(client_socket,))
        send_thread.daemon = True
        send_thread.start()


        # loop to send commands
        while True:
            choice = input(f"{CYAN}\nOptions: [1] Subscribe, [2] Publish, [3] Connect, [4] Reconnect, [5] Disconnect: {RESET}")

            if choice == "1" or choice.lower() == "subscribe":
                subject = input(f"{CYAN}Enter subject to subscribe to (WEATHER, NEWS): {RESET}")
                subscribe(subject)
            elif choice == "2" or choice.lower() == "publish":
                subject = input(f"{CYAN}Enter subject to publish to: {RESET}")
                message = input(f"{CYAN}Enter your message: {RESET}")
                publish(subject, message)
            elif choice == "3" or choice.lower() == "connect":
                connect()
            elif choice == "4" or choice.lower() == "reconnect":
                reconnect()
            elif choice == "5" or choice.lower() == "disconnect":
                disconnect()
                client_socket.close()
                break
            else:
                print(f"{RED}[ERROR]{RESET} Invalid option, please try again.")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[INFO]{RESET} Ctrl+C detected, disconnecting")
        try:
            disconnect(client_socket)
        except:
            exit()