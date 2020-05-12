from abc import ABCMeta, abstractmethod
from collections import defaultdict
import sys
from state import State

from hungarian import hungarian

class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State'):
        # Here's a chance to pre-process the static parts of the level.
        
        # Stores arrays of size (MAX_ROW, MAX_COL), denoting minimum push
        # distances from each goal (might use graphs instead).
        # The data is grouped by letters in the following way:
        # goalDistances - "A" : [[distances from goal 1] , [distances from goal 2]]
        #               - "B" : [[distances from goal 3]]
        #               - "C" : [[distances from goal 4]] etc...
        self.goalDistancesByLetter = defaultdict(list)
        
        # Store the references of the above goal distance arrays in a
        # flat array for easier searchhing
        self.goalDistances = []
        
        # Stores corresponding goal coordinates.
        # goalCoords - "A" : [(coords of goal 1), (coords of goal2)]
        #            - "B" : [(coords of goal 3)]
        #            - "C" : [(coords of goal 4)] etc...
        self.goalCoords = defaultdict(list)
        
        # Stores corresponding goal Ids in the same fashion as the
        # above defaultdicts.
        self.goalIds = defaultdict(list)
        
        # Stores pairs of goal and box ids that have been assigned
        # in the same fashion as the above defaultdicts.
        self.goalBoxAssignments = defaultdict(list)
        
        self.goalBoxAssignmentsAllTime = defaultdict(list)
        
        # Stores pairs of goal and box ids that have been assigned
        # grouped by COLOR instead of letter
        self.agentBoxAssignments = defaultdict(list)
        
        # Keeps track of boxes that have been pushed to their goals
        # UNUESED FOR NOW - FEATURE TO BE IMPLEMENTED
        self.boxIdsInGoal = set()
        
        # Keeps track of goals that have been completed
        self.goalIdsCompleted = set()
        
        # Populate the above containers
        for goal in initial_state.goals:
            distsFromGoal = Heuristic.gridBfs(initial_state.walls, goal.coords)
            self.goalDistances.append(distsFromGoal)
            self.goalDistancesByLetter[goal.letter.lower()].append(distsFromGoal)
            
            self.goalCoords[goal.letter.lower()].append(goal.coords)
            self.goalIds[goal.letter.lower()].append(goal.id)
        
        # Assign boxes to goals, and agents to those boxes
        self.resetAssignments(initial_state)
    
    def h(self, state: 'State') -> 'int':
        
        # Return the lowest possible step-distance based on assignments
        return self.real_dist(state)
    
    @staticmethod
    def gridBfs(walls, startCoords):
        
        # TODO: USE THE GRAPH REPRESENTATION OF THE LEVEL INSTEAD
        # A simple BFS that traverses the level defined by the 2d walls array
        # and outputs a 2d array of the same size, filled with distances from
        # a given point. Useful for precomputing distances from the goals
        #
        #   Input wall array                  Resulting array
        #
        #   wall     wall    start            0  0  0 (start)
        #   notwall  notwall notwall          3  2  1
        #   notwall  wall    notwall  ---->   4  0  2
        #   notwall  wall    notwall          5  0  3
        #
        
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

        # TODO: USE THE GRAPH REPRESENTATION OF THE LEVEL INSTEAD
        # Calculate distance between start_coords and end_coords with
        # a simple BFS. 
        
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
        
        # TODO: USE THE GRAPH REPRESENTATION OF THE LEVEL INSTEAD
        # Calculates distances between the_coords of one start point and 
        # many end points in a single graph traversal. Much more efficient than
        # running BFS for each of the end points.
        #
        # Returns an array representing the distances from the start point to
        # each of the end points, in a corresponding order as in the 
        # end_coords_array.
        
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
                
                if cand_check not in visited and candidate not in frontier:
                    frontier.append(candidate)
                
            visited.add((current[0], current[1]))
        
        return distances
    
    def resetAssignments(self, state: 'State'):
        
        # TO DO: HANDLE CASE WHEN THERE ARE LESS AGENTS THAN BOXES TO BE PUSHED
        # Allocates one distinct box to each of the goal and
        # allocates these boxes to distinct agents.
        
        # Reset the variables containing the assignments
        self.goalBoxAssignments = defaultdict(list)
        self.agentBoxAssignments = defaultdict(list)
        
        # BOX - GOAL ASSIGNMENT SECTION
        
        # Create containers for box IDs and box coords, in a similar way as we
        # did with goals in the __init__ method
        boxIds = defaultdict(list)
        boxCoords= defaultdict(list)
        
        for box in state.boxes:
            # Do not assign boxes already in goal
            if box.id in self.boxIdsInGoal:
                continue
            
            boxIds[box.letter.lower()].append(box.id)
            boxCoords[box.letter.lower()].append(box.coords)
            
        goalIds = defaultdict(list)
        goalCoords = defaultdict(list)
        goalDistances = defaultdict(list)
        
        for idx, goal in enumerate(state.goals):
            # Do not assign boxes already in goal
            if goal.id in self.goalIdsCompleted:
                continue
            
            goalIds[goal.letter.lower()].append(goal.id)
            goalCoords[goal.letter.lower()].append(goal.coords)
            goalDistances[goal.letter.lower()].append(self.goalDistances[idx])
            
        
        # DO IT FOR EACH GOAL/BOX LETTER
        for letter in goalDistances:
            
            # Create shorthands for readable code (they're just references,
            # without extra memory consumption)
            
            boxCoordsLetter = boxCoords[letter]
            goalDistsLetter = goalDistances[letter]
            
            box_cnt = len(boxCoordsLetter)
            goal_cnt = len(goalDistsLetter)
            
            # Create distance matrix containing distances
            # between boxes and goals in the following way:
            #
            #         box1 box2 box3
            # goal1    1    5    3
            # goal2    8    7    5
            # goal3    2    10   7
            
            distMatrix = [[goalDistsLetter[i][boxCoordsLetter[j][0]][boxCoordsLetter[j][1]] for j in range(box_cnt)] for i in range(goal_cnt)]
            
            # Assign a box to each of the goals with the Hungarian algorithm
            #
            # Get assignments in a 
            # [(goalX, boxY), (goalY, boxZ), (goalZ, boxX)] format
            # where goalX..Z and box..Z refers to their corresponding row/col
            # numbers in the DISTANCE MATRIX
            assignments = hungarian(distMatrix)
            
            # Get the real IDs of the assigned goals and boxes
            idAssignments = [(goalIds[letter][assignment[0]], boxIds[letter][assignment[1]]) for assignment in assignments]
            
            # Write the result as the assignment of boxes and goals of letter "letter".
            self.goalBoxAssignments[letter] = idAssignments
            self.goalBoxAssignmentsAllTime[letter] += idAssignments
            
        
        # AGENT - BOX ASSIGNMENT SECTION
        
        # Create containers for box and agent data, in a similar fashion as in
        # the above step, this time grouped by COLOR.
        boxIds = defaultdict(list)
        boxCoords= defaultdict(list)
        agentIds = defaultdict(list)
        agentCoords = defaultdict(list)

        # Work with boxes only if they have a corresponding goal
        # otherwise there's no point in pushing them with agents
        
        # Create a container of assigned box ids, for easier lookup
        assignedBoxIds = defaultdict(list)
        for letter in self.goalBoxAssignments:
            assignedBoxIds[letter] = [assignment[1] for assignment in self.goalBoxAssignments[letter]]
        
        # If a box is not assigned to a goal, discard it
        # Group box data by color
        for box in state.boxes:
            if box.id not in assignedBoxIds[box.letter.lower()]:
                continue
            boxIds[box.color].append(box.id)
            boxCoords[box.color].append(box.coords)
        
        # Group agent data by color
        for agent in state.agents:
            agentIds[agent.color].append(agent.number)
            agentCoords[agent.color].append(agent.coords)
            
        boxIdsWithAgents = []
    
        # DO IT FOR EACH AGENT/BOX COLOR ...
        for color in agentCoords:
            # Create shorthands for readable code (they're just references,
            # without extra memory consumption)
            boxCoordsColor = boxCoords[color]
            agentCoordsColor = agentCoords[color]
            
            box_cnt = len(boxCoordsColor)
            
            # Create distance matrix for Hungarian algorithm
            #         box1 box2 box3
            # agent1    1    5    3
            # agent2    8    7    5
            # agent3    2    10   7
            distMatrix = [Heuristic.get_distance_one_to_many(State.walls, agentCoord, boxCoordsColor) for agentCoord in agentCoordsColor]
            
            # Get assignments in a 
            # [(agentX, boxY), (agentY, boxZ), (agentZ, boxX)] format
            # where agentX..Z and box..Z refers to their corresponding row/col
            # numbers in the DISTANCE MATRIX
            assignments = hungarian(distMatrix)
            
            # Get the real IDs of the assigned agents and boxes
            idAssignments = [(agentIds[color][assignment[0]], boxIds[color][assignment[1]]) for assignment in assignments]
            
            # DEBUG
            boxIdsWithAgents += [assignment[1] for assignment in idAssignments]
            
            # Write the result as the assignment of agents and boxes of this color
            self.agentBoxAssignments[color] = idAssignments
        
        for color in self.goalBoxAssignments:            
            self.goalBoxAssignments[color] = [assignment for assignment in self.goalBoxAssignments[color] if assignment[1] in boxIdsWithAgents]
        

    def real_dist(self, state: 'State') -> 'int':
        
        # TO DO: Check if any new box has been pushed to the goal, then
        # reallocate.
        # self.resetAssignments(state)
        
        # A boolean denoting whether to reassign boxes at the end of the
        # heuristic calculation, or not
        doResetAssignments = False
        
        # A weight denoting the importance of box-goal distances over agent-box
        # distances,
        goalBoxMultiplier = 2
        
        # A weight denoting the punishment given for pushing already completed
        # boxes away from their goals
        goalBoxCompletedMultiplier = 5
        
        # The total distance
        totalDist = 0
        
        # Get the list of previously completed boxes and goals
        boxIdsInGoal = list(self.boxIdsInGoal)
        goalIdsCompleted = list(self.goalIdsCompleted)

        # Iterate through the previously completed box and goal IDs
        for i in range(len(self.boxIdsInGoal)):
            boxId = boxIdsInGoal[i]
            goalId = goalIdsCompleted[i]
            # Find the corresponding coordinates of the given boxID
            boxCoordsCurrent = next(box for box in state.boxes if box.id == boxId).coords
            
            # Find the index belonging to the goal with the given goalID in
            # tha flat goalDistances array
            goalIdx = next(j for j in range(len(state.goals)) if goalId == state.goals[j].id)
            
            # Given the above data, calculate the distance of the given
            # goal box pair
            goalBoxDist = self.goalDistances[goalIdx][boxCoordsCurrent[0]][boxCoordsCurrent[1]]
            totalDist += (goalBoxDist * goalBoxCompletedMultiplier)
        
        # For each letter...
        for letter in self.goalBoxAssignments:
            goalBoxAss = self.goalBoxAssignments[letter]

            # Get every GOAL-BOX assignment
            for i in range(len(goalBoxAss)):
                
                # Get the coordinates of thttps://mail.google.com/he box in the assignment, and
                # look up its distance from its corresponding goal
                boxCoordsCurrent = next(box for box in state.boxes if box.id == goalBoxAss[i][1]).coords
                goalId = goalBoxAss[i][0]
                goalIdx = next(j for j in range(len(state.goals)) if goalId == state.goals[j].id)
                goalBoxDist = self.goalDistances[goalIdx][boxCoordsCurrent[0]][boxCoordsCurrent[1]]
                
                # If box is in goal, do not assign it again at later stages
                if goalBoxDist < 1:
                    self.boxIdsInGoal.add(goalBoxAss[i][1])
                    self.goalIdsCompleted.add(goalBoxAss[i][0])
                    if not (len(self.boxIdsInGoal) % len(state.agents)):
                        doResetAssignments = True
                
                # Add it to the total distance
                totalDist += goalBoxDist * goalBoxMultiplier
            
        # For each color...
        for color in self.agentBoxAssignments:
            
            # For each AGENT-BOX assignment...
            for assignment in self.agentBoxAssignments[color]:
                # Look up the corresponding coordinates for the agent ID in the
                # AGENT-BOX assignment
                agentCoordsCurrent = next(agent for agent in state.agents if agent.number == assignment[0]).coords
                
                # Look up the corresponding coordinates for the box ID in the
                # AGENT-BOX assignment
                boxCoordsCurrent = next(box for box in state.boxes if box.id == assignment[1]).coords
                
                # Calculate distance between agent and box, and add it to the
                # total distance
                dist = Heuristic.get_distance(State.walls, agentCoordsCurrent, boxCoordsCurrent)
                totalDist += dist
        
        # Reset goal-box box-agent assignments, if needed
        if doResetAssignments:
            self.resetAssignments(state)
            
        #print(totalDist, file=sys.stderr, flush=True)
        print(state, file=sys.stderr, flush=True)
        
        # Done.                         ...Done?
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

