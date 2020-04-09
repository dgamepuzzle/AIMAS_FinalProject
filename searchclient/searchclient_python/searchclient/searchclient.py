import argparse
import re
import sys
from collections import defaultdict

import memory
from state import State
from strategy import StrategyBFS, StrategyDFS, StrategyBestFirst
from heuristic import AStar, WAStar, Greedy


class SearchClient:
    def __init__(self, server_messages):
        self.initial_state = None
        
        # Load lines into a temporary array to get rows and cols
        lines = []
        try:
            line = server_messages.readline().rstrip()
            
            while line:
                lines.append(line);
                line = server_messages.readline().rstrip()
        except Exception as ex:
            print('Error reading level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            sys.exit(1)
            
        rows = len(lines)
        cols = len(lines[0])
        
        colors_re = re.compile(r'^[a-z]+:\s*[0-9A-Z](\s*,\s*[0-9A-Z])*\s*$')
        try:
            # Read lines for colors. There should be none of these in warmup levels.
            if colors_re.fullmatch(lines[0]) is not None:   
                print('Error, client does not support colors.', file=sys.stderr, flush=True)
                sys.exit(1)
                
            State.maxRow = rows
            State.maxCol = cols
            
            self.initial_state = State()
                
            for row, line in enumerate(lines):
                for col, char in enumerate(line):
                    if char == '+': State.walls[row][col] = True
                    elif char in "0123456789":
                        if self.initial_state.agent_row is not None:
                            print('Error, encountered a second agent (client only supports one agent).', file=sys.stderr, flush=True)
                            sys.exit(1)
                        self.initial_state.agent_row = row
                        self.initial_state.agent_col = col
                    elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": self.initial_state.boxes[row][col] = char
                    elif char in "abcdefghijklmnopqrstuvwxyz": State.goals[row][col] = char
                    elif char == ' ':
                        # Free cell.
                        pass
                    else:
                        print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                        sys.exit(1)
        except Exception as ex:
            print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            sys.exit(1)
    
    def search(self, strategy: 'Strategy') -> '[State, ...]':
        print('Starting search with strategy {}.'.format(strategy), file=sys.stderr, flush=True)
        strategy.add_to_frontier(self.initial_state)
        
        iterations = 0
        while True:
            if iterations == 1000:
                print(strategy.search_status(), file=sys.stderr, flush=True)
                iterations = 0
            
            if memory.get_usage() > memory.max_usage:
                print('Maximum memory usage exceeded.', file=sys.stderr, flush=True)
                return None
            
            if strategy.frontier_empty():
                return None
            
            leaf = strategy.get_and_remove_leaf()
            
            if leaf.is_goal_state():
                return leaf.extract_plan()
            
            strategy.add_to_explored(leaf)
            for child_state in leaf.get_children(): # The list of expanded states is shuffled randomly; see state.py.
                if not strategy.is_explored(child_state) and not strategy.in_frontier(child_state):
                    strategy.add_to_frontier(child_state)
            
            iterations += 1

    def bi_search(self, strategy1: 'Strategy', strategy2: 'Strategy') -> '[State, ...]':
        print('Starting bidirectional search with strategy {}. and strategy {}.'.format(strategy1, strategy2), file=sys.stderr, flush=True)
        strategy1.add_to_frontier(self.initial_state)
        
        # To search backwards, we have to define our goal state
        
        # Create a "database" of vacant goals
        vacant_goal_coords = defaultdict(list)
        goal_coords = []
        
        # Loop through the goals, and save their coordinates
        for i in range(len(State.goals)):
            for j in range(len(State.goals[i])):
                if State.goals[i][j] is None:
                    continue
                if State.goals[i][j] in 'abcdefghijklmnopqrstuvwxyz':
                    vacant_goal_coords[State.goals[i][j]].append((i, j))
                    goal_coords.append((i, j))

        # Create new goal state with each goal having a corresponding box                    
        goal_state = State(copy=self.initial_state)
        goal_state.parent = None
        
        for i in range(len(goal_state.boxes)):
            for j in range(len(goal_state.boxes[i])):
                if goal_state.boxes[i][j] is None:
                    continue
                if goal_state.boxes[i][j] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    box_type = goal_state.boxes[i][j]
                    if not len(vacant_goal_coords[box_type]):
                        continue
                    goal_coord = vacant_goal_coords[box_type].pop()
                    goal_state.boxes[goal_coord[0], goal_coord[1]] = box_type
                    goal_state.boxes[i][j] = None
                    
        
        # We need to set realistic agent positions for our goal state!
        agent_offsets = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), 
                         (-1, 1), (1, -1)]
        
        # It is realistic to assume that our agent would be next to one of our
        # goals. Therefore we can generate goals
        for goal_coord in goal_coords:
            for agent_offset in agent_offsets:
                agent_new_row = goal_coord[0] + agent_offset[0]
                agent_new_col = goal_coord[1] + agent_offset[1]
                
                if agent_new_row >= len(goal_state.goals):
                    continue
                if agent_new_col >= len(goal_state.goals[agent_new_row]):
                    continue
                if goal_state.walls[agent_new_row][agent_new_col]:
                    continue
                if goal_state.goals[agent_new_row][agent_new_col] is not None:
                    continue
                #if goal_state.boxes[agent_new_row][agent_new_col] is not None:
                #    print('Box', file=sys.stderr, flush=True)
                #    continue
                
                another_goal_state = State(copy=goal_state)
                another_goal_state.agent_row = agent_new_row
                another_goal_state.agent_col = agent_new_col
                
                strategy2.add_to_frontier(another_goal_state)
        
        iterations = 0
        while True:
            if iterations == 1000:
                print(strategy1.search_status(), file=sys.stderr, flush=True)
                print(strategy2.search_status(), file=sys.stderr, flush=True)
                iterations = 0
            
            if memory.get_usage() > memory.max_usage:
                print('Maximum memory usage exceeded.', file=sys.stderr, flush=True)
                return None
            
            if strategy1.frontier_empty():
                print('Strategy1 frontier empty.', file=sys.stderr, flush=True)
                return None
            
            if strategy2.frontier_empty():
                print('Strategy2 frontier empty.', file=sys.stderr, flush=True)
                return None
            
            leaf1 = strategy1.get_and_remove_leaf()            
            leaf2 = strategy2.get_and_remove_leaf()
            
            if leaf1 == leaf2:
                first_half = leaf1.extract_plan()
                second_half = leaf2.extract_plan()
                
                print("First half", file=sys.stderr, flush=True)
    
                for state in [self.initial_state] + first_half:
                    print(state.action, file=sys.stderr, flush=True)
                    for i in range(len(state.boxes)):
                        for j in range(len(state.boxes[i])):
                            if state.boxes[i][j] is not None:
                                print('agent(%d, %d) box(%d, %d)' % (state.agent_row, state.agent_col, i, j), file=sys.stderr, flush=True)
                                break
                        if state.boxes[i][j] is not None:
                            break
                
                second_half.reverse()
                
                for state in second_half:
                    for i in range(len(state.boxes)):
                        for j in range(len(state.boxes[i])):
                            if state.boxes[i][j] is not None:
                                print('agent(%d, %d) box(%d, %d)' % (state.agent_row, state.agent_col, i, j), file=sys.stderr, flush=True)
                                break
                        if state.boxes[i][j] is not None:
                            break
                
                for i in range(1, len(second_half)):
                    second_half[i].parent = second_half[i-1]
                    second_half[i].action = second_half[i].action.get_inverse()
                    
                solution = first_half + second_half
                
                #for state in solution:
                #    print(state.action, file=sys.stderr, flush=None)
                
                print('Solution found.', file=sys.stderr, flush=True)
                print(second_half[-1].agent_row, second_half[-1].agent_col, file=sys.stderr, flush=True)
                return solution
            
            strategy1.add_to_explored(leaf1)
            strategy2.add_to_explored(leaf2)
            
            for child_state in leaf1.get_children(): # The list of expanded states is shuffled randomly; see state.py.
                if not strategy1.is_explored(child_state) and not strategy1.in_frontier(child_state):
                    strategy1.add_to_frontier(child_state)
                    
            for child_state in leaf2.get_children(): # The list of expanded states is shuffled randomly; see state.py.
                if not strategy2.is_explored(child_state) and not strategy2.in_frontier(child_state):
                    strategy2.add_to_frontier(child_state)
            
            iterations += 1


def main(strategy_str: 'str'):
    # Read server messages from stdin.
    server_messages = sys.stdin
    
    # Use stderr to print to console through server.
    print('SearchClient initializing. I am sending this using the error output stream.', file=sys.stderr, flush=True)
    
    # Read level and create the initial state of the problem.
    client = SearchClient(server_messages);

    strategy = None
    if strategy_str == 'bfs':
        strategy = StrategyBFS()
    elif strategy_str == 'dfs':
        strategy = StrategyDFS()
    elif strategy_str == 'astar':
        strategy = StrategyBestFirst(AStar(client.initial_state))
    elif strategy_str == 'wastar':
        strategy = StrategyBestFirst(WAStar(client.initial_state, 5))
    elif strategy_str == 'greedy':
        strategy = StrategyBestFirst(Greedy(client.initial_state))
    else:
        # Default to BFS strategy.
        strategy = StrategyBFS()
        print('Defaulting to BFS search. Use arguments -bfs, -dfs, -astar, -wastar, or -greedy to set the search strategy.', file=sys.stderr, flush=True)

    if strategy_str == 'bi':
        solution = client.bi_search(strategy, StrategyBFS())
    else:
        solution = client.search(strategy)
        
    if solution is None:
        print(strategy.search_status(), file=sys.stderr, flush=True)
        print('Unable to solve level.', file=sys.stderr, flush=True)
        sys.exit(0)
    else:
        print('\nSummary for {}.'.format(strategy), file=sys.stderr, flush=True)
        print('Found solution of length {}.'.format(len(solution)), file=sys.stderr, flush=True)
        print('{}.'.format(strategy.search_status()), file=sys.stderr, flush=True)
        
        for state in solution:
            print(state.action, flush=True)
            response = server_messages.readline().rstrip()
            if 'false' in response:
                print('Server responsed with "{}" to the action "{}" applied in:\n{}\n'.format(response, state.action, state), file=sys.stderr, flush=True)
                break


if __name__ == '__main__':
    # Program arguments.
    parser = argparse.ArgumentParser(description='Simple client based on state-space graph search.')
    parser.add_argument('--max-memory', metavar='<MB>', type=float, default=2048.0, help='The maximum memory usage allowed in MB (soft limit, default 2048).')
    
    strategy_group = parser.add_mutually_exclusive_group()
    strategy_group.add_argument('-bfs', action='store_const', dest='strategy', const='bfs', help='Use the BFS strategy.')
    strategy_group.add_argument('-dfs', action='store_const', dest='strategy', const='dfs', help='Use the DFS strategy.')
    strategy_group.add_argument('-astar', action='store_const', dest='strategy', const='astar', help='Use the A* strategy.')
    strategy_group.add_argument('-wastar', action='store_const', dest='strategy', const='wastar', help='Use the WA* strategy.')
    strategy_group.add_argument('-greedy', action='store_const', dest='strategy', const='greedy', help='Use the Greedy strategy.')
    strategy_group.add_argument('-bi', action='store_const', dest='strategy', const='bi', help='Use the Bidirectional strategy.')
    
    args = parser.parse_args()
    
    # Set max memory usage allowed (soft limit).
    memory.max_usage = args.max_memory
    
    # Run client.
    main(args.strategy)

