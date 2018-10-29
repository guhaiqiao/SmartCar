
import os
import math
from xml.dom.minidom import parse

os.chdir('E:\\程序文件\\OneDrive\\Documents\\大学\\社会活动\\社工\\工物科协\\2018-2019秋智能车大赛\\上位机\\交通仿真\\SUMO\\Smartcar')
edgedatafile = 'output-edgedata.xml'
totaltrafficfile = 'total.txt'

if not os.path.exists('./1'):
    os.mkdir('./1')

DOMTree = parse(edgedatafile)
collection = DOMTree.documentElement
intervals = collection.getElementsByTagName('interval')
idx = 0
for interval in intervals:
    idx += 1
    f = open('./1/' + str(idx) + '.txt', 'w')
    edges = interval.getElementsByTagName('edge')
    current = '-1'
    for edge in edges:
        id = edge.getAttribute('id')[4:].split('-')
        if current == '-1':   #文件开头的情况
            current = id[0]
            f.write(id[0])
        elif id[0] != current:
            current = id[0]
            f.write('\n' + id[0])
        f.write(' ' + id[1] + ' ' + ('0' if edge.getAttribute('occupancy') == '' else str(math.floor(float(edge.getAttribute('occupancy')) % 10))))
    f.close()

#Total
f = open('./1/' + totaltrafficfile, 'w')
for interval in intervals:
    f.write(interval.getAttribute('begin') + ' ' + interval.getAttribute('end') + '\n')
    edges = interval.getElementsByTagName('edge')
    current = '-1'
    for edge in edges:
        id = edge.getAttribute('id')[4:].split('-')
        if id[0] != current:
            current = id[0]
            f.write('\n' + id[0])
        f.write(' ' + id[1] + ' ' + ('0' if edge.getAttribute('occupancy') == '' else edge.getAttribute('occupancy')))
    f.write('\n\n')
f.close()

#按edge分的路况
os.mkdir('./1/edges')
for interval in intervals:
    edges = interval.getElementsByTagName('edge')
    for edge in edges:
        f = open('./1/edges/' + edge.getAttribute('id')[4:] + '.txt', 'a')
        f.write(interval.getAttribute('begin') + '-' + interval.getAttribute('end') + ' ' + ('0' if edge.getAttribute('occupancy') == '' else edge.getAttribute('occupancy')) + '\n')
        f.close()