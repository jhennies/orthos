import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy


class InfiniteLine(pg.InfiniteLine):
    sigPositionChanged = QtCore.Signal(object)


    def __init__(self, *args,**kwargs):
        super(InfiniteLine,self).__init__(*args,**kwargs)



    def setPos(self, pos, silent=False):
        
        if type(pos) in [list, tuple]:
            newPos = pos
        elif isinstance(pos, QtCore.QPointF):
            newPos = [pos.x(), pos.y()]
        else:
            if self.angle == 90:
                newPos = [pos, 0]
            elif self.angle == 0:
                newPos = [0, pos]
            else:
                raise Exception("Must specify 2D coordinate for non-orthogonal lines.")
        newPos = list(newPos)
        ## check bounds (only works for orthogonal lines)
        if self.angle == 90:
            if self.maxRange[0] is not None:    
                newPos[0] = max(newPos[0], self.maxRange[0])
            if self.maxRange[1] is not None:
                newPos[0] = min(newPos[0], self.maxRange[1])
        elif self.angle == 0:
            if self.maxRange[0] is not None:
                newPos[1] = max(newPos[1], self.maxRange[0])
            if self.maxRange[1] is not None:
                newPos[1] = min(newPos[1], self.maxRange[1])
            
        if self.p != newPos:
            self.p = newPos
            pg.GraphicsObject.setPos(self, pg.Point(self.p))
            self.update()
            if not silent:
                self.sigPositionChanged.emit(self)
