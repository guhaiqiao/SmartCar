'''
A module implementing Smartcar Protocol v2.0
Module version: 2.0

Usage:
    Use Smartcar class to everything.
'''

import serial
import threading


# 全局变量
inbuf = []  # 输入缓冲区，包含Package对象
outbuf = []  # 输出缓冲区，包含Package对象
seq = 0  # 对方发来的seq，我方的ack，即对方下次将要发送的包的seq
ack = 0  # 我方接收的ack，对方的seq，即我方下次将要发送的包的seq
PCID = 0  # 上位机的ID

# my_global = Global()

class Package():
    #数据包类，用于封装一个数据包

    def __init__(self, srcID, dstID, flag, data):
        self.srcID = srcID
        self.dstID = dstID
        self.flag = flag
        self.data = data  # 应为bytes类型
        self.len = len(data)
        self.check = 0


class Receiver(threading.Thread):
    # 数据包接收线程

    def __init__(self, car, srcID, lock):
        threading.Thread.__init__(self)
        self.car = car
        self.srcID = srcID
        self.lock = lock

    def run(self):
        global inbuf, outbuf, seq, ack, PCID
        while True:
            self.car.timeout = None
            head = self.car.read(10)
            with self.lock:
                if head[0] != self.srcID or head[1] != PCID:
                    self.car.timeout = 0.5
                    self.car.read(head[8])
                    continue
                elif int.from_bytes(head[2:4], byteorder="little") != seq:
                    self.car.timeout = 0.5
                    self.car.read(head[8])
                    print(
                        bytes([
                            PCID, self.srcID, ack % 256, ack // 256, seq % 256,
                            seq // 256, 0, 0, 0, 0
                        ]))  ###测试
                    self.car.write(
                        bytes([
                            PCID, self.srcID, ack % 256, ack // 256, seq % 256,
                            seq // 256, 0, 0, 0, 0
                        ]))
                    continue
                data = self.car.read(head[8])
                inbuf.append(Package(head[0], head[1], head[7], data))
                seq += 1
                self.car.write(
                    bytes([
                        PCID, self.srcID, ack % 256, ack // 256, seq % 256,
                        seq // 256, 0, 0, 0, 0
                    ]))


class Sender(threading.Thread):
    #数据包发送线程

    def __init__(self, car, dstID, lock, condition):
        threading.Thread.__init__(self)
        self.car = car
        self.dstID = dstID
        self.lock = lock
        self.condition = condition

    def run(self):
        global inbuf, outbuf, seq, ack, PCID
        while True:
            self.condition.acquire()
            self.condition.wait()
            with self.lock:
                p = outbuf.pop(0)
                while True:
                    self.car.write(
                        bytes([
                            PCID, self.dstID, ack % 256, ack // 256, seq %
                            256, seq // 256, 0, 0,
                            len(p.data), 0
                        ]) + p.data)
                    self.car.timeout = 1
                    buf = self.car.read(10)
                    print(seq)  ### 测试
                    print(ack)  ### 测试
                    if len(buf) < 10:
                        print("1")  ### 测试
                        print(len(buf))
                        continue
                    elif buf[0] != self.dstID or buf[1] != PCID:
                        print("2")  ### 测试
                        continue
                    elif buf[4:6] != bytes([(ack + 1) % 256,
                                            (ack + 1) // 256]):
                        print(buf)  ### 测试
                        print(bytes([(ack + 1) % 256,
                                     (ack + 1) // 256]))  # ##测试
                        print("3")  ### 测试
                        continue
                    else:
                        print("4")  # ##测试
                        ack += 1
                        break
            self.condition.release()


class Smartcar():
    # 小车类，属性有：serial对象car、整型小车ID ID

    def __init__(self, port, baudrate, dstID):
        self.car = serial.Serial(port, baudrate)
        self.dstID = dstID
        self.lock = threading.Lock()
        self.condition = threading.Condition()
        recv = Receiver(self.car, self.dstID, self.lock)
        sender = Sender(self.car, self.dstID, self.lock, self.condition)
        recv.start()
        sender.start()

    def send(self, data):
        # 发送一串bytes
        outbuf.append(Package(PCID, self.dstID, 0, data))
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()

    def read(self):
        #读取下一个数据包中的data(bytes)
        return inbuf.pop(0).data

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


if __name__ == "__main__":
    #调试代码

    car1 = Smartcar('COM7', 9600, 0)
    # car1.send("test".encode())
