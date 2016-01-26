# coding=utf-8
import numpy as np
import math
# fixed to "odd-r" horizontal layout
class HexGrid(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = {}

    def __getitem__(self, coords):
        if len(coords) == 2:
            col, row = coords
            return self.data[row, col]

    def __setitem__(self, coords, value):
        if len(coords) == 2:
            self.data[row, col] = value

    def __getitem__(self, item):
        print item

    def toArray(self):

        needed_columns = self.width + math.ceil(self.height / 2.0) - 1
        needed_rows = self.height

        arr = np.empty((needed_rows, needed_columns), dtype=np.int32)
        arr[:, :] = -1
        x_offset = math.ceil(self.height / 2.0) - 1

        for row in range(self.height):
            for col in range(self.width):
                if (col, row) in self.data:
                    x, y, z = oddr_to_cube(row, col)
                    arr[z, x + x_offset] = self.data[row, col]
        return arr


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

h = HexGrid(6, 6)

for row in range(6):
    for col in range(6):
        h[row, col] = row*10+col
print h.data
print h.toArray()


