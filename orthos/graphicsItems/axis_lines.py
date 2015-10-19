import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

class AxisLine(pg.GraphicsObject):
    def __init__(self, size, orientation, color):
        pg.GraphicsObject.__init__(self)
        self.size=size
        self.orientation = orientation
        self.color = color

    def boundingRect(self):
        if self.orientation =='h':
            return QtCore.QRectF(0,0,self.size,1)
        else:
            return QtCore.QRectF(0,0,1,self.size)

    def paint(self, p, *args): 
        p.setPen(pg.mkPen(color=self.color))
        if self.orientation =='h':
            p.drawRect(QtCore.QRectF(0,0,self.size,0.1))
        else:
            p.drawRect(QtCore.QRectF(0,0,0.1,self.size))

