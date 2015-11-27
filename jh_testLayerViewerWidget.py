import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import orthos
import h5py

from orthos.widgets import *
from orthos.layers import *
from orthos.data_source import *

pg.setConfigOptions(antialias=False,useOpenGL=True)

app = QtGui.QApplication([])
mw = MainWindow()
mw.setWindowTitle('Orthos')
mw.show()
mw.resize(800, 600)

shape = (600, 300, 200)
data = numpy.random.rand(*shape)*255.0
data = data.astype('uint8')


print "start"
opt = LayerViewerOptions()
opt.spatialDimensions = 3
opt.hasTimeAxis = False
opt.minPixelSize = 0.1
opt.maxPixelSize = 5

viewerWidget = LayerViewerWidget(spatialShape=shape, options=opt)
mw.setCentralWidget(viewerWidget)


for x in range(1):
    with vigra.Timer("create raw layer"):
        rawSource = NumpyArrayDataSource(data)
        rawLayer = GrayscaleLayer(name='raw%d' % x, levels=[0, 255], dataSource=rawSource, useLut=True)
        viewerWidget.addLayer(rawLayer)

with vigra.Timer("range changed"):
    viewerWidget.rangeChanged()


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
