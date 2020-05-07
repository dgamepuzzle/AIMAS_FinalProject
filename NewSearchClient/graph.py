# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:58:42 2020

@author: AIStars group
"""
import state
from _collections import defaultdict
from collections import deque
import sys

sys.setrecursionlimit(10000)

class Graph:
    def __init__(self):
        self.nodes = set()
        #self.edges = defaultdict(set)
        self.distances = {}

    def add_node(self, node):
        self.nodes.add(node)

    def contains_node(self, i,j):
        cols = state.State.MAX_COL
        for node in self.nodes:
            if node.coords2id(i,j) == node.value :
                return node
        return None
   
    def create_or_get_node(self, i, j):
        node = self.contains_node(i,j)
        if node == None:
            node = Node(i,j) 
            self.add_node(node)
        return node
    
    def create_goal_graph(self, coords):
        
        
        goal_node = self.contains_node(coords[0],coords[1])
        
        goal_node.distanceToGoal = 0
        print('gaol node: '+ str(goal_node), file=sys.stderr, flush=True)
        queue = deque()
        
        queue = self.add_to_queue(goal_node, queue)
        
    def add_to_queue(self, node, queue):
        for edge in node.edges:
            if edge.distanceToGoal == None:
                edge.distanceToGoal = node.distanceToGoal +1
                #print('current node: '+ str(node), file=sys.stderr, flush=True)
                #print('adding edge: '+ str(edge), file=sys.stderr, flush=True)
                queue.append(edge)
        
        if len(queue) >0:
            
            self.add_to_queue(queue.popleft(), queue)
        else:
            return queue
        
            
    def __repr__(self):
        lines = []
        for row in range(state.State.MAX_ROW):
            line = []
            for col in range(state.State.MAX_COL):
                node = self.contains_node(row, col)
                if node != None:
                    if node.distanceToGoal == None:
                        line.append(' ')
                    elif node.distanceToGoal < 10:
                        line.append(str(node.distanceToGoal))
                    else:
                        line.append('.')
                else:
                    line.append('+')
                
            #print(str(line), file=sys.stderr, flush=True)
            lines.append(''.join(line))
        return '\n'.join(lines)
    
# =============================================================================
#     def __deepcopy__(self, memodict={}):
#         copy_object = Graph()
#         for node in self.nodes:
#             copy_object.add_node = cp.deepcopy(node)
#         return copy_object
# =============================================================================

class Node:
    def __init__(self, i,j):
        self.value = self.coords2id(i,j)
        self.edges = set()
        self.distanceToGoal = None
      
    def add_edge(self, to_node):
        self.edges.add(to_node) 
      
    def coords2id(self, i,j):
        cols = state.State.MAX_COL
        return i*cols + j
  
    def id2coords(self, id):
        cols = state.State.MAX_COL
        return (int(id/cols),id % cols)
    
# =============================================================================
#     def __deepcopy__(self, memodict={}):
#         copy_object = Node()
#         copy_object.distanceToGoal = self.distanceToGoal
#         copy_object.edges = cp.deepcopy(node)
#         return copy_object
# =============================================================================
    
    def __repr__(self):
        return "Node at: " + str(self.id2coords(self.value)) + "with " + str(len(self.edges)) + " edges, and distance to goal " + str(self.distanceToGoal)