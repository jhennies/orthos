from abc import abstractmethod
from pyqtgraph.Qt import QtGui, QtCore
from collections import OrderedDict
from  ..widgets.layer_base_ctrl_widget import *


# request which can be send to a layer

class LayerRequestBase(object):
    def __init__(self):
        pass

class AxisAligned3dBlockRequest(LayerRequestBase):
    def __init__(self):
        super(AxisAligned3dBlockRequest, self).__init__()

class AxisAligned2dBlockRequest(LayerRequestBase):
    def __init__(self):
        super(AxisAligned2dBlockRequest, self).__init__()

class Arbitrary3dBlockRequest(LayerRequestBase):
    def __init__(self):
        super(Arbitrary3dBlockRequest, self).__init__()

class Arbitrary2dBlockRequest(LayerRequestBase):
    def __init__(self):
        super(Arbitrary2dBlockRequest, self).__init__()




class LayerBase(QtCore.QObject):


    sigAlphaChanged = QtCore.Signal(object)
    sigVisibilityChanged = QtCore.Signal(object)
    sigSpatialBoundsChanged = QtCore.Signal(object)
    sigTimeBoundsChanged = QtCore.Signal(object)
    sigLayerZValueChanged = QtCore.Signal(object)
    sigPriorityChanged = QtCore.Signal(object)
    sigNameChanged = QtCore.Signal(object)

    def __init__(self, name, layerZValue, alpha=1.0, visible=True, 
                 spatialBounds=(None,None), 
                 timeBounds=(None,None),priority=1):
        super(LayerBase, self).__init__()
        self.name_ = name
        self.layerZValue_ = layerZValue
        self.alpha_  = alpha
        self.visible_ = visible
        self.spatialBounds_ = spatialBounds
        self.timeBounds_ = timeBounds
        self.priority_ = priority

    def makeCtrlWidget(self):
        return LayerBaseCtrlWidget(layer=self)

    def setName(self, name):
        self.name_ = name
        self.sigNameChanged.emit(self.name_)
    def name(self):
        return self.name_

    def setVisible(self, visible):
        if visible != self.visible_:
            self.visible_ = visible
            self.sigVisibilityChanged.emit(self.visible_)
    def visible(self):
        return self.visible_

    def setAlpha(self, alpha):
        if abs(self.alpha_ - alpha) >= 0.00001:
            self.alpha_ = alpha
            self.sigAlphaChanged.emit(self.alpha_)

    def alpha(self):
        return self.alpha_

    def setSpatialBounds(self, spatialBounds):
        self.spatialBounds_ = spatialBounds
        self.sigSpatialBoundsChanged.emit(self.spatialBounds_)
    def spatialBounds(self):
        return self.spatialBounds_

    def setTimeBounds(self, timeBounds):
        self.timeBounds_ = timeBounds
        self.sigTimeBoundsChanged.emit(self.timeBounds_)
    def timeBounds(self):
        return self.timeBounds_

    def setPriority(self, priority):
        self.priority_ = priority
        self.emit.sigPriorityChanged(self.priority_)
    def priority(self):
        return self.priority_

    def setLayerZValue(self, layerZValue):
        self.layerZValue_ = layerZValue
        self.emit.sigLayerZValueChanged(self.layerZValue)
    def layerZValue(self):
        return self.layerZValue_


class PixelLayerBase(LayerBase):
    def __init__(self, name, layerZValue=1, alpha=1.0, visible=True, 
                 spatialBounds=(None,None,None), 
                 timeBounds=None,priority=1):
        super(PixelLayerBase,self).__init__(name=name, layerZValue=layerZValue, alpha=alpha, 
                           visible=visible,spatialBounds=spatialBounds, 
                           timeBounds=timeBounds,priority=priority)



class GrayscaleLayer(PixelLayerBase):
    def __init__(self,name, dataSource, mult=None):
        self.mult = mult
        self.dataSource = dataSource
        self.shape = self.dataSource.shape
        spatialBounds=((0,0,0), self.shape)
        timeBounds=(0,1)
        super(GrayscaleLayer,self).__init__(name=name,spatialBounds=spatialBounds,timeBounds=timeBounds)

    def request3DBlock(self, spatialSlicing, time):
        #print slicing
        for i,s in enumerate(spatialSlicing):
            if s.start < 0 or s.stop>self.shape[i]:
                return None
        data = self.dataSource[tuple(spatialSlicing)]
        if self.mult is not None:
            data*=self.mult
        data +=time
        return data


class PixelSegmentationEdgeLayerBase(object):
    def __init__(self):
        pass




class PixelLayers(QtCore.QObject):

    
    sigPixelLayerAdded  = QtCore.Signal(object)
    sigPixelLayerRemoved  = QtCore.Signal(object)

    def __init__(self):
        super(PixelLayers,self).__init__()
        self.layers = OrderedDict()

    def addLayer(self, layer):
        self.layers[layer.name()] = layer
        self.sigPixelLayerAdded.emit(layer)

    def removeLayer(self, layer):
        self.layers.pop(layer.name())
        self.sigPixelLayerRemoved.emit(layer)



