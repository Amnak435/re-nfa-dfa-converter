"""
nfa.py
------
Thompson's Construction Algorithm:
Builds an NFA (Non-deterministic Finite Automaton) from a postfix regular
expression produced by regex_parser.to_postfix().

Student : Amna Khurram
ID      : F24605061 | CS 2024-B
Instructor: Naveed Yousaf

Each NFA fragment has:
  - A single start state
  - A single accept state
  - ε-transitions represented by the key EPSILON = 'ε'
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple

EPSILON = 'ε'   # ε-transition label used throughout the project


# ---------------------------------------------------------------------------
# State class
# ---------------------------------------------------------------------------
class State:
    """A single NFA state."""

    _counter = 0  # class-level counter for unique IDs

    def __init__(self):
        self.id: int = State._counter
        State._counter += 1
        # transitions: symbol → list of target states
        self.transitions: Dict[str, List['State']] = {}
        self.is_accept: bool = False

    def add_transition(self, symbol: str, target: 'State'):
        self.transitions.setdefault(symbol, []).append(target)

    def __repr__(self):
        return f"q{self.id}"


# ---------------------------------------------------------------------------
# NFA Fragment (a pair of start / accept states + all interior states)
# ---------------------------------------------------------------------------
class NFAFragment:
    """Minimal NFA fragment produced by one Thompson construction step."""

    def __init__(self, start: State, accept: State):
        self.start  = start
        self.accept = accept


# ---------------------------------------------------------------------------
# Thompson construction primitives
# ---------------------------------------------------------------------------
def _symbol(ch: str) -> NFAFragment:
    """
    Base case: NFA for a single literal character.
        q_start --ch--> q_accept
    """
    s = State()
    a = State()
    a.is_accept = True
    s.add_transition(ch, a)
    return NFAFragment(s, a)


def _concat(f1: NFAFragment, f2: NFAFragment) -> NFAFragment:
    """
    Concatenation: f1 followed by f2.
    Connect f1's accept to f2's start via ε.
    """
    f1.accept.is_accept = False
    f1.accept.add_transition(EPSILON, f2.start)
    return NFAFragment(f1.start, f2.accept)


def _union(f1: NFAFragment, f2: NFAFragment) -> NFAFragment:
    """
    Union (alternation): f1 | f2.
    New start branches to both; both accepts merge into new accept.
    """
    s = State()
    a = State()
    a.is_accept = True

    f1.accept.is_accept = False
    f2.accept.is_accept = False

    s.add_transition(EPSILON, f1.start)
    s.add_transition(EPSILON, f2.start)
    f1.accept.add_transition(EPSILON, a)
    f2.accept.add_transition(EPSILON, a)

    return NFAFragment(s, a)


def _kleene_star(f: NFAFragment) -> NFAFragment:
    """
    Kleene star: f*.
    New start → f.start (ε), f.accept → f.start (ε), new start → new accept (ε).
    """
    s = State()
    a = State()
    a.is_accept = True

    f.accept.is_accept = False
    s.add_transition(EPSILON, f.start)
    s.add_transition(EPSILON, a)           # zero repetitions
    f.accept.add_transition(EPSILON, f.start)  # loop back
    f.accept.add_transition(EPSILON, a)    # exit loop

    return NFAFragment(s, a)


def _one_or_more(f: NFAFragment) -> NFAFragment:
    """One-or-more: f+  =  f · f* """
    import copy
    # We build  f · (f)*  by reusing _kleene_star on a duplicate fragment.
    # Because states are mutable objects we simply build a second NFA fragment
    # for the repeated part via another Thompson pass on the same symbol tree.
    # Simpler approach: chain original fragment with a Kleene-star copy.
    f_star = _kleene_star(_symbol_copy(f))
    return _concat(f, f_star)


def _symbol_copy(f: NFAFragment) -> NFAFragment:
    """Return a structurally identical but independently-numbered copy of f."""
    # Walk all reachable states and duplicate them
    old_to_new: Dict[State, State] = {}

    def copy_state(st: State) -> State:
        if st in old_to_new:
            return old_to_new[st]
        new_st = State()
        new_st.is_accept = st.is_accept
        old_to_new[st] = new_st
        for sym, targets in st.transitions.items():
            for t in targets:
                new_st.add_transition(sym, copy_state(t))
        return new_st

    new_start  = copy_state(f.start)
    new_accept = old_to_new[f.accept]
    return NFAFragment(new_start, new_accept)


def _zero_or_one(f: NFAFragment) -> NFAFragment:
    """Zero-or-one: f? = f | ε """
    s = State()
    a = State()
    a.is_accept = True

    f.accept.is_accept = False
    s.add_transition(EPSILON, f.start)
    s.add_transition(EPSILON, a)   # skip (zero occurrences)
    f.accept.add_transition(EPSILON, a)

    return NFAFragment(s, a)


# ---------------------------------------------------------------------------
# Main builder: postfix → NFA
# ---------------------------------------------------------------------------
def build_nfa(postfix: str) -> 'NFA':
    """
    Convert a postfix regex string to an NFA using Thompson's construction.
    Returns an NFA object.
    """
    # Reset state counter for reproducibility
    State._counter = 0

    stack: List[NFAFragment] = []

    for ch in postfix:
        if ch == '.':
            f2 = stack.pop()
            f1 = stack.pop()
            stack.append(_concat(f1, f2))

        elif ch == '|':
            f2 = stack.pop()
            f1 = stack.pop()
            stack.append(_union(f1, f2))

        elif ch == '*':
            f = stack.pop()
            stack.append(_kleene_star(f))

        elif ch == '+':
            f = stack.pop()
            stack.append(_one_or_more(f))

        elif ch == '?':
            f = stack.pop()
            stack.append(_zero_or_one(f))

        else:
            # Literal character
            stack.append(_symbol(ch))

    if len(stack) != 1:
        raise ValueError("Invalid postfix expression – stack not fully reduced.")

    fragment = stack[0]
    return NFA(fragment)


# ---------------------------------------------------------------------------
# NFA wrapper (collects all reachable states and builds transition table)
# ---------------------------------------------------------------------------
class NFA:
    """
    Wraps an NFAFragment and exposes:
      - states        : ordered list of all reachable State objects
      - alphabet      : set of non-epsilon symbols
      - start_state   : the initial state
      - accept_states : set of accepting states
      - transition_table : dict  state_id → symbol → [state_ids]
    """

    def __init__(self, fragment: NFAFragment):
        self.start_state  = fragment.start
        self.accept_states: Set[State] = set()

        # BFS/DFS to collect all reachable states
        visited: Set[State] = set()
        order:   List[State] = []
        stack = [fragment.start]
        while stack:
            st = stack.pop()
            if st in visited:
                continue
            visited.add(st)
            order.append(st)
            if st.is_accept:
                self.accept_states.add(st)
            for targets in st.transitions.values():
                for t in targets:
                    if t not in visited:
                        stack.append(t)

        # Sort by state ID for deterministic ordering
        self.states: List[State] = sorted(order, key=lambda s: s.id)
        self.alphabet: Set[str] = set()
        for st in self.states:
            for sym in st.transitions:
                if sym != EPSILON:
                    self.alphabet.add(sym)

        # Build transition table: {state_id: {symbol: [state_ids]}}
        self.transition_table: Dict[int, Dict[str, List[int]]] = {}
        for st in self.states:
            self.transition_table[st.id] = {}
            for sym, targets in st.transitions.items():
                self.transition_table[st.id][sym] = [t.id for t in targets]

    # ------------------------------------------------------------------ #
    # Pretty-print helpers
    # ------------------------------------------------------------------ #
    def state_names(self) -> List[str]:
        return [f"q{s.id}" for s in self.states]

    def print_table(self):
        symbols = sorted(self.alphabet) + [EPSILON]
        header  = f"{'State':>8} | " + " | ".join(f"{sym:^12}" for sym in symbols)
        print(header)
        print("-" * len(header))
        for st in self.states:
            row = f"{'→q'+str(st.id) if st == self.start_state else 'q'+str(st.id):>8} | "
            for sym in symbols:
                targets = self.transition_table[st.id].get(sym, [])
                cell    = "{" + ",".join(f"q{t}" for t in targets) + "}" if targets else "∅"
                row    += f"{cell:^12} | "
            marker = " *" if st in self.accept_states else ""
            print(row + marker)


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    from regex_parser import to_postfix
    regex   = '(a|b)*abb'
    postfix = to_postfix(regex)
    print(f"Regex  : {regex}")
    print(f"Postfix: {postfix}")
    print()
    nfa = build_nfa(postfix)
    print(f"States      : {nfa.state_names()}")
    print(f"Alphabet    : {sorted(nfa.alphabet)}")
    print(f"Start state : q{nfa.start_state.id}")
    print(f"Accept states: {[str(s) for s in nfa.accept_states]}")
    print()
    nfa.print_table()
