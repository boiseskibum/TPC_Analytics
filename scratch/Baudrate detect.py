# sample Python script to get USB ports

import serial
import time


import serial.tools.list_ports

#### Get a list of available serial ports
available_ports = list(serial.tools.list_ports.comports())

if not available_ports:
    print("No serial ports found!")
else:
    # Print the list of available serial ports
    for port in available_ports:
        print(port.device)

        try:
            # Open the serial port
            ser = serial.Serial(port.device, baudrate=0, timeout=1)

            # Wait for a short time to allow the device to send data
            ser.timeout = 0.5
            ser.read(1)

            # Get the detected baud rate of the serial port
            detected_baud_rate = ser.baudrate

            # Print the detected serial port and baud rate
            print(f"Detected serial port: {port.device}, Baud rate: {detected_baud_rate}")

            # Close the serial port
            ser.close()
        except (OSError, serial.SerialException):
            print(f'failed autobaud detection for port: {port}')






