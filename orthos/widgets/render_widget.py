import numpy
np = numpy
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui



class RenderWidget(QtGui.QWidget):
    def __init__(self, inputShape):
        super(RenderWidget,self).__init__()

        self.inputShape = inputShape
        self.viewerPos = [0,0,0]
        self.planes = [None,None,None]
        self.glw = gl.GLViewWidget()
        self.setupUI()
        self.setupGL()
        self.glw.opts['distance'] = 2000
        self.glw.show()
    def setupUI(self):
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.glw)
    
    def setupGL(self):
        
        shape = self.inputShape.spatialShape
        w = self.glw

        size = QtGui.QVector3D(-1*shape[0],-1*shape[1],1)
        self.xy = gl.GLBoxItem(size=size,color=(0,0,255))
        w.addItem(self.xy)

        size = QtGui.QVector3D(-1*shape[0],1,-1*shape[2])
        self.xz = gl.GLBoxItem(size=size,color=(0,255,0))
        w.addItem(self.xz)

        size = QtGui.QVector3D(1,-1*shape[1],-1*shape[2])
        self.yz = gl.GLBoxItem(size=size,color=(255,0,0))
        w.addItem(self.yz)

        self.planes[0] = self.yz
        self.planes[1] = self.xz
        self.planes[2] = self.xy

    def setYZPos(self, p):
        self.setPlanePos(0,p)
    def setXZPos(self, p):
        self.setPlanePos(1,p)
    def setXYPos(self, p):
        self.setPlanePos(2,p)
    def setPlanePos(self, axis, p):
        t=[0]*3
        #print self.planes[axis].transform()
        if self.viewerPos[axis] is None:
            t[axis]=p
            self.planes[axis].translat(*tuple(t))
        else:
            op = self.viewerPos[axis]
            t[axis]=op-p
            self.planes[axis].translate(*tuple(t))
        self.viewerPos[axis] = p


