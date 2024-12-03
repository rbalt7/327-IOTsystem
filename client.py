import socket
import ipaddress
import threading
import time
import contextlib
import errno

maxPacketSize = 1024
defaultPort = 4000  # Default port
serverIP = 'localhost'  # Change this to your instance IP

# Define the valid queries
valid_queries = [
    "What is the average moisture inside my kitchen fridge in the past three hours?",
    "What is the average water consumption per cycle in my smart dishwasher?",
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
]

# Initialize TCP socket
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    tcpPort = int(input("Please enter the TCP port of the host (or press Enter to use the default port): ") or defaultPort)
except ValueError:
    tcpPort = defaultPort

tcpSocket.connect((serverIP, tcpPort))

print("Connected to the server. Type your queries below (or type 'exit' to quit).")

while True:
    # Get user input
    clientMessage = input("> ")

    if clientMessage.lower() == "exit":
        print("Exiting the client...")
        break

    # Check if the input is a valid query
    if clientMessage not in valid_queries:
        print(f"Sorry, this query cannot be processed. Please try one of the following:\n{', '.join(valid_queries)}")
        continue

    # Send the valid query to the server
    tcpSocket.sendall(clientMessage.encode('utf-8'))
    print(f"Sent to server: {clientMessage}")

    # Receive and print the server's response
    data = tcpSocket.recv(maxPacketSize)
    print(f"Received from server: {data.decode('utf-8')}")

# Close the socket
tcpSocket.close()

