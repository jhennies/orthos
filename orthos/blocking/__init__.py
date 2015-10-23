import numpy
import vigra

def yield2d(shape):
    for x in range(shape[0]):
        for y in range(shape[1]):
            yield x,y


class MultiLevelBlocking(object):
    def __init__(self, spatialShape):
        self.spatialShape = spatialShape
        self.computeBlocking()


    def computeBlocking(self):
        self.blockShapes=numpy.array([
            (128,)*3, (256,)*3, (512,)*3,(1024,)*3
        ])
        self.blockPixelSizes=numpy.ones(self.blockShapes.shape)
        self.nBlockings = self.blockShapes.shape[0]
        self.blockings2d = [ [],[],[] ]
        self.blockings3d = []
        self.viewAxisList = [(1,2,0),(0,2,1),(0,1,2)]
        shape3d = self.spatialShape
        for i in range(self.nBlockings):
            
            #blocking 3d
            blockShape3d = self.blockShapes[i,:]
            b3d = vigra.blockwise.Blocking3D(shape3d, blockShape3d )
            self.blockings3d.append(b3d)

            # 3times blocking 2d
            for vi,viewAxis in enumerate(self.viewAxisList):
                shape2d = shape3d[viewAxis[0]],shape3d[viewAxis[1]]
                bs2d = blockShape3d[viewAxis[0]],blockShape3d[viewAxis[1]]
                b2d =vigra.blockwise.Blocking2D(shape2d, self.blockShape2d(i,vi) )
                self.blockings2d[vi].append(b2d)

    def shape2d(self, axis):
        shape3d = self.spatialShape
        viewAxis = self.viewAxisList[axis]
        return shape3d[viewAxis[0]],shape3d[viewAxis[1]]

    def blockShape2d(self,blockingIndex, axis):
        blockShape3d = self.blockShapes[blockingIndex,:]
        viewAxis = self.viewAxisList[axis]
        return blockShape3d[viewAxis[0]],blockShape3d[viewAxis[1]]


if __name__ == "__main__":
    b = MultiLevelBlocking([1000,500,200])


