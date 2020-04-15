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


class Box:
    def __init__(self, letter: 'str', color: 'str', coords):
        self.letter = letter
        self.color = color
        self.coords = coords


class Goal:
    def __init__(self, letter: 'str', color: 'str', coords):
        self.letter = letter
        self.color = color
        self.coords = coords
    