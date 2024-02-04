import search
import random
import math


ids = ["id1", "id2"]


class WumpusProblem(search.Problem):
    """This class implements a wumpus problem"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        goldlocations = self.where_gold(initial)
        distmap = self.mapCalc(initial, goldlocations)
        initial = (initial, (0,), goldlocations, distmap)
        search.Problem.__init__(self, initial)


    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        N = len(self.initial[0])
        M = len(self.initial[0][0])
        movements = self.Move(state, self.where_heros(state), N, M)
        shooting = self.Shoot(state, self.where_heros(state), N, M)
        actions = movements + shooting
        return actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        herolocations = self.where_heros(state)
        hero_x_y = ()
        for hero in herolocations:
            if hero[0] == action[1]:
                hero_x_y = (hero[1], hero[2])
                break
        current_map = state[0]
        current_key = state[1]
        if action[0] == "move":
            current_map = self.Update_Map(current_map, hero_x_y[0], hero_x_y[1], 10)
            if action[2] == "R":
                current_map, ismonster = self.Kill_Monsters_Sword(current_map, hero_x_y[0], hero_x_y[1] + 1)
                if ismonster == 0:
                    if self.is_key(current_map, hero_x_y[0], hero_x_y[1] + 1):
                        current_key = self.Update_Key(state, hero_x_y[0], hero_x_y[1] + 1)
                    current_map = self.Update_Map(current_map, hero_x_y[0], hero_x_y[1] + 1, action[1])
            elif action[2] == "L":
                current_map, ismonster = self.Kill_Monsters_Sword(current_map, hero_x_y[0], hero_x_y[1] - 1)
                if ismonster == 0:
                    if self.is_key(current_map, hero_x_y[0], hero_x_y[1] - 1):
                        current_key = self.Update_Key(state, hero_x_y[0], hero_x_y[1] - 1)
                    current_map = self.Update_Map(current_map, hero_x_y[0], hero_x_y[1] - 1, action[1])
            elif action[2] == "D":
                current_map, ismonster = self.Kill_Monsters_Sword(current_map, hero_x_y[0] + 1, hero_x_y[1])
                if ismonster == 0:
                    if self.is_key(current_map, hero_x_y[0] + 1, hero_x_y[1]):
                        current_key = self.Update_Key(state, hero_x_y[0] + 1, hero_x_y[1])
                    current_map = self.Update_Map(current_map, hero_x_y[0] + 1, hero_x_y[1], action[1])
            elif action[2] == "U":
                current_map, ismonster = self.Kill_Monsters_Sword(current_map, hero_x_y[0] - 1, hero_x_y[1])
                if ismonster == 0:
                    if self.is_key(current_map, hero_x_y[0] - 1, hero_x_y[1]):
                        current_key = self.Update_Key(state, hero_x_y[0] - 1, hero_x_y[1])
                    current_map = self.Update_Map(current_map, hero_x_y[0] - 1, hero_x_y[1], action[1])
        elif action[0] == "shoot":
            current_map = self.Kill_Monsters_Arrow(current_map, hero_x_y[0], hero_x_y[1], action[2])
        state = self.Update_State(current_map, current_key, state[2], state[3])
        return state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        goldlocations = state[2]
        for gold in goldlocations:
            if self.is_hero(state[0], gold[0], gold[1]):
                return True
        return False

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        herolocations = self.where_heros(node.state)
        value = ()
        for hero in herolocations:
            value = value + (node.state[3][hero[1]][hero[2]],)
        if not value:
            return 0
        elif len(node.state[0]) >= 15 and len(node.state[0][0]) >= 15:
            return min(value)
        else:
            return min(value) + node.path_cost / (node.depth + 1) + len(herolocations)

    def where_gold(self, initial):
        current_map = initial
        indexrow = -1
        indexcol = -1
        goldlocations = ()
        for row in current_map:
            indexrow += 1
            for cell in row:
                indexcol += 1
                if cell == 70:
                    goldlocations = goldlocations + ((indexrow, indexcol),)
            indexcol = -1
        return goldlocations

    def where_heros(self, state):
        current_map = state[0]
        indexrow = -1
        indexcol = -1
        herolocations = ()
        for row in current_map:
            indexrow += 1
            for cell in row:
                indexcol += 1
                if cell == 11 or cell == 12 or cell == 13 or cell == 14:
                    herolocations = herolocations + ((cell, indexrow, indexcol),)
            indexcol = -1
        return herolocations

    def is_key(self, current_map, x, y):
        if current_map[x][y] == 55 or current_map[x][y] == 56 or current_map[x][y] == 57 or current_map[x][y] == 58 or current_map[x][y] == 59:
            return True
        return False

    def is_door(self, current_map, x, y):
        if current_map[x][y] == 45 or current_map[x][y] == 46 or current_map[x][y] == 47 or current_map[x][y] == 48 or current_map[x][y] == 49:
            return True
        return False

    def is_hero(self, current_map, x, y):
        if current_map[x][y] == 11 or current_map[x][y] == 12 or current_map[x][y] == 13 or current_map[x][y] == 14:
            return True
        return False

    def have_door_key(self, state, x, y):
        for key in state[1]:
            if state[0][x][y] == key - 10:
                return True
        return False

    def Move(self, state, herolocations, N, M):
        movements = ()
        current_map = state[0]
        for hero in herolocations:
            """Right"""
            if hero[2]+1 < M:
                if current_map[hero[1]][hero[2] + 1] == 10 or current_map[hero[1]][hero[2] + 1] == 70 or (self.is_key(current_map, hero[1], hero[2] + 1) == True):
                    movements = movements + (("move", hero[0], "R"),)
                if self.is_door(current_map, hero[1], hero[2] + 1):
                    if self.have_door_key(state, hero[1], hero[2] + 1):
                        movements = movements + (("move", hero[0], "R"),)
            """Left"""
            if hero[2] - 1 >= 0:
                if current_map[hero[1]][hero[2] - 1] == 10 or current_map[hero[1]][hero[2] - 1] == 70 or (self.is_key(current_map, hero[1], hero[2] - 1) == True):
                    movements = movements + (("move", hero[0], "L"),)
                if self.is_door(current_map, hero[1], hero[2] - 1):
                    if self.have_door_key(state, hero[1], hero[2] - 1):
                        movements = movements + (("move", hero[0], "L"),)
            """Down"""
            if hero[1] + 1 < N:
                if current_map[hero[1] + 1][hero[2]] == 10 or current_map[hero[1] + 1][hero[2]] == 70 or (self.is_key(current_map, hero[1] + 1, hero[2]) == True):
                    movements = movements + (("move", hero[0], "D"),)
                if self.is_door(current_map, hero[1] + 1, hero[2]):
                    if self.have_door_key(state, hero[1] + 1, hero[2]):
                        movements = movements + (("move", hero[0], "D"),)
            """Up"""
            if hero[1] - 1 >= 0:
                if current_map[hero[1] - 1][hero[2]] == 10 or current_map[hero[1] - 1][hero[2]] == 70 or (self.is_key(current_map, hero[1] - 1, hero[2]) == True):
                    movements = movements + (("move", hero[0], "U"),)
                if self.is_door(current_map, hero[1] - 1, hero[2]):
                    if self.have_door_key(state, hero[1] - 1, hero[2]):
                        movements = movements + (("move", hero[0], "U"),)
        return movements

    def Shoot(self, state, herolocations, N, M):
        shooting = ()
        current_map = state[0]
        for hero in herolocations:
            """Right"""
            i = 1
            while hero[2]+i < M and current_map[hero[1]][hero[2]+i] != 20 and not self.is_hero(current_map, hero[1], hero[2]+i) and not self.is_door(current_map, hero[1], hero[2]+i):
                if current_map[hero[1]][hero[2]+i] == 60:
                    shooting = shooting + (("shoot", hero[0], "R"),)
                    break
                i += 1
            i = 1
            while hero[2]-i >= 0 and current_map[hero[1]][hero[2]-i] != 20 and not self.is_hero(current_map, hero[1], hero[2]-i) and not self.is_door(current_map, hero[1], hero[2]-i):
                if current_map[hero[1]][hero[2]-i] == 60:
                    shooting = shooting + (("shoot", hero[0], "L"),)
                    break
                i += 1
            """Down"""
            i = 1
            while hero[1] + i < N and current_map[hero[1]+i][hero[2]] != 20 and not self.is_hero(current_map, hero[1]+i, hero[2]) and not self.is_door(current_map, hero[1]+i, hero[2]):
                if current_map[hero[1]+i][hero[2]] == 60:
                    shooting = shooting + (("shoot", hero[0], "D"),)
                    break
                i += 1
            """Up"""
            i = 1
            while hero[1] - i >= 0 and current_map[hero[1] - i][hero[2]] != 20 and not self.is_hero(current_map, hero[1]-i, hero[2]) and not self.is_door(current_map, hero[1] - i, hero[2]):
                if current_map[hero[1] - i][hero[2]] == 60:
                    shooting = shooting + (("shoot", hero[0], "U"),)
                    break
                i += 1
        return shooting

    def Update_Map(self, current_map, ux, uy, value):
        state_tuple = current_map[ux]
        updated_tuple = state_tuple[:uy] + (value,) + state_tuple[uy + 1:]
        updated_map = current_map[:ux] + (updated_tuple,) + current_map[ux + 1:]
        return updated_map

    def Update_Key(self, state, ux, uy):
        state_key = state[1]
        if state_key[0] == 0:
            updated_key = (state[0][ux][uy],)
        else:
            updated_key = state_key + (state[0][ux][uy],)
        return updated_key

    def Update_State(self, current_map, current_key, goldlocations, distmap):
        updated_state = (current_map, current_key, goldlocations, distmap)
        return updated_state

    def Kill_Monsters_Sword(self, current_map, nx, ny):
        N = len(current_map)
        M = len(current_map[0])
        ismonster = 0
        "Right"
        if ny + 1 < M:
            if current_map[nx][ny+1] == 60:
                ismonster = 1
                current_map = self.Update_Map(current_map, nx, ny + 1, 10)
        "Left"
        if ny - 1 >= 0:
            if current_map[nx][ny - 1] == 60:
                ismonster = 1
                current_map = self.Update_Map(current_map, nx, ny - 1, 10)
        "Down"
        if nx + 1 < N:
            if current_map[nx + 1][ny] == 60:
                ismonster = 1
                current_map = self.Update_Map(current_map, nx + 1, ny, 10)
        "Up"
        if nx - 1 >= 0:
            if current_map[nx - 1][ny] == 60:
                ismonster = 1
                current_map = self.Update_Map(current_map, nx - 1, ny, 10)
        return current_map, ismonster

    def Kill_Monsters_Arrow(self, current_map, x, y, direction):
        i = 0
        j = 0
        while current_map[x+i][y+j] != 60:
            if direction == "R":
                j += 1
            if direction == "L":
                j -= 1
            if direction == "D":
                i += 1
            if direction == "U":
                i -= 1
        current_map = self.Update_Map(current_map, x + i, y + j, 10)
        return current_map

    def Amount_Monsters(self, current_map):
        monsters = 0
        for row in current_map:
            for cell in row:
                if cell == 60:
                    monsters += 1
        return monsters

    def Amount_Walls(self, current_map):
        walls = 0
        for row in current_map:
            for cell in row:
                if cell == 20:
                    walls += 1
        return walls

    def Amount_Holes(self, current_map):
        holes = 0
        for row in current_map:
            for cell in row:
                if cell == 30:
                    holes += 1
        return holes

    def Amount_Keys(self, current_map):
        keys = 0
        for row in current_map:
            for cell in row:
                if cell == 55 or cell == 56 or cell == 57 or cell == 58 or cell == 59:
                    keys += 1
        return keys

    def Amount_Doors(self, current_map, keys):
        doors = 0
        for row in current_map:
            for cell in row:
                if cell == 45 or cell == 46 or cell == 47 or cell == 48 or cell == 49:
                    have = 0
                    for key in keys:
                        if key == cell:
                            have = 1
                    if have == 0:
                        doors += 1
        return doors

    def Amount_Halls(self, current_map):
        halls = 0
        for row in current_map:
            for cell in row:
                if cell == 10:
                    halls += 1
        return halls

    def Square_Calc(self, node):
        guess = ()
        obstacles = ()
        totalguess = ()
        herolocations = self.where_heros(node.state)
        goldlocations = node.state[2]
        for hero in herolocations:
            minimum = abs(len(node.state[0])) + abs(len(node.state[0][0]))
            for gold in goldlocations:
                current_dist = abs(hero[1] - gold[0]) + abs(hero[2] - gold[1])
                if current_dist < minimum:
                    minimum = current_dist
            guess += ((hero[0], minimum),)

        for hero in herolocations:
            current_map = node.state[0]
            startrow = max(0, hero[1] - 1)
            endrow = min(len(node.state[0]), hero[1] + 2)
            square = current_map[startrow:endrow]
            startcol = max(0, hero[2] - 1)
            endcol = min(len(node.state[0][0]), hero[2] + 2)
            newsquare = ()
            for row in square:
                row = row[startcol:endcol]
                newsquare = newsquare + (row,)
            total = self.Amount_Monsters(newsquare) + self.Amount_Walls(newsquare) + self.Amount_Holes(newsquare) + self.Amount_Doors(newsquare, node.state[1]) - self.Amount_Halls(newsquare) / 5
            obstacles += ((hero[0], total),)
        for g in guess:
            for o in obstacles:
                if g[0] == o[0]:
                    totalguess += ((g[1] + o[1] + len(herolocations)),)
        if len(totalguess) == 0:
            return 0
        return min(totalguess)

    def mg(self, node):
        if self.goal_test(node.state):
            return 0
        minimum = 1000000
        herolocations = self.where_heros(node.state)
        goldlocations = node.state[2]
        for hero in herolocations:
            for gold in goldlocations:
                current_dist = abs(hero[1] - gold[0]) + abs(hero[2] - gold[1])
                if current_dist < minimum:
                     minimum = current_dist
        return minimum

    def mgmax(self, node):
        shortestdist = ()
        herolocations = self.where_heros(node.state)
        goldlocations = node.state[2]
        for hero in herolocations:
            minimum = abs(len(node.state[0])) + abs(len(node.state[0][0]))
            for gold in goldlocations:
                current_dist = abs(hero[1] - gold[0]) + abs(hero[2] - gold[1])
                if current_dist < minimum:
                    minimum = current_dist
            shortestdist += (minimum,)
        if len(shortestdist) == 0 or (len(shortestdist) == 1 and shortestdist[0] == 0):
            return 0
        closehero = min(shortestdist)
        farhero = max(shortestdist)
        if closehero == 0:
            closehero = 1
        if farhero == 0:
            farhero = 1
        obstacles = self.Amount_Monsters(node.state[0]) + self.Amount_Walls(node.state[0]) + self.Amount_Holes(node.state[0]) + self.Amount_Doors(node.state[0], node.state[1]) - self.Amount_Halls(node.state[0]) / 5
        obstacles = max(0, obstacles)
        return obstacles + (farhero + closehero) / farhero + len(herolocations)

    def adjacentCells(self, currentmap, currentplace):
        N = len(currentmap)
        M = len(currentmap[0])
        adjacentcells = []
        """Right"""
        if currentplace[1] + 1 < M:
            if currentmap[currentplace[0]][currentplace[1] + 1][0] != 20 and currentmap[currentplace[0]][currentplace[1] + 1][0] != 30:
                adjacentcells.append([currentplace[0], currentplace[1] + 1])
        """Left"""
        if currentplace[1] - 1 >= 0:
            if currentmap[currentplace[0]][currentplace[1] - 1][0] != 20 and currentmap[currentplace[0]][currentplace[1] - 1][0] != 30:
                adjacentcells.append([currentplace[0], currentplace[1] - 1])
        """Down"""
        if currentplace[0] + 1 < N:
            if currentmap[currentplace[0] + 1][currentplace[1]][0] != 20 and currentmap[currentplace[0] + 1][currentplace[1]][0] != 30:
                adjacentcells.append([currentplace[0] + 1, currentplace[1]])
        """Up"""
        if currentplace[0] - 1 >= 0:
            if currentmap[currentplace[0] - 1][currentplace[1]][0] != 20 and currentmap[currentplace[0] - 1][currentplace[1]][0] != 30:
                adjacentcells.append([currentplace[0] - 1, currentplace[1]])
        return adjacentcells

    def mapCalc(self, initial, goldlocations):
        mapcopy = []
        if len(goldlocations) == 1:
            mapcopy.append(initial)
        else:
            for gold1 in goldlocations:
                currentmap = initial
                for gold2 in goldlocations:
                    if gold1[0] != gold2[0] and gold1[1] != gold2[1]:
                        currentmap = self.Update_Map(currentmap, gold2[0], gold2[1], 10)
                mapcopy.append(currentmap)
        for map1 in range(len(mapcopy)):
            for row in range(len(mapcopy[0])):
                for cell in range(len(mapcopy[0][0])):
                    mapcopy[map1] = self.Update_Map(mapcopy[map1], row, cell, (mapcopy[map1][row][cell], 0))
        placeslist = []
        for map1 in range(len(mapcopy)):
            mapcopy[map1] = self.Update_Map(mapcopy[map1], goldlocations[map1][0], goldlocations[map1][1], (0, 1))
            placeslist.append([goldlocations[map1][0], goldlocations[map1][1]])
            while placeslist:
                currentplace = placeslist.pop()
                value = mapcopy[map1][currentplace[0]][currentplace[1]][0]
                adjacentcells = self.adjacentCells(mapcopy[map1], currentplace)
                for adjacentcell in range(len(adjacentcells)):
                    tempplace_x = adjacentcells[adjacentcell][0]
                    tempplace_y = adjacentcells[adjacentcell][1]
                    if mapcopy[map1][tempplace_x][tempplace_y][1] == 0 or mapcopy[map1][tempplace_x][tempplace_y][0] > value + 1:
                        placeslist.append(adjacentcells[adjacentcell])
                        mapcopy[map1] = self.Update_Map(mapcopy[map1], tempplace_x, tempplace_y, (value + 1, 1))
        calcmap = initial
        for row in range(len(initial)):
            for cell in range(len(initial[0])):
                minvalue = 100000000000
                for map1 in range(len(mapcopy)):
                    if mapcopy[map1][row][cell][0] < minvalue:
                        minvalue = mapcopy[map1][row][cell][0]
                calcmap = self.Update_Map(calcmap, row, cell, minvalue)
        return calcmap

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

def create_wumpus_problem(game):
    return WumpusProblem(game)
