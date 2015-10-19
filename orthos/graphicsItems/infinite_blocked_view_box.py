import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import vigra
import numpy
#from blocking import *
from functools import partial
from  infinite_grid_lines import *


def axisColor(axis):
    c=[0,0,0]
    c[axis] =255
    return c


class InfiniteBlockedViewBox(pg.ViewBox):


    sigScrolled = QtCore.Signal(object)                         
    sigBlocksAppeared = QtCore.Signal(object)
    sigBlocksDisappeared = QtCore.Signal(object)
    sigMoveOtherViewers = QtCore.Signal(object, object)

    sigPixelSizeChanged = QtCore.Signal(object)
    sigRectChanged = QtCore.Signal(object)

    def __init__(self, scrollAxis=2, viewAxis=[0,1], blockSizes=[128,256,512,1024,2048], 
                      minPixelSize=None, maxPixelSize=None):


        super(InfiniteBlockedViewBox,self).__init__(invertY=True,lockAspect=True)
        
        self.scrollAxis = scrollAxis
        self.viewAxis = viewAxis
        self.scrollCoordinate = 0
        self.blockSizes = blockSizes
        self.pixelSizes = [1,2,4,8,16]

        self.setRange( xRange=(0,1000),yRange=(0,1000), disableAutoRange=True)
        self.setAspectLocked(True)
        self.setMenuEnabled(False)
        self.invertY(True)


        # buffer pixel size and view rect
        self.viewPixelSizeBuffer = None #self.viewPixelSize()
        self.viewRectBuffer = None #self.viewRect()

        # connect range changed events
        self.sigXRangeChanged.connect(self.rangeChanged)
        self.sigYRangeChanged.connect(self.rangeChanged)
        self.sigPixelSizeChanged.connect(self.onPixelSizeChanged)


        self.minPixelSize = minPixelSize
        self.maxPixelSize = maxPixelSize



        
        # grid lines
        self.gridLines = InfiniteGridLines(self,blockSizes=self.blockSizes)
        self.addItem(self.gridLines)

        #navigation lines
        self.axis0Line = pg.InfiniteLine(movable=True, angle=90,pen=pg.mkPen(color=axisColor(viewAxis[0]),width=3))
        self.axis1Line = pg.InfiniteLine(movable=True, angle=0 ,pen=pg.mkPen(color=axisColor(viewAxis[1]),width=3))

        def fo():
            print self.axis0Line.pos()
        self.axis0Line.sigPositionChanged.connect(fo)

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

        if self.viewPixelSizeBuffer is None:
            self.viewPixelSizeBuffer = [ round(x,8) for x in self.viewPixelSize()]
            self.sigPixelSizeChanged.emit(self.viewPixelSizeBuffer)
        else:
            pz = [ round(x,8) for x in self.viewPixelSize()]
            if pz != self.viewPixelSizeBuffer:
                self.viewPixelSizeBuffer = pz
                self.sigPixelSizeChanged.emit(self.viewPixelSizeBuffer)

        if self.viewRectBuffer is None:
            self.viewRectBuffer = self.viewRect()
            self.sigRectChanged.emit(self.viewRectBuffer)
        else:
            vr = self.viewRect()
            if vr != self.viewPixelSizeBuffer:
                #print "changed rect"
                self.viewRectBuffer =vr
                self.sigRectChanged.emit(self.viewRectBuffer)


    def onPixelSizeChanged(self, pz):
        self.bestBlockIndex = self.findBestBlockIndex()
        print "best index",self.bestBlockIndex
    
    def changeScrollCoordinate(self, newScrollCoordinate):
        self.scrollCoordinate = newScrollCoordinate


    def onExternalAxisLineChanged(self, arg):
        self.changeScrollCoordinate(arg.value())
        self.sigScrolled.emit(arg.value())



    def rectChanged(self, vr):
        print "rect changed"



    # events from user
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
            self.scrollCoordinate +=d
            self.changeScrollCoordinate(self.scrollCoordinate)
            self.sigScrolled.emit(self.scrollCoordinate)




if __name__ == "__main__":
    import numpy as np
    from pyqtgraph.Qt import QtGui, QtCore
    import pyqtgraph as pg

    app = QtGui.QApplication([])
    mw = QtGui.QMainWindow()
    mw.setWindowTitle('pyqtgraph example: ViewBox')
    mw.show()
    mw.resize(800, 600)

    gv = pg.GraphicsView()
    mw.setCentralWidget(gv)
    l = QtGui.QGraphicsGridLayout()
    l.setHorizontalSpacing(0)
    l.setVerticalSpacing(0)

    vb = InfiniteBlockedViewBox(minPixelSize=(0.1,0.1),maxPixelSize=(10,10))

    # img = pg.ImageItem(border='w')
    # data = np.random.normal(size=(600, 600)).astype(np.uint8)
    # img.setImage(data)
    # vb.addItem(img)

    xScale = pg.AxisItem(orientation='bottom', linkView=vb)
    l.addItem(xScale, 1, 1)
    yScale = pg.AxisItem(orientation='left', linkView=vb)
    l.addItem(yScale, 0, 0)

    l.addItem(vb, 0, 1)



    #vb2 = InfiniteBlockedViewBox(minPixelSize=(0.1,0.1),maxPixelSize=(10,10))
    #l.addItem(vb2, 2, 0)


    gv.centralWidget.setLayout(l)

    ## Start Qt event loop unless running in interactive mode.
    if __name__ == '__main__':
        import sys
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
