"""
dfa.py
------
Subset Construction Algorithm:
Converts an NFA (from nfa.py) to an equivalent DFA.

Student : Amna Khurram
ID      : F24605061 | CS 2024-B
Instructor: Naveed Yousaf

Key operations:
  epsilon_closure(states)  – set of states reachable via ε only
  move(states, symbol)     – set of states reachable on a symbol
  subset_construction()    – main algorithm
"""

from __future__ import annotations
from typing import Dict, FrozenSet, List, Set, Tuple
from nfa import NFA, State, EPSILON


# ---------------------------------------------------------------------------
# ε-closure and move
# ---------------------------------------------------------------------------
def epsilon_closure(states: Set[State]) -> FrozenSet[State]:
    """
    Return the ε-closure of a set of NFA states:
    all states reachable from `states` using only ε-transitions.
    """
    closure: Set[State] = set(states)
    stack = list(states)
    while stack:
        st = stack.pop()
        for target in st.transitions.get(EPSILON, []):
            if target not in closure:
                closure.add(target)
                stack.append(target)
    return frozenset(closure)


def move(states: Set[State], symbol: str) -> Set[State]:
    """
    Return the set of NFA states reachable from any state in `states`
    via exactly one `symbol` transition.
    """
    result: Set[State] = set()
    for st in states:
        for target in st.transitions.get(symbol, []):
            result.add(target)
    return result


# ---------------------------------------------------------------------------
# DFA State
# ---------------------------------------------------------------------------
class DFAState:
    """A single DFA state, representing a frozenset of NFA states."""

    _counter = 0

    def __init__(self, nfa_subset: FrozenSet[State], is_accept: bool):
        self.id         = DFAState._counter
        DFAState._counter += 1
        self.nfa_subset = nfa_subset
        self.is_accept  = is_accept
        self.name       = f"D{self.id}"

    def __repr__(self):
        ids = sorted(s.id for s in self.nfa_subset)
        return "{" + ",".join(f"q{i}" for i in ids) + "}"


# ---------------------------------------------------------------------------
# DFA
# ---------------------------------------------------------------------------
class DFA:
    """
    Result of the subset construction.

    Attributes
    ----------
    states           : list of DFAState (ordered by discovery)
    alphabet         : list of input symbols (sorted)
    start_state      : DFAState
    accept_states    : list of DFAState
    transition_table : dict  DFAState.name → symbol → DFAState.name
    """

    def __init__(self):
        DFAState._counter = 0
        self.states:        List[DFAState]       = []
        self.alphabet:      List[str]            = []
        self.start_state:   DFAState | None      = None
        self.accept_states: List[DFAState]       = []
        self.transition_table: Dict[str, Dict[str, str]] = {}

    # ------------------------------------------------------------------ #
    # Pretty-print helpers
    # ------------------------------------------------------------------ #
    def print_table(self):
        header = f"{'DFA State':>14} | NFA Subset                    | " + \
                 " | ".join(f"{sym:^8}" for sym in self.alphabet)
        print(header)
        print("-" * len(header))
        for ds in self.states:
            nfa_repr = repr(ds)
            prefix   = "→" if ds == self.start_state else " "
            prefix  += "*" if ds.is_accept else " "
            row = f"{prefix+ds.name:>14} | {nfa_repr:30s} | "
            for sym in self.alphabet:
                target = self.transition_table.get(ds.name, {}).get(sym, "∅")
                row   += f"{target:^8} | "
            print(row)


# ---------------------------------------------------------------------------
# Main conversion
# ---------------------------------------------------------------------------
def build_dfa(nfa: NFA) -> DFA:
    """
    Apply the subset construction to convert an NFA to a DFA.

    Returns a DFA object.
    """
    dfa      = DFA()
    alphabet = sorted(nfa.alphabet)
    dfa.alphabet = alphabet

    nfa_accept_ids = {s.id for s in nfa.accept_states}

    # Map frozenset(NFA states) → DFAState
    subset_map: Dict[FrozenSet[State], DFAState] = {}

    def make_dfa_state(subset: FrozenSet[State]) -> DFAState:
        is_acc = any(s.id in nfa_accept_ids for s in subset)
        ds     = DFAState(subset, is_acc)
        dfa.states.append(ds)
        if ds.is_accept:
            dfa.accept_states.append(ds)
        return ds

    # Start state = ε-closure of NFA start
    start_closure = epsilon_closure({nfa.start_state})
    start_ds      = make_dfa_state(start_closure)
    dfa.start_state = start_ds
    subset_map[start_closure] = start_ds

    # Worklist / BFS
    worklist = [start_ds]
    while worklist:
        current_ds = worklist.pop(0)
        dfa.transition_table[current_ds.name] = {}

        for sym in alphabet:
            # move + ε-closure
            moved   = move(set(current_ds.nfa_subset), sym)
            closure = epsilon_closure(moved)

            if not closure:
                # Dead / sink state not added (represented as "∅")
                dfa.transition_table[current_ds.name][sym] = "∅"
                continue

            if closure not in subset_map:
                new_ds = make_dfa_state(closure)
                subset_map[closure] = new_ds
                worklist.append(new_ds)

            target_ds = subset_map[closure]
            dfa.transition_table[current_ds.name][sym] = target_ds.name

    return dfa


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    from regex_parser import to_postfix
    from nfa import build_nfa

    regex   = '(a|b)*abb'
    nfa     = build_nfa(to_postfix(regex))
    dfa     = build_dfa(nfa)

    print(f"DFA States      : {[s.name for s in dfa.states]}")
    print(f"DFA Start       : {dfa.start_state.name}")
    print(f"DFA Accept states: {[s.name for s in dfa.accept_states]}")
    print()
    dfa.print_table()
