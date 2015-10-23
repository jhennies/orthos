import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from operator import mul


def iYield2d(shape):
    i = 0 
    for x in range(shape[0]):
        for y in range(shape[1]):
            yield i,(x,y)
            i +=1








            
class VisibleTiles(QtCore.QObject):

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









class TileGrid(QtGui.QGraphicsItemGroup):
    """ A GRid of TileItems
    """

    def __init__(self,viewBox,blockingIndex, tileGridShape):


        super(TileGrid,self).__init__()
        self.scrollAxis = viewBox.scrollAxis
        self.mlBlocking = viewBox.navigator.mlBlocking
        self.tileGridShape = tileGridShape 
        self.tileShape = self.mlBlocking.blockShape2d(blockingIndex,self.scrollAxis)
        self.nTileItems = tileGridShape[0]*tileGridShape[1]

        self.tileItems = [TileItem(self.tileShape) for i in range(self.nTileItems)]
        self.gridToItemIndex = numpy.empty(tileGridShape,dtype='int32')
        self.visibleTiles = numpy.zeros(tileGridShape,dtype='bool')
        # make that faster ? (most probably not a bottleneck)
        for (i,(x,y)) in iYield2d(tileGridShape):
            self.gridToItemIndex[x,y] = i


        


class TileItem(QtGui.QGraphicsItemGroup):
    """ A Container of all Graphics Items in a Tile
    """

    def __init__(self, tileShape):
        super(TileItem,self).__init__()
        self.tileShape = tileShape
        self.items = set()
        self.pos = None
        self.isVisibleTile = None
    def addItemToTile(self, item):
        self.addToGroup(item)
        self.items.add(item)
    def removeItemFromTile(self, item):
        self.removeFromGroup(item)
        self.items.remove(item)



    def setTileVisibility(self, visible):
        assert self.pos is not None
        if visible !=self.isVisibleTile:
            self.isVisibleTile = visible
            self.onTileVisibilityChanged(visible)
    def onTileAppear(self, pos):
        self.pos = pos
        if not self.isVisibleTile:
            self.onTileVisibilityChanged(True)
    def onTileDisappear(self):
        self.pos = None
        if self.isVisibleTile:
            self.onTileVisibilityChanged(False)
    def onTileVisibilityChanged(self, visible):
        if visible:
            assert self.pos is not None
        self.isVisibleTile  = visible
        self.setEnabled(visible)
        self.setVisible(visible)
        for item in self.items:
            item.onTileVisibilityChanged(visible)

    def onScrollCoordinateChanged(self, coord):
        """ called when scrolled (usually from mouse wheel events)
        """
        # inform all items
        for item in self.items:
            item.onScrollCoordinateChanged(coord)
    def onTimeCoordinateChanged(self, coord):
        """ called when current time point changes (usually time-widget)
        """
        for item in self.items:
            item.onTimeCoordinateChanged(coord)

    def boundingRect(self):
        if pos is not None:
            QtCore.QRectF(self.pos[0],self.pos[1],self.tileShape[0],self.tileShape[1])
        else:
            return QtCore.QRectF()
