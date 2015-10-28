import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy



class ShapeSetterWidget(QtGui.QWidget):
    def __init__(self, maxVal=30):
        super(ShapeSetterWidget, self).__init__()

        self.maxVal = maxVal
        self.sliders = [QtGui.QSlider(QtCore.Qt.Horizontal, self) for x in range(3)]
        self.setupUI()
        self.drawKernel = numpy.zeros([3,3], dtype='uint8')

    def setupUI(self):

        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        for s in self.sliders:
            s.setMinimum(1)
            s.setMaximum(30)
            s.setValue(2)
            self.mainLayout.addWidget(s)
    

class KeImageItem(pg.ImageItem):
    def __init__(self, kernelEditor):
        super(KeImageItem,self).__init__(border='w')
        self.kernelEditor = kernelEditor
        self.kernel = kernelEditor.kernel
    def mouseClickEvent(self, ev, double=False):
        ev.accept()
        pos = ev.pos()
        pos = int(pos.x()),int(pos.y())
        l = self.kernel[pos]
        self.kernel[pos] = 255 * (not bool(l))
        self.updateImage(self.kernel)

    def mouseDragEvent(self, ev, axis=None):
        kmods = ev.modifiers()
        if kmods & pg.QtCore.Qt.ControlModifier and ev.button() == QtCore.Qt.LeftButton:
            super(InfiniteBlockedViewBox,self).mouseDragEvent(ev, axis)



class KeViewBox(pg.ViewBox):
    def __init__(self, kernelEditor):
        super(KeViewBox,self).__init__()
        self.kernelEditor = kernelEditor


class KernelEditorWidget(QtGui.QWidget):
    def __init__(self):
        super(KernelEditorWidget, self).__init__()


        # data
        self.kernel  = [[0,1,0],[1,1,1],[0,1,0]]
        self.kernel = numpy.array(self.kernel, dtype='uint8')*255


        self.viewBox = KeViewBox(self)
        self.imageItem = KeImageItem(self)
        self.viewBox.addItem(self.imageItem)
        self.glayout = pg.GraphicsLayout()
        self.gv = pg.GraphicsView()


        # actual ctrl content
        self.shapeSetterWidget = ShapeSetterWidget()
        self.setupUI()

        self.setDrawKernelImage_()

    def setupUI(self):

        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        # graphics view
        l = self.glayout
        self.gv.setCentralItem(l)
        self.mainLayout.addWidget(self.gv)
        l.addItem(self.viewBox, 0,0)

        # ctrl widgets
        self.ctrlLayout = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.ctrlLayout)
        self.ctrlLayout.addWidget(self.shapeSetterWidget)

    def setDrawKernelImage_(self):
        self.imageItem.updateImage(self.kernel)

if __name__ == "__main__":

    app = QtGui.QApplication([])
    mw = QtGui.QMainWindow()

    kernelEditor = KernelEditorWidget()

    mw.setCentralWidget(kernelEditor)

    mw.show()


    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
