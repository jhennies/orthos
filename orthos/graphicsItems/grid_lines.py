import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


class GridLines(pg.GraphicsObject):
    def __init__(self, blocking2d):
        pg.GraphicsObject.__init__(self)
        self.blocking2d = blocking2d
    def boundingRect(self):
        s = self.blocking2d.shape
        return QtCore.QRectF(0,0,s[0],s[1])
    def paint(self, p, *args):
        p.setPen(pg.mkPen('w'))
        nBlocks = len(self.blocking2d)
        for bIndex in range(nBlocks):
            tl,br = self.blocking2d[bIndex]
            w = br[0] - tl[0]
            h = br[1] - tl[1]
            p.drawRect(QtCore.QRectF(tl[0],tl[1],w,h))
