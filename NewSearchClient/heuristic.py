from abc import ABCMeta, abstractmethod

from state import State


class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State'):
        # Here's a chance to pre-process the static parts of the level.
        pass
    
    def h(self, state: 'State') -> 'int':
        
        def manDistFromBoxToGoal():
            h=0
            distanceFromAgentToNearestBox = float('inf');
            for box in state.boxes:
                # Find nearest goal
                bestManDist = float('inf')
                for goal in state.goals:
                    if box.letter == goal.letter:
                        newManDist = abs(box.coords[0]-goal.coords[0]) + abs(box.coords[1]-goal.coords[1])
                        bestManDist = min(bestManDist,newManDist)
                h+=bestManDist
                #TODO: Review this, because probably we can get a better implementation
                for agent in state.agents:
                    newDistanceFromAgentToNearestBox = abs(box.coords[0]-agent.coords[0]) + abs(box.coords[1]-agent.coords[1])
                    distanceFromAgentToNearestBox = min(newDistanceFromAgentToNearestBox,distanceFromAgentToNearestBox)
            return h+distanceFromAgentToNearestBox
        
        # Manhattan distance of all boxes to nearest goal, taking into account only the closer agent for each box
        h= manDistFromBoxToGoal()    
        return h
    
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


'''
#-----------------------------------------
def manDistFromGoalToBox():
    h=0
    for goal in state.goals:
        bestManDist = float('inf')
        for box in state.boxes:
            if box.letter == goal.letter:
                newManDist = abs(box.coords[0]-goal.coords[0]) + abs(box.coords[1]-goal.coords[1])
                bestManDist = min(bestManDist,newManDist)
        h+=bestManDist
    return h
#-----------------------------------------
'''

