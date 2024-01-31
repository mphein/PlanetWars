

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def not_totally_dominating(state):
  return if_neutral_planet_available(state) or any(state.enemy_planets())

def fleet_planet_balance(state):
  return len(state.my_planets()) > len(state.my_fleets())

def enemy_fleet_present(state):
  return any(state.enemy_fleets())

def true_default(state):
   return True
  