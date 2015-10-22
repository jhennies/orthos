from array_data_source_base import ArrayDataSourceBase
import numpy


class NumpyArrayDataSource(ArrayDataSourceBase):
    def __init__(self, array, mutable=False):
        self.array = array
        s = self.array.shape
        d = self.array.dtype
        super(NumpyArrayDataSource, self).__init__(shape=s,dtype=d,
                                                    mutable=mutable)


    def __getitem__(self,key):
        return self.array[key]
