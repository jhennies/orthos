from array_data_source_base import ArrayDataSourceBase
import vigra


class VigraChunkedArrayHdf5(ArrayDataSourceBase):
    def __init__(self, filepath, dset, mutable=False):
        self.chunkedArray = vigra.ChunkedArrayHDF5(filepath,dset)
        s = self.chunkedArray.shape
        d = self.chunkedArray.dtype
        super(VigraChunkedArrayHdf5, self).__init__(shape=s,dtype=d,
                                                    mutable=mutable)


    def __getitem__(self,key):
        return self.chunkedArray[key]
