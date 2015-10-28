import numpy
import orthos_cpp



import numpy as np

def sector_mask(radius):
    """
    Return a boolean mask for a circular sector. The start/stop angles in  
    `angle_range` should be given in clockwise order.
    """
    shape = (2*radius+1,)*2
    x,y = np.ogrid[:shape[0],:shape[1]]
    cx,cy = (radius,)*2
    # circular mask
    r2 = (x-cx)*(x-cx) + (y-cy)*(y-cy)
    circmask = r2 <= radius*radius
    return circmask.astype('uint8')



def applyDrawKernel(labels, kernel):
    if kernel.ndim == 2:
        resultLabels = numpy.zeros(labels.shape,dtype='uint8')
        resultLabels = orthos_cpp.applyDrawKernel2d(labels,kernel,resultLabels)
    else:
        raise RuntimeError("NotYetImplemented")
    return resultLabels




