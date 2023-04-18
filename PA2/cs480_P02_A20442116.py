"""CS480 - Fall 2022 - PA3"""

import argparse
from dataclasses import dataclass, field

import pandas as pd

INITIAL_STATE = 'NIL'
PARK_GOAL = 0
DMEMO: dict[str, object] = {}


@dataclass(order=True)
class node():
    name: str = field(compare=True)
    zone: int = field(compare=False)
    parks: int = field(compare=False)
    edges: dict[str, int] = field(compare=False)
    neighbors: set = field(compare=False)

    def __init__(self, name: str) -> None:
        self.name = name
        self.edges = {}
        self.neighbors = set()

    def connect(self, node_o, dist: int) -> None:
        self.edges[node_o.name] = dist
        self.neighbors.add(node_o.name)

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)


def get_node(name: str) -> node:
    if name in DMEMO:
        return DMEMO[name]
    DMEMO[name] = node(name)
    return DMEMO[name]


ZONES: dict[int, set[node]] = {}


def set_node_aux(name: str, zone: int, parks: int) -> None:
    if zone not in ZONES:
        ZONES[zone] = set()
    nd = get_node(name)
    nd.parks = parks
    nd.zone = zone
    ZONES[zone].add(nd.name)


def gen_graph(df: pd.DataFrame):
    for i, s in df.iloc[:, 1:].items():
        s = pd.concat([df[df.columns[0]], s], axis=1)
        s = s[s[s.columns[1]] > 0]
        nd = get_node(i)
        for _, v in s.iterrows():
            nd.connect(get_node(v[0]), v[1])


def backtrack(initial: str, park_goal: int, zones: dict[int, set[node]] = ZONES, path: list[node] = [], total_parks: int = 0) -> tuple[list[node], int]:
    curr_state = get_node(initial)
    path.append(curr_state)
    total_parks += curr_state.parks
    # print(f", {curr_state}", end='')
    if curr_state.zone+1 not in ZONES:
        return (path, total_parks)

    zone_copy = {x: set([z for z in y]) for x, y in zones.items()}
    next_zone = zone_copy[curr_state.zone+1]

    domain = list(next_zone.intersection(curr_state.neighbors))
    domain.sort()

    for state in domain:
        nd = get_node(state)
        if nd.zone+1 in ZONES or total_parks + nd.parks >= park_goal:
            res = backtrack(nd.name, park_goal, zone_copy, [x for x in path], total_parks)
            if res[0]:
                return res
        # print(f"\nX:{state} → {curr_state.name}", end='')
        next_zone.remove(state)

    return ([], total_parks)


def test() -> None:
    print(f"Rivera, Isaias, A20442116 solution:\nInital state: {INITIAL_STATE}\nMinimum number of parks: {PARK_GOAL}")

    path, parks = backtrack(INITIAL_STATE, PARK_GOAL)
    cnt = len(path)
    cost = 0

    if path:
        last = path[0]
        for s in path[1:]:
            cost += last.edges[s.name]
            last = s
    else:
        path = "FAILURE: NO PATH FOUND"
        parks = 0

    print(f"""
Solution path: {path}
Number of states on a path: {cnt}
Path cost: {cost}
Number of national parks visited: {parks}""")


def main() -> None:
    global INITIAL_STATE, PARK_GOAL
    parser = argparse.ArgumentParser(description='PA2')
    parser.add_argument('initial_state', metavar="Initial State", type=str, nargs=1, help='The state that we should start at')
    parser.add_argument('no_of_parks', metavar="Number of Parks", type=int, nargs=1, help='The number of parks to visit')

    try:
        args = parser.parse_args()
        INITIAL_STATE = args.initial_state[0]
        PARK_GOAL = int(args.no_of_parks[0])
    except (SystemExit, argparse.ArgumentError):
        exit('\nERROR: Not enough or too many input arguments.')

    driving_frame: pd.DataFrame = pd.read_csv("driving2.csv").convert_dtypes(int)
    zone_frame: pd.DataFrame = pd.read_csv("zones.csv").convert_dtypes(int)
    park_frame: pd.DataFrame = pd.read_csv("parks.csv").convert_dtypes(int)

    driving_frame = driving_frame.iloc[:, 1:].transpose()
    driving_frame.columns = driving_frame.index
    driving_frame = driving_frame.reset_index()

    gen_graph(driving_frame)

    for state in driving_frame.columns[1:]:
        set_node_aux(state, int(zone_frame[state][0]), int(park_frame[state][0]))

    test()


if __name__ == "__main__":
    main()
