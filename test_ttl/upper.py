# coding=utf-8
import os
import threading
from time import ctime, sleep
import serial

# ----------------------------------------------------------------------------------------------
# message组成： id + command（请求路况信息、收到、发送位置信息、强制减速、路况信息编号）+内容（位置、路况）
#   id : 0 ~ 9
#   command:
#       r(request)  : 请求路况信息
#       a(accept)   : 收到
#       p(position) : 发送位置信息
#       s(slowdown) : 是否强制减速
#       t(transfer) : 传输路况信息
# ----------------------------------------------------------------------------------------------
message = ['1']
def send(port, message, time=3):
    if not event.isSet():
        event.set()
    # while True:
    count = 0
    while count <= 5:
        event.clear()
        # for i in range(1, 11):
        port.write(id.encode('utf-8'))
        print("send %s %s" % (id, ctime()))
        event.set()
        count += 1
        sleep(time)


def receive(port, alldata):
    rdata = ''
    while True:
        if event.isSet():
            byte = port.read(1)
            byte = str(byte)[2:-1]
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
upper.port = 'COM4'
upper.baudrate = 9600
upper.timeout = 1
upper.open()

if __name__ == '__main__':
    alldata = ''   # 接收数据日志
    event = threading.Event()
    send_thread = threading.Thread(target=send, args=(upper, 'ghq'))
    # 启动发送线程
    send_thread.start()
    receive_thread = threading.Thread(target=receive, args=(upper, alldata))
    receive_thread.setDaemon(True)
    # 启动接收线程
    receive_thread.start()
    sleep(20)
    print("total receive: %s" % alldata)
    print(alldata)
    upper.close()
    os.system('pause')
