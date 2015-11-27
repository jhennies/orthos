import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import vigra
import numpy
#from blocking import *
from functools import partial
from  .. import *
from  ..infinite_line import *
from  infinite_grid_lines import *
from tile_item_group import *
from tile_grid import *

def axisColor(axis,val=200):
    c=[0,0,0]
    c[axis] =val
    return tuple(c)




class InfiniteBlockedViewBox(pg.ViewBox):

    #sigScrolled = QtCore.Signal(object)                         
    sigBlocksAppeared = QtCore.Signal(object)
    sigBlocksDisappeared = QtCore.Signal(object)
    sigMoveOtherViewers = QtCore.Signal(object, object)

    sigPixelSizeChanged = QtCore.Signal(object)
    sigRectChanged = QtCore.Signal(object)

    def __init__(self, navigator,pixelLayers,scrollAxis=2, viewAxis=[0,1], blockSizes=[128,256,512,1024,2048], 
                      minPixelSize=None, maxPixelSize=None):

        self.blockSizes = blockSizes
        self.pixelSizes = [1,2,4,8,16]

        self.imageItemDict = dict()
        for ps in self.pixelSizes:
            self.imageItemDict[ps] = dict()

        super(InfiniteBlockedViewBox,self).__init__(invertY=True,lockAspect=True)
        self.navigator = navigator
        self.pixelLayers = pixelLayers
        self.scrollAxis = scrollAxis
        self.viewAxis = viewAxis
        self.scrollCoordinate = 0
        self.timeCoordinate = 0
        
        sShape = navigator.spatialShape
        self.viewSpatialShape = (sShape[self.viewAxis[0]], sShape[self.viewAxis[1]] )
        self.setRange(xRange=(0,100),yRange=(0,100))

        self.setAspectLocked(True)
        self.setMenuEnabled(False)
        self.invertY(True)


        # buffer pixel size and view rect
        self.viewPixelSizeBuffer = None #self.viewPixelSize()
        self.viewRectBuffer = None #self.state['viewRange']

        # connect range changed events
        self.sigXRangeChanged.connect(self.rangeChanged)
        self.sigYRangeChanged.connect(self.rangeChanged)
        self.sigPixelSizeChanged.connect(self.onPixelSizeChanged)


        self.sigRectChanged.connect(self.rectChanged)

        self.minPixelSize = minPixelSize
        self.maxPixelSize = maxPixelSize



        
        # grid lines
        self.gridLines = InfiniteGridLines(self)
        self.addItem(self.gridLines,ignoreBounds=False)
        self.gridLines.setZValue(14)
        



        # new better tiling
        self.tileGrid = DynamicTileGrid(self,0,tileGridShape=(10,10))
        self.staticTileGrid = StaticTileGrid(self,0)
        
        self.addItem(self.tileGrid)
        #self.addItem(self.staticTileGrid)
        #navigation lines
        self.axis0Line = InfiniteLine(movable=True, angle=90,pen=pg.mkPen(color=axisColor(viewAxis[0]),width=3),
                                      bounds=[0,self.viewSpatialShape[0]-1]) 
        self.axis1Line = InfiniteLine(movable=True, angle=0 ,pen=pg.mkPen(color=axisColor(viewAxis[1]),width=3),
                                      bounds=[0,self.viewSpatialShape[1]-1])
        self.axis0Line.setZValue(15)
        self.axis1Line.setZValue(15)


        def a0Changed(line):
            v = int(line.value()+0.5)
            self.navigator.changedPlane(self.viewAxis[0],v,self.axis0Line)
        def a1Changed(line):
            v = int(line.value()+0.5)
            self.navigator.changedPlane(self.viewAxis[1],v)
        self.axis0Line.sigPositionChanged.connect(a0Changed)
        self.axis1Line.sigPositionChanged.connect(a1Changed)


        self.addItem(self.axis0Line, ignoreBounds=True)
        self.addItem(self.axis1Line, ignoreBounds=True)


        self.bestBlockIndex = None 


    def findBestBlockIndex(self):
        bestBlockIndex = 0
        ps =self.viewPixelSize()[0]
        if ps < 2.0:
            bestBlockIndex = 0
        else:
            for i,(blockPixelSize,bz) in enumerate(zip(self.pixelSizes,self.blockSizes)):

                if i == len(self.blockSizes)-1:
                    bestBlockIndex = i 
                    break
                if ps >= blockPixelSize and ps < self.pixelSizes[i+1]:
                    bestBlockIndex = i
                    break
        return bestBlockIndex



    # range change events
    def rangeChanged(self,*args,**kwargs):
        #print "rect buffer",self.viewRectBuffer
        #print "ps   buffer",self.viewPixelSizeBuffer

        #try:
        if self.viewPixelSizeBuffer is None:
            self.viewPixelSizeBuffer = [ round(x,8) for x in self.viewPixelSize()]
            self.sigPixelSizeChanged.emit(self.viewPixelSizeBuffer)
        else:
            pz = [ round(x,8) for x in self.viewPixelSize()]
            if pz != self.viewPixelSizeBuffer:
                self.viewPixelSizeBuffer = pz
                self.sigPixelSizeChanged.emit(self.viewPixelSizeBuffer)

        if self.viewRectBuffer is None:
            #print "buffer is NOne",self.scrollAxis
            self.viewRectBuffer = numpy.array(self.state['viewRange'])
            assert self.viewRectBuffer.shape == (2,2)
            self.sigRectChanged.emit(self.viewRectBuffer)
        else:
            assert self.viewRectBuffer.shape == (2,2)
            #print "WE HAVE BUFFER",self.scrollAxis
            vr = numpy.array(self.state['viewRange'])
            vrr = numpy.round(vr,5)
            assert self.viewRectBuffer.shape == (2,2)
            vrbr = numpy.round(self.viewRectBuffer,5)
            assert vrbr.shape == (2,2)
            if numpy.allclose(vrr,vrbr) == False:
                #print "chages"
                self.viewRectBuffer = vr
                assert self.viewRectBuffer.shape == (2,2)
                self.sigRectChanged.emit(self.viewRectBuffer)


    def integralViewBounds2(self):
        vrx = numpy.round(self.state['viewRange'][0],0).astype('int64')
        vry = numpy.round(self.state['viewRange'][1],0).astype('int64')
        minCoord = numpy.array([vrx[0],vry[0]])
        maxCoord = numpy.array([vrx[1],vry[1]])
        minCoord[0] = max(0,minCoord[0])
        minCoord[1] = max(0,minCoord[1])
        maxCoord[0] = min(self.viewSpatialShape[0],maxCoord[0])
        maxCoord[1] = min(self.viewSpatialShape[1],maxCoord[1])
        return minCoord, maxCoord


    def make3DCoordinate(self, coord, scrollOffset=0):
        coord3d = [0,0,0]
        coord3d[self.scrollAxis] = self.scrollCoordinate + scrollOffset
        coord3d[self.viewAxis[0]] = coord[0]
        coord3d[self.viewAxis[1]] = coord[1]
        return coord3d

    def get2dBlocking(self,blockingIndex):
        return self.navigator.mlBlocking.blockings2d[self.scrollAxis][blockingIndex]
    def onPixelSizeChanged(self, pz):
        self.bestBlockIndex = self.findBestBlockIndex()
        #print "best index",self.bestBlockIndex
    
    def changeScrollCoordinate(self, newScrollCoordinate):
        self.scrollCoordinate = newScrollCoordinate
        self.tileGrid.onScrollCoordinateChanged(newScrollCoordinate)

    def onTimeChanged(self, newTime):
        self.timeCoordinate = newTime
        self.tileGrid.onTimeCoordinateChanged(newTime)

    def rectChanged(self, vr):
        pass


    def mouseClickEvent(self, ev, double=False):
        pos = self.mapToView(ev.pos())
        pos = pos.x(),pos.y()
        s2d = self.viewSpatialShape
        if pos[0] >=0.0 and pos[0]<s2d[0] and  pos[1] >=0.0 and pos[1]<s2d[0] :
            if ev.button() ==QtCore.Qt.MiddleButton and ev.double():
                ev.accept()
                self.navigator.change2PlanesByDoubleClick(self.viewAxis, (int(pos[0]), int(pos[1]) ) )
            else:
                print "click in viewBox"
                self.pixelLayers.mouseClickEvent(ev=ev, pos2d=pos, clickedViewBox=self)

    def mouseDragEvent(self, ev, axis=None):
        kmods = ev.modifiers()
        if kmods & pg.QtCore.Qt.ControlModifier and ev.button() == QtCore.Qt.LeftButton:
            super(InfiniteBlockedViewBox,self).mouseDragEvent(ev, axis)

    def wheelEvent(self, ev, axis=None):     
        f = 1
        kmods = ev.modifiers()
        if kmods & pg.QtCore.Qt.ShiftModifier:
            f=5
        if kmods & pg.QtCore.Qt.ControlModifier:
            p = numpy.array(self.viewPixelSize())
            zoomIn = ev.delta() > 0
            doZoom = True
            if zoomIn and self.minPixelSize is not None:
                if p[0]<self.minPixelSize[0] or p[1]<self.minPixelSize[1]:
                    doZoom = False
            if not zoomIn and self.maxPixelSize is not None:
                if p[0]>self.maxPixelSize[0] or p[1]>self.maxPixelSize[1]:
                    doZoom = False
            if doZoom:
                super(InfiniteBlockedViewBox,self).wheelEvent(ev, axis)
        else:
            pass
            d = (ev.delta() * self.state['wheelScaleFactor'])
            if d<0:
                d = 1*f
            else:
                d =-1*f
            newCoord = self.scrollCoordinate + d
            newCoord = max(0,newCoord)
            if newCoord != self.scrollCoordinate:
                self.scrollCoordinate = newCoord
                self.navigator.changedPlane(self.scrollAxis,self.scrollCoordinate)

