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




class GrayScaleLayerCtrl(QtGui.QWidget):

    def __init__(self, layer):

        super(GrayScaleLayerCtrl,self).__init__()
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
        self.gradientWidget = pg.GradientWidget()

        self.setupUI()
        self.connectSignals()
    def setupUI(self):
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.baseLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.baseLayout)
        self.baseLayout.addWidget(self.layerNameLabel)
        self.baseLayout.addStretch(0)
        self.baseLayout.addWidget(self.visibleCheckbox)
        self.baseLayout.addWidget(self.visibleCheckbox)
        self.baseLayout.addWidget(self.alphaSlider)


        self.baseLayout2 = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.baseLayout2)
        self.baseLayout2.addWidget(self.gradientWidget)
    def connectSignals(self):

        # visibility changed
        def visibleCheckboxChanged(state):
            self.layer.setVisible(bool(state))
        self.visibleCheckbox.stateChanged.connect(visibleCheckboxChanged)


        # alpha slider changed
        def alphaSliderChanged(alpha):
            self.layer.setAlpha(alpha/100.0)
        self.alphaSlider.sliderMoved.connect(alphaSliderChanged)


        # gradient editor
        def gradientEditorChanged(editor):
            self.layer.onGradientEditorChanged(editor)
        self.gradientWidget.sigGradientChanged.connect(gradientEditorChanged)




class PaintLayerCtrl(QtGui.QWidget):

    def __init__(self, layer):

        super(PaintLayerCtrl,self).__init__()
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
      

        # active label spin box
        self.labelSpinBox = QtGui.QSpinBox()
        self.labelSpinBox.setValue(1)
        self.labelSpinBox.setMinimum(0)
        self.labelSpinBox.setMaximum(10)

        # brushsize slider
        self.brushSizeSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.brushSizeSlider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.brushSizeSlider.setMinimum(0)
        self.brushSizeSlider.setMaximum(10)
        self.brushSizeSlider.setSingleStep(1)
        self.brushSizeSlider.setValue(0)
        self.brushSizeSlider.setGeometry(30, 40, 100, 30)




        self.setupUI()
        self.connectSignals()
    def setupUI(self):
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.baseLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.baseLayout)
        self.baseLayout.addWidget(self.layerNameLabel)
        self.baseLayout.addStretch(0)
        self.baseLayout.addWidget(self.visibleCheckbox)
        self.baseLayout.addWidget(self.visibleCheckbox)
        self.baseLayout.addWidget(self.alphaSlider)


        self.baseLayout2 = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.baseLayout2)
        self.baseLayout2.addWidget(self.labelSpinBox)
        self.baseLayout2.addWidget(self.brushSizeSlider)
    def connectSignals(self):

        # visibility changed
        def visibleCheckboxChanged(state):
            self.layer.setVisible(bool(state))
        self.visibleCheckbox.stateChanged.connect(visibleCheckboxChanged)


        # alpha slider changed
        def alphaSliderChanged(alpha):
            self.layer.setAlpha(alpha/100.0)
        self.alphaSlider.sliderMoved.connect(alphaSliderChanged)

        # label spinbox changed
        def labelSpinBoxChanged(label):
            self.layer.onLabelChanged(label)
        self.labelSpinBox.valueChanged.connect(labelSpinBoxChanged)

        # brushsize slider changed
        def brushSizeSliderChanged(size):
            self.layer.onBrushSizeChanged(size)
        self.brushSizeSlider.sliderMoved.connect(brushSizeSliderChanged)
