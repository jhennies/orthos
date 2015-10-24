from collections import deque
import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import threading
import datetime
import time
import collections
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
            else:
                self.setVisible(False)
        else:
            self.setVisible(False)
    def onChangeTileVisible(self, visible):
        self.tileVisible_ = visible
        if visible :
            if self.layerVisible_:
                self.setVisible(True)
            else:
                self.setVisible(False)
        else:
            self.setVisible(False)


    @property
    def timeCoordinate(self):
        return self.viewBox.timeCoordinate
    

    def make3dSlicingAndBlockBegin(self):
        assert self.isInit
        blockBegin, blockEnd = self.blocking2d[self.blockCoord]
        begin3d = self.viewBox.make3DCoordinate(blockBegin)
        end3d = self.viewBox.make3DCoordinate(blockEnd,1)
        return make3dSlicing_(begin3d, end3d),blockBegin,blockEnd

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

