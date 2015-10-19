from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="The disappearing line act")
win.resize(800,800)




x = [0,1,2]
y = [0,1,2]
p1 = win.addPlot(x=x,y=y)
p1.showGrid(x=True, y=True)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
