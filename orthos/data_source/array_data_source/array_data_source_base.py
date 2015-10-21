from abc import abstractmethod, ABCMeta
from ..data_source_base import *

class ArrayDataSourceBase(DataSourceBase):
    __metaclass__ = ABCMeta
    def __init__(self, mutable, shape, dtype):
        super(ArrayDataSourceBase, self).__init__(mutable=mutable)
        self.shape = shape
        self.dtype = dtype

    @abstractmethod
    def __getitem__(self,key):
        pass
