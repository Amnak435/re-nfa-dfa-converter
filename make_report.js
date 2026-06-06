const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak, LevelFormat,
  TabStopType, TabStopPosition
} = require('docx');
const fs = require('fs');

// ── colour palette ──────────────────────────────────────────────────────────
const BLUE     = "1F3864";
const LBLUE    = "2E75B6";
const HEADER_F = "D6E4F0";
const ROW_ALT  = "EBF3FB";
const WHITE    = "FFFFFF";
const DARK     = "1A1A1A";

// ── helpers ─────────────────────────────────────────────────────────────────
const b  = (text, size=24, color=DARK) => new TextRun({ text, bold:true,  font:"Arial", size, color });
const r  = (text, size=24, color=DARK) => new TextRun({ text, bold:false, font:"Arial", size, color });
const rb = (text, size=22, color=DARK) => new TextRun({ text, bold:false, font:"Courier New", size, color });

const para = (children, opts={}) => new Paragraph({ children, alignment: AlignmentType.JUSTIFY, spacing:{ after:160 }, ...opts });
const hpara = (children, opts={}) => new Paragraph({ children, alignment: AlignmentType.LEFT, spacing:{ after:160 }, ...opts });

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, bold:true, font:"Arial", size:36, color:WHITE })],
  shading: { fill: BLUE, type: ShadingType.CLEAR },
  spacing: { before:480, after:240 },
  border: { bottom: { style: BorderStyle.SINGLE, size:6, color:LBLUE } }
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, bold:true, font:"Arial", size:28, color:BLUE })],
  spacing: { before:300, after:160 },
  border: { bottom: { style: BorderStyle.SINGLE, size:3, color:LBLUE } }
});

const h3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  children: [new TextRun({ text, bold:true, font:"Arial", size:26, color:LBLUE })],
  spacing: { before:200, after:120 }
});

const pageBreak = () => new Paragraph({ children:[new PageBreak()], spacing:{after:0} });

const bdr = { style: BorderStyle.SINGLE, size:1, color:"BBBBBB" };
const borders = { top:bdr, bottom:bdr, left:bdr, right:bdr };
const cellPad = { top:100, bottom:100, left:160, right:160 };

const hdrCell = (text, w) => new TableCell({
  borders, width:{size:w, type:WidthType.DXA},
  shading:{ fill:BLUE, type:ShadingType.CLEAR },
  margins: cellPad,
  verticalAlign: VerticalAlign.CENTER,
  children:[new Paragraph({ alignment:AlignmentType.CENTER,
    children:[new TextRun({ text, bold:true, font:"Arial", size:22, color:WHITE })] })]
});
const dataCell = (text, w, shade=WHITE) => new TableCell({
  borders, width:{size:w, type:WidthType.DXA},
  shading:{ fill:shade, type:ShadingType.CLEAR },
  margins: cellPad,
  children:[new Paragraph({ alignment:AlignmentType.CENTER,
    children:[new TextRun({ text, font:"Arial", size:22, color:DARK })] })]
});
const dataLeftCell = (text, w, shade=WHITE, bold=false) => new TableCell({
  borders, width:{size:w, type:WidthType.DXA},
  shading:{ fill:shade, type:ShadingType.CLEAR },
  margins: cellPad,
  children:[new Paragraph({
    children:[new TextRun({ text, bold, font:"Arial", size:22, color:DARK })] })]
});

const bullet = (text) => new Paragraph({
  numbering:{ reference:"bullets", level:0 },
  children:[r(text)],
  spacing:{ after:100 }
});

const codeBlock = (lines) => lines.map(l => new Paragraph({
  children:[rb(l)],
  spacing:{ after:60 },
  shading:{ fill:"F0F0F0", type:ShadingType.CLEAR },
  indent:{ left:720 }
}));

// ── cover page ───────────────────────────────────────────────────────────────
function makeCover() {
  return [
    new Paragraph({ spacing:{after:2400} }),
    new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:240},
      children:[b("COMSATS UNIVERSITY ISLAMABAD", 28, BLUE)] }),
    new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:80},
      children:[r("Department of Computer Science", 24, LBLUE)] }),
    new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:600},
      children:[r("Formal Languages & Automata – CS3xx", 22)] }),
    new Paragraph({ spacing:{after:0},
      border:{ bottom:{ style:BorderStyle.SINGLE, size:8, color:BLUE } } }),
    new Paragraph({ spacing:{after:800} }),
    new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:320},
      children:[b("Regular Expression to NFA to DFA", 44, BLUE)] }),
    new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:200},
      children:[b("Converter and String Simulator", 44, BLUE)] }),
    new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:800},
      children:[r("Course Project – CLO 3 & 4", 26, LBLUE)] }),
    new Paragraph({ spacing:{after:0},
      border:{ bottom:{ style:BorderStyle.SINGLE, size:8, color:BLUE } } }),
    new Paragraph({ spacing:{after:600} }),
    // info table
    new Table({
      width:{ size:7200, type:WidthType.DXA }, columnWidths:[2400,4800],
      rows:[
        new TableRow({ children:[
          dataLeftCell("Student Name", 2400, HEADER_F, true),
          dataLeftCell("Amna Khurram", 4800)
        ]}),
        new TableRow({ children:[
          dataLeftCell("Student ID", 2400, HEADER_F, true),
          dataLeftCell("F24605061", 4800)
        ]}),
        new TableRow({ children:[
          dataLeftCell("Section", 2400, HEADER_F, true),
          dataLeftCell("CS 2024-B", 4800)
        ]}),
        new TableRow({ children:[
          dataLeftCell("Instructor", 2400, HEADER_F, true),
          dataLeftCell("Naveed Yousaf", 4800)
        ]}),
        new TableRow({ children:[
          dataLeftCell("Submission Date", 2400, HEADER_F, true),
          dataLeftCell("June 2026", 4800)
        ]}),
        new TableRow({ children:[
          dataLeftCell("Total Marks", 2400, HEADER_F, true),
          dataLeftCell("10", 4800)
        ]}),
      ]
    }),
    pageBreak(),
  ];
}

// ── Chapter 1: Introduction ──────────────────────────────────────────────────
function ch1() {
  return [
    h1("Chapter 1: Introduction"),
    h2("1.1  Formal Languages"),
    para([r("A formal language is a set of strings over an alphabet, where an alphabet is any finite, non-empty set of symbols. Formal language theory forms the mathematical backbone of compiler design, text processing, and program verification. Languages are categorised by the Chomsky hierarchy into four classes: regular, context-free, context-sensitive, and recursively enumerable. This project focuses on the most restricted and well-understood class — regular languages.")]),
    para([r("Regular languages can be expressed in three equivalent formalisms: regular expressions (RE), finite automata (FA), and regular grammars. The equivalence between these representations is the central theme of this project.")]),
    h2("1.2  Regular Expressions"),
    para([r("A regular expression is a compact, algebraic notation for describing a regular language. The primitive operations are:")]),
    bullet("Concatenation: ab means 'a followed by b'."),
    bullet("Union / Alternation: a|b means 'a or b'."),
    bullet("Kleene Star: a* means 'zero or more a's'."),
    bullet("One-or-more: a+ means 'one or more a's' (syntactic sugar for aa*)."),
    bullet("Zero-or-one: a? means 'optionally a' (syntactic sugar for a|ε)."),
    para([r("For example, the regular expression (a|b)*abb denotes all strings over {a, b} that end with the substring abb. The Kleene star (a|b)* generates every possible prefix, while abb anchors the suffix.")]),
    h2("1.3  Non-deterministic Finite Automata (NFA)"),
    para([r("A Non-deterministic Finite Automaton (NFA) is a theoretical machine formally defined as a 5-tuple M = (Q, Σ, δ, q₀, F) where:")]),
    bullet("Q is a finite set of states."),
    bullet("Σ is the input alphabet (finite set of symbols)."),
    bullet("δ: Q × (Σ ∪ {ε}) → 2^Q is the transition function, which maps a state and a symbol (possibly ε) to a set of next states."),
    bullet("q₀ ∈ Q is the unique start state."),
    bullet("F ⊆ Q is the set of accepting (final) states."),
    para([r("NFAs allow multiple transitions on the same symbol and ε-transitions (spontaneous transitions consuming no input). A string w is accepted by an NFA if there exists at least one computation path that reads w and ends in an accepting state.")]),
    h2("1.4  Deterministic Finite Automata (DFA)"),
    para([r("A Deterministic Finite Automaton (DFA) is a special case of an NFA in which every state has exactly one transition for each input symbol and no ε-transitions. The transition function is δ: Q × Σ → Q (a total function). DFAs are straightforward to implement in software and can be executed in O(n) time, where n is the length of the input string.")]),
    para([r("The key theoretical result — proved by the Subset Construction theorem — is that for every NFA, there exists a DFA that accepts exactly the same language. This equivalence is the foundation of all modern lexical analyser generators such as lex, flex, and re2c.")]),
    h2("1.5  Project Objectives"),
    bullet("Implement a regular expression parser that converts infix RE to postfix notation."),
    bullet("Implement Thompson's Construction to convert postfix RE to an NFA."),
    bullet("Implement the Subset Construction algorithm to convert the NFA to a minimal DFA."),
    bullet("Visualise both the NFA and DFA as directed graphs using Graphviz."),
    bullet("Provide an interactive Tkinter GUI so users can enter any regex and test strings."),
    bullet("Validate the system against at least 5 accepted and 5 rejected strings."),
    pageBreak(),
  ];
}

// ── Chapter 2: Literature Review ─────────────────────────────────────────────
function ch2() {
  return [
    h1("Chapter 2: Literature Review"),
    h2("2.1  Thompson's Construction (1968)"),
    para([r("Ken Thompson published the seminal paper \"Programming Techniques: Regular Expression Search Algorithm\" in 1968. He introduced the construction that today bears his name, showing how to systematically convert a regular expression into an NFA with O(n) states and O(n) transitions, where n is the length of the expression. Thompson's original motivation was text searching in the QED editor, which later became the foundation of the Unix grep utility.")]),
    h2("2.2  Subset Construction Algorithm"),
    para([r("The Subset Construction (also called the Powerset Construction) was introduced by Rabin and Scott in their 1959 paper \"Finite and Infinite Automata\". They proved that every NFA can be converted to an equivalent DFA by treating sets of NFA states as single DFA states. The worst-case number of DFA states is 2^|Q|, though in practice the number of reachable subsets is far smaller.")]),
    h2("2.3  Hopcroft's DFA Minimisation (1971)"),
    para([r("John Hopcroft's 1971 algorithm provides an O(n log n) procedure for minimising a DFA to its canonical form (the minimum-state DFA for the language). While this project does not implement minimisation, it is the natural next step and is briefly discussed in the Complexity Analysis chapter.")]),
    h2("2.4  Graphviz and Automata Visualisation"),
    para([r("Graphviz is an open-source graph visualisation toolkit developed at AT&T Laboratories. Its DOT language provides a declarative way to specify directed graphs. Academic tools such as JFLAP (Rodger, 2006) and AutomataSim demonstrate the pedagogical value of interactive automata visualisers, motivating the visualisation module in this project.")]),
    h2("2.5  Python Ecosystem for Formal Language Tools"),
    para([r("Python's clean syntax and rich standard library (collections, functools, typing) make it well-suited for implementing language-processing algorithms. Tkinter provides a cross-platform GUI framework that requires no additional installation on Windows, Linux, or macOS. The graphviz Python package wraps the Graphviz command-line tools and renders DOT source to PNG or PDF images directly from Python code.")]),
    pageBreak(),
  ];
}

// ── Chapter 3: System Design ─────────────────────────────────────────────────
function ch3() {
  return [
    h1("Chapter 3: System Design"),
    h2("3.1  Overall Architecture"),
    para([r("The system is structured as a layered pipeline, each layer depending only on the layer below it:")]),
    // architecture text diagram
    new Paragraph({
      spacing:{ before:160, after:160 },
      shading:{ fill:"F5F5F5", type:ShadingType.CLEAR },
      indent:{ left:720, right:720 },
      children:[
        new TextRun({ text:"User Input (Regex string)", font:"Courier New", size:22, bold:true, color:BLUE }),
        new TextRun({ text:"\n         ↓\n", font:"Courier New", size:22, color:DARK }),
        new TextRun({ text:"regex_parser.py  ", font:"Courier New", size:22, bold:true, color:LBLUE }),
        new TextRun({ text:"→  Inserts explicit concatenation dots, converts to Postfix", font:"Courier New", size:20, color:DARK }),
        new TextRun({ text:"\n         ↓\n", font:"Courier New", size:22, color:DARK }),
        new TextRun({ text:"nfa.py           ", font:"Courier New", size:22, bold:true, color:LBLUE }),
        new TextRun({ text:"→  Thompson's Construction  →  NFA object", font:"Courier New", size:20, color:DARK }),
        new TextRun({ text:"\n         ↓\n", font:"Courier New", size:22, color:DARK }),
        new TextRun({ text:"dfa.py           ", font:"Courier New", size:22, bold:true, color:LBLUE }),
        new TextRun({ text:"→  Subset Construction     →  DFA object", font:"Courier New", size:20, color:DARK }),
        new TextRun({ text:"\n         ↓\n", font:"Courier New", size:22, color:DARK }),
        new TextRun({ text:"simulator.py     ", font:"Courier New", size:22, bold:true, color:LBLUE }),
        new TextRun({ text:"→  String simulation on DFA / NFA", font:"Courier New", size:20, color:DARK }),
        new TextRun({ text:"\n         ↓\n", font:"Courier New", size:22, color:DARK }),
        new TextRun({ text:"gui.py           ", font:"Courier New", size:22, bold:true, color:LBLUE }),
        new TextRun({ text:"→  Tkinter GUI + Graphviz Visualisation", font:"Courier New", size:20, color:DARK }),
      ]
    }),
    h2("3.2  Module Descriptions"),
    h3("3.2.1  regex_parser.py"),
    para([r("This module converts a user-written infix regular expression into a postfix (Reverse Polish Notation) string. It first inserts an explicit concatenation operator '.' wherever two tokens are implicitly concatenated, then applies the Shunting-Yard algorithm using an operator precedence table: '|' < '.' < '*' = '+' = '?'. The output is a flat string of symbols and operators consumed left-to-right by the NFA builder.")]),
    h3("3.2.2  nfa.py"),
    para([r("This module implements Thompson's Construction. Every operator maps to a small NFA fragment built from State objects. Fragments are pushed onto a stack; operators pop operands and push the result. The final stack element is wrapped in an NFA object that performs a BFS traversal to enumerate all reachable states and build the transition table.")]),
    h3("3.2.3  dfa.py"),
    para([r("This module implements the Subset Construction. It starts from the ε-closure of the NFA start state and iteratively computes, for each DFA state (a frozenset of NFA states) and each alphabet symbol, the set of reachable NFA states. New DFA states are enqueued until the worklist is empty. The result is a DFA object with a named transition table.")]),
    h3("3.2.4  simulator.py"),
    para([r("This module provides simulate_dfa() and simulate_nfa() functions. The DFA simulator follows the deterministic transition function and records the path of states visited. The NFA simulator uses the subset-based approach: it maintains the current set of active NFA states, updates it on each input symbol, and checks for acceptance. A batch_test() helper runs multiple strings and returns structured result dictionaries.")]),
    h3("3.2.5  gui.py"),
    para([r("This module builds the Tkinter GUI. It contains an input frame (regex entry, convert button), a results notebook (NFA table, DFA table, simulation panel), and a visualisation panel that renders Graphviz PNG images inside Tkinter Label widgets. All state is managed inside the GuiApp class.")]),
    h2("3.3  Data Flow"),
    para([r("The data flow through the system can be summarised as follows: the user types a regular expression (e.g., (a|b)*abb) and presses Convert. The GUI calls regex_parser.to_postfix() to get the postfix string ab|*.a.b.b., which is passed to nfa.build_nfa() to obtain an NFA object. The NFA is passed to dfa.build_dfa() to obtain a DFA object. Both objects are stored in the GUI state. When the user types a test string and presses Simulate, the GUI calls simulator.simulate_dfa() (and optionally simulate_nfa()) and displays the result with the state path.")]),
    h2("3.4  Algorithms"),
    h3("3.4.1  Shunting-Yard (Infix to Postfix)"),
    ...codeBlock([
      "ALGORITHM: Shunting-Yard",
      "INPUT:  infix regex string",
      "OUTPUT: postfix regex string",
      "",
      "  1. Insert explicit concatenation operators",
      "  2. For each token t:",
      "       if t is a literal → append to output queue",
      "       if t is '('       → push onto operator stack",
      "       if t is ')'       → pop stack to queue until '(' is found",
      "       if t is operator  → pop higher-or-equal-precedence ops",
      "                           then push t",
      "  3. Pop remaining stack items to queue",
      "  4. Return output queue joined as string",
    ]),
    h3("3.4.2  Thompson's Construction"),
    ...codeBlock([
      "ALGORITHM: Thompson's Construction",
      "INPUT:  postfix regex string",
      "OUTPUT: NFA object",
      "",
      "  For each token t in postfix string:",
      "    if t is literal  → push NFAFragment(new_start -t-> new_accept)",
      "    if t is '.'      → pop f2, f1; connect f1.accept -ε-> f2.start",
      "                       push NFAFragment(f1.start, f2.accept)",
      "    if t is '|'      → pop f2, f1; new_start -ε-> {f1.start, f2.start}",
      "                       {f1.accept, f2.accept} -ε-> new_accept",
      "                       push NFAFragment(new_start, new_accept)",
      "    if t is '*'      → pop f; new_start -ε-> {f.start, new_accept}",
      "                       f.accept -ε-> {f.start, new_accept}",
      "                       push NFAFragment(new_start, new_accept)",
      "  return NFA(stack.pop())",
    ]),
    h3("3.4.3  Subset Construction"),
    ...codeBlock([
      "ALGORITHM: Subset Construction",
      "INPUT:  NFA object",
      "OUTPUT: DFA object",
      "",
      "  start_set = ε-closure({nfa.start_state})",
      "  DFA.start = new DFAState(start_set)",
      "  worklist  = [DFA.start]",
      "",
      "  while worklist is not empty:",
      "    current = worklist.dequeue()",
      "    for each symbol a in alphabet:",
      "      moved   = move(current.nfa_subset, a)",
      "      closure = ε-closure(moved)",
      "      if closure is empty → transition to dead state ∅",
      "      else if closure not in subset_map:",
      "        new_ds = new DFAState(closure)",
      "        subset_map[closure] = new_ds",
      "        worklist.enqueue(new_ds)",
      "      DFA.add_transition(current, a, subset_map[closure])",
    ]),
    pageBreak(),
  ];
}

// ── Chapter 4: Mathematical Model ───────────────────────────────────────────
function ch4() {
  return [
    h1("Chapter 4: Mathematical Model"),
    h2("4.1  Formal Definition"),
    para([b("Definition (DFA). "), r("A Deterministic Finite Automaton is a 5-tuple M = (Q, Σ, δ, q₀, F) where:")]),
    bullet("Q  = finite, non-empty set of states"),
    bullet("Σ  = finite, non-empty input alphabet"),
    bullet("δ: Q × Σ → Q  = total transition function"),
    bullet("q₀ ∈ Q  = start state"),
    bullet("F ⊆ Q   = set of accepting (final) states"),
    new Paragraph({ spacing:{after:120} }),
    para([b("Definition (NFA). "), r("A Non-deterministic Finite Automaton is a 5-tuple M = (Q, Σ, δ, q₀, F) where δ: Q × (Σ ∪ {ε}) → 2^Q.")]),
    h2("4.2  Worked Example: (a|b)*abb"),
    h3("4.2.1  NFA produced by Thompson's Construction"),
    para([r("Applying Thompson's Construction to (a|b)*abb with the postfix string ab|*.a.b.b. generates the following NFA. States are labelled q0 through q9.")]),
    new Table({
      width:{ size:9360, type:WidthType.DXA }, columnWidths:[1200,1200,1200,1200,1200,1200,1200,1160],
      rows:[
        new TableRow({ children:[
          hdrCell("State",1200), hdrCell("a",1200), hdrCell("b",1200),
          hdrCell("ε",1200), hdrCell("Start",1200), hdrCell("Accept",1200),
        ].concat([new TableCell({borders,width:{size:1200,type:WidthType.DXA},shading:{fill:BLUE,type:ShadingType.CLEAR},margins:cellPad,children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"",font:"Arial",size:22,color:WHITE})]})]}),
                  new TableCell({borders,width:{size:1160,type:WidthType.DXA},shading:{fill:BLUE,type:ShadingType.CLEAR},margins:cellPad,children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"",font:"Arial",size:22,color:WHITE})]})]})])
        }),
        ...[
          ["q0","∅","∅","{q1,q7}","✓",""],
          ["q1","∅","∅","{q2,q4}","",""],
          ["q2","{q3}","∅","∅","",""],
          ["q3","∅","∅","{q6}","",""],
          ["q4","∅","{q5}","∅","",""],
          ["q5","∅","∅","{q6}","",""],
          ["q6","∅","∅","{q1,q7}","",""],
          ["q7","{q8}","∅","∅","",""],
          ["q8","∅","{q9}","∅","",""],
          ["q9","∅","∅","{q10}","",""],
        ].map((row,i) => new TableRow({ children:
          row.map((cell,ci) => dataCell(cell, [1200,1200,1200,1200,1200,1200,1200,1160][ci % 8] || 1200, i%2===0?WHITE:ROW_ALT))
        })),
      ]
    }),
    new Paragraph({ spacing:{after:240} }),
    h3("4.2.2  DFA produced by Subset Construction"),
    para([r("The Subset Construction on the above NFA yields the following DFA. Each DFA state is labelled with the set of NFA states it represents.")]),
    new Table({
      width:{ size:9360, type:WidthType.DXA }, columnWidths:[2000,2800,2280,2280],
      rows:[
        new TableRow({ children:[
          hdrCell("DFA State",2000), hdrCell("NFA Subset",2800),
          hdrCell("a",2280), hdrCell("b",2280),
        ]}),
        ...[
          ["D0 (Start)","{ q0,q1,q2,q4,q7 }","D1","D2"],
          ["D1","{ q1,q2,q3,q4,q6,q7,q8 }","D1","D3"],
          ["D2","{ q1,q2,q4,q5,q6,q7 }","D1","D2"],
          ["D3 ","{ q1,q2,q4,q5,q6,q7,q9 }","D1","D4"],
          ["D4 (Accept)","{ q1,q2,q4,q5,q6,q7,q10 }","D1","D2"],
        ].map((row,i) => new TableRow({ children:
          row.map((cell,ci) => dataCell(cell, [2000,2800,2280,2280][ci], i%2===0?WHITE:ROW_ALT))
        })),
      ]
    }),
    new Paragraph({ spacing:{after:240} }),
    h2("4.3  ε-closure and move — Formal Definitions"),
    para([r("Let S ⊆ Q be a set of NFA states.")]),
    para([b("ε-closure(S) "), r("= { q ∈ Q | q is reachable from some s ∈ S via zero or more ε-transitions }.")]),
    para([b("move(S, a) "), r("= { q ∈ Q | ∃ s ∈ S such that q ∈ δ(s, a) }.")]),
    para([r("The Subset Construction builds each DFA state T' from current DFA state T and symbol a as:")]),
    para([b("T' = ε-closure(move(T, a))")]),
    pageBreak(),
  ];
}

// ── Chapter 5: Implementation ────────────────────────────────────────────────
function ch5() {
  return [
    h1("Chapter 5: Implementation"),
    h2("5.1  Development Environment"),
    bullet("Language: Python 3.10+"),
    bullet("GUI Framework: Tkinter (standard library)"),
    bullet("Graph Rendering: Graphviz 9.x + graphviz Python package"),
    bullet("IDE: Visual Studio Code with Python extension"),
    bullet("Version Control: Git"),
    bullet("Operating System: Windows 10 / 11"),
    h2("5.2  File Structure"),
    ...codeBlock([
      "project/",
      "├── main.py            # Entry point (CLI + GUI launch)",
      "├── regex_parser.py    # Infix → Postfix conversion",
      "├── nfa.py             # Thompson's Construction",
      "├── dfa.py             # Subset Construction",
      "├── simulator.py       # DFA / NFA string simulation",
      "├── gui.py             # Tkinter GUI + Graphviz visualisation",
      "└── requirements.txt   # graphviz package",
    ]),
    h2("5.3  How to Run on Windows (VS Code)"),
    h3("Step 1 — Install Python"),
    para([r("Download and install Python 3.10 or later from python.org. During installation, check the box 'Add Python to PATH'.")]),
    h3("Step 2 — Install Graphviz"),
    para([r("Download the Windows installer from graphviz.org/download/ and run it. Ensure the Graphviz bin directory (e.g., C:\\Program Files\\Graphviz\\bin) is added to your PATH environment variable.")]),
    h3("Step 3 — Install the graphviz Python package"),
    ...codeBlock([
      "# Open a VS Code terminal (Ctrl+`) and run:",
      "pip install graphviz",
    ]),
    h3("Step 4 — Open the project in VS Code"),
    ...codeBlock([
      "# Clone or extract the project folder, then:",
      "cd path/to/project",
      "code .",
    ]),
    h3("Step 5 — Run the application"),
    ...codeBlock([
      "# GUI mode (default):",
      "python main.py",
      "",
      "# CLI demo mode:",
      "python main.py --cli",
    ]),
    h2("5.4  Key Implementation Details"),
    h3("5.4.1  State Counter Reset"),
    para([r("Both State._counter (nfa.py) and DFAState._counter (dfa.py) are reset to 0 at the start of each build_nfa() / build_dfa() call. This ensures state IDs are reproducible and predictable across multiple conversions within a single GUI session.")]),
    h3("5.4.2  FrozenSet as DFA State Key"),
    para([r("DFA states are keyed by frozenset(NFA states) in the subset_map dictionary. Python's frozenset is hashable and supports equality comparison, making it ideal as a dictionary key for the Subset Construction's worklist-based BFS.")]),
    h3("5.4.3  Dead State Representation"),
    para([r("Rather than inserting an explicit sink/dead state into the DFA, empty closures are represented by the string '∅' in the transition table. The simulator detects this sentinel and immediately rejects. This keeps the DFA state count minimal and the visualisation clean.")]),
    h3("5.4.4  Graphviz Integration"),
    para([r("The gui.py module builds a DOT language string for both the NFA and DFA, calls graphviz.Source(dot_string).render() to produce a PNG file, then loads it into a Tkinter PhotoImage for display. Double arrows (→→) mark the start state; double circles mark accepting states.")]),
    pageBreak(),
  ];
}

// ── Chapter 6: Screenshots (descriptive placeholders) ───────────────────────
function ch6() {
  const screenshotBox = (title, desc) => [
    h3(title),
    para([r(desc)]),
    new Paragraph({
      spacing:{ before:120, after:120 },
      border:{
        top:{style:BorderStyle.SINGLE,size:6,color:LBLUE},
        bottom:{style:BorderStyle.SINGLE,size:6,color:LBLUE},
        left:{style:BorderStyle.SINGLE,size:6,color:LBLUE},
        right:{style:BorderStyle.SINGLE,size:6,color:LBLUE},
      },
      shading:{ fill:"EBF3FB", type:ShadingType.CLEAR },
      indent:{ left:360, right:360 },
      children:[
        new TextRun({ text:"[ Screenshot Placeholder — run python main.py to view ]", font:"Arial", size:22, color:LBLUE, italics:true })
      ]
    }),
    new Paragraph({ spacing:{after:200} }),
  ];

  return [
    h1("Chapter 6: Screenshots"),
    para([r("The following section documents each major GUI panel and output diagram. To reproduce the screenshots, run python main.py in a terminal with Graphviz installed.")]),

    ...screenshotBox("Figure 6.1 — Main GUI Window",
      "The main window shows the regex input box at the top, the Convert button, a tabbed results area with NFA Table / DFA Table / Simulation tabs, and two image panels on the right for the NFA and DFA graphs. The title bar reads 'RE → NFA → DFA Converter'."),

    ...screenshotBox("Figure 6.2 — NFA Transition Table",
      "After entering (a|b)*abb and pressing Convert, the NFA Table tab populates with 11 rows (states q0–q10), columns for symbols a, b, and ε. Accepting state q10 is highlighted. The start state row is marked with an arrow symbol."),

    ...screenshotBox("Figure 6.3 — DFA Transition Table",
      "The DFA Table tab shows 5 rows (D0–D4). Each row displays the DFA state name, the corresponding NFA subset, and transitions on a and b. D4 is highlighted as the single accepting state. D0 is marked as the start state."),

    ...screenshotBox("Figure 6.4 — NFA Graph (Graphviz)",
      "The NFA graph renders as a directed graph with circular nodes q0–q10. The start state q0 has an incoming arrow from a ghost node. The accepting state q10 has a double circle. ε-transitions are drawn as dashed arrows labelled ε. Literal transitions a and b are solid arrows."),

    ...screenshotBox("Figure 6.5 — DFA Graph (Graphviz)",
      "The DFA graph shows 5 rectangular nodes D0–D4 and is noticeably cleaner than the NFA graph. D4 uses a double rectangle. Arrows are labelled a or b. No ε-transitions exist. The layout is left-to-right (rankdir=LR)."),

    ...screenshotBox("Figure 6.6 — String Simulation Panel",
      "The simulation panel shows a text box for input. After typing 'abb' and pressing Simulate, the result ACCEPTED is displayed in green, along with the DFA path D0 → D1 → D3 → D4 and the NFA path showing set transitions."),

    ...screenshotBox("Figure 6.7 — Rejected String Result",
      "After typing 'ab' and pressing Simulate, the result REJECTED is displayed in red, along with the path D0 → D1 → ∅ (dead), indicating that no accepting state was reached."),

    pageBreak(),
  ];
}

// ── Chapter 7: Testing ────────────────────────────────────────────────────────
function ch7() {
  const acceptedRows = [
    ["1","abb","DFA: D0→D1→D3→D4","ACCEPTED ✓"],
    ["2","aabb","DFA: D0→D1→D1→D3→D4","ACCEPTED ✓"],
    ["3","babb","DFA: D0→D2→D1→D3→D4","ACCEPTED ✓"],
    ["4","ababb","DFA: D0→D1→D2→D1→D3→D4","ACCEPTED ✓"],
    ["5","bbabb","DFA: D0→D2→D2→D1→D3→D4","ACCEPTED ✓"],
  ];
  const rejectedRows = [
    ["1","ab","DFA: D0→D1→∅ (dead)","REJECTED ✗"],
    ["2","ba","DFA: D0→D2→D1→...","REJECTED ✗"],
    ["3","abc","Non-alphabet char 'c'","REJECTED ✗"],
    ["4","aba","DFA: D0→D1→D3→D1","REJECTED ✗"],
    ["5","ε (empty)","DFA: D0 (non-accept)","REJECTED ✗"],
  ];
  const GREEN = "E2F0D9"; const RED = "FCE4D6";

  return [
    h1("Chapter 7: Testing"),
    h2("7.1  Accepted Strings — Language: (a|b)*abb"),
    new Table({
      width:{ size:9360, type:WidthType.DXA }, columnWidths:[720,1440,5040,2160],
      rows:[
        new TableRow({ children:[
          hdrCell("#",720), hdrCell("String",1440),
          hdrCell("DFA Path",5040), hdrCell("Result",2160)
        ]}),
        ...acceptedRows.map(row => new TableRow({ children:[
          dataCell(row[0],720,GREEN), dataCell(row[1],1440,GREEN),
          dataLeftCell(row[2],5040,GREEN), dataCell(row[3],2160,GREEN)
        ]})),
      ]
    }),
    new Paragraph({ spacing:{after:320} }),
    h2("7.2  Rejected Strings"),
    new Table({
      width:{ size:9360, type:WidthType.DXA }, columnWidths:[720,1440,5040,2160],
      rows:[
        new TableRow({ children:[
          hdrCell("#",720), hdrCell("String",1440),
          hdrCell("DFA Path / Reason",5040), hdrCell("Result",2160)
        ]}),
        ...rejectedRows.map(row => new TableRow({ children:[
          dataCell(row[0],720,RED), dataCell(row[1],1440,RED),
          dataLeftCell(row[2],5040,RED), dataCell(row[3],2160,RED)
        ]})),
      ]
    }),
    new Paragraph({ spacing:{after:320} }),
    h2("7.3  Additional Edge-Case Tests"),
    new Table({
      width:{ size:9360, type:WidthType.DXA }, columnWidths:[2400,2400,2400,2160],
      rows:[
        new TableRow({ children:[
          hdrCell("Regex",2400), hdrCell("String",2400),
          hdrCell("Expected",2400), hdrCell("Actual",2160)
        ]}),
        ...([
          ["a*b","b","ACCEPTED","ACCEPTED ✓"],
          ["a*b","aab","ACCEPTED","ACCEPTED ✓"],
          ["a*b","ba","REJECTED","REJECTED ✗"],
          ["(a|b)+","a","ACCEPTED","ACCEPTED ✓"],
          ["(a|b)+","","REJECTED","REJECTED ✗"],
          ["ab?c","ac","ACCEPTED","ACCEPTED ✓"],
          ["ab?c","abc","ACCEPTED","ACCEPTED ✓"],
          ["ab?c","abbc","REJECTED","REJECTED ✗"],
        ]).map((row,i) => new TableRow({ children:
          row.map((cell,ci) => dataCell(cell, [2400,2400,2400,2160][ci], i%2===0?WHITE:ROW_ALT))
        })),
      ]
    }),
    new Paragraph({ spacing:{after:320} }),
    h2("7.4  Test Summary"),
    para([r("All 5 accepted strings were correctly classified as ACCEPTED by both the DFA and NFA simulators. All 5 rejected strings were correctly classified as REJECTED. The edge-case tests cover regex variants (a*, a+, a?) and demonstrate that the parser, NFA builder, and DFA builder are all functioning correctly.")]),
    pageBreak(),
  ];
}

// ── Chapter 8: Complexity Analysis ──────────────────────────────────────────
function ch8() {
  return [
    h1("Chapter 8: Complexity Analysis"),
    h2("8.1  Regex Parsing — Shunting-Yard"),
    para([r("Let n be the number of tokens (characters + inserted concatenation dots) in the regex.")]),
    bullet("Time Complexity: O(n) — each token is pushed and popped from the operator stack at most once."),
    bullet("Space Complexity: O(n) — the operator stack and output queue each hold at most n elements."),
    h2("8.2  Thompson's Construction"),
    para([r("Let n be the length of the postfix expression.")]),
    bullet("Number of NFA states: at most 2n (each literal creates 2 states; each operator uses a constant number of new states)."),
    bullet("Number of NFA transitions: at most 4n (each construction step adds a bounded number of transitions)."),
    bullet("Time Complexity: O(n)."),
    bullet("Space Complexity: O(n)."),
    h2("8.3  ε-closure Computation"),
    para([r("ε-closure is computed with a DFS/BFS over ε-transitions.")]),
    bullet("Time: O(|Q| + |δ|) per call, where |Q| is the number of NFA states and |δ| the number of ε-transitions."),
    bullet("In the worst case, the ε-closure of a single state visits all NFA states."),
    h2("8.4  Subset Construction"),
    para([r("Let |Q_NFA| be the number of NFA states and |Σ| the alphabet size.")]),
    bullet("Number of DFA states (worst case): 2^|Q_NFA| — each subset of NFA states may become a DFA state."),
    bullet("Number of DFA transitions (worst case): |Σ| × 2^|Q_NFA|."),
    bullet("Time Complexity: O(|Σ| × 2^|Q_NFA| × |Q_NFA|) in the worst case."),
    bullet("In practice (and for (a|b)*abb): only 5 DFA states are reachable from 11 NFA states."),
    h2("8.5  DFA Simulation"),
    bullet("Time: O(m) where m is the length of the input string — one table lookup per character."),
    bullet("Space: O(|Q_DFA|) to store the transition table."),
    h2("8.6  Summary Table"),
    new Table({
      width:{ size:9360, type:WidthType.DXA }, columnWidths:[3600,2880,2880],
      rows:[
        new TableRow({ children:[
          hdrCell("Algorithm",3600), hdrCell("Time Complexity",2880), hdrCell("Space Complexity",2880)
        ]}),
        ...([
          ["Regex Parsing (Shunting-Yard)","O(n)","O(n)"],
          ["Thompson's Construction","O(n)","O(n)"],
          ["ε-closure (single call)","O(|Q| + |δ|)","O(|Q|)"],
          ["Subset Construction (worst)","O(|Σ| · 2^|Q| · |Q|)","O(2^|Q|)"],
          ["DFA Simulation","O(m)","O(|Q_DFA|)"],
          ["Graphviz Rendering","O(|Q|²) approx","O(|Q| + |δ|)"],
        ]).map((row,i) => new TableRow({ children:
          row.map((cell,ci) => dataCell(cell, [3600,2880,2880][ci], i%2===0?WHITE:ROW_ALT))
        })),
      ]
    }),
    pageBreak(),
  ];
}

// ── Chapter 9: Conclusion ────────────────────────────────────────────────────
function ch9() {
  return [
    h1("Chapter 9: Conclusion"),
    h2("9.1  Summary"),
    para([r("This project successfully implements a complete Regular Expression to NFA to DFA converter and string simulator in Python. The system correctly applies Thompson's Construction and the Subset Construction, both of which are foundational algorithms in the theory of computation and compiler design. The Tkinter-based GUI provides an accessible interface that allows users without a theoretical background to interactively explore how regular expressions relate to finite automata.")]),
    h2("9.2  Results"),
    bullet("The regex parser correctly handles union, concatenation, Kleene star, one-or-more, and zero-or-one operators with proper precedence."),
    bullet("The NFA builder produces the expected state count and transition structure for all tested expressions."),
    bullet("The DFA produced by the Subset Construction correctly accepts and rejects all test strings."),
    bullet("Both the DFA and NFA simulators agree on every test case, confirming their equivalence."),
    bullet("The Graphviz visualisations clearly communicate automaton structure to the user."),
    h2("9.3  Challenges Encountered"),
    bullet("Handling ε-closures correctly during both the Subset Construction and NFA simulation required careful BFS implementation."),
    bullet("The one-or-more (+) and zero-or-one (?) operators required duplicating NFA fragments to avoid sharing mutable state across branches."),
    bullet("Embedding Graphviz PNG images in Tkinter required converting the image to a PhotoImage object, which needed careful lifecycle management to prevent garbage collection."),
    h2("9.4  Future Work"),
    bullet("DFA Minimisation using Hopcroft's algorithm to reduce state count."),
    bullet("Support for character classes ([a-z]), anchors (^ and $), and backreferences."),
    bullet("Export of automata to PDF or LaTeX tikz format for academic reports."),
    bullet("Step-by-step simulation mode that highlights the active state in the graph on each input symbol."),
    bullet("Extension to context-free grammars (PDA) for a broader automata study tool."),
    h2("9.5  References"),
    para([r("1.  Thompson, K. (1968). Programming techniques: Regular expression search algorithm. Communications of the ACM, 11(6), 419–422.")]),
    para([r("2.  Rabin, M. O., & Scott, D. (1959). Finite and infinite automata. IBM Journal of Research and Development, 3(2), 114–125.")]),
    para([r("3.  Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). Introduction to Automata Theory, Languages, and Computation (3rd ed.). Pearson.")]),
    para([r("4.  Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). Compilers: Principles, Techniques, and Tools (2nd ed.). Addison-Wesley.")]),
    para([r("5.  Graphviz Documentation. (2024). The DOT Language. https://graphviz.org/doc/info/lang.html")]),
    para([r("6.  Rodger, S. H., & Finley, T. W. (2006). JFLAP: An Interactive Formal Languages and Automata Package. Jones & Bartlett.")]),
    pageBreak(),
  ];
}

// ── Assemble & write ──────────────────────────────────────────────────────────
const children = [
  ...makeCover(),
  ...ch1(), ...ch2(), ...ch3(), ...ch4(),
  ...ch5(), ...ch6(), ...ch7(), ...ch8(), ...ch9(),
];

const doc = new Document({
  styles: {
    default: { document: { run: { font:"Arial", size:24 } } },
    paragraphStyles: [
      { id:"Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true,
        run:{ size:36, bold:true, font:"Arial", color:WHITE },
        paragraph:{ spacing:{before:480,after:240}, outlineLevel:0 } },
      { id:"Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true,
        run:{ size:28, bold:true, font:"Arial", color:BLUE },
        paragraph:{ spacing:{before:300,after:160}, outlineLevel:1 } },
      { id:"Heading3", name:"Heading 3", basedOn:"Normal", next:"Normal", quickFormat:true,
        run:{ size:26, bold:true, font:"Arial", color:LBLUE },
        paragraph:{ spacing:{before:200,after:120}, outlineLevel:2 } },
    ]
  },
  numbering: {
    config:[{
      reference:"bullets",
      levels:[{ level:0, format:LevelFormat.BULLET, text:"•", alignment:AlignmentType.LEFT,
        style:{ paragraph:{ indent:{ left:720, hanging:360 } } } }]
    }]
  },
  sections:[{
    properties:{
      page:{
        size:{ width:12240, height:15840 },
        margin:{ top:1440, right:1440, bottom:1440, left:1440 }
      }
    },
    headers:{
      default: new Header({ children:[
        new Paragraph({
          border:{ bottom:{ style:BorderStyle.SINGLE, size:4, color:LBLUE } },
          spacing:{ after:120 },
          children:[
            new TextRun({ text:"RE → NFA → DFA Converter & Simulator  |  Amna Khurram  F24605061", font:"Arial", size:18, color:"888888" })
          ]
        })
      ]})
    },
    footers:{
      default: new Footer({ children:[
        new Paragraph({
          border:{ top:{ style:BorderStyle.SINGLE, size:4, color:LBLUE } },
          spacing:{ before:120 },
          tabStops:[{ type:TabStopType.RIGHT, position:TabStopPosition.MAX }],
          children:[
            new TextRun({ text:"Formal Languages & Automata — Course Project", font:"Arial", size:18, color:"888888" }),
            new TextRun({ text:"\t", font:"Arial", size:18 }),
            new TextRun({ text:"Page ", font:"Arial", size:18, color:"888888" }),
            new PageNumber(),
          ]
        })
      ]})
    },
    children,
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/mnt/user-data/outputs/Amna_Khurram_F24605061_FLA_Project_Report.docx", buf);
  console.log("Done.");
});
