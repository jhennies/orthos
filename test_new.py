import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import orthos
import h5py

from orthos.widgets import *
from orthos.layers import *

from pyqtgraph.dockarea import *



app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.setWindowTitle('pyqtgraph example: ViewBox')
mw.show()
mw.resize(800, 600)




f = "/media/tbeier/data/datasets/hhess/2x2x2nm_chunked/data.h5"
raw = h5py.File(f)['data']
rawLayer = H5PixelLayer(dset=raw, name='raw')



viewBoxWidgets, navigator = linked3dViewBoxWidgets()
area = DockArea()
mw.setCentralWidget(area)

# some data

for vbw in viewBoxWidgets :
    renderArea = vbw.viewBox.renderArea
    renderArea.rawDataLayer = rawLayer


for vbw in viewBoxWidgets :
    d = Dock("a dock")
    area.addDock(d)
    d.addWidget(vbw)




## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
