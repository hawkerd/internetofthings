# Internet of Things

This project implementes a basic messaging system using a publish-subscribe model. Clients can connect to a server, subscribe to topics, and receive messages published by
other clients. Publishers send messages to the server, which forwards the messages to any subscribed clients. Based on a simplified version of the MQTT protocol. The server
is multithreaded to handle multiple connections at once.

The purpose of this project is to understand socket programming and concurrent client-server communication.

Usage:

To start the server, run the provided script.
```
$ python3 server.py
```

To connect to the server as a client, execute the following any number of times.
```
$ python3 client.py
```

### Code Design
This project was written in Python. 

#### Server Design
A server constantly listens for incoming connection requests. If it receives a requests, it creates a new thread to handle that client. The server will listen for messages of the form CONN, RECONNECT, DISC, PUBLISH, and SUB, and respond accordingly. A dictionary is used to map client name to http connection and a queue of outgoing messages. Each client thread repeatedly pulls from this queue to push messages to the clients. After RECONNECT, the client will be met with a list of their subscribed topics that they missed.

#### Client Design
The client initiates a connection with the server. Once connected, the client uses a command line interface to send commands line CONN, RECONNECT, DISC, PUBLISH, and SUB. Any messages from the server will be displayed in real time.