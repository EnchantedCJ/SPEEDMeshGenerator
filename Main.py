# -*- coding:utf-8 -*-
import Geometry as Geo


def main():
    mySite = Geo.Site()
    mySite.iptCoordSiteCorner('./input/coordSiteCorner.txt')
    mySite.iptMeshConfig('./input/meshConfig.txt')
    mySite.iptCoordDrill('./input/coordDrill.txt')

    mySite.genPoint()
    mySite.genHex()
    mySite.genABSOSurface()
    mySite.genDGSurface()

    mySite.optMesh('mySite.mesh')


if __name__ == '__main__':
    main()
