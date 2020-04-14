from abc import ABCMeta, abstractmethod
from state import State
from collections import defaultdict

import sys

class Heuristic(metaclass=ABCMeta):
    
    def __init__(self, initial_state: 'State', backwards=False):
        
        self.goalCoords = defaultdict(list)
        
        # Loop through the goals, and save their coordinates
        if not backwards:
            for i in range(len(State.goals)):
                for j in range(len(State.goals[i])):
                    if State.goals[i][j] is None:
                        continue
                    if State.goals[i][j] in 'abcdefghijklmnopqrstuvwxyz':
                        self.goalCoords[State.goals[i][j]].append((i, j))
        else:
            self.goalCoords = Heuristic.findBoxCoords(initial_state)
            #print(self.goalCoords, file=sys.stderr, flush=True)
    
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
    
    def manhattan(self, state: 'State') -> 'int':
        boxCoords = Heuristic.findBoxCoords(state)
        totalDist = 0
        
        for goalType in self.goalCoords:
            for i in range(len(self.goalCoords[goalType])):
                goalCoord = self.goalCoords[goalType][i]
                minDist = float('inf')
                for j in range(len(boxCoords[goalType])):
                    boxCoord = boxCoords[goalType][j]
                    dist = abs(goalCoord[0] - boxCoord[0]) + \
                    abs(goalCoord[1] - boxCoord[1])
                    if dist < minDist:
                        minDist = dist
                    totalDist += minDist
        #print(totalDist, file=sys.stderr, flush=True)
        return totalDist
        
    
    def h(self, state: 'State') -> 'int':
        return self.manhattan(state);
    
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

