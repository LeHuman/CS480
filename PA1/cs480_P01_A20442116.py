import argparse
from dataclasses import dataclass, field
from queue import PriorityQueue
from timeit import timeit

import pandas as pd

INITIAL_STATE = GOAL_STATE = 'NIL'
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


@dataclass(order=True)
class entry:
    h_cost: int = field(compare=True)  # Heuristic
    cost: int = field(compare=False)  # Path cost
    curr_node: node = field(compare=False)  # Current node
    pre_entry: object | None = field(compare=False)  # Previous node
    a_cost: int = field(compare=False)


def run_greedy(initial: str, goal: str, As: bool = False) -> tuple[int, list[node]]:
    initial_state = get_node(initial)
    goal_state = get_node(goal)
    frontier: PriorityQueue[entry] = PriorityQueue()

    def getDistance(nod: node):
        if nod.name not in goal_state.dists:
            return -1
        return goal_state.dists[nod.name]

    reached: dict[str, entry] = {initial_state.name: entry(getDistance(initial_state), 0, initial_state, None, 0)}  # (hubristic cost, cost, node)
    visited_le: list[entry] = []
    frontier.put(reached[initial_state.name])
    while not frontier.empty():
        curr_entry = frontier.get()
        if curr_entry.h_cost < 0:
            return (0, [])
        visited_le.append(curr_entry)
        if curr_entry.curr_node is goal_state:
            break
        for name, cost in curr_entry.curr_node.edges.items():
            n = get_node(name)
            a_cost = cost + curr_entry.a_cost
            h = getDistance(n) + (a_cost if As else 0)
            node_o = entry(h, cost, n, curr_entry, a_cost)
            if name not in reached or node_o.h_cost < reached[name].h_cost:  # check for less than last visit?
                reached[name] = node_o
                frontier.put(node_o)
    total_cost = 0
    path = []
    back: entry = visited_le[-1]
    while back:
        path.append(back.curr_node)
        total_cost += back.cost
        back = back.pre_entry
    return (total_cost, path[::-1])


def gen_graph(df: pd.DataFrame, neighbors: bool):
    for i, s in df.iloc[:, 1:].items():
        s = pd.concat([df[df.columns[0]], s], axis=1)
        s = s[s[s.columns[1]] > 0]
        nd = get_node(i)
        for i, v in s.iterrows():
            nd.connect(get_node(v[0]), v[1], neighbors)


def test(command: str, iterations: int) -> tuple[str, int, int, int]:
    avg_time = timeit(command, globals=globals(), number=iterations) / iterations / 0.000001
    cost, path = eval(command)
    p_len = len(path)
    path = ", ".join([str(x) for x in path])
    return path if path else "FAILURE: NO PATH FOUND", p_len, cost, round(avg_time, 2)


def full_test(iterations: int):
    print(f"Rivera, Isaias, A20442116 solution:\nInital state: {INITIAL_STATE}\nGoal state: {GOAL_STATE}")

    results = test('run_greedy(INITIAL_STATE, GOAL_STATE)', iterations)
    print(f"""
Greedy Best First Search
Solution path: {results[0]}
Number of states on a path: {results[1]}
Path cost: {results[2]}
Execution time: {results[3]} μs""")

    results = test('run_greedy(INITIAL_STATE, GOAL_STATE, True)', iterations)
    print(f"""
A* Search
Solution path: {results[0]}
Number of states on a path: {results[1]}
Path cost: {results[2]}
Execution time: {results[3]} μs""")


def main() -> None:
    global INITIAL_STATE, GOAL_STATE
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('initial_state', metavar="Initial State", type=str, nargs=1, help='The state that we should start at')
    parser.add_argument('goal_state', metavar="Goal State", type=str, nargs=1, help='The state that we should end at')
    parser.add_argument('-i', '--iterations', metavar="Iterations", required=False, type=int, default=1, help='Number of times to repeat for an avg. runtime')

    test_iterations = 1

    try:
        args = parser.parse_args()
        INITIAL_STATE = args.initial_state[0]
        GOAL_STATE = args.goal_state[0]
        test_iterations = 100000 if args.iterations < 0 else args.iterations
    except (SystemExit, argparse.ArgumentError):
        exit('\nERROR: Not enough or too many input arguments.')

    driving_frame: pd.DataFrame = pd.read_csv("driving.csv").convert_dtypes(int)
    straight_frame: pd.DataFrame = pd.read_csv("straightline.csv").convert_dtypes(int)

    gen_graph(driving_frame, True)
    gen_graph(straight_frame, False)

    full_test(test_iterations)


if __name__ == "__main__":
    main()
