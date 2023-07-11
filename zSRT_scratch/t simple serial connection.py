import serial.tools.list_ports


ser = serial.Serial('COM3', baudrate=115200)

line = ser.readline().decode().strip()
print(f"--- line: {line}")


