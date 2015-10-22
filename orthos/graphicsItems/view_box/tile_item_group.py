import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from operator import mul


def iYield2d(shape):
    i = 0 
    for x in range(shape[0]):
        for y in range(shape[1]):
            yield i,(x,y)
            i +=1

class TileGrid(QtGui.QGraphicsItemGroup):
    """ A GRid of TileItems
    """

    def __init__(self, tileGridShape, tileShape):
        super(QtGui.TileGrid,self).__init__()
        self.tileGridShape = tileGridShape 
        self.tileShape = tileShape
        self.nTileItems = reduce(tileGridShape,mul)

        self.tileItems = [TileItem(tileShape) for i in self.nTileItems]
        self.gridToItemIndex = numpy.empty(tileGridShape,dtype='int32')
        self.visibleTiles = numpy.zeros(tileGridShape,dtype='bool')
        # make that faster ? (most probably not a bottleneck)
        for (i,(x,y)) in iYield2d(tileGridShape):
            self.gridToItemIndex[x,y] = i


        


class TileItem(QtGui.QGraphicsItemGroup):
    """ A Container of all Graphics Items in a Tile
    """

    def __init__(self, tileShape):
        super(QtGui.TileItem,self).__init__()
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
        assert self.pos is not None:
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
            assert self.pos is not None:
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
            item.onTimeCoordinateChanged(coord

    def boundingRect(self):
        if pos is not None:
            QtCore.QRectF(self.pos[0],self.pos[1],self.tileShape[0],self.tileShape[1])
        else:
            return QtCore.QRectF():
