import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import orthos
import h5py

from orthos.widgets import *
from orthos.layers import *
from orthos.data_source import *



app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.setWindowTitle('Orthos')
mw.show()
mw.resize(800, 600)



# raw layer
f = "/media/tbeier/data/datasets/hhess/2x2x2nm_chunked/data.h5"


rawSource = VigraChunkedArrayHdf5(f,'data')
rawLayer = GrayscaleLayer(name='raw',dataSource=rawSource)


spatialShape = rawSource.shape


opt = LayerViewerOptions()
opt.spatialDimensions = 3
opt.hasTimeAxis = False
viewerWidget = LayerViewerWidget(spatialShape=spatialShape, options=opt)
mw.setCentralWidget(viewerWidget)
viewerWidget.addLayer(rawLayer)
viewerWidget.update()




## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
