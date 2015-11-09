import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from operator import mul

import orthos_cpp















class TileItemGroup(pg.ItemGroup):
    """ A Container of all Graphics Items in a single(!) 2d-tile
    """

    def __init__(self, viewBox, tileInfo):
        self.viewBox = viewBox
        self.tileInfo = tileInfo
        self.items = dict()
        super(TileItemGroup,self).__init__()
        


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
        #print "add layer",name
        if self.tileVisible:
            #print "is tile visible"
            item.onTileAppear()
        else:
            pass
            #print "noy tile visible"
    def removeLayer(self,name):
        self.removeFromGroup(item)
        self.items.pop(item)

    def onTileAppear(self):
        for layerName in self.items:
            self.items[layerName].onTileAppear()

    def onTileUpdate(self, layerName=None):
        if layerName is None:
            for layerName in self.items:
                self.items[layerName].onTileUpdate()
        else:
            self.items[layerName].onTileUpdate()

    def onTileDisappear(self):
        for layerName in self.items:
            self.items[layerName].onTileDisappear()

    def onScrollCoordinateChanged(self):
        """ called when scrolled (usually from mouse wheel events)
        """
        # inform all items
        for layerName in self.items:
            self.items[layerName].onScrollCoordinateChanged()
    def onTimeCoordinateChanged(self):
        """ called when current time point changes (usually time-widget)
        """
        for layerName in self.items:
            self.items[layerName].onTimeCoordinateChanged()



