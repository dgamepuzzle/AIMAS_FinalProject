# Literature

## Overview articles

- [The most comprehensive paper on search algorithms, heuristics and pruning techniques, with speed comparisons](https://findit.dtu.dk/en/catalog/2261200197)

- [Sokoban wiki page, with very good problem visualizations and explanations](http://sokobano.de/wiki/index.php?title=Solver)

- [Short and shallow overview of search algorithms & pruning techniques](https://arxiv.org/pdf/1807.00049.pdf)

- [Another short overview of techniques](http://sokoban.dk/wp-content/uploads/2016/02/docslide.us_willy-a-sokoban-solving-agent.pdf)

---
## Articles on more specific topics

- [Relevance cuts (a graph pruning technique)](https://core.ac.uk/download/pdf/82273659.pdf)

---
## Other

- [Treasure trove of articles](http://sokoban.dk/science/)

# Techniques

## State space traversal

- **BFS, DFS, different iterations of A star**

- **Bidirectional search** - Instead of creating one very deep search tree, we grow two shallower trees starting out from the initial and the goal states. Since trees grow exponentially with the increase in depth, this could be a huge benefit.

## Heuristics

- **Free goals count** - Fast, but very inaccurate

- **L1, L2, etc (geometric) distance without walls** - More accurate, but still fails in more complex levels

- **Greedy heuristic** - Calculates the sum of distances between the boxes and the closest goals. There might be boxes that are assigned to the same goal, while some goals don't get assigned at all.

- **Minimum matching lower bound** - Assigns one goal to each of the boxes. Multiple algorithms exist, like the Hungarian algorithm. Complex and computationally intensive, might be overkill for easier levels, and unclear whether it works if there are more boxes than goals.

## Pruning

- **Tunnel detection** mostly useful in multi-agent setting.

- **Deadlock detection** (might be out of question, since we can pull boxes in our modified Sokoban domain - meaning that our actions are reversible.)





