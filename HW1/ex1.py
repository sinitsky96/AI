import search
import random
import math

ids = ["111111111", "111111111"]


class OnePieceProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        treasure_lookup = self.create_treasure_lookup(initial)
        pirate_base_location=initial["pirate_ships"]["pirate_ship_1"]
        pirate_ships = self.create_pirate_ships(pirate_base_location, len(initial["pirate_ships"]))
        current_map = initial["map"]
        marine_ships = self.create_marine_ships(initial)

        initial = (pirate_ships, marine_ships, treasure_lookup, current_map)
        actions= self.actions(initial)
        print(actions)

        search.Problem.__init__(self, initial)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        movements = self.pirate_sailing_options(state)
        loadings = self.pirate_loading_options(state)
        waitings = self.pirate_waiting_options(state)
        unloadings = self.pirate_unloading_options(state)
        return movements + loadings + waitings + unloadings


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""

    def h1(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate
        number of uncollected treasures divided by the number of pirates."""
        treasure_lookup= node.state[2]
        num_of_pirates= len(node.state[0])
        #num of treasure where collected is no
        uncollected=0
        for treasure in treasure_lookup:
            if treasure_lookup[treasure]["collected"]=="no":
                uncollected+=1

        return uncollected/num_of_pirates

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    # location functions

    def locate_treasures(self, initial):
        # return the locations of the treasures
        return [t for t in initial["treasures"].values()]

    def pirate_base_locations(self, initial):
        # return the locations of the pirate bases
        return initial["pirate_ships"].values()

    # consruction functions

    def create_pirate_ships(self, pirate_base_location, number_of_ships):
        # create the pirate ships list, every ship has a location and a load
        pirate_ships = {}
        for i in range(number_of_ships):
            pirate_ships[f"pirate_{i + 1}"] = {"location": pirate_base_location, "load": 0,
                                               "loaded_treaure_location": []}
        return pirate_ships

    def create_treasure_lookup(self, initial):
        treasure_lookup = {}
        for treasure in initial["treasures"]:
            treasure_lookup[treasure] = {"location": initial["treasures"][treasure], "collected": "no"}
        # collected can be "no", "yes" or "pending"
        return treasure_lookup

    def create_marine_ships(self, initial):
        marine_ships = {}
        for marine in initial["marine_ships"]:
            marine_ships[marine] = {"location": initial["marine_ships"][marine][0],
                                    "path": initial["marine_ships"][marine]}
        return marine_ships

    # map functions

    def Update_Map(self, state, x, y, value):
        # update the map with the new value
        updated_map = state[3]
        updated_map[x][y] = value
        return updated_map

    def print_map(self, state):
        # print the map for debugging
        for i in range(len(state[3])):
            print(state[3][i])

    # marine ship functions

    def location_index_in_path(self, location, path):
        # return the index of the location in the path
        return path.index(location)

    def move_marine_ship(self, state):
        current_marine_ships = state[1]
        for marine in current_marine_ships:
            initial_location = current_marine_ships[marine]["location"]
            path = current_marine_ships[marine]["path"]
            index = self.location_index_in_path(initial_location, path)
            if index + 1 < len(path):
                current_marine_ships[marine]["location"] = path[index + 1]
            else:
                current_marine_ships[marine]["location"] = path[index - 1]
                current_marine_ships[marine]["path"] = path[::-1]
        return current_marine_ships

    def is_ship_full(self, ship):
        # check if the ship is full
        return ship["load"] >= 2

    def pirate_sailing_options(self, state):
        # move the pirate ships
        pirate_ships = state[0]
        movements = ()
        map = state[3]
        for ship in pirate_ships:
            x, y = pirate_ships[ship]["location"]
            if x - 1 >= 0 and map[x - 1][y] != "I":
                movements += (("sail", ship, (x - 1, y)),)
            if x + 1 < len(map) and map[x + 1][y] != "I":
                movements += (("sail", ship, (x + 1, y)),)
            if y - 1 >= 0 and map[x][y - 1] != "I":
                movements += (("sail", ship, (x, y - 1)),)
            if y + 1 < len(map[0]) and map[x][y + 1] != "I":
                movements += (("sail", ship, (x, y + 1)),)
        return movements

    def treasure_adjacent(self, treasure, ship):
        # check if the treasure is adjacent to the ship
        if abs(treasure["location"][0] - ship["location"][0]) + abs(
                treasure["location"][1] - ship["location"][1]) == 1 and \
                treasure["collected"] == "no":
            return True

        return False

    def pirate_loading_options(self, state):
        # load the treasures
        loading_actions = ()
        pirate_ships = state[0]
        treasures = state[2]
        for ship in pirate_ships:
            for treasure in treasures:
                if self.treasure_adjacent(treasures[treasure], pirate_ships[ship]) and not self.is_ship_full(
                        pirate_ships[ship]):
                    loading_actions += (("“collect_treasure", ship, treasure),)
        return loading_actions

    def pirate_waiting_options(self, state):
        # wait for the next turn
        pirate_ships = state[0]
        waiting_actions = ()
        for ship in pirate_ships:
            waiting_actions += ("wait", ship)
        return waiting_actions

    def pirate_unloading_options(self, state):
        # unload the treasures
        pirate_ships = state[0]
        map = state[3]
        unloading_actions = ()
        for ship in pirate_ships:
            x, y = pirate_ships[ship]["location"]
            if pirate_ships[ship]["load"] > 0 and map[x][y] == "B":
                unloading_actions += (("deposit_treasure", ship),)
        return unloading_actions


def create_onepiece_problem(game):
    return OnePieceProblem(game)
