import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore



class TilingImageItem(pg.ImageItem):
    def __init__(self, *args, **kwargs):
        super(TilingImageItem, self).__init__(*args,**kwargs)
        self.visibleInTiling = True
        self.widgetVisibility = self.isVisible()


    # this is called by callbacks
    #  mainly from the layer ctrl gui
    def setVisible(self, visible): 
        self.widgetVisibility = visible
        if visible == True:
            if self.visibleInTiling :
                super(TilingImageItem, self).setVisible(True)
            else:
                super(TilingImageItem, self).setVisible(False)
        if visible == False:
            super(TilingImageItem, self).setVisible(False)

    def setTilingVisible(self, visible):
        self.visibleInTiling = visible
        if visible == True:
            if self.widgetVisibility == True:
                super(TilingImageItem, self).setVisible(True)
            else:
                super(TilingImageItem, self).setVisible(False)
        else:
            super(TilingImageItem, self).setVisible(False)
