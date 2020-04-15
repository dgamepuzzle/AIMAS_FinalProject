# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:14:20 2020

@author: AIStars group
"""

import sys

from graph import Graph
from level_entities import Agent, Box, Goal


class State:
    agents = []
    boxes = []
    goals = []
    
    def __init__(self, MAX_ROW: 'int', MAX_COL: 'int', level_lines):
        self.MAX_ROW = MAX_ROW
        self.MAX_COL = MAX_COL
        self.graph = Graph()
        
        #Parse full level (build graph and save mobile entities)
        try:
            for row, line in enumerate(level_lines):
                for col, char in enumerate(level_lines):
                    if char != '+':
                        cur_node = self.graph.coords2id(col,row,MAX_COL)
                        self.graph.add_node(cur_node)
                        for coord in [(-1,0),(1,0),(0,1),(0,-1)]:
                            k = coord[0]
                            l = coord[1]
                            h = min(MAX_ROW-1, max(0, row+k))
                            u = min(MAX_COL-1, max(0, col+l))
                            if level_lines[h][u]!='+':
                                dest_node = self.graph.coords2id(h, u, MAX_COL)
                                self.graph.add_node(dest_node)
                                self.graph.add_edge(cur_node, dest_node, 1) # default distance = 1
                                #print(str(cur_node) + " ->" + str(dest_node), file=sys.stderr, flush=True)
                        #Parse agents
                        if char in "0123456789":
                            self.agents.append((row, col))
                        #Parse boxes
                        elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            self.boxes.append((row, col))
                        #Parse goals
                        elif char in "abcdefghijklmnopqrstuvwxyz":
                            self.goals.append((row, col))
    
                        else:
                            print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                            sys.exit(1)
                    else:
                        # Walls are not being processed
                        pass
            
        except Exception as ex:
            print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            sys.exit(1)
    
