import re
import numpy as np
from pprint import pprint
import terrain
import units
import colors
import hexlib

NONE = 0
TERRAIN = 1
UNITS = 2

mode = NONE
maps = []

def split_map(map_list, dimensions):
    return [map_list[i:i + dimensions[1]] for i in xrange(0, dimensions[0] * dimensions[1], dimensions[1])]

class Map(object):
    def __init__(self):
        self.name = ""
        self.credits_per_base = 0
        self.start_credits = 0
        self.board = None
        self.units_string = ""
        self.terrain = None
        self.terrain_string = ""
        self.num_columns = []
        self.num_rows = 0
        self.units = {}

    def zoc(self, unit_class, neutral_color):

        max_row, max_col = self.terrain.shape

        zoc = np.zeros_like(self.terrain)
        for color in self.units:
            if color == neutral_color:
                continue

            for unit in self.units[color]:

                if unit_class not in units.type[unit.id].has_zoc_on:
                    continue

                for x, y in hexlib.neighbors:
                    target_col, target_row = unit.col + x, unit.row + y
                    if target_row < max_row and target_col < max_col:
                        zoc[target_row, target_col] = 1

        return zoc

current_map = None

terrain_string = ""
units_string = ""
with open("maps.cfg") as f:
    content = f.readlines()

    for line in content:

        m = re.match("^\[([^\[\]]+)\]$", line)
        if m:
            if current_map:
                maps.append(current_map)

            current_map = Map()
            current_map.name = m.groups()[0]
            continue

        m = re.match("terrain:", line)
        if m:
            mode = TERRAIN
            continue

        m = re.match("units:", line)
        if m:
            mode = UNITS
            continue

        m = re.match("credits_per_base:[^0-9]*([0-9]+)", line)
        if m:
            current_map.credits_per_base = int(m.groups()[0])
            continue

        m = re.match("start_credits:[^0-9]*([0-9]+)", line)
        if m:
            current_map.start_credits = int(m.groups()[0])
            continue

        if line.strip() == "" or line[0] == "#":
            continue

        if mode == TERRAIN:
            current_map.terrain_string += line[:-1]
            current_map.num_columns.append(len(re.split("([A-Z\.\~][a-z]?)", line)[1::2]))
            current_map.num_rows += 1

        if mode == UNITS:
            current_map.units_string += line[:-1]

    maps.append(current_map)


for m in maps:
    rowlength = set(m.num_columns)
    if len(rowlength) != 1:
        raise ValueError('all rows need to be of equal length')
    rowlength = rowlength.pop()

    ## convert map string to python list
    map_list = re.split("([A-Z\.\~][a-z]?)", m.terrain_string)[1::2]

    m.width = rowlength
    m.height = len(map_list) / m.width

    splitted_map = split_map(map_list, (m.height, m.width))

    # convert units string to python list
    splitted_units = split_map(re.split("([A-Za-z0-9]+|\.)", m.units_string)[1::2], (m.height, m.width))

    # create numpy array for tiles
    g = np.vectorize(lambda x: terrain.getTileID(x))
    m.tiles = g(np.array(splitted_map)).astype(np.int32)
    m.tiles = hexlib.oddr_to_axial_array(m.tiles)

    # create numpy array for terrain
    g = np.vectorize(lambda x: terrain.getTerrainID(x))
    m.terrain = g(np.array(splitted_map)).astype(np.int32)
    m.terrain = hexlib.oddr_to_axial_array(m.terrain)

    # create numpy array for units
    m.board = np.zeros((3, m.height, m.width), dtype=np.int32)
    for (row, col), unit_code in np.ndenumerate(np.array(splitted_units)):
        if unit_code != ".":
            unit_id = units.id_from_code(unit_code[0:2])
            unit_color = unit_code[2]
            unit_health = int(unit_code[3]) if len(unit_code)>3 else 10

            color_id = colors.id_from_code(unit_color)

            m.board[0, row, col] = unit_id
            m.board[1, row, col] = color_id
            m.board[2, row, col] = unit_health

    m.board = np.array([hexlib.oddr_to_axial_array(m.board[x]) for x in range(3)])

    ## create units dict from numpy array
    for row, col in np.transpose(np.nonzero(m.board[0] > 0)):
        unit_id, unit_color, unit_health = m.board[:, row, col]
        if unit_color not in m.units:
            m.units[unit_color] = []
        u = units.Unit(unit_id, unit_color, unit_health, row, col)
        m.units[unit_color].append(u)

for m in maps:
    pprint(vars(m))

#print hexlib.rings(maps[0].terrain.shape, 5, 5, 2)
