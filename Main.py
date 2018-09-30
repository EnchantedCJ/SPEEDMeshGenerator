# -*- coding:utf-8 -*-
import Geometry as geo
import IO as io


def main():
    mySite = geo.Site()
    mySite.iptCoordSiteCorner('./input/coordSiteCorner.txt')
    mySite.iptMeshConfig('./input/meshConfig.txt')

    mySite.genPoint()
    mySite.genHex()
    mySite.genDGSurface()
    mySite.genABSOSurface()


if __name__ == '__main__':
    main()
