
import os
from random import choice
from random import randint

os.chdir('E:\\程序文件\\OneDrive\\Documents\\大学\\社会活动\\社工\\工物科协\\2018-2019秋智能车大赛\\上位机\\交通仿真\\SUMO\\Smartcar')
netdatafile = 'map.net.xml'
flowdatafile = 'FLOW.flow.xml'
routedatafile = 'ROU.rou.xml'

beginedges = ['edge4-13', 'edge5-14', 'edge16-15', 'edge21-22', 'edge35-36', 'edge48-47', 'edge52-53', 'edge24-25', 'edge33-34', 'edge18-19', 'edge17-13'] #顺序：南门，东门，东2门，西门，西北门，东北门， 紫荆园，二校门，刘卿楼，主楼，李兆基
endedges = []
for edge in beginedges:
    spl = edge[4:].split('-')
    endedges.append(edge[:4] + spl[1] + '-' + spl[0])
cartypes = ['CarA', 'CarB', 'CarC', 'CarD']

f = open(flowdatafile, 'w')
f.write('<flows>\n')
f.write('	<vType accel="3.0" decel="6.0" id="CarA" length="5.0" minGap="2.5" maxSpeed="50.0" sigma="0.5" />\n')
f.write('   <vType accel="2.0" decel="6.0" id="CarB" length="7.5" minGap="2.5" maxSpeed="50.0" sigma="0.5" />\n')
f.write('   <vType accel="1.0" decel="5.0" id="CarC" length="5.0" minGap="2.5" maxSpeed="40.0" sigma="0.5" />\n')
f.write('   <vType accel="1.0" decel="5.0" id="CarD" length="7.5" minGap="2.5" maxSpeed="30.0" sigma="0.5" />\n')
for i in range(100):
    begintime = randint(0, 2000)
    endtime = begintime + randint(50, 150)
    f.write('   <flow id="flow' + str(i) + '" from="' + choice(beginedges) + '" to="' + choice(endedges) + '" begin="' + str(begintime) + '" end="' + str(endtime) + '" number="' + str(randint(10, 100)) + '" type="' + choice(cartypes) + '"/>\n')
f.write('</flows>\n')
f.close()

print(os.system('duarouter -n ' + netdatafile + ' -f ' + flowdatafile + ' -o ' + routedatafile))
