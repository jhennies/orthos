import numpy
np = numpy
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui

from view_box_widget import *
from color_dock import *
from orthos.layers import *
from pyqtgraph.dockarea import *
from pyqtgraph.dockarea import *


class LayerViewerOptions(object):
    def __init__(self):

        # about the data to be displayed
        self.spatialDimension = 3
        self.hasTimeAxis = False

        # the view box options
        self.minPixelSize = 0.01
        self.maxPixelSize = 16.0

        # pixel layer options
        self.pyramidLevels = 1
        self.tileSize = 256
        self.tilingShape = (10,10)



class LayerViewerWidget(QtGui.QWidget):
    def __init__(self,options):
        super(LayerViewerWidget,self).__init__()

        self.options = options
        res = linked3dViewBoxWidgets(options)
        self.viewBoxWidgets = res[0]
        self.renderWidget = res[1]
        self.navigator = res[2]
        self.pixelLayers = res[3]
        self.layersCtrlWidget = res[4]
        self.timeCtrlWidget = res[5]
        self.timeCtrlDock = None
        self.area = MyDockArea()
        self.orthoViewsDocks = []
        self.renderDock = None
        self.setupUI()
    def setupUI(self):
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.area)
    
        for vbw in self.viewBoxWidgets :
            dockColor = axisColor(vbw.viewBox.scrollAxis,val=200)
            viewerName = aixsLetters[vbw.viewBox.viewAxis[0]] +  aixsLetters[vbw.viewBox.viewAxis[1]]
            d = ColorDock(name=viewerName,color=dockColor)
            self.orthoViewsDocks.append(d)
            d.addWidget(vbw)

        self.renderDock = ColorDock(name=viewerName,color=(200,200,200))
        self.renderDock.addWidget(self.renderWidget)


        if self.options.hasTimeAxis:
            self.timeCtrlDock = ColorDock(name="T",color=(1,1,1))

        layersCtrlDock = ColorDock(name="layerCtrl",color=(1,1,1))
        layersCtrlDock.addWidget(self.layersCtrlWidget)


        self.area.addDock(self.orthoViewsDocks[2],'left')
        self.area.addDock(self.orthoViewsDocks[1],'right')
        self.area.addDock(self.orthoViewsDocks[0],'bottom')#,self.orthoViewsDocks[0])
        self.area.addDock(self.renderDock,'right',self.orthoViewsDocks[0])
        self.area.addDock(layersCtrlDock,'right')
        if self.options.hasTimeAxis:
            self.area.addDock(self.timeCtrlDock,'bottom')
            self.timeCtrlDock.setStretch(1,1)
            self.timeCtrlDock.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
            self.timeCtrlDock.label.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
            self.timeCtrlDock.widgetArea.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
            self.timeCtrlWidget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
            self.timeCtrlDock.addWidget(self.timeCtrlWidget)


    # handle key events
    def keyPressEvent(self, e):
        key = e.key()
        modifiers = QtGui.QApplication.keyboardModifiers()
        ctrlPressed = modifiers == QtCore.Qt.ControlModifier
        if key == QtCore.Qt.Key_G and ctrlPressed:
            for vbw in self.viewBoxWidgets :
                vb = vbw.viewBox
                vb.gridLines.setVisible(not vb.gridLines.isVisible())
            e.accept()

        if key == QtCore.Qt.Key_A and ctrlPressed:
            for vbw in self.viewBoxWidgets :
                vb = vbw.viewBox
                vb.axis0Line.setVisible(not vb.axis0Line.isVisible())
                vb.axis1Line.setVisible(not vb.axis1Line.isVisible())
            e.accept()

        if key == QtCore.Qt.Key_S and ctrlPressed:
            for vbw in self.viewBoxWidgets :
                if vbw.scalesAdded == True:
                    vbw.glayout.removeItem(vbw.xScale)
                    vbw.glayout.removeItem(vbw.yScale)
                    #vbw.xScale.setVisible(not vbw.xScale.isVisible())
                else:
                    vbw.glayout.addItem(vbw.xScale,2,1)
                    vbw.glayout.addItem(vbw.yScale,1,0)
                vbw.scalesAdded = not vbw.scalesAdded
            e.accept()

        if key == QtCore.Qt.Key_T and ctrlPressed:
            for vbw in self.viewBoxWidgets :
                if vbw.textAdded == True:
                    vbw.glayout.removeItem(vbw.textItem1)
                else:
                    vbw.glayout.addItem(vbw.textItem1,0,1)
                vbw.textAdded = not vbw.textAdded
            e.accept()


    # add LAYERS
    def addLayer(self, layer):

        # add layer to ctrl gui
        self.layersCtrlWidget.addLayer(layer)

        # add layer to the suitable layers container
        if isinstance(layer, PixelLayerBase):
            self.pixelLayers.addLayer(layer)
        else:
            raise RuntimeError("Not yet implemented")
    def removeLayer(self, layer):
        # remove layer to ctrl gui
        self.layersCtrlWidget.removeLayer(layer)

        # remove layer from the suitable container
        if isinstance(layer, PixelLayerBase):
            self.pixelLayers.removeLayer(layer)
        else:
            raise RuntimeError("Not yet implemented")

    def update(self):
        for vbw in self.viewBoxWidgets :
            vbw.viewBox.renderArea.updateVisibleBlocks()
