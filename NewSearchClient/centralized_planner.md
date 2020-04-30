# Centralized Planner Idea

## Naive approach...

### At the beginning:
1. Allocate a box to each of the goals (that also depends on letter!)
2. Assign an agent to each of the allocated boxes (that also depends on color!)
- Result: 
  - A list of box-goal allocations
  - A list of agent-box allocations

... These can be stored as class-level variables in the Heuristic class.

### At each heuristic calculation:
1. Recall result of the above operation
2. Calculate sum of box-goal distances from the box-goal allocation list
3. Calculate sum of agent-box distances from the agent-box allocation list
4. Sum the results of #2 and #3 to obtain a heuristic value
---
## Problems:

### What if there're less agents than boxes to be pushed?
Each time a box is pushed into a goal, a reallocation should follow. The planner should try to solve only a limited subset of the goals per reallocation.
