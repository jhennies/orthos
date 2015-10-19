import numpy
np = numpy
import vigra
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *

from data_source import InputType, InputShape
from viewbox import BvGridViewBox
from ortho_view import OrthoView
from orthos.widgets import *

import scipy.ndimage as ndi
import h5py



class ViewerCtrlWidget(QtGui.QWidget):
    def __init__(self):
        super(ViewerCtrlWidget,self).__init__()
        self.setupUI()

    def setupUI(self):
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.button = QtGui.QPushButton("test")
        self.mainLayout.addWidget(self.button)
    


class ViewerDockArea(DockArea):

    def __init__(self, inputShape, blockShape=(128,)*3):
        super(ViewerDockArea,self).__init__()

        self.inputShape = inputShape
        self.blockShape = blockShape

        self.viewBoxes = []
        self.orthoViews = []
        self.orthoViewsDocks = []

        self.renderWidget = None
        self.renderDock = None
        # setup ortho-views
        if inputShape.nSpatialDim == 3:
            self.renderWidget = RenderWidget(inputShape=inputShape)
            self.renderDock  = Dock("R")
            self.renderDock.addWidget(self.renderWidget)
            for axis,axisName in zip([0,1,2],('yz','xz','xy')):
                ov = OrthoView(inputShape=inputShape,
                               blockShape=blockShape,
                               axis=axis)
                self.viewBoxes.append(ov.viewBox)
                ovDock = Dock(axisName)
                ovDock.addWidget(ov) 
               

                self.orthoViews.append(ov)
                self.orthoViewsDocks.append(ovDock)

            # connect
            self.viewBoxes[0].sigScrolled.connect(self.renderWidget.setYZPos)
            self.viewBoxes[1].sigScrolled.connect(self.renderWidget.setXZPos) 
            self.viewBoxes[2].sigScrolled.connect(self.renderWidget.setXYPos)


            # "z" changed
            # - inform 'yz' box
            ## - inform 'xz' box
            self.viewBoxes[2].sigScrolled.connect(self.viewBoxes[0].updateHLinePos)
            self.viewBoxes[2].sigScrolled.connect(self.viewBoxes[1].updateHLinePos)
#
#
            ## "y" changed
            ## - inform 'yz' box
            ## - inform 'xy' box
            self.viewBoxes[1].sigScrolled.connect(self.viewBoxes[0].updateVLinePos)
            self.viewBoxes[1].sigScrolled.connect(self.viewBoxes[2].updateHLinePos)
#
#
            ## "x" changed
            ## - inform 'xy' box
            ## - inform 'xz' box
            self.viewBoxes[0].sigScrolled.connect(self.viewBoxes[2].updateVLinePos)
            self.viewBoxes[0].sigScrolled.connect(self.viewBoxes[1].updateVLinePos)



            self.viewBoxes[0].sigMoveOtherViewers.connect(self.viewBoxes[1].movedBy)
            self.viewBoxes[0].sigMoveOtherViewers.connect(self.viewBoxes[2].movedBy)

            self.viewBoxes[1].sigMoveOtherViewers.connect(self.viewBoxes[0].movedBy)
            self.viewBoxes[1].sigMoveOtherViewers.connect(self.viewBoxes[2].movedBy)

            self.viewBoxes[2].sigMoveOtherViewers.connect(self.viewBoxes[0].movedBy)
            self.viewBoxes[2].sigMoveOtherViewers.connect(self.viewBoxes[1].movedBy)

            self.addDock(self.orthoViewsDocks[2],'left')
            self.addDock(self.orthoViewsDocks[1],'right')
            self.addDock(self.orthoViewsDocks[0],'bottom')#,self.orthoViewsDocks[0])
            self.addDock(self.renderDock,'right',self.orthoViewsDocks[0])




class LayerCtrlWidget(QtGui.QWidget):
    def __init__(self):
        super(LayerCtrlWidget,self).__init__()
        self.setupUI()

    def setupUI(self):

        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
    
        self.tree = pg.TreeWidget()
        w  = self.tree
        w.setColumnCount(1)
        w.show()
        w.setWindowTitle('pyqtgraph example: TreeWidget')

        self.voxelLayer  = QtGui.QTreeWidgetItem(["VoxelLayer"])
        b5 = QtGui.QPushButton('Button')
        



        w.addTopLevelItem(self.voxelLayer)
        #w.setItemWidget(i1,0, b5)
        #w.addTopLevelItem(i2)
        #w.addTopLevelItem(i3)
        #w.addTopLevelItem(i4)
        #w.addTopLevelItem(i5)
        #i1.addChild(i11)
        #i1.addChild(i12)
        #i2.addChild(i21)
        #i21.addChild(i211)
        #i21.addChild(i212)
        #i2.addChild(i22)

        #b1 = QtGui.QPushButton("Button")
        #w.setItemWidget(i1, 1, b1)
        self.mainLayout.addWidget(w)

    def addPixelLayer(self,layer,name):
        child = QtGui.QTreeWidgetItem([name])
        self.voxelLayer.addChild(child)
        self.tree.setItemWidget(child,0,layer.widget())

class ViewerWidget(QtGui.QWidget):

    def __init__(self, inputShape, blockShape):
        super(ViewerWidget,self).__init__()
        self.inputShape = inputShape
        self.blockShape = blockShape

        # make the ui
        self.viewerDockArea = ViewerDockArea(inputShape=inputShape, 
                                             blockShape=blockShape)
        self.viewerCtrlWidget = ViewerCtrlWidget()
        self.layerCtrlWidget  =LayerCtrlWidget()
        self.setupUI()

        self.pixelLayer = dict()

    def setupUI(self):
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)

        

        self.subLayout = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.subLayout,3)
        self.subLayout.addWidget(self.viewerDockArea,3)
        self.subLayout.addWidget(self.viewerCtrlWidget)
        

        self.mainLayout.addWidget(self.layerCtrlWidget)

    def addPixelLayer(self, layer, name):
        self.pixelLayer[name] = layer
        self.layerCtrlWidget.addPixelLayer(layer,name)
        for orthoView in self.viewerDockArea.orthoViews :
            vb = orthoView.viewBox
            vb.addPixelLayer(layer, name)

    def setShowGridLines(self, show):
        for orthoView in self.viewerDockArea.orthoViews :
            vb = orthoView.viewBox
            vb.setShowGridLines(show)



class RawDataLayerWidget(QtGui.QWidget):
    def __init__(self, layer):
        super(RawDataLayerWidget, self).__init__()
        self.layer = layer
        self.ge = pg.GradientWidget(orientation='top')
        self.setupUI()

    def setupUI(self):
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.ge = pg.GradientWidget(orientation='top')
        self.mainLayout.addWidget(self.ge)







class RawDataLayer(object):
    def __init__(self, data):
        self.data = data
        self.widget_ =  RawDataLayerWidget(self)
    def getData(self,slicing):
        #print "slicing ",slicing, self.data.shape
        t = tuple(slicing)
        
        d = self.data[t]#.astype('uint8')
        return d

    def widget(self):
        return self.widget_

if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()


    # load data
    f = "/home/tbeier/Desktop/hhes/data_sub.h5"
    raw = h5py.File(f)['data']
    #raw = raw.astype('float32')#[0:10,0:90,0:180]

    rawDataLayer = RawDataLayer(raw)


    shape = InputShape(spatialShape=raw.shape, nTimePoint=False)
    viewer = ViewerWidget(inputShape=shape, blockShape=(128,128,128))

    viewer.addPixelLayer(rawDataLayer,"raw")
    viewer.setShowGridLines(False)

    win.setCentralWidget(viewer)
    win.resize(1000,500)
    win.show()

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
