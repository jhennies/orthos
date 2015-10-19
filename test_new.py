import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import orthos
from orthos.widgets import *
from pyqtgraph.dockarea import *


app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.setWindowTitle('pyqtgraph example: ViewBox')
mw.show()
mw.resize(800, 600)

[x,y,z] = linked3dViewBoxWidgets()

area = DockArea()
mw.setCentralWidget(area)

for vbw in [x,y,z] :
    d = Dock("a dock")
    area.addDock(d)
    d.addWidget(vbw)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
