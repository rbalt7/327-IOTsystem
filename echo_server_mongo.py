from pymongo import MongoClient
from datetime import datetime, timedelta,timezone
from urllib.parse import quote_plus
import socket
import pytz

def calculate_average_moisture(collection):
    """Calculate average moisture in the kitchen fridge over the past three hours."""
    # start time = three_hours_ago, end time = datetime.utcnow()
    three_hours_ago = datetime.now(timezone.utc) - timedelta(hours=3)
    print("current time = ", datetime.now(timezone.utc))
    print("three hours ago = ", three_hours_ago)
    # , "payload.asset_uid": "h0t-x8q-7ai-v5g"
    # 'timestamp': {"$lte": datetime.now(), "$gte": three_hours_ago}
    # 'time': {"$lte": datetime.now(), "$gte": three_hours_ago},
    query = {"payload.asset_uid": "h0t-x8q-7ai-v5g", 'time': {"$gte": three_hours_ago}}
    results = collection.find(query)

    # Check if we have any results
    if collection.count_documents(query) > 0:
        print("Query returned results.")
    else:
        print("Query returned no results.")

    total_moisture = 0
    count = 0

    #testing time format here
    for result in results:
        total_moisture += float(result['payload'].get('Moisture Meter Fridge', 0))
        # testing time format here
        print(result['time'])
        count += 1
    print("count = ", count)
    if count == 0:
        return "No moisture data available for the past 3 hours."

    average_moisture = total_moisture / count
    print(f"Average moisture in the fridge in past 3 hours: {average_moisture}")

    return(f"Average moisture in the fridge in past 3 hours: {average_moisture: .2f} %")
def dishwasher_water_consumption(collection):
    # Water consumption per cycle is generally pre-determined
    query = {"payload.asset_uid": "y7n-vo4-g2f-hi4"}
    results = collection.find(query)

    # Check if we have any results
    if collection.count_documents(query) > 0:
        print("Query returned results.")
    else:
        print("Query returned no results.")

    total_water_consumption = 0
    count = 0

    for result in results:
        total_water_consumption += float(result['payload'].get('Water Level Sensor', 0))
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
        "Raspberry Pi 4 - pi": "Ammeter",
        "board 2 172c8747-1fe7-4fe2-bae1-ef320ba4bafb": "Ammeter Fridge",
        "board 1 377a33c8-ff29-48a3-9b4b-b2333d911c3e": "Ammeter Dishwasher"
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
        username = quote_plus("alvaromora015")
        password = quote_plus("@Callofduty1")
        link = f"mongodb+srv://{username}:{password}@cluster0.wfhb7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(link)

        # MongoDB
        data = client['test']
        collection = data['Table_virtual']

        if command == "1":
            return calculate_average_moisture(collection)
        elif command == "2":
            return dishwasher_water_consumption(collection)
        elif command == "3":
            return find_greatest_ammeter_reading(collection)
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
