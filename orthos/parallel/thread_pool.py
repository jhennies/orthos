import concurrent.futures
import sys
import time
from functools import partial
import threading
from kivy.clock import Clock, mainthread
class Task(object):
    def __init__(self,f, *args,**kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs

class ThreadPool(object):
    def __init__(self, maxWorkers):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers)

    def submit(self, task, onTaskFinished=None):
        futureRes =  self.executor.submit(task.f, *task.args, **task.kwargs)
        if onTaskFinished is not None:
            futureRes.add_done_callback(onTaskFinished)
        return futureRes
    def join(self):
        self.executor.join()




if __name__ == "__main__":

    printLock = threading.Lock()

    def waitForIt(t, m):
        time.sleep(1)
        printLock.acquire()
        #print threading.currentThread(),"prints",m
        printLock.release()
    
    def finished(future,m):
        def realFinished():
            #printLock.acquire()
            print threading.currentThread(),"realFinished",m
            #printLock.release()
        t = Clock.schedule_once(realFinished)

        #printLock.acquire()
        #print threading.currentThread(),"finished",m
        #printLock.release()
    finished(None,1)
    def lala():
        print "lalala"
    t = Clock.schedule_once(lala)


    p = ThreadPool(8)
    futures = []
    print "start submit"
    for x in range(20):
        t = Task(waitForIt,10,x)
        futures.append( p.submit(t,partial(finished,m=x)))
    print "end submit"
    for f in futures:
        f.result()


