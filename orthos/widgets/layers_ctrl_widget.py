
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

from  ..layers.layer_base import *

class LayersCtrlWidget(QtGui.QWidget):

    def __init__(self):
        super(LayersCtrlWidget,self).__init__()
        

        self.pixelLayers = dict()
        self.pixelLayersItem = QtGui.QTreeWidgetItem(["PixelLayers"])

        ## Create tree of Parameter objects
        self.treeWidget = pg.TreeWidget()
        self.treeWidget.setColumnCount(1)

        self.setupUI()

    def setupUI(self):
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.treeWidget)
        

    def nPixelLayers(self):
        return len(self.pixelLayers)

    def addLayer(self, layer):
        if isinstance(layer, PixelLayerBase):
            nPixelLayersPost = self.nPixelLayers()
            self.pixelLayers[layer.name()] = layer
            if(nPixelLayersPost==0):
                self.treeWidget.addTopLevelItem(self.pixelLayersItem)

            layerItem = pg.TreeWidgetItem([''])
            self.pixelLayersItem.addChild(layerItem)

            ctrlWidget = layer.makeCtrlWidget()
            layerItem.setWidget(0,ctrlWidget)

        else:
            raise RuntimeError("Not yet implemented")

    def removeLayer(self, layer):
        if isinstance(layer, PixelLayerBase):
            self.pixelLayers.pop(layer,None)
        else:
            raise RuntimeError("Not yet implemented")
