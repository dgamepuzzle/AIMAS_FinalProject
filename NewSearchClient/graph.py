# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:58:42 2020

@author: AIStars group
"""

from _collections import defaultdict

class Graph:
  def __init__(self):
    self.nodes = set()
    self.edges = defaultdict(set)
    self.distances = {}

  def add_node(self, value):
    self.nodes.add(value)

  def add_edge(self, from_node, to_node, distance):
    self.edges[from_node].add(to_node)
    self.edges[to_node].add(from_node)
    self.distances[(from_node, to_node)] = distance
    
  def coords2id(self, i,j, cols):
      return i*cols + j
  
  def id2coords(self, id, cols):
      return (int(id/cols),id % cols)
