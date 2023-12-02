import serial
import json
import time
import datetime
from collections import deque

class LimitedQueue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.queue = deque()

    def enqueue(self, value):
        if len(self.queue) >= self.max_size:
            self.queue.popleft()  # Remove the oldest value
        self.queue.append(value)

    def read(self, n):
        if n < 1 or n > len(self.queue):
            return None
        return self.queue[-n]

def count_measurements(duration, port, baudrate):
    start_time = time.time()
    end_time = start_time + duration
    s1_queue = LimitedQueue(5)  # create queues
    s2_queue = LimitedQueue(5)

    total_measurements = 0
    s1_errors = 0
    s2_errors = 0
    s2_disabled = False
    s1 = 0
    s2 = 0

    with serial.Serial(port, baudrate) as ser:

        print(f"Testing rate of reads from serial port: {port}, Baud: {baudrate}")
        ser.flushInput()

        #flush first XX measurements
        i = 0
        while i < 10:
            line = ser.readline().decode().strip()
            i+= 1

        while time.time() < end_time:
            line = ser.readline().decode().strip()
            total_measurements += 1

            try:
                data = json.loads(line)
            except:
                print(f"CRITICAL JSON Error Unable to load: {line}")

            s1 = data['s1']
            s2 = data['s2']
            s1_queue.enqueue(s1)
            s2_queue.enqueue(s2)

            # check for errors
            error = -101
            s2_count_delay = 10

            if s1 == error:
                s1_errors += 1
                print(f"   #{total_measurements}  s1: {s1}   2: {s1_queue.read(2)} 3: {s1_queue.read(3)} 4: {s1_queue.read(4)}")
            if s2 == error and s2_disabled == False:
                s2_errors += 1
                # this code ignores the second port and assumes it is disconnected if all errors after a certain value
                if total_measurements == s2_errors and total_measurements > 10:
                    s2_disabled = True
                else:
                    print(f"   #{total_measurements}  s2: {s2}  2: {s2_queue.read(2)} 3: {s2_queue.read(3)} 4: {s2_queue.read(4)}, s2_errors :{s2_errors}")

            if s1 == error and s2 == error and s2_disabled == False:
                print(f"  DOUBLE Error - count# {total_measurements}")

            if total_measurements % 2000 == 0:  # Print every 10th measurement

                # Extract the seconds and milliseconds from the timestamp
                current_time = datetime.datetime.now()
                seconds = current_time.second
                milliseconds = current_time.microsecond // 1000  # Convert microseconds to milliseconds

                print(f"{total_measurements} -  {seconds}:{milliseconds},  s1_errors {s1_errors} s2_errors: {s2_errors}   -  {line} \n")

    elapsed_time = time.time() - start_time
    measurements_per_second = total_measurements / elapsed_time

    print("\n--- Summary ---")
    print(f"Total measurements: {total_measurements}")
    print(f"Set Duration: {duration} seconds")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Measurements per second: {measurements_per_second:.2f}")
    print(f"Total Errors:   s1_errors {s1_errors} s2_errors: {s2_errors}")
    print(f"percent errors: s1: {s1_errors/total_measurements * 100}%  s2: {s2_errors/total_measurements * 100}%")

#get list of port and display
import serial.tools.list_ports

# Get a list of available serial ports
available_ports = list(serial.tools.list_ports.comports())

if not available_ports:
    print("No serial ports found!")
else:
    # Print the list of available serial ports
    for port in available_ports:
        print(f"Comport available: {port.device}")

# Example usage
count_measurements(duration=100, port='COM4', baudrate=115200)

