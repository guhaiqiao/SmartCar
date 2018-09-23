class Traffic():
    def __init__(self):
        self.line = []
        # self.point_num = 8

    def read(self, file):
        self.line = []
        f = open(file, 'r')
        info = f.readlines()
        self.point_num = len(info)
        # print(info)
        for i in range(0, self.point_num):
            line = []
            for k in range(0, self.point_num):
                line.append(0)
            if i != (len(info) - 1):
                info[i] = info[i][:-1]
            info[i] = [int(x) for x in info[i].split()]
            for j in range(1, len(info[i]), 2):
                line[info[i][j] - 1] = info[i][j + 1]
            self.line.append(line)
            # print(info[i])
        # print(self.line)


# if __name__ == '__main__':
#     map_info = Traffic()
#     map_info.read(
#         'D:\\Computer\\AST\\SmartCar\\Upper Computer
#            \\Program\\traffic_test.dat'
#     )
