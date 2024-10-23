import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            # listen for messages
            message = client_socket.recv(1024).decode()
            if message:
                print(f"\n[NOTIFICATION] {message}")
            else:
                break
        except:
            # error handling
            print("[ERROR] Connection closed or error in receiving messages.")
            break

def connect(host, port, client_name):
    # connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # send connect command
    client_socket.send(f"{client_name}, CONN\n".encode())
    response = client_socket.recv(1024).decode()
    print(f"\033[35mServer: {response}\033[0m")

    return client_socket

def subscribe(client_socket, client_name, subject):
    # send subscribe command
    client_socket.send(f"{client_name}, SUB, {subject}\n".encode())
    response = client_socket.recv(1024).decode()
    print(f"\033[35mServer: {response}\033[0m")

def publish(client_socket, client_name, subject, message):
    # send publish command
    client_socket.send(f"{client_name}, PUB, {subject}, {message}\n".encode())
    response = client_socket.recv(1024).decode()
    print(f"\033[35mServer: {response}\033[0m")

def disconnect(client_socket):
    # send disconnect command
    client_socket.send(f"DISC\n".encode())
    response = client_socket.recv(1024).decode()
    print(f"\033[35mServer: {response}\033[0m")
    client_socket.close()


if __name__ == "__main__":
    try:
        # get user input for client name
        client_name = input("Enter your client name: ")

        # connect to the server
        client_socket = connect('localhost', 5555, client_name)
        
        # create thread for listening
        receive_thread = threading.Thread(target=receive_messages, args=([client_socket]))
        receive_thread.daemon = True
        receive_thread.start()

        # loop to send commands
        while True:
            print("\nOptions: [1] Subscribe, [2] Publish, [3] Disconnect")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                subject = input("Enter subject to subscribe to (WEATHER, NEWS): ")
                subscribe(client_socket, client_name, subject)
            elif choice == "2":
                subject = input("Enter subject to publish to: ")
                message = input("Enter your message: ")
                publish(client_socket, client_name, subject, message)
            elif choice == "3":
                disconnect(client_socket)
                break
            else:
                print("Invalid option, please try again.")
    except KeyboardInterrupt:
        try:
            disconnect(client_socket)
        except:
            exit()