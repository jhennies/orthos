import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from viewbox import BvGridViewBox


class OrthoView(QtGui.QWidget):
    def __init__(self, inputShape, blockShape, axis=0):
        super(OrthoView,self).__init__()

        

        self.inputShape = inputShape
        self.blockShape = blockShape
        self.axis = axis

        # make the ui
        self.setupUI()
    def setupUI(self):

        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)


        # view box
        vb = BvGridViewBox(inputShape=self.inputShape,
                           blockShape=self.blockShape,
                           axis=self.axis)
        self.viewBox = vb

        # graphics view
        self.gv = pg.GraphicsView()
        l = QtGui.QGraphicsGridLayout()
        l.addItem(vb, 0, 1)
        self.gv.centralWidget.setLayout(l)
        self.mainLayout.addWidget(self.gv)

