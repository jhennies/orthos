from __future__ import division
import numpy
np = numpy
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui

class RenderWidget(QtGui.QWidget):
    def __init__(self, inputShape, widgets):
        super(RenderWidget,self).__init__()

        self.inputShape = inputShape
        self.relativeInputShape = tuple([d / min(inputShape) for d in inputShape])
        self.viewerPos = [0, 0, 0]
        self.sectionPosXY = [0, 0, 0]
        self.sectionPosXZ = [0, 0, 0]
        self.sectionPosYZ = [0, 0, 0]
        self.planes = [None,None,None]
        self.sections = [None, None, None]
        self.glw = gl.GLViewWidget()
        self.setupUI()
        self.setupGL()
        self.glw.opts['distance'] = max(self.relativeInputShape) * 1.1
        self.glw.opts['center'] = QtGui.QVector3D(0, self.relativeInputShape[1], 0)
        self.glw.opts['fov'] = 50
        self.glw.show()
        self.widgets = widgets
        self.widgets[0].viewBox.sigRectChanged.connect(self.onWidget0ViewBoxRectChanged)
        self.widgets[1].viewBox.sigRectChanged.connect(self.onWidget1ViewBoxRectChanged)
        self.widgets[2].viewBox.sigRectChanged.connect(self.onWidget2ViewBoxRectChanged)

    def onWidget0ViewBoxRectChanged(self):
        self.setSectionPos(0, self.viewerPos[0])

    def onWidget1ViewBoxRectChanged(self):
        self.setSectionPos(1, self.viewerPos[1])

    def onWidget2ViewBoxRectChanged(self):
        self.setSectionPos(2, self.viewerPos[2])

    def setupUI(self):
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.glw)
    
    def setupGL(self):
        
        shape = self.relativeInputShape
        w = self.glw

        size = QtGui.QVector3D(-1*shape[0],1*shape[1],0)
        self.xy = gl.GLBoxItem(size=size,color=(0,0,255))
        w.addItem(self.xy)

        size = QtGui.QVector3D(-1*shape[0],0,-1*shape[2])
        self.xz = gl.GLBoxItem(size=size,color=(0,255,0))
        w.addItem(self.xz)

        size = QtGui.QVector3D(0,1*shape[1],-1*shape[2])
        self.yz = gl.GLBoxItem(size=size,color=(255,0,0))
        w.addItem(self.yz)

        self.planes[0] = self.yz
        self.planes[1] = self.xz
        self.planes[2] = self.xy
        # self.xy.setSize
        size = QtGui.QVector3D(-1*shape[0],-1*shape[1], 0)
        self.sections[0] = gl.GLBoxItem(size=size,color=(255,0,0))
        size = QtGui.QVector3D(-1*shape[0],0,-1*shape[2])
        self.sections[1] = gl.GLBoxItem(size=size,color=(0,255,0))
        size = QtGui.QVector3D(0,-1*shape[1],-1*shape[2])
        self.sections[2] = gl.GLBoxItem(size=size,color=(0,0,255))
        w.addItem(self.sections[0])
        w.addItem(self.sections[1])
        w.addItem(self.sections[2])

    def setYZPos(self, p):
        self.setPlanePos(0,p)
    def setXZPos(self, p):
        self.setPlanePos(1,p)
    def setXYPos(self, p):
        self.setPlanePos(2,p)
    def setPlanePos(self, axis, p):
        t=[0]*3
        q = p / min(self.inputShape)
        #print self.planes[axis].transform()
        if self.viewerPos[axis] is None:
            t[axis]=q
            # self.planes[axis].translat(*tuple(t))
        else:
            op = self.viewerPos[axis] / min(self.inputShape)
            t[axis]=op-q
        t[1] = -t[1]
        self.planes[axis].translate(*tuple(t))
        self.setSectionPos(axis, p)
        self.viewerPos[axis] = p

    def setSectionPos(self, axis, p):
        q = p / min(self.inputShape)
        t = [0] * 3
        op = self.viewerPos[axis] / min(self.inputShape)

        t[axis]=op-q
        t[1] = -t[1]

        minCoord0, maxCoord0 = self.widgets[0].viewBox.integralViewBounds2()
        minCoord1, maxCoord1 = self.widgets[1].viewBox.integralViewBounds2()
        minCoord2, maxCoord2 = self.widgets[2].viewBox.integralViewBounds2()
        if axis == 0:
            size = QtGui.QVector3D(0, (maxCoord0[0]-minCoord0[0]) / min(self.inputShape), -(maxCoord0[1]-minCoord0[1]) / min(self.inputShape))
            t[1] = -self.sectionPosYZ[1] + (minCoord0[0] / min(self.inputShape))
            t[2] = -self.sectionPosYZ[2] - (minCoord0[1] / min(self.inputShape))
            # print "Positions:"
            # print self.sectionPosYZ
            # print (minCoord0[0] / min(self.inputShape))
            # print (minCoord0[1] / min(self.inputShape))
            # print t
            self.sections[axis].setSize(size=size)
            self.sections[axis].translate(*tuple(t))
            self.sectionPosYZ = [t[0], (minCoord0[0] / min(self.inputShape)), -(minCoord0[1] / min(self.inputShape)) ]
        if axis == 1:
            size = QtGui.QVector3D(-(maxCoord1[0]-minCoord1[0]) / min(self.inputShape), 0, -(maxCoord1[1]-minCoord1[1]) / min(self.inputShape))
            t[0] = -self.sectionPosXZ[0] - (minCoord1[0] / min(self.inputShape))
            t[2] = -self.sectionPosXZ[2] - (minCoord1[1] / min(self.inputShape))
            self.sections[axis].setSize(size=size)
            self.sections[axis].translate(*tuple(t))
            self.sectionPosXZ = [-(minCoord1[0] / min(self.inputShape)), t[1], -(minCoord1[1] / min(self.inputShape)) ]
        if axis == 2:
            size = QtGui.QVector3D(-(maxCoord2[0]-minCoord2[0]) / min(self.inputShape), (maxCoord2[1]-minCoord2[1]) / min(self.inputShape), 0)
            t[0] = -self.sectionPosXY[0] - (minCoord2[0] / min(self.inputShape))
            t[1] = -self.sectionPosXY[1] + (minCoord2[1] / min(self.inputShape))
            self.sections[axis].setSize(size=size)
            self.sections[axis].translate(*tuple(t))
            self.sectionPosXY = [-(minCoord2[0] / min(self.inputShape)), (minCoord2[1] / min(self.inputShape)), t[2]]





