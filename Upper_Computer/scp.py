'''
A module implementing Smartcar Protocol v2.0
Module version: 2.1
Usage:
    Use Smartcar class for everything.
I may cancel Package class and add verification in the next version.
'''

import serial
import threading

# 全局变量
recvbuf = []  # 输入缓冲区，包含Package对象
sendbuf = []  # 输出缓冲区，包含Package对象
seq = 0  # 对方发来的seq，我方的ack，即对方下次将要发送的包的seq
ack = 0  # 我方接收的ack，对方的seq，即我方下次将要发送的包的seq
PCID = 1  # 上位机的ID
sending_flag = False


class Package():
    # 数据包类，用于封装一个数据包

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
        global recvbuf, sendbuf, seq, ack, PCID, sending_flag, timer
        while True:
            self.car.timeout = None
            head = self.car.read(10)
            with self.lock:
                if head[0] != self.srcID or head[1] != PCID:  # 地址不符合则丢弃该包
                    self.car.timeout = 0.5
                    self.car.read(head[8])
                    continue
                elif int.from_bytes(
                        head[2:4], byteorder="little") != seq:  # seq不符合则发送ACK
                    self.car.timeout = 0.5
                    self.car.read(head[8])
                    self.car.write(
                        bytes([
                            PCID, self.srcID, ack % 256, ack // 256, seq % 256,
                            seq // 256, 0, 0, 0, 0
                        ]))  # 发ACK包
                    continue
                elif head[8] != 0:
                    data = self.car.read(head[8])  # 存储该包，有3个步骤
                    recvbuf.append(Package(head[0], head[1], head[7], data))
                    seq += 1
                    if sending_flag:
                        timer.cancel()  # 清除计时，有4个步骤
                        sending_flag = False
                        sendbuf.pop(0)
                        ack += 1
                elif head[8] == 0 and int.from_bytes(
                        head[4:6], byteorder="little") != ack + 1:
                    pass
                elif head[8] == 0 and int.from_bytes(
                        head[4:6],
                        byteorder="little") == ack + 1 and sending_flag:
                    timer.cancel()
                    sending_flag = False
                    sendbuf.pop(0)
                    ack += 1


def send_once(car, dstID, lock):
    global timer, sending_flag
    with lock:
        car.write(
            bytes([
                PCID, dstID, ack % 256, ack // 256, seq % 256, seq //
                256, 0, 0,
                len(sendbuf[0].data), 0
            ]) + sendbuf[0].data)
        sending_flag = True
        timer = threading.Timer(0.5, send_once, (car, dstID, lock))
        timer.start()


class Smartcar():
    # 小车类，属性有：serial对象car、整型小车ID ID

    def __init__(self, port, baudrate, dstID):
        self.car = serial.Serial(port, baudrate)
        self.dstID = dstID
        self.lock = threading.Lock()
        recv = Receiver(self.car, self.dstID, self.lock)
        recv.start()

    def send(self, data):
        # 发送一串bytes
        while len(sendbuf) > 0:
            pass
        sendbuf.append(Package(PCID, self.dstID, 0, data))
        send_once(self.car, self.dstID, self.lock)

    def read(self):
        # 读取下一个数据包中的data(bytes)
        return recvbuf.pop(0).data

    def readable(self):
        # 检测当前缓冲区是否有数据包可读
        if len(recvbuf) > 0:
            return True
        else:
            return False

    def recvbufcount(self):
        # 输入缓冲区数据包个数
        return len(recvbuf)

    def sendbufcount(self):
        # 输出缓冲区数据包个数
        return len(sendbuf)


if __name__ == "__main__":
    # 调试代码

    car = Smartcar('COM4', 9600, 0)
    # while True:
    #    car.send("1111111111111111".encode())
