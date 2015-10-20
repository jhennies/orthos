from abc import abstractmethod



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
    sigVisibilityChanged = QCore.Signal(object)
    sigSpatialBoundsChanged = QCore.Signal(object)
    sigTimeBoundsChanged = QCore.Signal(object)
    sigLayerZValueChanged = QCore.Signal(object)
    sigPriorityChanged = QCore.Signal(object)
    sigNameChanged = QCore.Signal(object)

    def __init__(self, name, layerZValue, alpha=1.0, visible=True, 
                 spatialBounds=(None,None,None), 
                 timeBounds=None,priority=1):

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


class PixelLayerBase(object):
    def __init__(self):
        pass

class PixelSegmentationEdgeLayerBase(object):
    def __init__(self):
        pass




