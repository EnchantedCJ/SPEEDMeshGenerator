# -*- coding:utf-8 -*-
import Geometry as geo


def main():
    mySite = geo.Site()
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
