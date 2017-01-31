import re
import numpy as np
from pprint import pprint
import terrain
import units
from colors import Color as Color
import hexlib
import string
from itertools import groupby
from operator import attrgetter
import sys


class Map(object):

    def __init__(self, name, start_credits, credits_per_base, terrain_string, units_string):

        """
        Generate Map object from data in config file

        :param name:
        :param start_credits:
        :param credits_per_base:
        :param terrain_string:
        :param units_string:
        :return:
        """

        self.name = name
        self.credits_per_base = credits_per_base
        self.start_credits = start_credits

        ## numpy array
        self.board = None

        ## numpy array
        self.terrain = None

        ## size: (rows, columns)
        self.size = (0, 0)

        ## number of columns
        self.width = 0

        ## number of rows
        self.height = 0

        ## dict containing unit.Unit objects
        self.units = {}

        ## convert terrain string to python list
        terrain_list = [re.split("([A-Z\.~][a-z]?)", line)[1::2] for line in string.split(terrain_string, "\n") if line != ""]

        ## convert terrain string to python list
        units_list = [re.split("([^\s]+)", line)[1::2] for line in string.split(units_string, "\n") if line != ""]

        ## check if all rows have the same number of columns
        terrain_row_lenghts = set(len(x) for x in terrain_list)
        if len(terrain_row_lenghts) != 1:
            raise ValueError('error in terrain data: all rows need to be of equal length')

        ## set width and height
        self.width = terrain_row_lenghts.pop()
        self.height = len(terrain_list)
        self.size = (self.height, self.width)

        # create numpy array for terrain
        self.terrain = self.map_list_to_numpy_array(terrain_list, terrain.getTerrainID)

        # create numpy array for terrain groups (formerly named "tiles")
        self.terrain_group = self.map_list_to_numpy_array(terrain_list, terrain.getTerrainGroupID)

        ## create numpy array for board (unit id, color and health)
        self.board = self. generate_board(units_list)

        ## generate units dict from board
        self.units = self.generate_units_dict_from_board(self.board)

    @staticmethod
    def map_list_to_numpy_array(map_list, id_converter):
        id_converter_function = np.vectorize(lambda x: id_converter(x))
        map_array = id_converter_function(np.array(map_list)).astype(np.int32)
        map_array = hexlib.oddr_to_axial_array(map_array)
        return map_array

    @staticmethod
    def generate_board(units_list):
        """
         create numpy array for units

        :param units_list:
        :return:
        """

        def unit_code_to_list(unit_code):

            if unit_code == ".":
                return 0, 0, 0

            unit_id = units.id_from_code(unit_code[0:2])
            unit_color = unit_code[2]
            unit_health = int(unit_code[3]) if len(unit_code) > 3 else 10

            return unit_id, Color.id(unit_color), unit_health

        board = np.transpose(np.array([map(unit_code_to_list, row) for row in units_list]), (2, 0, 1))
        board = np.array([hexlib.oddr_to_axial_array(board[x]) for x in range(3)])

        return board

    @staticmethod
    def generate_units_dict_from_board(board):

        """
        generates units dict from 3d board numpy array

        :param board:
        :return:
        """

        ## get indices of nonempty board positions
        idx = np.transpose(np.nonzero(board[0] > 0))

        ## merge indices with board data
        ## (there *must* be a simpler way to do this...!)
        units_list = np.concatenate((np.transpose(board[:, idx[:, 0], idx[:, 1]]), idx), axis=1)

        ## convert lists to Unit objects
        units_objs = [units.Unit(*x) for x in units_list]

        ## group by color
        g = groupby(sorted(units_objs, key=attrgetter('color')), attrgetter('color'))

        ## convert to dict
        units_by_color = dict([(color, list(items)) for color, items in g])

        return units_by_color


    def zoc(self, unit_class, neutral_color):
        """
        Returns numpy array with 1's where a given unit has ZoC

        :param unit_class:
        :param neutral_color:
        :return:
        """

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


def load(mapname):

    with open("maps.cfg") as f:
        content = f.read()

    ## remove comments
    content = re.sub("#[^\n]*", "", content)

    ## remove blank lines
    content = re.sub("[\n]+", "\n", content)

    ## split at [MapName] tags
    maps = re.split("\[([^\[\]]+)\]", content)

    ## remove empty lines
    maps = [x for x in maps if x != ""]

    ## join with name tags
    maps = [maps[x:x + 2] for x in xrange(0, len(maps), 2)]

    for this_map_name, map_data_blob in maps:

        ## ignore all other maps
        if this_map_name != mapname:
            continue

        ## split at "attribute:" tags
        map_data = re.split("\n([a-z0-9_]+):", map_data_blob)

        ## remove empty lines
        map_data = [x for x in map_data if x != ""]

        ## join with tags
        map_data = [tuple(map_data[x:x + 2]) for x in xrange(0, len(map_data), 2)]

        ## convert to dict
        map_data = dict(map_data)

        return Map(name=this_map_name,
                   start_credits=map_data['start_credits'],
                   credits_per_base=map_data['credits_per_base'],
                   terrain_string=map_data['terrain'],
                   units_string=map_data['units'])

    ## if no map with given name was found, return None
    return None


#================================================================
# Tests
#============================================================

this_map = load("Stirling's Aruba")

for color in this_map.units:
    for u in this_map.units[color]:
        pprint(vars(u))
