class Traffic():
    def __init__(self):
        # self.point = []
        # self.x = []
        # self.y = []
        self.line = []
        self.point_num = 8

    def read(self, file):
        f = open(file, 'r')
        while True:
            info = f.readline()
            line = [0, 0, 0, 0, 0, 0, 0, 0]
            if not info:
                break
            info = [int(x) for x in info.split()]
            for i in range(1, len(info), 2):
                line[info[i] - 1] = info[i + 1]
            self.line.append(line)
            # print(info)
        # print(self.line)


if __name__ == '__main__':
    map_info = Traffic()
    map_info.read(
        'D:\\Computer\\AST\\SmartCar\\Upper Computer\\Program\\traffic_test.dat')