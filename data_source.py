from blocking import *



class InputType(object):
    def __init__(self, nSpatialDim =3, hasTime=False):
        self.nSpatialDim = nSpatialDim
        self.hasTime = hasTime

class InputShape(object):
    def __init__(self, spatialShape, nTimePoint=None):
        self.spatialShape = spatialShape
        self.nTimePoint = nTimePoint

    def planeShape(self, blockShape, axis):
        if self.nSpatialDim == 2:
            return tuple(self.spatialShape),tuple(blockShape)
        else :
            shape =[]
            pb=[]
            for a in range(3):
                if a != axis:
                    shape.append(self.spatialShape[a])
                    pb.append(blockShape[a])
            return tuple(shape),tuple(pb)

    def planeBlocking(self,blockShape, axis):
        s,b = self.planeShape(blockShape=blockShape, axis=axis)
        return Blocking2d(shape=s,blockShape=b)


    @property
    def nSpatialDim(self):
        return len(self.spatialShape)



