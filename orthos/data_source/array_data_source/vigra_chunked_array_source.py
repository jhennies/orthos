from array_data_source_base import ArrayDataSourceBase
import vigra


class VigraChunkedArrayHdf5(ArrayDataSourceBase):
    def __init__(self, **kwargs):
        mutable = kwargs.pop('mutable',False)
        self.chunkedArray = vigra.ChunkedArrayHDF5(**kwargs)
        s = self.chunkedArray.shape
        d = self.chunkedArray.dtype
        super(VigraChunkedArrayHdf5, self).__init__(shape=s,dtype=d,
                                                    mutable=mutable)


    def __getitem__(self,key):
        return self.chunkedArray[key]
    def commitSubarray(self,start,val):
        print start
        print val.shape, val.dtype
        self.chunkedArray.commitSubarray(start,val)

    def flushToDisk(self):
        print "CLOSE THAT ARRAY"
        self.chunkedArray.flush()