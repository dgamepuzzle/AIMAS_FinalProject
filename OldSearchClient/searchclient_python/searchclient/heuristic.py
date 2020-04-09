from abc import ABCMeta, abstractmethod


class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State'):
        # Here's a chance to pre-process the static parts of the level.
        pass
    
    def h(self, state: 'State') -> 'int':
        
        def manDistFromBoxToGoal():
            h=0
            distanceFromAgentToNearestBox= float('inf');
            for rowBox in range(state.MAX_ROW):
                for colBox in range(state.MAX_COL):
                    box = state.boxes[rowBox][colBox]
                    if box != None :
                        #find nearest goal
                        bestManDist = float('inf')
                        for rowGoal in range(state.MAX_ROW):
                            for colGoal in range(state.MAX_COL):
                                goal = state.goals[rowGoal][colGoal]
                                if goal!=None and box.lower() == goal :
                                    newManDist = abs(rowBox-rowGoal) + abs(colBox-colGoal)
                                    bestManDist = min(bestManDist,newManDist)
                         
                        h+=bestManDist
                        #see if this is the nearest box to player and add heuristic value.           
                        newDistanceFromAgentToNearestBox= abs(rowBox-state.agent_row) + abs(colBox-state.agent_col)
                        distanceFromAgentToNearestBox=min(newDistanceFromAgentToNearestBox,distanceFromAgentToNearestBox)
            return h+distanceFromAgentToNearestBox
        #-----------------------------------------
        def manDistFromGoalToBox():
            h=0
            for rowGoal in range(state.MAX_ROW):
                for colGoal in range(state.MAX_COL):
                    goal = state.goals[rowGoal][colGoal]
                    if goal != None :
                        bestManDist = float('inf')
                        for rowBox in range(state.MAX_ROW):
                            for colBox in range(state.MAX_COL):
                                box = state.boxes[rowBox][colBox]
                                if box!=None and box.lower() == goal :
                                    newManDist = abs(rowBox-rowGoal) + abs(colBox-colGoal)
                                    bestManDist = min(bestManDist,newManDist)
                                    
                        h+=bestManDist
            return h
        #-----------------------------------------
        
        #Manhatten distance of all boxes to nearest goal
        
        h= manDistFromBoxToGoal()    
        #h=manDistFromGoalToBox()            
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

