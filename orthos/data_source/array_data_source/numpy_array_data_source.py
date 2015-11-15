from array_data_source_base import ArrayDataSourceBase
import numpy


class NumpyArrayDataSource(ArrayDataSourceBase):
    def __init__(self, array, mutable=False):
        self.array = array
        s = self.array.shape
        d = self.array.dtype
        self.dimension = len(s)
        super(NumpyArrayDataSource, self).__init__(shape=s,dtype=d,
                                                    mutable=mutable)


    def getData(self, spatialSlicing, t=None):
        if self.dimension == 3:
            return  self.array[spatialSlicing]
        else:
            tslice = (slice(t,t+1),)
            slicing  = spatialSlicing + tslice
            return  self.array[slicing]

