# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:55:58 2020

@author: AIStars group
"""
import sys

class Agent:
    def __init__(self, number: 'int', color: 'str', coords):
        self.number = number
        self.color = color
        self.coords = coords

    def is_at(self, row, col):
        return (self.coords == (row,col))

class Box:
    def __init__(self, letter: 'str', color: 'str', coords):
        self.letter = letter
        self.color = color
        self.coords = coords

    def is_at(self, row, col):
        return (self.coords == (row,col))

class Goal:
    def __init__(self, letter: 'str', coords):
        self.letter = letter
        self.coords = coords
    
    def is_at(self, row, col):
        return (self.coords == (row,col))