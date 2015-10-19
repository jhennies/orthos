import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import vigra
import numpy
#from blocking import *
from functools import partial
from  ..graphicsItems.infinite_blocked_view_box import *


aixsLetters={0:'x',1:'y',2:'z'}



def linked3dViewBoxWidgets():

    x = ViewBoxWidget(scrollAxis=0, viewAxis=[1,2])
    y = ViewBoxWidget(scrollAxis=1, viewAxis=[0,2])
    z = ViewBoxWidget(scrollAxis=2, viewAxis=[0,1])

    x.connectOtherViewBoxWidgets([y,z])
    y.connectOtherViewBoxWidgets([x,z])
    z.connectOtherViewBoxWidgets([x,y])

    return [x,y,z]


class ViewBoxWidget(QtGui.QWidget):
    def __init__(self, scrollAxis=0, viewAxis=[0,1], 
                 blockSizes=[128,256,512,1024,2048], 
                 minPixelSize=None, maxPixelSize=None):
        super(ViewBoxWidget,self).__init__()

        

        self.viewBox = InfiniteBlockedViewBox(scrollAxis=scrollAxis,
                                              viewAxis=viewAxis,blockSizes=blockSizes,
                                              minPixelSize=minPixelSize, 
                                              maxPixelSize=maxPixelSize)

        self.connectedViewBoxWidgets = []


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
    @property
    def sigScrolled(self):
        return self.viewBox.sigScrolled

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
        self.sigScrolled.connect(self.onScrolled)



    def connectOtherViewBoxWidgets(self, others):

        self.connectedViewBoxWidgets = others

        for vbw in self.connectedViewBoxWidgets:
            vb = vbw.viewBox

            if self.viewBox.viewAxis[0] == vb.scrollAxis:
                self.viewBox.axis0Line.sigPositionChanged.connect(vb.onExternalAxisLineChanged)
            elif self.viewBox.viewAxis[1] == vb.scrollAxis:
                self.viewBox.axis1Line.sigPositionChanged.connect(vb.onExternalAxisLineChanged)


    def onScrolled(self, scrollCoordinate):
        #print self.viewBox.scrollAxis,scrollCoordinate
        # update other viewers
        for vbw in self.connectedViewBoxWidgets:
            vb = vbw.viewBox
            
            if self.viewBox.scrollAxis == vb.viewAxis[0]:
                vb.axis0Line.setPos((scrollCoordinate,0))
            elif self.viewBox.scrollAxis == vb.viewAxis[1]:
                vb.axis1Line.setValue((0,scrollCoordinate))


            #vb.update()
        self.updateText()
    def onPixelSizeChanged(self, ps):
        self.updateText()

    def updateText(self):
        al = aixsLetters[self.viewBox.scrollAxis]
        ps = numpy.round(self.viewBox.viewPixelSize(),2)
        ps = str(ps)
        s = "%s=%d,       zoom=%s"%(al,self.viewBox.scrollCoordinate,ps)
        self.textItem1.setText(s)   