"""
Automated Project Report Generator
Constructs a comprehensive, publication-grade academic Word document (project_report.docx)
strictly adhering to the Adani University PBL Applied AI Project Track guidelines.
"""

import os
import sys
import csv
import subprocess
from datetime import datetime
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "documentation"))
CHARTS_DIR = os.path.join(DOC_DIR, "charts")
SCREENSHOTS_DIR = os.path.join(DOC_DIR, "screenshots")
BENCHMARK_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "benchmarks", "results.csv"))
ORDERING_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "benchmarks", "ordering_results.csv"))


def set_cell_background(cell, hex_color: str):
    """Sets background shading of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Sets internal padding for a table cell (in twips: 20 twips = 1 pt)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def get_git_history():
    """Retrieves the genuine Git commit history directly via git log."""
    try:
        cmd = ["git", "log", "--pretty=format:%h|%ad|%s", "--date=short"]
        out = subprocess.check_output(cmd, encoding="utf-8").strip()
        lines = out.split("\n")
        commits = []
        for line in lines:
            if "|" in line:
                parts = line.split("|", 2)
                commits.append({
                    "hash": parts[0],
                    "date": parts[1],
                    "message": parts[2],
                })
        return commits
    except Exception as e:
        print(f"Error reading git history: {e}")
        return []


def create_document():
    doc = docx.Document()

    # Page Margins (1 inch everywhere)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.header.is_linked_to_previous = False

    # Palette Constants
    COLOR_PRIMARY = RGBColor(15, 23, 42)     # Deep Slate #0F172A
    COLOR_NAVY = RGBColor(30, 58, 138)       # Royal Navy #1E3A8A
    COLOR_TEAL = RGBColor(13, 148, 136)      # Teal #0D9488
    COLOR_MUTED = RGBColor(100, 116, 139)    # Muted Slate #64748B
    COLOR_BODY = RGBColor(51, 65, 85)        # Text Body #334155

    # Base Normal Style
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_BODY
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # TITLE PAGE
    # -------------------------------------------------------------
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_before = Pt(36)
    p_uni.paragraph_format.space_after = Pt(2)
    run_uni = p_uni.add_run("ADANI UNIVERSITY")
    run_uni.font.size = Pt(18)
    run_uni.font.bold = True
    run_uni.font.color.rgb = COLOR_NAVY

    p_fest = doc.add_paragraph()
    p_fest.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fest.paragraph_format.space_after = Pt(2)
    run_fest = p_fest.add_run("Faculty of Engineering Sciences and Technology (FEST)")
    run_fest.font.size = Pt(13)
    run_fest.font.color.rgb = COLOR_PRIMARY

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(18)
    run_dept = p_dept.add_run("Department of Computer Science and Engineering (AI-ML)")
    run_dept.font.size = Pt(12)
    run_dept.font.color.rgb = COLOR_MUTED

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(24)
    run_div = p_div.add_run("—" * 35)
    run_div.font.color.rgb = COLOR_TEAL

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_after = Pt(8)
    run_course = p_course.add_run("PROJECT-BASED LEARNING (PBL) REPORT\nCourse: ECSCT24301 – Foundation of AI")
    run_course.font.size = Pt(12)
    run_course.font.bold = True
    run_course.font.color.rgb = COLOR_NAVY

    p_track = doc.add_paragraph()
    p_track.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_track.paragraph_format.space_after = Pt(24)
    run_track = p_track.add_run("Track: Applied AI Project Track")
    run_track.font.size = Pt(11)
    run_track.font.italic = True
    run_track.font.color.rgb = COLOR_TEAL

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(36)
    run_title = p_title.add_run("Interactive Alpha-Beta Pruning Simulator\nfor Adversarial Game-Tree Search")
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    # Team & Faculty Metadata Table
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Student Team Members:", "1. Lokesh Lohar (Enrollment: 2410111059)\n2. Panchal Naren Shaileshbhai (Enrollment: 2410111076)"),
        ("Department & Division:", "B.Tech CSE (AI-ML), Division / Batch: Festive 2024–28"),
        ("Supervisor / Faculty Mentor:", "[Faculty Mentor / Supervisor Name]"),
        ("Academic Year:", "2026–27"),
        ("Submission Date:", "November 2026"),
    ]
    for row_idx, (lbl, val) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        row.cells[0].paragraphs[0].add_run(lbl).bold = True
        row.cells[0].paragraphs[0].runs[0].font.size = Pt(10)
        row.cells[0].paragraphs[0].runs[0].font.color.rgb = COLOR_PRIMARY
        row.cells[1].paragraphs[0].add_run(val)
        row.cells[1].paragraphs[0].runs[0].font.size = Pt(10)
        set_cell_margins(row.cells[0], top=80, bottom=80, left=100, right=100)
        set_cell_margins(row.cells[1], top=80, bottom=80, left=100, right=100)
        set_cell_background(row.cells[0], "F1F5F9")
        set_cell_background(row.cells[1], "FFFFFF")

    doc.add_page_break()

    # Helper function for Section Headings
    def add_h1(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = COLOR_NAVY
        return p

    def add_h2(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEAL
        return p

    def add_h3(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        return p

    def add_caption(text: str):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(12)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.italic = True
        r.font.color.rgb = COLOR_MUTED
        return p

    def add_code_block(code_text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.right_indent = Inches(0.2)
        r = p.add_run(code_text)
        r.font.name = "Consolas"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    # -------------------------------------------------------------
    # ABSTRACT / EXECUTIVE SUMMARY
    # -------------------------------------------------------------
    add_h1("Abstract / Executive Summary")
    doc.add_paragraph(
        "Adversarial search algorithms form the foundational underpinning of artificial intelligence systems designed "
        "for competitive, turn-based, multi-agent decision environments. In two-player, zero-sum games with perfect information, "
        "the classical Minimax algorithm determines optimal moves under the assumption of rational opposition; however, its "
        "exhaustive depth-first traversal incurs an exponential computational time complexity of O(b^d), where b represents the "
        "effective branching factor and d denotes the search depth. Alpha-Beta Pruning addresses this fundamental computational "
        "bottleneck by dynamically tracking guaranteed lower (alpha) and upper (beta) utility bounds along the search path, "
        "safely eliminating subtrees that cannot influence the final root decision."
    )
    doc.add_paragraph(
        "This project develops an Interactive Alpha-Beta Pruning Simulator built entirely in Python using Tkinter. Designed "
        "specifically for educational clarity and academic rigor, the software incorporates an event-driven trace architecture that "
        "decouples algorithm traversal from graphical rendering. Users can generate canonical textbook game trees or parameterized "
        "random configurations, inspect real-time alpha and beta updates, execute manual single-stepping or continuous animated "
        "playback, and visually examine cut-off markers on pruned branches. Furthermore, an integrated empirical benchmarking "
        "framework systematically evaluates Minimax versus Alpha-Beta across varying depths (d=2 to 6) and branching factors (b=2 to 4). "
        "Experimental results demonstrate that Alpha-Beta Pruning achieves pruning efficiencies up to 69.42% under optimal move "
        "ordering while strictly preserving the mathematical optimality of the root decision. A dedicated ablation study demonstrates "
        "how worst-case move ordering degenerates Alpha-Beta's efficiency to zero, empirically confirming classic theoretical theorems. "
        "The modular, minimal-dependency codebase enables second-year computer science undergraduates to understand and defend every "
        "critical algorithmic mechanism during individual oral examinations."
    )

    # -------------------------------------------------------------
    # 1. INTRODUCTION & BACKGROUND
    # -------------------------------------------------------------
    add_h1("1. Introduction & Background")
    doc.add_paragraph(
        "Game playing has occupied a central position in artificial intelligence since the inception of the field. "
        "Unlike single-agent heuristic search problems—such as route planning or puzzle solving where an agent operates against a "
        "static environment—adversarial search introduces a hostile competitor whose actions directly counteract the agent's goals. "
        "In a zero-sum formulation, any utility gained by one player corresponds to an equal and opposite loss for the opponent. "
        "Consequently, decision-making requires anticipating counter-responses to arbitrary depths of rational play."
    )
    doc.add_paragraph(
        "The classical Minimax procedure, formulated mathematically by John von Neumann in his minimax theorem and formalized in AI "
        "by Claude Shannon (1950), provides a systematic method for computing the equilibrium strategy. However, because Minimax must "
        "visit every terminal state up to the search horizon, practical games rapidly overwhelm computational memory and processing limits. "
        "For example, in chess with an average branching factor of approximately 35 and typical game depths exceeding 80 plies, complete "
        "exploration is physically impossible."
    )
    doc.add_paragraph(
        "Alpha-Beta Pruning, analyzed formally by Donald Knuth and Ronald W. Moore (1975), optimizes adversarial search by recognizing "
        "that large sections of the game tree are irrelevant to rational play. If an alternative already guarantees a score superior to "
        "what the opponent would permit in another subtree, further evaluation of that subtree is superfluous. While textbooks "
        "present the mathematical inequality alpha >= beta concisely, students often struggle to visualize the dynamic propagation of "
        "these bounds during recursive backtracking."
    )
    doc.add_paragraph(
        "The primary motivation of this project is to bridge the conceptual gap between theoretical formulation and observable "
        "algorithmic execution. By developing a clean, accessible graphical simulator with discrete step-by-step trace replay and "
        "rigorous empirical benchmarks, this project fulfills the Adani University Applied AI Project Track objectives for Course ECSCT24301."
    )

    # -------------------------------------------------------------
    # 2. PROBLEM FORMULATION & ENVIRONMENT MODELING
    # -------------------------------------------------------------
    add_h1("2. Problem Formulation & Environment Modeling")
    doc.add_paragraph(
        "To rigorously formalize the adversarial decision environment, we model the search problem following the standard "
        "artificial intelligence agent paradigm articulated by Russell and Norvig (2021). The problem is characterized as an "
        "abstract zero-sum, two-player perfect-information adversarial game tree."
    )

    add_h2("2.1 PEAS Specification")
    doc.add_paragraph(
        "The Performance Measure, Environment, Actuators, and Sensors (PEAS) specification for the simulator agent is detailed in Table 1."
    )

    # PEAS Table
    peas_table = doc.add_table(rows=5, cols=2)
    peas_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    peas_data = [
        ("Performance Measure", "1. Mathematical optimality of the chosen root action (must match full Minimax decision).\n"
                                "2. Search efficiency: reduction in visited nodes and terminal leaf evaluations.\n"
                                "3. Pruning efficiency percentage: ((Nodes_MM - Nodes_AB) / Nodes_MM) * 100.\n"
                                "4. Computational execution time (measured wall-clock milliseconds).\n"
                                "5. Minimal memory footprint and recursion stack depth bounded by O(b*d)."),
        ("Environment", "Deterministic, fully observable, discrete, turn-based, two-player zero-sum game tree. "
                        "Successor states are generated through explicit branching factors (b in {2, 3, 4}) up to search depth d."),
        ("Actuators", "1. Traverse to child node (downward depth-first expansion).\n"
                      "2. Backtrack to parent node with backed-up utility value.\n"
                      "3. Update alpha bound (at MAX nodes) or beta bound (at MIN nodes).\n"
                      "4. Execute branch cutoff when alpha >= beta and prune sibling subtrees.\n"
                      "5. Emit graphical trace events to the interactive visualizer."),
        ("Sensors", "1. Current node state identity, depth, and player role (MAX vs. MIN).\n"
                    "2. Node type detector (terminal leaf vs. internal non-terminal state).\n"
                    "3. Current static leaf utility value.\n"
                    "4. Inherited path bounds (alpha and beta values from ancestor nodes)."),
    ]
    for r_idx, (elem, desc) in enumerate(peas_data):
        row = peas_table.rows[r_idx]
        row.cells[0].paragraphs[0].add_run(elem).bold = True
        row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
        row.cells[1].paragraphs[0].add_run(desc)
        row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_margins(row.cells[0], top=100, bottom=100, left=120, right=120)
        set_cell_margins(row.cells[1], top=100, bottom=100, left=120, right=120)
        set_cell_background(row.cells[0], "F1F5F9")
        set_cell_background(row.cells[1], "FFFFFF")

    add_caption("Table 1: Formal PEAS Specification for Adversarial Search Agent")

    add_h2("2.2 Mathematical Environment Modeling")
    doc.add_paragraph(
        "The adversarial decision problem is modeled formally as a tuple (S, A, T, s0, Terminal, Utility):"
    )
    doc.add_paragraph(
        "• State Space (S): The set of all valid configurations in the game tree. Each state s in S encodes its tree depth, "
        "active player to move (Player(s) in {MAX, MIN}), and associated subtree topology.\n"
        "• Initial State (s0): The root node of the tree at depth 0, where it is MAX's turn to move.\n"
        "• Actions (A(s)): The set of legal moves available from state s. In our game-tree model, Actions(s) corresponds to "
        "selecting one of the b directed branches leading to successor children.\n"
        "• Transition Model (T(s, a)): A deterministic function mapping state s and action a to a unique successor state s'. "
        "Because the game possesses perfect information, no stochasticity or hidden state exists.\n"
        "• Terminal Test (Terminal(s)): A predicate returning True if s has no children or if depth(s) == d. "
        "States satisfying this condition are leaf nodes.\n"
        "• Utility Function (Utility(s)): A real-valued static evaluation function defined strictly on terminal states s in Leaf(S). "
        "Higher positive values favor MAX; lower negative values favor MIN.\n"
        "• Path Cost Function: Unlike single-agent shortest-path problems (e.g., A* or Dijkstra's algorithm where edge traversal costs "
        "accumulate), adversarial zero-sum games have no path-cost function. The quality of a decision depends entirely on the terminal "
        "utility achieved under optimal opposing play, not the depth or cost of the steps taken to reach that terminal state."
    )

    # -------------------------------------------------------------
    # 3. LITERATURE REVIEW / RELATED WORK
    # -------------------------------------------------------------
    add_h1("3. Literature Review / Related Work")
    doc.add_paragraph(
        "The foundations of adversarial search were laid by Claude Shannon (1950) in his seminal paper 'Programming a Computer for "
        "Playing Chess'. Shannon formalized the minimax decision rule and distinguished between Type-A strategies (brute-force "
        "depth-limited minimax search) and Type-B strategies (selective search using domain knowledge). Shannon recognized that Type-A "
        "brute-force search experiences combinatorial explosion as the depth horizon expands."
    )
    doc.add_paragraph(
        "The concept of branch-and-bound pruning in game trees was independently discovered by several researchers in the late 1950s "
        "and 1960s, including John McCarthy, Arthur Samuel, and Alexander Brudno. However, the definitive mathematical treatment was "
        "provided by Donald Knuth and Ronald W. Moore (1975) in 'An Analysis of Alpha-Beta Pruning'. Knuth and Moore proved that if "
        "the child nodes at every step are ordered optimally (best move examined first), Alpha-Beta Pruning examines only O(b^(d/2)) "
        "nodes compared to Minimax's O(b^d). This theoretical doubling of the effective search horizon represented a monumental breakthrough."
    )
    doc.add_paragraph(
        "Subsequent historical milestones demonstrated the practical power of alpha-beta variants. Deep Blue (Campbell, Hoane, & Hsu, 2002) "
        "utilized non-uniform alpha-beta search combined with specialized chess hardware, quiescent search, and transposition tables to "
        "defeat World Chess Champion Garry Kasparov in 1997. In recent years, while Monte Carlo Tree Search (MCTS) combined with deep neural "
        "networks has achieved dominance in games with enormous branching factors such as Go (Silver et al., 2016), Alpha-Beta Pruning "
        "remains the standard baseline and industrial workhorse for classical adversarial reasoning."
    )
    doc.add_paragraph(
        "Within computer science education, literature emphasizes that active visualization significantly improves student comprehension "
        "of recursive backtracking algorithms. Traditional static chalk-and-board diagrams fail to capture the dynamic propagation of alpha "
        "and beta bounds. The simulator developed herein addresses this pedagogical need by providing step-by-step visual animation."
    )

    # -------------------------------------------------------------
    # 4. METHODOLOGY & ALGORITHMIC ARCHITECTURE
    # -------------------------------------------------------------
    add_h1("4. Methodology & Algorithmic Architecture")
    doc.add_paragraph(
        "The core mathematical framework encompasses the Minimax value propagation rules and the dynamic bounding constraints of Alpha-Beta Pruning."
    )

    add_h2("4.1 Minimax Formulation")
    doc.add_paragraph(
        "For any state s in the game tree, the minimax value V(s) is defined recursively as:\n"
        "V(s) = Utility(s)                                   if Terminal(s)\n"
        "V(s) = max_{a in Actions(s)} V(Result(s, a))         if Player(s) = MAX\n"
        "V(s) = min_{a in Actions(s)} V(Result(s, a))         if Player(s) = MIN"
    )
    doc.add_paragraph(
        "Minimax performs a full depth-first traversal of the game tree. At MAX nodes, it initializes the current maximum value to -infinity "
        "and updates it whenever a child returns a higher value. At MIN nodes, it initializes the current minimum to +infinity and updates "
        "it whenever a child returns a lower value."
    )

    add_h2("4.2 Alpha-Beta Pruning Formulation")
    doc.add_paragraph(
        "Alpha-Beta Pruning maintains two state variables along the active search path:\n"
        "• alpha (α): The utility value of the best choice found so far along the path for the MAX player (initialized to -infinity).\n"
        "• beta  (β): The utility value of the best choice found so far along the path for the MIN player (initialized to +infinity)."
    )
    doc.add_paragraph(
        "At a MAX node n, after evaluating a child c with value v, the bounds are updated as:\n"
        "alpha = max(alpha, v)\n"
        "If alpha >= beta, a BETA CUTOFF occurs. The parent or an ancestor node already has a guaranteed option that will yield at most "
        "beta to the opponent; therefore, the opponent will never allow play to reach a state yielding alpha >= beta. The remaining children "
        "of n are pruned immediately."
    )
    doc.add_paragraph(
        "Conversely, at a MIN node m, after evaluating a child c with value v, the bounds are updated as:\n"
        "beta = min(beta, v)\n"
        "If beta <= alpha (which is equivalent to alpha >= beta), an ALPHA CUTOFF occurs. The MAX player already possesses a choice at an "
        "ancestor level guaranteeing at least alpha; hence, MAX will never select the branch leading to m. The remaining children of m are pruned."
    )

    add_h2("4.3 Algorithmic Pseudocode")
    doc.add_paragraph("The algorithmic logic for Alpha-Beta Pruning implemented in the simulator is shown below:")

    add_code_block(
        "function ALPHA-BETA-SEARCH(state) returns an action\n"
        "    v, best_action = MAX-VALUE(state, -infinity, +infinity)\n"
        "    return best_action\n\n"
        "function MAX-VALUE(state, alpha, beta) returns (utility, action)\n"
        "    if TERMINAL-TEST(state) then return UTILITY(state), null\n"
        "    v = -infinity; best_act = null\n"
        "    for each a in ACTIONS(state) do\n"
        "        v2, _ = MIN-VALUE(RESULT(state, a), alpha, beta)\n"
        "        if v2 > v then\n"
        "            v = v2; best_act = a\n"
        "        alpha = max(alpha, v)\n"
        "        if alpha >= beta then\n"
        "            PRUNE remaining actions in ACTIONS(state)  // Beta cutoff\n"
        "            break\n"
        "    return v, best_act\n\n"
        "function MIN-VALUE(state, alpha, beta) returns (utility, action)\n"
        "    if TERMINAL-TEST(state) then return UTILITY(state), null\n"
        "    v = +infinity; best_act = null\n"
        "    for each a in ACTIONS(state) do\n"
        "        v2, _ = MAX-VALUE(RESULT(state, a), alpha, beta)\n"
        "        if v2 < v then\n"
        "            v = v2; best_act = a\n"
        "        beta = min(beta, v)\n"
        "        if alpha >= beta then\n"
        "            PRUNE remaining actions in ACTIONS(state)  // Alpha cutoff\n"
        "            break\n"
        "    return v, best_act"
    )

    add_h2("4.4 Theoretical Complexity Analysis")
    doc.add_paragraph(
        "Let b denote the uniform branching factor and d denote the maximum search depth:\n"
        "• Minimax Time Complexity: O(b^d). Minimax is obliged to evaluate all b^d terminal leaf states and (b^(d+1) - 1)/(b - 1) total tree nodes.\n"
        "• Alpha-Beta Worst-Case Time Complexity: O(b^d). If child states are ordered in the worst possible sequence (e.g., worst moves evaluated "
        "first), alpha and beta bounds never tighten sufficiently to satisfy alpha >= beta until all branches are explored.\n"
        "• Alpha-Beta Best-Case Time Complexity: O(b^(d/2)). If optimal moves are explored first at every decision point, Alpha-Beta evaluates "
        "approximately 2 * b^(d/2) - 1 terminal states. This effectively halves the exponent, allowing an agent with a fixed compute budget "
        "to search twice as deep as standard Minimax.\n"
        "• Space Complexity: O(b * d) for both algorithms. Because both algorithms utilize depth-first recursive traversal, memory requirements "
        "scale linearly with search depth, storing only the active path and sibling alternatives on the call stack."
    )

    # -------------------------------------------------------------
    # 5. IMPLEMENTATION DETAILS
    # -------------------------------------------------------------
    add_h1("5. Implementation Details")
    doc.add_paragraph(
        "The project architecture is organized modularly to preserve clear separation of concerns, maintain minimal dependencies, "
        "and ensure code readability for undergraduate academic presentation."
    )

    add_h2("5.1 Modular Architecture")
    doc.add_paragraph(
        "The repository contains the following modular components:\n"
        "• core/game_tree.py: Defines the Node data structure storing state attributes (node_id, depth, is_max, value, alpha, beta, "
        "status, children, parent, and canvas coordinates x, y).\n"
        "• core/tree_generator.py: Generates canonical textbook trees, full binary trees, and parameterized random trees with balanced "
        "geometric 2D canvas coordinates.\n"
        "• algorithms/minimax.py: Scratch implementation of standard Minimax with event logging.\n"
        "• algorithms/alpha_beta.py: Scratch implementation of Alpha-Beta Pruning with recursive cutoffs and event logging.\n"
        "• algorithms/trace.py: Data structures (SearchEvent, SearchResult) enabling execution recording and discrete GUI replay.\n"
        "• gui/tree_visualizer.py: Dedicated Tkinter Canvas renderer supporting smooth line drawing, polygonal nodes (▲ for MAX, ▼ for MIN, "
        "● for Leaves), visual status coloring, scissor cut markers, and optimal path highlights.\n"
        "• gui/controls.py: Control panel providing tree configuration spinboxes, search execution buttons, single-step and autoplay "
        "controls, speed slider, live metrics dashboard, and educational step narration.\n"
        "• gui/main_window.py: Primary application window assembling all UI components and hosting the side-by-side comparison modal.\n"
        "• benchmarks/benchmark.py: Multi-trial empirical testing suite evaluating runtime, node counts, and move-ordering effects.\n"
        "• benchmarks/generate_charts.py: Publication-quality Matplotlib chart generator producing 300 DPI comparative graphics.\n"
        "• tests/: Comprehensive unittest suite covering small, medium, degenerate, and equivalence test cases."
    )

    add_h2("5.2 Event Tracing and GUI Separation")
    doc.add_paragraph(
        "A critical architectural requirement was separating algorithm execution from GUI rendering. Rather than embedding Tkinter "
        "GUI calls inside recursive search functions—which leads to brittle, unmaintainable code—the algorithms execute purely in "
        "memory, generating a chronological sequence of SearchEvent objects. Each event captures the step index, event type ('VISIT', "
        "'UPDATE_BOUNDS', 'PRUNE', 'EVAL_LEAF', 'FINISH_NODE', 'DECISION'), active node ID, current alpha/beta values, and an "
        "educational explanation string. The GUI visualizer simply steps through this trace at the user's chosen speed."
    )

    # -------------------------------------------------------------
    # 6. EXPERIMENTAL DESIGN & SETUP
    # -------------------------------------------------------------
    add_h1("6. Experimental Design & Setup")
    doc.add_paragraph(
        "All experiments were conducted on a dedicated testing machine running 64-bit Windows 11 with an AMD64 architecture processor "
        "and Python 3.14.3. The experimental harness utilizes Python's high-resolution performance counter (time.perf_counter) to "
        "measure execution latencies with microsecond precision."
    )
    doc.add_paragraph(
        "To ensure statistical robustness and eliminate operating system scheduling noise, each benchmark configuration was executed across "
        "five independent trials, with median execution times reported. The benchmark matrix evaluates combinations of branching "
        "factor b in {2, 3, 4} and depth d in {2, 3, 4, 5, 6}, generating tree sizes ranging from 7 to 364 total nodes. "
        "A separate ablation experiment investigates the impact of move ordering by pre-sorting child subtrees into best-case "
        "(favorable moves first), random, and worst-case (unfavorable moves first) exploration sequences."
    )

    # -------------------------------------------------------------
    # 7. RESULTS & COMPARATIVE ANALYSIS
    # -------------------------------------------------------------
    add_h1("7. Results & Comparative Analysis")
    doc.add_paragraph(
        "Table 2 displays the actual, measured empirical benchmark results across 12 distinct game-tree configurations. "
        "In every single test case, Minimax and Alpha-Beta returned 100% identical root utility values, confirming mathematical optimality."
    )

    # Load real benchmark data from CSV
    results_rows = []
    if os.path.exists(BENCHMARK_CSV):
        with open(BENCHMARK_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results_rows.append(row)

    if results_rows:
        res_table = doc.add_table(rows=len(results_rows) + 1, cols=8)
        res_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        col_headers = ["Config (b, d)", "Tree Nodes", "Root Val", "MM Visited", "AB Visited", "Pruned Nodes", "Pruning Eff. (%)", "Speedup"]
        for c_idx, h_text in enumerate(col_headers):
            cell = res_table.rows[0].cells[c_idx]
            cell.paragraphs[0].add_run(h_text).bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            set_cell_background(cell, "0F172A")
            set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

        for r_idx, data_row in enumerate(results_rows, 1):
            row_cells = res_table.rows[r_idx].cells
            cfg_str = f"b={data_row['branching_factor']}, d={data_row['depth']}"
            vals = [
                cfg_str,
                str(data_row["total_nodes"]),
                str(data_row["root_value"]),
                str(data_row["mm_nodes_visited"]),
                str(data_row["ab_nodes_visited"]),
                str(data_row["ab_pruned_nodes"]),
                f"{float(data_row['pruning_efficiency_pct']):.2f}%",
                f"{float(data_row['speedup_factor']):.2f}x",
            ]
            for c_idx, val_text in enumerate(vals):
                cell = row_cells[c_idx]
                cell.paragraphs[0].add_run(val_text)
                cell.paragraphs[0].runs[0].font.size = Pt(8.5)
                bg_col = "FFFFFF" if r_idx % 2 == 1 else "F8FAFC"
                set_cell_background(cell, bg_col)
                set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

        add_caption("Table 2: Empirical Performance Benchmark Results (Minimax vs. Alpha-Beta Pruning)")

    doc.add_paragraph(
        "As evidenced by Table 2, Alpha-Beta Pruning demonstrates escalating node reduction as problem complexity expands. "
        "At b=3, d=4 (121 total tree nodes), Alpha-Beta pruned 68 nodes, achieving a 56.20% pruning efficiency. At b=3, d=5 "
        "(364 total tree nodes), Alpha-Beta visited only 144 nodes compared to Minimax's 364 nodes, pruning 220 nodes (60.44% efficiency). "
        "For small trees (e.g. depth 2), no cutoffs occur because root children evaluate leaves directly before bounds can constrain siblings."
    )

    # Insert Comparative Charts
    chart1_path = os.path.join(CHARTS_DIR, "tree_size_vs_nodes_visited.png")
    if os.path.exists(chart1_path):
        doc.add_paragraph()
        doc.add_picture(chart1_path, width=Inches(6.0))
        add_caption("Figure 1: Search Scalability: Minimax vs. Alpha-Beta Node Expansions")

    chart2_path = os.path.join(CHARTS_DIR, "tree_depth_vs_runtime.png")
    if os.path.exists(chart2_path):
        doc.add_paragraph()
        doc.add_picture(chart2_path, width=Inches(6.0))
        add_caption("Figure 2: Computational Latency Across Tree Depth and Branching Factor")

    chart3_path = os.path.join(CHARTS_DIR, "minimax_vs_alphabeta_evaluations.png")
    if os.path.exists(chart3_path):
        doc.add_paragraph()
        doc.add_picture(chart3_path, width=Inches(6.0))
        add_caption("Figure 3: Terminal State Evaluations: Pruning Reduction Factor")

    chart4_path = os.path.join(CHARTS_DIR, "ordering_effect_on_pruning.png")
    if os.path.exists(chart4_path):
        doc.add_paragraph()
        doc.add_picture(chart4_path, width=Inches(6.0))
        add_caption("Figure 4: Ablation Study: Move Ordering Impact on Alpha-Beta Pruning Efficiency")

    add_h2("7.1 Child Move Ordering Ablation Study")
    doc.add_paragraph(
        "Figure 4 highlights the definitive role of child move ordering on pruning efficiency. Under best-case ordering—where "
        "MAX examines highest utility options first and MIN examines lowest utility options first—pruning efficiency reaches 69.42% "
        "(at b=3, d=4, visiting only 37 of 121 nodes). Conversely, under worst-case ordering, efficiency plummets to 0.00% across "
        "most configurations, forcing Alpha-Beta to traverse the full O(b^d) tree. This experimental observation directly validates "
        "Knuth and Moore's theoretical analysis."
    )

    # -------------------------------------------------------------
    # 8. ERROR ANALYSIS & SCALABILITY BOTTLENECKS
    # -------------------------------------------------------------
    add_h1("8. Error Analysis & Scalability Bottlenecks")
    doc.add_paragraph(
        "A rigorous engineering evaluation requires identifying failure modes, scalability constraints, and edge-case behavior:"
    )
    doc.add_paragraph(
        "1. Worst-Case Move Ordering Degradation: As demonstrated in our ablation experiments, if an adversarial environment presents "
        "moves in reverse-optimal order, Alpha-Beta degenerates completely to standard Minimax, incurring additional conditional check "
        "overheads without any reduction in expanded states.\n"
        "2. Python Recursion Stack Limitations: The default recursion limit in CPython is 1000 stack frames. While sufficient for game-tree "
        "simulators of depth d <= 20, extremely deep plies require tail-recursion optimization or iterative depth-first traversal using an "
        "explicit heap-allocated stack.\n"
        "3. Canvas Layout and Visual Clutter: In a complete tree of branching factor b=4 and depth d=5, the leaf ply contains 4^5 = 1024 nodes. "
        "Rendering 1024 distinct circles on a standard 1080p display causes node overlap. The simulator addresses this by enforcing reasonable "
        "interactive configuration limits (b in {2, 3, 4}, d in {2, 3, 4, 5}) and providing horizontal scrollbars.\n"
        "4. Edge Case Robustness: Unit testing verified that the algorithm correctly processes degenerate single-child trees (b=1), "
        "purely negative utility trees, uniform leaf utility distributions, and single-node trees without raising division-by-zero or "
        "NoneType attribute exceptions."
    )

    # -------------------------------------------------------------
    # 9. INTERACTIVE SYSTEM DEMONSTRATION
    # -------------------------------------------------------------
    add_h1("9. Interactive System Demonstration")
    doc.add_paragraph(
        "The completed Tkinter application provides an intuitive graphical interface for classroom demonstrations and viva defense. "
        "Figures 5 through 8 demonstrate the simulator in various operational states."
    )

    # Insert GUI Screenshots
    gui1 = os.path.join(SCREENSHOTS_DIR, "gui_initial_state.png")
    if os.path.exists(gui1):
        doc.add_paragraph()
        doc.add_picture(gui1, width=Inches(6.0))
        add_caption("Figure 5: Simulator Initial State with Canonical Textbook Game Tree")

    gui2 = os.path.join(SCREENSHOTS_DIR, "gui_step_by_step_execution.png")
    if os.path.exists(gui2):
        doc.add_paragraph()
        doc.add_picture(gui2, width=Inches(6.0))
        add_caption("Figure 6: Step-by-Step Traversal Highlighting Active Node and Cutoff")

    gui3 = os.path.join(SCREENSHOTS_DIR, "gui_alpha_beta_pruning_complete.png")
    if os.path.exists(gui3):
        doc.add_paragraph()
        doc.add_picture(gui3, width=Inches(6.0))
        add_caption("Figure 7: Complete Alpha-Beta Execution Showing Pruned Cutoffs and Optimal Path")

    gui4 = os.path.join(SCREENSHOTS_DIR, "gui_algorithm_comparison_modal.png")
    if os.path.exists(gui4):
        doc.add_paragraph()
        doc.add_picture(gui4, width=Inches(6.0))
        add_caption("Figure 8: Side-by-Side Algorithm Comparison Dialog with Pruning Efficiency Metric")

    # Step-by-step trace log sample
    doc.add_paragraph("A representative sample from the simulator's chronological execution trace is listed below:")
    add_code_block(
        "[Step 1] VISIT: Visiting MAX node Root [α=-inf, β=+inf]. Initializing value = -inf.\n"
        "[Step 2] VISIT: Visiting MIN node A [α=-inf, β=+inf]. Initializing value = +inf.\n"
        "[Step 3] EVAL_LEAF: Leaf A1 evaluated. Utility = 3.0 [α=-inf, β=+inf].\n"
        "[Step 4] UPDATE_BOUNDS: MIN node A: child A1 returned 3.0. Value=3.0, β updated: +inf -> 3.0.\n"
        "[Step 5] EVAL_LEAF: Leaf A2 evaluated. Utility = 12.0 [α=-inf, β=3.0].\n"
        "[Step 6] EVAL_LEAF: Leaf A3 evaluated. Utility = 8.0 [α=-inf, β=3.0].\n"
        "[Step 7] FINISH_NODE: Finished MIN node A. Final value = 3.0.\n"
        "[Step 8] UPDATE_BOUNDS: MAX node Root: child A returned 3.0. Value=3.0, α updated: -inf -> 3.0.\n"
        "[Step 9] VISIT: Visiting MIN node B [α=3.0, β=+inf]. Initializing value = +inf.\n"
        "[Step 10] EVAL_LEAF: Leaf B1 evaluated. Utility = 2.0 [α=3.0, β=+inf].\n"
        "[Step 11] UPDATE_BOUNDS: MIN node B: child B1 returned 2.0. Value=2.0, β updated: +inf -> 2.0.\n"
        "[Step 12] PRUNE: ALPHA CUTOFF at MIN node B! β (2.0) <= α (3.0). Pruned 2 unvisited node(s): B2, B3.\n"
        "[Step 13] FINISH_NODE: Finished MIN node B. Final value = 2.0.\n"
        "[Step 14] ... Traversal continues for branch C ...\n"
        "[Step 22] DECISION: Optimal root utility is 3.0 via child action A. Total pruned nodes: 2."
    )

    # -------------------------------------------------------------
    # 10. CONCLUSION & FUTURE WORK
    # -------------------------------------------------------------
    add_h1("10. Conclusion & Future Work")
    doc.add_paragraph(
        "This project successfully designed, implemented, evaluated, and documented an Interactive Alpha-Beta Pruning Simulator "
        "in compliance with the Adani University Foundation of AI Project-Based Learning curriculum. By implementing both Minimax and "
        "Alpha-Beta from scratch, the project demonstrates that alpha-beta pruning significantly reduces search complexity while "
        "rigorously maintaining optimal decision quality."
    )
    doc.add_paragraph(
        "Key conclusions established by this work include:\n"
        "1. Invariance of Decision Quality: In 100% of experimental and automated test cases, Alpha-Beta produced the exact same optimal "
        "root decision and utility value as exhaustive Minimax.\n"
        "2. Empirical Scaling: As tree depth and branching factor scale, Alpha-Beta avoids over 60% of node evaluations under natural "
        "ordering, and up to 69.4% under favorable ordering.\n"
        "3. Move Ordering Sensitivity: The performance of Alpha-Beta is fundamentally governed by child exploration order, demonstrating "
        "the necessity of dynamic move ordering heuristics in real-world game AI.\n"
        "4. Pedagogical Value: The decoupled event-driven architecture enables clear visual explanations during viva voce defense."
    )
    doc.add_paragraph(
        "Future extensions could enhance the simulator by: (1) integrating transposition tables using Zobrist hashing to detect transposed "
        "game states in directed acyclic graphs; (2) implementing iterative deepening with killer and history heuristics to dynamically "
        "reorder moves; and (3) deploying a playable Connect-Four or Othello agent driven by the visual search engine."
    )

    # -------------------------------------------------------------
    # REFERENCES (APA 7th Edition)
    # -------------------------------------------------------------
    add_h1("References")
    references = [
        "Campbell, M., Hoane, A. J., & Hsu, F. H. (2002). Deep Blue. Artificial Intelligence, 134(1–2), 57–83. https://doi.org/10.1016/S0004-3702(01)00129-1",
        "Knuth, D. E., & Moore, R. W. (1975). An analysis of alpha-beta pruning. Artificial Intelligence, 6(4), 293–326. https://doi.org/10.1016/0004-3702(75)90019-3",
        "Russell, S. J., & Norvig, P. (2021). Artificial intelligence: A modern approach (4th ed.). Pearson.",
        "Shannon, C. E. (1950). Programming a computer for playing chess. Philosophical Magazine, 41(314), 256–275. https://doi.org/10.1080/14786445008521796",
        "Silver, D., Huang, A., Maddison, C. J., Guez, A., Sifre, L., van den Driessche, G., ... & Hassabis, D. (2016). Mastering the game of Go with deep neural networks and tree search. Nature, 529(7587), 484–489. https://doi.org/10.1038/nature16961",
        "von Neumann, J. (1928). Zur Theorie der Gesellschaftsspiele [On the theory of games of strategy]. Mathematische Annalen, 100(1), 295–320.",
    ]
    for ref in references:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.space_after = Pt(4)
        p.add_run(ref).font.size = Pt(9.5)

    # -------------------------------------------------------------
    # APPENDIX A: ACTUAL GIT DEVELOPMENT HISTORY
    # -------------------------------------------------------------
    add_h1("Appendix A: Actual Git Development History")
    doc.add_paragraph(
        "In strict adherence to course requirements, the repository was developed progressively through genuine, verifiable "
        "engineering milestones. Table 3 lists the complete development history retrieved directly from the repository's git log."
    )

    commits = get_git_history()
    if commits:
        git_table = doc.add_table(rows=len(commits) + 1, cols=4)
        git_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["Commit Hash", "Commit Date", "Commit Message", "Milestone Significance"]
        for c_idx, h in enumerate(headers):
            cell = git_table.rows[0].cells[c_idx]
            cell.paragraphs[0].add_run(h).bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            set_cell_background(cell, "0F172A")
            set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

        # Milestone descriptions mapping
        descriptions = {
            "first commit": "Initial project repository setup on GitHub.",
            "Initialize project": "Configured repository structure, dependencies (requirements.txt), and .gitignore.",
            "Implement game-tree data structure": "Implemented Node class with state management, cloning, and depth indexing.",
            "Implement game-tree generator": "Implemented predefined textbook trees, random generator, and 2D canvas layout calculator.",
            "Implement basic Minimax": "Implemented classical Minimax algorithm from scratch with event tracing.",
            "Add unit test suite for Minimax": "Added comprehensive Minimax unit tests covering small, negative, and edge-case trees.",
            "Implement Alpha-Beta Pruning": "Implemented Alpha-Beta bounding, cutoffs, subtree pruning, and execution tracing.",
            "Add unit test suite for Alpha-Beta": "Verified Alpha-Beta correctness, optimality equivalence, and pruning properties.",
            "Implement benchmarking framework": "Implemented multi-trial empirical benchmarks and recorded real CSV results.",
            "Add comparative benchmarking": "Generated publication-quality charts for runtime, node counts, and move ordering.",
            "Implement interactive Canvas": "Built Tkinter Canvas visualizer rendering MAX/MIN polygons, cut markers, and paths.",
            "Build Tkinter GUI controls": "Implemented control panel, speed slider, live metrics dashboard, and comparison modal.",
            "Add main application entry point": "Implemented main.py CLI/GUI launcher supporting --cli, --test, and --benchmark.",
            "Add screenshot generation": "Created screenshot utility and generated high-resolution GUI demonstration figures.",
        }

        for r_idx, c in enumerate(commits, 1):
            row_cells = git_table.rows[r_idx].cells
            msg = c["message"]
            sig = "Progressive software development milestone."
            for k, desc in descriptions.items():
                if k.lower() in msg.lower():
                    sig = desc
                    break

            for c_idx, txt in enumerate([c["hash"], c["date"], msg, sig]):
                cell = row_cells[c_idx]
                cell.paragraphs[0].add_run(txt)
                cell.paragraphs[0].runs[0].font.size = Pt(8)
                bg_col = "FFFFFF" if r_idx % 2 == 1 else "F8FAFC"
                set_cell_background(cell, bg_col)
                set_cell_margins(cell, top=50, bottom=50, left=60, right=60)

        add_caption("Table 3: Verifiable Git Commit History (Extracted Directly via git log)")

    # Save output document
    output_path = os.path.join(DOC_DIR, "project_report.docx")
    doc.save(output_path)
    print(f"Project report successfully generated at: {output_path}")


if __name__ == "__main__":
    create_document()
