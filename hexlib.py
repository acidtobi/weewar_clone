# coding=utf-8
from __future__ import division
import numpy as np
import math

# oddr layout
#moves = (((-1, -1,), (0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)), ((0, -1,), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)))

# axial layout
#neighbors = np.array(((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)))
neighbors = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))

# fixed to "odd-r" horizontal layout
class HexGrid(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = {}
        self.grid = None

    def __getitem__(self, coords):
        if len(coords) == 2:
            col, row = coords
            return self.data[row, col]

    def __setitem__(self, coords, value):
        if len(coords) == 2:
            self.data[row, col] = value

    def toArray(self):

        needed_columns = self.width + math.ceil(self.height / 2.0) - 1
        needed_rows = self.height

        arr = np.empty((needed_rows, needed_columns), dtype=np.int32) * np.nan
        #arr[:, :] = -1
        x_offset = math.ceil(self.height / 2.0) - 1

        for row in range(self.height):
            for col in range(self.width):
                if (col, row) in self.data:
                    x, y, z = oddr_to_cube(row, col)
                    arr[z, x + x_offset] = self.data[row, col]

        self.grid = arr
        return arr

def rings(shape, row, col, radius):
    a = np.zeros(shape, dtype=np.int64)
    max_row, max_col = shape

    target_row = row + neighbors[4][0] * radius
    target_col = col + neighbors[4][1] * radius
    for row_d, col_d in neighbors:
        for offset in xrange(radius):
            target_row += row_d
            target_col += col_d
            if 0 <= target_row < max_row and 0 <= target_col < max_col:
                a[target_row, target_col] = 1
    return a

# convert cube to odd-r offset
def cube_to_oddr(x, y, z):
    col = x + (z - (z & 1)) / 2
    row = z
    return row, col


# convert odd-r offset to cube
def oddr_to_cube(row, col):
    x = col - (row - (row & 1)) / 2
    z = row
    y = -x - z
    return x, y, z


def oddr_to_axial_array(source_array):

    height, width = source_array.shape

    needed_columns = width + math.ceil(height/2) - 1
    needed_rows = height

    x_offset = math.ceil(height/2) - 1

    arr = np.zeros((needed_rows, needed_columns), dtype=np.int64)
    #arr[:] = -1

    for row in range(height):
        arr[row, x_offset - int(row / 2):x_offset - int(row / 2) + width] = source_array[row, :]

    return arr

def pixel_to_hexcoords(coords, width, height):

    x, y = coords
    row = int(y / 26)
    ymod = y % 26

    ## "between rows"
    if ymod <= 8:
        xmod = (x - (row % 2) * 16) % 32
        if (2 * (8 - ymod)) > (16 - abs(xmod - 16)):
            row -= 1

    col = int((x - (row % 2) * 16) / 32)

    x, y, z = oddr_to_cube(row, col)

    x += math.ceil(height / 2) - 1

    return z, x

def hexcoords_to_pixel(coords, width, height):

    row, col = coords
    row, col = cube_to_oddr(col, 0, row)
    col -= math.ceil(height / 2) - 1

    y = row * 26 + 17
    x = col * 32 + (row & 1) * 16 + 16

    return x, y


#h = HexGrid(6, 6)
#
#for row in range(6):
#    for col in range(6):
#        h[row, col] = row*10+col
#print h.data
#print h.toArray()


