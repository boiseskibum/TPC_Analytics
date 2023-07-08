import serial
import datetime
import json

def read_line_and_write_to_file():
    # Set the serial port name and baud rate
    port = 'COM4'  # Replace with the name of your serial port
    #baud_rate = 57600  # Replace with the baud rate of your serial port
    baud_rate = 115200  # Replace with the baud rate of your serial port

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"test_output_{timestamp}.txt"
    max_lines = 670  # about 10 seconds

    f = open(filename, 'w')

    # Open the serial port
    ser = serial.Serial(port, baud_rate)

    # Wait for the serial port to initialize
    ser.reset_input_buffer()
    ser.flushInput()

    error_cnt = 0
    error = -101
    i=0
    # Loop to read values from the serial port and save them to file
    while True:
        # Read a line of data from the serial port
        line = ser.readline().decode().rstrip()

        # If the line is not empty, display it in the console
        if line:
            if i < max_lines:
                if i % 100 == 0:
                    print(f"line: {i}: {line}")
                i += 1
                f.write(line + "\n")

                # count errors
                data = json.loads(line)
                s1 = data['s1']
                s2 = data['s2']

                if s1 == error or s2 == error:
                    error_cnt += 1

            else:
                f.close()
                print (f"closing file and exiting,  total rows: {i}  error rows: {error_cnt}")
                return (1)


read_line_and_write_to_file()
