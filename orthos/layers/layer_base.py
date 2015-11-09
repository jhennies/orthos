from abc import ABCMeta, abstractmethod
from pyqtgraph.Qt import QtGui, QtCore
from collections import OrderedDict
from  ..widgets.layer_base_ctrl_widget import *
from  ..graphicsItems.linked_view_box.tile_items import *
from  ..parallel import *
import datetime
import time
from orthos_cpp import *
# request which can be send to a layer




def noErrorIfTaskCanceled(future):
    try:
        exp =  future.exception()
        if exp is not None:
           raise exp
    except concurrent.futures.CancelledError:
        pass
    except RuntimeError as e:
        print e


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
        self.pool = QtCore.QThreadPool.globalInstance()
        self.threadPool = ThreadPool(8)

    def makeTileGraphicsItem(self,layer, tileItemGroup):
        raise RuntimeError("not implemented")


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

    def onTileUpdate(self, tileItem):
        raise RuntimeError("Needs to be implemented by derived class")
    def onTileAppear(self, tileItem):
        self.onTileUpdate(tileItem)
    def onTileDisappear(self, tileItem):
        pass
    def onScrollCoordinateChanged(self, tileItem):
        self.onTileUpdate(tileItem)
    def onScrollCoordinateChanged(self, tileItem):
        self.onTileUpdate(tileItem)




class UpdateData(object):
    def __init__(self,tileInfo,ts):
        self.tileInfo = tileInfo
        self.ts = ts



class PixelLayerBase(LayerBase):
    def __init__(self, name, layerZValue=1, alpha=1.0, visible=True, 
                 spatialBounds=(None,None,None), 
                 timeBounds=None,priority=1):
        super(PixelLayerBase,self).__init__(name=name, layerZValue=layerZValue, alpha=alpha, 
                           visible=visible,spatialBounds=spatialBounds, 
                           timeBounds=timeBounds,priority=priority)



class CppLutLayer(PixelLayerBase):

    sigCppLutChanged = QtCore.Signal()
    _sigMinMaxChangedInternal = QtCore.Signal(object, object)
    sigMinMaxChanged = QtCore.Signal(object, object)

    def __init__(self, name, dataSource, cppLut, trackMinMax):

        self.dataSource = dataSource
        self.shape = self.dataSource.shape
        spatialBounds=((0,0,0), self.shape)
        timeBounds=(0,1)

        super(CppLutLayer,self).__init__(name=name,spatialBounds=spatialBounds,timeBounds=timeBounds)

        self.name
        self.dataSource = dataSource
        self.cppLut = cppLut
        self.trackMinMax = trackMinMax
        self.minMax = [None, None]

        # signals
        self._sigMinMaxChangedInternal.connect(self._onMinMaxValChangedInternal)

    def makeTileGraphicsItem(self,layer, tileItemGroup):
        ti = TileImageItem(layer=layer, tileItemGroup=tileItemGroup, cppLut = self.cppLut)
        self.sigAlphaChanged.connect(ti.setOpacity)
        self.sigVisibilityChanged.connect(ti.onChangeLayerVisible)
        self.sigCppLutChanged.connect(ti.cppLutChanged)
        return ti

    def _onMinMaxValChangedInternal(self, minVal, maxVal):
        changes = False
        if  self.minMax[0] is None or minVal<self.minMax[0]:
            self.minMax[0] = minVal 
            changes = True
        if self.minMax[1] is None or maxVal>self.minMax[1]:
            self.minMax[1] = maxVal 
            changes = True
        if changes:
            self.sigMinMaxChanged.emit(minVal, maxVal)
            if isinstance(minVal, (numpy.float32,numpy.float64)):
                self.cppLut.setMinMax(float(minVal),float(maxVal))
            else:
                self.cppLut.setMinMax(long(minVal),long(maxVal))
            self.sigCppLutChanged.emit()

    def onTileUpdate(self, tileItem):

        def fetchData(item, ts, tileInfo, dataSource, oldMinMax):
            if tileInfo == item.tileInfo():
                data = dataSource[tileInfo.slicing3d()].squeeze()
                

                # if levels are automatic, we need to 
                # search for the min max and see if it changed
                if self.trackMinMax :
                    # search min and max simultaneously
                    minVal = data.min()
                    maxVal = data.max()
                    if(oldMinMax[0] is None or minVal<oldMinMax[0] or maxVal>oldMinMax[1]):
                        self._sigMinMaxChangedInternal.emit(minVal, maxVal)

                qimg = item.preRender(data)
                item.setImageToUpdateFrom(data,ts, qimg=qimg)
                d = UpdateData(tileInfo,ts)
                item.updateQueue.sigUpdateFinished.emit(d)


        # add task to pool
        oldMinMax = self.minMax[0], self.minMax[1]
        tileInfo = tileItem.tileInfo().copy()
        ts = time.clock()
        task = Task(fetchData,tileItem, ts,tileInfo, self.dataSource, oldMinMax)
        future = self.threadPool.submit(task=task, onTaskFinished=noErrorIfTaskCanceled)
        # add future to queue
        tileItem.updateQueue.addFuture(future)

    def mouseClickEvent(self, ev, pos2d, clickedViewBox):
        print "layer",self.name(),"clicked at",pos2d


class GrayscaleLayer(CppLutLayer):

    sigGradientEditorChanged = QtCore.Signal(object)


    def __init__(self,name, dataSource, levels='auto', useLut=False, lut='widget'):


        self.levels = levels
        self.useLut = useLut
        self._ctrlWidget = None
        
        self.inputDtype = dataSource.dtype
        if useLut:
            cppLut = ValToRgba.normalizeAndColormap(dtype=self.inputDtype)()
        else:
            cppLut = ValToRgba.normalize(dtype=self.inputDtype)()
        if levels is not 'auto':
            cppLut.setMinMax(levels[0],levels[1])

        super(GrayscaleLayer,self).__init__(name=name,dataSource=dataSource, cppLut=cppLut, trackMinMax=levels=='auto')
        self._ctrlWidget = GrayScaleLayerCtrl(layer=self)
        if useLut:
            elut = self._ctrlWidget.makeLut()
            cppLut.setLutArray(elut)
        
    def makeCtrlWidget(self):
        if self._ctrlWidget is None:
            self._ctrlWidget = GrayScaleLayerCtrl(layer=self)
        return self._ctrlWidget

    def onGradientEditorChanged(self, gi):
        if self.useLut:
            elut = gi.getLookupTable(256,True)
            self.cppLut.setLutArray(elut)
            self.sigCppLutChanged.emit()



class SupervoxelLayer(CppLutLayer):
    def __init__(self,name, dataSource):

    
        self.inputDtype = dataSource.dtype
        cppLut = ValToRgba.intToRandColor(dtype=self.inputDtype)()
        super(SupervoxelLayer,self).__init__(name=name,dataSource=dataSource, cppLut=cppLut, trackMinMax=False)

    def makeCtrlWidget(self):
        return SuperVoxelLayerCtrl(layer=self)

    def onOffsetChanged(self, offset):
        self.cppLut.offset = offset
        self.sigCppLutChanged.emit()


class ObjectLayer(CppLutLayer):
    def __init__(self,name, dataSource, objectLabels = None):

        if objectLabels is None:
            self.objectLabels = Uint32_Uint8_Map()
        
        self.labelColors = [
            [0,0,0,0],
            [255,0,0,255],
            [0,255,0,255],
            [255,0,255,255],
        ]
        self.label = 1
        self.labelColors = numpy.array(self.labelColors,dtype='uint8')
        self.inputDtype = dataSource.dtype
        cppLut = ValToRgba.uintSparseLut(dtype=self.inputDtype)(self.objectLabels)
        cppLut.setLutArray(self.labelColors)
        super(ObjectLayer,self).__init__(name=name,dataSource=dataSource, cppLut=cppLut, trackMinMax=False)



    def makeTileGraphicsItem(self,layer, tileItemGroup):

        def onMouseClickCallback(tileItem, ev):
            pos = ev.pos()
            x = int(pos.x())
            y = int(pos.y())
            spLabel = tileItem.image[x,y]

            label = tileItem.layer.label
            if label == 0 :
                del tileItem.layer.objectLabels[long(spLabel)]
            else:
                tileItem.layer.objectLabels[long(spLabel)] = label
            tileItem.layer.objectLabels[long(spLabel)] = tileItem.layer.label
            tileItem.layer.sigCppLutChanged.emit()


        tileItem = TileImageItem(layer=layer, tileItemGroup=tileItemGroup, cppLut = self.cppLut)
        self.sigAlphaChanged.connect(tileItem.setOpacity)
        self.sigVisibilityChanged.connect(tileItem.onChangeLayerVisible)
        self.sigCppLutChanged.connect(tileItem.cppLutChanged)
        tileItem.onMouseClickCallback = onMouseClickCallback
        return tileItem

    def makeCtrlWidget(self):
        return ObjectLayerCtrl(layer=self)

    def onOffsetChanged(self, offset):
        self.cppLut.offset = offset
        self.sigCppLutChanged.emit()

    def onLabelChanged(self, label):
        self.label = label










class PaintLayer(CppLutLayer):


    sigLabelChanged = QtCore.Signal(object)
    sigBrushSizeChanged = QtCore.Signal(object)


    def __init__(self,name, dataSource):


        self.labelColors = [
            [0,0,0,0],
            [255,0,0,255],
            [0,255,0,255],
            [0,0,255,255],
        ]
        self.labelColors = numpy.array(self.labelColors,dtype='uint8')
        
        self.inputDtype = dataSource.dtype
        cppLut = ValToRgba.uintColormap(self.inputDtype)()
        cppLut.setLutArray(self.labelColors)
        super(PaintLayer,self).__init__(name=name,dataSource=dataSource, cppLut=cppLut, trackMinMax=False)


        
    @abstractmethod
    def makeTileGraphicsItem(self,layer, tileItemGroup):
        ti = TilePaintImage(layer=layer, tileItemGroup=tileItemGroup,labelColors=self.labelColors,cppLut=self.cppLut)
        self.sigAlphaChanged.connect(ti.setOpacity)
        self.sigVisibilityChanged.connect(ti.onChangeLayerVisible)
        self.sigLabelChanged.connect(ti.onLabelChanged)
        self.sigBrushSizeChanged.connect(ti.onBrushSizeChanged)
        return ti

    def makeCtrlWidget(self):
        return PaintLayerCtrl(layer=self)


    def onLabelChanged(self, label):
        self.sigLabelChanged.emit(label)

    def onBrushSizeChanged(self, size):
        self.sigBrushSizeChanged.emit(size)




    def writeLabelsToDataSource(self, labelsBlock, labelsBlockBegin):
        
        slicing = [ ]
        labelsBlockEnd = [0,0,0]
        for i in range(3):
            s =slice(labelsBlockBegin[i],labelsBlockBegin[i]+labelsBlock.shape[i])
            labelsBlockEnd[i] = labelsBlockBegin[i]+labelsBlock.shape[i]
            slicing.append(s)
        
        whereLabels = numpy.where(labelsBlock!=0)
        print "passed block",labelsBlock.shape
        print slicing

        oldLabels = self.dataSource[tuple(slicing)]

        print "OLD LABELS SHAPE",oldLabels.shape

        newLabels = oldLabels
        newLabels[whereLabels] = labelsBlock[whereLabels]
        newLabels[newLabels==255] = 0
        self.dataSource.commitSubarray(labelsBlockBegin,newLabels)

        
        for tileGrid in self.viewer.yieldTileGrids():
            tileGrid.updateTiles(roi3D=(labelsBlockBegin,labelsBlockEnd))



















class PixelLayers(QtCore.QObject):

    
    sigPixelLayerAdded  = QtCore.Signal(object)
    sigPixelLayerRemoved  = QtCore.Signal(object)

    def __init__(self):
        super(PixelLayers,self).__init__()
        self.layers = OrderedDict()
        self.viewer = None

    def addLayer(self, layer):
        self.layers[layer.name()] = layer
        layer.viewer = self.viewer
        self.sigPixelLayerAdded.emit(layer)

    def removeLayer(self, layer):
        self.layers.pop(layer.name())
        self.sigPixelLayerRemoved.emit(layer)


    def mouseClickEvent(self, ev, pos2d, clickedViewBox):
        #print "click in pixel layers"
        for layerName in self.layers:
            self.layers[layerName].mouseClickEvent(ev, pos2d, clickedViewBox)
