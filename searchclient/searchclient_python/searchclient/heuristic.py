from abc import ABCMeta, abstractmethod
from state import State


class Heuristic(metaclass=ABCMeta):
    
    goalCoords = []
    
    def __init__(self, initial_state: 'State'):
        for row in range(State.maxRow):
            for col in range(State.maxCol):
                if State.goals[row][col]:
                    Heuristic.goalCoords.append((row, col))
        
        
    def findBoxCoords(self, state: 'State'):
        boxCoords = []
        for row in range(State.maxRow):
            for col in range(State.maxCol):
                if state.boxes[row][col]:
                    boxCoords.append((row, col))
        return boxCoords
    
    def manhattan(self, state: 'State') -> 'int':
        boxCoords = self.findBoxCoords(state)
        totalDist = 0
        
        for boxCoord in boxCoords:
            minDist = float('inf')
            for goalCoord in Heuristic.goalCoords:
                dist = abs(goalCoord[0] - boxCoord[0]) + \
                abs(goalCoord[1] - boxCoord[1])
                if dist < minDist:
                    minDist = dist
            totalDist += minDist
        return totalDist
        
    
    def h(self, state: 'State') -> 'int':
        return self.manhattan(state);
    
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

