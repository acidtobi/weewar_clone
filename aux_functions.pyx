from __future__ import division
import numpy as np
import math
import hexlib

# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# currently part of the Cython distribution).
cimport numpy as np
cimport cython
@cython.boundscheck(False) # turn of bounds-checking for entire function
@cython.wraparound(False) # turn of bounds-checking for entire function
@cython.nonecheck(False) # turn of bounds-checking for entire function

def find_paths(np.ndarray[long, ndim=2] visited,
               np.ndarray[long, ndim=2]  zoc,
               np.ndarray[long, ndim=2]  movecost,
               int start_row,
               int start_col,
               int points_left):

    cdef long p = 0
    cdef long max_row = 0
    cdef long max_col = 0
    cdef long target_col = 0
    cdef long target_row = 0

    #global total_calls
    #total_calls += 1

    visited[start_row, start_col] = points_left
    if points_left == 0:
        return visited

    max_row = movecost.shape[0]
    max_col = movecost.shape[1]

    for x, y in hexlib.neighbors:
        target_col, target_row = start_col + x, start_row + y
        if 0 <= target_row < max_row and 0 <= target_col < max_col:

            p = points_left - movecost[target_row, target_col]
            if p > 0 and zoc[target_row, target_col] == 1:
                p = 0

            ## been there with more points left using other path
            if visited[target_row, target_col] >= p:
                continue

            if p >= 0:
                find_paths(visited, zoc, movecost, target_row, target_col, p)
    return visited