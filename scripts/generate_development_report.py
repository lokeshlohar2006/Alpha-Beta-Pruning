"""
Comprehensive Project Development Report Generator
Builds a detailed, publication-grade academic Word document (Project_Development_Report.docx)
chronicling the entire engineering lifecycle, milestone-by-milestone Git commits,
system architecture, empirical benchmarks, and student viva defense guide.
"""

import os
import sys
import csv
import subprocess
from datetime import datetime
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

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


def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    """Sets internal cell margins in twips (20 twips = 1 pt)."""
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


def get_git_commit_details():
    """Extracts detailed Git commit logs including hash, author, date, message, and stats."""
    try:
        cmd = ["git", "log", "--pretty=format:%h|%an|%ad|%s", "--date=iso"]
        out = subprocess.check_output(cmd, encoding="utf-8").strip()
        lines = out.split("\n")
        commits = []
        for line in lines:
            if "|" in line:
                parts = line.split("|", 3)
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2][:10],
                    "message": parts[3],
                })
        return commits
    except Exception as e:
        print(f"Error reading git commits: {e}")
        return []


def create_development_report():
    doc = docx.Document()

    # Page Margins (1.0 inch all around)
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
    COLOR_BODY = RGBColor(51, 65, 85)        # Body Text #334155

    # Base Normal Style
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_BODY
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Helper functions
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
    # TITLE PAGE
    # -------------------------------------------------------------
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_before = Pt(30)
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
    p_dept.paragraph_format.space_after = Pt(16)
    run_dept = p_dept.add_run("Department of Computer Science and Engineering (AI-ML)")
    run_dept.font.size = Pt(12)
    run_dept.font.color.rgb = COLOR_MUTED

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(20)
    run_div = p_div.add_run("—" * 36)
    run_div.font.color.rgb = COLOR_TEAL

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_after = Pt(6)
    run_course = p_course.add_run("PROJECT-BASED LEARNING (PBL) TECHNICAL REPORT\nCourse: ECSCT24301 – Foundation of AI")
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
    p_title.paragraph_format.space_after = Pt(32)
    run_title = p_title.add_run("Software Development Report & Technical Documentation:\nInteractive Alpha-Beta Pruning Simulator")
    run_title.font.size = Pt(19)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    # Academic & Student Metadata Table
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

    # -------------------------------------------------------------
    # EXECUTIVE SUMMARY / ABSTRACT
    # -------------------------------------------------------------
    add_h1("Executive Summary")
    doc.add_paragraph(
        "This technical development report documents the design, progressive implementation, empirical evaluation, and software "
        "architecture of the Interactive Alpha-Beta Pruning Simulator, developed for Course ECSCT24301 (Foundation of AI) at Adani University. "
        "Adversarial game-tree search constitutes a foundational pillar of artificial intelligence, enabling rational decision-making in "
        "zero-sum, turn-based competitive environments. While the exhaustive Minimax algorithm guarantees optimal decision equilibrium, "
        "its brute-force exploration incurs an exponential time complexity of O(b^d). Alpha-Beta Pruning optimizes this search by dynamically "
        "maintaining guaranteed utility bounds (alpha and beta) along the search path, pruning subtrees that cannot alter the final choice."
    )
    doc.add_paragraph(
        "Rather than treating algorithms as theoretical abstractions, this project implements both Minimax and Alpha-Beta Pruning from "
        "scratch in pure Python, coupled with a responsive Tkinter graphical interface. To ensure maximum code readability and viva "
        "defensibility for second-year undergraduate students, the system avoids complex dependencies and implements an event-driven "
        "trace architecture that completely decouples search execution from GUI canvas rendering. The simulator allows users to generate "
        "canonical textbook trees or parameterized random trees, step through search events manually, play continuous animations, and "
        "inspect live metrics alongside a side-by-side comparison modal. Furthermore, rigorous multi-trial benchmarking across 12 tree "
        "configurations and a move-ordering ablation study confirm that Alpha-Beta achieves up to 69.42% pruning efficiency under favorable "
        "move ordering while maintaining 100% mathematical decision optimality. The entire software engineering lifecycle is recorded "
        "through 17 verifiable, progressive Git commits, documented comprehensively herein."
    )

    # -------------------------------------------------------------
    # SECTION 1: INTRODUCTION & DEVELOPMENT OBJECTIVES
    # -------------------------------------------------------------
    add_h1("1. Introduction & Development Objectives")
    doc.add_paragraph(
        "The primary objective of Project-Based Learning (PBL) in Foundation of AI is to cultivate end-to-end engineering competence: "
        "transitioning from formal problem formulation and state-space modeling to algorithmic implementation, empirical benchmarking, and "
        "interactive demonstration. Adversarial search was selected as the core domain because it models multi-agent conflict where an "
        "agent must anticipate deliberate opposing actions."
    )
    doc.add_paragraph(
        "Key Engineering Goals of this Development Project:\n"
        "1. Beginner-Friendly, Zero-Overengineering Architecture: Avoid enterprise bloat, external GUI wrappers, or opaque frameworks. "
        "Ensure every single class, method, and helper can be clearly articulated and defended by a second-year student during viva voce.\n"
        "2. Scratch Algorithmic Implementations: Implement recursive Minimax and Alpha-Beta Pruning without external search libraries, "
        "adhering strictly to the alpha >= beta cutoff criterion.\n"
        "3. Decoupled Event-Driven Visualization: Isolate search traversal from Tkinter GUI rendering through an explicit chronological "
        "trace of SearchEvent objects, allowing smooth pause, rewind, and stepping.\n"
        "4. Quantitative Empirical Rigor: Benchmark real execution timings and expanded node counts across varying branching factors (b in {2, 3, 4}) "
        "and depths (d in {2, 3, 4, 5, 6}), evaluating move-ordering sensitivity.\n"
        "5. Genuine Progressive Version Control: Develop the repository iteratively through verifiable Git commits representing genuine "
        "functional milestones rather than artificial monolithic code dumps."
    )

    # -------------------------------------------------------------
    # SECTION 2: END-TO-END DEVELOPMENT LIFECYCLE & GIT MILESTONES
    # -------------------------------------------------------------
    add_h1("2. End-to-End Development Lifecycle & Progressive Git Milestones")
    doc.add_paragraph(
        "In strict compliance with the university's engineering guidelines, the project was executed sequentially across 17 distinct, "
        "verifiable development milestones. Each commit was created only after the respective component was implemented, executed, and "
        "empirically verified. Table 1 chronicles the progressive development journey retrieved directly from the repository's git log."
    )

    commits = get_git_commit_details()
    if commits:
        git_table = doc.add_table(rows=len(commits) + 1, cols=4)
        git_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["Commit Hash", "Date", "Commit Message", "Engineering Significance"]
        for c_idx, h in enumerate(headers):
            cell = git_table.rows[0].cells[c_idx]
            cell.paragraphs[0].add_run(h).bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            set_cell_background(cell, "0F172A")
            set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

        milestone_explanations = {
            "first commit": "Initial root commit setting up the project repository on GitHub.",
            "Initialize project structure": "Established base directory layout, dependencies (requirements.txt), and version control exclusions (.gitignore).",
            "Implement game-tree data structure": "Authored core/game_tree.py introducing the Node class with dynamic bounds, status flags, and deep cloning.",
            "Implement game-tree generator": "Authored core/tree_generator.py with canonical Russell & Norvig textbook trees, random generators, and 2D layout engine.",
            "Implement basic Minimax": "Authored algorithms/minimax.py and trace.py implementing recursive depth-first Minimax with event logging.",
            "Add unit test suite for Minimax": "Authored tests/test_minimax.py validating Minimax on small, negative, uniform, and degenerate single-child trees.",
            "Implement Alpha-Beta Pruning": "Authored algorithms/alpha_beta.py implementing bounding, alpha >= beta cutoffs, subtree pruning, and trace logging.",
            "Add unit test suite for Alpha-Beta": "Authored tests/test_alpha_beta.py proving 100% root value equivalence between Minimax and Alpha-Beta across 15 seeds.",
            "Implement benchmarking framework": "Authored benchmarks/benchmark.py executing multi-trial latency and move-ordering ablation experiments to CSV.",
            "Add comparative benchmarking": "Authored benchmarks/generate_charts.py generating four 300 DPI publication-grade Matplotlib comparison charts.",
            "Implement interactive Canvas": "Authored gui/tree_visualizer.py rendering polygonal nodes (▲ MAX, ▼ MIN, ● Leaf), cut markers, and optimal paths.",
            "Build Tkinter GUI controls": "Authored gui/controls.py and main_window.py introducing the control panel, speed slider, metrics, and comparison modal.",
            "Add main application entry point": "Authored main.py implementing unified CLI/GUI routing (--cli, --test, --benchmark, --charts).",
            "Add screenshot generation": "Authored scripts/capture_screenshots.py producing high-resolution UI demonstration captures for documentation.",
            "Generate comprehensive academic Word project report": "Authored scripts/generate_report.py automating python-docx report generation conforming to PBL guidelines.",
            "Complete comprehensive README.md": "Authored production-ready README.md containing complete usage instructions, math formulation, and sample outputs.",
            "Finalize project documentation report": "Recompiled final Word report synchronized with complete Git audit logs and verification metrics.",
        }

        for r_idx, c in enumerate(commits, 1):
            row_cells = git_table.rows[r_idx].cells
            msg = c["message"]
            sig = "Progressive software engineering milestone."
            for k, desc in milestone_explanations.items():
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

        add_caption("Table 1: Progressive Git Commit Milestones and Engineering Significance")

    add_h2("2.1 Detailed Milestone Breakdown")

    milestone_details = [
        ("Milestone 1 to 3: Core Foundation & Tree Topology",
         "The initial development phase established repository standards (.gitignore, requirements.txt) and constructed the fundamental "
         "state-space abstractions. The Node class in core/game_tree.py models individual game states, encapsulating depth, active player "
         "(MAX vs. MIN), tentative utility, dynamic alpha/beta bounds, and tree topology. To support fair algorithmic comparison, the clone() "
         "method creates independent deep copies of tree topologies so Minimax and Alpha-Beta can evaluate identical instances without cross-contamination. "
         "The tree generator in core/tree_generator.py provides the canonical Russell & Norvig textbook tree alongside parameterized random generators, "
         "incorporating a balanced post-order 2D canvas layout algorithm that automatically computes spatial coordinates (x, y) preventing visual overlap."),

        ("Milestone 4 to 7: Algorithmic Implementations & Verification Suites",
         "The algorithmic core was implemented strictly from scratch without external libraries. algorithms/minimax.py implements pure recursive "
         "depth-first exploration, maximizing at depth % 2 == 0 and minimizing at depth % 2 == 1. algorithms/alpha_beta.py enhances this with dynamic "
         "alpha and beta tracking. When alpha >= beta occurs at any node, the algorithm prunes all remaining sibling branches using _mark_subtree_pruned(), "
         "flagging nodes as 'pruned' and counting bypassed computations. Both algorithms log discrete SearchEvent objects. Rigorous unit test suites "
         "(tests/test_minimax.py and tests/test_alpha_beta.py) verify correctness across edge cases, negative utilities, identical leaves, and single-child "
         "chains, explicitly asserting that Alpha-Beta produces the mathematically identical root value as Minimax across 15 randomized tree seeds."),

        ("Milestone 8 to 10: Empirical Benchmarking & Visualization Assets",
         "To establish quantitative performance data, benchmarks/benchmark.py was developed. It conducts automated evaluations over 12 tree configurations "
         "(b in {2, 3, 4}, d in {2, 3, 4, 5, 6}) across 5 repetitions, recording median execution times, node expansions, and leaf evaluations into CSV. "
         "An ablation study evaluates child move ordering (best-case, random, worst-case). benchmarks/generate_charts.py reads this real data and generates "
         "four publication-grade Matplotlib figures at 300 DPI. scripts/capture_screenshots.py generates high-resolution UI captures of the system in action."),

        ("Milestone 11 to 17: Interactive GUI, CLI Integration & Final Report",
         "The user experience was constructed in Tkinter. gui/tree_visualizer.py draws polygonal nodes (▲ Blue for MAX, ▼ Pink for MIN, ● Circles for Leaves), "
         "dashed red lines with scissor cuts (✕) for pruned branches, and bold emerald paths for optimal decisions. gui/controls.py provides single-step "
         "stepping, autoplay, a speed slider, live metrics, and an educational narration log. gui/main_window.py binds components together and hosts a "
         "side-by-side comparison modal with the explicit pruning efficiency formula. main.py unifies execution routing (--cli, --test, --benchmark, --charts), "
         "and scripts/generate_report.py automates the production of this comprehensive Word report."),
    ]

    for phase_title, phase_desc in milestone_details:
        add_h3(phase_title)
        doc.add_paragraph(phase_desc)

    # -------------------------------------------------------------
    # SECTION 3: PROBLEM FORMULATION & ENVIRONMENT SPECIFICATION
    # -------------------------------------------------------------
    add_h1("3. Problem Formulation & PEAS Specification")
    doc.add_paragraph(
        "Adversarial search problems are formally modeled following the intelligent agent framework (Russell & Norvig, 2021). "
        "The environment represents a two-player, zero-sum, turn-based game tree with perfect information. Table 2 details the PEAS elements."
    )

    # PEAS Table
    peas_table = doc.add_table(rows=5, cols=2)
    peas_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    peas_data = [
        ("Performance Measure", "• Correctness: 100% preservation of optimal minimax root decision.\n"
                                "• Search Efficiency: Reduction in total visited states and terminal leaf evaluations.\n"
                                "• Pruning Efficiency (%): ((Minimax_Visited - AlphaBeta_Visited) / Minimax_Visited) * 100.\n"
                                "• Wall-clock latency (milliseconds) measured via Python time.perf_counter.\n"
                                "• Linear memory footprint bounded by recursion stack depth O(b*d)."),
        ("Environment", "Deterministic, fully observable, turn-based, discrete zero-sum game tree. State transitions are non-stochastic, "
                        "and legal actions correspond to directed tree edges branching down to depth d."),
        ("Actuators", "• Traverse to successor child node (depth-first expansion).\n"
                      "• Backtrack to parent node with computed minimax value.\n"
                      "• Update alpha bound (at MAX) or beta bound (at MIN).\n"
                      "• Prune sibling subtrees upon alpha >= beta cutoff.\n"
                      "• Transmit event signals to GUI visualizer."),
        ("Sensors", "• Active node identifier, tree depth, and player turn (MAX vs. MIN).\n"
                    "• Node classification sensor (terminal leaf vs. non-terminal internal node).\n"
                    "• Static leaf utility score reader.\n"
                    "• Active path bound inspector (inherited alpha and beta values)."),
    ]
    for r_idx, (elem, desc) in enumerate(peas_data):
        row = peas_table.rows[r_idx]
        row.cells[0].paragraphs[0].add_run(elem).bold = True
        row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
        row.cells[1].paragraphs[0].add_run(desc)
        row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_margins(row.cells[0], top=80, bottom=80, left=100, right=100)
        set_cell_margins(row.cells[1], top=80, bottom=80, left=100, right=100)
        set_cell_background(row.cells[0], "F1F5F9")
        set_cell_background(row.cells[1], "FFFFFF")

    add_caption("Table 2: PEAS Specification for Adversarial Search Agent")

    add_h2("3.1 Mathematical State-Space Formulation")
    doc.add_paragraph(
        "The adversarial search problem is modeled as a formal 6-tuple (S, A, T, s0, Terminal, Utility):\n"
        "1. State Space (S): Finite directed tree of game configurations. Each state s in S defines depth(s), Player(s) in {MAX, MIN}, "
        "and successor children Children(s).\n"
        "2. Initial State (s0): Tree root node at depth 0, where Player(s0) = MAX.\n"
        "3. Actions (A(s)): Directed edges from node s to each successor child c in Children(s).\n"
        "4. Transition Model (T(s, a)): Deterministic transition yielding the chosen child state s'.\n"
        "5. Terminal Test (Terminal(s)): Predicate returning True if Children(s) is empty or depth(s) == d.\n"
        "6. Utility Function (Utility(s)): Real-valued evaluation defined on terminal leaf states. In zero-sum games, Utility(s) represents "
        "the payoff to MAX, with MIN receiving the exact negative payoff -Utility(s). Path costs are zero because decision quality depends "
        "solely on terminal leaf payoffs under optimal adversarial counterplay."
    )

    # -------------------------------------------------------------
    # SECTION 4: ARCHITECTURE & ALGORITHMIC SPECIFICATION
    # -------------------------------------------------------------
    add_h1("4. Software Architecture & Algorithmic Mechanics")
    doc.add_paragraph(
        "The software architecture enforces strict modular separation. Algorithms operate as pure mathematical functions on tree data "
        "structures, emitting discrete SearchEvent records that the GUI visualizer replays."
    )

    add_h2("4.1 Algorithmic Pseudocode and Mathematical Formulations")
    doc.add_paragraph(
        "Minimax recursively calculates equilibrium payoffs according to:\n"
        "V(s) = Utility(s)                                   if Terminal(s)\n"
        "V(s) = max_{a in Actions(s)} V(Result(s, a))         if Player(s) = MAX\n"
        "V(s) = min_{a in Actions(s)} V(Result(s, a))         if Player(s) = MIN\n\n"
        "Alpha-Beta Pruning enhances this formulation by maintaining active path bounds alpha in [-inf, +inf] and beta in [-inf, +inf]. "
        "The complete recursive implementation is shown below:"
    )

    add_code_block(
        "def alpha_beta(node: Node, alpha: float, beta: float) -> float:\n"
        "    if node.is_leaf:\n"
        "        return node.value\n\n"
        "    if node.is_max:\n"
        "        max_eval = -math.inf\n"
        "        for child in node.children:\n"
        "            eval_val = alpha_beta(child, alpha, beta)\n"
        "            max_eval = max(max_eval, eval_val)\n"
        "            alpha = max(alpha, max_eval)          # Alpha update at MAX\n"
        "            if alpha >= beta:                    # Beta Cutoff\n"
        "                mark_subtree_pruned(remaining_children)\n"
        "                break\n"
        "        return max_eval\n"
        "    else:\n"
        "        min_eval = math.inf\n"
        "        for child in node.children:\n"
        "            eval_val = alpha_beta(child, alpha, beta)\n"
        "            min_eval = min(min_eval, eval_val)\n"
        "            beta = min(beta, min_eval)           # Beta update at MIN\n"
        "            if alpha >= beta:                    # Alpha Cutoff\n"
        "                mark_subtree_pruned(remaining_children)\n"
        "                break\n"
        "        return min_eval"
    )

    add_h2("4.2 Theoretical Complexity Analysis")
    doc.add_paragraph(
        "• Time Complexity of Minimax: O(b^d). Minimax must visit every one of the b^d terminal leaves and (b^(d+1)-1)/(b-1) tree nodes.\n"
        "• Best-Case Time Complexity of Alpha-Beta: O(b^(d/2)). When the best child move is evaluated first at every node, Alpha-Beta evaluates "
        "approximately 2 * b^(d/2) - 1 terminal states, effectively halving the search exponent.\n"
        "• Worst-Case Time Complexity of Alpha-Beta: O(b^d). If moves are evaluated in reverse-optimal order (worst moves first), no cutoffs "
        "occur, degenerating to complete Minimax traversal.\n"
        "• Space Complexity: O(b * d) for both algorithms. Because search is executed via recursive depth-first backtracking, memory requirements "
        "scale linearly with search depth, storing only the active path and sibling alternatives on the call stack."
    )

    # -------------------------------------------------------------
    # SECTION 5: EMPIRICAL BENCHMARKS & EXPERIMENTAL RESULTS
    # -------------------------------------------------------------
    add_h1("5. Empirical Benchmarks & Experimental Results")
    doc.add_paragraph(
        "Benchmark experiments were executed on Windows 11 with Python 3.14.3. Each problem instance was evaluated over five independent "
        "runs using time.perf_counter, reporting median execution times to eliminate OS scheduling noise. Table 3 presents the measured data."
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

        add_caption("Table 3: Measured Empirical Benchmark Data Across 12 Game-Tree Configurations")

    doc.add_paragraph(
        "Critical Findings from Table 3:\n"
        "1. Absolute Root Optimality: In 100% of the 12 configurations, Minimax and Alpha-Beta returned the exact same optimal root utility value.\n"
        "2. Escalating Efficiency: As tree depth expands, pruning efficiency increases substantially. At b=3, d=4, Alpha-Beta pruned 68 nodes "
        "(56.20% efficiency); at b=3, d=5, it pruned 220 out of 364 total nodes (60.44% efficiency), visiting only 144 nodes.\n"
        "3. Shallow Tree Behavior: For depth 2 trees, no cutoffs occur because root children evaluate leaves directly before bounds can constrain siblings."
    )

    # Insert Comparative Benchmark Charts
    chart1_path = os.path.join(CHARTS_DIR, "tree_size_vs_nodes_visited.png")
    if os.path.exists(chart1_path):
        doc.add_paragraph()
        doc.add_picture(chart1_path, width=Inches(5.8))
        add_caption("Figure 1: Total Game-Tree Size vs. Visited Nodes (Minimax vs. Alpha-Beta)")

    chart2_path = os.path.join(CHARTS_DIR, "tree_depth_vs_runtime.png")
    if os.path.exists(chart2_path):
        doc.add_paragraph()
        doc.add_picture(chart2_path, width=Inches(5.8))
        add_caption("Figure 2: Computational Latency Across Search Depth and Branching Factor")

    chart3_path = os.path.join(CHARTS_DIR, "minimax_vs_alphabeta_evaluations.png")
    if os.path.exists(chart3_path):
        doc.add_paragraph()
        doc.add_picture(chart3_path, width=Inches(5.8))
        add_caption("Figure 3: Terminal Leaf Evaluations: Full Minimax vs. Alpha-Beta Pruning")

    chart4_path = os.path.join(CHARTS_DIR, "ordering_effect_on_pruning.png")
    if os.path.exists(chart4_path):
        doc.add_paragraph()
        doc.add_picture(chart4_path, width=Inches(5.8))
        add_caption("Figure 4: Ablation Study: Impact of Move Ordering on Pruning Efficiency (%)")

    add_h2("5.1 Move-Ordering Ablation Study")
    doc.add_paragraph(
        "Figure 4 illustrates the decisive impact of child exploration order. In our ablation experiments, sorting children favorably "
        "(best move evaluated first) propelled pruning efficiency to 69.42% (at b=3, d=4, visiting only 37 out of 121 nodes). "
        "In contrast, reverse-optimal ordering (worst move evaluated first) caused pruning efficiency to collapse to 0.00% across most "
        "configurations, forcing the algorithm to explore the entire O(b^d) state space. This empirically validates Knuth & Moore's theorem."
    )

    # -------------------------------------------------------------
    # SECTION 6: GRAPHICAL USER INTERFACE DEMONSTRATION
    # -------------------------------------------------------------
    add_h1("6. Graphical User Interface Demonstration")
    doc.add_paragraph(
        "The Tkinter GUI offers a clean visual presentation designed for classroom lectures and viva voce defense. "
        "Figures 5 through 8 demonstrate the system across its primary operational phases."
    )

    gui1 = os.path.join(SCREENSHOTS_DIR, "gui_initial_state.png")
    if os.path.exists(gui1):
        doc.add_paragraph()
        doc.add_picture(gui1, width=Inches(5.8))
        add_caption("Figure 5: Simulator Initial State: Canonical Textbook Game Tree (b=3, d=3)")

    gui2 = os.path.join(SCREENSHOTS_DIR, "gui_step_by_step_execution.png")
    if os.path.exists(gui2):
        doc.add_paragraph()
        doc.add_picture(gui2, width=Inches(5.8))
        add_caption("Figure 6: Step-by-Step Traversal: Active Node Highlight and Pruned Cutoff Trigger")

    gui3 = os.path.join(SCREENSHOTS_DIR, "gui_alpha_beta_pruning_complete.png")
    if os.path.exists(gui3):
        doc.add_paragraph()
        doc.add_picture(gui3, width=Inches(5.8))
        add_caption("Figure 7: Search Complete: Pruned Branches Marked with Scissor Cuts (✕) and Optimal Path Highlighted")

    gui4 = os.path.join(SCREENSHOTS_DIR, "gui_algorithm_comparison_modal.png")
    if os.path.exists(gui4):
        doc.add_paragraph()
        doc.add_picture(gui4, width=Inches(5.8))
        add_caption("Figure 8: Side-by-Side Algorithm Comparison Dialog with Calculated Pruning Efficiency Metric")

    # -------------------------------------------------------------
    # SECTION 7: VIVA VOCE & CODE DEFENSE GUIDE
    # -------------------------------------------------------------
    add_h1("7. Viva Voce & Code Defense Guide")
    doc.add_paragraph(
        "To ensure team members are thoroughly prepared for individual oral examinations, this section summarizes the key theoretical "
        "concepts, code walkthroughs, and expected viva defense questions."
    )

    viva_qa = [
        ("Q1: What does alpha and beta represent in the recursive call?",
         "Alpha (α) represents the highest utility value that the MAX player is guaranteed along the current search path to the root. "
         "Beta (β) represents the lowest utility value that the MIN player is guaranteed along the current search path. "
         "Alpha is initialized to -infinity, and beta is initialized to +infinity."),

        ("Q2: Why is the cutoff condition alpha >= beta rather than alpha > beta?",
         "Alpha-Beta pruning assumes rational play. If alpha == beta, the MAX player already has an alternative guaranteeing alpha, "
         "while the MIN player has an alternative holding the score down to beta (which equals alpha). Neither player has an incentive "
         "to explore further branches because rational play will never result in a better outcome for either party. Pruning at alpha >= beta "
         "saves unnecessary branch evaluations without compromising the minimax decision."),

        ("Q3: Does Alpha-Beta Pruning ever return a different root decision or value than Minimax?",
         "No. Alpha-Beta Pruning is mathematically guaranteed to return the exact same optimal root utility value and the same optimal action "
         "as exhaustive Minimax. It only prunes branches that are provably irrelevant to rational decision-makers."),

        ("Q4: How does your code decouple algorithm execution from the GUI?",
         "In algorithms/minimax.py and algorithms/alpha_beta.py, the search operates purely in memory, generating a chronological list of "
         "SearchEvent objects (recording event_type, node_id, depth, alpha, beta, and narration). The Tkinter GUI in gui/main_window.py "
         "simply steps through this recorded list at the user's chosen playback speed, completely isolating search logic from visual rendering."),

        ("Q5: What is the significance of move ordering, and what did your ablation study show?",
         "Under best-case move ordering (evaluating optimal moves first), Alpha-Beta visits only O(b^(d/2)) leaves, effectively doubling the "
         "search horizon. Under worst-case move ordering (evaluating worst moves first), cutoffs never trigger, and complexity degenerates "
         "to O(b^d). Our ablation study proved this empirically: pruning efficiency dropped from 69.42% in the best case to 0.00% in the worst case."),
    ]

    for q, a in viva_qa:
        add_h3(q)
        doc.add_paragraph(a)

    # -------------------------------------------------------------
    # SECTION 8: CONCLUSION & REFERENCES
    # -------------------------------------------------------------
    add_h1("8. Conclusion & References")
    doc.add_paragraph(
        "The Interactive Alpha-Beta Pruning Simulator successfully fulfills all Applied AI Project Track requirements for Course ECSCT24301. "
        "Through scratch Python implementations, decoupled event tracing, interactive visual rendering, and empirical benchmarking, the "
        "project provides a comprehensive, academically defensible educational tool."
    )

    add_h2("References (APA 7th Edition)")
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

    # Save to both Project_Development_Report.docx and project_report.docx
    dev_report_path = os.path.join(DOC_DIR, "Project_Development_Report.docx")
    project_report_path = os.path.join(DOC_DIR, "project_report.docx")

    doc.save(dev_report_path)
    doc.save(project_report_path)
    print(f"Project Development Report successfully saved to:\n  - {dev_report_path}\n  - {project_report_path}")


if __name__ == "__main__":
    create_development_report()
