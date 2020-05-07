# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:14:20 2020

@author: AIStars group
"""

import copy as cp
import random
import sys
from itertools import product

from graph import Graph, Node
from jointaction import Action, ActionType, ALL_ACTIONS
from level_elements import Agent, Box, Goal

class State:
    _RNG = random.Random(1)
    MAX_ROW = None
    MAX_COL = None
    goals = []
    colors = []
    walls = []
    
    mainGraph = Graph()
    goalGraphs = []
    
    def __init__(self, copy: 'State' = None, level_lines = "", goal_state = False):
        self._hash = None
        if copy == None:
            self.agents = []
            self.boxes = []
            self.parent = None
            self.jointaction = []
            self.g = 0
            self.h = -1
            State.walls = [[False for _ in range(State.MAX_COL)] for _ in range(State.MAX_ROW)]
            
            # Parse full level (build static graph and save static/non-static entities).
            try:
                for row, line in enumerate(level_lines):
                    for col, char in enumerate(line):
                        
                        if char != '+':
                            
                            # First, as it's not a wall, add node to the static graph.
                            cur_node = State.mainGraph.create_or_get_node(row, col)
                            
                                
                            for coord in [(-1,0),(1,0),(0,1),(0,-1)]:
                                k = coord[0]
                                l = coord[1]
                                h = min(State.MAX_ROW-1, max(0, row+k))
                                u = min(State.MAX_COL-1, max(0, col+l))
                                if level_lines[h][u]!='+':
                                    dest_node = State.mainGraph.create_or_get_node(h, u)
                                    cur_node.add_edge(dest_node)
                                    #mainGraph.add_edge(cur_node, dest_node, 1) # default distance = 1
                                    #print(str(cur_node) + " ->" + str(dest_node), file=sys.stderr, flush=True)
                            
                            # Parse agents.
                            if char in "0123456789":
                                color = State.colors[char]
                                self.agents.append(Agent(char,color,(row, col)))
                                #print("Saving agent at "+ str((row,col)), file=sys.stderr, flush=True)
                                
                            # Parse boxes.
                            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                                color = State.colors[char]
                                self.boxes.append(Box(char, color, (row, col)))
                                if goal_state: #Parse goals
                                    State.goals.append(Goal(char,(row, col)))
                                    #print("adding goal at "+ str((row,col)), file=sys.stderr, flush=True)
                            
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
                            pass
                
            except Exception as ex:
                print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
                sys.exit(1)
              
                
            #Generate goal graphs
            
            for goal in State.goals:
                new_goal_state = cp.deepcopy(State.mainGraph)
                new_goal_state.create_goal_graph(goal.coords)
                State.goalGraphs.append(new_goal_state)
                goal.distanceGraph = new_goal_state
                
                
            #print(list(State.mainGraph.nodes)[0], file=sys.stderr, flush=True) 
           # print(State.mainGraph, file=sys.stderr, flush=True)
            
        
           
        # Generate a state with info. from parent.
        else:
            self.agents = cp.deepcopy(copy.agents)
            self.boxes = cp.deepcopy(copy.boxes)
            self.parent = copy.parent
            self.jointaction = cp.deepcopy(copy.jointaction)
            
            self.g = copy.g
            self.h = copy.h
            

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
        return not State.walls[row][col] and not any(box.coords == (row,col) for box in self.boxes) and not any(agent.coords == (row,col) for agent in self.agents)
    
    def box_at(self, row: 'int', col: 'int', color: 'str') -> 'Box':
        for box in self.boxes:
            if box.coords == (row,col) and box.color == color:
                return box
        return None

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
            prime = 31
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
    