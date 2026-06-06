"""
gui.py
------
Professional Tkinter GUI for the RE → NFA → DFA Converter.

Student : Amna Khurram
ID      : F24605061 | CS 2024-B
Instructor: Naveed Yousaf

Features
--------
  • Regex input with live validation
  • Convert button (Thompson + Subset construction)
  • NFA / DFA transition tables displayed in scrollable grid
  • String test panel with Accept / Reject output
  • Graphviz-rendered NFA and DFA diagrams shown inline
  • Batch-test panel (pre-defined accepted / rejected strings)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import threading
import subprocess
import tempfile
import shutil
from pathlib import Path

# ── project modules ──────────────────────────────────────────────────────────
from regex_parser import to_postfix
from nfa          import build_nfa, EPSILON
from dfa          import build_dfa
from simulator    import simulate_dfa, simulate_nfa, batch_test, ACCEPTED_STRINGS, REJECTED_STRINGS

# ── optional Graphviz PIL integration ────────────────────────────────────────
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

GRAPHVIZ_AVAILABLE = shutil.which("dot") is not None

# ── colour palette ────────────────────────────────────────────────────────────
BG        = "#1E1E2E"   # main background
PANEL     = "#2A2A3E"   # panel / frame background
ACCENT    = "#7C3AED"   # purple accent
ACCEPT_CL = "#22C55E"   # green for accept
REJECT_CL = "#EF4444"   # red for reject
FG        = "#E2E8F0"   # primary text
FG2       = "#94A3B8"   # secondary text
ENTRY_BG  = "#0F0F1A"
MONO      = ("Consolas", 10)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: generate Graphviz DOT and render to PNG
# ─────────────────────────────────────────────────────────────────────────────

def _nfa_to_dot(nfa) -> str:
    lines = [
        'digraph NFA {',
        '    rankdir=LR;',
        '    node [shape=circle fontname="Arial" style=filled fillcolor="#2A2A3E" fontcolor="white" color="#7C3AED"];',
        '    edge [color="#7C3AED" fontcolor="#E2E8F0" fontname="Arial"];',
        '    "__start__" [shape=none label="" width=0];',
        f'    "__start__" -> "q{nfa.start_state.id}";',
    ]
    # Double-circle accept states
    for st in nfa.accept_states:
        lines.append(f'    "q{st.id}" [shape=doublecircle fillcolor="#22C55E" fontcolor="black"];')
    # Transitions
    for st in nfa.states:
        for sym, targets in st.transitions.items():
            lbl = sym if sym != EPSILON else 'ε'
            for t in targets:
                lines.append(f'    "q{st.id}" -> "q{t.id}" [label="{lbl}"];')
    lines.append('}')
    return '\n'.join(lines)


def _dfa_to_dot(dfa) -> str:
    lines = [
        'digraph DFA {',
        '    rankdir=LR;',
        '    node [shape=circle fontname="Arial" style=filled fillcolor="#2A2A3E" fontcolor="white" color="#6366F1"];',
        '    edge [color="#6366F1" fontcolor="#E2E8F0" fontname="Arial"];',
        '    "__start__" [shape=none label="" width=0];',
        f'    "__start__" -> "{dfa.start_state.name}";',
    ]
    for ds in dfa.accept_states:
        lines.append(f'    "{ds.name}" [shape=doublecircle fillcolor="#22C55E" fontcolor="black"];')
    for src, sym_map in dfa.transition_table.items():
        for sym, tgt in sym_map.items():
            if tgt != "∅":
                lines.append(f'    "{src}" -> "{tgt}" [label="{sym}"];')
    lines.append('}')
    return '\n'.join(lines)


def render_dot(dot_src: str, out_path: str) -> bool:
    """Render DOT source to a PNG file. Returns True on success."""
    if not GRAPHVIZ_AVAILABLE:
        return False
    try:
        proc = subprocess.run(
            ["dot", "-Tpng", "-o", out_path],
            input=dot_src.encode(),
            capture_output=True,
            timeout=15,
        )
        return proc.returncode == 0
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RE → NFA → DFA Converter  |  Amna Khurram  F24605061")
        self.geometry("1280x820")
        self.minsize(1000, 700)
        self.configure(bg=BG)

        self._nfa   = None
        self._dfa   = None
        self._tmpdir = tempfile.mkdtemp(prefix="nfa_dfa_")

        self._build_ui()
        self._set_default_regex()

    # ──────────────────────────────────────────────────────
    # UI construction
    # ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── title bar ────────────────────────────────────
        title_bar = tk.Frame(self, bg=ACCENT, height=42)
        title_bar.pack(fill="x", side="top")
        tk.Label(
            title_bar,
            text="  Regular Expression → NFA → DFA Converter & Simulator",
            bg=ACCENT, fg="white",
            font=("Arial", 13, "bold"),
        ).pack(side="left", padx=12, pady=8)
        tk.Label(
            title_bar,
            text="Amna Khurram | F24605061 | CS 2024-B",
            bg=ACCENT, fg="#DDD6FE",
            font=("Arial", 10),
        ).pack(side="right", padx=12)

        # ── main paned window ────────────────────────────
        main_pw = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=6, sashrelief="flat")
        main_pw.pack(fill="both", expand=True, padx=8, pady=8)

        # Left control panel
        left_panel = tk.Frame(main_pw, bg=PANEL, bd=0)
        main_pw.add(left_panel, minsize=340)

        # Right notebook
        right_nb = ttk.Notebook(main_pw)
        self._style_notebook(right_nb)
        main_pw.add(right_nb, minsize=600)

        self._build_left_panel(left_panel)
        self._build_right_notebook(right_nb)

    def _style_notebook(self, nb):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",       background=BG,    borderwidth=0)
        style.configure("TNotebook.Tab",   background=PANEL, foreground=FG2,
                        padding=[14, 6],  font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

    def _build_left_panel(self, parent):
        pad = {"padx": 14, "pady": 6}

        # ── section: Regex Input ─────────────────────────
        tk.Label(parent, text="Regular Expression", bg=PANEL, fg=ACCENT,
                 font=("Arial", 11, "bold")).pack(anchor="w", **pad)

        self._regex_var = tk.StringVar()
        entry = tk.Entry(parent, textvariable=self._regex_var,
                         bg=ENTRY_BG, fg=FG, insertbackground=FG,
                         font=("Consolas", 14), relief="flat", bd=6)
        entry.pack(fill="x", padx=14, pady=(0, 4))
        entry.bind("<Return>", lambda e: self._convert())

        tk.Label(parent, text="Example:  (a|b)*abb   |   a*b+   |   (ab)?c",
                 bg=PANEL, fg=FG2, font=("Arial", 9)).pack(anchor="w", padx=14)

        tk.Button(
            parent, text="▶  Convert", command=self._convert,
            bg=ACCENT, fg="white", activebackground="#6D28D9",
            font=("Arial", 11, "bold"), relief="flat", cursor="hand2",
            padx=20, pady=8,
        ).pack(fill="x", padx=14, pady=10)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=14, pady=4)

        # ── section: String Tester ───────────────────────
        tk.Label(parent, text="Test a String", bg=PANEL, fg=ACCENT,
                 font=("Arial", 11, "bold")).pack(anchor="w", **pad)

        self._test_var = tk.StringVar()
        tk.Entry(parent, textvariable=self._test_var,
                 bg=ENTRY_BG, fg=FG, insertbackground=FG,
                 font=("Consolas", 13), relief="flat", bd=6,
                 ).pack(fill="x", padx=14, pady=(0, 6))

        tk.Button(
            parent, text="⚡  Test String", command=self._test_string,
            bg="#0F766E", fg="white", activebackground="#0D9488",
            font=("Arial", 11, "bold"), relief="flat", cursor="hand2",
            padx=20, pady=8,
        ).pack(fill="x", padx=14, pady=(0, 8))

        # Result banner
        self._result_frame = tk.Frame(parent, bg=PANEL)
        self._result_frame.pack(fill="x", padx=14, pady=4)
        self._result_label = tk.Label(
            self._result_frame, text="", font=("Arial", 15, "bold"),
            bg=PANEL, fg=FG, width=20,
        )
        self._result_label.pack(expand=True, fill="x", ipady=10)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=14, pady=4)

        # ── section: Info Box ────────────────────────────
        tk.Label(parent, text="Automaton Info", bg=PANEL, fg=ACCENT,
                 font=("Arial", 11, "bold")).pack(anchor="w", **pad)

        self._info_text = scrolledtext.ScrolledText(
            parent, bg=ENTRY_BG, fg=FG2, font=MONO,
            relief="flat", state="disabled", height=14,
        )
        self._info_text.pack(fill="both", expand=True, padx=14, pady=4)

    def _build_right_notebook(self, nb):
        # Tab 1: NFA Transition Table
        self._nfa_tab = tk.Frame(nb, bg=BG)
        nb.add(self._nfa_tab, text="  NFA Table  ")

        # Tab 2: DFA Transition Table
        self._dfa_tab = tk.Frame(nb, bg=BG)
        nb.add(self._dfa_tab, text="  DFA Table  ")

        # Tab 3: NFA Diagram
        self._nfa_img_tab = tk.Frame(nb, bg=BG)
        nb.add(self._nfa_img_tab, text="  NFA Diagram  ")

        # Tab 4: DFA Diagram
        self._dfa_img_tab = tk.Frame(nb, bg=BG)
        nb.add(self._dfa_img_tab, text="  DFA Diagram  ")

        # Tab 5: Batch Tests
        self._batch_tab = tk.Frame(nb, bg=BG)
        nb.add(self._batch_tab, text="  Batch Tests  ")

        self._build_batch_tab()

    # ── batch test tab ────────────────────────────────────────────────────

    def _build_batch_tab(self):
        hdr = tk.Label(self._batch_tab,
                       text="Pre-defined Test Cases  (run after conversion)",
                       bg=BG, fg=ACCENT, font=("Arial", 11, "bold"))
        hdr.pack(anchor="w", padx=14, pady=8)

        tk.Button(
            self._batch_tab, text="▶  Run Batch Tests",
            command=self._run_batch,
            bg="#1D4ED8", fg="white", font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", padx=16, pady=6,
        ).pack(anchor="w", padx=14, pady=(0, 8))

        frame = tk.Frame(self._batch_tab, bg=BG)
        frame.pack(fill="both", expand=True, padx=14, pady=4)

        style = ttk.Style()
        style.configure("Batch.Treeview",
                        background=ENTRY_BG, foreground=FG,
                        rowheight=24, fieldbackground=ENTRY_BG,
                        font=("Consolas", 10))
        style.configure("Batch.Treeview.Heading",
                        background=PANEL, foreground=ACCENT,
                        font=("Arial", 10, "bold"), relief="flat")
        style.map("Batch.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        cols = ("string", "expected", "dfa_result", "dfa_path")
        self._batch_tree = ttk.Treeview(
            frame, columns=cols, show="headings",
            style="Batch.Treeview",
        )
        self._batch_tree.heading("string",     text="Input String")
        self._batch_tree.heading("expected",   text="Expected")
        self._batch_tree.heading("dfa_result", text="DFA Result")
        self._batch_tree.heading("dfa_path",   text="DFA Path")

        self._batch_tree.column("string",     width=120, anchor="center")
        self._batch_tree.column("expected",   width=90,  anchor="center")
        self._batch_tree.column("dfa_result", width=90,  anchor="center")
        self._batch_tree.column("dfa_path",   width=300, anchor="w")

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=self._batch_tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self._batch_tree.xview)
        self._batch_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._batch_tree.pack(fill="both", expand=True)

        self._batch_tree.tag_configure("accept", foreground=ACCEPT_CL)
        self._batch_tree.tag_configure("reject", foreground=REJECT_CL)

    # ──────────────────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────────────────

    def _set_default_regex(self):
        self._regex_var.set("(a|b)*abb")

    def _convert(self):
        regex = self._regex_var.get().strip()
        if not regex:
            messagebox.showwarning("Input Error", "Please enter a regular expression.")
            return
        try:
            postfix     = to_postfix(regex)
            self._nfa   = build_nfa(postfix)
            self._dfa   = build_dfa(self._nfa)
        except Exception as exc:
            messagebox.showerror("Conversion Error", str(exc))
            return

        self._populate_nfa_table()
        self._populate_dfa_table()
        self._render_nfa_diagram()
        self._render_dfa_diagram()
        self._update_info_box(regex, postfix)

    def _test_string(self):
        if self._dfa is None:
            messagebox.showinfo("Not Ready", "Please convert a regex first.")
            return
        s   = self._test_var.get()
        ok, path = simulate_dfa(self._dfa, s)
        label = "ACCEPT ✓" if ok else "REJECT ✗"
        color = ACCEPT_CL if ok else REJECT_CL
        self._result_label.config(text=label, fg=color,
                                  bg="#14532D" if ok else "#450A0A")
        # Show path in info box
        display = f'String "{s}": {label}\nDFA path: {" → ".join(path)}\n'
        self._append_info(display)

    def _run_batch(self):
        if self._dfa is None or self._nfa is None:
            messagebox.showinfo("Not Ready", "Please convert a regex first.")
            return
        self._batch_tree.delete(*self._batch_tree.get_children())
        all_strings  = [(s, "ACCEPT") for s in ACCEPTED_STRINGS] + \
                       [(s, "REJECT") for s in REJECTED_STRINGS]
        for s, expected in all_strings:
            ok, path = simulate_dfa(self._dfa, s)
            result   = "ACCEPT" if ok else "REJECT"
            tag      = "accept" if ok else "reject"
            display  = s if s else "ε"
            self._batch_tree.insert(
                "", "end",
                values=(display, expected, result, " → ".join(path)),
                tags=(tag,),
            )

    # ──────────────────────────────────────────────────────
    # Table builders
    # ──────────────────────────────────────────────────────

    def _clear_tab(self, tab):
        for w in tab.winfo_children():
            w.destroy()

    def _populate_nfa_table(self):
        self._clear_tab(self._nfa_tab)
        nfa = self._nfa
        symbols = sorted(nfa.alphabet) + [EPSILON]

        tk.Label(self._nfa_tab, text="NFA Transition Table",
                 bg=BG, fg=ACCENT, font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=8)

        frame = tk.Frame(self._nfa_tab, bg=BG)
        frame.pack(fill="both", expand=True, padx=14, pady=4)

        self._make_table(
            frame,
            headers=["State", "Type"] + symbols,
            rows=self._nfa_rows(nfa, symbols),
        )

    def _nfa_rows(self, nfa, symbols):
        rows = []
        for st in nfa.states:
            state_name = f"q{st.id}"
            if st == nfa.start_state and st in nfa.accept_states:
                stype = "Start/Accept"
            elif st == nfa.start_state:
                stype = "Start →"
            elif st in nfa.accept_states:
                stype = "Accept *"
            else:
                stype = "—"
            row = [state_name, stype]
            for sym in symbols:
                targets = nfa.transition_table.get(st.id, {}).get(sym, [])
                cell    = "{" + ",".join(f"q{t}" for t in targets) + "}" if targets else "∅"
                row.append(cell)
            rows.append(row)
        return rows

    def _populate_dfa_table(self):
        self._clear_tab(self._dfa_tab)
        dfa = self._dfa

        tk.Label(self._dfa_tab, text="DFA Transition Table",
                 bg=BG, fg=ACCENT, font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=8)

        frame = tk.Frame(self._dfa_tab, bg=BG)
        frame.pack(fill="both", expand=True, padx=14, pady=4)

        self._make_table(
            frame,
            headers=["DFA State", "NFA Subset", "Type"] + dfa.alphabet,
            rows=self._dfa_rows(dfa),
        )

    def _dfa_rows(self, dfa):
        rows = []
        for ds in dfa.states:
            nfa_repr = "{" + ",".join(f"q{s.id}" for s in sorted(ds.nfa_subset, key=lambda x: x.id)) + "}"
            if ds == dfa.start_state and ds.is_accept:
                stype = "Start/Accept"
            elif ds == dfa.start_state:
                stype = "Start →"
            elif ds.is_accept:
                stype = "Accept *"
            else:
                stype = "—"
            row = [ds.name, nfa_repr, stype]
            for sym in dfa.alphabet:
                row.append(dfa.transition_table.get(ds.name, {}).get(sym, "∅"))
            rows.append(row)
        return rows

    def _make_table(self, parent, headers, rows):
        style = ttk.Style()
        style.configure("Data.Treeview",
                        background=ENTRY_BG, foreground=FG,
                        rowheight=26, fieldbackground=ENTRY_BG,
                        font=("Consolas", 10))
        style.configure("Data.Treeview.Heading",
                        background=PANEL, foreground=ACCENT,
                        font=("Arial", 10, "bold"), relief="flat")
        style.map("Data.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        tv = ttk.Treeview(parent, columns=headers, show="headings",
                          style="Data.Treeview")
        for h in headers:
            tv.heading(h, text=h)
            tv.column(h,  width=max(80, len(h) * 10), anchor="center")

        for row in rows:
            tv.insert("", "end", values=row)

        vsb = ttk.Scrollbar(parent, orient="vertical",   command=tv.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tv.pack(fill="both", expand=True)

    # ──────────────────────────────────────────────────────
    # Graphviz diagrams
    # ──────────────────────────────────────────────────────

    def _render_nfa_diagram(self):
        self._clear_tab(self._nfa_img_tab)
        dot  = _nfa_to_dot(self._nfa)
        path = os.path.join(self._tmpdir, "nfa.png")
        self._render_diagram(self._nfa_img_tab, dot, path, "NFA")

    def _render_dfa_diagram(self):
        self._clear_tab(self._dfa_img_tab)
        dot  = _dfa_to_dot(self._dfa)
        path = os.path.join(self._tmpdir, "dfa.png")
        self._render_diagram(self._dfa_img_tab, dot, path, "DFA")

    def _render_diagram(self, tab, dot_src, out_path, label):
        tk.Label(tab, text=f"{label} Automaton Diagram",
                 bg=BG, fg=ACCENT, font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=8)

        if not GRAPHVIZ_AVAILABLE:
            tk.Label(tab, text="⚠  Graphviz not found.  Install it and add to PATH.",
                     bg=BG, fg=REJECT_CL, font=("Arial", 11)).pack(padx=14, pady=20)
            # Show raw DOT source as fallback
            st = scrolledtext.ScrolledText(tab, bg=ENTRY_BG, fg=FG2, font=MONO)
            st.pack(fill="both", expand=True, padx=14, pady=4)
            st.insert("end", dot_src)
            st.config(state="disabled")
            return

        ok = render_dot(dot_src, out_path)
        if not ok:
            tk.Label(tab, text="⚠  Graphviz render failed.",
                     bg=BG, fg=REJECT_CL, font=("Arial", 11)).pack(padx=14, pady=20)
            return

        if not PIL_AVAILABLE:
            tk.Label(tab,
                     text=f"✓ Diagram saved to: {out_path}\n(Install Pillow for inline preview)",
                     bg=BG, fg=ACCEPT_CL, font=("Arial", 11)).pack(padx=14, pady=20)
            return

        # Load and display inline
        try:
            img = Image.open(out_path)
            # Fit image within the tab area (~900×600)
            img.thumbnail((900, 580), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            canvas = tk.Canvas(tab, bg="#0F0F1A", highlightthickness=0)
            canvas.pack(fill="both", expand=True, padx=14, pady=4)

            def _draw(event=None):
                canvas.delete("all")
                cw, ch = canvas.winfo_width(), canvas.winfo_height()
                x, y   = max(cw // 2, 10), max(ch // 2, 10)
                canvas.create_image(x, y, anchor="center", image=photo)

            canvas.photo = photo   # keep reference
            canvas.bind("<Configure>", _draw)
            self.after(100, _draw)
        except Exception as exc:
            tk.Label(tab, text=f"Image load error: {exc}",
                     bg=BG, fg=REJECT_CL, font=("Arial", 10)).pack()

    # ──────────────────────────────────────────────────────
    # Info box
    # ──────────────────────────────────────────────────────

    def _update_info_box(self, regex, postfix):
        nfa, dfa = self._nfa, self._dfa
        lines = [
            f"Regex         : {regex}",
            f"Postfix       : {postfix}",
            "",
            f"NFA States    : {len(nfa.states)}",
            f"NFA Start     : q{nfa.start_state.id}",
            f"NFA Accept    : {[str(s) for s in nfa.accept_states]}",
            f"Alphabet      : {sorted(nfa.alphabet)}",
            "",
            f"DFA States    : {len(dfa.states)}",
            f"DFA Start     : {dfa.start_state.name}",
            f"DFA Accept    : {[s.name for s in dfa.accept_states]}",
            "",
        ]
        self._info_text.config(state="normal")
        self._info_text.delete("1.0", "end")
        self._info_text.insert("end", "\n".join(lines))
        self._info_text.config(state="disabled")

    def _append_info(self, text):
        self._info_text.config(state="normal")
        self._info_text.insert("end", text + "\n")
        self._info_text.see("end")
        self._info_text.config(state="disabled")

    def destroy(self):
        shutil.rmtree(self._tmpdir, ignore_errors=True)
        super().destroy()


# ─────────────────────────────────────────────────────────────────────────────

def run_gui():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
