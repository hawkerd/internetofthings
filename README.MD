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