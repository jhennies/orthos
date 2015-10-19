import numpy
import vigra


class Blocking2d(object):
    def __init__(self, shape, blockShape):
        self.blocking = vigra.blockwise.Blocking2D(shape, blockShape)
        self.shape = shape
    def iBlocks(self, rect):
        tl = rect.topLeft()
        br = rect.bottomRight()

        begin = (  int(tl.x()-0.5), int(tl.y()-0.5))
        end = (  int(br.x()+0.5), int(br.y()+0.5))
        return self.blocking.intersectingBlocks(begin,end)
    def __getitem__(self, key):
        return self.blocking[key]
    def __len__(self):
        return len(self.blocking)



class Blocking3d(object):
    def __init__(self,shape, blockShape):
        s = shape
        b = blockShape
        self.blocking = vigra.blockwise.Blocking3D(shape, blockShape)
        self.blockingXY = Blocking2d((s[0],s[1]),(b[0],b[1]))
        self.blockingXZ = Blocking2d((s[0],s[2]),(b[0],b[2]))
        self.blockingYZ = Blocking2d((s[1],s[2]),(b[1],b[2]))
        self.shape = shape
        self.blockShape = blockShape

    def __getitem__(self, key):
        return self.blocking[key]

    def __len__(self):
        return len(self.blocking)
