# coding=utf-8
# import os
import threading
from time import ctime, sleep
import serial

# -------------------------------------------------------------------------------------------------
# message组成： id + command（请求路况信息、收到、发送位置信息、强制减速、路况信息编号）+内容（位置、路况）
#   id : 0 ~ 9
#   command:
#       r(request)  : 请求路况信息
#       a(accept)   : 收到
#       p(position) : 发送位置信息
#       s(slowdown) : 是否强制减速
#       t(transfer) : 传输路况信息
# -------------------------------------------------------------------------------------------------

message = '0r'
check = chr(ord(message[0]) ^ ord(message[1]))
message += check


def send(port, message, time=3):
    if not event.isSet():
        event.set()
    # while True:
    count = 0
    while count <= 5:
        event.clear()
        # for i in range(1, 11):
        port.write(message.encode('utf-8'))
        print("send %s %s" % (message, ctime()))
        event.set()
        count += 1
        sleep(time)


def receive(port, alldata):
    rdata = ''
    while True:
        if event.isSet():
            byte = port.read(1)
            byte = byte.decode('utf-8')
            if byte != '':
                rdata += byte
                alldata += byte
                print("receiving...one byte %s %s" % (byte, ctime()))
            else:
                print("receiving...nothing %s" % ctime())
            if len(rdata) >= 10:
                print("receive %s %s" % (rdata, ctime()))
                rdata = ''
        else:
            event.wait()


# 设置端口
upper = serial.Serial()
upper.port = 'COM7'
upper.baudrate = 9600
upper.timeout = 1

if __name__ == '__main__':
    alldata = ''   # 接收数据日志
    upper.open()
    event = threading.Event()
    send_thread = threading.Thread(target=send, args=(upper, message))
    receive_thread = threading.Thread(target=receive, args=(upper, alldata))
    # 启动发送线程
    send_thread.start()
    receive_thread.setDaemon(True)
    # 启动接收线程
    receive_thread.start()

    # send_thread.join()
    # receive_thread.join()
    # sleep(20)
    # print("total receive: %s" % alldata)
    # # print(alldata)
    # upper.close()
    # os.system('pause')
