
import os

os.chdir('E:/程序文件/OneDrive/Documents/大学/社会活动/社工/工物科协/2018-2019秋智能车大赛/上位机/交通仿真/SUMO/Smartcar')
mapdatafile = 'map.txt'
nodedatafile = 'map_NODE.nod.xml'
edgedatafile = 'map_EDGE.edg.xml'
netdatafile = 'map.net.xml'

map = []
f = open(mapdatafile)
for line in f:
    params = line.split(' ')
    map.append(params)
f.close()

f = open(nodedatafile, 'w')
f.write('<nodes>\n')
for node in map:
    f.write('<node id="' + node[0] + '" x="' + node[1] + '" y="' + node[2])
    if len(node) >= 7:
        f.write('" type="traffic_light" />\n')
    else:
        f.write('" />\n')
f.write('</nodes>')
f.close()

f = open(edgedatafile, 'w')
f.write('<edges>\n')
for node in map:
    for dst in node[3:]:
        dst = dst.strip('\n')
        f.write('<edge id="edge' + node[0] + '-' + dst + '" from="' + node[0] + '" to="' + dst + '" priority="75" numLanes="3" speed="70" />\n')
f.write('</edges>')
f.close()

print(os.system('netconvert --node-files=' + nodedatafile + ' --edge-files=' + edgedatafile + ' --output-file=' + netdatafile))