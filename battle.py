import units
import terrain

#p = 0.05 * (((A + Ta) - (D + Td))+B) + 0.5
#if p < 0 set p to 0
#if p > 1 set p to 1

#For each sub unit of the attacker six random numbers (r) between 0 and 1 are generated. For each r < p a hit is counted.
#The total number of hits divided by 6 is the number of sub units the opponent loses during the attack.

#Attacker and defender then switch roles and the process starts over. Please note: Losses will only be removed when
#the battle is over. They will not affect the calculations of the current attack.

def evaluate(attacking_type, attacking_health, attacking_terrain, defending_type, defending_health, defending_terrain):

    attacking_class = units[attacking_type].unitclass
    defending_class = units[defending_type].unitclass

    attacking_power = units[attacking_type].power[defending_class]
    defending_power = units[defending_type].power[attacking_class]

    attacking_terrain_modifier = terrain.getTerrainModifier(attacking_class, attacking_terrain)
    defending_terrain_modifier = terrain.getTerrainModifier(defending_class, defending_terrain)

    ## todo: not yet implemented
    gangup_bonus = 0

    for i in range(attacking_health):
        for _ in range(6):
            p = max(0, min(1, 0.05 * (((attacking_power + attacking_terrain_modifier) - (defending_power + defending_terrain_modifier)) + gangup_bonus) + 0.5))
            print p
