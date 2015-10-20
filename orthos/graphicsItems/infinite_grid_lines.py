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
    def __init__(self, viewBox, blockSize = 256, nBlocks=[10,10]):
        pg.GraphicsObject.__init__(self)
        self.viewBox = viewBox
        self.blockSize = blockSize
        self.nBlocks = nBlocks
        self.nTotalBlocks = nBlocks[0]*nBlocks[1]
        self.block2d = [Block2d() for i in range(self.nTotalBlocks)]
        self.visibleBlocks = set()
        self.globalBlockIdToLocal = dict()


        self.globalCoordToImageItem = dict()
        self.freeImageItems = set()
        self.usedImageItems = set()

        self.imageItems = [pg.ImageItem(border=None) for i in range(self.nTotalBlocks)]
        for index,imageItem in enumerate(self.imageItems):
            imageItem._index = index
            self.viewBox.addItem(imageItem)
            self.freeImageItems.add(index)
        self.rawDataLayer = None


    def boundingRectChanged(self, rect):
        self.updateVisibleBlocks()

    def boundingRect(self):
        return self.viewBox.viewRect()


    def updateVisibleBlocks(self):
        blockSize = self.blockSize
        pixSize =  self.viewBox.viewPixelSize()

        vrx = numpy.round(self.viewBox.state['viewRange'][0],0).astype('int64')
        vry = numpy.round(self.viewBox.state['viewRange'][1],0).astype('int64')
        minCoord = numpy.array([vrx[0],vry[0]])
        minCoord[0] = max(minCoord[0],0) 
        minCoord[1] = max(minCoord[1],0) 


        maxCoord = numpy.array([vrx[1],vry[1]])
        startBlockCoord = minCoord/blockSize
        endBlockCoord = maxCoord/blockSize + 1
        diffBlockCoord = endBlockCoord-startBlockCoord
        diffBlockCoord[0] = min(self.nBlocks[0],diffBlockCoord[0] ) 
        diffBlockCoord[1] = min(self.nBlocks[1],diffBlockCoord[1] ) 

        print "MinMaxCoord",minCoord,maxCoord
        print "START BLOCK COORD ",startBlockCoord,diffBlockCoord
        newVisibleBlocks = set()
        for biy in range(diffBlockCoord[1]):
            for bix in range(diffBlockCoord[0]):
                localBC  = bix,biy
                globalBC = bix+startBlockCoord[0],biy+startBlockCoord[1]
                newVisibleBlocks.add(globalBC)



        dissapeared = self.visibleBlocks - newVisibleBlocks
        appeared = newVisibleBlocks - self.visibleBlocks


        if(len(dissapeared)>0):
            self.blocksDissapear(dissapeared)
        if(len(appeared)>0):
            self.blocksAppear(appeared)

        self.visibleBlocks = newVisibleBlocks


    def blocksDissapear(self, globalBlocks):
        print "\n\n\n\n"
        for gb in globalBlocks:
            imageItem = self.globalCoordToImageItem.pop(gb)
            imageItem.setVisible(False)
            self.freeImageItems.add(imageItem._index)
            self.usedImageItems.remove(imageItem._index)

    def blocksAppear(self, globalBlocks):
        for gb in globalBlocks:
            assert len(self.freeImageItems)>0
            freeImageItemIndex = self.freeImageItems.pop()
            imageItem = self.imageItems[freeImageItemIndex]

            # request DATA
            print "RENDER",gb
            if self.rawDataLayer is not None:
                #print "request"
                coordB = gb[0]*self.blockSize,gb[1]*self.blockSize
                coordE = (gb[0]+1)*self.blockSize, (gb[1]+1)*self.blockSize
                zCoord = self.viewBox.scrollCoordinate

                coordBegin = [0,0,0]
                coordEnd = [0,0,0]

                coordBegin[self.viewBox.viewAxis[0]] = coordB[0]
                coordBegin[self.viewBox.viewAxis[1]] = coordB[1]
                coordBegin[self.viewBox.scrollAxis] = self.viewBox.scrollCoordinate
                coordEnd[self.viewBox.viewAxis[0]] = coordE[0]
                coordEnd[self.viewBox.viewAxis[1]] = coordE[1]
                coordEnd[self.viewBox.scrollAxis] = self.viewBox.scrollCoordinate+1

                slicing = []
                for b,e in zip(coordBegin, coordEnd):
                    slicing.append(slice(b,e))
                res = self.rawDataLayer.request3Dblock(slicing)
                #print "SET POS"
                imageItem.setPos(*coordB)

                #imageItem.update()
                
                if res is not None:
                    res = res.squeeze()
                    imageItem.setImage(res)
                    imageItem.setVisible(True)
                    imageItem.update()
                    imageItem.setLevels([0,255])
                else:
                    print "NO DATA"
            else:
                print "no layer"
            self.globalCoordToImageItem[gb] = imageItem
            self.usedImageItems.add(freeImageItemIndex)


    def paint(self, p, *args):

        if False:
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
