import argparse
import pandas as pd
from queue import PriorityQueue


DMEMO: dict[str, object] = {}


class node():
    name: str = None
    edges: dict[str, int] = None
    dists: dict[str, int] = None

    def __init__(self, name: str) -> None:
        self.name = name
        self.edges = {}
        self.dists = {name: 0}

    def connect(self, node_o, dist: int, isNeighbor: bool) -> None:
        self.dists[node_o.name] = dist
        if isNeighbor:
            self.edges[node_o.name] = dist

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self)


def get_node(name: str) -> node:
    if name in DMEMO:
        return DMEMO[name]
    DMEMO[name] = node(name)
    return DMEMO[name]


# def best_first_search(problem, f):
#     node = Node(problem.initial)
#     frontier = PriorityQueue([node], key=f)
#     reached = {problem.initial: node}
#     while frontier:
#         node = frontier.pop()
#         if problem.is_goal(node.state):
#             return node
#         for child in expand(problem, node):
#             s = child.state
#             if s not in reached or child.path_cost < reached[s].path_cost:
#                 reached[s] = child
#                 frontier.add(child)
#     return failure


def run_greedy(initial: str, goal: str) -> tuple[int, list[node]]:
    initial_state = get_node(initial)
    goal_state = get_node(goal)
    queue = PriorityQueue()
    visited_e: dict[str, tuple[int, int, node]] = {}
    explored_e: dict[str, tuple[int, int, node]] = {}
    visited_le: list[node] = list()
    cost = 0
    visited_e[initial_state.name] = (initial_state.dists[goal_state.name], 0, initial_state)
    explored_e[initial_state.name] = visited_e[initial_state.name]
    queue.put(visited_e[initial_state.name])
    while not queue.empty():
        curr_node: node = queue.get()[2]
        visited_le.append(curr_node)
        if curr_node is goal_state:
            break
        for name, dist in curr_node.edges.items():
            h = goal_state.dists[name] + dist
            node_o = (h, dist, get_node(name))
            if name not in visited_e or h < explored_e[name][0]:  # check for less than last visit?
                visited_e[name] = node_o
                queue.put(node_o)
                explored_e[name] = node_o
    cost = sum(visited_e[k.name][1] for k in visited_le)
    return (cost, visited_le)


def gen_graph(df: pd.DataFrame, neighbors: bool):
    for i, s in df.iloc[:, 1:].items():
        s = pd.concat([df[df.columns[0]], s], axis=1)
        s = s[s[s.columns[1]] > 0]
        nd = get_node(i)
        for i, v in s.iterrows():
            nd.connect(get_node(v[0]), v[1], neighbors)


def main() -> None:
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('initial_state', metavar='INITIAL', type=str, nargs=1, help='The state that we should start at')
    parser.add_argument('goal_state', metavar='GOAL', type=str, nargs=1, help='The state that we should end at')

    try:
        args = parser.parse_args()
    except (SystemExit, argparse.ArgumentError):
        exit('\nERROR: Not enough or too many input arguments.')

    df: pd.DataFrame = pd.read_csv("driving.csv").convert_dtypes(int)
    sf: pd.DataFrame = pd.read_csv("straightline.csv").convert_dtypes(int)

    gen_graph(df, True)
    gen_graph(sf, False)

    cost, path = run_greedy(args.initial_state[0], args.goal_state[0])
    print(cost, ":", ", ".join([str(x) for x in path]))


if __name__ == "__main__":
    main()
