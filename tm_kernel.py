#!/usr/bin/env python
## to plot binary kernel or model file 
## usage: python $seisDD/auxiliaries/visualize/plot_bin /path/to/files parameters nproc
## python version: Python 2.7.11

import os
import sys
import math
import numpy as np

def isnonzero(a):
    zmin = np.min(a, axis=0)
    zmax = np.max(a, axis=0)
    return np.flatnonzero(zmax-zmin)


def stack(v):
    s = np.hstack(v)
    return s
   
def read_fortran(filename):
    """ Reads Fortran style binary data and returns a numpy array.
    """
    with open(filename, 'rb') as file:
        # read size of record
        file.seek(0)
        n = np.fromfile(file, dtype='int32', count=1)[0]

        # read contents of record
        file.seek(4)
        v = np.fromfile(file, dtype='float32')

    return v[:-1]

def uniquerows(a, sort_array=False, return_index=False):
    """ Finds unique rows of numpy array
    """
    if sort_array:
        if return_index:
            sa, si = sortrows(a, return_index=True)
        else:
            sa = sortrows(a)
    else:
        sa, sj = sortrows(a, return_inverse=True)
    ui = np.ones(len(sa), 'bool')
    ui[1:] = (np.diff(sa, axis=0) != 0).any(axis=1)

    if sort_array:
        ua = sa[ui]
        if return_index:
            ui = si[ui]
    else:
        ua = a[ui[sj]]
        if return_index:
            ui = np.array(range(len(ui)))[ui[sj]]

    if return_index:
        return ua, ui
    else:
        return ua

if __name__ == '__main__':
    """ Plots data on 2-D unstructured mesh
    Reads mesh coordinates from first two columns of text file and data from
    subsequent columns, computes Delaunay triangulation, and plots data
    using matplotlib.
    In particular, can be used to plot kernels and models output from SPECFEM2D
    on unstructured GLL bases.
    """
    dirname = sys.argv[1]
    parameters = sys.argv[2]
    nproc=int(sys.argv[3])
    print (dirname,parameters, nproc)

    x = []
    z = []
    for par in parameters.split(','):
        v = []
        temp = []
        min = 1000000
        max = -1000000
        for iproc in range(0,nproc):
            
            filename = os.path.join(dirname, 'proc%06d_x.bin' % iproc)
            x += [read_fortran(filename)]
            filename = os.path.join(dirname, 'proc%06d_z.bin' % iproc)
            z += [read_fortran(filename)]
  
            filename = os.path.join(dirname, 'proc%06d_%s.bin' % (iproc, par))
            temp = [read_fortran(filename)]
            v+= temp

        if ('kernel' in par):
            levels=np.linspace(-np.max(abs(stack(v)))*1.001,np.max(abs(stack(v)))*1.001,101)
        else:
            levels=np.linspace(np.min((stack(v)))*0.999,np.max((stack(v)))*1.001,101)
        sx=stack(x)
        sz=stack(z)
        sv=stack(v)
        fout=open(parameters+'.txt','w')
        for i in range(0,120000):
            """
            if (x[i]>600000 and x[i]<1000000 and y[i]>140000):
            """
            fout.write(str(sx[i]/1000)+' '+str((150000-sz[i])/1000)+' '+str(sv[i]*100000000)+'\n')
        fout.close()
