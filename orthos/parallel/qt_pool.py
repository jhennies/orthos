import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import time

class WorkerSignals(QtCore.QObject):
    result = QtCore.pyqtSignal(object)
    result2 = QtCore.Signal(object)
    def __init__(self):
        super(WorkerSignals,self).__init__()

class QTask(QtCore.QRunnable):

    
    def __init__(self, f, *args, **kwargs):
        super(QTask, self).__init__()
        self.taskSig = WorkerSignals()
        self.f=f
        self.args = args
        self.kwargs = kwargs
    def run(self):
        self.taskSig.result2.emit(0)
        self.f(*self.args,**self.kwargs)
        self.taskSig.result.emit(0)
        
    def autoDelete(self):
        return False
        

class  QTPool(QtCore.QThreadPool):
    def __init__(self, nWorkers):
        super(QTPool, self).__init__()



class Reciver(QtCore.QObject):
    
    def __init__(self, worker):
        super(Reciver, self).__init__()
        worker.taskSig.result.connect(self.taskDone)
    def taskDone(self, anInt):
        print "task done"


if __name__  == "__main__":


    import  sys
    
    app = QtGui.QApplication([])

    pool = QTPool(8)

    def foo(msg):
        print msg
        pass


    task = QTask(f=foo,msg="hello World!")
    r = Reciver(task)
    pool.start(task)
    pool.start(task)

    pool.waitForDone()

    
    sys.exit(app.exec_())
