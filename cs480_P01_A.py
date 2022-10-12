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

    def __str__(self) -> str:
        return f"{str(self.state)}:{str(self.val)}"


class node():
    uid: str = None
    edges: list[edge] = None

    def __init__(self, uid) -> None:
        self.priority = 0
        self.uid = uid
        self.edges = list()

    def connect(self, neighbor, value) -> None:
        self.edges.append(edge(neighbor, value))
        self.edges.sort()

    def __hash__(self):
        return hash(self.uid)

    def __str__(self) -> str:
        return str(self.uid)

    def __repr__(self) -> str:
        return f"{self.uid}"  # :{[str(x) for x in self.edges]}


DMEMO: dict[str, node] = {}
SMEMO: dict[str, node] = {}


def get_dnode(state: str) -> node:
    global DMEMO
    return DMEMO[state]


def get_snode(state: str) -> node:
    global SMEMO
    return SMEMO[state]


def run_greedy(initial: str, goal: str) -> set[node]:
    initial_state = get_dnode(initial)
    goal_state = get_dnode(goal)
    queue = PriorityQueue()
    visited: set[node] = set()
    queue.put(edge(initial_state, 0))
    while not queue.empty():
        curr_state: node = queue.get().state
        if curr_state in visited:
            continue
        if curr_state is goal_state:
            # print(f"done {goal_state}")
            break
        visited.add(curr_state)
        # print(curr_state)
        for edg in curr_state.edges:
            # print("\t", edg)
            if edg.state not in visited:
                queue.put(edg)
    return visited


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

    df_i = df[df.columns[0]]
    sf_i = sf[sf.columns[0]]

    global DMEMO
    global SMEMO
    gen_graph(df, DMEMO)
    gen_graph(sf, SMEMO)

    # for i, v in df.iterrows():
    #     i = 0
    #     nd = get_node(str(v[0]), DMEMO)
    #     for x in v[1:]:
    #         if x > 0:
    #             nd.connect(get_node(df_i[i], DMEMO), x)
    #         i += 1

    # global DMEMO
    # DMEMO = {str(v[1].iloc[0]): hlist(v[1].iloc[1:][v[1].iloc[1:] > 0].convert_dtypes(int).sort_values()).set_id(str(v[1].iloc[0])) for v in df.iterrows()}
    # global SMEMO
    # SMEMO = {str(v[1].iloc[0]): hlist(v[1].iloc[1:][v[1].iloc[1:] > 0].convert_dtypes(int).sort_values()).set_id(str(v[1].iloc[0])) for v in sf.iterrows()}

    # print(df)

    print(", ".join([str(x) for x in run_greedy(args.initial_state[0], args.goal_state[0])]))


if __name__ == "__main__":
    main()
