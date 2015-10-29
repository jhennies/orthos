# In theory, the extension already imports vigra for us.
# But for some reason that doesn't seem to work on all systems.
# The quick workaround is to just import it here.
import vigra
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


