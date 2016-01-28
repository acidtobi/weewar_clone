from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("aux_functions", ["aux_functions.pyx"])]
)

# original python (interpreted) version of "findpaths" function
def find_paths_python(visited, zoc, movecost, start_row, start_col, points_left):

    global total_calls
    total_calls += 1

    visited[start_row, start_col] = points_left
    if points_left == 0:
        return visited

    max_row, max_col = movecost.shape

    for x, y in hexlib.neighbors:
        target_col, target_row = start_col + x, start_row + y
        if 0 <= target_row < max_row and 0 <= target_col < max_col:

            m = movecost[target_row, target_col]

            p = points_left - abs(m)
            if p > 0 and m < 0:
                p = 0

            ## been there with more points left using other path
            if visited[target_row, target_col] >= p:
                continue

            if p >= 0:
                find_paths(visited, zoc, movecost, target_row, target_col, p)
    return visited
