# Import necessary modules
from opcua import Server
import datetime
import socket  # as a gate for external connection
import os  # for pinging
import struct  # to parse data from Cleco if needed

# Initialize the server
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")  # Set endpoint URL
server.set_server_name("FreeOpcUa Example Server")  # Set server information

# Create a namespace for your variables
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)

# Create sample object
# Create an object (e.g., Device or Machine)
objects = server.get_objects_node()
my_device = objects.add_object(idx, "MyDevice")
# Add a variable to this object (e.g., temperature)
temperature_var = my_device.add_variable(idx, "Temperature", 20.0)
temperature_var.set_writable()  # Allow client to modify this variable (variable writable or read-only.)

### CLECO ###
# Create an object for the Cleco Controller
cleco_controller = objects.add_object(idx, "ClecoController")
# Add variables to the Cleco object (e.g., torque, angle)
torque_var = cleco_controller.add_variable(idx, "Torque", 0.0)
angle_var = cleco_controller.add_variable(idx, "Angle", 0.0)

# Add a variable to track the Cleco connection status
connection_status_var = cleco_controller.add_variable(idx, "ConnectionStatus", False)
########

# Start the server
server.start()
print("OPC UA Server is running. Press Ctrl+C to stop.")

# Socket setup to communicate with Cleco Controller
controller_ip = "192.168.100.200"
controller_port = 9002  # Open Protocol communication port
buffer_size = 1024

try:
    while True:
        # Check if the controller is reachable using ping
        response = os.system(f"ping -c 1 {controller_ip}" if os.name != "nt" else f"ping -n 1 {controller_ip}")
        if response == 0:
            connection_status_var.set_value(True)
            print(f"Cleco Controller at {controller_ip} is reachable.")
        else:
            connection_status_var.set_value(False)
            print(f"Cleco Controller at {controller_ip} is NOT reachable.")
            continue  # Skip the rest if Cleco is not reachable

        # Create socket connection
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((controller_ip, controller_port))
                print(f"Connected to Cleco Controller at {controller_ip}:{controller_port}")

                # Send a command or request for data (specific to your Cleco Controller)
                request_message = b'GET_DATA'  # Placeholder message to request data
                s.sendall(request_message)

                # Receive data from the Cleco Controller
                data = s.recv(buffer_size)
                if data:
                    # Assuming data received is structured with torque and angle values
                    # For example, assume data comes in the form: "TORQUE:1.23;ANGLE:45.6"
                    decoded_data = data.decode().strip()
                    print(f"Received data from Cleco Controller: {decoded_data}")

                    # Parse the data received
                    try:
                        # Extracting torque and angle from the response string
                        parts = decoded_data.split(';')
                        torque_str = [x for x in parts if "TORQUE" in x][0]
                        angle_str = [x for x in parts if "ANGLE" in x][0]

                        # Extract values from the strings
                        torque_value = float(torque_str.split(':')[1])
                        angle_value = float(angle_str.split(':')[1])

                        # Update OPC UA variables
                        torque_var.set_value(torque_value)
                        angle_var.set_value(angle_value)

                        print(f"Updated OPC UA Server - Torque: {torque_value}, Angle: {angle_value}")

                    except (IndexError, ValueError) as e:
                        print(f"Error parsing data: {e}")

        except socket.error as e:
            print(f"Socket error: {e}")

except KeyboardInterrupt:
    print("Shutting down the server and socket connection.")
    server.stop()

finally:
    server.stop()
