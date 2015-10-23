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
            maxBlockC = maxX/bs2d[0] + 2,maxY/bs2d[1] +2


            for bcx in range(minBlockC[0],maxBlockC[0]):
                x = min(bcx*bs2d[0],self.shape2d[0])
                p.drawLine(x,minY,x,maxY )
            for bcy in range(minBlockC[1],maxBlockC[1]):
                y = min(bcy*bs2d[1],self.shape2d[1])
                p.drawLine(minX,y,maxX,y )


        #usableSizes = []
        #for bi,bz in enumerate(self.blockSizes):
        #    if pixSize[0] > bz/16:
        #        pass
        #    else:
        #        usableSizes.append((bi,bz))
        #if len(usableSizes) ==0 :
        #    usableSizes.append((bi,self.blockSizes[-1]))
        #for bi,bz in usableSizes:

            #print "PX",pixSize[0]
            #if pixSize[0] > bz/16:
            #    pass
            #else:
            #    bMinX = minX/bz
            #    bMaxX = maxX/bz
            #    bMinY = minY/bz
            #    bMaxY = maxY/bz
            #    #print bMinX,bMaxX
            #    w = float(bz)/128.0
            #    p.setPen(pg.mkPen(color=self.blockColors[bi,:],width=(bi+1)*0.1) )
            #    for biX in range(bMinX, bMaxX+1):
            #        p.drawLine(biX*bz,minY, biX*bz,maxY )
            #    for biY in range(bMinY, bMaxY+1):
            #        p.drawLine(minX,biY*bz, maxX, biY*bz)

            #if bz ==64:

            #    font = p.font()
            #    font.setPixelSize(5)
            #    p.setFont(font)
            #    p.setPen(pg.mkPen(color="w",width=0.2))
            #    for biX in range(bMinX, bMaxX+1):
            #        for biY in range(bMinY, bMaxY+1):
            #            rect = QtCore.QRectF(biX*bz,biY*bz,60,6)
            #            #p.drawText(pos,"%d/%d"%(biX,biY))
            #            p.drawText(rect, QtCore.Qt.AlignLeft, "%d/%d"%(biX,biY))








class BlockImageItems(object):

    def __init__(self,renderArea):
        self.renderArea = renderArea
        self.viewBox = renderArea.viewBox
        self.pixelLayers = self.viewBox.pixelLayers
        self.imgItemDict = dict()

        
        self.pixelLayers.sigPixelLayerAdded.connect(self.addPixelLayer)
    def setPos(self, x,y):
        for k,imageItem in self.imgItemDict.iteritems():
            imageItem.setPos(x,y)
    def setTilingVisible(self, visible):
        for k,imageItem in self.imgItemDict.iteritems():
            imageItem.setTilingVisible(visible)

    def addPixelLayer(self, layer):
        #print "layer added",layer.name()
        imageItem = TilingImageItem()
        imageItem.setZValue(10)
        self.imgItemDict[layer.name()] = imageItem
        self.viewBox.addItem(imageItem,ignoreBounds=True)


        # connect image item to signals
        layer.sigVisibilityChanged.connect(imageItem.setVisible)
        layer.sigAlphaChanged.connect(imageItem.setOpacity)



        #self.renderArea.updateVisibleBlocks()

    def blockAppear(self, spatialSlicing, time, blockPos):
        #print "block appeared",blockPos

        for name,layer in self.pixelLayers.layers.iteritems():
            if name in self.imgItemDict:
                imgItem = self.imgItemDict[name]
                res = layer.request3DBlock(spatialSlicing=spatialSlicing, time=time)
                imgItem.setPos(*blockPos)
                if res is not None:
                    #print "has data"
                    res = res.squeeze()
                    imgItem.setImage(res)
                    imgItem.setTilingVisible(True)
                    #imgItem.update()
                    imgItem.setLevels([0,255])
                else:
                    pass#print "and has no data"






class RenderArea(object):
    def __init__(self, viewBox, blockSize = 200, nBlocks=[10,10]):
        self.blockSize = blockSize
        self.pixelLayers = viewBox.pixelLayers


        #self.pixelLayers.sigPixelLayerAdded.connect(self.addPixelLayer)


        #pg.GraphicsObject.__init__(self)
        self.viewBox = viewBox
        self.visibleBlocks = VisibleBlocks(viewBox=viewBox, blockSize=blockSize,nBlocks=nBlocks)

        self.visibleBlocks.sigBlocksAppeared.connect(self.onBlocksAppear)
        self.visibleBlocks.sigBlocksDisappeared.connect(self.onBlocksDisappear)

        self.globalCoordToImageItem = dict()
        self.freeImageItems = set()
        self.usedImageItems = set()

        self.imageItems = [BlockImageItems(renderArea=self) for i in range(self.visibleBlocks.nTotalBlocks)]
        #self.tileItemGroups = [TileItemGroup() for i in range(self.visibleBlocks.nTotalBlocks)]

        for index,imageItem in enumerate(self.imageItems):
            imageItem._index = index
            self.freeImageItems.add(index)

            #self.viewBox.addItem(self.tileItemGroups[index])

        self.rawDataLayer = None


    #def boundingRectChanged(self, rect):
    #    self.updateVisibleBlocks()

    def boundingRect(self):
        return self.viewBox.viewRect()

    def setNoBlockVisible(self):
        pass

    def onScrolled(self):
        self.updateVisibleBlocks()

    def onTimeChanged(self, newTime):
        self.updateVisibleBlocks()

    def onViewRectChanged(self):
        self.visibleBlocks.onViewRectChanged()



    def onBlocksDisappear(self, globalBlocks):
        #print "remove",globalBlocks
        for gb in globalBlocks:
            imageItem = self.globalCoordToImageItem.pop(gb)
            imageItem.setTilingVisible(False)
            self.freeImageItems.add(imageItem._index)
            self.usedImageItems.remove(imageItem._index)

    def onBlocksAppear(self, globalBlocks):
        for gb in globalBlocks:
            assert len(self.freeImageItems)>0
            freeImageItemIndex = self.freeImageItems.pop()
            imageItem = self.imageItems[freeImageItemIndex]

            # request DATA
            #print "RENDER",gb
            #print "request"
            coordB = gb[0]*self.blockSize,gb[1]*self.blockSize
            coordE = (gb[0]+1)*self.blockSize, (gb[1]+1)*self.blockSize
            coordBegin = self.viewBox.make3DCoordinate(coordB)
            coordEnd = self.viewBox.make3DCoordinate(coordE,scrollOffset=1)
            spatialSlicing = make3dSlicing(coordBegin, coordEnd)
            self.updateSingleBlock(imageItem,spatialSlicing, coordB)
            imageItem.setPos(*coordB)
            self.globalCoordToImageItem[gb] = imageItem
            self.usedImageItems.add(freeImageItemIndex)

    def updateVisibleBlocks(self):
        ##import sys
        #sys.exit()
        for gb in self.visibleBlocks.visibleBlocks:
            imageItem = self.globalCoordToImageItem[gb]

            coordB = gb[0]*self.blockSize,gb[1]*self.blockSize
            coordE = (gb[0]+1)*self.blockSize, (gb[1]+1)*self.blockSize
            coordBegin = self.viewBox.make3DCoordinate(coordB)
            coordEnd = self.viewBox.make3DCoordinate(coordE,scrollOffset=1)
            slicing = make3dSlicing(coordBegin, coordEnd)
            self.updateSingleBlock(imageItem,slicing, coordB)
            #imageItem.setPos(*coordB)
            self.globalCoordToImageItem[gb] = imageItem


    def updateSingleBlock(self, imageItem, slicing, blockPos):  
        imageItem.blockAppear(spatialSlicing=slicing, blockPos=blockPos, 
                              time=self.viewBox.timeCoordinate)

    def paint(self, p, *args):
        pass
