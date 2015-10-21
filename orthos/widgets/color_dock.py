import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
from pyqtgraph.dockarea.Dock import DockLabel
import types

def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple
    # that's it! '%02x' means zero-padded, 2-digit hex values
    return hexcolor


class MyDockArea(DockArea):
    def __init__(self,*args,**kwargs):
        super(MyDockArea,self).__init__(*args,**kwargs)

    def clear(self):
        docks = self.findAll()[1]
        for dock in docks.values():
            print "CLOSE DOCK"
            if dock.closable:
                dock.close()
            else:
                self.home.moveDock(dock, "top", None)


class ColorDock(Dock):


    def __init__(self,color,*args,**kwargs):
        super(ColorDock,self).__init__(*args,**kwargs)
        def labelUpdateStyle(self):
            r = '3px'
            if self.dim:
                fg = '#aaa'
                bg = '#44a'
                border = '#339'
            else:
                fg = '#fff'
                bg = RGBToHTMLColor(color)
                border = '#55B'
            
            if self.orientation == 'vertical':
                self.vStyle = """DockLabel { 
                    background-color : %s; 
                    color : %s; 
                    border-top-right-radius: 0px; 
                    border-top-left-radius: %s; 
                    border-bottom-right-radius: 0px; 
                    border-bottom-left-radius: %s; 
                    border-width: 0px; 
                    border-right: 2px solid %s;
                    padding-top: 3px;
                    padding-bottom: 3px;
                }""" % (bg, fg, r, r, border)
                self.setStyleSheet(self.vStyle)
            else:
                self.hStyle = """DockLabel { 
                    background-color : %s; 
                    color : %s; 
                    border-top-right-radius: %s; 
                    border-top-left-radius: %s; 
                    border-bottom-right-radius: 0px; 
                    border-bottom-left-radius: 0px; 
                    border-width: 0px; 
                    border-bottom: 2px solid %s;
                    padding-left: 3px;
                    padding-right: 3px;
                }""" % (bg, fg, r, r, border)
                self.setStyleSheet(self.hStyle)

        method = types.MethodType(labelUpdateStyle, self.label)
        self.label.updateStyle = method
        self.label.updateStyle()




