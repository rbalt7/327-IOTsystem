from pymongo import MongoClient
from typing import List, Optional, Any
from datetime import datetime, timedelta

# Global variables (adjust as needed for your application)
DBName = "test"  # Replace with your actual database name
connectionURL = "mongodb+srv://ces7290:MzZyfX3pqH9h5N2S@cluster0.q42n7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
currentDBName = None
running = False
filterTime = None
sensorTable = "iot_data2_virtual"  # Change this to the name of your sensor data table


def QueryToList(query) -> List[Any]:
    """
    Converts the result of a MongoDB query to a Python list.
    
    Args:
        query: The MongoDB query result (cursor).

    Returns:
        A list containing all the documents from the query.
    """
    list_result = []
    for doc in query:
        list_result.append(doc)
    return list_result


def QueryDatabase() -> Optional[List[str]]:
    """
    Connects to the MongoDB database and retrieves the collection names.

    Returns:
        A list of collection names if successful, or None if an error occurs.
    """
    global DBName
    global connectionURL
    global currentDBName
    global running
    global filterTime
    global sensorTable

    cluster = None
    client = None
    db = None
    try:
        # Establish connection to MongoDB
        cluster = connectionURL
        client = MongoClient(cluster)
        db = client[DBName]
        print("Connected to the database.")
        print("Database collections: ", db.list_collection_names())

        # Ask the user which collection they'd like to draw from
        sensorTable = db[sensorTable]
        print("Table:", sensorTable)

        # Return the list of collections
        return db.list_collection_names()
    except Exception as e:
        print(f"Error querying database: {e}")
        return None


def calculate_average_moisture(collection_virtual, collection_metadata) -> str:
    """
    Calculates the average moisture in the kitchen fridge over the past 3 hours.
    
    Args:
        collection_virtual: The MongoDB collection for virtual data.
        collection_metadata: The MongoDB collection for metadata.

    Returns:
        A string describing the average moisture or an error message.
    """
    three_hours_ago = datetime.now() - timedelta(hours=3)
    print(f"Fetching data since {three_hours_ago}")

    try:
        # Query metadata for the fridge
        query = {"customAttributes.name": {"$regex": "Fridge", "$options": "i"}}
        fridge_metadata = collection_metadata.find_one(query)
        if not fridge_metadata:
            return "No metadata available for the fridge."
        fridge_uid = fridge_metadata["assetUid"]

        # Query virtual data for the fridge
        query = {
            "payload.parent_asset_uid": fridge_uid,
            "time": {"$gte": three_hours_ago}
        }
        results = list(collection_virtual.find(query))

        if not results:
            return "No data found for the fridge in the past 3 hours."

        # Calculate average moisture
        total_moisture = sum(
            float(entry["payload"].get("Moisture Meter1", 0)) +
            float(entry["payload"].get("Moisture Meter2", 0))
            for entry in results
        )
        average_moisture = total_moisture / len(results)
        return f"Average moisture in the fridge: {average_moisture:.2f} RH%."
    except Exception as e:
        return f"Error calculating average moisture: {e}"


def dishwasher_water_consumption(collection_virtual, collection_metadata) -> str:
    """
    Calculates the average water consumption per cycle for the dishwasher.

    Args:
        collection_virtual: The MongoDB collection for virtual data.
        collection_metadata: The MongoDB collection for metadata.

    Returns:
        A string describing the average water consumption or an error message.
    """
    try:
        # Query metadata for the dishwasher
        query = {"customAttributes.name": {"$regex": "Dishwasher", "$options": "i"}}
        dishwasher_metadata = collection_metadata.find_one(query)
        if not dishwasher_metadata:
            return "No metadata available for the dishwasher."
        dishwasher_uid = dishwasher_metadata["assetUid"]

        # Query virtual data for the dishwasher
        results = list(collection_virtual.find({
            "payload.parent_asset_uid": dishwasher_uid
        }))

        if not results:
            return "No water consumption data found."

        # Calculate average water consumption
        total_water_consumption = sum(
            float(entry["payload"].get("WaterSensor", 0))
            for entry in results
        )
        average_water = total_water_consumption / len(results)
        return f"Average water consumption per cycle: {average_water:.2f} gallons."
    except Exception as e:
        return f"Error calculating water consumption: {e}"


# Example usage
if __name__ == "__main__":
    collections = QueryDatabase()
    if collections:
        print(f"Collections available: {collections}")
    else:
        print("Failed to retrieve collections.")
