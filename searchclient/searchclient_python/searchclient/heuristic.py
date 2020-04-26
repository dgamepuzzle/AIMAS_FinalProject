from abc import ABCMeta, abstractmethod
from state import State
from collections import defaultdict
from hungarian import Hungarian

import sys

class Heuristic(metaclass=ABCMeta):
    
    def __init__(self, initial_state: 'State', backwards=False):
        
        self.goalCoords = defaultdict(list)
        self.goalDists = defaultdict(list)
        
        # Loop through the goals, and save their coordinates
        if not backwards:
            for i in range(len(State.goals)):
                for j in range(len(State.goals[i])):
                    if State.goals[i][j] is None:
                        continue
                    if State.goals[i][j] in 'abcdefghijklmnopqrstuvwxyz':
                        self.goalCoords[State.goals[i][j]].append((i, j))
                        dists_from_goal = Heuristic.grid_bfs(State.walls, (i, j))
                        self.goalDists[State.goals[i][j]].append(dists_from_goal)
        else:
            self.goalCoords = Heuristic.findBoxCoords(initial_state)
            for goalType in self.goalCoords:
                for i in range(len(self.goalCoords[goalType])):
                    self.goalDists[State.goals[i][j]].append(self.goalCoords[goalType][i])
            
    @staticmethod
    def grid_bfs(walls, start_coords):
        row_cnt = len(walls)
        col_cnt = len(walls[0])
        grid_dist = [[0 for j in range(col_cnt)] for i in range(row_cnt)]
        
        start = (start_coords[0], start_coords[1], 0)
        frontier = [start]
        visited = set()
        offsets = ((0, 1), (1, 0), (-1, 0), (0, -1))
        
        while len(frontier) > 0:
            current = frontier.pop(0)
            grid_dist[current[0]][current[1]] = current[2]            
            for offset in offsets:
                x = current[0] + offset[0]
                y = current[1] + offset[1]                
                if (x < 0) or (x >= row_cnt):
                    continue
                if (y < 0) or (y >= col_cnt):
                    continue            
                if walls[x][y]:
                    continue
                candidate = (x, y, current[2]+1)
                cand_check = (x, y)                
                if cand_check not in visited:
                    frontier.append(candidate)                
            visited.add((current[0], current[1]))        
        return grid_dist
    
    @staticmethod
    def findBoxCoords(state: 'State'):
        boxCoords = defaultdict(list)
    
        for i in range(len(state.boxes)):
            for j in range(len(state.boxes[i])):
                if state.boxes[i][j] is None:
                    continue
                if state.boxes[i][j] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    boxCoords[state.boxes[i][j].lower()].append((i, j))
                    
        return boxCoords
    
    def real_dist(self, state: 'State') -> 'int':
        boxCoords = Heuristic.findBoxCoords(state)
        totalDist = 0
        
        for goalType in self.goalDists:
            box_cnt = len(boxCoords[goalType])
            goal_cnt = len(self.goalDists[goalType])
            
            box_goal_d = []
            
            for i in range(box_cnt):
                box_x = boxCoords[goalType][i][0]
                box_y = boxCoords[goalType][i][1]
                
                dists_from_this_box = [float('inf')] * goal_cnt
                
                for j in range(goal_cnt):
                    dists_from_this_box[j] = self.goalDists[goalType][j][box_x][box_y]
                
                box_goal_d.append(dists_from_this_box)
                
            #for box_dists in box_goal_d:
            #    totalDist += min(box_dists)
                
            #for i in range(goal_cnt):
            #    totalDist += 0.01 * self.goalDists[goalType][i][state.agent_row][state.agent_col]
            
            #print(box_goal_d, file=sys.stderr, flush=True)
            
            hu = Hungarian()
            hu.solve(box_goal_d)
            totalDist += hu.get_min_cost()
            
            #print("%d %d" % (len(box_goal_d), len(box_goal_d[0])), file=sys.stderr, flush=True)
        return totalDist
        
    
    def h(self, state: 'State') -> 'int':
        return self.real_dist(state);
    
    @abstractmethod
    def f(self, state: 'State') -> 'int': pass
    
    @abstractmethod
    def __repr__(self): raise NotImplementedError


class AStar(Heuristic):
    def __init__(self, initial_state: 'State', backwards=False):
        super().__init__(initial_state, backwards)
    
    def f(self, state: 'State') -> 'int':
        return state.g + self.h(state)
    
    def __repr__(self):
        return 'A* evaluation'


class WAStar(Heuristic):
    def __init__(self, initial_state: 'State', w: 'int', backwards=False):
        super().__init__(initial_state, backwards)
        self.w = w
    
    def f(self, state: 'State') -> 'int':
        return state.g + self.w * self.h(state)
    
    def __repr__(self):
        return 'WA* ({}) evaluation'.format(self.w)


class Greedy(Heuristic):
    def __init__(self, initial_state: 'State', backwards=False):
        super().__init__(initial_state, backwards)
    
    def f(self, state: 'State') -> 'int':
        return self.h(state)
    
    def __repr__(self):
        return 'Greedy evaluation'

