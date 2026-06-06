"""
app.py
------
Streamlit Web App for RE → NFA → DFA Converter & Simulator
Student : Amna Khurram | F24605061 | CS 2024-B
Instructor: Naveed Yousaf
"""

import streamlit as st
from regex_parser import to_postfix
from nfa import build_nfa, EPSILON
from dfa import build_dfa
from simulator import simulate_dfa, simulate_nfa, batch_test, ACCEPTED_STRINGS, REJECTED_STRINGS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RE → NFA → DFA Converter",
    page_icon="🤖",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .stApp { background-color: #1E1E2E; color: #E2E8F0; }
    h1, h2, h3 { color: #7C3AED; }
    .accept { color: #22C55E; font-weight: bold; font-size: 1.3em; }
    .reject { color: #EF4444; font-weight: bold; font-size: 1.3em; }
    .info-box { background-color: #2A2A3E; padding: 15px; border-radius: 8px;
                border-left: 4px solid #7C3AED; margin: 10px 0; }
    .code-box { background-color: #0F0F1A; padding: 12px; border-radius: 6px;
                font-family: monospace; font-size: 0.85em; color: #9CDCFE; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🤖 Regular Expression → NFA → DFA Converter & Simulator")
st.markdown("**Amna Khurram | F24605061 | CS 2024-B | Instructor: Naveed Yousaf**")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Input")
    regex = st.text_input(
        "Enter Regular Expression",
        value="(a|b)*abb",
        help="Supported operators: | * + ? and grouping ()"
    )
    st.caption("Examples: `(a|b)*abb`  |  `a*b+`  |  `(ab)?c`")

    convert_btn = st.button("▶ Convert", type="primary", use_container_width=True)

    st.divider()
    st.markdown("## 🧪 Test a String")
    test_string = st.text_input("Input string (leave empty for ε)", value="abb")
    test_btn = st.button("⚡ Test String", use_container_width=True)

    st.divider()
    st.markdown("## 📋 Batch Test")
    batch_btn = st.button("🔁 Run Batch Test", use_container_width=True)

    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown("""
    - **Thompson's Construction** → NFA  
    - **Subset Construction** → DFA  
    - **Shunting-Yard** → Postfix  
    """)

# ── Session state ─────────────────────────────────────────────────────────────
if "nfa" not in st.session_state:
    st.session_state.nfa = None
    st.session_state.dfa = None
    st.session_state.postfix = None
    st.session_state.regex = None


def nfa_dot_source(nfa):
    dot_lines = ['digraph NFA {', '    rankdir=LR;',
                 '    node [shape=circle];',
                 '    "__start__" [shape=none label=""];',
                 f'    "__start__" -> "q{nfa.start_state.id}";']
    for s in nfa.accept_states:
        dot_lines.append(f'    "q{s.id}" [shape=doublecircle];')
    for s in nfa.states:
        for sym, targets in s.transitions.items():
            lbl = sym if sym != EPSILON else 'ε'
            for t in targets:
                dot_lines.append(f'    "q{s.id}" -> "q{t.id}" [label="{lbl}"];')
    dot_lines.append('}')
    return '\n'.join(dot_lines)


def dfa_dot_source(dfa):
    dot_lines = ['digraph DFA {', '    rankdir=LR;',
                 '    node [shape=circle];',
                 '    "__start__" [shape=none label=""];',
                 f'    "__start__" -> "{dfa.start_state.name}";']
    for ds in dfa.accept_states:
        dot_lines.append(f'    "{ds.name}" [shape=doublecircle];')
    for src, sym_map in dfa.transition_table.items():
        for sym, tgt in sym_map.items():
            if tgt != "∅":
                dot_lines.append(f'    "{src}" -> "{tgt}" [label="{sym}"];')
    dot_lines.append('}')
    return '\n'.join(dot_lines)

# ── Convert ───────────────────────────────────────────────────────────────────
if convert_btn:
    try:
        postfix = to_postfix(regex)
        nfa = build_nfa(postfix)
        dfa = build_dfa(nfa)
        st.session_state.nfa = nfa
        st.session_state.dfa = dfa
        st.session_state.postfix = postfix
        st.session_state.regex = regex
        st.success(f"✅ Converted successfully! NFA: {len(nfa.states)} states | DFA: {len(dfa.states)} states")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ── Main content ──────────────────────────────────────────────────────────────
nfa = st.session_state.nfa
dfa = st.session_state.dfa

if nfa and dfa:
    postfix = st.session_state.postfix
    reg = st.session_state.regex

    # ── Info cards ────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Regex", reg)
    col2.metric("Postfix", postfix)
    col3.metric("NFA States", len(nfa.states))
    col4.metric("DFA States", len(dfa.states))

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 NFA Table",
        "📊 DFA Table",
        "🖼️ NFA Graph",
        "🖼️ DFA Graph",
        "🔍 NFA Details",
        "🔍 DFA Details",
    ])

    # NFA Table
    with tab1:
        st.markdown("### NFA Transition Table")
        st.markdown(f"""
        <div class='info-box'>
        <b>Start State:</b> q{nfa.start_state.id} &nbsp;|&nbsp;
        <b>Accept States:</b> {[str(s) for s in nfa.accept_states]} &nbsp;|&nbsp;
        <b>Alphabet:</b> {sorted(nfa.alphabet)}
        </div>
        """, unsafe_allow_html=True)

        symbols = sorted(nfa.alphabet) + [EPSILON]
        rows = []
        for st_obj in nfa.states:
            row = {"State": f"q{st_obj.id}"}
            if st_obj == nfa.start_state and st_obj in nfa.accept_states:
                row["Type"] = "Start / Accept"
            elif st_obj == nfa.start_state:
                row["Type"] = "→ Start"
            elif st_obj in nfa.accept_states:
                row["Type"] = "* Accept"
            else:
                row["Type"] = "—"
            for sym in symbols:
                targets = nfa.transition_table.get(st_obj.id, {}).get(sym, [])
                row[sym] = "{" + ",".join(f"q{t}" for t in targets) + "}" if targets else "∅"
            rows.append(row)

        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # DFA Table
    with tab2:
        st.markdown("### DFA Transition Table")
        st.markdown(f"""
        <div class='info-box'>
        <b>Start State:</b> {dfa.start_state.name} &nbsp;|&nbsp;
        <b>Accept States:</b> {[s.name for s in dfa.accept_states]} &nbsp;|&nbsp;
        <b>Alphabet:</b> {dfa.alphabet}
        </div>
        """, unsafe_allow_html=True)

        dfa_rows = []
        for ds in dfa.states:
            nfa_repr = "{" + ",".join(f"q{s.id}" for s in sorted(ds.nfa_subset, key=lambda x: x.id)) + "}"
            row = {"DFA State": ds.name, "NFA Subset": nfa_repr}
            if ds == dfa.start_state and ds.is_accept:
                row["Type"] = "Start / Accept"
            elif ds == dfa.start_state:
                row["Type"] = "→ Start"
            elif ds.is_accept:
                row["Type"] = "* Accept"
            else:
                row["Type"] = "—"
            for sym in dfa.alphabet:
                row[sym] = dfa.transition_table.get(ds.name, {}).get(sym, "∅")
            dfa_rows.append(row)

        st.dataframe(pd.DataFrame(dfa_rows), use_container_width=True, hide_index=True)

    # NFA Graph
    with tab3:
        st.markdown("### NFA Graph")
        nfa_dot = nfa_dot_source(nfa)
        st.graphviz_chart(nfa_dot, use_container_width=True)
        st.code(nfa_dot, language="dot")

    # DFA Graph
    with tab4:
        st.markdown("### DFA Graph")
        dfa_dot = dfa_dot_source(dfa)
        st.graphviz_chart(dfa_dot, use_container_width=True)
        st.code(dfa_dot, language="dot")

    # NFA Details
    with tab5:
        st.markdown("### NFA Details")
        st.markdown(f"**Total States:** {len(nfa.states)}")
        st.markdown(f"**Start State:** q{nfa.start_state.id}")
        st.markdown(f"**Accept States:** {[str(s) for s in nfa.accept_states]}")
        st.markdown(f"**Alphabet:** {sorted(nfa.alphabet)}")
        st.markdown("**DOT Source (paste at graphviz.online to visualize):**")
        st.code(nfa_dot_source(nfa), language="dot")
        st.info("💡 Copy the DOT code above and paste it at **https://graphviz.online** to see the NFA diagram!")

    # DFA Details
    with tab6:
        st.markdown("### DFA Details")
        st.markdown(f"**Total States:** {len(dfa.states)}")
        st.markdown(f"**Start State:** {dfa.start_state.name}")
        st.markdown(f"**Accept States:** {[s.name for s in dfa.accept_states]}")
        st.markdown("**DOT Source (paste at graphviz.online to visualize):**")
        st.code(dfa_dot_source(dfa), language="dot")
        st.info("💡 Copy the DOT code above and paste it at **https://graphviz.online** to see the DFA diagram!")

    st.divider()

    # ── String Test ───────────────────────────────────────────────────────────
    if test_btn:
        st.markdown("## 🧪 String Test Result")
        s = test_string
        dfa_ok, dfa_path = simulate_dfa(dfa, s)
        nfa_ok, nfa_path = simulate_nfa(nfa, s)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### DFA Result")
            if dfa_ok:
                st.markdown(f"<p class='accept'>✅ ACCEPTED</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p class='reject'>❌ REJECTED</p>", unsafe_allow_html=True)
            st.markdown(f"**Path:** `{' → '.join(dfa_path)}`")

        with col2:
            st.markdown("### NFA Result")
            if nfa_ok:
                st.markdown(f"<p class='accept'>✅ ACCEPTED</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p class='reject'>❌ REJECTED</p>", unsafe_allow_html=True)
            st.markdown(f"**Path:** `{' → '.join(nfa_path)}`")

    # ── Batch Test ────────────────────────────────────────────────────────────
    if batch_btn:
        st.markdown("## 🔁 Batch Test Results")
        all_strings = ACCEPTED_STRINGS + REJECTED_STRINGS
        results = batch_test(dfa, nfa, all_strings)

        batch_rows = []
        for r in results:
            batch_rows.append({
                "String": r["string"] if r["string"] else "ε",
                "Expected": "✅ ACCEPT" if r["string"] in ACCEPTED_STRINGS else "❌ REJECT",
                "DFA Result": "✅ ACCEPT" if r["dfa_accepted"] else "❌ REJECT",
                "NFA Result": "✅ ACCEPT" if r["nfa_accepted"] else "❌ REJECT",
                "DFA Path": r["dfa_path"],
            })

        st.dataframe(pd.DataFrame(batch_rows), use_container_width=True, hide_index=True)

else:
    # Welcome screen
    st.markdown("""
    ## 👈 Enter a Regular Expression in the sidebar and click **Convert**

    ### Supported Operators:
    | Operator | Meaning | Example |
    |----------|---------|---------|
    | `\\|` | Union / OR | `a\\|b` matches a or b |
    | `*` | Kleene Star (zero or more) | `a*` matches ε, a, aa, ... |
    | `+` | One or more | `a+` matches a, aa, aaa, ... |
    | `?` | Zero or one | `a?` matches ε or a |
    | `()` | Grouping | `(ab)*` |

    ### Example Regexes to try:
    - `(a|b)*abb` — strings over {a,b} ending in abb
    - `a*b+` — zero or more a's followed by one or more b's
    - `(ab)?c` — optional ab followed by c
    """)
