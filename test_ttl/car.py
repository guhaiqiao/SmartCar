import serial
# import os
car = serial.Serial('COM4', 9600, timeout=5)
while(1):
    print(car.read(1))
