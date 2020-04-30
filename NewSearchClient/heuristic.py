from abc import ABCMeta, abstractmethod
from collections import defaultdict
import sys
from state import State

from hungarian import Hungarian

class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State'):
        # Here's a chance to pre-process the static parts of the level.
        print(initial_state.goals[0].coords, file=sys.stderr, flush=True)
        print(initial_state.goals[0].letter, file=sys.stderr, flush=True)
        
        # Stores arrays of size (MAX_ROW, MAX_COL), denoting minimum push
        # distances from each goal (might use graphs instead).
        # The data is grouped by colors, for easier lookup.
        self.goalDistances = defaultdict(list)
        self.goalCoords = defaultdict(list)
        self.goalIds = defaultdict(list)
        self.goalBoxAssignments = defaultdict(list)
        self.agentBoxAssignments = defaultdict(list)
        self.boxesIdsInGoal = set()
        
        for goal in initial_state.goals:
            print(goal.id, file=sys.stderr, flush=True)
            self.goalDistances[goal.letter.lower()].append(
                Heuristic.gridBfs(initial_state.walls, goal.coords)
            )
            self.goalCoords[goal.letter.lower()].append(goal.coords)
            self.goalIds[goal.letter.lower()].append(goal.id)
            
        self.resetAssignments(initial_state)
        print('G_B_ASS', file=sys.stderr, flush=True)
        print(self.goalBoxAssignments, file=sys.stderr, flush=True)
        print('A_B_ASS', file=sys.stderr, flush=True)
        print(self.agentBoxAssignments, file=sys.stderr, flush=True)
    
    def h(self, state: 'State') -> 'int':
        
        return self.real_dist(state)
    
    @staticmethod
    def gridBfs(walls, startCoords):
        rowCnt = len(walls)
        colCnt = len(walls[0])
        gridDistances = [[0 for j in range(colCnt)] for i in range(rowCnt)]
        
        start = (startCoords[0], startCoords[1], 0)
        frontier = [start]
        visited = set()
        offsets = ((0, 1), (1, 0), (-1, 0), (0, -1))
        
        while len(frontier) > 0:
            current = frontier.pop(0)
            gridDistances[current[0]][current[1]] = current[2]            
            for offset in offsets:
                x = current[0] + offset[0]
                y = current[1] + offset[1]                
                if (x < 0) or (x >= rowCnt):
                    continue
                if (y < 0) or (y >= colCnt):
                    continue            
                if walls[x][y]:
                    continue
                candidate = (x, y, current[2]+1)
                candidateCheck = (x, y)                
                if candidateCheck not in visited:
                    frontier.append(candidate)                
            visited.add((current[0], current[1]))        
        return gridDistances
    
    @staticmethod
    def get_distance(walls, start_coords, end_coords):
        row_cnt = len(walls)
        col_cnt = len(walls[0])
        
        start = (start_coords[0], start_coords[1], 0)
        frontier = [start]
        visited = set()
        offsets = ((0, 1), (1, 0), (-1, 0), (0, -1))
        
        while len(frontier) > 0:
            current = frontier.pop(0)
            
            if current[0] == end_coords[0] and current[1] == end_coords[1]:
                return current[2]
            
            for offset in offsets:
                x = current[0] + offset[0]
                y = current[1] + offset[1]
                
                if (x < 0) or (x > row_cnt):
                    continue
                if (y < 0) or (y > col_cnt):
                    continue            
                if walls[x][y]:
                    continue
                    
                candidate = (x, y, current[2]+1)
                cand_check = (x, y)
                
                if cand_check not in visited:
                    frontier.append(candidate)
                
            visited.add((current[0], current[1]))
        
        return float('inf')
    
    @staticmethod
    def get_distance_one_to_many(walls, start_coords, end_coords_array):
        row_cnt = len(walls)
        col_cnt = len(walls[0])
    
        distances = [float('inf') for i in range(len(end_coords_array))]
        cnt_found = 0
        
        start = (start_coords[0], start_coords[1], 0)
        frontier = [start]
        visited = set()
        offsets = ((0, 1), (1, 0), (-1, 0), (0, -1))
        
        while len(frontier) > 0:
            current = frontier.pop(0)
            
            if current[0:2] in end_coords_array:
                end_coord_idx = end_coords_array.index(current[0:2])
                distances[end_coord_idx] = current[2]
                cnt_found += 1
                if cnt_found >= len(end_coords_array):
                    return distances
            
            for offset in offsets:
                x = current[0] + offset[0]
                y = current[1] + offset[1]
                
                if (x < 0) or (x > row_cnt):
                    continue
                if (y < 0) or (y > col_cnt):
                    continue            
                if walls[x][y]:
                    continue
                    
                candidate = (x, y, current[2]+1)
                cand_check = (x, y)
                
                if cand_check not in visited:
                    frontier.append(candidate)
                
            visited.add((current[0], current[1]))
        
        return distances
    
    def resetAssignments(self, state: 'State'):
        
        self.goalBoxAssignments = defaultdict(list)
        self.boxAgentAssignments = defaultdict(list)
        
        boxIds = defaultdict(list)
        boxCoords= defaultdict(list)
        
        for box in state.boxes:
            boxIds[box.letter.lower()].append(box.id)
            boxCoords[box.letter.lower()].append(box.coords) 
        
        for goalType in self.goalDistances:
            boxCoordss = boxCoords[goalType]
            goalDists = self.goalDistances[goalType]
            
            box_cnt = len(boxCoordss)
            goal_cnt = len(goalDists)
            
            distMatrix = [[goalDists[i][boxCoordss[j][0]][boxCoordss[j][1]] for j in range(box_cnt)] for i in range(goal_cnt)]
            
            # dist matrix:
            #         box1 box2 box3
            # goal1    1    5    3
            # goal2    8    7    5
            # goal3    2    10   7
            
            h = Hungarian()
            h.solve(distMatrix)
            assignments = h.get_assignments()
            idAssignments = [(self.goalIds[goalType][assignment[0]], boxIds[goalType][assignment[0]]) for assignment in assignments]
            self.goalBoxAssignments[goalType] = idAssignments
            
        boxIds = defaultdict(list)
        boxCoords= defaultdict(list)
        agentIds = defaultdict(list)
        agentCoords = defaultdict(list)
        
        assignedBoxIds = defaultdict(list)
        for goalType in self.goalBoxAssignments:
            assignedBoxIds[goalType] = [ass[1] for ass in self.goalBoxAssignments[goalType]]
        
        for box in state.boxes:
            
            if box.id not in assignedBoxIds[box.letter.lower()]:
                continue
            print(box.id, file=sys.stderr, flush=True)
            boxIds[box.color].append(box.id)
            boxCoords[box.color].append(box.coords)
            
        for agent in state.agents:
            agentIds[agent.color].append(agent.id)
            agentCoords[agent.color].append(agent.coords)
    
        for agentColor in agentCoords:
            boxCoordss = boxCoords[agentColor]
            agentCoordss = agentCoords[agentColor]
            
            box_cnt = len(boxCoords)
            
            distMatrix = [Heuristic.get_distance_one_to_many(State.walls, agentCoord, boxCoordss) for agentCoord in agentCoordss]
            
            h = Hungarian()
            h.solve(distMatrix)
            assignments = h.get_assignments()
            idAssignments = [(agentIds[agentColor][assignment[0]], boxIds[agentColor][assignment[1]]) for assignment in assignments]
            self.agentBoxAssignments[agentColor] = idAssignments
        

    
    def real_dist(self, state: 'State') -> 'int':
        
        #self.resetAssignments(state)
        
        goalBoxMultiplier = 2
        
        totalDist = 0
        
        for goalType in self.goalBoxAssignments:

            goalBoxAss = self.goalBoxAssignments[goalType]
            goalDists = self.goalDistances[goalType]

            for i in range(len(goalBoxAss)):
                
                current_box_coords = next(box for box in state.boxes if box.id == goalBoxAss[i][1]).coords
                totalDist += (goalDists[i][current_box_coords[0]][current_box_coords[1]] * goalBoxMultiplier)
            
        for agentColor in self.agentBoxAssignments:
            
            for assignment in self.agentBoxAssignments[agentColor]:
                currentAgentCoords = next(agent for agent in state.agents if agent.id == assignment[0]).coords
                currentBoxCoords = next(box for box in state.boxes if box.id == assignment[1]).coords
                totalDist += Heuristic.get_distance(State.walls, currentAgentCoords, currentBoxCoords)
            
        return totalDist
        
    @abstractmethod
    def f(self, state: 'State') -> 'int': pass
    
    @abstractmethod
    def __repr__(self): raise NotImplementedError


class AStar(Heuristic):
    def __init__(self, initial_state: 'State'):
        super().__init__(initial_state)
    
    def f(self, state: 'State') -> 'int':
        return state.g + self.h(state)
    
    def __repr__(self):
        return 'A* evaluation'


class WAStar(Heuristic):
    def __init__(self, initial_state: 'State', w: 'int'):
        super().__init__(initial_state)
        self.w = w
    
    def f(self, state: 'State') -> 'int':
        return state.g + self.w * self.h(state)
    
    def __repr__(self):
        return 'WA* ({}) evaluation'.format(self.w)


class Greedy(Heuristic):
    def __init__(self, initial_state: 'State'):
        super().__init__(initial_state)
    
    def f(self, state: 'State') -> 'int':
        return self.h(state)
    
    def __repr__(self):
        return 'Greedy evaluation'

