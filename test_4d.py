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
        
    print "chuneked 4d data"
    data =  numpy.random.rand(10, 200,200,200)*255.0
    data = data.astype('uint8')
    f = h5py.File("/home/tbeier/Desktop/input/3dttttt_.h5")
    f.create_dataset('data',shape=data.shape,data=data,chunks=(3,64,64,64))
    f.close()





f = "/home/tbeier/Desktop/input/3dttttt_.h5"
#f = "/media/tbeier/data/datasets/hhess/2x2x2nm_chunked/data.h5"
rawSource = VigraChunkedArrayHdf5(file_name=f,dataset_name='data')
rawLayer = GrayscaleLayer(name='raw',levels=[0,255],dataSource=rawSource,useLut=True)


spatialShape =rawSource.shape[0:3]

print "spatial ", spatialShape



opt = LayerViewerOptions()
opt.spatialDimensions = 4
opt.hasTimeAxis = True

with vigra.Timer("create viewer"):
    viewerWidget = LayerViewerWidget(spatialShape=spatialShape, options=opt)
    mw.setCentralWidget(viewerWidget)

with vigra.Timer("add raw layer"):
    viewerWidget.addLayer(rawLayer)



viewerWidget.rangeChanged()




## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
