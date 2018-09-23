class Graph():
    def __init__(self):
        self.x = []
        self.y = []
        self.line = []

    def read(self, file):

        self.line = []
        f = open(file, 'r')
        info = f.readlines()
        self.point_num = len(info)
        for i in range(0, self.point_num):
            line = []
            for k in range(0, self.point_num):
                line.append(0)
            if i != (len(info) - 1):
                info[i] = info[i][:-1]
            info[i] = [int(x) for x in info[i].split()]
            self.x.append(info[i][1])
            self.y.append(info[i][2])
            for j in info[i][3:]:
                line[j - 1] = 1
            self.line.append(line)
        # print(info)
        # print(self.point)
        # print(self.line)


if __name__ == '__main__':
    map_info = Graph()
    map_info.read(
        'D:\\Computer\\AST\\SmartCar\\Upper Computer\\Program\\map_test.txt')