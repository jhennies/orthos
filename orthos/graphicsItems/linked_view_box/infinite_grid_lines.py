import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy
from ..tiling_image_item import *
from tiling import VisibleBlocks


def make3dSlicing(begin,end):
    slicing = []
    for b,e in zip(begin, end):
        slicing.append(slice(b,e))
    return slicing




class InfiniteGridLines(pg.GraphicsObject):
    def __init__(self, viewBox):
        pg.GraphicsObject.__init__(self)
        self.viewBox = viewBox
        self.mlBlocking = self.viewBox.navigator.mlBlocking

        self.initialzie()

    def initialzie(self):


        self.shape2d = self.mlBlocking.shape2d(self.viewBox.scrollAxis)
        self.blockColors = numpy.zeros(shape=(self.mlBlocking.nBlockings, 3))

        fLen = float(self.mlBlocking.nBlockings)
        for bi in range(self.mlBlocking.nBlockings):
            r = 50.0
            b = 20 + (fLen-bi)/fLen * 180.0
            g = 50.0 
            self.blockColors[bi, :] = r,g,b
    def boundingRect(self):
        return QtCore.QRectF(0,0,self.shape2d[0],self.shape2d[1])
    def paint(self, p, *args):


        vrx = self.viewBox.state['viewRange'][0]
        vry = self.viewBox.state['viewRange'][1]
        minX = max(int(vrx[0]),0)
        minY = max(int(vry[0]),0)
        maxX = min(int(vrx[1]),self.shape2d[0])
        maxY = min(int(vry[1]),self.shape2d[1])

        mlB = self.mlBlocking

        for blockingIndex in range(mlB.nBlockings):

            w = float(blockingIndex+1)*2.0
            c = self.blockColors[blockingIndex,:]
            p.setPen(pg.mkPen(color=c,width=w ))

            bs2d = mlB.blockShape2d(blockingIndex, self.viewBox.scrollAxis)

            # draw horizonal lines
            minBlockC = minX/bs2d[0],minY/bs2d[1]
            maxBlockC = maxX/bs2d[0] + 2,maxY/bs2d[1] +1


            for bcx in range(minBlockC[0],maxBlockC[0]):
                x = min(bcx*bs2d[0],self.shape2d[0])
                p.drawLine(x,minY,x,maxY )
            for bcy in range(minBlockC[1],maxBlockC[1]):
                y = min(bcy*bs2d[1],self.shape2d[1])
                p.drawLine(minX,y,maxX,y )

