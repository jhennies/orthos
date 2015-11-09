import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from operator import mul

import orthos_cpp
from tile_item_group import *



class DynamicTileGrid(pg.ItemGroup):
    """ A GRid of TileItems
    """

    def __init__(self,viewBox,blockingIndex, tileGridShape):
        super(DynamicTileGrid,self).__init__()
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
        self.tileItems = [TileItemGroup(self.viewBox, self.tileGridManager.tileInfo(i)) for i in range(self.nTileItems)]


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
        aTiles,dTiles = self.tileGridManager.updateCurrentRoi(minCoord, maxCoord)
        if(len(dTiles)>0):
            #print "dTiles",dTiles
            self.onTilesDisappear(dTiles)

        if(len(aTiles)>0):
            #print "atiles",aTiles
            self.onTilesAppear(aTiles)

    def onAddLayer(self, layer):
        #print "tile item group add layer",layer.name()
        self.layers[layer.name()] = layer
        for tileItem in self.tileItems:
            tileGraphicItem = layer.makeTileGraphicsItem(layer=layer,tileItemGroup=tileItem)
            tileItem.addLayer(layer.name(),tileGraphicItem)

    def onRemoveLayer(self, layer):
        self.layers[layer.name()] = layer
        for tileItem in self.tileItems:
            tileItem.removeLayer(layer.name())
        self.layers.pop(layer.name())

    def onTilesAppear(self, tiles):

        #for ti in range(self.nTileItems):
        #    print self.tileGridManager.tileInfo(ti).tileVisible()
        for tileIndex in tiles:
            tileItem = self.tileItems[tileIndex]
            assert tileItem.tileInfo.tileVisible
            #print  tileItem.tileInfo.roi2d.begin
            tileItem.onTileAppear()

    def updateTiles(self, layerName = None, roi2D = None, roi3D=None):

        if roi2D is not None and roi3D is not None:
            raise RuntimeError("roi2D and roi3D cannot are both not None")

        elif roi2D is None and roi3D is None:
            tilesToUpdate = self.tileGridManager.visibleTiles()
        elif roi2D is not None:
            tilesToUpdate = self.tileGridManager.visibleTilesInRoi2D(roi2D[0],roi2D[1])
        elif roi3D is not None:
            tilesToUpdate = self.tileGridManager.visibleTilesInRoi3D(roi3D[0],roi3D[1])

        for tileIndex in tilesToUpdate:
            tileItem = self.tileItems[tileIndex]
            tileItem.onTileUpdate(layerName=layerName)

    def onTilesDisappear(self, tiles):
        for tileIndex in tiles:
            tileItem = self.tileItems[tileIndex]
            #assert tileItem.tileInfo.tileVisible == False
            tileItem.onTileDisappear()

    def onScrollCoordinateChanged(self, coord):
        #print "coord set",coord
        self.tileGridManager.updateScrollCoordinate(coord)
        for tileIndex in self.tileGridManager.visibleTiles():
            tileItem = self.tileItems[tileIndex]
            tileItem.onScrollCoordinateChanged()
            #print "ne coord",tileItem.scrollCoordinate
    
    def onTimeCoordinateChanged(self, coord):
        self.tileGridManager.updateTimeCoordinate(coord)
        for tileIndex in self.tileGridManager.visibleTiles():
            tileItem = self.tileItems[tileIndex]
            tileItem.onTimeCoordinateChanged()

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



class StaticTileGrid(pg.ItemGroup):
    def __init__(self,viewBox,blockingIndex):
        super(StaticTileGrid,self).__init__()
        self.viewBox = viewBox
        self.scrollAxis = self.viewBox.scrollAxis
        self.mlBlocking = viewBox.navigator.mlBlocking
        self.blocking2d = self.mlBlocking.blockings2d[self.scrollAxis][blockingIndex]

        

        # number of tiles == number of 2d blocks
        self.nTiles = len(self.blocking2d)
        self.tileItems = [None for x in range(self.nTiles)]

        # cpp tile grid manager
        self.tileGridManager = orthos_cpp.StaticTileGridManager(self.blocking2d, self.viewBox.scrollAxis, self.viewBox.viewAxis)
        # connect 
        self.viewBox.sigRectChanged.connect(self.onViewBoxViewRectChanged)

    def onViewBoxViewRectChanged(self):
        print "ON VIEW BOX RECT CHANGE"
        minCoord, maxCoord = self.viewBox.integralViewBounds2()
        aTiles,dTiles = self.tileGridManager.updateCurrentRoi(minCoord, maxCoord)
        if(len(dTiles)>0):
            print "dTiles",dTiles
            #self.onTilesDisappear(dTiles)

        if(len(aTiles)>0):
            print "atiles",aTiles
            #self.onTilesAppear(aTiles)
