import numpy as np
import terrain

NONE, HARD, SOFT, SUB, BOAT, AMPHIBIC, AIR, SPEEDBOAT = range(8)
unit_class = ("NONE", "HARD", "SOFT", "SUB", "BOAT", "AMPHIBIC", "AIR", "SPEEDBOAT")

unitdata = [
    [0,     ".",    ""],
    [1,     "TR",   "001",          SOFT,  75, 100,  9, (1, 1), 6, 1, 1,  True, (SOFT, HARD, SPEEDBOAT, AMPHIBIC, BOAT)], # Trooper
    [2,     "TT",   "002"],         # Heavy Trooper
    [3,     "RD",   "003",          HARD, 200, 200, 12, (1, 1), 8, 2, 1, False, (SOFT, HARD, SPEEDBOAT, AMPHIBIC, BOAT)], # Raider
    [4,     "TK",   "005"],        # Tank
    [5,     "LA",   "008"],        # Light Artillery
    [6,     "HT",   "006"],        # Heavy Tank
    [7,     "HA",   "009"],        # Heavy Artillery
    [8,     "AS",   "004"],        # Assault Artillery
    [9,     "DA",   "010"],        # Death From Above
    [10,    "BE",   "007"],        # Berserker
    [11,    "AA",   "antiair"],    # AA-Gun
    [12,    "HC",   "hovercraft"], # Hovercraft
    [13,    "HE",   "heli"],       # Helicopter
    [14,    "JT",   "jet",         AIR,   800, 800, 18, (1, 1), 12, 3, 1, False, (SOFT, HARD, AIR, SPEEDBOAT, AMPHIBIC, BOAT)],        # Jet
    [15,    "BB",   "bomber"],     # Bomber
    [16,    "SB",   "speedboat"],  # Speedboat
    [17,    "DD",   "destroyer"],  # Destroyer
    [18,    "SU",   "sub"],        # Submarine
    [19,    "BS",   "battleship"], # Battleship
    [20,    "C0",   "capturing"],  # Capturing
    [21,    "C1",   "capturing"],  # Capturing
    [22,    "C2",   "capturing"]   # Capturing
]

class Unit(object):

    def __init__(self, id, color, health, row, col):
        self.id =     id
        self.color =  color
        self.health = health
        self.row =    row
        self.col =    col


class UnitBaseData(object):

    def __init__(self, id, code, picture,
                 unitclass=None, cost=0,
                 value=0, movementpoints=0,
                 attackrange=(0, 0), defense=0,
                 repair=0, attacks=0, cancapture=False,
                 has_zoc_on=()):
        self.id =               id
        self.code =             code
        self.picture =          picture
        self.unitclass =        unitclass
        self.cost =             cost
        self.value =            value
        self.movementpoints =   movementpoints
        self.attackrange =      attackrange
        self.defense =          defense
        self.repair =           repair
        self.attacks =          attacks
        self.cancapture =       cancapture
        self.has_zoc_on =       has_zoc_on

type = [UnitBaseData(*x) for x in unitdata]
code2id = dict((x[1], x[0]) for x in unitdata)

unitclass2movementcost = np.array([movement for (id, code, picture, attack, defend, movement) in terrain.terraindata]).T

def id_from_code(unit_code):
    return code2id[unit_code]
