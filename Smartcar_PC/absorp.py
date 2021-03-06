########################
#  道路吸附算法
########################
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def cal_dis(self, point):  # 两点间距离
        dx = self.x - point.x
        dy = self.y - point.y
        return math.sqrt(dx**2 + dy**2)


class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.x = end.x - start.x
        self.y = end.y - start.y
        self.length = start.cal_dis(end)

    def cal_dot(self, line):  # 计算点乘，默认有公共顶点start
        return self.x * line.x + self.y * line.y

    def cal_distance(self, point):  # 计算点到线段距离
        l_s = Line(self.start, point)
        flag = self.cal_dot(l_s) / (self.length**2)
        if l_s.length == 0:
            return 0
        if flag > 1:
            return self.end.cal_dis(point)
        elif flag < 0:
            return self.start.cal_dis(point)
        else:
            cos = self.cal_dot(l_s) / self.length / l_s.length
            sin = math.sqrt(1 - cos**2)
            return l_s.length * sin

    def projection(self, point):  # 返回点在线段上的投影坐标
        l_s = Line(self.start, point)
        flag = self.cal_dot(l_s) / (self.length**2)
        if flag > 1:
            return self.end.x, self.end.y
        elif flag < 0:
            return self.start.x, self.start.y
        else:
            x_pro = (int)(self.start.x + self.x * flag)
            y_pro = (int)(self.start.y + self.y * flag)
        return x_pro, y_pro


def absorp(x: int, y: int, map) -> (int, int, int):
    '''

    :param x: car's actual x position
    :param y: car's actual y position
    :param map: map data
    :return: tuple, (start_num, end_num, distance from the start of the road)
    '''
    car = Point(x, y)
    lines = []
    dis = []
    for i in range(map.point_num):
        for j in range(i, map.point_num):
            if map.line[i][j] == 1:
                start = Point(map.x[i], 6000 - map.y[i])
                end = Point(map.x[j], 6000 - map.y[j])
                lines.append(Line(start, end))
    for line in lines:
        dis.append((int)(line.cal_distance(car)))
    nearest = lines[dis.index(min(dis))]
    car.x, car.y = nearest.projection(car)

    # Get the index of the start and the end of the road
    for i in range(map.point_num):
        if map.x[i] == nearest.start.x and 6000 - map.y[i] == nearest.start.y:
            start_num = i + 1
            break
    for i in range(map.point_num):
        if map.x[i] == nearest.end.x and 6000 - map.y[i] == nearest.end.y:
            end_num = i + 1
            break
    if start_num > end_num:
        t = start_num
        start_num = end_num
        end_num = t

    # Calculate the distance from the start of the road
    start_point = Point(map.x[start_num - 1], map.y[start_num - 1])
    s = int(car.cal_dis(start_point))

    return start_num, end_num, s
    # return nearest.start, nearest.end