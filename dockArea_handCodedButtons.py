from pyqtgraph.dockarea import *
from PyQt4 import QtGui, QtCore
from pyqtgraph.dockarea.DockArea import *
from pyqtgraph.dockarea.Dock import *
from pyqtgraph.widgets.VerticalLabel import *

from PyQt4 import Qt
# from PyQt4.QtGui import *


__author__ = 'jhennies'


class MyDockArea(DockArea):
    def __init__(self, *args, **kwargs):
        super(MyDockArea, self).__init__(*args, **kwargs)

    def clear(self):
        docks = self.findAll()[1]
        for dock in docks.values():
            print "CLOSE DOCK"
            if dock.closable:
                dock.close()
            else:
                self.home.moveDock(dock, "top", None)

    def addTempArea(self):
        if self.home is None:
            area = DockArea(temporary=True, home=self)
            self.tempAreas.append(area)
            win = TempAreaWindow(area)
            win.setWindowFlags(Qt.Qt.WindowMinimizeButtonHint)
            area.win = win
            win.show()
        else:
            area = self.home.addTempArea()
        #print "added temp area", area, area.window()
        return area


class MyDock(Dock):

    def __init__(self, name, area=None, size=(10, 10), widget=None, hideTitle=False, autoOrientation=True,
                 closable=False):
        super(MyDock, self).__init__(name, area, size, widget, hideTitle, autoOrientation, closable)

        self.label = MyDockLabel(name, self, closable)
        self.label.sigButtonClick1.connect(self.sig_button_click_1)
        self.label.sigButtonClick2.connect(self.sig_button_click_2)
        self.label.sigButtonClick3.connect(self.sig_button_click_3)

    def sig_button_click_1(self):
        print "Button 1 clicked on " + self._name + "!"

    def sig_button_click_2(self):
        print "Button 2 clicked on " + self._name + "!"

    def sig_button_click_3(self):
        print "Button 3 clicked on " + self._name + "!"


class MyDockLabel(DockLabel):

    sigButtonClick1 = QtCore.Signal()
    sigButtonClick2 = QtCore.Signal()
    sigButtonClick3 = QtCore.Signal()

    def __init__(self, text, dock, showCloseButton):
        super(MyDockLabel, self).__init__(text, dock, showCloseButton)

        self.buttons = [QtGui.QToolButton(self), QtGui.QToolButton(self), QtGui.QToolButton(self)]
        self.buttons[0].setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_ArrowUp))
        self.buttons[0].clicked.connect(self.sigButtonClick1)
        self.buttons[1].setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_ArrowLeft))
        self.buttons[1].clicked.connect(self.sigButtonClick2)
        self.buttons[2].setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_ArrowRight))
        self.buttons[2].clicked.connect(self.sigButtonClick3)

    def resizeEvent(self, ev):
        # if self.Button1:
        #     if self.orientation == 'vertical':
        #         size = ev.size().width()
        #         pos = QtCore.QPoint(0, ev.size().height() - size)
        #     else:
        #         size = ev.size().height()
        #         pos = QtCore.QPoint(0, 0)
        #     self.button1.setFixedSize(QtCore.QSize(size, size))
        #     self.button1.move(pos)
        if self.buttons:
            for i in range(0, len(self.buttons)):
                if self.orientation == 'vertical':
                    size = ev.size().width()
                    pos = QtCore.QPoint(0, ev.size().height() - i*size - size)
                else:
                    size = ev.size().height()
                    pos = QtCore.QPoint(i*size, 0)
                self.buttons[i].setFixedSize(QtCore.QSize(size, size))
                self.buttons[i].move(pos)
        super(MyDockLabel, self).resizeEvent(ev)


########################################################################################################################
# __main__
########################################################################################################################
if __name__ == "__main__":

    app = QtGui.QApplication([])

    mw = QtGui.QMainWindow()
    mw.setWindowTitle('nonClosableDocks')
    area = MyDockArea()
    mw.setCentralWidget(area)
    mw.resize(800, 600)

    d1 = MyDock("Dock1", size=(1, 1), closable=False)     ## give this dock the minimum possible size
    d2 = MyDock("Dock2 - Console", size=(500,300), closable=True)
    d3 = MyDock("Dock3", size=(500,400))
    d4 = MyDock("Dock4 (tabbed) - Plot", size=(500,200))
    d5 = Dock("Dock5 - Image", size=(500,200))
    d6 = Dock("Dock6 (tabbed) - Plot", size=(500,200))

    # Modify docks #####################################################################################################
    # d2.setWindowFlags(Qt.Qt.CustomizeWindowHint)
    # mw.setWindowFlags(Qt.Qt.WindowCloseButtonHint)

    area.addDock(d1, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
    area.addDock(d2, 'right')     ## place d2 at right edge of dock area
    area.addDock(d3, 'bottom', d1)## place d3 at bottom edge of d1
    area.addDock(d4, 'right')     ## place d4 at right edge of dock area
    area.addDock(d5, 'left', d1)  ## place d5 at left edge of d1
    area.addDock(d6, 'top', d4)   ## place d5 at top edge of d4

    mw.show()

    app.exec_()

