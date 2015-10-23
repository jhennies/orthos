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
<<<<<<< HEAD
#f = "/media/tbeier/data/datasets/hhess/2x2x2nm_chunked/data.h5"
f = "/home/tbeier/Desktop/hhes/pmap_pipe/raw.h5"
=======
f = "/media/tbeier/data/datasets/hhess/2x2x2nm_chunked/data.h5"
f = "/media/tbeier/data/datasets/hhess/pmap_pipe/raw.h5"
>>>>>>> f51d250749b59652190bbf2c667a82bc5239efb9

rawSource = VigraChunkedArrayHdf5(f,'data')
rawLayer = GrayscaleLayer(name='raw',dataSource=rawSource)

# pmap layer
f = "/media/tbeier/data/datasets/hhess/pmap_pipe/pmap_c0.h5"
pmapSource = VigraChunkedArrayHdf5(f,'data')
pmapLayer = GrayscaleLayer(name='pmap',dataSource=pmapSource,mult=255.0)


<<<<<<< HEAD
spatialShape = rawSource.shape
=======

>>>>>>> f51d250749b59652190bbf2c667a82bc5239efb9

opt = LayerViewerOptions()
opt.spatialDimensions = 3
opt.hasTimeAxis = False
viewerWidget = LayerViewerWidget(spatialShape=spatialShape, options=opt)
mw.setCentralWidget(viewerWidget)
viewerWidget.addLayer(rawLayer)
#viewerWidget.addLayer(pmapLayer)
viewerWidget.update()




## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
