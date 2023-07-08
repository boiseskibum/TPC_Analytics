import serial.tools.list_ports

# Get a list of available serial ports
available_ports = list(serial.tools.list_ports.comports())

if not available_ports:
    print("No serial ports found!")
else:
    # Print the list of available serial ports
    for port in available_ports:
        print(port.device)
