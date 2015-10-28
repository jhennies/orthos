from collections import deque
import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import threading
import datetime
import time
import collections
import vigra
from ....core import *
def make3dSlicing_(begin,end):
    slicing = []
    for b,e in zip(begin, end):
        slicing.append(slice(b,e))
    return slicing






class UpdateQueue(QtCore.QObject):
    sigUpdateFinished  = QtCore.Signal(object)
    def __init__(self,item):
        super(UpdateQueue,self).__init__()

        self.futuresLock = threading.Lock()  
        self.item = item
        self.sigUpdateFinished.connect(self.item.onUpdateFinished)
        self.futures = []

    def addFuture(self, newFuture):
        #self.futuresLock.acquire()
        stillRunning = [ ]
        # check all existing futures and remove finished ones
        # and try to cancel all others
        for i in range(len(self.futures)):
            future = self.futures[i]
            if future.done():
                pass
            else:
                # try to cancel
                isCanceled = future.cancel()
                if not isCanceled:
                    stillRunning.append(future)
        stillRunning.append(newFuture)
        self.futures = stillRunning
        #self.futuresLock.release()

class TileItemMixIn(object):
    def __init__(self):
        super(TileItemMixIn, self).__init__()
        self.updateQueue = UpdateQueue(self)
        self.layer = None
        self.viewBox = None
        self.blockingIndex = None
        self.blockCoord = (0,0)
        self.blockings2d = None
        self.isInit = False

        self.tileVisible_ = False 
        self.layerVisible_ = True

    def initialize(self, layer, viewBox, blockingIndex):
        self.isInit = True
        self.layer = layer
        self.viewBox = viewBox
        self.blockingIndex = blockingIndex
        self.blocking2d = viewBox.get2dBlocking(blockingIndex)
    def onTileAppear(self, blockCoord):
        self.onChangeTileVisible(True)
        assert self.isInit
        self.blockCoord = blockCoord 
        self.layer.onTileAppear(self)
    def blockBeginEnd(self):
        b = self.blocking2d[self.blockCoord]
        return b.begin,b.end
    def onScrollCoordinateChanged(self, coord):
        self.layer.onTileScrollCoordinateChanged(self,coord)
    def onTileDisappear(self):
        self.onChangeTileVisible(False)
        self.layer.onTileDisappear(self)

    def onChangeLayerVisible(self, visible):
        self.layerVisible_ = visible
        if visible:
            if self.tileVisible_:
                self.setVisible(True)
                self.setEnabled(True)
            else:
                self.setVisible(False)
                self.setEnabled(False)
        else:
            self.setVisible(False)
            self.setEnabled(False)
    def onChangeTileVisible(self, visible):
        self.tileVisible_ = visible
        if visible :
            if self.layerVisible_:
                self.setVisible(True)
                self.setEnabled(True)
            else:
                self.setVisible(False)
                self.setEnabled(False)
        else:
            self.setVisible(False)
            self.setEnabled(False)

    def tileVisible(self):
        return self.tileVisible_

    @property
    def timeCoordinate(self):
        return self.viewBox.timeCoordinate
    

    def make3dSlicingAndBlockBegin(self):
        assert self.isInit
        block = self.blocking2d[self.blockCoord]
        blockBegin, blockEnd = block.begin,block.end
        begin3d = self.viewBox.make3DCoordinate(blockBegin)
        end3d = self.viewBox.make3DCoordinate(blockEnd,1)
        return make3dSlicing_(begin3d, end3d),blockBegin,blockEnd

    def shape2d(self):
        block = self.blocking2d[self.blockCoord]
        blockBegin, blockEnd = block.begin,block.end
        return tuple([e-b for e,b in zip(blockEnd,blockBegin)])


class TileImageItem(pg.ImageItem, TileItemMixIn):

    def __init__(self, *args, **kwargs):

        self.setNewImageLock = threading.Lock()  
        BaseImageItem = pg.ImageItem
        BaseImageItem.__init__(self, *args, **kwargs)   
        TileItemMixIn.__init__(self)
        self.lastStemp = time.clock()
        self.newImgDict = dict()
    def onUpdateFinished(self, updateData):
        #print "update finished",updateData.pos
        ts = updateData.ts
        #print ts
        #print "own ts",self.lastStemp,"update ts",ts
        if ts >= self.lastStemp:
            #print "FRESH UPDATE"
            self.setNewImageLock.acquire()
            self.setPos(*updateData.pos)
            self.lastStemp = ts
            newImg = self.newImgDict.pop(ts)
            self.setImage(newImg,levels=self.layer.levels)
            #print self.levels
            self.setNewImageLock.release()
        else:
            self.setNewImageLock.acquire()
            self.newImgDict.pop(ts)
            self.setNewImageLock.release()

    def setImageToUpdateFrom(self, newImage, ts):
        self.setNewImageLock.acquire()
        self.newImgDict[ts] = newImage.copy()
        self.setNewImageLock.release()

    def mouseClickEvent(self, ev, double=False):
        print "click in image",ev.pos()



class TilePaintImage(pg.ImageItem, TileItemMixIn):

    def __init__(self, *args, **kwargs):

        self.labelColors = kwargs.pop('labelColors')

        self.setNewImageLock = threading.Lock()  
        BaseImageItem = pg.ImageItem
        BaseImageItem.__init__(self, *args, **kwargs)   
        TileItemMixIn.__init__(self)
        self.lastStemp = time.clock()
        self.newImgDict = dict()
        self.label = 1 
        self.brushRad = 0
        self.pathX = []
        self.pathY = []
        self.pathItem = pg.PlotCurveItem()
        

    def initialize(self, layer, viewBox, blockingIndex):
        TileItemMixIn.initialize(self,layer,viewBox,blockingIndex)
        self.viewBox.addItem(self.pathItem)

    def onLabelChanged(self, label):
        self.label = label
        c = self.labelColors[self.label]


    def onBrushSizeChanged(self, brushRad):
        self.brushRad = brushRad
        c = self.labelColors[self.label]
        


    def onUpdateFinished(self, updateData):
        #print "update finished",updateData.pos
        ts = updateData.ts
        #print ts
        #print "own ts",self.lastStemp,"update ts",ts
        if ts >= self.lastStemp:
            #print "FRESH UPDATE"
            self.setNewImageLock.acquire()
            self.setPos(*updateData.pos)
            self.lastStemp = ts
            newImg = self.newImgDict.pop(ts)
            #print "DO THE UPDATE"
            self.setImage(newImg)#,levels=(0,255))
            #print self.levels
            self.setNewImageLock.release()
        else:
            self.setNewImageLock.acquire()
            self.newImgDict.pop(ts)
            self.setNewImageLock.release()

    def setImageToUpdateFrom(self, newImage, ts):
        self.setNewImageLock.acquire()
        self.newImgDict[ts] = newImage.copy()
        self.setNewImageLock.release()

    #def mousePressEvent(self, ev):
    #    print "PRESS PAINT"
    #    ev.accept()

    def mouseClickEvent(self, ev, double=False):
        print "click in paint",ev.pos()
    #    self.image[pos[0],pos[1],0:4] = 255 
    #    self.updateImage(self.image)


    def mouseDragEvent(self, ev, axis=None):
        kmods = ev.modifiers()
        s2d = self.shape2d()
        if  ev.button() == QtCore.Qt.LeftButton and (kmods == pg.QtCore.Qt.NoModifier): #and (noShift and noCtrl):
            
            pos = ev.pos()
            begin,end = self.blockBeginEnd()
            pos = pos.x()+begin[0],pos.y()+begin[1]
            
            print pos
            if True:#pos[0]>=0 and pos[0]<s2d[0] and pos[1]>=0 and pos[1]<s2d[1]:
                ev.accept()

                c = self.labelColors[self.label]
                w = (self.brushRad*2+1)/self.viewBox.viewPixelSize()[0]
                self.pathItem.setPen(pg.mkPen(color=c,width=w))

                if not ev.isFinish():
                    if len(self.pathX)==0:
                        print "first click"
                    print len(self.pathX)

                    self.pathX.append(pos[0])
                    self.pathY.append(pos[1])
                    #self.image[pos[0],pos[1],0:4] = 255 
                    #self.updateImage(self.image)
                    
                    
                    self.pathItem.updateData(x=numpy.array(self.pathX), y=numpy.array(self.pathY))

                else:
                    self.makeArrayFromPath()
                    self.pathX = []
                    self.pathY = []
                    self.pathItem.updateData()


    def makeArrayFromPath(self):
        begin,end = self.blockBeginEnd()

        npx = numpy.array(self.pathX)
        npy = numpy.array(self.pathY)

        self.pathX = []
        self.pathY = []
        self.pathItem.updateData()



        linSpace = numpy.linspace

        startCoord = numpy.floor(numpy.array([numpy.min(npx),numpy.min(npy)])).astype('int64')
        stopCoord  = numpy.round(numpy.array([numpy.max(npx)+1,numpy.max(npy)+1]),0).astype('int64')



        shape = stopCoord - startCoord
        shape = [int(s) for s in shape]
        shape3d = [1,1,1]
        shape3d[self.viewBox.viewAxis[0]] = int(shape[0])
        shape3d[self.viewBox.viewAxis[1]] = int(shape[1])

        start3d = [0,0,0]
        start3d[self.viewBox.viewAxis[0]] = int(startCoord[0])
        start3d[self.viewBox.viewAxis[1]] = int(startCoord[1])
        start3d[self.viewBox.scrollAxis]  = int(self.viewBox.scrollCoordinate)

        labelsBlock = numpy.zeros(shape,'uint8')

        for i in range(len(npx)-1):
            #print i
            x0,y0 = npx[i],npy[i]
            x1,y1 = npx[i+1],npy[i+1]
            dist = numpy.sqrt( (x0-x1)**2 + (y0-y1)**2)
            num = max(int(dist +0.5),1)
            #print "NUM:",dist
            

            x, y = linSpace(x0, x1, num), linSpace(y0, y1, num)
            x = numpy.floor(x).astype('uint64')
            y = numpy.floor(y).astype('uint64')
            x -= startCoord[0]
            y -= startCoord[1]
            labelsBlock[x,y] = 1

        dLabels = vigra.filters.discDilation(labelsBlock, self.brushRad)

        # make draw kernel
    
        drawKernel = numpy.ones((2*self.brushRad+1,)*2,dtype='uint8')
        drawKernel = sector_mask(self.brushRad)
        print drawKernel
        print "DRAW KERNEL SHAPE",drawKernel.shape
        resultLabels = applyDrawKernel(labelsBlock, drawKernel)




        if self.label != 0:
            resultLabels *=self.label
        else:
            resultLabels *=255
        labelsBlock = resultLabels.reshape(shape3d)
        #print "LABELS MAX IN BLOCK",labelsBlock.max()
        self.layer.writeLabelsToDataSource(labelsBlock, start3d)
