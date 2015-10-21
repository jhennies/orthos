import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui


class LayerBaseCtrlWidget(QtGui.QWidget):

    def __init__(self, layer):

        super(LayerBaseCtrlWidget,self).__init__()
        self.layer = layer

        # name
        self.layerNameLabel = QtGui.QLabel(layer.name(), self)
        self.layerNameLabel.setFixedWidth(10)
        # is visible
        self.visibleCheckbox = QtGui.QCheckBox('V', self)
        self.visibleCheckbox.setChecked(layer.visible())
        # alpha
        self.alphaSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.alphaSlider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.alphaSlider.setMinimum(0)
        self.alphaSlider.setMaximum(100)
        self.alphaSlider.setSingleStep(1)
        self.alphaSlider.setValue(int(layer.alpha()*100))
        self.alphaSlider.setGeometry(30, 40, 100, 30)
        
        #self.alphaSlider.valueChanged[int].connect(self.changeValue)


        self.setupUI()
        self.connectSignals()
    def setupUI(self):
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.layerNameLabel)
        self.mainLayout.addStretch(0)
        self.mainLayout.addWidget(self.visibleCheckbox)
        self.mainLayout.addWidget(self.visibleCheckbox)
        self.mainLayout.addWidget(self.alphaSlider)

    def connectSignals(self):

        # visibility changed
        def visibleCheckboxChanged(state):
            self.layer.setVisible(bool(state))
        self.visibleCheckbox.stateChanged.connect(visibleCheckboxChanged)


        # alpha slider changed
        def alphaSliderChanged(alpha):
            self.layer.setAlpha(alpha/100.0)
        self.alphaSlider.sliderMoved.connect(alphaSliderChanged)
