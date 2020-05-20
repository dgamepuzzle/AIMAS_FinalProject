# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:58:42 2020

@author: AIStars group
"""
import state
from collections import defaultdict, deque
import sys

sys.setrecursionlimit(10000)

class Graph:
    def __init__(self):
        self.nodes = set()

    def add_node(self, node):
        self.nodes.add(node)

    def contains_node(self, i,j):
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
    
    def get_distance(self, coordsA, coordsB):
        nodeA = self.contains_node(coordsA[0],coordsA[1])
        nodeB = self.contains_node(coordsB[0],coordsB[1])
        distances = defaultdict()
        queue = deque()
        distances[nodeA.value] = 0
        queue.append(nodeA)
        while queue:
            node = queue.pop()
            dist = distances[node.value] + 1
            for neighbor in node.edges:
                if not neighbor.explored:
                    if neighbor == nodeB:
                        self.reset_explored_flags()
                        return dist
                    distances[neighbor.value] = dist
                    queue.append(neighbor)
            node.explored = True
        self.reset_explored_flags()
        print("Couldn't compute the distance to "+str(coordsB), file=sys.stderr, flush=True)
        return float('inf')
    
    # Calculates distances between the_coords of one start point and 
    # many end points in a single graph traversal. Much more efficient than
    # running BFS for each of the end points.
    #
    # Returns an array representing the distances from the start point to
    # each of the end points, in a corresponding order as in the 
    # end_coords_array.
    def get_distance_one_to_many(self, start_coords, end_coords_array):
        distances = [float('inf') for i in range(len(end_coords_array))]
        dist = defaultdict()
        cnt_found = 0
        start = self.contains_node(start_coords[0],start_coords[1])
        queue = deque()
        queue.append(start)
        dist[start.value] = 0
        while queue:
            node = queue.pop()
            if (node.coords[0],node.coords[1]) in end_coords_array:
                end_coord_idx = end_coords_array.index((node.coords[0],node.coords[1]))
                distances[end_coord_idx] = dist[node.value]
                cnt_found += 1
                if cnt_found >= len(end_coords_array):
                    return distances
            for neighbor in node.edges:
                if not neighbor.explored:
                    dist[neighbor.value] = dist[node.value] + 1
                    queue.append(neighbor)
            node.explored = True
        self.reset_explored_flags()
        return distances
    
    def update_goal_distances(self, coords, goalId):
        goal_node = self.contains_node(coords[0],coords[1])
        goal_node.distancesToGoals[goalId] = 0
        #print('Goal ' + str(goalId) + ' node: '+ str(goal_node), file=sys.stderr, flush=True)
        self.compute_goal_distances(goal_node, goalId)
        
    def compute_goal_distances(self, origin, goalId):
        queue = deque()
        queue.append(origin)
        while queue:
            node = queue.pop()
            dist = node.distancesToGoals[goalId] + 1
            for neighbor in node.edges:
                if not neighbor.explored:
                    neighbor.distancesToGoals[goalId] = dist
                    queue.append(neighbor)
            node.explored = True
        self.reset_explored_flags()
    
    def reset_explored_flags(self):
        for node in self.nodes:
            node.explored = False
        
    def __repr__(self):
        lines = []
        for row in range(state.State.MAX_ROW):
            line = []
            for col in range(state.State.MAX_COL):
                node = self.contains_node(row, col)
                if node != None:
                    line.append('O')
                else:
                    line.append(' ')
            #print(str(line), file=sys.stderr, flush=True)
            lines.append(line)
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
        self._hash = None
        self.value = self.coords2id(i,j)
        self.coords = (i, j)
        self.edges = set()
        self.distancesToGoals = defaultdict()
        self.explored = False
      
    def add_edge(self, to_node):
        self.edges.add(to_node) 
      
    def coords2id(self, i,j):
        cols = state.State.MAX_COL
        return i*cols + j
  
    def id2coords(self, id):
        cols = state.State.MAX_COL
        return (int(id/cols),id % cols)
    
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
    
    def __eq__(self, other: 'Node'):
        if not isinstance(other, Node): return False
        if self.value != other.value: return False
        return True
    
# =============================================================================
#     def __deepcopy__(self, memodict={}):
#         copy_object = Node()
#         copy_object.distanceToGoal = self.distanceToGoal
#         copy_object.edges = cp.deepcopy(node)
#         return copy_object
# =============================================================================
    
    def __repr__(self):
        return "Node at: " + str(self.id2coords(self.value)) + "with " + str(len(self.edges)) + " edges, and distances to goals " + str(self.distancesToGoals)