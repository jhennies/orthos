import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import vigra
import numpy
#from blocking import *
from functools import partial
from  ..graphicsItems.infinite_blocked_view_box import *


aixsLetters={0:'x',1:'y',2:'z'}

class Navigator(object):
    def __init__(self):
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

def linked3dViewBoxWidgets():

    navigator = Navigator()
    x = ViewBoxWidget(navigator=navigator,scrollAxis=0, viewAxis=[1,2])
    y = ViewBoxWidget(navigator=navigator,scrollAxis=1, viewAxis=[0,2])
    z = ViewBoxWidget(navigator=navigator,scrollAxis=2, viewAxis=[0,1])
    navigator.setViewBoxWidgets([x,y,z])

    return [x,y,z], navigator


class ViewBoxWidget(QtGui.QWidget):
    def __init__(self, navigator, scrollAxis=0, viewAxis=[0,1], 
                 blockSizes=[128,256,512,1024,2048], 
                 minPixelSize=None, maxPixelSize=None):
        super(ViewBoxWidget,self).__init__()

        

        self.viewBox = InfiniteBlockedViewBox(navigator=navigator,
                                              scrollAxis=scrollAxis,
                                              viewAxis=viewAxis,blockSizes=blockSizes,
                                              minPixelSize=minPixelSize, 
                                              maxPixelSize=maxPixelSize)


        # graphic items
        self.xScale = pg.AxisItem(orientation='bottom', linkView=self.viewBox)
        self.yScale = pg.AxisItem(orientation='left', linkView=self.viewBox)
        self.xScale.setLabel(text=aixsLetters[viewAxis[0]])
        self.yScale.setLabel(text=aixsLetters[viewAxis[1]])

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
        l = pg.GraphicsLayout()
        
        #l.setHorizontalSpacing(1)
        #l.setVerticalSpacing(1) 
        
        

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
