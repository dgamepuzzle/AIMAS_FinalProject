# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:18:04 2020

@author: AIStars group
"""

import sys

from state import State


class Plan:
    def __init__(self, server_messages, strategy_str):
        
        #TODO: Process strategy
        
        try:
            line = server_messages.readline().rstrip()
            while line != "#end":
                
                #Read domain
                if line == "#domain":
                    self.domain = server_messages.readline().rstrip()
                    line = server_messages.readline().rstrip()

                #Read levelname
                if line == "#levelname":
                    self.name = server_messages.readline().rstrip()
                    line = server_messages.readline().rstrip()
                
                #Read colors
                if line == "#colors":
                    colors = {}
                    currentLine = server_messages.readline().rstrip()
                    while "#" not in currentLine:
                        currentLine.replace(" ", "")
                        color, currentLine = currentLine.split(":")
                        colors[color] = currentLine.split(",")
                        currentLine = server_messages.readline().rstrip()
                    self.colors = colors
                    line = currentLine
                
                #Read initial state
                if line == "#initial":
                    #Add all lines to an array to know how many rows we have
                    lines = []
                    longestLine = 0;
                    currentLine = server_messages.readline().rstrip()
                    while "#" not in currentLine:
                        lines.append(currentLine)
                        if len(currentLine)>longestLine:
                            longestLine=len(currentLine)
                        currentLine = server_messages.readline().rstrip()
                    line = currentLine
                    #Set max size of states based on input
                    self.MAX_COL=longestLine
                    self.MAX_ROW=len(lines)
                    # Read lines for initial state
                    self.initial_state = State(self.MAX_ROW, self.MAX_COL, lines)
                
                #Read lines for goal state
                if line == "#goal":
                    currentLine = server_messages.readline().rstrip()
                    while "#" not in currentLine:
                        lines.append(currentLine)
                        currentLine = server_messages.readline().rstrip()
                    line = currentLine
                    self.goal_state = State(self.MAX_ROW, self.MAX_COL, lines)
                    
        
        except Exception as ex:
            print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            sys.exit(1)
