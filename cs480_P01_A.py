import argparse
from genericpath import exists
from typing import Dict
import pandas as pd
import pickle

MEMO_PKL = "map.pkl"
MEMO = {}


def get_node(df: pd.DataFrame, state: str, memo: Dict[str, pd.DataFrame] = MEMO) -> pd.DataFrame:
    if state in memo:
        return memo[state]
    nodes = df[["STATE", state]]
    nodes = nodes[nodes[state] != -1]
    nodes = nodes[nodes["STATE"] != state]
    nodes.sort_values(by=[state], inplace=True)
    memo[state] = nodes
    return nodes


def run_greedy(df: pd.DataFrame, initial: str, goal: str) -> None:
    print(get_node(df, initial))


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Process some integers.')
    parser.add_argument('initial_state', metavar='INITIAL',
                        type=str, nargs=1, help='The state that we should start at')
    parser.add_argument('goal_state', metavar='GOAL', type=str,
                        nargs=1, help='The state that we should end at')

    args = parser.parse_args()
    # print('ERROR: Not enough or too many input arguments.')
    df = pd.read_csv("driving.csv")
    sf = pd.read_csv("straightline.csv")
    df = (pd.concat([df, sf]).stack().groupby(
        level=[0, 1]).apply(tuple).unstack())

    global MEMO
    try:
        with open(MEMO_PKL, 'rb') as f:
            MEMO = pickle.load(f)
    except:
        pass

    run_greedy(df, args.initial_state[0], args.goal_state[0])

    with open(MEMO_PKL, 'wb') as f:
        pickle.dump(MEMO, f)


if __name__ == "__main__":
    main()
