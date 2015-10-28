import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from operator import mul

import orthos_cpp






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
        
  

        # cpp 
        blocking2d = self.mlBlocking.blockings2d[self.viewBox.scrollAxis][blockingIndex]
        self.tileGridManager = orthos_cpp.TileGridManager(blocking2d,tileGridShape, self.viewBox.scrollAxis, self.viewBox.viewAxis)
        self.viewBox.sigRectChanged.connect(self.onViewBoxViewRectChanged)
        self.tileItems = [TileItemGroup(self.tileShape,self,self.tileGridManager.tileInfo(i)) for i in range(self.nTileItems)]


        # add all tile items to the group
        for i,tileItem in enumerate(self.tileItems):
            tileItem.setPos(0,0)
            self.addItem(tileItem)

        # LAYERS 
        # connect the layer class with the tile grid
        self.layers = dict()
        self.viewBox.pixelLayers.sigPixelLayerAdded.connect(self.onAddLayer)
        self.viewBox.pixelLayers.sigPixelLayerRemoved.connect(self.onRemoveLayer)



    def onViewBoxViewRectChanged(self):
        minCoord, maxCoord = self.viewBox.integralViewBounds2()
        a,d = self.tileGridManager.updateCurrentRoi(minCoord, maxCoord)
        self.onTilesDisappear(d)
        self.onTileAppear(a)
        

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
            tileItem.addLayer(layer.name(),tileGraphicItem)
            #if self.tileVisible_ :
            #    self.
    def onRemoveLayer(self, layer):
        self.layers[layer.name()] = layer
        for tileItem in self.tileItems:
            tileItem.removeLayer(layer.name())
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
            #
    def yieldVisibleTileItems(self,roi=None):
        if roi is None:
            for tileBlockCoord in self.visibleTiles.visibleBlocks:
                tileIndex =  self.tileBlockCoordToTileIndex[tileBlockCoord]
                tileItem = self.tileItems[tileBlockCoord]
                yield tileItem
        else:
            raise RuntimeError("not yet implemented")


    def yieldVisibleLayerItem(self, layerName,  roi=None):
        for visibleTilesItem in self.yieldVisibleTileItems(roi=roi):
            yield visibleTilesItem[layerName]









class TileItemGroup(pg.ItemGroup):
    """ A Container of all Graphics Items in a single(!) 2d-tile
    """

    def __init__(self, tileShape,parent, tileInfo):
        self.tileInfo = tileInfo
        super(TileItemGroup,self).__init__()
        self.tileShape = tileShape
        self.items = dict()
        self.tileVisible_ = False
        self.blockCoord2d_ = None

    def __getitem__(self, layerName):
        return self.items[layerName]


    @property
    def tileVisible(self):
        return self.tileInfo.tileVisible
    @property
    def roi2d(self):
        return self.tileInfo.roi2d
    @property
    def roi3d(self):
        return self.tileInfo.roi3d
    @property
    def scrollCoordinate(self):
        return self.tileInfo.scrollCoordinate
    @property
    def timeCoordinate(self):
        return self.tileInfo.timeCoordinate



    def addLayer(self,name, item):
        self.addItem(item)
        self.items[name]=item
        if self.tileVisible_:
            item.onTileAppear(self.blockCoord2d_)
    def removeLayer(self,name):
        self.removeFromGroup(item)
        self.items.pop(item)

    def onTileAppear(self, gbi):
        self.tileVisible_ = True
        self.blockCoord2d_ = gbi
        for layerName in self.items:
            self.items[layerName].onTileAppear(gbi)
    def onTileDisappear(self):
        self.tileVisible_ = False
        for layerName in self.items:
            self.items[layerName].onTileDisappear()

    def onScrollCoordinateChanged(self, coord):
        """ called when scrolled (usually from mouse wheel events)
        """
        # inform all items
        for layerName in self.items:
            self.items[layerName].onScrollCoordinateChanged(coord)
            assert self.items[layerName].blockCoord is not None
    def onTimeCoordinateChanged(self, coord):
        """ called when current time point changes (usually time-widget)
        """
        for layerName in self.items:
            self.items[layerName].onTimeCoordinateChanged(coord)



