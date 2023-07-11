
import serial
import datetime
from time import sleep

def read_line_to_screen():
    # Set the serial port name and baud rate
    port = 'COM4'  # Replace with the name of your serial port
    baud_rate = 115200  # Replace with the baud rate of your serial port

    # Open the serial port
    ser = serial.Serial(port, baud_rate)

    # Wait for the serial port to initialize
    ser.reset_input_buffer()
    ser.readline()

    i=0
    # Loop to read values from the serial port and display them
    while True:

        if ser.in_waiting > 0:
            # Read a line of data from the serial port
            line = ser.readline().decode().rstrip()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # If the line is not empty, display it in the console

            print(f"line# {i}: {line}  timestamp:{timestamp}")
            i += 1


    # Close the serial port when done
    ser.close()

read_line_to_screen()

