import argparse
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable
import pandas as pd
from queue import PriorityQueue


@dataclass(order=True)
class edge():
    val: int
    state: object = field(compare=False)

    def __init__(self, state: object, val: int) -> None:
        self.state = state
        self.val = val

    def __hash__(self):
        return hash(self.state)

    def __str__(self) -> str:
        return f"{str(self.state)}:{str(self.val)}"


class node():
    uid: str = None
    edges: list[edge] = None

    def __init__(self, uid) -> None:
        self.uid = uid
        self.edges = list()

    def connect(self, neighbor, value) -> None:
        self.edges.append(edge(neighbor, value))
        self.edges.sort()  # Helpful for visualize

    def __hash__(self):
        return hash(self.uid)

    def __str__(self) -> str:
        return str(self.uid)

    def __repr__(self) -> str:
        return f"{self.uid}:{[str(x) for x in self.edges]}"


DMEMO: dict[str, node] = {}
SMEMO: dict[str, node] = {}


def get_dnode(state: str) -> node:
    global DMEMO
    return DMEMO[state]


def get_snode(state: str) -> node:
    global SMEMO
    return SMEMO[state]

# Initial: MA | Goal: MD | Path: ['MA', 'NY', 'PA', 'MD']
# Path cost: 575 miles


def run_greedy(initial: str, goal: str) -> list[node]:
    initial_state = get_dnode(initial)
    goal_state = get_dnode(goal)
    goal_h = get_snode(goal_state.uid).edges
    queue = PriorityQueue()
    visited_e: dict[str, edge] = {}
    visited_le: list[edge] = list()
    queue.put(edge(initial_state, goal_h[initial_state.uid]))
    while not queue.empty():
        curr_edge: edge = queue.get()
        curr_state: node = curr_edge.state
        visited_e[curr_state.uid] = curr_edge
        visited_le.append(curr_edge)
        if curr_state is goal_state:
            break
        for next_edge in curr_state.edges:
            next_state_uid = next_edge.state.uid
            val = goal_h[next_state_uid] + next_edge.val
            if next_state_uid not in visited_e or val < visited_e[next_state_uid].val + goal_h[next_state_uid]:
                queue.put((val, next_edge))
                visited_e[next_state_uid] = next_edge
    return visited_le


def gen_graph(df: pd.DataFrame, memo: dict[str, node]):
    def get_node(key):
        if key in memo:
            return memo[key]
        memo[key] = node(key)
        return memo[key]

    for i, s in df.iloc[:, 1:].items():
        s = pd.concat([df[df.columns[0]], s], axis=1)
        s = s[s[s.columns[1]] > 0]
        nd = get_node(i)
        for i, v in s.iterrows():
            nd.connect(get_node(v[0]), v[1])


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

    global DMEMO
    global SMEMO
    gen_graph(df, DMEMO)
    gen_graph(sf, SMEMO)

    print(", ".join([str(x) for x in run_greedy(args.initial_state[0], args.goal_state[0])]))


if __name__ == "__main__":
    main()
