from __future__ import division

import units
import terrain
import random
import operator
from collections import Counter
import math
import numpy as np
from scipy.special import binom

#p = 0.05 * (((A + Ta) - (D + Td))+B) + 0.5
#if p < 0 set p to 0
#if p > 1 set p to 1

#For each sub unit of the attacker six random numbers (r) between 0 and 1 are generated. For each r < p a hit is counted.
#The total number of hits divided by 6 is the number of sub units the opponent loses during the attack.

#Attacker and defender then switch roles and the process starts over. Please note: Losses will only be removed when
#the battle is over. They will not affect the calculations of the current attack.


def get_hit_probability(attacking_power, attacking_terrain_modifier, defending_defense, defending_terrain_modifier, gangup_bonus):
    return np.clip(0.05 * (((attacking_power + attacking_terrain_modifier) - (defending_defense + defending_terrain_modifier)) + gangup_bonus) + 0.49, 0.0, 1.0)


def get_single_result(attacking_health, attacking_power, attacking_terrain_modifier, defending_health, defending_defense, defending_terrain_modifier, gangup_bonus):
    p = get_hit_probability(attacking_power, attacking_terrain_modifier, defending_defense, defending_terrain_modifier, gangup_bonus)
    r = np.random.uniform(0, 1, attacking_health * 6)
    hits = np.sum(r < p)
    return max(0, defending_health - int(hits / 6))


def calc_probabilities(attacking_health, attacking_power, attacking_terrain_modifier, defending_health, defending_defense, defending_terrain_modifier, gangup_bonus):

    p = get_hit_probability(attacking_power, attacking_terrain_modifier, defending_defense, defending_terrain_modifier, gangup_bonus)
    n = attacking_health * 6
    probs = [binom(n, k) * p ** k * (1 - p) ** (n - k) for k in range(60)]
    binned_probs = 100.0 * np.array(probs).reshape(10, -1).sum(axis=1)[::-1]
    z = np.zeros(20)
    z[defending_health:defending_health + 10] = np.array(binned_probs)
    z[9] = sum(z[:10])

    return dict(enumerate(z[9:20]))

#@profile
def simulate_probabilities(attacking_health, attacking_power, attacking_terrain_modifier, defending_health, defending_defense, defending_terrain_modifier, gangup_bonus):

    num_simulations = 1000000

    p = get_hit_probability(attacking_power, attacking_terrain_modifier, defending_defense, defending_terrain_modifier, gangup_bonus)

    #res = []
    #for x in range(num_simulations):
    #    #r = np.random.randint(0, 100, attacking_health * 6) + 1
    #    r = np.random.uniform(0, 1, attacking_health * 6)
    #    hits = np.sum(r < p)
    #    res.append(max(0, defending_health - int(hits / 6)))
    #return dict([(key, 100.0 * value / num_simulations) for key, value in Counter(res).items()])

    r = np.random.uniform(0, 1, (num_simulations, attacking_health * 6))
    hits = np.sum(r < p, axis=1)
    res = np.clip(defending_health - np.floor(hits / 6), 0, 10).astype(np.int64)
    bins = np.bincount(res) * 100.0 / num_simulations
    return dict(enumerate(bins))

def evaluate(attacking_type, attacking_health, attacking_terrain, defending_type, defending_health, defending_terrain):

    attacking_class = units.type[attacking_type].unitclass
    defending_class = units.type[defending_type].unitclass

    attacking_power = units.type[attacking_type].power[defending_class]
    defending_power = units.type[defending_type].power[attacking_class]

    attacking_terrain_modifier = terrain.getTerrainModifier(attacking_class, attacking_terrain)
    defending_terrain_modifier = terrain.getTerrainModifier(defending_class, defending_terrain)

    ## todo: not yet implemented
    gangup_bonus = 0

    attacking_left = get_single_result(defending_health, defending_power, defending_terrain_modifier[0], attacking_health, units.type[attacking_type].defense, attacking_terrain_modifier[1], gangup_bonus)
    defending_left = get_single_result(attacking_health, attacking_power, attacking_terrain_modifier[0], defending_health, units.type[defending_type].defense, defending_terrain_modifier[1], gangup_bonus)

    return attacking_left, defending_left

def debug(attacking_type, attacking_health, attacking_terrain, defending_type, defending_health, defending_terrain):

    attacking_class = units.type[attacking_type].unitclass
    defending_class = units.type[defending_type].unitclass

    attacking_power = units.type[attacking_type].power[defending_class]
    defending_power = units.type[defending_type].power[attacking_class]

    attacking_terrain_modifier = terrain.getTerrainModifier(attacking_class, attacking_terrain)
    defending_terrain_modifier = terrain.getTerrainModifier(defending_class, defending_terrain)

    ## todo: not yet implemented
    gangup_bonus = 0

    for i in range(0, 11):
        print "%10d" % i,
    print
    print "------------------------------------------------"
    r = simulate_probabilities(defending_health, defending_power, defending_terrain_modifier[0], attacking_health, units.type[attacking_type].defense, attacking_terrain_modifier[1], gangup_bonus)
    for i in range(0, 11):
        print "%10.6f" % (r[i] if i in r else 0),
    print
    r = calc_probabilities(defending_health, defending_power, defending_terrain_modifier[0], attacking_health, units.type[attacking_type].defense, attacking_terrain_modifier[1], gangup_bonus)
    for i in range(0, 11):
        print "%10.6f" % (r[i] if i in r else 0),
    print

    r = simulate_probabilities(attacking_health, attacking_power, attacking_terrain_modifier[0], defending_health, units.type[defending_type].defense, defending_terrain_modifier[1], gangup_bonus)
    for i in range(0, 11):
        print "%10.6f" % (r[i] if i in r else 0),
    print
    r = calc_probabilities(attacking_health, attacking_power, attacking_terrain_modifier[0], defending_health, units.type[defending_type].defense, defending_terrain_modifier[1], gangup_bonus)
    for i in range(0, 11):
        print "%10.6f" % (r[i] if i in r else 0),
    print
    print


