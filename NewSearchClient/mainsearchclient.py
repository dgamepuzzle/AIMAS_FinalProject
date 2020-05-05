import argparse
#import re
import sys

import configuration
from communicator import Communicator
from planning import Plan

GROUPNAME = "AIStars"

#GENERAL STEPS:
#1. Send client name
#2. Read level
#3. Solve level
#4. Send commands
#5. Celebrate

def main(strategy_str: 'str'):
    
    # Read the level data from server.
    com = Communicator()
    com.ReadServerMessage()
    
    # Create a plan to solve the level.
    planner = Plan(com.starting_state, com.goal_state, strategy_str)
    
    # Solve the level (resolve the plan and get a path from initial state to goal state).
    commands = planner.resolve()
    for command in commands:  
        print(str(command.jointaction), file=sys.stderr, flush=True)
    
    # Send actions to server.
    com.send_commands_to_server(commands)

    # Level completed!

if __name__ == '__main__':
    # Program arguments, reads the arguments from the command prompt through the argparse module.
    ##This code is taken directly from the warmup assignment.
    parser = argparse.ArgumentParser(description='Simple client based on state-space graph search.')
    parser.add_argument('--max-memory', metavar='<MB>', type=float, default=2048.0, help='The maximum memory usage allowed in MB (soft limit, default 2048).')
    
    # Parsing strategy args.
    strategy_group = parser.add_mutually_exclusive_group()
    strategy_group.add_argument('-bfs', action='store_const', dest='strategy', const='bfs', help='Use the BFS strategy.')
    strategy_group.add_argument('-dfs', action='store_const', dest='strategy', const='dfs', help='Use the DFS strategy.')
    strategy_group.add_argument('-astar', action='store_const', dest='strategy', const='astar', help='Use the A* strategy.')
    strategy_group.add_argument('-wastar', action='store_const', dest='strategy', const='wastar', help='Use the WA* strategy.')
    strategy_group.add_argument('-greedy', action='store_const', dest='strategy', const='greedy', help='Use the Greedy strategy.')
    args = parser.parse_args()
    if(args.strategy != None):
        print("strategy: "+args.strategy, file=sys.stderr, flush=True)
    
    # Set max memory usage allowed (soft limit).
    configuration.max_memory_usage = args.max_memory
    
    # Run client.
    main(args.strategy)
    