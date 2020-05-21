# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:18:04 2020

@author: AIStars group
"""

import time
import sys
import configuration as config
from heuristic import AStar, WAStar, Greedy
from strategy import StrategyBFS, StrategyDFS, StrategyBestFirst


class Plan:
    def __init__(self, start_state, goal_state, strategy_str):

        # Save info. of initial and goal states.
        self.start_state = start_state
        self.goal_state = goal_state     

        # Process strategy.
        if strategy_str == 'bfs':
            self.strategy = StrategyBFS()
        elif strategy_str == 'dfs':
            self.strategy = StrategyDFS()
        elif strategy_str == 'astar':
            self.strategy = StrategyBestFirst(AStar(self.start_state))
        elif strategy_str == 'wastar':
            self.strategy = StrategyBestFirst(WAStar(self.start_state, 5)) # default w = 5 (g + w*h)
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
        
        # Infinite loop to resolve the level.
        iterations = 0
        while True:
            
            # Print search info. every 250 iterations.
            if iterations == 250:
                print(strategy.search_status(), file=sys.stderr, flush=True)
                iterations = 0
            
            # Check if memory limit is exceeded.
            if config.get_memory_usage() > config.max_usage:
                print('Maximum memory usage exceeded.', file=sys.stderr, flush=True)
                return None
            
            # Check if there are no more leafs in the search tree (empty frontier).
            if strategy.frontier_empty():
                return None
            
            # Take next state (leaf) from the frontier.     
            print("---top 3 in queue---", file=sys.stderr, flush=True)
            for i in range(3):
                s = strategy.frontier.peek(i)
                
                print(str(s), file=sys.stderr, flush=True)
            leaf = strategy.get_and_remove_leaf()
            #print(str(leaf.jointaction), file=sys.stderr, flush=True)
            time.sleep(0.5)
            # Check if the current state corresponds to a goal state. If True return the current plan.
            if leaf.is_goal_state():
                print('found goal', file=sys.stderr, flush=True)
                return leaf.extract_plan()
            
            # Mark leaf as explored and add children states to frontier.
            strategy.add_to_explored(leaf)
            for child_state in leaf.get_children(): # The list of expanded states is shuffled randomly; see state.py.
                if not strategy.is_explored(child_state) and not strategy.in_frontier(child_state):
                    strategy.add_to_frontier(child_state)
                    #print(child_state, file=sys.stderr, flush=True)
            iterations += 1
        pass
    