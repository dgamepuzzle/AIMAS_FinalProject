from abc import ABCMeta, abstractmethod
from collections import defaultdict
import sys

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
        
        for goal in initial_state.goals:
            self.goalDistances[goal.letter.lower()].append(
                Heuristic.gridBfs(initial_state.walls, goal.coords)
            )
            
        for goal in initial_state.goals:
            self.goalCoords[goal.letter.lower()].append(goal.coords)
            
    
    def h(self, state: 'State') -> 'int':
        
        '''
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
        
        #h= manDistFromBoxToGoal()    
        #h=manDistFromGoalToBox()
        '''
        h = self.real_dist(state)
        
        return h
    
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
    
    def real_dist(self, state: 'State') -> 'int':
        boxCoords = defaultdict(list)
        
        for box in state.boxes:
            boxCoords[box.letter.lower()].append(box.coords)
        
        totalDist = 0
        
        for goalType in self.goalDistances:
            box_cnt = len(boxCoords[goalType])
            goal_cnt = len(self.goalCoords[goalType])
            
            box_goal_d = []
            
            for i in range(goal_cnt):
                goal_x = self.goalCoords[goalType][i][0]
                goal_y = self.goalCoords[goalType][i][1]
                
                dists_from_this_goal = [float('inf')] * box_cnt
                
                for j in range(box_cnt):
                    box_x, box_y = boxCoords[goalType][j]
                    dists_from_this_goal[j] = self.goalDistances[goalType][i][box_x][box_y]
                
                box_goal_d.append(dists_from_this_goal)
             
            '''
            # Greedy estimate...    
            for goal_dists in box_goal_d:
                totalDist += min(goal_dists)                    
                
            print(box_goal_d, file=sys.stderr, flush=True)
            print(totalDist, file=sys.stderr, flush=True)
            #for i in range(goal_cnt):
            #    totalDist += 0.01 * self.goalDists[goalType][i][state.agent_row][state.agent_col]                
            '''
            
            hu = Hungarian()
            hu.solve(box_goal_d)
            test = hu.get_min_cost()
            totalDist += test
            print(test, file=sys.stderr, flush=True)
            
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

