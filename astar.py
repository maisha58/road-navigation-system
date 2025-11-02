# astar.py

from graph_data import EDGES, NODES
import heapq

# ----------------- Find All Simple Paths -----------------
def all_paths(start, goal, path=[]):
    """
    Recursively finds all simple paths (no cycles) from start to goal.
    """
    path = path + [start]
    if start == goal:
        return [path]
    paths = []
    for neighbor in EDGES.get(start, {}):
        if neighbor not in path:
            newpaths = all_paths(neighbor, goal, path) # each neighbor ar all path ke recursivly call kore
            for p in newpaths:     # Add each new path found from recursion into the main paths list.
                paths.append(p)
    return paths # After checking all neighbors, return the list of all possible paths from start to goal

def path_distance(path):
    """
    Calculates total distance along a path using EDGES distances.
    """
    distance = 0
    for i in range(len(path)-1):
        distance += EDGES[path[i]][path[i+1]]
    return distance

# ----------------- A* Algorithm -----------------
def heuristic(node, goal):
    """
    Straight-line (Euclidean) distance heuristic using coordinates.
    """
    x1, y1 = NODES[node]
    x2, y2 = NODES[goal]
    return ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5

def a_star(start, goal):
    """
    Returns the optimal path from start to goal using A* search.
    """
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, [start]))
    visited = set()

    while open_set:
        f, g, current, path = heapq.heappop(open_set)

        if current == goal:
            return path

        if current in visited:
            continue
        visited.add(current)

        for neighbor, dist in EDGES.get(current, {}).items():
            if neighbor not in visited:
                new_g = g + dist # actual cost ,cost from start to this neighbor
                new_f = new_g + heuristic(neighbor, goal) 
                heapq.heappush(open_set, (new_f, new_g, neighbor, path + [neighbor]))

    return None  # No path found qeue theke sob pop hiye gese but goal akhono pai nai 

# ----------------- Example Usage -----------------
if __name__ == "__main__":
    start_node = "Rampura"
    goal_node = "Bashundhara"

    # All paths and shortest
    paths = all_paths(start_node, goal_node)
    if paths:
        optimal_path = min(paths, key=path_distance)
        print("All paths:", paths)
        print("Optimal path (shortest distance):", optimal_path)
        print("Distance:", path_distance(optimal_path))

    # A* search
    astar_path = a_star(start_node, goal_node)
    print("A* optimal path:", astar_path)
    if astar_path:
        print("A* path distance:", path_distance(astar_path))
