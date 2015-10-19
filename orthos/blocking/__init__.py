

# Multi bocking:
#
#  64,128,512,1024, 2048
#
#
#
import numpy

sizes  = numpy.array([64,128,512,1024],dtype='uint32')
coord  = numpy.array([125,2124,20],dtype='uint32')
print  coord/sizes[:,None]
