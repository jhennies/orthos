import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy

class InfiniteGridLines(pg.GraphicsObject):
    def __init__(self, viewBox,blockSizes):
        pg.GraphicsObject.__init__(self)
        self.viewBox = viewBox
        self.blockSizes = [64,128,256,512, 1024, 2048]
        self.pixelSize =  [1,2,4,8,16]
        self.blockColors = numpy.zeros(shape=(len(self.blockSizes), 3))

        fLen = float(len(self.blockSizes))
        for bi in range(len(self.blockSizes)):
            r = 255.0
            b = (fLen-bi)/fLen * 255.0
            g = 255.0 - b
            self.blockColors[bi, :] = r,g,b
    def boundingRect(self):
        return self.viewBox.viewRect()
    def paint(self, p, *args):

        pixSize =  self.viewBox.viewPixelSize()

        vrx = self.viewBox.state['viewRange'][0]
        vry = self.viewBox.state['viewRange'][1]

        #print vrx,vry
        minX = int(vrx[0])
        maxX = int(vrx[1])
        minY = int(vry[0])
        maxY = int(vry[1])

        usableSizes = []
        for bi,bz in enumerate(self.blockSizes):
            if pixSize[0] > bz/16:
                pass
            else:
                usableSizes.append((bi,bz))

        if len(usableSizes) ==0 :
            usableSizes.append((bi,self.blockSizes[-1]))

        for bi,bz in usableSizes:

            #print "PX",pixSize[0]
            if pixSize[0] > bz/16:
                pass
            else:
                bMinX = minX/bz
                bMaxX = maxX/bz
                bMinY = minY/bz
                bMaxY = maxY/bz
                #print bMinX,bMaxX
                w = float(bz)/128.0
                p.setPen(pg.mkPen(color=self.blockColors[bi,:],width=(bi+1)*0.1) )
                for biX in range(bMinX, bMaxX+1):
                    p.drawLine(biX*bz,minY, biX*bz,maxY )
                for biY in range(bMinY, bMaxY+1):
                    p.drawLine(minX,biY*bz, maxX, biY*bz)

            if bz ==64:

                font = p.font()
                font.setPixelSize(5)
                p.setFont(font)
                p.setPen(pg.mkPen(color="w",width=0.2))
                for biX in range(bMinX, bMaxX+1):
                    for biY in range(bMinY, bMaxY+1):
                        rect = QtCore.QRectF(biX*bz,biY*bz,60,6)
                        #p.drawText(pos,"%d/%d"%(biX,biY))
                        p.drawText(rect, QtCore.Qt.AlignLeft, "%d/%d"%(biX,biY))







class Block2d(object):
    def __init__(self):
        pass




class RenderArea(pg.GraphicsObject):
    def __init__(self, viewBox, blockSize = 512, nBlocks=[6,5]):
        pg.GraphicsObject.__init__(self)
        self.viewBox = viewBox
        self.blockSize = blockSize
        self.nBlocks = nBlocks
        self.block2d = [Block2d() for i in range(nBlocks[0]*nBlocks[1])]

        self.visibleBlocks = set()
    def boundingRect(self):
        return self.viewBox.viewRect()


    def updateVisibleBlocks(self):
        blockSize = self.blockSize
        pixSize =  self.viewBox.viewPixelSize()

        vrx = self.viewBox.state['viewRange'][0]
        vry = self.viewBox.state['viewRange'][1]
        #print vrx,vry
        minX = int(vrx[0])/blockSize
        maxX = int(vrx[1])/blockSize
        minY = int(vry[0])/blockSize
        maxY = int(vry[1])/blockSize


        

        print "mimadiff",diff

    def paint(self, p, *args):
        self.updateVisibleBlocks()
        blockSize = self.blockSize
        pixSize =  self.viewBox.viewPixelSize()

        vrx = self.viewBox.state['viewRange'][0]
        vry = self.viewBox.state['viewRange'][1]
        #print vrx,vry
        minX = int(vrx[0])
        maxX = int(vrx[1])
        minY = int(vry[0])
        maxY = int(vry[1])

        bMinX = (minX/blockSize)*blockSize
        bMinY = (minY/blockSize)*blockSize

        bMaxX = (maxX/blockSize)*blockSize
        bMaxY = (maxX/blockSize)*blockSize


        font = p.font()
        font.setPixelSize(50)
        p.setFont(font)

        for y in range(self.nBlocks[1]):
            for x in range(self.nBlocks[0]):
                

                c=bMinX + x*blockSize,bMinY + y*blockSize

                p.setPen(pg.mkPen(color="w",width=0.2))
                p.drawRect(c[0],c[1],blockSize,blockSize)

                p.setPen(pg.mkPen(color="w",width=0.2))
                rect = QtCore.QRectF(c[0],c[1],60,6)
                p.drawText(c[0],c[1],"%d/%d"%c)
                #p.drawText(rect, QtCore.Qt.AlignLeft, "%d/%d"%c)
