'''
A module implementing Smartcar Protocol v2.0
Module version: 2.2

Usage:
    Use Smartcar class for everything.

I may add exception handling and verification in the next version.
'''

import serial
import threading

# 全局变量
recvbuf = []  # 输入缓冲区，包含bytes类型
sendbuf = []  # 输出缓冲区，包含bytes类型
seq = 0  # 对方发来的seq，我方的ack，即对方下次将要发送的包的seq
ack = 0  # 我方接收的ack，对方的seq，即我方下次将要发送的包的seq
PCID = 0  # 上位机的ID
sending_flag = False  # 发送中标志


def setID(ID):
    # 设置上位机ID
    global PCID
    PCID = ID


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
                elif int.from_bytes(
                        head[2:4], byteorder="little") != seq:  # seq不符合则发送ACK
                    if head[7] == 3:  # 判断是否为SYN包
                        seq = int.from_bytes(head[2:4], byteorder="little") + 1
                        ack = int.from_bytes(head[4:6], byteorder="little")
                        self.car.write(
                            bytes([
                                PCID, self.srcID, ack % 256, ack // 256,
                                seq % 256, seq // 256, 0, 0, 0, 0
                            ]))  # 发ACK包
                    else:
                        self.car.timeout = 0.5
                        self.car.read(head[8])
                        self.car.write(
                            bytes([
                                PCID, self.srcID, ack % 256, ack // 256,
                                seq % 256, seq // 256, 0, 0, 0, 0
                            ]))  # 发ACK包
                elif head[8] != 0 and int.from_bytes(
                        head[4:6],
                        byteorder="little") != ack + 1:  # 新包情形或同时发包情形
                    data = self.car.read(head[8])  # 校验-存储-ACK
                    if head[9] != verify(data):
                        continue
                    recvbuf.append(data)
                    seq += 1
                    self.car.write(
                        bytes([
                            PCID, self.srcID, ack % 256, ack // 256, seq % 256,
                            seq // 256, 0, 0, 0, 0
                        ]))  # 发ACK包
                elif head[8] != 0 and int.from_bytes(
                        head[4:6], byteorder="little") == ack + 1:  # ACK包丢失情形
                    data = self.car.read(head[8])  # 校验-存储-ACK
                    if head[9] != verify(data):
                        continue
                    recvbuf.append(data)
                    seq += 1
                    self.car.write(
                        bytes([
                            PCID, self.srcID, ack % 256, ack // 256, seq % 256,
                            seq // 256, 0, 0, 0, 0
                        ]))  # 发ACK包
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


def send_once(car, dstID, lock, flags):
    global recvbuf, sendbuf, seq, ack, PCID, sending_flag, timer
    with lock:
        car.write(
            bytes([
                PCID, dstID, ack % 256, ack // 256, seq % 256, seq //
                256, 0, flags,
                len(sendbuf[0]), 0
            ]) + sendbuf[0])
        sending_flag = True
        timer = threading.Timer(0.5, send_once, (car, dstID, lock, flags))
        timer.start()


def verify(data):
    return 0


class Smartcar():
    # 小车类，属性有：serial对象car、整型小车ID ID

    def __init__(self, port, baudrate, dstID):
        self.car = serial.Serial(port, baudrate)
        self.dstID = dstID
        self.lock = threading.Lock()
        self.recv = Receiver(self.car, self.dstID, self.lock)
        self.recv.start()

    def close(self):
        global recvbuf, sendbuf, seq, ack, PCID, sending_flag, timer
        seq = 0
        ack = 0
        self.car.close()

    def send(self, data):
        # 发送一串bytes
        global recvbuf, sendbuf, seq, ack, PCID, sending_flag, timer
        if seq > 65500 or ack > 65500:
            seq = 0
            ack = 0
            sendbuf.append(bytes())
            send_once(self.car, self.dstID, self.lock, 3)
            while sending_flag:
                pass
        sendbuf.append(data)
        send_once(self.car, self.dstID, self.lock, 1)
        while sending_flag:
            pass

    def read(self):
        # 读取下一个数据包中的data(bytes)
        return recvbuf.pop(0)

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

    car = Smartcar('COM1', 9600, 0)
