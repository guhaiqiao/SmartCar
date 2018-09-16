import serial
# import sys
# import os?

ser = serial.Serial('COM4', 9600, timeout=10)

for i in range(1, 10):
    print(ser.write(b'id'))
# print(ser.name)

# print(ser.read(100))
# print(ser.read(10))
# os.system('pause')
