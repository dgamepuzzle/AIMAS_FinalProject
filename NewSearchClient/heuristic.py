from abc import ABCMeta, abstractmethod
from collections import defaultdict
import sys
from state import State
import time
from hungarian import hungarian

class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State'):
        
        # Assign boxes to goals, and agents to those boxes
        self.doResetAssignments = False
        self.resetAssignments(initial_state)
    
    def h(self, state: 'State') -> 'int':
        
        # Return the lowest possible step-distance based on assignments
        return self.real_dist(state)
    
    def resetAssignments(self, state: 'State'):
        
        # TODO: HANDLE CASE WHEN THERE ARE LESS AGENTS THAN BOXES TO BE PUSHED
        # Allocates one distinct box to each of the goal and
        # allocates these boxes to distinct agents.
        
        # Reset the variables containing the assignments
        state.goalBoxAssignments = defaultdict(list)
        state.agentBoxAssignments = defaultdict(list)
        
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
            if state.parent is not None:
                if box.id in state.parent.boxIdsCompleted:
                    continue
            
            boxIdsToBeCompleted[box.letter.lower()].append(box.id)
            boxCoordsToBeCompleted[box.letter.lower()].append(box.coords)
        
        for idx, goal in enumerate(state.goals):
            # Do not assign boxes already in goal
            
            if state.parent is not None:
                if goal.id in state.parent.goalIdsCompleted:
                    continue
            
            goalIdsToBeCompleted[goal.letter.lower()].append(goal.id)
            goalCoordsToBeCompleted[goal.letter.lower()].append(goal.coords)
            goalDistancesToBeCompleted[goal.letter.lower()].append(State.goalDistances[idx])
        
        # DO IT FOR EACH GOAL/BOX LETTER
        print('goalIdsToBeCompleted = '+str(goalIdsToBeCompleted), file=sys.stderr, flush=True)
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
            print('distMatrix = '+str(distMatrix), file=sys.stderr, flush=True)
            time.sleep(5)
            
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
            state.goalBoxAssignments[letter] = idAssignments
            
        #print(state.goalBoxAssignments, file=sys.stderr, flush=True)
            
        
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
        
        for letter in state.goalBoxAssignments:
            boxIdsWithGoals[letter] = [assignment[1] for assignment in state.goalBoxAssignments[letter]]

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
            state.agentBoxAssignments[color] = idAssignments
        
        # Remove the GOAL_BOX assignments that have no associated agent.
        for color in state.goalBoxAssignments:            
            state.goalBoxAssignments[color] = [assignment for assignment in state.goalBoxAssignments[color] if assignment[1] in boxIdsWithAgents]
        
        '''
        print('GOAL-BOX', file=sys.stderr, flush=True)
        print(state.goalBoxAssignments, file=sys.stderr, flush=True)
        print('AGENT-BOX', file=sys.stderr, flush=True)
        print(state.agentBoxAssignments, file=sys.stderr, flush=True)
        '''
 
    def distance_already_completed_goals(self, state: 'State')-> 'int':
        
        # A weight denoting the punishment given for pushing already completed
        # boxes away from their goals
        goalBoxCompletedMultiplier = 5
        
        dist =0
        # Get the list of previously completed boxes and goals
        boxIdsCompleted = list(state.boxIdsCompleted)
        goalIdsCompleted = list(state.goalIdsCompleted)

        # Iterate through the previously completed box and goal IDs
        for i in range(len(state.boxIdsCompleted)):
            boxId = boxIdsCompleted[i]
            goalId = goalIdsCompleted[i]
            # Find the corresponding coordinates of the given boxID
            boxCoordsCurrent = next(box for box in state.boxes if box.id == boxId).coords
            
            # Find the index belonging to the goal with the given goalID in
            # the flat goalDistances array
            goalIdx = next(j for j in range(len(state.goals)) if goalId == state.goals[j].id)
            
            # Given the above data, calculate the distance of the given
            # goal box pair
            goalBoxDist = State.goalDistances[goalIdx][boxCoordsCurrent[0]][boxCoordsCurrent[1]]
            dist += (goalBoxDist * goalBoxCompletedMultiplier)
        
        state.debugDistances[0] = dist
        return dist

    def distance_between_boxes_and_goals(self, state: 'State') -> 'int':

        # A weight denoting the importance of box-goal distances over agent-box
        # distances,
        goalBoxMultiplier = 2        
        
        dist=0
        
        # For each letter...
        for letter in state.goalBoxAssignments:
            goalBoxAss = state.goalBoxAssignments[letter]

            # Get every GOAL-BOX assignment
            for i in range(len(goalBoxAss)):
                
                # Get the coordinates of the box in the assignment, and
                # look up its distance from its corresponding goal
                boxCoordsCurrent = next(box for box in state.boxes if box.id == goalBoxAss[i][1]).coords
                goalId = goalBoxAss[i][0]
                goalIdx = next(j for j in range(len(state.goals)) if goalId == state.goals[j].id)
                goalBoxDist = State.goalDistances[goalIdx][boxCoordsCurrent[0]][boxCoordsCurrent[1]]
                
                #print('D( box%d, goal%d) = %d' % (goalBoxAss[i][1], goalBoxAss[i][0], goalBoxDist), file=sys.stderr, flush=True)
                
                # If box is in goal, do not assign it again at later stages
                if goalBoxDist < 1:
                    #print('box #%d pushed to goal #%d' % (goalBoxAss[i][1], goalBoxAss[i][0]), file=sys.stderr, flush=True)
                    state.boxIdsCompleted.add(goalBoxAss[i][1])
                    state.goalIdsCompleted.add(goalBoxAss[i][0])
                    #if not (len(self.boxIdsCompleted) % len(state.agents)):
                        #print(goalBoxDist, file=sys.stderr, flush=True);
                    self.doResetAssignments = True
                    #print(state, file=sys.stderr, flush=True)
                
                # Add it to the total distance
                dist += goalBoxDist * goalBoxMultiplier  
                
        state.debugDistances[1] = dist        
        return dist
    
    def distance_between_agents_and_boxes(self, state: 'State') -> 'int':
        
        dist=0
        
        # For each color...
        for color in state.agentBoxAssignments:
            
            # For each AGENT-BOX assignment...
            for assignment in state.agentBoxAssignments[color]:
                # Look up the corresponding coordinates for the agent ID in the
                # AGENT-BOX assignment
                agentCoordsCurrent = next(agent for agent in state.agents if agent.number == assignment[0]).coords
                
                # Look up the corresponding coordinates for the box ID in the
                # AGENT-BOX assignment
                boxCoordsCurrent = next(box for box in state.boxes if box.id == assignment[1]).coords
                
                # Calculate distance between agent and box, and add it to the
                # total distance
                dist_between_agent_box = state.mainGraph.get_distance(agentCoordsCurrent, boxCoordsCurrent)
                dist += (dist_between_agent_box) # / len(self.agentBoxAssignments[color]))
        
        state.debugDistances[2] = dist
        return dist
               
    def punish_unassigned_agents(self,state: 'State') -> 'int':
        
        # A weight denoting the punishment of the movement of unassigned agents
        unassignedAgentMovementMultiplier = 2
        
        dist =0
        # If there are unassigned agents, punish them for moving
        # If there is previous state
        if state.parent is not None:                
            #print("agentBoxAssignments " + str(self.agentBoxAssignments), file=sys.stderr, flush=True)
            agentBoxAssignmentsValues = state.agentBoxAssignments.values()
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
                    dist += (diffX + diffY) * unassignedAgentMovementMultiplier
        
        state.debugDistances[3] = dist        
        return dist

    def punish_unassigned_boxes(self,state: 'State') -> 'int':
        
        # A weight denoting the punishment of having unassigned and non-
        # completed boxes in the level
        loneBoxMultiplier = 1000
        
        # Punish boxes that are unassigned and are not yet in their goals
        boxIdsToBePunished = set([box.id for box in state.boxes])
        
        # Exclude boxes that have a corresponding agent
        for color in state.agentBoxAssignments:
            for assignment in state.agentBoxAssignments[color]:
                boxIdsToBePunished.remove(assignment[1])
        
        # Exclude boxes already in goal
        for boxId in state.boxIdsCompleted:
            if boxId in boxIdsToBePunished:
                boxIdsToBePunished.remove(boxId)
          
            
        dist = (len(boxIdsToBePunished) * loneBoxMultiplier)
        state.debugDistances[4] = dist
        return dist
               
    def real_dist(self, state: 'State') -> 'int':
        
        # A boolean denoting whether to reassign boxes at the end of the
        # heuristic calculation, or not
        self.doResetAssignments = False
               
        
        # The total distance
        totalDist = 0
        
        #print(state.goalDistances, file=sys.stderr, flush=True)
        
        totalDist += self.distance_already_completed_goals(state)
        
        totalDist += self.distance_between_boxes_and_goals(state)
        
        totalDist += self.distance_between_agents_and_boxes(state)
        
        totalDist += self.punish_unassigned_agents(state)
        
        totalDist += self.punish_unassigned_boxes(state)
            
        

        
        
                
        
                
        
        # Reset goal-box box-agent assignments, if needed
        if self.doResetAssignments:
            self.resetAssignments(state)
         
        '''
        print("totalDist: "+ str(totalDist), file=sys.stderr, flush=True)
        print("GB", file=sys.stderr, flush=True)
        print(state.goalBoxAssignments, file=sys.stderr, flush=True)
        print("AB", file=sys.stderr, flush=True)
        print(state.agentBoxAssignments, file=sys.stderr, flush=True)
        print(state, file=sys.stderr, flush=True)
        '''
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

