import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import vigra
import numpy
from blocking import *
from functools import partial

from orthos.graphicsItems import *




class ImageItemContainer(object):
    def __init__(self,viewBox,inputShape, blocking2d, axis):

        self.viewBox = viewBox
        self.inputShape = inputShape
        self.axis = axis
        self.blocking2d = blocking2d
        nBlocks = len(self.blocking2d)
        self.imageItemsPerBlock =[None]*nBlocks
        self.layers = dict()
        self.blockToIndex = dict()
        

    def toSlicing(self, block, p):
        if self.axis == 0:
            begin = (p,block[0][0],block[0][1])
            end = (p+1,block[1][0],block[1][1])
        elif self.axis == 1:
            begin = (block[0][0],p,block[0][1])
            end = (block[1][0],p+1,block[1][1])
        elif self.axis == 2:
            begin = (block[0][0],block[0][1],p)
            end = (block[1][0],block[1][1],p+1)

        slicing=[]
        for b,e in zip(begin,end):
            slicing.append(slice(b,e))
        return slicing

    def onBlocksAppear(self, blocks):
        try:
            for blockIndex in blocks:
                self.updateBlockData(blockIndex)
        except:
            pass

    def updateBlockData(self, blockIndex):
        blockIndex = int(blockIndex)
        #print blockIndex
        block = self.blocking2d[blockIndex]
        blockLayerDict = self.imageItemsPerBlock[blockIndex]
        if blockLayerDict is None:
            blockLayerDict = dict()
            self.imageItemsPerBlock[blockIndex] = blockLayerDict
        for layerName in blockLayerDict.keys():
            layer = self.layers[layerName]
            imgItem = blockLayerDict[layerName]
            slicing = self.toSlicing(block,self.viewBox.axisPos())
            data = layer.getData(slicing).squeeze()

            lut = layer.widget().ge.item.getLookupTable(nPts=256)
            imgItem.setLookupTable(lut)
            imgItem.updateImage(data)




    def onBlocksDissappear(self, blocks):
        print "dissappear",blocks

    def onScroll(self, p):
        print "blocks to update",len(self.viewBox.visibleBlocks)
        for block in self.viewBox.visibleBlocks:
            self.updateBlockData(block)

    def updateVisible(self):
        "on update visibile"
        self.onBlocksAppear(self.viewBox.visibleBlocks)

    def updateLut(self, blockIndex):
        blockIndex = int(blockIndex)
        blockLayerDict = self.imageItemsPerBlock[blockIndex]
        if blockLayerDict is None:
            blockLayerDict = dict()
            self.imageItemsPerBlock[blockIndex] = blockLayerDict
        for layerName in blockLayerDict.keys():
            imgItem = blockLayerDict[layerName]
            layer = self.layers[layerName]
            lut = layer.widget().ge.item.getLookupTable(nPts=256)
            imgItem.setLookupTable(lut)
            #imgItem.updateImage()




    def addPixelLayer(self, layer, name):
        with vigra.Timer("add pixel layer"):
            self.layers[name] = layer
            nBlocks = len(self.blocking2d)

            for blockIndex in range(nBlocks):
                block = self.blocking2d[blockIndex]

                blockLayerDict  = self.imageItemsPerBlock[blockIndex]

                blockLayerDict = self.imageItemsPerBlock[blockIndex]
                if blockLayerDict is None:
                    blockLayerDict = dict()
                self.imageItemsPerBlock[blockIndex] = blockLayerDict


                imageItem = pg.ImageItem(border=None)
                imageItem.setPos(block[0][0],block[0][1])


                item = layer.widget_.ge.item

                item.sigGradientChanged.connect(partial(self.updateLut,blockIndex))

                #self.onBlocksAppear(self.viewBox.visibleBlocks)

                self.viewBox.addItem(imageItem)
                blockLayerDict[name] = imageItem

            self.onBlocksAppear(self.viewBox.visibleBlocks)





class BvGridViewBox(pg.ViewBox):


    sigScrolled = QtCore.Signal(object)                         
    sigBlocksAppeared = QtCore.Signal(object)
    sigBlocksDisappeared = QtCore.Signal(object)
    sigMoveOtherViewers = QtCore.Signal(object, object)

    def __init__(self, inputShape,blockShape, axis=2):


        super(BvGridViewBox,self).__init__(invertY=True,lockAspect=True)
        self.setRange( xRange=(450,550),yRange=(450,550), disableAutoRange=True)
        self.inputShape=inputShape
        self.axis=axis
        s2d = self.shape2d()

        self.setAspectLocked(True)
        self.setMenuEnabled(False)

       
        self.blocking2d = inputShape.planeBlocking(blockShape=blockShape, axis=axis)
        
        self.imageItemContainer = ImageItemContainer(viewBox=self,
                                                     inputShape=inputShape,
                                                     blocking2d=self.blocking2d,
                                                     axis=axis)

        #self.sigScrolled.connect(self.imageItemContainer.onScroll)
        self.sigBlocksAppeared.connect(self.imageItemContainer.onBlocksAppear)
        self.sigBlocksDisappeared.connect(self.imageItemContainer.onBlocksDissappear)



        self.blockVisibility = numpy.zeros(len(self.blocking2d),dtype='bool')
        self.visibleBlocks = None
        self.setAcceptHoverEvents(True)

        self.viewerPos = [0,0,0] 

        self.color = [0,0,0]
        self.color[axis] = 255

        #proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        self.sigScrolled.connect(self.onScroll)

        self.sigXRangeChanged.connect(self.rangeChanged)
        self.sigYRangeChanged.connect(self.rangeChanged)

        # grid lines
        self.gridLines  = None
        self.addGridLines()

        # axis lines
        if self.axis == 0:
            color = ('b','g')
        if self.axis == 1:
            color = ('b','r')
        if self.axis == 2:
            color = ('g','r')

        self.hLine = AxisLine(orientation='h',size=self.shape2d()[0],color=color[0])
        self.vLine = AxisLine(orientation='v',size=self.shape2d()[1],color=color[1])
        self.hLine.setZValue(15)
        self.vLine.setZValue(15)
        self.addItem(self.hLine)
        self.addItem(self.vLine)

        # scale bar
        self.scale = pg.ScaleBar(size=3,width=10, suffix='* 2nm')
        self.scale.setParentItem(self)
        self.scale.anchor((1, 1), (1, 1), offset=(-20, -20))

        s = self.inputShape.spatialShape[self.axis] 
        p = self.viewerPos[self.axis]
        # coordinates
        self.coordinatesText = pg.TextItem("[%d / %d]"%(p, s),color=self.color)#, anchor=(0.5, -1.0))
        self.coordinatesText.setParentItem(self)


        # buttons
        
        self.button = PushRect()
        self.button.setParentItem(self)
        self.button.anchor((1,0),(1,0),offset=(-10,0))
        self.setShowScaleBar(True)

    def updateHLinePos(self, pos):
        self.hLine.setPos(0,pos)

    def updateVLinePos(self,pos):
        self.vLine.setPos(pos,0)

    def shape2d(self):
        sShape = self.inputShape.spatialShape
        s = sShape[0:self.axis] + sShape[self.axis+1:len(sShape)+1]
        return s
    def mouseClickEvent(self, p,double=False):
        if p.button() ==4 and p.double():
            pos = self.mapToView(p.pos())
            pos = (int(pos.x()),int(pos.y()))
            s2d = self.shape2d()
            print pos,s2d
            if pos[0]>=0 and pos[0] < s2d[0] and pos[1]>=0 and pos[1] < s2d[1]:
                self.sigMoveOtherViewers.emit(self.axis,pos)
                p.accept()

    def mouseDragEvent(self, ev, axis=None):

        kmods = ev.modifiers()
        if kmods & pg.QtCore.Qt.ControlModifier:
            super(BvGridViewBox,self).mouseDragEvent(ev, axis)

    def movedBy(self, axis, pos):
        if(axis==0): #'yz'
            if self.axis==1:
                self.sigScrolled.emit(pos[0])
            elif self.axis == 2:
                self.sigScrolled.emit(pos[1])

        elif axis == 1: #xz
            if self.axis==0:
                self.sigScrolled.emit(pos[0])
            elif self.axis == 2:
                self.sigScrolled.emit(pos[1])
        elif axis == 2: #xy
            if self.axis==0:
                self.sigScrolled.emit(pos[0])
            elif self.axis == 1:
                self.sigScrolled.emit(pos[1])
            
    def addPixelLayer(self, layer, name):
        self.imageItemContainer.addPixelLayer(layer, name)

    def setShowScaleBar(self,show):
        self.scale.setVisible(show)

    def setShowGridLines(self,show):
        self.gridLines.setVisible(show)
    def addGridLines(self):
        self.gridLines = GridLines(blocking2d=self.blocking2d)
        self.gridLines.setZValue(11)
        self.addItem(self.gridLines)

    def axisPos(self):
        return self.viewerPos[self.axis]

    def onScroll(self, newAxisPos):
        print "on scroll changed"
        self.viewerPos[self.axis]=newAxisPos
        s = self.inputShape.spatialShape[self.axis] 
        self.coordinatesText.setText("[%d / %d]"%(newAxisPos,s),color=self.color)
        self.imageItemContainer.onScroll(newAxisPos)
        self.update()

    def rangeChanged(self):
        print "range changed"
        rect =  self.viewRect()

        self.visibleBlocks =  self.blocking2d.iBlocks(rect)

        tmp = self.blockVisibility.copy()
        #print self.blockVisibility
        self.blockVisibility[:] = 0
        self.blockVisibility[self.visibleBlocks] = 1

        changingBlocks = numpy.where(tmp!=self.blockVisibility)[0]

        if(len(changingBlocks)>0):
            newState = self.blockVisibility[changingBlocks]
            self.sigBlocksAppeared.emit( changingBlocks[numpy.where(newState==1)] )
            self.sigBlocksDisappeared.emit( changingBlocks[numpy.where(newState==0)] )


        #print self.blockVisibility
    def wheelEvent(self, ev, axis=None):
        pz = numpy.array(self.viewPixelSize())
        print "pixelSize",pz
        f = 1
        kmods = ev.modifiers()
        if kmods & pg.QtCore.Qt.ShiftModifier:
            f=5
        if kmods & pg.QtCore.Qt.ControlModifier:
            super(BvGridViewBox,self).wheelEvent(ev, axis)
        else:
            d = (ev.delta() * self.state['wheelScaleFactor'])
            if d<0:
                d = 1*f
            else:
                d =-1*f
            currentPos = self.viewerPos[self.axis]
            newPos = currentPos + d
            s = self.inputShape.spatialShape[self.axis] 
            if newPos >=0 and newPos<s:
                axisPos=newPos
                self.coordinatesText.setText("[%d/%s]"%(axisPos,s))
                self.viewerPos[self.axis] = axisPos
                self.sigScrolled.emit(axisPos)

    def addBlockImageItems(self, blockImageItems):

        for imageItem in blockImageItems.imageItems:
            block = imageItem.block
            self.addItem(imageItem)

