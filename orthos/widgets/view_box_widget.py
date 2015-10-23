import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import vigra
import numpy
#from blocking import *
from functools import partial
from   ..graphicsItems import linked_view_box
from  ..layers.layer_base import *
from render_widget import *
from time_ctrl_widget import *
from layers_ctrl_widget import *
from ..blocking import *
aixsLetters={0:'x',1:'y',2:'z'}



class Navigator(object):

    def __init__(self, spatialShape, nTimePoints):
        self.mlBlocking = MultiLevelBlocking(spatialShape=spatialShape)
        self.spatialShape = spatialShape
        self.nTimePoints = nTimePoints
        self.planePosition = [0,0,0]
        self.viewBoxWidgets = []

    def setViewBoxWidgets(self, viewBoxWidgets):
        self.viewBoxWidgets = viewBoxWidgets

    def changedPlane(self, scrollAxis, scrollAxisCoordinate, updatedBy=None):
        self.planePosition[scrollAxis] = scrollAxisCoordinate
        print self.planePosition
        for vbw in self.viewBoxWidgets:
            vb = vbw.viewBox
            if vb.scrollAxis == scrollAxis:
                vb.changeScrollCoordinate(scrollAxisCoordinate)
                vbw.onScrolled(scrollAxisCoordinate)
            else:
                if vb.viewAxis[0] == scrollAxis:
                    if vb.axis0Line != updatedBy:
                        vb.axis0Line.setPos((scrollAxisCoordinate,0),silent=True)
                else:
                    if vb.axis1Line != updatedBy:
                        vb.axis1Line.setPos((0,scrollAxisCoordinate),silent=True)

    def onTimeChanged(self, newTime):
        print "time changed to",newTime
        for vbw in self.viewBoxWidgets:
            vbw.viewBox.onTimeChanged(newTime)
def linked3dViewBoxWidgets(spatialShape, nTimePoints, options):

    pixelLayers = PixelLayers()
    layersCtrl = LayersCtrlWidget()
    navigator = Navigator(spatialShape=spatialShape, nTimePoints=nTimePoints)
    x = ViewBoxWidget(navigator=navigator,pixelLayers=pixelLayers,scrollAxis=0, viewAxis=[1,2])
    y = ViewBoxWidget(navigator=navigator,pixelLayers=pixelLayers,scrollAxis=1, viewAxis=[0,2])
    z = ViewBoxWidget(navigator=navigator,pixelLayers=pixelLayers,scrollAxis=2, viewAxis=[0,1])
    widgets = [x,y,z]
    renderWidget = RenderWidget([1,1,1])
    navigator.setViewBoxWidgets(widgets)

    if options.hasTimeAxis:
        timeCtrlWidget = TimeCtrlWidget(navigator=navigator)
    else:
        timeCtrlWidget = None

    return [x,y,z],renderWidget, navigator,pixelLayers,layersCtrl,timeCtrlWidget


class ViewBoxWidget(QtGui.QWidget):


    def __init__(self, navigator, pixelLayers,
                 scrollAxis=0, viewAxis=[0,1], 
                 blockSizes=[128,256,512,1024,2048], 
                 minPixelSize=None, maxPixelSize=None):
        super(ViewBoxWidget,self).__init__()

        self.pixelLayers = pixelLayers

        self.viewBox = linked_view_box.InfiniteBlockedViewBox(navigator=navigator,
                                              pixelLayers=pixelLayers,
                                              scrollAxis=scrollAxis,
                                              viewAxis=viewAxis,blockSizes=blockSizes,
                                              minPixelSize=minPixelSize, 
                                              maxPixelSize=maxPixelSize)

        self.glayout = pg.GraphicsLayout()
        # graphic items
        self.xScale = pg.AxisItem(orientation='bottom', linkView=self.viewBox)
        self.yScale = pg.AxisItem(orientation='left', linkView=self.viewBox)
        self.xScale.setLabel(text=aixsLetters[viewAxis[0]])
        self.yScale.setLabel(text=aixsLetters[viewAxis[1]])
        self.scalesAdded = False
        self.textAdded = False
        self.textItem1 = pg.LabelItem("text1")
        self.textItem2 = pg.LabelItem("text2")




        # make the ui
        self.setupUI()
        self.setupSignals()



    # signals from view box
    @property
    def sigPixelSizeChanged(self):
        return self.viewBox.sigPixelSizeChanged

    def setupUI(self):

        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)


        # view box
        
 

        # graphics view
        self.gv = pg.GraphicsView()
        l = self.glayout
        
        #l.setHorizontalSpacing(1)
        #l.setVerticalSpacing(1) 
        
        
        self.scalesAdded = True
        self.textAdded = True
        l.addItem(self.textItem1, 0, 1)
        
        l.addItem(self.yScale, 1, 0)
        l.addItem(self.viewBox, 1, 1)
        l.addItem(self.xScale, 2, 1)

        self.gv.setCentralItem(l)
        self.mainLayout.addWidget(self.gv)

    def setupSignals(self):
        
        # connect pixel size change
        self.sigPixelSizeChanged.connect(self.onPixelSizeChanged)





    def onScrolled(self, scrollCoordinate):
        self.updateText()
    def onPixelSizeChanged(self, ps):
        self.updateText()

    def updateText(self):
        al = aixsLetters[self.viewBox.scrollAxis]
        ps = numpy.round(self.viewBox.viewPixelSize(),2)
        ps = str(ps)
        s = "%s=%d,       zoom=%s"%(al,self.viewBox.scrollCoordinate,ps)
        self.textItem1.setText(s)   
