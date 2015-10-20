from abc import abstractmethod
from pyqtgraph.Qt import QtGui, QtCore


class DataSourceBase(object):
    def __init__(self):
        pass

class PixelDataSourceBase(DataSourceBase):
    def __init__(self):
        pass




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




class LayerBase(object):


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

        self.name_ = name
        self.layerZValue_ = layerZValue
        self.alpha_  = alpha
        self.visible_ = visible
        self.spatialBounds_ = spatialBounds
        self.timeBounds_ = timeBounds
        self.priority_ = priority


    def setName(self, name):
        self.name_ = name
        self.sigNameChanged.emit(self.name_)
    def name(self):
        return self.name_

    def setVisible(self, visible):
        self.visible_ = visible
        self.sigVisibilityChanged.emit(self.visible_)
    def visible(self):
        return self.visible_

    def setAlpha(self, alpha):
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

class H5PixelLayer(PixelLayerBase):
    def __init__(self, dset, name):

        self.dset = dset
        self.shape = self.dset.shape
        spatialBounds=((0,0,0), self.shape)
        timeBounds=(0,1)
        super(H5PixelLayer,self).__init__(name=name,spatialBounds=spatialBounds,timeBounds=timeBounds)

    def request3Dblock(self, slicing):
        #print slicing
        for i,s in enumerate(slicing):
            if s.start < 0 or s.stop>self.shape[i]:
                return None
        return self.dset[tuple(slicing)]

class PixelSegmentationEdgeLayerBase(object):
    def __init__(self):
        pass




