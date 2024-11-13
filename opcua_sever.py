# Import necessary modules
from opcua import Server
import datetime
import socket  # as a gate for external connection
import os     # for pinging

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
torque_var.set_writable()  # Allow client to modify this variable if needed

angle_var = cleco_controller.add_variable(idx, "Angle", 0.0)
angle_var.set_writable()  # Allow client to modify this variable if needed

# Add a variable to track the Cleco connection status
connection_status_var = cleco_controller.add_variable(idx, "ConnectionStatus", False)
connection_status_var.set_writable()  # Allow client to modify this variable if needed
########

# Start the server
server.start()
print("OPC UA Server is running. Press Ctrl+C to stop.")

# Socket setup to communicate with Cleco Controller
controller_ip = "192.168.50.150"
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

        # Create socket connection
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((controller_ip, controller_port))
                print(f"Connected to Cleco Controller at {controller_ip}:{controller_port}")

                # Just to test the connection
                test_message = b'TEST_CONNECTION'  # Placeholder message to check connection
                s.sendall(test_message)
                response = s.recv(buffer_size)
                if response:
                    print(f"Received response from Cleco Controller: {response.decode().strip()}")
        except socket.error as e:
            print(f"Socket error: {e}")

except KeyboardInterrupt:
    print("Shutting down the server and socket connection.")
    server.stop()

finally:
    server.stop()
