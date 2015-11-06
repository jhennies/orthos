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
mw = MainWindow()
mw.setWindowTitle('Orthos')
mw.show()
mw.resize(800, 600)



if False:
    print "read"
    data = vigra.impex.readHDF5("/home/tbeier/Desktop/input/superpixels_10000.h5",'data')
    f = h5py.File("/home/tbeier/Desktop/input/superpixels_10000c.h5")
    print "write"
    f.create_dataset('data',shape=data.shape,data=data,chunks=(64,64,64))
    f.close()


f = "/home/tbeier/Desktop/input/raw.h5"
#f = "/media/tbeier/data/datasets/hhess/2x2x2nm_chunked/data.h5"
rawSource = VigraChunkedArrayHdf5(file_name=f,dataset_name='data')
rawLayer = GrayscaleLayer(name='raw',levels=[0,255],dataSource=rawSource,useLut=True)


# pmap layer
f = "/home/tbeier/Desktop/input/pmap_c0.h5"
pmapSource = VigraChunkedArrayHdf5(file_name=f,dataset_name='data')
pmapLayer = GrayscaleLayer(name='pmap',levels='auto',dataSource=pmapSource,useLut=True)


## supervoxel layer
f = "/home/tbeier/Desktop/input/superpixels_10000c.h5"
superVoxelSource = VigraChunkedArrayHdf5(file_name=f,dataset_name='data')
superVoxelLayer = SupervoxelLayer(name='sv',dataSource=superVoxelSource)
objectLayer = ObjectLayer(name='obj',dataSource=superVoxelSource)

# paint layer
f = "/home/tbeier/Desktop/input/labels_out.h5"
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
viewerWidget.addLayer(superVoxelLayer)
viewerWidget.addLayer(objectLayer)
viewerWidget.addLayer(paintLayer)
viewerWidget.rangeChanged()

def closeCallback():
    labelsSource.flushToDisk()
mw.closeCallback = closeCallback



## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
