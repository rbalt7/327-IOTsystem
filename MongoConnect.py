from pymongo import MongoClient, database
import subprocess
import threading
import pymongo
from datetime import datetime, timedelta
import time

DBName = "test" #Use this to change which Database we're accessing
connectionURL = "insert DB URL here"
#Put your database URL here
sensorTable = "traffic data" #Change this to the name of your sensor data table

def QueryToList(query):
  #TODO: Convert the query that you get in this function to a list and return it
  list = []
  #n =0;
  for doc in query:
    #print("in loop"+n)
    #n+= 1
    list.append(doc)
  #HINT: MongoDB queries are iterable
  return list

def QueryDatabase() -> []:
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
		cluster = connectionURL
		client = MongoClient(cluster)
		db = client[DBName]
		print("Database collections: ", db.list_collection_names())

		#We first ask the user which collection they'd like to draw from.
		sensorTable = db[sensorTable]
		print("Table:", sensorTable)
		#We convert the cursor that mongo gives us to a list for easier iteration.
		timeCutOff =  datetime.now() - timedelta(minutes=25)
		#TODO: Set how many minutes you allow

		oldDocuments = QueryToList(sensorTable.find({"time":{"$gte":timeCutOff}}))
		currentDocuments = QueryToList(sensorTable.find({"time":{"$lte":timeCutOff}}))

		print("Current Docs:",oldDocuments)
		print("Old Docs:",currentDocuments)

		#TODO: Parse the documents that you get back for the sensor data that you need
		return currentDocuments[0]['topic'][8:19]
		#Return that sensor data as a list
		
	
	      


	except Exception as e:
		print("Please make sure that this machine's IP has access to MongoDB.")
		print("Error:",e)
		exit(0)
