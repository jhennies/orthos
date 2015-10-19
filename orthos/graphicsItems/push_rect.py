import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

class PushRect(pg.GraphicsObject, pg.GraphicsWidgetAnchor):
    sigClicked = QtCore.Signal(object)
    def __init__(self, color='r'):
        pg.GraphicsObject.__init__(self)
        pg.GraphicsWidgetAnchor.__init__(self)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
    def boundingRect(self):
        return QtCore.QRectF(0,0,10,10)

    def paint(self, p, *args): 
        p.setPen(pg.mkPen(color='r'))
        p.drawRect(QtCore.QRectF(0,0,10,10))
        
    def mousePressEvent(self, e):
        print "clicked"
        self.sigClicked.emit()
