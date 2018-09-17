import threading
import serial


class Send_thread(threading.Thread):
    def __init__(self, func, args):
        super().__init__(self)
        self.func = func
        self.args = args















class Receive_thread(threading.Thread):
    def __init__(self, func, args):
        super().__init__(self)
        self.func = func
        self.args = args
