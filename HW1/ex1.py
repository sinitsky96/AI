import search
import random
import math
from itertools import product

ids = ["111111111", "111111111"]


class OnePieceProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        treasure_lookup = self.create_treasure_lookup(initial)
        pirate_ships = self.create_pirate_ships(initial["pirate_ships"]["pirate_ship_1"], len(initial["pirate_ships"]))
        marine_ships = self.create_marine_ships(initial)
        distance_map = self.mapout(initial, treasure_lookup)
        original_map = tuple(tuple(inner_list) for inner_list in initial["map"])
        initial = (pirate_ships, marine_ships, treasure_lookup, distance_map, original_map)
        search.Problem.__init__(self, initial)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        pirates = state[0]
        actions = []
        for p in range(len(pirates)):
            movements_out = self.pirate_sailing_options(state, p)
            loadings_out = self.pirate_loading_options(state, p)
            waitings_out = self.pirate_waiting_options(state, p)
            unloadings_out = self.pirate_unloading_options(state, p)
            actions.append(unloadings_out+loadings_out+movements_out + waitings_out)
        if len(pirates) > 1:
            output_actions = tuple(product(*actions))
        else:
            output_actions = actions[0]

        return output_actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        pirate_ships, marine_ships, treasure_lookup, current_map, original_map = state
        new_marine = self.move_marine_ship(state)

        # if action is a tuple of tuples
        if isinstance(action[0], tuple):
            for act in action:
                if act[0] == "sail":
                    pirate_ships = self.move_pirate_ship(act, pirate_ships)
                    x=1
                elif act[0] == "collect_treasure":
                    pirate_ships, treasure_lookup = self.collect_treasure(act, pirate_ships, treasure_lookup)
                elif act[0] == "wait":
                    pass
                elif act[0] == "deposit_treasure":
                    pirate_ships, treasure_lookup = self.deposit_treasure(act, pirate_ships, treasure_lookup)

            pirate_ships, treasure_lookup = self.check_colli_with_marine(new_marine, pirate_ships,
                                                                         treasure_lookup)
        else:
            if action[0] == "sail":
                pirate_ships = self.move_pirate_ship(action, pirate_ships)
            elif action[0] == "collect_treasure":
                pirate_ships, treasure_lookup = self.collect_treasure(action, pirate_ships, treasure_lookup)
            elif action[0] == "wait":
                pass
            elif action[0] == "deposit_treasure":
                pirate_ships, treasure_lookup = self.deposit_treasure(action, pirate_ships, treasure_lookup)
            pirate_ships, treasure_lookup = self.check_colli_with_marine(new_marine, pirate_ships, treasure_lookup)
        state = (pirate_ships, new_marine, treasure_lookup, current_map, original_map)
        return state


    def move_pirate_ship(self, action, pirate_ships):
        ship = pirate_ships[int(action[1].split("_")[1]) - 1]
        location = action[2]
        pirate_ships = tuple(
                (ship[0], location, ship[2], ship[3], ship[4]) if i + 1 == ship[0] else pirate_ships[i] for i in
                range(len(pirate_ships)))
        return pirate_ships

    def deposit_treasure(self, action, pirate_ships, treasure_lookup):
        ship = pirate_ships[int(action[1].split("_")[1]) - 1]
        for t in range(len(ship[3])):
            treasure_index = int(ship[3][t].split("_")[1]) - 1
            treasure_lookup = tuple(
                (treasure_lookup[i][0], treasure_lookup[i][1], 1) if i == treasure_index else treasure_lookup[i]
                for i in range(len(treasure_lookup)))
        pirate_ships = tuple(
            (ship[0], ship[1], 0, (), ship[4]) if i + 1 == ship[0] else pirate_ships[i]
            for i in range(len(pirate_ships)))
        return pirate_ships, treasure_lookup

    def collect_treasure(self, action, pirate_ships, treasure_lookup):
        ship = pirate_ships[int(action[1].split("_")[1]) - 1]
        treasure = treasure_lookup[int(action[2].split("_")[1]) - 1]
        if ship[2] >= 2:
            pass
        treasure_lookup = tuple((treasure[0], treasure[1], 2) if i + 1 == treasure[0] else treasure_lookup[i] for i in
                                range(len(treasure_lookup)))
        pirate_ships = tuple(
            (ship[0], ship[1], ship[2] + 1, ship[3] + (action[2],), ship[4]) if i + 1 == ship[0] else pirate_ships[i]
            for i
            in range(len(pirate_ships)))
        return pirate_ships, treasure_lookup

    def check_colli_with_marine(self, new_marine, pirate_ships, treasure_lookup):
        pirate_ships_updated = pirate_ships
        treasure_lookup_updated = treasure_lookup
        for m in range(len(new_marine)):
            for p in range(len(pirate_ships)):
                if new_marine[m][1] == pirate_ships[p][1] and pirate_ships[p][2] > 0:
                    for t in range(len(pirate_ships[p][3])):
                        treasure = int(pirate_ships[p][3][t].split("_")[1])
                        treasure_lookup_updated = tuple(
                            (treasure_lookup[i][0], treasure_lookup[i][1], 0) if i == treasure else treasure_lookup[i]
                            for i in range(len(treasure_lookup)))
                    ship = pirate_ships[p]
                    pirate_ships_updated = tuple(
                        (ship[0], ship[1], 0, (), ship[4]) if i == p else pirate_ships[i]
                        for i in range(len(pirate_ships)))
        return pirate_ships_updated, treasure_lookup_updated



    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        treasure_lookup = state[2]
        for i in range(len(treasure_lookup)):
            if treasure_lookup[i][2] == 0 or treasure_lookup[i][2] == 2:
                return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

        return self.h3(node)+self.h1(node)

    def empty_island(self, state, location):
        for t in range(len(state[2])):
            if state[2][t][1] == location:
                if state[2][t][2] == 0:
                    return False

        return True
    def h3(self, node):
        """
        number of pirates that are adjacent to an empty island
        """
        pirate_ships = node.state[0]
        map = node.state[4]
        adjacent = 0
        for p in range(len(pirate_ships)):
            x, y = pirate_ships[p][1]
            if x - 1 >= 0 and map[x - 1][y] == "I":
                if self.empty_island(node.state, (x - 1, y)):
                    adjacent += 1
            if x + 1 < len(map) and map[x + 1][y] == "I":
                if self.empty_island(node.state, (x + 1, y)):
                    adjacent += 1
            if y - 1 >= 0 and map[x][y - 1] == "I":
                if self.empty_island(node.state, (x, y - 1)):
                    adjacent += 1
            if y + 1 < len(map[0]) and map[x][y + 1] == "I":
                if self.empty_island(node.state, (x, y + 1)):
                    adjacent += 1
        return adjacent

    def h1(self, node):
        """number of uncollected treasures divided by the number of pirates."""
        treasure_lookup = node.state[2]
        num_of_pirates = len(node.state[0])
        # num of treasure where collected is no
        uncollected = 0
        for t in range(len(treasure_lookup)):
            if treasure_lookup[t][2] == 0:
                uncollected += 1

        return uncollected / num_of_pirates

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def manhattan_distance(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def surrounded(self, map, x, y):
        if x - 1 >= 0 and map[x - 1][y] == "I":
            if x + 1 < len(map) and map[x + 1][y] == "I":
                if y - 1 >= 0 and map[x][y - 1] == "I":
                    if y + 1 < len(map[0]) and map[x][y + 1] == "I":
                        return True
        return False

    def h2(self, node):
        """Sum of the distances from the pirate base to the closest sea cell adjacent to a treasure -
            for each treasure, divided by the number of pirates. If there is a treasure which all the
            adjacent cells are islands – return infinity"""

        treasure_lookup = node.state[2]
        pirate_ships = node.state[0]
        pirate_base = pirate_ships[0][4]
        dist = 0
        for t in range(len(treasure_lookup)):
            treasure = treasure_lookup[t]
            tx, ty = treasure[1]
            px, py = pirate_base
            if self.surrounded(node.state[4], tx, ty):
                return math.inf
            elif treasure[2] == 0:
                manhattan_dist = self.manhattan_distance(tx, ty, px, py)
                dist += manhattan_dist
        for p in range(len(pirate_ships)):
            if pirate_ships[p][2] > 0:
                px, py = pirate_ships[p][1]
                bx, by = pirate_base
                manhattan_dist = self.manhattan_distance(bx, by, px, py)
                dist += manhattan_dist
        return dist / len(pirate_ships)

    # location functions

    def locate_treasures(self, initial):
        # return the locations of the treasures
        return [t for t in initial["treasures"].values()]

    def pirate_base_locations(self, initial):
        # return the locations of the pirate bases
        return initial["pirate_ships"].values()

    def Update_Map(self, current_map, ux, uy, value):
        state_tuple = current_map[ux]
        updated_tuple = state_tuple[:uy] + [value, ] + state_tuple[uy + 1:]
        updated_map = current_map[:ux] + [updated_tuple, ] + current_map[ux + 1:]
        return updated_map

    def check_adjacency(self, map, current_location):
        adjacent_tiles = []
        x, y = current_location
        if x - 1 >= 0 and map[x - 1][y] != "I":
            adjacent_tiles.append((x - 1, y))
        if x + 1 < len(map) and map[x + 1][y] != "I":
            adjacent_tiles.append((x + 1, y))
        if y - 1 >= 0 and map[x][y - 1] != "I":
            adjacent_tiles.append((x, y - 1))
        if y + 1 < len(map[0]) and map[x][y + 1] != "I":
            adjacent_tiles.append((x, y + 1))
        return adjacent_tiles

    def mapout(self, initial, treasure_lookup):

        treasure_locations = self.locate_treasures(initial)
        treasure_maps = {}
        if len(treasure_locations) == 1:
            treasure_maps["treasure_1"] = initial["map"]
        else:
            for treasure1 in treasure_lookup:
                current_map = initial["map"]
                for treasure2 in treasure_lookup:
                    if treasure1 != treasure2:
                        current_map = self.Update_Map(current_map, treasure2[1][0],
                                                      treasure2[1][1], 'S')
                treasure_maps[f"treasure_{treasure1[0]}"] = current_map
        for treasure in treasure_maps:
            for row in range(len(treasure_maps[treasure])):
                for cell in range(len(treasure_maps[treasure][0])):
                    treasure_maps[treasure] = self.Update_Map(treasure_maps[treasure], row, cell,
                                                              (treasure_maps[treasure][row][cell], 0))
        locations = []
        for treasure in treasure_maps:
            treasure_maps[treasure] = self.Update_Map(treasure_maps[treasure], initial["treasures"][treasure][0],
                                                      initial["treasures"][treasure][1], (0, 1))
            locations.append(initial["treasures"][treasure])
            while locations:
                current_location = locations.pop()
                dist = treasure_maps[treasure][current_location[0]][current_location[1]][0]
                adjacent_tiles = self.check_adjacency(treasure_maps[treasure], current_location)
                for tile in adjacent_tiles:
                    x, y = tile
                    if treasure_maps[treasure][x][y][1] == 0 or treasure_maps[treasure][x][y][0] > dist + 1:
                        locations.append(tile)
                        treasure_maps[treasure] = self.Update_Map(treasure_maps[treasure], x, y, (dist + 1, 1))
        ready_map = initial["map"]
        for row in range(len(ready_map)):
            for cell in range(len(ready_map[0])):
                min_dist = math.inf
                for treasure in treasure_maps:
                    if treasure_maps[treasure][row][cell][0] < min_dist:
                        min_dist = treasure_maps[treasure][row][cell][0]
                ready_map = self.Update_Map(ready_map, row, cell, min_dist)
        tuple_map = tuple(tuple(inner_list) for inner_list in ready_map)
        return tuple_map

    # consruction functions

    def create_pirate_ships(self, pirate_base_location, number_of_ships):
        # create the pirate ships list, every ship has a location and a load
        """

       pirate ships structure:
         (ship number, location, load, loaded_treasure_name, pirate_base_location)
        """
        pirate_ships = ()
        for i in range(number_of_ships):
            pirate_ships += ((i + 1, pirate_base_location, 0, (), pirate_base_location),)

        return pirate_ships

    def create_treasure_lookup(self, initial):
        treasure_lookup = ()
        """
        treasure_lookup structure:
        (treasure number, location, collected)
        collected can be "no" = 0 , "yes" = 1 or "pending" = 2
        """
        for i, treasure in enumerate(initial["treasures"]):
            treasure_lookup += ((i + 1, initial["treasures"][treasure], 0),)

        return treasure_lookup

    def create_marine_ships(self, initial):
        """
        marine_ships structure:
        (marine number, location, path)
        """
        marine_ships = ()

        for i, marine in enumerate(initial["marine_ships"]):
            path = initial["marine_ships"][marine]
            back_path = path[1:-1][::-1]
            path = tuple(path + back_path)
            marine_ships += ((i + 1, initial["marine_ships"][marine][0],
                              path),)

        return marine_ships

    # map functions

    def print_map(self, state):
        # print the map for debugging
        for i in range(len(state[3])):
            print(state[3][i])

    # marine ship functions

    def location_index_in_path(self, location, path):
        # return the index of the location in the path
        return path.index(location)

    def move_marine_ship(self, state):
        shift_left = lambda t: t[1:] + (t[0],) if len(t) > 2 else t[::-1]
        current_marine_ships = state[1]

        new_marine_ships = tuple((i + 1, current_marine_ships[i][2][1 * (len(current_marine_ships[i][2]) - 1)],
                                  shift_left(current_marine_ships[i][2])) for i in
                                 range(len(current_marine_ships)))
        return new_marine_ships

    def is_ship_full(self, ship):
        # check if the ship is full
        return ship[2] >= 2

    def pirate_sailing_options(self, state, p):
        # move the pirate ships
        pirate_ships = state[0]
        original_map = state[4]
        movements = ()
        map = state[3]
        for i in range(len(pirate_ships)):
            if i == p:
                x, y = pirate_ships[i][1]
                if x - 1 >= 0 and original_map[x - 1][y] != "I":
                    movements += (("sail", f"pirate_{i + 1}", (x - 1, y)),)
                if x + 1 < len(map) and original_map[x + 1][y] != "I":
                    movements += (("sail", f"pirate_{i + 1}", (x + 1, y)),)
                if y - 1 >= 0 and original_map[x][y - 1] != "I":
                    movements += (("sail", f"pirate_{i + 1}", (x, y - 1)),)
                if y + 1 < len(map[0]) and original_map[x][y + 1] != "I":
                    movements += (("sail", f"pirate_{i + 1}", (x, y + 1)),)
        return movements

    def treasure_adjacent(self, treasure, ship):
        # check if the treasure is adjacent to the ship
        if abs(treasure[1][0] - ship[1][0]) + abs(
                treasure[1][1] - ship[1][1]) == 1 and \
                treasure[2] == 0:
            return True

        return False

    def pirate_loading_options(self, state, pirate):
        # load the treasures
        loading_actions = ()
        pirate_ships = state[0]
        treasures = state[2]
        for p in range(len(pirate_ships)):
            if p == pirate:
                for t in range(len(treasures)):
                    if self.treasure_adjacent(treasures[t], pirate_ships[p]) and not self.is_ship_full(
                            pirate_ships[p]):
                        loading_actions += (("collect_treasure", f"pirate_{p + 1}", f"treasure_{t + 1}"),)
        return loading_actions

    def pirate_waiting_options(self, state, p):
        # wait for the next turn
        pirate_ships = state[0]
        waiting_actions = ()
        for ship in range(len(pirate_ships)):
            if ship == p:
                waiting_actions += (("wait", f"pirate_{ship + 1}"),)
        return waiting_actions

    def pirate_unloading_options(self, state, pirate):
        # unload the treasures
        pirate_ships = state[0]
        unloading_actions = ()
        for p in range(len(pirate_ships)):
            if p == pirate:
                if pirate_ships[p][2] > 0 and pirate_ships[p][1] == pirate_ships[p][4]:
                    unloading_actions += (("deposit_treasure", f"pirate_{p + 1}"),)
        return unloading_actions


def create_onepiece_problem(game):
    return OnePieceProblem(game)