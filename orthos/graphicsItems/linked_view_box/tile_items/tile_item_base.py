from collections import deque
import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import threading
import datetime
import time
import collections
import vigra
from ....core import *
from orthos_cpp import *

def make3dSlicing_(begin,end):
    slicing = []
    for b,e in zip(begin, end):
        slicing.append(slice(b,e))
    return slicing









class ImageItemBase(pg.ImageItem):
    def __init__(self, cppLut):
        self.brect__ = QtCore.QRectF(0., 0., 0., 0.,)
        super(ImageItemBase, self).__init__()
        self.cppLut = cppLut
    def setImage(self, image=None, autoLevels=None,qimg=None, **kargs):
        """
        Update the image displayed by this item. For more information on how the image
        is processed before displaying, see :func:`makeARGB <pyqtgraph.makeARGB>`
        
        =================  =========================================================================
        **Arguments:**
        image              (numpy array) Specifies the image data. May be 2D (width, height) or 
                           3D (width, height, RGBa). The array dtype must be integer or floating
                           point of any bit depth. For 3D arrays, the third dimension must
                           be of length 3 (RGB) or 4 (RGBA).
        autoLevels         (bool) If True, this forces the image to automatically select 
                           levels based on the maximum and minimum values in the data.
                           By default, this argument is true unless the levels argument is
                           given.
        lut                (numpy array) The color lookup table to use when displaying the image.
                           See :func:`setLookupTable <pyqtgraph.ImageItem.setLookupTable>`.
        levels             (min, max) The minimum and maximum values to use when rescaling the image
                           data. By default, this will be set to the minimum and maximum values 
                           in the image. If the image array has dtype uint8, no rescaling is necessary.
        opacity            (float 0.0-1.0)
        compositionMode    see :func:`setCompositionMode <pyqtgraph.ImageItem.setCompositionMode>`
        border             Sets the pen used when drawing the image border. Default is None.
        autoDownsample     (bool) If True, the image is automatically downsampled to match the
                           screen resolution. This improves performance for large images and 
                           reduces aliasing.
        =================  =========================================================================
        """
        #profile = debug.#Profiler()

        gotNewData = False
        if image is None:
            if self.image is None:
                return
        else:
            gotNewData = True
            shapeChanged = (self.image is None or image.shape != self.image.shape)
            self.image = image.view(np.ndarray)
            if self.image.shape[0] > 2**15-1 or self.image.shape[1] > 2**15-1:
                if 'autoDownsample' not in kargs:
                    kargs['autoDownsample'] = True
            if shapeChanged:
                self.brect__ = QtCore.QRectF(0., 0., float(self.image.shape[0]), float(self.image.shape[1]))
                self.prepareGeometryChange()
                self.informViewBoundsChanged()

        #profile()

        if autoLevels is None:
            if 'levels' in kargs:
                autoLevels = False
            else:
                autoLevels = True
        if autoLevels:
            img = self.image
            while img.size > 2**16:
                img = img[::2, ::2]
            mn, mx = img.min(), img.max()
            if mn == mx:
                mn = 0
                mx = 255
            kargs['levels'] = [mn,mx]

        #profile()

        self.setOpts(update=False, **kargs)

        #profile()
        if qimg is None:
            self.qimage = None
        else:
            self.qimage = qimg
        self.update()

        #profile()

        if gotNewData:
            self.sigImageChanged.emit()



    def updateImage(self, *args, **kargs):
        ## used for re-rendering qimage from self.image.
        
        ## can we make any assumptions here that speed things up?
        ## dtype, range, size are all the same?
        defaults = {
            'autoLevels': False,
        }
        defaults.update(kargs)
        return self.setImage(*args, **defaults)
    def render2(self):
        #Convert data to QImage for display.
        
        #profile = debug.Profiler()
        if self.image is None or self.image.size == 0:
            return
        if isinstance(self.lut, collections.Callable):
            lut = self.lut(self.image)
        else:
            lut = self.lut

        if False:#self.autoDownsample:
            # reduce dimensions of image based on screen resolution
            o = self.mapToDevice(QtCore.QPointF(0,0))
            x = self.mapToDevice(QtCore.QPointF(1,0))
            y = self.mapToDevice(QtCore.QPointF(0,1))
            w = Point(x-o).length()
            h = Point(y-o).length()
            xds = int(1/max(1, w))
            yds = int(1/max(1, h))
            image = pg.downsample(self.image, xds, axis=0)
            image = pg.downsample(image, yds, axis=1)
        else:
            image = self.image
        
        argb, alpha =  pg.makeARGB(image.transpose((1, 0, 2)[:image.ndim]), lut=lut, levels=self.levels)
        self.qimage = pg.makeQImage(argb, alpha, transpose=False)

    def render(self):
        #Convert data to QImage for display.
        
        #profile = debug.Profiler()
        if self.image is None or self.image.size == 0:
            return
        if isinstance(self.lut, collections.Callable):
            lut = self.lut(self.image)
        else:
            lut = self.lut

        if False:#self.autoDownsample:
            # reduce dimensions of image based on screen resolution
            o = self.mapToDevice(QtCore.QPointF(0,0))
            x = self.mapToDevice(QtCore.QPointF(1,0))
            y = self.mapToDevice(QtCore.QPointF(0,1))
            w = Point(x-o).length()
            h = Point(y-o).length()
            xds = int(1/max(1, w))
            yds = int(1/max(1, h))
            image = pg.downsample(self.image, xds, axis=0)
            image = pg.downsample(image, yds, axis=1)
        else:
            image = self.image


        
        imageRGBA = makeRGBAImage(image,self.cppLut)
        imageNew = imageRGBA
        argb, alpha =  pg.makeARGB(imageNew.transpose((1, 0, 2)[:imageNew.ndim]), lut=None, levels=None)
        self.qimage = pg.makeQImage(argb, alpha, transpose=False)


    def preRender(self, image):
        imageRGBA = makeRGBAImage(image,self.cppLut)
        imageNew = imageRGBA
        argb, alpha =  pg.makeARGB(imageNew.transpose((1, 0, 2)[:imageNew.ndim]), lut=None, levels=None)
        self.qimage = pg.makeQImage(argb, alpha, transpose=False)

    def cppLutChanged(self):
        self.qimage = None
        self.update()



    def boundingRect(self):
        return self.brect__















class UpdateQueue(QtCore.QObject):
    
    sigUpdateFinished  = QtCore.Signal(object)

    def __init__(self,item):
        super(UpdateQueue,self).__init__()

        self.futuresLock = threading.Lock()  
        self.item = item
        self.sigUpdateFinished.connect(self.item.onUpdateFinished)
        self.futures = []

    def addFuture(self, newFuture):
        #self.futuresLock.acquire()
        stillRunning = [ ]
        # check all existing futures and remove finished ones
        # and try to cancel all others
        for i in range(len(self.futures)):
            future = self.futures[i]
            if future.done():
                pass
            else:
                # try to cancel
                isCanceled = future.cancel()
                if not isCanceled:
                    stillRunning.append(future)
        stillRunning.append(newFuture)
        self.futures = stillRunning
        #self.futuresLock.release()



class TileItemMixIn(object):
    def __init__(self, layer, tileItemGroup):
        super(TileItemMixIn, self).__init__()
        self.updateQueue = UpdateQueue(self)
        self.layerVisible_ = True
        self.layer = layer
        self.tileItemGroup = tileItemGroup


    #@property
    def tileVisible(self):
        assert self.tileItemGroup is not None
        return self.tileItemGroup.tileVisible
    @property
    def roi2d(self):
        assert self.tileItemGroup is not None
        return self.tileItemGroup.roi2d
    @property
    def roi3d(self):
        assert self.tileItemGroup is not None
        return self.tileItemGroup.roi3d
    @property
    def scrollCoordinate(self):
        assert self.tileItemGroup is not None
        return self.tileItemGroup.scrollCoordinate
    @property
    def timeCoordinate(self):
        assert self.tileItemGroup is not None
        return self.tileItemGroup.timeCoordinate

    def tileInfo(self):
        return self.tileItemGroup.tileInfo
    




    def onTileUpdate(self):
        self.layer.onTileAppear(self)

    def onTileAppear(self):
        self.onChangeTileVisible(True)
        self.layer.onTileAppear(self)

    def onTileDisappear(self):
        self.onChangeTileVisible(False)
        self.layer.onTileDisappear(self)

    def onScrollCoordinateChanged(self):
        self.layer.onScrollCoordinateChanged(self)

    def onTimeCoordinateChanged(self):
        self.layer.onTimeCoordinateChanged(self)




    def onChangeLayerVisible(self, visible):
        self.layerVisible_ = visible
        if visible:
            if self.tileVisible():
                self.setVisible(True)
                self.setEnabled(True)
            else:
                self.setVisible(False)
                self.setEnabled(False)
        else:
            self.setVisible(False)
            self.setEnabled(False)

    def onChangeTileVisible(self, visible):
        if visible :
            if self.layerVisible_:
                self.setVisible(True)
                self.setEnabled(True)
            else:
                self.setVisible(False)
                self.setEnabled(False)
        else:
            self.setVisible(False)
            self.setEnabled(False)



class TileImageItem(ImageItemBase, TileItemMixIn):

    def __init__(self, layer, tileItemGroup, cppLut):
        self.setNewImageLock = threading.Lock()  
        BaseImageItem = ImageItemBase
        BaseImageItem.__init__(self, cppLut=cppLut)   
        TileItemMixIn.__init__(self,layer=layer, tileItemGroup=tileItemGroup)
        self.lastStemp = time.clock()
        self.newImgDict = dict()
        self.onMouseClickCallback = None

    def onUpdateFinished(self, updateData):
        #print "update finished",updateData.pos
        ts = updateData.ts
        #print ts
        #print "own ts",self.lastStemp,"update ts",ts
        if ts >= self.lastStemp:
            #print "FRESH UPDATE"
            self.setNewImageLock.acquire()
            self.setPos(*updateData.tileInfo.roi2d.begin)
            self.lastStemp = ts
            newImg,qimg = self.newImgDict.pop(ts)
            self.setImage(newImg, qimg=qimg)
            #print self.levels
            self.setNewImageLock.release()
        else:
            #print "bad updatre"
            self.setNewImageLock.acquire()
            self.newImgDict.pop(ts)
            self.setNewImageLock.release()

    def setImageToUpdateFrom(self, newImage, ts, qimg=None):
        self.setNewImageLock.acquire()
        self.newImgDict[ts] = ( newImage.copy(), qimg)
        self.setNewImageLock.release()

    def mouseClickEvent(self, ev, double=False):
        print "click in image",ev.pos()

    def mouseClickEvent(self, ev, double=False):
        if self.onMouseClickCallback is not None:
            self.onMouseClickCallback(self,ev)








class TilePaintImage(ImageItemBase, TileItemMixIn):

    def __init__(self, layer, tileItemGroup, cppLut, labelColors):


        self.labelColors = labelColors
        self.setNewImageLock = threading.Lock()  
        BaseImageItem = ImageItemBase
        BaseImageItem.__init__(self, cppLut=cppLut)   
        TileItemMixIn.__init__(self,layer=layer, tileItemGroup=tileItemGroup)
        self.lastStemp = time.clock()
        self.newImgDict = dict()
        self.label = 1 
        self.brushRad = 0
        self.pathX = []
        self.pathY = []
        self.pathItem = pg.PlotCurveItem()
        
        self.viewBox = self.tileItemGroup.viewBox
        self.viewBox.addItem(self.pathItem)



    def onLabelChanged(self, label):
        self.label = label
        c = self.labelColors[self.label,:]


    def onBrushSizeChanged(self, brushRad):
        self.brushRad = brushRad
        c = self.labelColors[self.label,:]
        


    def onUpdateFinished(self, updateData):
        #print "update finished",updateData.pos
        ts = updateData.ts
        if ts >= self.lastStemp:
            self.setNewImageLock.acquire()
            self.setPos(*updateData.tileInfo.roi2d.begin)
            self.lastStemp = ts
            newImg,qimg = self.newImgDict.pop(ts)
            self.setImage(newImg, qimg=qimg)
            self.setNewImageLock.release()
        else:
            self.setNewImageLock.acquire()
            self.newImgDict.pop(ts)
            self.setNewImageLock.release()

    def setImageToUpdateFrom(self, newImage, ts):
        self.setNewImageLock.acquire()
        self.newImgDict[ts] = newImage.copy()
        self.setNewImageLock.release()

    def setImageToUpdateFrom(self, newImage, ts, qimg=None):
        self.setNewImageLock.acquire()
        self.newImgDict[ts] = ( newImage.copy(), qimg)
        self.setNewImageLock.release()

    #def mousePressEvent(self, ev):
    #    print "PRESS PAINT"
    #    ev.accept()

    def mouseClickEvent(self, ev, double=False):
        print "click in paint",ev.pos()
    #    self.image[pos[0],pos[1],0:4] = 255 
    #    self.updateImage(self.image)


    def mouseDragEvent(self, ev, axis=None):
        kmods = ev.modifiers()
        s2d = self.roi2d.shape
        if  ev.button() == QtCore.Qt.LeftButton and (kmods == pg.QtCore.Qt.NoModifier): #and (noShift and noCtrl):
            
            pos = ev.pos()
            begin,end = self.roi2d.begin, self.roi2d.end
            pos = pos.x()+begin[0],pos.y()+begin[1]
            
            print pos
            if True:#pos[0]>=0 and pos[0]<s2d[0] and pos[1]>=0 and pos[1]<s2d[1]:
                ev.accept()

                c = tuple(self.labelColors[self.label,:])#+(75,)
                w = (self.brushRad*2+1)/self.viewBox.viewPixelSize()[0]
                self.pathItem.setPen(pg.mkPen(color=c,width=w))

                if not ev.isFinish():
                    if len(self.pathX)==0:
                        print "first click"
                    print len(self.pathX)

             
                    self.pathX.append(pos[0])
                    self.pathY.append(pos[1])
                    #self.image[pos[0],pos[1],0:4] = 255 
                    #self.updateImage(self.image)
                    
                    
                    self.pathItem.updateData(x=numpy.array(self.pathX), y=numpy.array(self.pathY))

                else:
                    self.makeArrayFromPath()
                    self.pathX = []
                    self.pathY = []
                    self.pathItem.updateData()


    def makeArrayFromPath(self):
        begin,end  = self.roi2d.begin, self.roi2d.end

        npx = numpy.array(self.pathX)
        npy = numpy.array(self.pathY)

        self.pathX = []
        self.pathY = []
        self.pathItem.updateData()



        linSpace = numpy.linspace

        startCoord = numpy.floor(numpy.array([numpy.min(npx),numpy.min(npy)])).astype('int64')
        stopCoord  = numpy.round(numpy.array([numpy.max(npx)+1,numpy.max(npy)+1]),0).astype('int64')

        startCoord -= self.brushRad + 1
        stopCoord  += self.brushRad + 1

        shape = stopCoord - startCoord
        shape = [int(s) for s in shape]
        shape3d = [1,1,1]
        shape3d[self.viewBox.viewAxis[0]] = int(shape[0])
        shape3d[self.viewBox.viewAxis[1]] = int(shape[1])

        start3d = [0,0,0]
        start3d[self.viewBox.viewAxis[0]] = int(startCoord[0])
        start3d[self.viewBox.viewAxis[1]] = int(startCoord[1])
        start3d[self.viewBox.scrollAxis]  = int(self.viewBox.scrollCoordinate)

        labelsBlock = numpy.zeros(shape,'uint8')

        for i in range(len(npx)-1):
            #print i
            x0,y0 = npx[i],npy[i]
            x1,y1 = npx[i+1],npy[i+1]
            dist = numpy.abs(x0-x1) + numpy.abs(y0-y1)
            num = max(int(dist +0.5),10)*5
            #print "NUM:",dist
            

            x, y = linSpace(x0, x1, num), linSpace(y0, y1, num)
            x = numpy.floor(x).astype('uint64')
            y = numpy.floor(y).astype('uint64')
            x -= startCoord[0]
            y -= startCoord[1]
            labelsBlock[x,y] = 1


        # make draw kernel
        drawKernel = numpy.ones((2*self.brushRad+1,)*2,dtype='uint8')
        drawKernel = sector_mask(self.brushRad)
        print drawKernel
        print "DRAW KERNEL SHAPE",drawKernel.shape
        resultLabels = applyDrawKernel(labelsBlock, drawKernel)




        if self.label != 0:
            resultLabels *=self.label
        else:
            resultLabels *=255
        labelsBlock = resultLabels.reshape(shape3d)
        #print "LABELS MAX IN BLOCK",labelsBlock.max()
        
        
        # "clip" the block into the spatial range 
        #  ! TODO re-implement this shit
        startInBlock = [0,0,0]
        startInBlock[0] = max(0,0-start3d[0])
        startInBlock[1] = max(0,0-start3d[1])
        startInBlock[2] = max(0,0-start3d[2])

        start3d[0] = max(0, start3d[0])
        start3d[1] = max(0, start3d[1])
        start3d[2] = max(0, start3d[2])
        labelsBlock = labelsBlock[startInBlock[0]::,startInBlock[1]::,startInBlock[2]::]

        shape3d = self.viewBox.navigator.spatialShape
        labelsBlock = labelsBlock[
            0 : min(labelsBlock.shape[0], shape3d[0]-start3d[0]),
            0 : min(labelsBlock.shape[1], shape3d[1]-start3d[1]),
            0 : min(labelsBlock.shape[2], shape3d[2]-start3d[2]),
        ]


    
        self.layer.writeLabelsToDataSource(labelsBlock, start3d)
    
