from abc import ABCMeta, abstractmethod
from collections import defaultdict
import sys
from state import State
import time
from hungarian import hungarian

class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State'):
        # Here's a chance to pre-process the static parts of the level.
        
        # Stores arrays of size (MAX_ROW, MAX_COL), denoting minimum push
        # distances from each goal.
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
        
        # Stores pairs of goal and box ids that have been assigned
        # grouped by COLOR instead of letter
        self.agentBoxAssignments = defaultdict(list)
        
        # Keeps track of boxes that have been pushed to their goals
        self.boxIdsCompleted = set()
        
        # Keeps track of goals that have been completed
        self.goalIdsCompleted = set()
        
        # Populate the above containers
        for goal in initial_state.goals:
            #distsFromGoal = Heuristic.gridBfs(initial_state.walls, goal.coords)
            distsFromGoal = initial_state.mainGraph.gridForGoal(initial_state.walls, goal.coords)
            self.goalDistances.append(distsFromGoal)
            self.goalDistancesByLetter[goal.letter.lower()].append(distsFromGoal)
            self.goalCoords[goal.letter.lower()].append(goal.coords)
            self.goalIds[goal.letter.lower()].append(goal.id)
        
        # Assign boxes to goals, and agents to those boxes
        self.resetAssignments(initial_state)
    
    def h(self, state: 'State') -> 'int':
        
        # Return the lowest possible step-distance based on assignments
        return self.real_dist(state)
    
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
        boxIdsToBeCompleted = defaultdict(list)
        boxCoordsToBeCompleted = defaultdict(list)   
         
        goalIdsToBeCompleted = defaultdict(list)
        goalCoordsToBeCompleted = defaultdict(list)
        goalDistancesToBeCompleted = defaultdict(list)
        
        for box in state.boxes:
            # Do not assign boxes already in goal
            if box.id in self.boxIdsCompleted:
                continue
            
            boxIdsToBeCompleted[box.letter.lower()].append(box.id)
            boxCoordsToBeCompleted[box.letter.lower()].append(box.coords)
        
        for idx, goal in enumerate(state.goals):
            # Do not assign boxes already in goal
            if goal.id in self.goalIdsCompleted:
                continue
            
            goalIdsToBeCompleted[goal.letter.lower()].append(goal.id)
            goalCoordsToBeCompleted[goal.letter.lower()].append(goal.coords)
            goalDistancesToBeCompleted[goal.letter.lower()].append(self.goalDistances[idx])
            
        
        # DO IT FOR EACH GOAL/BOX LETTER
        for letter in goalIdsToBeCompleted:
            
            # Create shorthands for readable code (they're just references,
            # without extra memory consumption)
            
            boxCoordsLetter = boxCoordsToBeCompleted[letter]
            goalDistsLetter = goalDistancesToBeCompleted[letter]
            
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
            idAssignments = [(goalIdsToBeCompleted[letter][assignment[0]], boxIdsToBeCompleted[letter][assignment[1]]) for assignment in assignments]
            
            # Write the result as the assignment of boxes and goals of letter "letter".
            self.goalBoxAssignments[letter] = idAssignments
            
        
        # AGENT - BOX ASSIGNMENT SECTION
        
        # Create containers for box and agent data, in a similar fashion as in
        # the above step, this time grouped by COLOR.
        
        # For the AGENT-BOX assignments, use boxes only that have an associated
        # goal.
        boxIdsWithGoals = defaultdict(list)
        boxCoordsWithGoals = defaultdict(list)
        
        agentIds = defaultdict(list)
        agentCoords = defaultdict(list)

        # Work with boxes only if they have a corresponding goal
        # otherwise there's no point in pushing them with agents
        
        for letter in self.goalBoxAssignments:
            boxIdsWithGoals[letter] = [assignment[1] for assignment in self.goalBoxAssignments[letter]]
        
        # If a box is not assigned to a goal, discard it
        # Group box data by color
        for box in state.boxes:
            if box.id not in boxIdsWithGoals[box.letter.lower()]:
                continue
            boxIdsWithGoals[box.color].append(box.id)
            boxCoordsWithGoals[box.color].append(box.coords)
        
        # Group agent data by color
        for agent in state.agents:
            agentIds[agent.color].append(agent.number)
            agentCoords[agent.color].append(agent.coords)
            
        boxIdsWithAgents = []
    
        # DO IT FOR EACH AGENT/BOX COLOR ...
        for color in agentCoords:
            # Create shorthands for readable code (they're just references,
            # without extra memory consumption)
            boxCoordsColor = boxCoordsWithGoals[color]
            agentCoordsColor = agentCoords[color]
            
            box_cnt = len(boxCoordsColor)
            
            # Create distance matrix for Hungarian algorithm
            #         box1 box2 box3
            # agent1    1    5    3
            # agent2    8    7    5
            # agent3    2    10   7
            distMatrix = [state.mainGraph.get_distance_one_to_many(agentCoord, boxCoordsColor) for agentCoord in agentCoordsColor]
            
            # Get assignments in a 
            # [(agentX, boxY), (agentY, boxZ), (agentZ, boxX)] format
            # where agentX..Z and box..Z refers to their corresponding row/col
            # numbers in the DISTANCE MATRIX
            assignments = hungarian(distMatrix)
            
            # Get the real IDs of the assigned agents and boxes
            idAssignments = [(agentIds[color][assignment[0]], boxIdsWithGoals[color][assignment[1]]) for assignment in assignments]
            
            # Collect the IDs of boxes that have an associated agent
            boxIdsWithAgents += [assignment[1] for assignment in idAssignments]
            
            # Write the result as the assignment of agents and boxes of this color
            self.agentBoxAssignments[color] = idAssignments
        
        # Remove the GOAL_BOX assignments that have no associated agent.
        for color in self.goalBoxAssignments:            
            self.goalBoxAssignments[color] = [assignment for assignment in self.goalBoxAssignments[color] if assignment[1] in boxIdsWithAgents]
        
        print('GOAL-BOX', file=sys.stderr, flush=True)
        print(self.goalBoxAssignments, file=sys.stderr, flush=True)
        print('AGENT-BOX', file=sys.stderr, flush=True)
        print(self.agentBoxAssignments, file=sys.stderr, flush=True)
        

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
        
        # A weight denoting the punishment of the movement of unassigne dagents
        unassignedAgentMovementMultiplier = 2
        
        # A weight denoting the punishment of having unassigned and non-
        # completed boxes in the level
        loneBoxMultiplier = 1000
        
        # The total distance
        totalDist = 0
        
        # Get the list of previously completed boxes and goals
        boxIdsCompleted = list(self.boxIdsCompleted)
        goalIdsCompleted = list(self.goalIdsCompleted)

        # Iterate through the previously completed box and goal IDs
        for i in range(len(self.boxIdsCompleted)):
            boxId = boxIdsCompleted[i]
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
                    self.boxIdsCompleted.add(goalBoxAss[i][1])
                    self.goalIdsCompleted.add(goalBoxAss[i][0])
                    #if not (len(self.boxIdsCompleted) % len(state.agents)):
                        #print(goalBoxDist, file=sys.stderr, flush=True);
                    doResetAssignments = True
                    print(state, file=sys.stderr, flush=True)
                
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
                dist = state.mainGraph.get_distance(agentCoordsCurrent, boxCoordsCurrent)
                totalDist += (dist) # / len(self.agentBoxAssignments[color]))



        # If there are unassigned agents, punish them for moving
        # If there is previous state
        if state.parent is not None:                
            #print("agentBoxAssignments " + str(self.agentBoxAssignments), file=sys.stderr, flush=True)
            agentBoxAssignmentsValues = self.agentBoxAssignments.values()
            assignedAgentIds =set()
            for color in agentBoxAssignmentsValues:
                for agentid in color:
                    assignedAgentIds.add( agentid[0])
            
            #print("assigned agents+ " + str(assignedAgentIds), file=sys.stderr, flush=True)
            
            for i in range(len(state.agents)):
                currentAgent = state.agents[i]
                
                pastAgent = state.parent.agents[i]
                
                if currentAgent.number not in assignedAgentIds:
                    diffY = abs(currentAgent.coords[0] - pastAgent.coords[0])
                    diffX = abs(currentAgent.coords[1] - pastAgent.coords[1])       
                    #print("punishment: "+ "agent "+ str(currentAgent.number)+" is punished by: "+str((diffX + diffY) * unassignedAgentMovementMultiplier), file=sys.stderr, flush=True)
                    totalDist += (diffX + diffY) * unassignedAgentMovementMultiplier
                
                
        # Punish boxes that are unassigned and are not yet in their goals
        boxIdsToBePunished = set([box.id for box in state.boxes])
        
        # Exclude boxes that have a corresponding agent
        for color in self.agentBoxAssignments:
            for assignment in self.agentBoxAssignments[color]:
                boxIdsToBePunished.remove(assignment[1])
        
        # Exclude boxes already in goal
        for boxId in self.boxIdsCompleted:
            try:
                boxIdsToBePunished.remove(boxId)
            except:
                # Apparently, there are cases when a box has been just pushed
                # to its goal, but it's still assigned to its agent
                # If this happens, we try to remove the box two times from the
                # set, which raises an error
                print('Erm, error handling...', file=sys.stderr, flush=True)
            
        totalDist += (len(boxIdsToBePunished) * loneBoxMultiplier)
                
        
        # Reset goal-box box-agent assignments, if needed
        if doResetAssignments:
            self.resetAssignments(state)
         
        
        #print("totalDist: "+ str(totalDist), file=sys.stderr, flush=True)
        #print(state, file=sys.stderr, flush=True)
        #time.sleep(0.5)    
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

