from pymongo import MongoClient
from datetime import datetime, timedelta
import socket

# Saves metadata info for each device
device_list = []

# Function to extract metadata
def extract_metadata_info(document, device_list):
    device = {}
    sensors = []

    # device info
    device["assetUid"] = document["assetUid"]
    device["name"] = document["customAttributes"]["name"]
    device["boards"] = [] # A list to hold board information

    # Iterate over boards
    for child1 in document["customAttributes"].get("children", []):
        board = {
            "name": child1["customAttributes"]["name"],
            "sensors": []
        }

        # Iterate over sensors in the board
        for child2 in child1["customAttributes"].get("children", []):
            sensor = {
                "name": child2["customAttributes"]["name"],
                "unit": child2["customAttributes"].get("unit", ""),
                "minValue": child2["customAttributes"].get("minValue", ""),
                "maxValue": child2["customAttributes"].get("maxValue", ""),
                "DMinValue": child2["customAttributes"].get("desiredMinValue", ""),
                "DMaxValue": child2["customAttributes"].get("desiredMaxValue", "")
            }
            board["sensors"].append(sensor)

        device["boards"].append(board)

    # Append the complete device info to the list
    device_list.append(device)


# Function to find average humidity in fridge
def calculate_average_moisture(collection_virtual, collection_metadata):
    """Calculate average moisture in the kitchen fridge over the past three hours."""
    three_hours_ago = datetime.utcnow() - timedelta(hours=3)
    # Get fridge id
    query = {"customAttributes.name": {"$regex": "fridge", "$options": "i"}}
    device_id = collection_metadata.find_one(query)['assetUid']
    # Get fridge moisture meter data
    query = {"payload.parent_asset_uid": device_id, 'time': {"$gte": three_hours_ago}}
    results = collection_virtual.find(query)

    # Check if we have any results
    if collection_virtual.count_documents(query) > 0:
        print("Query returned results.")
    else:
        print("Query returned no results.")

    total_moisture = 0
    count = 0

    # Find average moisture reading
    for result in results:
        # Enter sensor name here
        total_moisture += float(result['payload'].get('Moisture Meter 1', 0))
        # testing time format here
        print(result['time'])
        count += 1
    print("count = ", count)
    if count == 0:
        return "No moisture data available for the past 3 hours."

    average_moisture = total_moisture / count
    print(f"Average moisture in the fridge in past 3 hours: {average_moisture}")

    return(f"Average moisture in the fridge in past 3 hours: {average_moisture: .2f} %")


# Function to find average water consumption in dishwasher
def dishwasher_water_consumption(collection_virtual, collection_metadata):
    # Get dishwasher id
    query = {"customAttributes.name": {"$regex": "Dishwasher", "$options": "i"}}
    device_id = collection_metadata.find_one(query)['assetUid']
    # Get dishwasher water sensor data
    query = {"payload.parent_asset_uid": device_id}
    results = collection_virtual.find(query)

    # Check if we have any results
    if collection_virtual.count_documents(query) > 0:
        print("Query returned results.")
    else:
        print("Query returned no results.")

    total_water_consumption = 0
    count = 0

    for result in results:
        total_water_consumption += float(result['payload'].get('Water Flow Sensor', 0))
        count += 1
    print("count = ", count)
    if count == 0:
        return "No water consumption data available."

    average_water_consumption = total_water_consumption / count
    return f"Average water consumption per cycle in dishwasher: {average_water_consumption: .2f} gallons"


# Function to find device with the highest ammeter reading
def find_greatest_ammeter_reading(collection_virtual):
    # Mapping of board names to their Ammeter fields
    device_info = {}
    board_name = ""
    for device in device_list:
        for board in device.get("boards", []):
            board_name = board["name"]
            for sensor in board.get("sensors", []):
                if "Ammeter" in sensor["name"]:
                    device_info[board_name] = sensor["name"]
                    break
            else:
                continue

    ammeter_readings = {}

    for board_name, ammeter_field in device_info.items():
        query = {"payload.board_name": board_name}
        result = collection_virtual.find_one(query)

        if result:
            # Ammeter
            ammeter_reading = float(result['payload'].get(ammeter_field, 0))
            ammeter_readings[board_name] = ammeter_reading

    max_board = max(ammeter_readings, key=ammeter_readings.get)
    max_reading = ammeter_readings[max_board]

    print("Ammeter measurement:")
    for board, reading in ammeter_readings.items():
        print(f"  {board}: {reading} Amps")

    print(f"Highest Ammeter reading: {max_board} ({max_reading} A)")
    return(f"Highest Ammeter reading: {max_board} ({max_reading} A)")


# Function to connect to mongoDB cluster and reply to client
def mongoConnection(command: str, flg) -> str:
    device_list.clear()
    try:
        link = "mongodb+srv://ces7290:MzZyfX3pqH9h5N2S@cluster0.q42n7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(link)

        # MongoDB
        data = client['test']
        collection_virtual = data['iot_data2_virtual']
        collection_metadata = data['iot_data2_metadata']

        # Extract metadata info for each device, store in dictionary list
        devices = collection_metadata.find()
        for device in devices:
            extract_metadata_info(device, device_list)

        # Client message commands
        if command == "1":
            return calculate_average_moisture(collection_virtual, collection_metadata)
        elif command == "2":
            return dishwasher_water_consumption(collection_virtual, collection_metadata)
        elif command == "3":
            return find_greatest_ammeter_reading(collection_virtual)
        else:
            return "Incorrect command. Try again. 1, 2, 3, or 4."

    except Exception as error:
        print(f"Error connecting to MongoDB: {error}")


# Function to start server
def start_server():
    flag = False
    # Input our port and host
    port = int(input("Enter the port number for server hosting:"))
    # 0.0.0.0 for Locahost
    #host = '0.0.0.0'
    # 10.39.30.228 is wi-fi IPv4
    #host = '10.39.30.228'
    host = input("Enter the host IP for server hosting:")


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind to the proper port
        server_socket.bind((host, port))

        # Listening
        server_socket.listen(5)
        print(f"Server is now listening on {host}:{port}")

        while True:
            # Accept the connection from client
            client_socket, client_address = server_socket.accept()
            print(f" Client connection : {client_address}")

            while True:
                try:

                    # Attempt to recieve clients message
                    message = client_socket.recv(1024).decode('utf-8')

                    if not message:
                        break

                    print(f"Recieved message from client: {message}")

                    # Convert to uppercase
                    # capitalized_message = message.upper()

                    #Send it back capitalized
                    #client_socket.send(capitalized_message.encode('utf-8'))
                    client_socket.send(mongoConnection(message, flag).encode('utf-8'))
                except ConnectionResetError:
                    print("Connection Reset Error")
                    break
                except Exception as error:
                    print(f"Unexpected Error: {error}")
                    client_socket.send(f"Server error: {error}".encode('utf-8'))

            print(f"Connection closed with {client_address}")
            client_socket.close()

    except Exception as error:
        print(f"Error: {error}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
    #TO DO: Client request and call functions
