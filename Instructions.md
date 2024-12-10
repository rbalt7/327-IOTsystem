Overview

This project implements a comprehensive end-to-end IoT system that integrates:

A TCP client-server for user query processing and response.
A MongoDB database for IoT device data and metadata storage.
Virtual IoT sensor data sourced from Dataniz for real-time processing and analysis.
The system supports three key user queries:

What is the average moisture inside my kitchen fridge in the past three hours?
What is the average water consumption per cycle in my smart dishwasher?
Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?
The project highlights the integration of IoT sensors, metadata utilization, real-world unit conversions, and robust query handling.

System Architecture

The system consists of the following components:

TCP Client:

Accepts user queries via a command-line interface.
Sends valid queries to the TCP server for processing.
Receives and displays responses from the server.
TCP Server:

Processes incoming queries by fetching relevant data from the MongoDB database.
Utilizes metadata from Dataniz to enhance query processing and data organization.
Performs unit conversions (e.g., moisture to RH%, water to gallons, electricity to kWh) and calculations.
Returns results to the client.
Database (MongoDB):

Stores IoT device metadata (e.g., device IDs, attributes, and configurations).
Stores real-time and historical IoT sensor data.
IoT Devices (Virtual):

Includes two smart refrigerators and a smart dishwasher.
Generates data for moisture levels, water consumption, and electricity usage.

process to run:
1 - start the server file by "python <filename>" and then it will prompt you to enter the ipv4 address and port number of the vm
2 - once the server is started then you can start the client by "python <filename>" that will ask for the same IP address and port number. which will then prompt the three different queries that we are asking to our mongoDB to provide.
3 - after all four queries have successfully ran, we can press "4" to quitt the program or "crtl c" to kill the terminal. 

