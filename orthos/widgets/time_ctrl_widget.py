import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui


class TimeCtrlWidget(QtGui.QWidget):
    def __init__(self, navigator):
        super(TimeCtrlWidget,self).__init__()
        self.navigator = navigator
        # alpha
        self.timeSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        #self.timeSlider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.timeSlider.setMinimum(0)
        self.timeSlider.setMaximum(100)
        self.timeSlider.setSingleStep(1)
        self.timeSlider.setValue(0)
        #self.timeSlider.setGeometry(30, 40, 100, 30)

        # alpha slider changed
        def timeSliderChanged(newTime):
            self.navigator.onTimeChanged(newTime)
        self.timeSlider.sliderMoved.connect(timeSliderChanged)


        self.setupUI()
    def setupUI(self):
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.timeSlider)
        
        #self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
