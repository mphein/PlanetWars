import sys, logging
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def expand_frontier(state):
    # Keep a list of targeted planets to avoid overlapping in the same turn.
    targeted = []

    # Identify owned planets under threat to prevent enemy from taking planet.
    threatened_planets = [f.destination_planet for f in state.enemy_fleets()]

    # Determine number of ships to send from each owned planet towards potential targets.
    ships_to_send = {}
    
    for planet in state.my_planets():
        if planet.ID in threatened_planets: continue

        # Prioritize targets proportionally to their growth rate
        # and inversely to the distance and number of ships required
        # to take over the planet
        targets = sorted(state.not_my_planets(), 
                         key=lambda p: p.growth_rate / ((p.num_ships + 1) * state.distance(planet.ID, p.ID)),
                         reverse=True)

        t = 0
        outbound_ships = 0
        while t < len(targets) and outbound_ships < planet.num_ships / 2:
            target = targets[t]
            t += 1
            
            if target in targeted: continue
            
            fleet_size = target.num_ships + 1
            if target.owner == 2:
                fleet_size += target.growth_rate * state.distance(planet.ID, target.ID)
            
            if fleet_size > planet.num_ships: continue
            
            ships_to_send[(planet.ID, target.ID)] = fleet_size
            outbound_ships += fleet_size
            targeted.append(target)

    # Attempt to send ships
    one_planet_invaded = False
    for p in ships_to_send.keys():
        one_planet_invaded = issue_order(state, p[0], p[1], ships_to_send[p]) or one_planet_invaded
    return one_planet_invaded

def request_reinforcement(state):
    # For each of our planets targeted by an attack, identify
    # the required amount of reinforcement
    defense_needed = {}

    for f in state.enemy_fleets():
        filtered_planets = [p for p in state.my_planets() if p.ID == f.destination_planet]
        if len(filtered_planets) == 0: continue
        defense_target = filtered_planets[0]

        if defense_target.owner == 1:
            fleet_size = f.num_ships
            planet_growth = f.turns_remaining * defense_target.growth_rate
            total_needed = fleet_size - (planet_growth + defense_target.num_ships)

            # Skip if no reinforcement is needed
            if total_needed <= 0:
                continue

            if not (defense_target.ID in defense_needed.keys()):
                defense_needed[defense_target.ID] = total_needed
            else:
                defense_needed[defense_target.ID] += total_needed
    
    # Do nothing if all planets are sufficiently fortified
    if len(defense_needed) == 0: return False

    # For each planet needing defense, try to draw required reinforcements from nearby planets
    one_planet_defended = False
    for t in defense_needed.keys():
        nearest_allies = sorted(state.my_planets(), key=lambda p: state.distance(t, p.ID))

        defense_required = defense_needed[t]
        defense_sent = 0
        p = 0

        while p < len(nearest_allies) and defense_sent < defense_required:
            sendable = min(nearest_allies[p].num_ships / 2, defense_required)
            if sendable > 0 and issue_order(state, nearest_allies[p].ID, t, sendable): defense_sent += sendable
            p += 1
        one_planet_defended = one_planet_defended or defense_sent >= defense_required
    
    return one_planet_defended
