# Import necessary modules
from opcua import Server
import datetime

# Initialize the server
server = Server()

# Set endpoint URL
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

# Set server information
server.set_server_name("FreeOpcUa Example Server")

# Create a namespace for your variables
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)

# Create an object (e.g., Device or Machine)
objects = server.get_objects_node()
my_device = objects.add_object(idx, "MyDevice")

# Add a variable to this object (e.g., temperature)
temperature_var = my_device.add_variable(idx, "Temperature", 20.0)
temperature_var.set_writable()  # Allow client to modify this variable

# Start the server
server.start()
print("OPC UA Server is running. Press Ctrl+C to stop.")

try:
    while True:
        # Update the temperature value (e.g., simulate temperature changes)
        new_temperature = 20.0 + 5.0 * (datetime.datetime.now().second % 10)
        temperature_var.set_value(new_temperature)

except KeyboardInterrupt:
    print("Shutting down the server.")
    server.stop()
