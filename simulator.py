"""
simulator.py
------------
Simulates input strings on both the DFA and NFA.

Student : Amna Khurram
ID      : F24605061 | CS 2024-B
Instructor: Naveed Yousaf
"""

from __future__ import annotations
from typing import List, Tuple, Set
from nfa import NFA, State, EPSILON
from dfa import DFA, epsilon_closure, move


# ---------------------------------------------------------------------------
# DFA Simulation
# ---------------------------------------------------------------------------
def simulate_dfa(dfa: DFA, input_string: str) -> Tuple[bool, List[str]]:
    """
    Simulate `input_string` on `dfa`.

    Returns
    -------
    (accepted: bool, path: list of DFA state names visited)
    """
    if dfa.start_state is None:
        return False, []

    current = dfa.start_state
    path    = [current.name]

    for ch in input_string:
        transitions = dfa.transition_table.get(current.name, {})
        next_name   = transitions.get(ch, "∅")
        if next_name == "∅":
            return False, path + ["∅ (dead)"]
        # Find DFAState by name
        next_state = next((s for s in dfa.states if s.name == next_name), None)
        if next_state is None:
            return False, path + ["∅ (dead)"]
        current = next_state
        path.append(current.name)

    accepted = current.is_accept
    return accepted, path


# ---------------------------------------------------------------------------
# NFA Simulation (via ε-closure / move)
# ---------------------------------------------------------------------------
def simulate_nfa(nfa: NFA, input_string: str) -> Tuple[bool, List[Set[str]]]:
    """
    Simulate `input_string` on `nfa` using the subset-based approach.

    Returns
    -------
    (accepted: bool, path: list of state-set snapshots after each symbol)
    """
    current_states = epsilon_closure({nfa.start_state})
    path = [_state_set_str(current_states)]

    for ch in input_string:
        next_states = epsilon_closure(move(set(current_states), ch))
        path.append(_state_set_str(next_states))
        current_states = next_states
        if not current_states:
            return False, path

    accepted = any(s in nfa.accept_states for s in current_states)
    return accepted, path


def _state_set_str(states) -> str:
    ids = sorted(s.id for s in states)
    return "{" + ",".join(f"q{i}" for i in ids) + "}"


# ---------------------------------------------------------------------------
# Batch test runner (returns list of result dicts)
# ---------------------------------------------------------------------------
def batch_test(dfa: DFA, nfa: NFA, test_strings: List[str]) -> List[dict]:
    """
    Run a list of strings through both DFA and NFA simulators and
    return a list of result dictionaries.
    """
    results = []
    for s in test_strings:
        dfa_acc, dfa_path = simulate_dfa(dfa, s)
        nfa_acc, nfa_path = simulate_nfa(nfa, s)
        results.append({
            "string":       s if s else "ε (empty)",
            "dfa_accepted": dfa_acc,
            "nfa_accepted": nfa_acc,
            "dfa_path":     " → ".join(dfa_path),
            "nfa_path":     " → ".join(nfa_path),
        })
    return results


# ---------------------------------------------------------------------------
# Pre-defined test cases for (a|b)*abb
# ---------------------------------------------------------------------------
ACCEPTED_STRINGS = ["abb", "aabb", "babb", "ababb", "bbabb"]
REJECTED_STRINGS = ["ab",  "ba",   "abc",  "aba",   ""]


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    from regex_parser import to_postfix
    from nfa import build_nfa
    from dfa import build_dfa

    regex   = '(a|b)*abb'
    nfa     = build_nfa(to_postfix(regex))
    dfa     = build_dfa(nfa)

    print("=== ACCEPTED strings ===")
    for s in ACCEPTED_STRINGS:
        ok, path = simulate_dfa(dfa, s)
        print(f"  '{s}':  {'ACCEPT' if ok else 'REJECT'}  path={path}")

    print("\n=== REJECTED strings ===")
    for s in REJECTED_STRINGS:
        ok, path = simulate_dfa(dfa, s)
        print(f"  '{s}':  {'ACCEPT' if ok else 'REJECT'}  path={path}")
