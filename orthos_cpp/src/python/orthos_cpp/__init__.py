# In theory, the extension already imports vigra for us.
# But for some reason that doesn't seem to work on all systems.
# The quick workaround is to just import it here.
import vigra
import numpy
from _orthos_cpp import *





class injector(object):
    class __metaclass__(TileInfo.__class__):
        def __init__(self, name, bases, dict):
            for b in bases:
                if type(b) not in (self, type):
                    for k,v in dict.items():
                        setattr(b,k,v)
            return type.__init__(self, name, bases, dict)


class MoreTileInfo(injector, TileInfo):


    def slicing3d(self):
        begin = self.roi3d.begin
        end   = self.roi3d.end
        return tuple([slice(b,e) for b,e in zip(begin,end)])
    


    def slicing2d(self):
        begin = self.roi2d.begin
        end   = self.roi2d.end
        return tuple([slice(b,e) for b,e in zip(begin,end)])








class ValToRgba(object):


    dtypeDict = {
        numpy.uint8   : 'uint8',
        numpy.uint16  : 'uint16',
        numpy.uint32  : 'uint32',
    }

    @classmethod
    def normalizeAndColormap(cls, dtype):
        dtypeStr = ValToRgba.dtypeDict[dtype]
        cls = _orthos_cpp.__dict__['NormalizedExplicitLut_%s'%dtypeStr]
        return cls


    def normalize(dtype, channels=None):
        dtypeStr = dtype
        cls = _orthos_cpp.__dict__['NormalizedGray_%s'%dtypeStr]
        return cls

    def unmodified(dtype, channels=None):
        """
            only for values which naturally
            fall into the uint8 range.

            No normalization what so ever is applied,
            values are just casted to a tiny vector
            of uint8 of length 4.
        """
        pass

    def labelToImplicitRandom(dtype):
        pass

    def sparseMappedExplicit(dtype):
        pass





def makeRGBAImage(image, cppLut):
    return applyLut2D(image, cppLut)
    #sshape = image.shape[0:2]
    #imageFlat = image.reshape([sshape[0]*sshape[1],-1])
    #imageFlat = imageFlat.squeeze()
    ##print "FLAT",imageFlat.shape, imageFlat.dtype
    #imageFlatRGBA = applyLut(imageFlat, cppLut)
    #imageRGBA = imageFlatRGBA.reshape([sshape[0],sshape[1],-1])
    #return imageRGBA.squeeze()