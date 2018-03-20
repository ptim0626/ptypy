'''
useful utilities from ptypy that should be ported to gpu. These don't ahve external dependencies
'''
import numpy as np
from scipy import ndimage as ndi


def abs2(input):
    '''
    
    :param input. An array that we want to take the absolute value of and square. Can be inplace. Can be complex or real. 
    :return: The real valued abs**2 array
    '''
    return np.multiply(input, input.conj()).real

def sum_to_buffer(in1, outshape, in1_addr, out1_addr, dtype):
    '''
    :param in1. An array . Can be inplace. Can be complex or real.
    :param outshape. An array.
    :param in1_addr. An array . Can be inplace. Can be complex or real.
    :param out1_addr. An array . Can be inplace. Can be complex or real.
    :return: The real valued abs**2 array
    '''
    out1 = np.zeros(outshape, dtype=dtype)
    inshape = in1.shape
    for i1, o1 in zip(in1_addr, out1_addr):
        out1[o1[0], o1[1]:(o1[1] + inshape[1]), o1[2]:(o1[2] + inshape[2])] += in1[i1[0]]
    return out1

def norm2(input):
    '''
    Input here could be a variety of 1D, 2D, 3D complex or real. all will be single precision at least.
    return should be real
    '''
    return np.sum(abs2(input))

def complex_gaussian_filter(input, mfs):
    '''
    takes 2D and 3D arrays. Complex input, complex output. mfs has len==input.ndim
    '''
    return (ndi.gaussian_filter(np.real(input), mfs) +1j *ndi.gaussian_filter(np.imag(input), mfs)).astype(input.dtype)

def mass_center(A):
    '''
    Input will always be real, and 2d or 3d, single precision here
    '''
    return np.array(ndi.measurements.center_of_mass(A))

def interpolated_shift(c, shift):
    '''
    complex bicubic interpolated shift.
    complex output. This shift should be applied to 2D arrays. shift should have len=c.ndims 
    
    '''
    return ndi.interpolation.shift(np.real(c), shift, order=5) + 1j*ndi.interpolation.shift(np.imag(c), shift, order=5)


def clip_complex_magnitudes_to_range(complex_input, clip_min, clip_max):
    '''
    This takes a single precision 2D complex input, clips the absolute magnitudes to be within a range, but leaves the phase untouched.
    '''
    ampl = np.abs(complex_input)
    phase = np.exp(1j * np.angle(complex_input))
    ampl = np.clip(ampl, clip_min, clip_max)
    complex_input[:] = ampl * phase