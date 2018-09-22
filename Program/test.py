import serial
import serial.tools.list_ports
list = serial.tools.list_ports.comports()
print(str(list[0]))
# print(list[0] == 'COM4 - Silicon Labs CP210x USB to UART Bridge (COM4)')