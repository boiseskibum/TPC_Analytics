import serial.tools.list_ports
import json

def check_serial_ports():
    ports = serial.tools.list_ports.comports()
    active_ports = []


    for port in ports:
        print(f"port: {port.device}")
        try:
            ser = serial.Serial(port.device, baudrate=115200)

            line = ser.readline().decode().strip()
            if 's1' in line:
                active_ports.append(port.device)
                print(f"--- line: {line}")
            ser.close()
        except serial.SerialException:
            pass

    return active_ports

# Example usage
active_ports = check_serial_ports()
print(f"active ports: {active_ports}" )

