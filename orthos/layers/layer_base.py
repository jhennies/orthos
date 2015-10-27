from abc import ABCMeta, abstractmethod
from pyqtgraph.Qt import QtGui, QtCore
from collections import OrderedDict
from  ..widgets.layer_base_ctrl_widget import *
from  ..graphicsItems.linked_view_box.tile_items import *
from  ..parallel import *
import datetime
import time
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
        self.pool = QtCore.QThreadPool.globalInstance()
        self.threadPool = ThreadPool(8)

    def makeTileGraphicsItem(self):
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


    def onTileAppear(self, tileItem, bi):
        raise RuntimeError("not implemented")
    def onTileDisappear(self, tileItem):
        raise RuntimeError("not implemented")


class PixelLayerBase(LayerBase):
    def __init__(self, name, layerZValue=1, alpha=1.0, visible=True, 
                 spatialBounds=(None,None,None), 
                 timeBounds=None,priority=1):
        super(PixelLayerBase,self).__init__(name=name, layerZValue=layerZValue, alpha=alpha, 
                           visible=visible,spatialBounds=spatialBounds, 
                           timeBounds=timeBounds,priority=priority)




class UpdateData(object):
    def __init__(self,data,pos,ts):
        self.data = data
        self.pos = pos
        self.ts = ts





class GrayscaleLayer(PixelLayerBase):

    sigGradientEditorChanged = QtCore.Signal(object)

    def __init__(self,name, levels,dataSource, mult=None):
        self.mult = mult
        self.dataSource = dataSource
        self.shape = self.dataSource.shape
        self.levels = levels
        spatialBounds=((0,0,0), self.shape)
        timeBounds=(0,1)
        super(GrayscaleLayer,self).__init__(name=name,spatialBounds=spatialBounds,timeBounds=timeBounds)

    @abstractmethod
    def makeTileGraphicsItem(self):
        ti = TileImageItem()
        self.sigAlphaChanged.connect(ti.setOpacity)
        self.sigVisibilityChanged.connect(ti.onChangeLayerVisible)
        self.sigGradientEditorChanged.connect(ti.setLookupTable)
        return ti

    def makeCtrlWidget(self):
        return GrayScaleLayerCtrl(layer=self)

    def onGradientEditorChanged(self, gi):
        lut = gi.getLookupTable(256)
        self.sigGradientEditorChanged.emit(lut)

    def onTileAppear(self, tileItem):
        spatialSlicing,blockBegin,blockEnd = tileItem.make3dSlicingAndBlockBegin()

        sc = tileItem.viewBox.scrollCoordinate
        tc = tileItem.viewBox.timeCoordinate
        def fetchData(ts, spatialSlicing,blockBegin, dataSource,item,sc,tc):
            nsc = item.viewBox.scrollCoordinate
            ntc = item.viewBox.timeCoordinate
            if sc == nsc and tc == ntc and item.tileVisible():
                data = dataSource[tuple(spatialSlicing)].squeeze()
                item.setImageToUpdateFrom(data,ts)
                d = UpdateData(None,blockBegin,ts)
                item.updateQueue.sigUpdateFinished.emit(d)


        def onTaskFinished(future, item, blockBegin):
            try:
                exp =  future.exception()
                if exp is not None:
                   raise exp
            except concurrent.futures.CancelledError:
                pass
            except RuntimeError as e:
                print e
            #item.updateQueue.sigUpdateFinished.emit(blockBegin)

        ts = time.clock()
        task = Task(fetchData,ts,spatialSlicing,blockBegin,self.dataSource, tileItem,sc,tc)
        onF = partial(onTaskFinished,item=tileItem, blockBegin=blockBegin)
        future = self.threadPool.submit(task=task, onTaskFinished=None)

        # add future to UpdateQueue
        tileItem.updateQueue.addFuture(future)





    def onTileScrollCoordinateChanged(self, tileItem,coord):
        assert tileItem.blockCoord is not None
        self.onTileAppear(tileItem)

    def onTileDisappear(self, tileItem):
        #print self.name(),"disappear"
        pass



    def mouseClickEvent(self, ev, pos2d, clickedViewBox):
        print "layer",self.name(),"clicked at",pos2d





class PaintLayer(PixelLayerBase):

    sigBrushSizeChanged = QtCore.Signal(object)
    sigLabelChanged = QtCore.Signal(object)


    def __init__(self,name,dataSource):


        self.labelColors = [
            [0,0,0],
            [255,0,0],
            [0,255,0],
            [255,0,255],
        ]

        self.dataSource = dataSource
        self.shape = dataSource.shape
        spatialBounds=((0,0,0), self.shape)
        timeBounds=(0,1)
        super(PaintLayer,self).__init__(name=name,spatialBounds=spatialBounds,timeBounds=timeBounds)

        self.paintRad = 0

    @abstractmethod
    def makeTileGraphicsItem(self):
        ti = TilePaintImage(labelColors=self.labelColors)
        self.sigAlphaChanged.connect(ti.setOpacity)
        self.sigVisibilityChanged.connect(ti.onChangeLayerVisible)
        self.sigLabelChanged.connect(ti.onLabelChanged)
        self.sigBrushSizeChanged.connect(ti.onBrushSizeChanged)
        return ti

    def onLabelChanged(self, label):
        self.sigLabelChanged.emit(label)

    def onBrushSizeChanged(self, size):
        self.sigBrushSizeChanged.emit(size)

    def makeCtrlWidget(self):
        return PaintLayerCtrl(layer=self)



    def onTileAppear(self, tileItem):
        spatialSlicing,blockBegin,blockEnd = tileItem.make3dSlicingAndBlockBegin()
        tileItem.setPos(*blockBegin)

        #s2d = tileItem.shape2d()
        #imgShape = s2d + (3,)
        #dataRGBA = numpy.zeros(imgShape,dtype='uint8')



        sc = tileItem.viewBox.scrollCoordinate
        tc = tileItem.viewBox.timeCoordinate
        def fetchData(ts, spatialSlicing,blockBegin, dataSource,item,sc,tc):
            nsc = item.viewBox.scrollCoordinate
            ntc = item.viewBox.timeCoordinate
            if sc == nsc and tc == ntc and item.tileVisible():
                data = dataSource[tuple(spatialSlicing)].squeeze()
                whereLabels = numpy.where(data!=0)
                #print whereLabels

                s2d = item.shape2d()
                imgShape = s2d + (4,)


                lut = numpy.array(self.labelColors)
                dataRGBA = numpy.zeros(imgShape,dtype='uint8')
                dataRGBA[:,:,0:3] = numpy.take(lut, data, axis=0, mode='clip') 
                dataA   = dataRGBA[:,:,3] 
                #dataRGB[whereLabels] = 255,255,255
                dataA[whereLabels] = 255
                item.setImageToUpdateFrom(dataRGBA,ts)
                d = UpdateData(None,blockBegin,ts)
                item.updateQueue.sigUpdateFinished.emit(d)
        def onTaskFinished(future):#, item, blockBegin):
            try:
                exp =  future.exception()
                if exp is not None:
                   raise exp
            except concurrent.futures.CancelledError:
                pass
            except RuntimeError as e:
                print e
            #item.updateQueue.sigUpdateFinished.emit(blockBegin)
        ts = time.clock()
        task = Task(fetchData,ts,spatialSlicing,blockBegin,self.dataSource, tileItem,sc,tc)
        onF = partial(onTaskFinished,item=tileItem, blockBegin=blockBegin)
        future = self.threadPool.submit(task=task, onTaskFinished=onTaskFinished)
        # add future to UpdateQueue
        tileItem.updateQueue.addFuture(future)


    def writeLabelsToDataSource(self, labelsBlock, labelsBlockBegin):
        
        slicing = [ ]
        for i in range(3):
            s =slice(labelsBlockBegin[i],labelsBlockBegin[i]+labelsBlock.shape[i])
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

        self.dataSource.chunkedArray.flush()
    



    def onTileScrollCoordinateChanged(self, tileItem,coord):
        assert tileItem.blockCoord is not None
        self.onTileAppear(tileItem)

    def onTileDisappear(self, tileItem):
        #print self.name(),"disappear"
        pass



    def mouseClickEvent(self, ev, pos2d, clickedViewBox):
        #print "layer",self.name(),"clicked at",pos2d
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


    def mouseClickEvent(self, ev, pos2d, clickedViewBox):
        #print "click in pixel layers"
        for layerName in self.layers:
            self.layers[layerName].mouseClickEvent(ev, pos2d, clickedViewBox)
