import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


def yield2d(shape):
    for x in range(shape[0]):
        for y in range(shape[1]):
            yield x,y

            
class VisibleBlocks(QtCore.QObject):

    sigBlocksAppeared  = QtCore.Signal(object)
    sigBlocksDisappeared  = QtCore.Signal(object)

    def __init__(self, viewBox, blockSize, nBlocks):
        super(VisibleBlocks,self).__init__()
        self.viewBox = viewBox
        self.blockSize = blockSize
        self.nBlocks = nBlocks
        self.nTotalBlocks = nBlocks[0]*nBlocks[1]
        self.visibleBlocks = set()

    def getBlockCoords(self, minCoord, maxCoord):
        startBlockCoord = minCoord/self.blockSize
        stopBlockCoord= maxCoord/self.blockSize + 1
        for i in range(2):
            stopBlockCoord[i] = min(stopBlockCoord[i],startBlockCoord[i]+self.nBlocks[i])
        return startBlockCoord, stopBlockCoord

    def onViewRectChanged(self):
        blockSize = self.blockSize
        pixSize =  self.viewBox.viewPixelSize()
        minCoord, maxCoord = self.viewBox.integralViewBounds(noZeroMin=True)
        #print "       MIN MAX",minCoord,maxCoord
        if maxCoord[0]<=0 or maxCoord[1]<=0:
            d =  set(self.visibleBlocks)
            self.visibleBlocks.clear()
            self.sigBlocksDisappeared.emit(d)
        else:
            startBC, stopBC = self.getBlockCoords(minCoord,maxCoord)
            nBlocks  = stopBC - startBC
            newVisibleBlocks = set()
            for bix,biy in yield2d(nBlocks):
                localBC  = bix,biy
                globalBC = bix+startBC[0],biy+startBC[1]
                newVisibleBlocks.add(globalBC)

            dissapeared = self.visibleBlocks - newVisibleBlocks
            appeared = newVisibleBlocks - self.visibleBlocks
            if(len(dissapeared)>0):
                self.sigBlocksDisappeared.emit(dissapeared)
            if(len(appeared)>0):
                self.sigBlocksAppeared.emit(appeared)
            self.visibleBlocks = newVisibleBlocks
