# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:55:58 2020

@author: AIStars group
"""


class Agent:
    
    def __init__(self, number: 'int', color: 'str', coords):
        self.number = number
        self.color = color
        self.coords = coords

    def is_at(self, row, col):
        return (self.coords == (row,col))
    
    def __eq__(self, other: 'Agent'):
        if not isinstance(other, Agent): return False
        if self.number != other.number: return False
        if self.color != other.color: return False
        if self.coords != other.coords: return False
        return True

class Box:
    
    autoIncrement = 0
    
    def __init__(self, letter: 'str', color: 'str', coords):
        self.letter = letter
        self.color = color
        self.coords = coords
        self.id = Box.autoIncrement
        Box.autoIncrement += 1
        
    def is_at(self, row, col):
        return (self.coords == (row,col))
    
    def __eq__(self, other: 'Box'):
        if not isinstance(other, Box): return False
        if self.letter != other.letter: return False
        if self.color != other.color: return False
        if self.coords != other.coords: return False
        if self.id != other.id: return False
        return True

class Goal:
    
    autoIncrement = 0
    
    def __init__(self, letter: 'str', coords):
        self.letter = letter
        self.coords = coords
        self.id = Goal.autoIncrement
        Goal.autoIncrement += 1
    
    def is_at(self, row, col):
        return (self.coords == (row,col))
    
    def __eq__(self, other: 'Goal'):
        if not isinstance(other, Goal): return False
        if self.letter != other.letter: return False
        if self.coords != other.coords: return False
        if self.id != other.id: return False
        return True
    