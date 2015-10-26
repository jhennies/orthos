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
def yield2d(shape):
    for x in range(shape[0]):
        for y in range(shape[1]):
            yield (x,y)

            
class VisibleTiles(QtCore.QObject):

    sigTilesAppeared  = QtCore.Signal(object)
    sigTilesDisappeared  = QtCore.Signal(object)

    def __init__(self, tileGrid):
        super(VisibleTiles,self).__init__()
        self.tileGrid = tileGrid
        self.viewBox = tileGrid.viewBox
        sa = tileGrid.viewBox.scrollAxis 
        bi = tileGrid.blockingIndex
        self.tileGridShape = tileGrid.tileGridShape
        self.blocking2d = tileGrid.mlBlocking.blockings2d[sa][bi]
        self.blockShape = tileGrid.mlBlocking.blockShape2d(bi, sa)
        # connect viewbox on change 
        self.viewBox.sigRectChanged.connect(self.onViewBoxViewRectChanged)

        self.visibleBlocks = set()

    def onViewBoxViewRectChanged(self):
        minCoord, maxCoord = self.viewBox.integralViewBounds2()
        startBlockC = minCoord / self.blockShape
        endBlockC   = maxCoord / self.blockShape + 1
        nBlocks     = numpy.minimum(self.tileGridShape, endBlockC-startBlockC)
        newVisibleBlocks = set()
        for xy in yield2d(nBlocks):
            bi = int(xy[0]+startBlockC[0]),int(xy[1]+startBlockC[1])
            newVisibleBlocks.add(bi)
        
        appBlocks     = newVisibleBlocks - self.visibleBlocks
        dissAppBlocks = self.visibleBlocks - newVisibleBlocks
        self.visibleBlocks = newVisibleBlocks

        if len(self.visibleBlocks)>=25:
            print "nblocks",nBlocks
        if dissAppBlocks :
            self.tileGrid.onTilesDisappear(dissAppBlocks)
        if appBlocks :
            self.tileGrid.onTilesAppear(appBlocks)








class TileGrid(pg.ItemGroup):
    """ A GRid of TileItems
    """

    def __init__(self,viewBox,blockingIndex, tileGridShape):
        super(TileGrid,self).__init__()
        self.viewBox = viewBox
        self.blockingIndex = blockingIndex
        self.tileGridShape = tileGridShape
        self.mlBlocking = viewBox.navigator.mlBlocking
        
        self.scrollAxis = viewBox.scrollAxis
        self.mlBlocking = viewBox.navigator.mlBlocking
        self.tileShape = self.mlBlocking.blockShape2d(blockingIndex,self.scrollAxis)
        self.nTileItems = tileGridShape[0]*tileGridShape[1]
        self.tileItems = [TileItemGroup(self.tileShape,self) for i in range(self.nTileItems)]
        self.tileVisible_ = False
        # add all tile items to the group
        for tileItem in self.tileItems:
            tileItem.setPos(0,0)
            self.addItem(tileItem)


        # LAYERS 
        # connect the layer class with the tile grid
        self.layers = dict()
        self.viewBox.pixelLayers.sigPixelLayerAdded.connect(self.onAddLayer)
        self.viewBox.pixelLayers.sigPixelLayerRemoved.connect(self.onRemoveLayer)


        # mapping from a tile index to the corresponding tile item index
        self.tileBlockCoordToTileIndex = dict()
        self.freeTiles = set()
        for ti in range(self.nTileItems):
            self.freeTiles.add(ti)
        self.usedTiles = set()

        self.initialize()

    def initialize(self):
        self.visibleTiles = VisibleTiles(self)
        self.visibleTiles.sigTilesAppeared.connect(self.onTilesAppear)
        self.visibleTiles.sigTilesDisappeared.connect(self.onTilesDisappear)


    def onTilesAppear(self, tiles):
        self.tileVisible_ = True
        #print len(self.visibleTiles.visibleBlocks),self.nTileItems
        assert len(self.visibleTiles.visibleBlocks)<=self.nTileItems
        tileBlockCoordToTileIndex  = self.tileBlockCoordToTileIndex
        for tileBlockCoord in tiles:

            # nasty mappings
            assert tileBlockCoord not in self.tileBlockCoordToTileIndex
            #if len(self.freeTiles) ==0 :
            #    print self.usedTiles
            freeTileIndex = self.freeTiles.pop()
            assert freeTileIndex not in self.usedTiles
            freeTileItem = self.tileItems[freeTileIndex]
            self.usedTiles.add(freeTileIndex)
            self.tileBlockCoordToTileIndex[tileBlockCoord] = freeTileIndex


            freeTileItem.onTileAppear(tileBlockCoord)
            #print "tile item scale",freeTileItem.scale()

    def onTilesDisappear(self, tiles):
        self.tileVisible_ = False
        tileBlockCoordToTileIndex  = self.tileBlockCoordToTileIndex
        for tileBlockCoord in tiles:
            assert tileBlockCoord in self.tileBlockCoordToTileIndex
            usedTileIndex = self.tileBlockCoordToTileIndex.pop(tileBlockCoord)
            assert usedTileIndex in self.usedTiles
            assert usedTileIndex not in self.freeTiles
            usedTileItem = self.tileItems[usedTileIndex]
            self.usedTiles.remove(usedTileIndex)
            self.freeTiles.add(usedTileIndex)
            usedTileItem.onTileDisappear()

    def onAddLayer(self, layer):
        #print "tile item group add layer",layer.name()
        self.layers[layer.name()] = layer
        for tileItem in self.tileItems:
            tileGraphicItem = layer.makeTileGraphicsItem()
            tileGraphicItem.initialize(layer=layer,viewBox=self.viewBox,
                                       blockingIndex=self.blockingIndex)
            tileItem.addItemToTile(tileGraphicItem)
            #if self.tileVisible_ :
            #    self.
    def onRemoveLayer(self, layer):
        self.layers[layer.name()] = layer
        for tileItem in self.tileItems:
            assert  False
            #tileGraphicItem = layer.makeTileGraphicsItem()
            #tileItem.removeItemFromTile(tileGraphicItem)
        self.layers.pop(layer.name())

    def onScrollCoordinateChanged(self, coord):
        for tileBlockCoord in self.visibleTiles.visibleBlocks:
            assert tileBlockCoord in self.tileBlockCoordToTileIndex
            usedTileIndex = self.tileBlockCoordToTileIndex[tileBlockCoord]
            assert usedTileIndex in self.usedTiles
            assert usedTileIndex not in self.freeTiles
            usedTileItem = self.tileItems[usedTileIndex]
            usedTileItem.onScrollCoordinateChanged(coord)
            #print "tileBlockCoord",tileBlockCoord

class TileItemGroup(pg.ItemGroup):
    """ A Container of all Graphics Items in a single(!) 2d-tile
    """

    def __init__(self, tileShape,parent):
        super(TileItemGroup,self).__init__()
        self.tileShape = tileShape
        self.items = set()
        self.tileVisible_ = False
        self.blockCoord2d_ = None
    def addItemToTile(self, item):
        self.addItem(item)
        self.items.add(item)
        if self.tileVisible_:
            item.onTileAppear(self.blockCoord2d_)
    def removeItemFromTile(self, item):
        self.removeFromGroup(item)
        self.items.remove(item)

    def onTileAppear(self, gbi):
        self.tileVisible_ = True
        self.blockCoord2d_ = gbi
        for item in self.items:
            item.onTileAppear(gbi)
    def onTileDisappear(self):
        self.tileVisible_ = False
        for item in self.items:
            item.onTileDisappear()

    def onScrollCoordinateChanged(self, coord):
        """ called when scrolled (usually from mouse wheel events)
        """
        # inform all items
        for item in self.items:
            item.onScrollCoordinateChanged(coord)
            assert item.blockCoord is not None
    def onTimeCoordinateChanged(self, coord):
        """ called when current time point changes (usually time-widget)
        """
        for item in self.items:
            item.onTimeCoordinateChanged(coord)



