"""
main.py
-------
Entry point for the RE → NFA → DFA Converter & Simulator.

Student    : Amna Khurram
ID         : F24605061 | CS 2024-B
Instructor : Naveed Yousaf

Usage
-----
  python main.py            # Launch GUI (default)
  python main.py --cli      # Run CLI demo only
"""

from __future__ import annotations
import argparse
import sys


# ---------------------------------------------------------------------------
# CLI Demo (no GUI needed)
# ---------------------------------------------------------------------------
def run_cli():
    from regex_parser import to_postfix
    from nfa          import build_nfa
    from dfa          import build_dfa
    from simulator    import simulate_dfa, simulate_nfa, ACCEPTED_STRINGS, REJECTED_STRINGS

    regex   = '(a|b)*abb'
    print("=" * 60)
    print("  RE → NFA → DFA Converter  |  Amna Khurram  F24605061")
    print("=" * 60)
    print(f"\nRegex   : {regex}")

    postfix = to_postfix(regex)
    print(f"Postfix : {postfix}")

    nfa = build_nfa(postfix)
    print(f"\nNFA States    : {nfa.state_names()}")
    print(f"NFA Start     : q{nfa.start_state.id}")
    print(f"NFA Accept    : {[str(s) for s in nfa.accept_states]}")
    print(f"Alphabet      : {sorted(nfa.alphabet)}")
    print()
    nfa.print_table()

    dfa = build_dfa(nfa)
    print(f"\nDFA States    : {[s.name for s in dfa.states]}")
    print(f"DFA Start     : {dfa.start_state.name}")
    print(f"DFA Accept    : {[s.name for s in dfa.accept_states]}")
    print()
    dfa.print_table()

    print("\n=== ACCEPTED strings ===")
    for s in ACCEPTED_STRINGS:
        ok, path = simulate_dfa(dfa, s)
        label    = "ACCEPT ✓" if ok else "REJECT ✗"
        print(f"  '{s}':  {label}  path: {' → '.join(path)}")

    print("\n=== REJECTED strings ===")
    for s in REJECTED_STRINGS:
        ok, path = simulate_dfa(dfa, s)
        label    = "ACCEPT ✓" if ok else "REJECT ✗"
        print(f"  '{s or 'ε'}':  {label}  path: {' → '.join(path)}")


# ---------------------------------------------------------------------------
# GUI Entry
# ---------------------------------------------------------------------------
def run_gui():
    from gui import run_gui as _run
    _run()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="RE → NFA → DFA Converter & Simulator"
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="Run command-line demo instead of opening the GUI"
    )
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()
