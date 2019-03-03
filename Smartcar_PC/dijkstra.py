from collections import defaultdict
from heapq import *
import extdata
import absorp
import sys
import os

path = os.getcwd()
MAP = path + os.sep + 'map.txt'

def dijkstra(edges, f, t):
    g = defaultdict(set)
    for l,r,c in edges:
        g[l].add((c, r))
        g[r].add((c, l))

    q, seen, mins = [(0,f,())], set(), {f: 0}
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)
            if v1 == t: return (cost, path)

            for c, v2 in g.get(v1, ()):
                if v2 in seen: continue
                prev = mins.get(v2, None)
                next = cost + c
                if prev is None or next < prev:
                    mins[v2] = next
                    heappush(q, (next, v2, path))

    return float("inf")

def get_route(start_num, end_num):
    edges = []
    graph = extdata.Graph()
    graph.read(MAP)
    for i in range(graph.point_num):
        for j in range(graph.point_num):
            if graph.line[i][j] != 0 and i < j:
                edge = (str(i + 1), str(j + 1), int(absorp.Point(graph.x[i], graph.y[i]).cal_dis(absorp.Point(graph.x[j], graph.y[j]))))
                edges.append(edge)
    
    out = dijkstra(edges, str(start_num), str(end_num))
    data = {}
    data['cost'] = out[0]
    aux = []
    while len(out) > 1:
        aux.append(out[0])
        out = out[1]
    aux.remove(data['cost'])
    aux.reverse()
    data['path'] = aux

    return data

def get_cost(start_num, end_num):
    graph = extdata.Graph()
    graph.read(MAP)
    return int(absorp.Point(graph.x[start_num], graph.y[start_num]).cal_dis(absorp.Point(graph.x[end_num], graph.y[end_num])))

if __name__ == "__main__":
    print("=== Dijkstra ===")
    # print(edges)
    print(get_route(sys.argv[1], sys.argv[2]))
    # print "A -> E:"
    # print dijkstra(edges, "A", "E")
    # print "F -> G:"
    # print dijkstra(edges, "F", "G")
