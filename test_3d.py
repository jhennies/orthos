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


f = "/home/tbeier/Desktop/hhes/pmap_pipe/raw.h5"
rawSource = VigraChunkedArrayHdf5(file_name=f,dataset_name='data')
rawLayer = GrayscaleLayer(name='raw',levels=[0,255],dataSource=rawSource)

# pmap layer
f = "/home/tbeier/Desktop/hhes/pmap_pipe/pmap_c0.h5"
pmapSource = VigraChunkedArrayHdf5(file_name=f,dataset_name='data')
pmapLayer = GrayscaleLayer(name='pmap',levels=[0.0,1.0],dataSource=pmapSource,mult=255.0)


# labels layer
f = "/home/tbeier/Desktop/hhes/pmap_pipe/labels_out2.h5"
labelsSource = VigraChunkedArrayHdf5(file_name=f,dataset_name='data',shape=rawSource.shape,
                                     mode=vigra.HDF5Mode.ReadWrite, compression=vigra.Compression.ZLIB_FAST,
                                     chunk_shape=[64,64,64],dtype='uint8')
paintLayer = PaintLayer(name="paint",dataSource=labelsSource)

spatialShape = rawSource.shape




opt = LayerViewerOptions()
opt.spatialDimensions = 3
opt.hasTimeAxis = False
viewerWidget = LayerViewerWidget(spatialShape=spatialShape, options=opt)
mw.setCentralWidget(viewerWidget)
viewerWidget.addLayer(rawLayer)
viewerWidget.addLayer(pmapLayer)
viewerWidget.addLayer(paintLayer)
viewerWidget.rangeChanged()




## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
