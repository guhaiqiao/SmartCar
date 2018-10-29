########################
#  此模块包含读取外部数据文件的相关类
########################

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

class Traffic():
    def __init__(self, point_num=0):
        self.line = []
        self.original_data = ''
        self.point_num = point_num
        for i in range(point_num):
            self.line.append([0 for _ in range(point_num)])

    def read(self, file):
        self.line = []
        f = open(file, 'r')
        self.original_data = f.read()
        f.seek(0)
        lines = f.readlines()
        self.point_num = len(lines)
        for i in range(0, self.point_num):
            line = []
            for k in range(0, self.point_num):
                line.append(0)
            if i != (len(lines) - 1):
                lines[i] = lines[i][:-1]
            lines[i] = [int(x) for x in lines[i].split()]
            for j in range(1, len(lines[i]), 2):
                line[lines[i][j] - 1] = lines[i][j + 1]
            self.line.append(line)

class Team():
    def __init__(self):
        self.team_names = []

    def read(self, file):
        f = open(file)
        for name in f:
            self.team_names.append(name.strip('\n'))
        f.close()