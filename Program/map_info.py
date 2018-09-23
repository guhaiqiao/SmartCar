class Graph():
    def __init__(self):
        self.point = []
        self.x = []
        self.y = []
        self.line = []
        self.point_num = 8

    def read(self, file):
        f = open(file, 'r')
        while True:
            info = f.readline()
            if not info:
                break
            info = [int(x) for x in info.split()]
            self.x.append(info[1])
            self.y.append(info[2])
            self.point.append((info[1], info[2]))
            line = [0, 0, 0, 0, 0, 0, 0, 0]
            for i in info[3:]:
                line[i - 1] = 1
            self.line.append(line)
            # print(info)
        # print(self.point)
        # print(self.line)


if __name__ == '__main__':
    map_info = Graph()
    map_info.read(
        'D:\\Computer\\AST\\SmartCar\\Upper Computer\\Program\\map_test.txt')