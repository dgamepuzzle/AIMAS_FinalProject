# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:14:20 2020

@author: AIStars group
"""

import copy as cp
import random
import sys
from itertools import product
import networkx as nx

#from graph import Graph
from jointaction import Action, ActionType, ALL_ACTIONS
from level_elements import Agent, Box, Goal
from collections import defaultdict

class State:
    _RNG = random.Random(1)
    MAX_ROW = None
    MAX_COL = None
    goals = []
    colors = []
    walls = []
    goalDistancesByLetter = defaultdict(list)
    goalDistances = []                              # Store the references of the above goal distance arrays in a
                                                    # flat array for easier searchhing
    
    goalCoords = defaultdict(list)                  # Stores corresponding goal coordinates.
                                                    # goalCoords - "A" : [(coords of goal 1), (coords of goal2)]
                                                    #            - "B" : [(coords of goal 3)]
                                                    #            - "C" : [(coords of goal 4)] etc...
    
    goalIds = defaultdict(list)                     # Stores corresponding goal Ids in the same fashion as the
                                                    # above defaultdicts.
    
    #mainGraph = Graph()
    mainGraph = nx.Graph()
    mainGraphDistances = None
    
    def __init__(self, copy: 'State' = None, level_lines = "", goal_state = False):
        self._hash = None
        
        self.goalBoxAssignments = defaultdict(list)         # Stores pairs of goal and box ids that have been assigned
                                                            # in the same fashion as the above defaultdicts.
                                                            
        self.agentBoxAssignments = defaultdict(list)        # Stores pairs of goal and box ids that have been assigned
                                                            # grouped by COLOR instead of letter
                                                            
        self.boxIdsCompleted = set()                        # Keeps track of boxes that have been pushed to their goals
        self.goalIdsCompleted = set()                       # Keeps track of goals that have been completed
        
        if copy == None:
            self.agents = []
            self.boxes = []
            self.parent = None
            self.jointaction = []
            self.g = 0
            self.h = -1
            State.walls = [[False for _ in range(State.MAX_COL)] for _ in range(State.MAX_ROW)]
            
            self.debugDistances=[0]*5
            
            # Parse full level (build static graph and save static/non-static entities).
            #try:
            for row, line in enumerate(level_lines):
                for col, char in enumerate(line):
                    
                    if char != '+':
                        
                        # First, as it's not a wall, add node to the static graph and create its relevant edges.
                        #cur_node = State.mainGraph.create_or_get_node(row, col)
                        cur_node_id = self.coords2id(row, col)
                        if not State.mainGraph.has_node(cur_node_id): State.mainGraph.add_node(cur_node_id)
                        for coord in [(-1,0),(1,0),(0,1),(0,-1)]:
                            k = coord[0]
                            l = coord[1]
                            h = min(State.MAX_ROW-1, max(0, row+k))
                            u = min(State.MAX_COL-1, max(0, col+l))
                            if level_lines[h][u]!='+':
                                #dest_node = State.mainGraph.create_or_get_node(h, u)
                                #cur_node.add_edge(dest_node)
                                dest_node_id = self.coords2id(h, u)
                                if not State.mainGraph.has_node(dest_node_id): State.mainGraph.add_node(dest_node_id)
                                if not State.mainGraph.has_edge(cur_node_id,dest_node_id): State.mainGraph.add_edge(cur_node_id,dest_node_id)
                        
                        # Parse agents.
                        if char in "0123456789":
                            color = State.colors[char]
                            self.agents.append(Agent(char,color,(row, col)))
                            #print("Saving agent at "+ str((row,col)), file=sys.stderr, flush=True)
                            
                        # Parse boxes.
                        elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            if goal_state: #Parse goals
                                State.goals.append(Goal(char,(row, col)))
                                #print("adding goal at "+ str((row,col)), file=sys.stderr, flush=True)
                            else: #parse boxes
                                color = State.colors[char]
                                self.boxes.append(Box(char, color, (row, col)))
                            
                        
                        # Parse spaces.
                        elif (char ==' '):
                            # Do nothing after creating the node.
                            pass
                        
                        else:
                            print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                            sys.exit(1)
                    
                    else:
                        # Save wall position.
                        State.walls[row][col] = True
            
            # Convert unmovable boxes to walls
            box_colors = set([box.color for box in self.boxes])
            agent_colors = set([agent.color for agent in self.agents])
            for color in box_colors:
                if color not in agent_colors:
                    box_coords = [box.coords for box in self.boxes if box.color == color]
                    self.boxes = [box for box in self.boxes if box.coords in box_coords]
                    for coords in box_coords:
                        #State.mainGraph.remove_node(coords)
                        State.mainGraph.remove_node(self.coords2id(coords[0],coords[1]))
                        State.walls[coords[0]][coords[1]] = True
                    State.colors = {key:val for key, val in State.colors.items() if val != color}
            
            # Order the agents by their number
            self.agents.sort(key=lambda x: int(x.number))
            
            # Order boxes and goals by their id
            self.boxes.sort(key=lambda x: int(x.id))
            self.goals.sort(key=lambda x: int(x.id))
            
            # Pre-compute distances between all nodes in the graph
            print('Pre-computing distances for the level...', file=sys.stderr, flush=True)
            #State.mainGraph.compute_distances()
            State.mainGraphDistances = nx.all_pairs_shortest_path_length(State.mainGraph)
            for goal in State.goals:
                #distsFromGoal = State.mainGraph.gridForGoal(State.walls, goal.coords)
                distsFromGoal = self.gridForGoal(goal.coords)
                State.goalDistances.append(distsFromGoal)
                State.goalDistancesByLetter[goal.letter.lower()].append(distsFromGoal)
                State.goalCoords[goal.letter.lower()].append(goal.coords)
                State.goalIds[goal.letter.lower()].append(goal.id)
            print('Pre-computing of distances completed succesfully!', file=sys.stderr, flush=True)
                
            '''except Exception as ex:
                print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
                sys.exit(1)'''
           
        # Generate a state with info. from parent.
        else:
            self.agents = cp.deepcopy(copy.agents)
            self.boxes = cp.deepcopy(copy.boxes)
            self.parent = copy.parent
            self.jointaction = cp.deepcopy(copy.jointaction)
            
            self.goalBoxAssignments = cp.deepcopy(copy.goalBoxAssignments)
            self.agentBoxAssignments = cp.deepcopy(copy.agentBoxAssignments)   
            self.boxIdsCompleted = cp.deepcopy(copy.boxIdsCompleted)
            self.goalIdsCompleted = cp.deepcopy(copy.goalIdsCompleted)
            
            self.g = copy.g
            self.h = copy.h
            
            self.debugDistances= cp.deepcopy(copy.debugDistances)
            

    def get_children(self) -> '[State, ...]':
        '''
        Returns a list of child states attained from applying every combination of applicable actions in the current state.
        The order of the actions within the joint action is random.
        '''
        children = []
        joint_actions = []
        num_agents = len(self.agents)
        
        # Compute available actions per each agent.
        for agent_idx in range(num_agents):
            joint_actions.append(self.check_agent_possible_actions(self.agents[agent_idx]))
        # Generate permutations with the available actions.
        perms = list(product(*joint_actions))
        #print(str(perms), file=sys.stderr, flush=True)
        
        # Generate a children state for each permutation.
        for perm in perms:
            child = State(self)
            child.jointaction = perm
            
            # Manage conflicts and update the positions of agents and boxes.
            if child.update_positions():
                child.parent = self
                child.g += 1
                
                children.append(child)
        
        # Sort children states randomly.
        State._RNG.shuffle(children)
        return children
    
    
    def check_agent_possible_actions(self, agent: 'Agent'):
        actions = []
        # Adding 'No action' possibility
        actions.append(Action(ActionType.NoOp, None, None))
        for action in ALL_ACTIONS:
            # Determine new coords. for the agent
            new_agent_row = agent.coords[0] + action.agent_dir.way[0]
            new_agent_col = agent.coords[1] + action.agent_dir.way[1]
            # Check if 'Move' action is possible
            if action.action_type is ActionType.Move:
                if self.is_free(new_agent_row, new_agent_col):
                    actions.append(action)
            # Check if 'Push' action is possible
            elif action.action_type is ActionType.Push:
                if self.box_at(new_agent_row, new_agent_col, agent.color):
                    new_box_row = new_agent_row + action.box_dir.way[0]
                    new_box_col = new_agent_col + action.box_dir.way[1]
                    if self.is_free(new_box_row, new_box_col):
                        actions.append(action)
            # Check if 'Pull' action is possible
            elif action.action_type is ActionType.Pull:
                if self.is_free(new_agent_row, new_agent_col):
                    box_row = agent.coords[0] + action.box_dir.way[0]
                    box_col = agent.coords[1] + action.box_dir.way[1] 
                    if self.box_at(box_row, box_col, agent.color):
                        actions.append(action)     
        return actions
    
    
    def update_positions(self) -> 'bool':
        for idx, action in enumerate(self.jointaction):
            if action.action_type is ActionType.NoOp:
                pass
            else:
                agent = self.agents[idx]
                new_agent_row = agent.coords[0] + action.agent_dir.way[0]
                new_agent_col = agent.coords[1] + action.agent_dir.way[1]
                if action.action_type is ActionType.Move:
                    if self.is_free(new_agent_row, new_agent_col):
                        self.agents[idx].coords = (new_agent_row, new_agent_col)
                    else: return False
                elif action.action_type is ActionType.Push:
                    box = self.box_at(new_agent_row, new_agent_col, agent.color)
                    if box != None:
                        new_box_row = box.coords[0] + action.box_dir.way[0]
                        new_box_col = box.coords[1] + action.box_dir.way[1]
                        if self.is_free(new_box_row, new_box_col):
                            self.agents[idx].coords = (new_agent_row, new_agent_col)
                            box.coords = (new_box_row, new_box_col)
                        else: return False
                    else: return False
                elif action.action_type is ActionType.Pull:
                    if self.is_free(new_agent_row, new_agent_col):
                        box_row = agent.coords[0] + action.box_dir.way[0]
                        box_col = agent.coords[1] + action.box_dir.way[1] 
                        box = self.box_at(box_row, box_col, agent.color)
                        if box != None:
                            new_box_row = agent.coords[0]
                            new_box_col = agent.coords[1]
                            self.agents[idx].coords = (new_agent_row, new_agent_col)
                            box.coords = (new_box_row, new_box_col)
                        else: return False
                    else: return False
        return True
    
    '''# Returns a list of coords in which there are obstacles in a path between two positions
    def is_path_clear(self, coordsA, coordsB):
        path = State.mainGraph.get_path(coordsA,coordsB)
        obstacles = []
        for pos in path:
            if not self.is_free(pos[0],pos[1]):
                obstacles.append(pos)
        return obstacles
    
    # Returns the agent/box matching the coords
    def get_object_at(self, coords):
        for box in self.boxes:
            if box.coords == (coords[0],coords[1]):
                return box
        for agent in self.agents:
            if agent.coords == (coords[0],coords[1]):
                return agent
        print("Couldn't get the object at "+str(coords), file=sys.stderr, flush=True)
        return None'''
    
    def is_initial_state(self) -> 'bool':
        return self.parent is None
    
    def is_goal_state(self) -> 'bool':
        for goal in State.goals:
            goal_is_statisfied = False
            for box in self.boxes:
                if(goal.letter == box.letter and goal.coords == box.coords):
                    #print(str(goal.coords) +" = "+  str(box.coords), file=sys.stderr, flush=True)
                    goal_is_statisfied=True
                    break
            
            if not goal_is_statisfied: return False   
        return True

    def extract_plan(self) -> '[State, ...]':
        plan = []
        state = self
        while not state.is_initial_state():
            plan.append(state)
            state = state.parent
        plan.reverse()
        return plan
    
    def is_free(self, row: 'int', col: 'int') -> 'bool':
        '''if row==3 and col==10 and not any(agent.coords == (row,col) for agent in self.agents):
            print("not State.walls[row][col]="+str(not State.walls[row][col]) \
              +" not any(box.coords == (row,col) for box in self.boxes)="+str(not any(box.coords == (row,col) for box in self.boxes)) \
              +" not any(agent.coords == (row,col) for agent in self.agents)="+str(not any(agent.coords == (row,col) for agent in self.agents)), file=sys.stderr, flush=True)
            print(self, file=sys.stderr, flush=True)'''
        if State.walls[row][col]:
            return False
        elif any(box.coords == (row,col) for box in self.boxes):
            return False
        elif any(agent.coords == (row,col) for agent in self.agents):
            return False
        else :
            return True
            
        #return not State.walls[row][col] and not any(box.coords == (row,col) for box in self.boxes) and not any(agent.coords == (row,col) for agent in self.agents)
    
    def box_at(self, row: 'int', col: 'int', color: 'str') -> 'Box':
        for box in self.boxes:
            if box.coords == (row,col) and box.color == color:
                return box
        return None
    
    
    ### GRAPH METHODS ###
    
    # Traverses the level defined by the 2d walls array
    # and outputs a 2d array of the same size, filled with distances from
    # a given point.
    #
    #   Input wall array                  Resulting array
    #
    #   wall     wall    start            0  0  0 (start)
    #   notwall  notwall notwall          3  2  1
    #   notwall  wall    notwall  ---->   4  0  2
    #   notwall  wall    notwall          5  0  3
    #
    def gridForGoal(self, startCoords):
        rowCnt = len(State.walls)
        colCnt = len(State.walls[0])
        gridDistances = [[0 for j in range(colCnt)] for i in range(rowCnt)]
        for node in State.mainGraph:
            node_coords = self.id2coords(node)
            try:
                gridDistances[node_coords[0]][node_coords[1]] = State.mainGraphDistances[node][self.coords2id(startCoords[0],startCoords[1])]
            except:
                gridDistances[node_coords[0]][node_coords[1]] = 0
        return gridDistances
    
    # Calculates distances between the_coords of one start point and 
    # many end points in a single graph traversal. Much more efficient than
    # running BFS for each of the end points.
    #
    # Returns an array representing the distances from the start point to
    # each of the end points, in a corresponding order as in the 
    # end_coords_array.
    def get_distance_one_to_many(self, start_coords, end_coords_array):
        distances = [float('inf') for i in range(len(end_coords_array))]
        start = self.coords2id(start_coords[0],start_coords[1])
        for idx, end_coords in enumerate(end_coords_array):
            try:
                distances[idx] = State.mainGraphDistances[start][self.coords2id(end_coords)]
            except:
                distances[idx] = float('inf')
        return distances
    
    # Returns the distance between two nodes
    def get_distance(self, coordsA, coordsB):
        try:
            return State.mainGraphDistances[self.coords2id(coordsA)][self.coords2id(coordsB)]
        except:
            print("Couldn't compute the distance to "+str(coordsB), file=sys.stderr, flush=True)
            return float('inf')
    
    def coords2id(self, i,j):
        return i*self.MAX_COL + j
  
    def id2coords(self, id):
        return (int(id/self.MAX_COL),id % self.MAX_COL)
    
    ### END OF GRAPH METHODS ###

    def __repr__(self):
        lines = []
        for row in range(State.MAX_ROW):
            line = []
            cont=False
            for col in range(State.MAX_COL):
                cont=False
               
                for box in self.boxes:
                    #print(str(box.is_at(row,col)), file=sys.stderr, flush=True)
                    if box.is_at(row,col):  
                         #print("box at" + str((row,col)), file=sys.stderr, flush=True)
                         line.append(box.letter)
                         cont = True
                
                for agent in self.agents:
                     if agent.is_at(row,col):
                         #print("agent at" + str((row,col)), file=sys.stderr, flush=True)
                         line.append(agent.number)
                         cont = True
                
                if cont: continue
                
                for goal in self.goals:
                     if goal.is_at(row,col):  
                         #print("goal at" + str((row,col)), file=sys.stderr, flush=True)
                         line.append(goal.letter.lower())
                         cont = True
                         
                
                
                if cont: continue
                if self.walls[row][col]: 
                    line.append('+')
                else: line.append(' ')
                
            #print(str(line), file=sys.stderr, flush=True)
            lines.append(''.join(line))
        return '\n'.join(lines)
    
    def __hash__(self):
        if self._hash is None:
            _hash = 1
            '''
            _hash = _hash * prime + self.agent_row
            _hash = _hash * prime + self.agent_col
            _hash = _hash * prime + hash(tuple(tuple(row) for row in self.boxes))
            _hash = _hash * prime + hash(tuple(tuple(row) for row in self.goals))
            _hash = _hash * prime + hash(tuple(tuple(row) for row in self.walls))
            '''
            self._hash = _hash
            
        return self._hash
    
    
    def __eq__(self, other):
        if not isinstance(other, State): return False
        if self.agents != other.agents: return False
        if self.boxes != other.boxes: return False
        return True
    