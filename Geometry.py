# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class Point(object):
    def __init__(self, x, y, z):
        self.id = 0
        self.x = x
        self.y = y
        self.z = z


class Surface(object):
    def __init__(self, points):
        self.id = 0
        self.points = points
        self.mate = 0
        pass

    pass


class Hex(object):
    def __init__(self, points):
        self.id = 0
        self.points = points
        self.mate = 0
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
    def __init__(self, depth, meshSize):
        self.id = 0
        self.depth = depth
        self.mSize_x = meshSize[0]
        self.mSize_y = meshSize[1]
        self.mSize_z = meshSize[2]
        self.meshx = 0
        self.meshy = 0
        self.meshz = 0
        self.ptcount = 0
        self.hexcount = 0
        self.surfcount = 0
        self.DGsurfcount = 0
        self.ABSOsurfcount = 0
        self.connectUp = False
        self.connectLow = False


class Drill(object):
    def __init__(self, x, y):
        self.id = 0
        self.x = x
        self.y = y
        pass


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
        self.DGsurfs = []
        self.ABSOsurfs = []
        self.ptcount = 0
        self.hexcount = 0
        self.surfcount = 0
        self.DGsurfcount = 0
        self.ABSOsurfcount = 0

        self.drills = []
        self.drcount = 0
        self.matecount = 0

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
                mSize_x = float(temp[2])
                mSize_y = float(temp[3])
                mSize_z = float(temp[4])
                meshSize = [mSize_x, mSize_y, mSize_z]
                ly = Layer(depth, meshSize)
                ly.id = id
                self.layers.append(ly)

                ly.meshx = int((self.maxx - self.minx) / ly.mSize_x)
                ly.meshy = int((self.maxy - self.miny) / ly.mSize_y)
                ly.meshz = int(ly.depth / ly.mSize_z)
                print('Layer{i} mesh num: {x} x {y} x {z}'.format(i=ly.id, x=ly.meshx, y=ly.meshy, z=ly.meshz))

    def iptCoordDrill(self, dir):
        with open(dir, 'r', encoding='utf-8') as f:
            f.readline()
            for line in f.readlines():
                temp = line.strip('\n').split()
                id = int(temp[0])
                x = float(temp[1])
                y = float(temp[2])
                dr = Drill(x, y)
                dr.id = id
                self.drills.append(dr)
                self.drcount += 1
                print('Drill{id} {x} {y}'.format(id=id, x=x, y=y))

    def optMesh(self, dir):
        with open(dir, 'w', encoding='utf-8') as f:
            # headline
            f.write('%10d' % self.ptcount)  # number of nodes
            f.write('%10d' % (self.hexcount + self.surfcount))  # number of elements
            for i in range(3):
                f.write('%10d' % 0)
            f.write('\n')
            # nodes
            for pt in self.points:
                f.write('%d  ' % pt.id)
                f.write('%15.7e' % pt.x)
                f.write('%15.7e' % pt.y)
                f.write('%15.7e' % pt.z)
                f.write('\n')
            # ABSO surface
            for surf in self.ABSOsurfs:
                f.write('%d' % surf.id)
                f.write('%10d' % surf.mate)
                f.write(' quad ')
                for pt in surf.points:
                    f.write('%10d' % pt.id)
                f.write('\n')
            # DG surface
            for surf in self.DGsurfs:
                f.write('%d' % surf.id)
                f.write('%10d' % surf.mate)
                f.write(' quad ')
                for pt in surf.points:
                    f.write('%10d' % pt.id)
                f.write('\n')
            # hexes
            for hex in self.hexes:
                f.write('%d' % hex.id)
                f.write('%10d' % hex.mate)
                f.write(' hex ')
                for pt in hex.points:
                    f.write('%10d' % pt.id)
                f.write('\n')

    def genPoint(self):
        # fig = plt.figure()
        # ax = fig.gca(projection='3d')

        self.ptcount = 0
        ptx = 0
        pty = 0
        ptz = 0

        # 判断连接性
        lastSize_x = -1
        lastSize_y = -1
        for i in range(len(self.layers)):
            thisSize_x = self.layers[i].mSize_x
            thisSize_y = self.layers[i].mSize_y
            if thisSize_x == lastSize_x and thisSize_y == lastSize_y:
                self.layers[i - 1].connectUp = True
                self.layers[i].connectLow = True
            lastSize_x = thisSize_x
            lastSize_y = thisSize_y

        for ly in self.layers:

            if ly.connectLow:
                iterz = ly.meshz  # 如果连接，不重复连接高度处的点
            else:
                iterz = ly.meshz + 1
            for i in range(iterz):
                if i == 0 and not ly.connectLow:
                    pass
                else:
                    ptz = ptz - ly.mSize_z
                for j in range(ly.meshy + 1):
                    if j == 0:
                        pty = self.miny  # 重置为左下角点
                    else:
                        pty = pty + ly.mSize_y
                    for k in range(ly.meshx + 1):
                        if k == 0:
                            ptx = self.minx  # 重置为左下角点
                        else:
                            ptx = ptx + ly.mSize_x

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

        #   3---4    z
        #  /|  /|    | /y
        # 1---2      |/
        # | 7-|-8     --- x
        # 5---6/

        # tianyuan order

        #   8---7
        #  /|  /|
        # 5---6
        # | 4-|-3
        # 1---2/

        # fig = plt.figure()
        # ax = fig.gca(projection='3d')

        idbase = 0
        for ly in self.layers:
            if ly.id == 1:
                pass
            else:
                idbase += self.layers[ly.id - 2].ptcount  # 每个layer的起始点，id叠加上一层的总节点数
            if ly.connectLow:  # 如果连接，该layer最上层点与上个layer最下层点重合，idbase应折减上个layer一层的点数
                idbase -= (self.layers[ly.id - 2].meshx + 1) * (self.layers[ly.id - 2].meshy + 1)
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
                        hex.id = self.hexcount
                        # different materials when belong to different drills
                        nearestDrill = self._findNearestDrill(hex)
                        hex.mate = self.matecount + nearestDrill.id
                        self.hexes.append(hex)

                        print(hex.id, end="\t")
                        print('{m} hex'.format(m=hex.mate), end="\t")
                        for m in range(len(hex.points)):
                            print(hex.points[m].id, end="\t")
                        print('\n')
                        # ax.scatter([hex.center.x], [hex.center.y], [hex.center.z], color='b')

                # different materials when meshz increases
                self.matecount += self.drcount

                # plt.show()

    def _findNearestDrill(self, hex):
        dists = []
        for drill in self.drills:
            dist = pow(pow(hex.center.x - drill.x, 2) + pow(hex.center.y - drill.y, 2), 0.5)
            dists.append(dist)
        nearestID = dists.index(min(dists)) + 1
        return self.drills[nearestID - 1]

    def genABSOSurface(self):
        # my order

        # surf 1~4        surf bottom
        # 1 -- 2          3 -- 4
        # |    |          |    |
        # 3 -- 4          1 -- 2

        # tianyuan order

        # what are surf 1~4
        #    ---        z
        #  /| 3/|       | /y
        #  --- 2        |/
        # |41-|-        --- x
        #  --- /

        # surf 1          surf 2          surf 3          surf 4          surf bottom
        # 4 -- 3   z      4 -- 3   z      3 -- 4   z      3 -- 4   z      1 -- 2   y
        # |    |   |      |    |   |      |    |   |      |    |   |      |    |   |
        # 1 -- 2   ----x  1 -- 2   ----y  2 -- 1   ----x  2 -- 1   ----y  4 -- 3   ----x

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        idbase = 0
        for ly in self.layers:
            if ly.id == 1:
                pass
            else:
                idbase += self.layers[ly.id - 2].ptcount  # 每个layer的起始点，id叠加上一层的总节点数
            if ly.connectLow:  # 如果连接，该layer最上层点与上个layer最下层点重合，idbase应折减上个layer一层的点数
                idbase -= (self.layers[ly.id - 2].meshx + 1) * (self.layers[ly.id - 2].meshy + 1)
            for i in range(ly.meshz):
                # surf 1
                j = 0
                for k in range(ly.meshx):
                    id1 = idbase + (ly.meshx + 1) * (ly.meshy + 1) * i + (ly.meshx + 1) * j + k + 1
                    id2 = id1 + 1
                    id3 = id1 + (ly.meshx + 1) * (ly.meshy + 1)
                    id4 = id3 + 1
                    idlist = [id3, id4, id2, id1]
                    ptlist = []
                    for id in idlist:
                        ptlist.append(self.points[id - 1])  # list start from 0

                    surf = Surface(ptlist)
                    self.ABSOsurfcount += 1
                    self.surfcount += 1
                    ly.ABSOsurfcount += 1
                    ly.surfcount += 1
                    surf.id = self.surfcount
                    surf.mate = self.matecount + 2
                    self.ABSOsurfs.append(surf)

                    print(surf.id, end="\t")
                    print('{m} quad'.format(m=surf.mate), end="\t")
                    for m in range(len(surf.points)):
                        print(surf.points[m].id, end="\t")
                        # ax.scatter([surf.points[m].x], [surf.points[m].y], [surf.points[m].z], color='k')
                    print('\n')
                # surf 2
                k = ly.meshx
                for j in range(ly.meshy):
                    id1 = idbase + (ly.meshx + 1) * (ly.meshy + 1) * i + (ly.meshx + 1) * j + k + 1
                    id2 = id1 + (ly.meshx + 1)
                    id3 = id1 + (ly.meshx + 1) * (ly.meshy + 1)
                    id4 = id3 + (ly.meshx + 1)
                    idlist = [id3, id4, id2, id1]
                    ptlist = []
                    for id in idlist:
                        ptlist.append(self.points[id - 1])  # list start from 0

                    surf = Surface(ptlist)
                    self.ABSOsurfcount += 1
                    self.surfcount += 1
                    ly.ABSOsurfcount += 1
                    ly.surfcount += 1
                    surf.id = self.surfcount
                    surf.mate = self.matecount + 3
                    self.ABSOsurfs.append(surf)

                    print(surf.id, end="\t")
                    print('{m} quad'.format(m=surf.mate), end="\t")
                    for m in range(len(surf.points)):
                        print(surf.points[m].id, end="\t")
                        # ax.scatter([surf.points[m].x], [surf.points[m].y], [surf.points[m].z], color='k')
                    print('\n')
                # surf 3
                j = ly.meshy
                for k in range(ly.meshx):
                    id1 = idbase + (ly.meshx + 1) * (ly.meshy + 1) * i + (ly.meshx + 1) * j + k + 1
                    id2 = id1 + 1
                    id3 = id1 + (ly.meshx + 1) * (ly.meshy + 1)
                    id4 = id3 + 1
                    idlist = [id4, id3, id1, id2]
                    ptlist = []
                    for id in idlist:
                        ptlist.append(self.points[id - 1])  # list start from 0

                    surf = Surface(ptlist)
                    self.ABSOsurfcount += 1
                    self.surfcount += 1
                    ly.ABSOsurfcount += 1
                    ly.surfcount += 1
                    surf.id = self.surfcount
                    surf.mate = self.matecount + 4
                    self.ABSOsurfs.append(surf)

                    print(surf.id, end="\t")
                    print('{m} quad'.format(m=surf.mate), end="\t")
                    for m in range(len(surf.points)):
                        print(surf.points[m].id, end="\t")
                        # ax.scatter([surf.points[m].x], [surf.points[m].y], [surf.points[m].z], color='k')
                    print('\n')
                # surf 4
                k = 0
                for j in range(ly.meshy):
                    id1 = idbase + (ly.meshx + 1) * (ly.meshy + 1) * i + (ly.meshx + 1) * j + k + 1
                    id2 = id1 + (ly.meshx + 1)
                    id3 = id1 + (ly.meshx + 1) * (ly.meshy + 1)
                    id4 = id3 + (ly.meshx + 1)
                    idlist = [id4, id3, id1, id2]
                    ptlist = []
                    for id in idlist:
                        ptlist.append(self.points[id - 1])  # list start from 0

                    surf = Surface(ptlist)
                    self.ABSOsurfcount += 1
                    self.surfcount += 1
                    ly.ABSOsurfcount += 1
                    ly.surfcount += 1
                    surf.id = self.surfcount
                    surf.mate = self.matecount + 5
                    self.ABSOsurfs.append(surf)

                    print(surf.id, end="\t")
                    print('{m} quad'.format(m=surf.mate), end="\t")
                    for m in range(len(surf.points)):
                        print(surf.points[m].id, end="\t")
                        # ax.scatter([surf.points[m].x], [surf.points[m].y], [surf.points[m].z], color='k')
                    print('\n')
            # surf bottom
            if ly.id == len(self.layers):
                i = ly.meshz
                for j in range(ly.meshy):
                    for k in range(ly.meshx):
                        id1 = idbase + (ly.meshx + 1) * (ly.meshy + 1) * i + (ly.meshx + 1) * j + k + 1
                        id2 = id1 + 1
                        id3 = id1 + (ly.meshx + 1)
                        id4 = id3 + 1
                        idlist = [id3, id4, id2, id1]
                        ptlist = []
                        for id in idlist:
                            ptlist.append(self.points[id - 1])  # list start from 0

                        surf = Surface(ptlist)
                        self.ABSOsurfcount += 1
                        self.surfcount += 1
                        ly.ABSOsurfcount += 1
                        ly.surfcount += 1
                        surf.id = self.surfcount
                        surf.mate = self.matecount + 1
                        self.ABSOsurfs.append(surf)

                        print(surf.id, end="\t")
                        print('{m} quad'.format(m=surf.mate), end="\t")
                        for m in range(len(surf.points)):
                            print(surf.points[m].id, end="\t")
                            # ax.scatter([surf.points[m].x], [surf.points[m].y], [surf.points[m].z], color='k')
                        print('\n')

        self.matecount += 5
        # plt.show()

    def genDGSurface(self):
        # my order
        # 3 -- 4   y
        # |    |   |
        # 1 -- 2   ----x

        # tianyuan order
        # 1 -- 2   y
        # |    |   |
        # 4 -- 3   ----x

        # fig = plt.figure()
        # ax = fig.gca(projection='3d')

        idbase = 0
        for ly in self.layers:
            if ly.id == 1:
                pass
            else:
                idbase += self.layers[ly.id - 2].ptcount  # 每个layer的起始点，id叠加上一层的总节点数
            if ly.connectLow:  # 如果连接，该layer最上层点与上个layer最下层点重合，idbase应折减上个layer一层的点数
                idbase -= (self.layers[ly.id - 2].meshx + 1) * (self.layers[ly.id - 2].meshy + 1)
            for i in [0, ly.meshz]:  # 每个layer的最上层和最下层
                if i == 0 and ly.id == 1:
                    continue  # 第一个layer的最上层不设DG面
                if i == ly.meshz and ly.id == len(self.layers):
                    continue  # 最后一个layer的最下层不设DG面
                if i == 0 and ly.connectLow:
                    continue  # 连接面下layer的最上层不设DG面
                if i == ly.meshz and ly.connectUp:
                    continue  # 连接面上layer的最下层不设DG面

                for j in range(ly.meshy):
                    for k in range(ly.meshx):
                        id1 = idbase + (ly.meshx + 1) * (ly.meshy + 1) * i + (ly.meshx + 1) * j + k + 1
                        id2 = id1 + 1
                        id3 = id1 + (ly.meshx + 1)
                        id4 = id3 + 1
                        idlist = [id3, id4, id2, id1]
                        ptlist = []
                        for id in idlist:
                            ptlist.append(self.points[id - 1])  # list start from 0

                        surf = Surface(ptlist)
                        self.DGsurfcount += 1
                        self.surfcount += 1
                        ly.DGsurfcount += 1
                        ly.surfcount += 1
                        surf.id = self.surfcount
                        surf.mate = self.matecount + 1
                        self.DGsurfs.append(surf)

                        print(surf.id, end="\t")
                        print('{m} quad'.format(m=surf.mate), end="\t")
                        for m in range(len(surf.points)):
                            print(surf.points[m].id, end="\t")
                            # ax.scatter([surf.points[m].x], [surf.points[m].y], [surf.points[m].z], color='g')
                        print('\n')

                # different materials when i changes
                self.matecount += 1
                # plt.show()
