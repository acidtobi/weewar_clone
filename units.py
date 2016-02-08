import numpy as np
import terrain
from operator import itemgetter

NONE, HARD, SOFT, SUB, BOAT, AMPHIBIC, AIR, SPEEDBOAT = range(8)
NN, HA, SO, SU, BO, AM, AI, SP = range(8)
unit_class = ("NONE", "HARD", "SOFT", "SUB", "BOAT", "AMPHIBIC", "AIR", "SPEEDBOAT")

unitdata = [
    [0,     ".",    ""],
    [1,     "TR",   "001",         SOFT,      75,  100, ( 9,  ), (1, 1), (  6,  3,  0,  3,  3,  0,  3),  6, 1, 1, True,  (SO, HA,     SP, AM,     BO)], # Trooper
    [2,     "TT",   "002",         SOFT,     150,  150, ( 6,  ), (1, 1), (  6,  8,  6,  8,  8,  0,  8),  6, 1, 1, True,  (SO, HA, AI, SP, AM,     BO)], # Heavy Trooper
    [3,     "RD",   "003",         HARD,     200,  200, (12,  ), (1, 1), ( 10,  4,  4,  4,  8,  0,  4),  8, 2, 1, False, (SO, HA,     SP, AM,     BO)], # Raider
    [4,     "TK",   "005",         HARD,     300,  300, ( 9,  ), (1, 1), ( 10,  7,  0,  7,  7,  0,  7), 10, 2, 1, False, (SO, HA,     SP, AM,     BO)], # Tank
    [5,     "LA",   "008",         HARD,     200,  200, ( 9,  ), (2, 3), ( 10,  4,  0,  4,  4,  0,  4),  3, 1, 1, False, (                          )], # Light Artillery
    [6,     "HT",   "006",         HARD,     600,  600, ( 7,  ), (1, 1), ( 10, 12,  0, 10, 10,  0, 10), 14, 2, 1, False, (SO, HA,     SP, AM,     BO)], # Heavy Tank
    [7,     "HA",   "009",         HARD,     600,  600, ( 6,  ), (3, 4), ( 12, 10,  0, 10, 10,  0, 10),  4, 1, 1, False, (                          )], # Heavy Artillery
    [8,     "AS",   "004",         HARD,     450,  450, (12,  ), (1, 2), (  8,  6,  6,  6,  6,  0,  6),  6, 2, 1, False, (SO, HA, AI, SP, AM,     BO)], # Assault Artillery
    [9,     "DA",   "010",         HARD,    1200, 1200, ( 6,  ), (2, 5), ( 16, 14,  0, 14, 14,  0, 14),  4, 1, 1, False, (                          )], # Death From Above
    [10,    "BE",   "007",         HARD,     900,  900, ( 6,  ), (1, 1), ( 14, 16,  0, 14, 14,  0, 14), 14, 2, 1, False, (SO, HA,     SP, AM,     BO)], # Berserker
    [11,    "AA",   "antiair",     HARD,     300,  300, ( 9,  ), (1, 3), (  8,  3,  9,  3,  3,  0,  3),  9, 2, 1, False, (SO, HA, AI, SP, AM,     BO)], # AA-Gun
    [12,    "HC",   "hovercraft",  AMPHIBIC, 300,  300, (12,  ), (1, 1), ( 10,  6,  0,  8, 10,  0,  6),  8, 2, 1, True,  (SO, HA,     SP, AM,     BO)], # Hovercraft
    [13,    "HE",   "heli",        AIR,      600,  600, (15, 3), (1, 1), ( 16, 10,  6, 12, 12,  0,  8), 10, 3, 1, False, (SO, HA, AI, SP, AM,     BO)], # Helicopter
    [14,    "JT",   "jet",         AIR,      800,  800, (18, 6), (1, 1), (  6,  8, 16,  6,  6,  0,  6), 12, 3, 1, False, (SO, HA, AI, SP, AM,     BO)], # Jet
    [15,    "BB",   "bomber",      AIR,      900,  900, (18, 6), (1, 1), ( 14, 14,  0, 14, 14,  0, 14), 10, 3, 1, False, (SO, HA,     SP, AM,     BO)], # Bomber
    [16,    "SB",   "speedboat",   BOAT,     200,  200, (12,  ), (1, 1), (  8,  6,  6, 10, 16,  0,  6),  6, 2, 1, False, (SO, HA, AI, SP, AM,     BO)], # Speedboat
    [17,    "DD",   "destroyer",   BOAT,     900,  900, (12,  ), (1, 3), ( 10, 10, 12, 12, 12, 16, 10), 12, 2, 1, False, (SO, HA, AI, SP, AM, SU, BO)], # Destroyer
    [18,    "SU",   "sub",         SUB,     1000, 1000, ( 9,  ), (1, 2), (  0,  0,  0,  0,  0, 10, 16), 10, 2, 1, False, (                    SU, BO)], # Submarine
    [19,    "BS",   "battleship",  BOAT,    2000, 2000, ( 6,  ), (1, 4), ( 10, 14,  6, 14, 14,  4, 14), 14, 2, 2, False, (SO, HA, AI, SP, AM, SU, BO)], # Battleship
    [20,    "C0",   "capturing",   SOFT,  999999, 1000, ( 0,  ), (1, 1), (  0,  0,  0,  0,  0,  0,  0),  2, 0, 0, True,  (                          )], # Capturing
    [21,    "C1",   "capturing",   SOFT,  999999, 1000, ( 0,  ), (1, 1), (  0,  0,  0,  0,  0,  0,  0),  2, 0, 0, True,  (                          )], # Capturing
    [22,    "C2",   "capturing",   SOFT,  999999, 1000, ( 0,  ), (1, 1), (  0,  0,  0,  0,  0,  0,  0),  2, 0, 0, True,  (                          )]  # Capturing
]

## exceptions:
## BS has range 1 against subs
## AA has range 1 again non-air
## air can only repair on friendly/neutral airfields
## LA, HA, DF cannot attack after moving
## DD has range 1-2 against subs
## DD, BS, SU: movement cost 99 for enemy harbors

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
                 attackrange=(0, 0),
                 power=(  0,  0,  0,  0,  0,  0,  0),
                 defense=0, repair=0,
                 attacks=0, cancapture=False,
                 has_zoc_on=()):
        self.id =               id
        self.code =             code
        self.picture =          picture
        self.unitclass =        unitclass
        self.cost =             cost
        self.value =            value
        self.movementpoints =   movementpoints
        self.attackrange =      attackrange
        self.power =            power
        self.defense =          defense
        self.repair =           repair
        self.attacks =          attacks
        self.cancapture =       cancapture
        self.has_zoc_on =       has_zoc_on

type = [UnitBaseData(*x) for x in unitdata]

## shift attacking power to match index
for t in type:
    t.power = itemgetter(NONE, SOFT, HARD, AIR, SPEEDBOAT, AMPHIBIC, SUB, BOAT)((0,) + t.power)

code2id = dict((x[1], x[0]) for x in unitdata)

unitclass2movementcost = np.array([movement for (id, code, picture, attack, defend, movement) in terrain.terraindata]).T

def id_from_code(unit_code):
    return code2id[unit_code]
