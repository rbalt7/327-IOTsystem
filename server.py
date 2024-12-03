import socket
import threading
import time
import contextlib
import errno
from pymongo import MongoClient
from datetime import datetime
from dataclasses import dataclass

exitSignal = 0
maxPacketSize = 1024
defaultPort = 4000  # Set this to your preferred port

# Connect to MongoDB
def connect_to_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["iot_data"]
    return db

db = connect_to_db()

# Binary Tree Implementation for Efficient Data Management
class Node:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, key, data):
        if not self.root:
            self.root = Node(key, data)
        else:
            self._insert(self.root, key, data)

    def _insert(self, current_node, key, data):
        if key < current_node.key:
            if current_node.left:
                self._insert(current_node.left, key, data)
            else:
                current_node.left = Node(key, data)
        elif key > current_node.key:
            if current_node.right:
                self._insert(current_node.right, key, data)
            else:
                current_node.right = Node(key, data)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, current_node, key):
        if not current_node:
            return None
        if key == current_node.key:
            return current_node.data
        elif key < current_node.key:
            return self._search(current_node.left, key)
        else:
            return self._search(current_node.right, key)

# Query database for metadata and build binary tree
def build_metadata_tree():
    metadata_tree = BinaryTree()
    devices = db["devices"].find()
    for device in devices:
        metadata_tree.insert(device["device_id"], device)
    return metadata_tree

metadata_tree = build_metadata_tree()

# Helper function for unit conversions
def convert_to_relative_humidity(moisture_reading):
    return round((moisture_reading / 100.0) * 100, 2)

def convert_to_gallons(liters):
    return round(liters * 0.264172, 2)

def convert_to_kwh(joules):
    return round(joules / 3600000, 2)

# Handle incoming TCP connections
def listen_on_tcp(connection_socket, socket_address):
    while True:
        data = connection_socket.recv(maxPacketSize)
        if data == b"exit":
            global exitSignal
            exitSignal = 1
            break

        if data:
            query = data.decode("utf-8")
            print(f"Received query from {socket_address}: {query}")

            # Process the query
            response = process_query(query)

            # Send response back to the client
            connection_socket.sendall(response.encode("utf-8"))
            print("Response sent back to client.")
        else:
            print(f"No data received from client at {socket_address}")
            break

    print(f"Connection closed to {socket_address}.")
    connection_socket.close()

# Process incoming queries
def process_query(query):
    if query == "What is the average moisture inside my kitchen fridge in the past three hours?":
        # Query the database for moisture data
        device_data = metadata_tree.search("fridge")
        if device_data:
            avg_moisture = sum(device_data["moisture_readings"]) / len(device_data["moisture_readings"])
            rh = convert_to_relative_humidity(avg_moisture)
            return f"The average relative humidity in the fridge over the past three hours is {rh}%."
        return "Device data not found."

    elif query == "What is the average water consumption per cycle in my smart dishwasher?":
        # Query the database for water consumption data
        device_data = metadata_tree.search("dishwasher")
        if device_data:
            avg_liters = sum(device_data["water_consumption"]) / len(device_data["water_consumption"])
            gallons = convert_to_gallons(avg_liters)
            return f"The average water consumption per cycle in the dishwasher is {gallons} gallons."
        return "Device data not found."

    elif query == "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?":
        # Compare electricity consumption
        fridge1 = metadata_tree.search("fridge1")
        fridge2 = metadata_tree.search("fridge2")
        dishwasher = metadata_tree.search("dishwasher")

        if fridge1 and fridge2 and dishwasher:
            fridge1_kwh = convert_to_kwh(fridge1["electricity_usage"])
            fridge2_kwh = convert_to_kwh(fridge2["electricity_usage"])
            dishwasher_kwh = convert_to_kwh(dishwasher["electricity_usage"])

            max_usage = max(fridge1_kwh, fridge2_kwh, dishwasher_kwh)
            if max_usage == fridge1_kwh:
                return "Fridge 1 consumed the most electricity."
            elif max_usage == fridge2_kwh:
                return "Fridge 2 consumed the most electricity."
            else:
                return "The dishwasher consumed the most electricity."
        return "Device data not found."

    else:
        return "Invalid query. Please send a valid query."

# Create TCP socket
def create_tcp_socket():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(('localhost', defaultPort))
    tcp_socket.listen(5)
    print(f"Server listening on port {defaultPort}")
    return tcp_socket

# Launch TCP threads
def launch_tcp_threads():
    tcp_socket = create_tcp_socket()
    while True:
        connection_socket, connection_address = tcp_socket.accept()
        threading.Thread(target=listen_on_tcp, args=(connection_socket, connection_address)).start()

# Main execution
if __name__ == "__main__":
    tcp_thread = threading.Thread(target=launch_tcp_threads)
    tcp_thread.start()

    while not exitSignal:
        time.sleep(1)

    print("Shutting down the server...")
