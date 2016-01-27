import numpy as np
#Effect on attack (Ta) 	Effect on defense (Td) 	Movement cost
#(HARD, SOFT, SUB, BOAT, AMPHIBIC, AIR, SPEEDBOAT)
terraindata =[
    [0,  " ",   "blank",       (  0,  0,  0,  0,  0,  0,  0), (  0,  0,  0,  0,  0,  0,  0), (999,999,999,999,999,999,999,999)],
    [1,  "W",   "water",       (-10,-10,  0,  0,  0,  0,  0), (-10,-10,  0,  0,  0,  0,  0), (999, 99, 99,  3,  3,  3,  3,  3)],
    [2,  "P",   "plain",       (  0,  0,  0,  0,  0,  0,  0), (  0,  0,  0,  0,  0,  0,  0), (999,  3,  3, 99, 99,  3,  3, 99)],
    [3,  "F",   "forest",      (  0,  2,  0,  0,  0,  0,  0), ( -3,  3,  0,  0,  0,  0,  0), (999,  6,  4, 99, 99, 99,  3, 99)],
    [4,  "M",   "mountain",    (-10,  2,  0,  0,  0,  0,  0), (-10,  4,  0,  0,  0,  0,  0), (999, 99,  6, 99, 99, 99,  3, 99)],
    [5,  "D",   "desert",      (  0, -1,  0,  0,  0,  0,  0), (  0, -1,  0,  0,  0,  0,  0), (999,  4,  5, 99, 99,  3,  3, 99)],
    [6,  "S",   "swamp",       ( -1, -1,  0,  0,  0,  0,  0), ( -2, -2,  0,  0,  0,  0,  0), (999,  6,  6, 99, 99,  3,  3, 99)],
    [7,  "C",   "city",        (  0,  2,  0,  0,  0,  0,  0), ( -1,  2,  0,  0,  0,  0,  0), (999,  2,  3, 99, 99,  3,  3, 99)],
    [8,  "A",   "airfield",    (  0,  2, -2,  0,  0,  3,  0), ( -1,  2, -1, -1, -1,  3,  0), (999,  2,  3, 99, 99,  3,  3, 99)],
    [9,  "H",   "harbor",      (  0,  2, -2,  0,  0,  0,  0), ( -1,  2, -1, -1, -1,  0,  0), (999,  2,  3,  3,  3,  3,  3,  3)],
    [10, "R",   "repairshop",  (  0,  0,  0,  0,  0,  0,  0), ( -6, -6,  0,  0,  0,  0,  0), (999,  3,  3, 99, 99,  3,  3, 99)],
    [11, "B",   "bridge",      (  0,  0,  0,  0,  0,  0,  0), ( -2, -2,  0,  0,  0,  0,  0), (999,  3,  3,  3,  3,  3,  3,  3)]
]

#   ID     code   picture
tiledata = [
    [0,     ".",    0, "blank"],
    [1,     "~",    1, "water"],
    [2,     "P",    2, "plain"],
    [3,     "F",    3, "forest"],
    [4,     "M",    4, "mountain"],
    [5,     "D",    5, "desert"],
    [6,     "S",    6, "swamp"],
    [7,     "C",    7, "city"],
    [8,     "Cr",   7, "red_city"],
    [9,     "Cb",   7, "blue_city"],
    [10,    "Cy",   7, "yellow_city"],
    [11,    "A",    8, "airfield"],
    [12,    "Ar",   8, "red_airfield"],
    [13,    "Ab",   8, "blue_airfield"],
    [14,    "Ay",   8, "yellow_airfield"],
    [15,    "1",   11, "bridgeew"],
    [16,    "2",   11, "bridgenwse"],
    [17,    "3",   11, "bridgenesw"],
    [18,    "H",    9, "harbor"],
    [19,    "Hr",   9, "red_harbor"],
    [20,    "Hb",   9, "blue_harbor"],
    [21,    "Hy",   9, "yellow_harbor"],
    [22,    "R",   10, "repairshop"]
]

class Terrain(object):
    def __init__(self, id, code, terrain_id, picture):
        self.id = id
        self.terrain_id = terrain_id
        self.code = code
        self.picture = picture

type = [Terrain(*x) for x in tiledata]

code2terrainid = dict((code, id) for (id, code, terrain_id, picture) in tiledata)
def getTerrainID(tile_code):
    return code2terrainid[tile_code]

code2tileid = dict((code, terrain_id) for (id, code, terrain_id, picture) in tiledata)
def getTileID(tile_code):
    return code2tileid[tile_code]