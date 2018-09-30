# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
from  mpl_toolkits.mplot3d import Axes3D


class Point(object):
    def __init__(self, x, y, z):
        self.id = 0
        self.x = x
        self.y = y
        self.z = z
        pass

    pass


class Surface(object):
    def __init__(self):
        pass

    pass


class Hex(object):
    def __init__(self, points):
        self.id=0
        self.points = points
        self.calCenter()

    def calCenter(self):
        xlist = []
        ylist = []
        zlist = []
        for pt in self.points:
            xlist.append(pt.x)
            ylist.append(pt.y)
            zlist.append(pt.z)
        numofpoints = len(self.points)
        xcenter = sum(xlist) / numofpoints
        ycenter = sum(ylist) / numofpoints
        zcenter = sum(zlist) / numofpoints
        self.center = Point(xcenter, ycenter, zcenter)


class Layer(object):
    def __init__(self, depth, meshLength):
        self.id = 0
        self.depth = depth
        self.meshLength = meshLength
        self.meshx = 0
        self.meshy = 0
        self.meshz = 0
        self.ptcount = 0
        self.hexcount = 0


class Site(object):
    def __init__(self):
        self.corners = []
        self.layers = []
        self.minx = 0
        self.maxx = 0
        self.miny = 0
        self.maxy = 0
        self.points = []
        self.hexes = []
        self.ptcount = 0
        self.hexcount = 0

    def iptCoordSiteCorner(self, dir):
        with open(dir, 'r', encoding='utf-8') as f:
            f.readline()
            for i in range(4):
                temp = f.readline().strip('\n').split()
                id = int(temp[0])
                x = float(temp[1])
                y = float(temp[2])
                pt = Point(x, y, 0)
                self.corners.append(pt)

        corner_x = []
        corner_y = []
        for pt in self.corners:
            corner_x.append(pt.x)
            corner_y.append(pt.y)
        self.minx = min(corner_x)
        self.maxx = max(corner_x)
        self.miny = min(corner_y)
        self.maxy = max(corner_y)
        print('Site corner: ', self.minx, self.maxx, self.miny, self.maxy)

    def iptMeshConfig(self, dir):
        with open(dir, 'r', encoding='utf-8') as f:
            f.readline()
            for line in f.readlines():
                temp = line.strip('\n').split()
                id = int(temp[0])
                depth = float(temp[1])
                meshLength = float(temp[2])
                ly = Layer(depth, meshLength)
                ly.id = id
                self.layers.append(ly)

                ly.meshx = int((self.maxx - self.minx) / ly.meshLength)
                ly.meshy = int((self.maxy - self.miny) / ly.meshLength)
                ly.meshz = int(ly.depth / ly.meshLength)
                print('Layer{i} mesh num: {x} x {y} x {z}'.format(i=ly.id, x=ly.meshx, y=ly.meshy, z=ly.meshz))

        pass

    def genPoint(self):
        # fig = plt.figure()
        # ax = fig.gca(projection='3d')

        self.ptcount = 0
        ptx = 0
        pty = 0
        ptz = 0
        for ly in self.layers:

            for i in range(ly.meshz + 1):
                if i == 0:
                    pass
                else:
                    ptz = ptz - ly.meshLength
                for j in range(ly.meshy + 1):
                    if j == 0:
                        pty = self.miny
                    else:
                        pty = pty + ly.meshLength
                    for k in range(ly.meshx + 1):
                        if k == 0:
                            ptx = self.minx
                        else:
                            ptx = ptx + ly.meshLength

                        pt = Point(ptx, pty, ptz)
                        self.ptcount += 1
                        ly.ptcount += 1
                        pt.id = self.ptcount
                        self.points.append(pt)
                        print(pt.id, ptx, pty, ptz)

                        # ax.scatter([ptx], [pty], [ptz], color='r')
        # plt.show()

    def genHex(self):
        # my order

        #   3---4
        #  /|  /|
        # 1---2
        # | 7-|-8
        # 5---6/

        # tianyuan order

        #   8---7
        #  /|  /|
        # 5---6
        # | 4-|-3
        # 1---2/

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        idbase = 0
        for ly in self.layers:
            if ly.id==1:
                pass
            else:
                idbase += self.layers[ly.id-2].ptcount  #id加上一层的总节点数
            for i in range(ly.meshz):
                for j in range(ly.meshy):
                    for k in range(ly.meshx):
                        id1 = idbase + (ly.meshx + 1) * (ly.meshy + 1) * i + (ly.meshx + 1) * j + k + 1
                        id2 = id1 + 1
                        id3 = id1 + (ly.meshx + 1)
                        id4 = id3 + 1
                        id5 = id1 + (ly.meshx + 1) * (ly.meshy + 1)
                        id6 = id5 + 1
                        id7 = id3 + (ly.meshx + 1) * (ly.meshy + 1)
                        id8 = id7 + 1
                        idlist = [id5, id6, id8, id7, id1, id2, id4, id3]
                        ptlist = []
                        for id in idlist:
                            ptlist.append(self.points[id - 1])  # list start from 0
                        hex = Hex(ptlist)
                        self.hexcount += 1
                        ly.hexcount += 1
                        hex.id=self.hexcount
                        self.hexes.append(hex)
                        print(hex.id, end="\t")
                        for m in range(len(hex.points)):
                            print(hex.points[m].id, end="\t")
                        print('\n')

                        ax.scatter([hex.center.x], [hex.center.y], [hex.center.z], color='b')
        plt.show()



    def genDGSurface(self):
        pass

    def genABSOSurface(self):
        pass
