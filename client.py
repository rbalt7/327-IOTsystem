import socket

def start_client():
    while True:
        try:
            # User input ip and port
            server_port = int(input("Server Port Number:"))
            server_ip = input("Server IP Address: ")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to server
            client_socket.connect((server_ip, server_port))
            print(f"Connected to the server {server_ip}:{server_port}")

            while True:
                # User input message
                #message = input("Enter message for server or 'exit' to exit':")
                message = input("Enter command:"
                                "\n1 for Average Moisture"
                                "\n2 for Dishwasher Water cycle consumption"
                                "\n3 for Device that consumes the most electricity"
                                "\n4 to Quit\n")
                if message.lower() == '4':
                    print("Closing connection")
                    break

                # Send
                client_socket.send(message.encode('utf-8'))

                # Receive Response
                response = client_socket.recv(1024).decode('utf-8')
                print(f"Server response: {response}")

            client_socket.close()
            break
        except (ValueError, socket.error) as error:
            print(f"Error : {error}")
            continue



start_client()
