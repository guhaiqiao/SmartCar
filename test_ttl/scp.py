import serial
import threading

#全局变量，输入缓冲区、输出缓冲区以及序列号seq
inbuf = []
outbuf = []
seq = 0

class Package():
    def __init__(self, ID, flag, data):
        self.ID = ID
        self.flag = flag
        self.data = data   #应为bytes类型
        self.len = len(data)
        self.check = 0
        
class Listener(threading.Thread):
    #监听器，负责一直收发数据，属性有：car、ID
    
    def __init__(self, car, ID):
        threading.Thread.__init__(self)
        self.car = car
        self.ID = ID

    def sendpackage(self):
        #发送缓冲区中第一个包，若无，则发送一个空包。反复发送直到接收到ACK。若ACK无数据，返回True，若ACK有数据，则把包放入缓冲区，且若此时输出缓冲区非空，则返回True，否则返回False。

        global seq, inbuf, outbuf
        seq += 1
        while True:
            if len(inbuf) > 0:
                package = outbuf.pop(0)
                self.car.write(bytes([package.ID, seq, 0, len(package.data), package.check]))   #首部
                self.car.write(package.data)   #数据
            else:
                self.car.write(bytes([self.ID, seq, 0, 0, 0]))
            self.car.timeout = 0.5
            buf = self.car.read(5)
            if len(buf) < 5:
                continue
            elif buf[0:3] != bytes([package.ID, seq + 1, 1]):
                continue

            if buf[3] == bytes([0]):
                seq += 1
                return True
            else:
                car.timeout = None
                inbuf.append(Package(int.from_bytes(buf[0], byteorder = 'big'), int.from_bytes(buf[2], byteorder = 'big'), self.car.read(int.from_bytes(buf[3], byteorder = 'big'))))
                seq += 1
                if len(outbuf) > 0:
                    return True
                else:
                    return False

    def recvpackage(self):
        #反复回复ACK直到接收到下一个包，反复接收此包直到接收成功，然后把包放入缓冲区，若此时输出缓冲区有数据，则返回False，否则返回True

        global seq, inbuf, outbuf
        seq += 1
        while True:
            self.car.write(bytes([self.ID, seq, 1, 0, 0]))
            self.car.timeout = 0.5
            buf = self.car.read(5)
            if len(buf) < 5:
                continue
            elif buf[0:3] != bytes([self.ID, seq + 1, 0]):
                continue
            self.car.timeout = None
            inbuf.append(Package(int.from_bytes(buf[0], byteorder = 'big'), int.from_bytes(buf[2], byteorder = 'big'), self.car.read(int.from_bytes(buf[3], byteorder = 'big'))))
            seq += 1
            if len(outbuf) > 0:
                return False
            else:
                return True

    def run(self):
        while True:
            while (self.sendpackage()):
                pass
            while (self.recvpackage()):
                pass

class Smartcar():
    #小车类，属性有：serial对象car、整型小车ID ID
    
    def __init__(self, port, baudrate, ID):
        self.car = serial.Serial(port, baudrate)
        self.ID = ID
        lis = Listener(self.car, self.ID)
        lis.start()
        
    def send(self, package):
        #发送一个数据包
        outbuf.append(package)

    def read(self):
        #读取一个数据包
        return inbuf.pop(0)

    def readable(self):
        #检测当前缓冲区是否有数据包可读
        if len(inbuf) > 0:
            return True
        else:
            return False

    def inbufcount(self):
        #输入缓冲区数据包个数
        return len(inbuf)

    def outbufcount(self):
        #输出缓冲区数据包个数
        return len(outbuf)
