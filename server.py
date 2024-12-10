from pymongo import MongoClient
from datetime import datetime, timedelta
import socket
import pytz

def calculate_average_moisture(collection_virtual, collection_metadata):
    """Calculate average moisture in the kitchen fridge over the past three hours."""
    # start time = three_hours_ago, end time = datetime.utcnow()
    three_hours_ago = datetime.utcnow() - timedelta(hours=3)
    print("current time = ", datetime.utcnow())
    print("three hours ago = ", three_hours_ago)
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
    # So we just return a pre-determined variable
    # "Water consumption of Dishwasher: 10 gallons/cycle"
    return f"Average water consumption per cycle in dishwasher: {average_water_consumption: .2f} gallons"
def find_greatest_ammeter_reading(collection):
    # Mapping of board names to their Ammeter fields
    device_info = {
        "arduino uno - board 1": "Ammeter Fridge 1",
        "board 1 30f4d706-4a8c-419b-969f-9221ba897fd7": "Ammeter Fridge 2",
        "arduino uno - board 2": "Ammeter Dishwasher"
    }

    ammeter_readings = {}


    for board_name, ammeter_field in device_info.items():
        query = {"payload.board_name": board_name}
        result = collection.find_one(query)

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

def mongoConnection(command: str) -> str:
    try:
        link = "mongodb+srv://ces7290:MzZyfX3pqH9h5N2S@cluster0.q42n7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(link)

        # MongoDB
        data = client['test']
        collection_virtual = data['iot_data2_virtual']
        collection_metadata = data['iot_data2_metadata']

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


def start_server():
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
                    client_socket.send(mongoConnection(message).encode('utf-8'))
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
