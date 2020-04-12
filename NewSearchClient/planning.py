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
                    self.initial_state = State()
                    for row, line in enumerate(lines):
                        for col, char in enumerate(line):
                            if char == '+': self.initial_state.walls[row][col] = True
                            elif char in "0123456789":
                                self.initial_state.agents_row[int(char)] = row
                                self.initial_state.agents_col[int(char)] = col
                                if self.num_agents is None:
                                    self.num_agents = 1
                                else:
                                    self.num_agents += 1
                            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": self.initial_state.boxes[row][col] = char
                            elif char in "abcdefghijklmnopqrstuvwxyz": self.initial_state.goals[row][col] = char
                            elif char == ' ':
                                # Free cell.
                                pass
                            else:
                                print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                                sys.exit(1)
                
                #Read lines for goal state
                if line == "#goal":
                    currentLine = server_messages.readline().rstrip()
                    while "#" not in currentLine:
                        lines.append(currentLine)
                        currentLine = server_messages.readline().rstrip()
                    line = currentLine
                    self.goal_state = State()
                    for row, line in enumerate(lines):
                        for col, char in enumerate(line):
                            if char == '+': self.goal_state.walls[row][col] = True
                            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": self.initial_state.boxes[row][col] = char
                            elif char == ' ':
                                # Free cell.
                                pass
                            else:
                                print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                                sys.exit(1)
                    
        
        except Exception as ex:
            print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            sys.exit(1)
