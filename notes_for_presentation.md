## Client optimization
- Levels represented as a graph data structure
- Orders of magnitude less memory usage

## Heuristic
- Goal-box and agent-box assignments done by Hungarian algorithm
- Assignments minimize BFS-calculated cityblock move/push distances
- Heuristic consists of 5 differently weighted metrics:
  - Distance between assigned goal and boxes
  - Distance between assigned agents and boxes
  - Punishment for boxes being pushed out of their goals
  - Punishment for the movement of unallocated agents
  - Punishment for the presence of unallocated boxes
- Reallocation takes place at the beginning and at each time whenever a box is pushed to its goal

## Conflict detection
- ???