# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:14:20 2020

@author: AIStars group
"""
from itertools import product

import itertools
import sys
import random

from graph import Graph
from jointaction import ActionType, ALL_ACTIONS
from level_elements import Agent, Box, Goal
from jointaction import ALL_ACTIONS, ActionType

class State:
    _RNG = random.Random(1)
    MAX_ROW = None
    MAX_COL = None
    goals = []
    colors = []
    walls = []
    
    def __init__(self, copy: 'State', level_lines = "", goal_state = False):
        
        if copy ==None:
            self.graph = Graph()
            self.agents = []
            self.boxes = []
            self.parent = None
            self.jointaction = []

            self.g = 0
            self.h = -1
            
            State.walls = [[False for _ in range(State.MAX_COL)] for _ in range(State.MAX_ROW)]
            
            #Parse full level (build graph and save mobile entities)
            try:
                for row, line in enumerate(level_lines):
                    for col, char in enumerate(line):
                        if char != '+':
                            cur_node = self.graph.coords2id(col,row,State.MAX_COL)
                            self.graph.add_node(cur_node)
                            for coord in [(-1,0),(1,0),(0,1),(0,-1)]:
                                k = coord[0]
                                l = coord[1]
                                h = min(State.MAX_ROW-1, max(0, row+k))
                                u = min(State.MAX_COL-1, max(0, col+l))
                                if level_lines[h][u]!='+':
                                    dest_node = self.graph.coords2id(h, u, State.MAX_COL)
                                    self.graph.add_node(dest_node)
                                    self.graph.add_edge(cur_node, dest_node, 1) # default distance = 1
                                    #print(str(cur_node) + " ->" + str(dest_node), file=sys.stderr, flush=True)
                            #Parse agents
                            if char in "0123456789":
                                color = State.colors[char]
                                self.agents.append(Agent(char,color,(row, col)))
                                
                                print("saving agent at "+ str((row,col)), file=sys.stderr, flush=True)
                            #Parse boxes
                            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                                color = State.colors[char]
                                self.boxes.append(Box(char, color, (row, col)))
                                if goal_state: #Parse goals
                                    print("adding goal to array", file=sys.stderr, flush=True)
                                    State.goals.append(Goal(char,(row, col)))
                            #Parse spaces
                            elif (char ==' '):
                                #Do nothing after creating the node
                                pass
                            else:
                                print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                                sys.exit(1)
                        else:
                            # Walls are not being processed
                            State.walls[row][col] = True
                            pass
                
            except Exception as ex:
                print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
                sys.exit(1)
        else:
            self.graph = copy.graph
            self.agents = copy.agents
            self.boxes = copy.boxes
            self.parent = copy.parent
            self.jointaction = copy.jointaction
            
            self.g = copy.g
            self.h = copy.h

    def get_children(self) -> '[State, ...]':
        '''
        Returns a list of child states attained from applying every combination of applicable actions in the current state.
        The order of the actions within the joint action is random.
        '''
        #print('get children', file=sys.stderr, flush=True)
        children = []
        joint_actions = []
        num_agents = len(self.agents)
        # Compute available actiones per each agent
        for agent_idx in range(num_agents):
            joint_actions.append(self.agents[agent_idx])
        # Generate permutations with the available actions
        perms = list(itertools.product(ALL_ACTIONS, repeat= num_agents))
        # Generate a children state for each permutation
        #print(str(perms), file=sys.stderr, flush=True)
        for perm in perms:
            child = State(self)
            child.jointaction = perm
            # Manage conflicts and update the positions of agents and boxes
            if child.update_positions():
                child.parent = self
                child.g += 1
                children.append(child)
        
        State._RNG.shuffle(children)
        return children
    
    def check_agent_possible_actions(self, agent: 'Agent'):
        actions = []
        for action in ALL_ACTIONS:
            # Determine if action is applicable.
            new_agent_row = agent.coords[0] + action.agent_dir.way[0]
            new_agent_col = agent.coords[1] + action.agent_dir.way[1]
            
            if action.action_type is ActionType.Move:
                if self.is_free(new_agent_row, new_agent_col):
                    actions.append(action)
            elif action.action_type is ActionType.Push:
                if self.box_at(new_agent_row, new_agent_col):
                    new_box_row = new_agent_row + action.box_dir.way[0]
                    new_box_col = new_agent_col + action.box_dir.way[1]
                    if self.is_free(new_box_row, new_box_col):
                        actions.append(action)
            elif action.action_type is ActionType.Pull:
                if self.is_free(new_agent_row, new_agent_col):
                    box_row = self.agent_row + action.box_dir.way[0]
                    box_col = self.agent_col + action.box_dir.way[1]
                    if self.box_at(box_row, box_col):
                        actions.append(action)
                        
        
        return actions
    
    def update_positions(self) -> 'bool':
        for idx, action in enumerate(self.jointaction):
            agent = self.agents[idx]
            new_agent_row = agent.coords[0] + action.agent_dir.way[0]
            new_agent_col = agent.coords[1] + action.agent_dir.way[1]
            if action.action_type is ActionType.Move:
                if self.is_free(new_agent_row, new_agent_col):
                    self.agents[idx].coords = (new_agent_row, new_agent_col)
                else: return False
            elif action.action_type is ActionType.Push:
                if self.box_at(new_agent_row, new_agent_col):
                    new_box_row = new_agent_row + action.box_dir.way[0]
                    new_box_col = new_agent_col + action.box_dir.way[1]
                    if self.is_free(new_box_row, new_box_col):
                        self.agents[idx].coords[0] = new_agent_row
                        self.agents[idx].coords[1] = new_agent_col
                        #TODO Fix this, identify the box first
                        #self.boxes[idx].coords[0] = new_box_row
                        #self.boxes[idx].coords[1] = new_box_col
                    else: return False
                else: return False
            elif action.action_type is ActionType.Pull:
                if self.is_free(new_agent_row, new_agent_col):
                    box_row = agent.coords[0] + action.box_dir.way[0]
                    box_col = agent.coords[1] + action.box_dir.way[1]
                    if self.box_at(box_row, box_col):
                        self.agents[idx].coords[0] = new_agent_row
                        self.agents[idx].coords[1] = new_agent_col
                        #TODO Fix this, identify the box first
                        #self.boxes[self.agent_row][self.agent_col] = self.boxes[box_row][box_col]
                        #self.boxes[box_row][box_col] = None
                    else: return False
                else: return False
        return True
    
    def is_initial_state(self) -> 'bool':
        return self.parent is None
    
    def is_goal_state(self) -> 'bool':
        for goal in State.goals:
            for box in self.boxes:
                
                if(goal.letter == box.letter.lower() and goal.coords == box.coords):
                    print(goal.letter +" = "+ box.letter.lower(), file=sys.stderr, flush=True)
                    print(goal.coords +" = "+  box.coords, file=sys.stderr, flush=True)
                    break
            
            return False    
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
        return self.graph.contains_node(row,col, self.MAX_COL) and not any(box.coords == (row,col) for box in self.boxes) and not any(agent.coords == (row,col) for agent in self.agents)
    
    def box_at(self, row: 'int', col: 'int') -> 'bool':
        return any(box.coords == (row,col) for box in self.boxes)

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
                         print("box at" + str((row,col)), file=sys.stderr, flush=True)
                         line.append(box.letter)
                         cont = True
                
                for goal in self.goals:
                     if goal.is_at(row,col):  
                         print("goal at" + str((row,col)), file=sys.stderr, flush=True)
                         line.append(goal.letter)
                         cont = True
                         
                for agent in self.agents:
                     if agent.is_at(row,col):
                         print("agent at" + str((row,col)), file=sys.stderr, flush=True)
                         line.append(agent.number)
                         cont = True
                
                if cont: continue
                if self.walls[row][col]: 
                    line.append('+')
                else: line.append(' ')
                
            print(str(line), file=sys.stderr, flush=True)
            lines.append(''.join(line))
        return '\n'.join(lines)