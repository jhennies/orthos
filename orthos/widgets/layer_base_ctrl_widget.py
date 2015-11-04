import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.graphicsItems

class FractionSelectionBar( QtGui.QWidget ):
    fractionChanged = QtCore.Signal(float)

    def __init__( self, initial_fraction=1., parent=None ):
        super(FractionSelectionBar, self).__init__( parent=parent )
        self._fraction = initial_fraction
        self._lmbDown = False

    def fraction( self ):
        return self._fraction

    def setFraction( self, value ):
        if value == self._fraction:
            return
        if(value < 0.):
            value = 0.
            warnings.warn("FractionSelectionBar.setFraction(): value has to be between 0. and 1. (was %s); setting to 0." % str(value))
        if(value > 1.):
            value = 1.
            warnings.warn("FractionSelectionBar.setFraction(): value has to be between 0. and 1. (was %s); setting to 1." % str(value))
        self._fraction = float(value)
        self.update()

    def mouseMoveEvent(self, event):
        if self._lmbDown:
            self.setFraction(self._fractionFromPosition( event.posF() ))
            self.fractionChanged.emit(self._fraction)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            return
        self._lmbDown = True
        self.setFraction(self._fractionFromPosition( event.posF() ))
        self.fractionChanged.emit(self._fraction)

    def mouseReleaseEvent(self, event):
        self._lmbDown = False

    def paintEvent( self, ev ):
        painter = QtGui.QPainter(self)

        # calc bar offset
        y_offset =(self.height() - self._barHeight()) // 2
        ## prevent negative offset
        y_offset = 0 if y_offset < 0 else y_offset

        # frame around fraction indicator
        painter.setBrush(self.palette().dark())
        painter.save()
        ## no fill color
        b = painter.brush(); b.setStyle(QtCore.Qt.NoBrush); painter.setBrush(b)
        painter.drawRect(
            QtCore.QRect(QtCore.QPoint(0, y_offset),
                  QtCore.QSize(self._barWidth(), self._barHeight())))
        painter.restore()

        # fraction indicator
        painter.drawRect(
            QtCore.QRect(QtCore.QPoint(0, y_offset),
                  QtCore.QSize(self._barWidth()*self._fraction, self._barHeight())))

    def sizeHint( self ):
        return QtCore.QSize(100, 10)

    def minimumSizeHint( self ):
        return QtCore.QSize(1, 3)

    def _barWidth( self ):
        return self.width()-1

    def _barHeight( self ):
        return self.height()-1

    def _fractionFromPosition( self, pointf ):
        frac = pointf.x() / self.width()
        # mouse has left the widget
        if frac < 0.:
            frac = 0.
        if frac > 1.:
            frac = 1.
        return frac

class ToggleEye( QtGui.QLabel ):
    activeChanged = QtCore.Signal(bool)

    def __init__( self, parent=None ):
        super(ToggleEye, self).__init__( parent=parent )
        self._active = True
        self._eye_open = QtGui.QPixmap(":icons/icons/stock-eye-20.png")
        self._eye_closed = QtGui.QPixmap(":icons/icons/stock-eye-20-gray.png")
        self.setPixmap(self._eye_open)

    def active( self ):
        return self._active

    def setActive( self, b ):
        if b == self._active:
            return
        self._active = b
        if b:
            self.setPixmap(self._eye_open)
        else:
            self.setPixmap(self._eye_closed)

    def toggle( self ):
        if self.active():
            self.setActive( False )
        else:
            self.setActive( True )

    def mousePressEvent( self, ev ):
        self.toggle()
        self.activeChanged.emit( self._active )


class LayerItemWidget( QtGui.QWidget ):
    @property
    def layer(self):
        return self._layer


    def __init__( self,layer, parent=None ):
        super(LayerItemWidget, self).__init__( parent=parent )
        self._layer = layer

        self._font = QtGui.QFont(QtGui.QFont().defaultFamily(), 9)
        self._fm = QtGui.QFontMetrics( self._font )
        self.bar = FractionSelectionBar( initial_fraction = layer.alpha() )
        self.bar.setFixedHeight(10)
        self.nameLabel = QtGui.QLabel( parent=self )
        self.nameLabel.setFont( self._font )
        self.nameLabel.setText( "None" )
        self.opacityLabel = QtGui.QLabel( parent=self )
        self.opacityLabel.setAlignment(QtCore.Qt.AlignRight)
        self.opacityLabel.setFont( self._font )
        self.opacityLabel.setText( u"\u03B1=%0.1f%%" % (100.0*(self.bar.fraction())))
        self.toggleEye = ToggleEye( parent=self )
        self.toggleEye.setActive(layer.visible())
        self.toggleEye.setFixedWidth(35)
        self.toggleEye.setToolTip("Visibility")
        self.channelSelector = QtGui.QSpinBox( parent=self )
        self.channelSelector.setFrame( False )
        self.channelSelector.setFont( self._font )
        self.channelSelector.setMaximumWidth( 35 )
        self.channelSelector.setAlignment(QtCore.Qt.AlignRight)
        self.channelSelector.setToolTip("Channel")
        self.channelSelector.setVisible(False)

        self._layout = QtGui.QGridLayout( self )
        self._layout.addWidget( self.toggleEye, 0, 0 )
        self._layout.addWidget( self.nameLabel, 0, 1 )
        self._layout.addWidget( self.opacityLabel, 0, 2 )
        self._layout.addWidget( self.channelSelector, 1, 0)
        self._layout.addWidget( self.bar, 1, 1, 1, 2 )

        self._layout.setColumnMinimumWidth( 0, 35 )
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(5,2,5,2)

        self.setLayout( self._layout )

        #self.bar.fractionChanged.connect( self._onFractionChanged )
        #self.toggleEye.activeChanged.connect( self._onEyeToggle )
        self.channelSelector.valueChanged.connect( self._onChannelChanged )

    def mousePressEvent( self, ev ):
        super(LayerItemWidget, self).mousePressEvent( ev )

    #def _onFractionChanged( self, fraction ):
    #    if self._layer and (fraction != self._layer.opacity):
    #        self._layer.opacity = fraction

    #def _onEyeToggle( self, active ):
    #    if self._layer and (active != self._layer.visible):
    #        
    #        if self._layer._allowToggleVisible:
    #            self._layer.visible = active
    #        else:
    #            self.toggleEye.setActive(True)

    def _onChannelChanged( self, channel ):
        if self._layer and (channel != self._layer.channel):
            self._layer.channel = channel

    def _updateState( self ):
        if self._layer:
            self.toggleEye.setActive(self._layer.visible)
            self.bar.setFraction( self._layer.opacity )
            self.opacityLabel.setText( u"\u03B1=%0.1f%%" % (100.0*(self.bar.fraction())))
            self.nameLabel.setText( self._layer.name )
            
            if self._layer.numberOfChannels > 1:
                self.channelSelector.setVisible( True )
                self.channelSelector.setMaximum( self._layer.numberOfChannels - 1 )
                self.channelSelector.setValue( self._layer.channel )
            else:
                self.channelSelector.setVisible( False )
                self.channelSelector.setMaximum( self._layer.numberOfChannels - 1)
                self.channelSelector.setValue( self._layer.channel )
            self.update()



class LayerBaseCtrlWidget(QtGui.QWidget):

    def __init__(self, layer):

        super(LayerBaseCtrlWidget,self).__init__()
        self.layer = layer

        self.basicCtrl = LayerItemWidget(layer=layer)
        self.basicCtrl.nameLabel.setText(self.layer.name())


        self.setupUI2()
        self.connectSignals2()

    def setupUI2(self):
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.basicCtrl)
    def connectSignals2(self):
        # visibility changed
        def visibleCheckboxChanged(state):
            self.layer.setVisible(bool(state))
        self.basicCtrl.toggleEye.activeChanged.connect(visibleCheckboxChanged)


        # alpha slider changed
        def alphaSliderChanged(alpha):
            self.layer.setAlpha(alpha)
        self.basicCtrl.bar.fractionChanged.connect(alphaSliderChanged)




class GrayScaleLayerCtrl(LayerBaseCtrlWidget):

    def __init__(self, layer):

        super(GrayScaleLayerCtrl,self).__init__(layer=layer)
        self.gradientWidget = pg.GradientWidget()
        d = {'ticks': [(0.0, (165, 0, 60, 255)), (1.0, (0, 170, 60, 255))], 'mode': 'rgb'}
        d = pg.graphicsItems.GradientEditorItem.Gradients['grey']
        self.gradientWidget.restoreState(d)

        self.setupUI()
        self.connectSignals()

    def setupUI(self):
        #self.gradientWidget.setFixedHeight(15)
        self.mainLayout.addWidget(self.gradientWidget)
    def connectSignals(self):
        def gradientEditorChanged(editor):
            self.layer.onGradientEditorChanged(editor)
        self.gradientWidget.sigGradientChanged.connect(gradientEditorChanged)




class PaintLayerCtrl(LayerBaseCtrlWidget):

    def __init__(self, layer):

        super(PaintLayerCtrl,self).__init__(layer=layer)


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


        self.layerItemWidget = LayerItemWidget(layer)
        self.layerItemWidget.nameLabel.setText(self.layer.name())

        self.setupUI()
        self.connectSignals()

    def setupUI(self):
       

        baseLayout = QtGui.QHBoxLayout()
        baseLayout.addWidget(self.labelSpinBox)
        baseLayout.addWidget(self.brushSizeSlider)
        self.mainLayout.addLayout(baseLayout)

    def connectSignals(self):

        # label spinbox changed
        def labelSpinBoxChanged(label):
            self.layer.onLabelChanged(label)
        self.labelSpinBox.valueChanged.connect(labelSpinBoxChanged)

        # brushsize slider changed
        def brushSizeSliderChanged(size):
            self.layer.onBrushSizeChanged(size)
        self.brushSizeSlider.sliderMoved.connect(brushSizeSliderChanged)
