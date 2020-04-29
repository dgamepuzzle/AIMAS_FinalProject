# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:18:04 2020

@author: AIStars group
"""

import sys
import time
from heuristic import AStar, WAStar, Greedy
from state import State
from strategy import StrategyBFS, StrategyDFS, StrategyBestFirst
import configuration as config


class Plan:
    def __init__(self, start_state, goal_state, strategy_str):

        self.start_state = start_state
        test = State(start_state)
        self.goal_state = goal_state     
        print("Equal???: " + str(start_state == test), file=sys.stderr, flush=True)

        #TODO: Process strategy
        if strategy_str == 'bfs':
            self.strategy = StrategyBFS()
        elif strategy_str == 'dfs':
            self.strategy = StrategyDFS()
        elif strategy_str == 'astar':
            self.strategy = StrategyBestFirst(AStar(self.start_state))
        elif strategy_str == 'wastar':
            self.strategy = StrategyBestFirst(WAStar(self.start_state, 5))
        elif strategy_str == 'greedy':
            self.strategy = StrategyBestFirst(Greedy(self.start_state))
        else:
            # Default to BFS strategy.
            self.strategy = StrategyBFS()
            print('Defaulting to BFS search. Use arguments -bfs, -dfs, -astar, -wastar, or -greedy to set the search strategy.', file=sys.stderr, flush=True)
            
        
    def resolve(self):
        strategy = self.strategy
        print('Starting search with strategy {}.'.format(strategy), file=sys.stderr, flush=True)
        strategy.add_to_frontier(self.start_state)
        
        iterations = 0
        while True:
            if iterations == 250:
                print(strategy.search_status(), file=sys.stderr, flush=True)
                iterations = 0
            
            if config.get_memory_usage() > config.max_usage:
                print('Maximum memory usage exceeded.', file=sys.stderr, flush=True)
                return None
            
            if strategy.frontier_empty():
                return None
            
            leaf = strategy.get_and_remove_leaf()
            #print(str(leaf), file=sys.stderr, flush=True)
            #print(str(leaf.jointaction), file=sys.stderr, flush=True)
            
            if leaf.is_goal_state():
                print('found goal', file=sys.stderr, flush=True)
                return leaf.extract_plan()
            
            strategy.add_to_explored(leaf)
            for child_state in leaf.get_children(): # The list of expanded states is shuffled randomly; see state.py.
                if not strategy.is_explored(child_state) and not strategy.in_frontier(child_state):
                    strategy.add_to_frontier(child_state)
                    #print(str(child_state), file=sys.stderr, flush=True)
                    #print(str(child_state.jointaction), file=sys.stderr, flush=True)
            
            iterations += 1
            #time.sleep(2)
        pass
    
    