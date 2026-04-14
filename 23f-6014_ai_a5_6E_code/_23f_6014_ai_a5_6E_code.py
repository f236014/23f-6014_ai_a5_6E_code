
import copy
import sys
from collections import deque

# Helpers to compute Sudoku constraints

def get_peers(cell):
    """Return all cells that share a row, column, or 3x3 box with `cell`."""
    row, col = divmod(cell, 9)
    peers = set()
    # Same row
    for c in range(9):
        peers.add(row * 9 + c)
    # Same column
    for r in range(9):
        peers.add(r * 9 + col)
    # Same 3x3 box
    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            peers.add(r * 9 + c)
    peers.discard(cell)
    return peers


# Pre-compute peers for every cell 
PEERS = {cell: get_peers(cell) for cell in range(81)}

# All arcs (xi, xj) where xi and xj are peers
ALL_ARCS = [(xi, xj) for xi in range(81) for xj in PEERS[xi]]

# CSP representation


def parse_board(filename):
    """Read a 9×9 board file; return domains dict {cell: set of int}."""
    with open(filename) as f:
        lines = f.read().strip().split()
    domains = {}
    for i, line in enumerate(lines):
        for j, ch in enumerate(line):
            cell = i * 9 + j
            digit = int(ch)
            if digit == 0:
                domains[cell] = set(range(1, 10))
            else:
                domains[cell] = {digit}
    return domains


# AC-3


def revise(domains, xi, xj):
    """
    Remove values from domains[xi] that have no support in domains[xj].
    Returns True if domains[xi] was reduced.
    """
    revised = False
    # A value v in xi has support iff xj has at least one value != v
    to_remove = set()
    for v in domains[xi]:
        # No support if xj's domain is exactly {v} (only that value, equals v)
        if domains[xj] == {v}:
            to_remove.add(v)
    if to_remove:
        domains[xi] -= to_remove
        revised = True
    return revised


def ac3(domains, arcs=None):
    
    queue = deque(arcs if arcs is not None else ALL_ARCS)
    while queue:
        xi, xj = queue.popleft()
        if xi not in domains or xj not in domains:
            continue
        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False   # Domain wiped out → inconsistency
            # Re-add all arcs (xk, xi) for neighbours xk of xi (except xj)
            for xk in PEERS[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True


# Backtracking search

stats = {"calls": 0, "failures": 0}


def select_unassigned(domains):
    """
    MRV heuristic: pick the unassigned cell with the smallest domain (> 1 value).
    Returns None if all cells are assigned (domain size == 1).
    """
    unassigned = [(len(domains[c]), c) for c in range(81) if len(domains[c]) > 1]
    if not unassigned:
        return None
    return min(unassigned)[1]   # cell with fewest remaining values


def is_solution(domains):
    """Return True if every cell has exactly one value assigned."""
    return all(len(domains[c]) == 1 for c in range(81))


def backtrack(domains):
    """
    Recursive backtracking with forward checking via AC-3.
    Returns solved domains dict or None on failure.
    """
    stats["calls"] += 1

    if is_solution(domains):
        return domains

    cell = select_unassigned(domains)
    if cell is None:
        return domains   # All assigned (shouldn't reach here normally)

    for value in sorted(domains[cell]):   # Try values in order
        # Deep copy domains so we can restore on backtrack
        new_domains = copy.deepcopy(domains)
        new_domains[cell] = {value}

        # Forward checking: run AC-3 restricted to arcs involving `cell`
        # We only need to propagate from the newly assigned cell
        arcs = [(peer, cell) for peer in PEERS[cell]]
        consistent = ac3(new_domains, arcs)

        if consistent:
            result = backtrack(new_domains)
            if result is not None:
                return result

    # All values for this cell failed
    stats["failures"] += 1
    return None


# Formatting helpers


def domains_to_grid(domains):
    """Convert solved domains to a 9×9 list of ints."""
    grid = []
    for i in range(9):
        row = []
        for j in range(9):
            cell = i * 9 + j
            vals = domains[cell]
            row.append(next(iter(vals)) if len(vals) == 1 else 0)
        grid.append(row)
    return grid


def print_board(grid, title=""):
    """Pretty-print a 9×9 board."""
    if title:
        print(f"\n{'─'*25} {title} {'─'*25}")
    for i, row in enumerate(grid):
        if i % 3 == 0 and i > 0:
            print("------+-------+------")
        line = ""
        for j, val in enumerate(row):
            if j % 3 == 0 and j > 0:
                line += " | "
            line += str(val) if val != 0 else "."
            if j % 3 != 2:
                line += " "
        print(line)
    print()



# Solve one board


def solve(filename, label):
    global stats
    stats = {"calls": 0, "failures": 0}

    print(f"\n{' '*55}")
    print(f"  Solving: {label}  ({filename})")
    print(f"{' '*55}")

    domains = parse_board(filename)

    # Print initial board
    print_board(domains_to_grid(domains), "Initial board")

    # Step 1: Apply AC-3 to the full board (initial propagation)
    ok = ac3(domains)
    if not ok:
        print("  AC-3 found contradiction in initial board!")
        return

    # Step 2: If AC-3 solved it completely, no backtracking needed
    if is_solution(domains):
        print("  Solved by AC-3 alone (no backtracking needed)")
        print_board(domains_to_grid(domains), "Solution")
        print(f"  BACKTRACK calls: {stats['calls']}   Failures: {stats['failures']}")
        return

    # Step 3: Run backtracking search
    result = backtrack(domains)

    if result is None:
        print("  No solution found!")
    else:
        print_board(domains_to_grid(result), "Solution")

    print(f"  BACKTRACK calls  : {stats['calls']}")
    print(f"  BACKTRACK failures: {stats['failures']}")

    # Brief commentary
    if stats["calls"] <= 10:
        print("  Comment: Very few backtracks — AC-3 + MRV solved most cells directly.")
    elif stats["calls"] <= 100:
        print("  Comment: Moderate search — forward checking kept the space small.")
    else:
        print("  Comment: Hard puzzle — significant backtracking required despite propagation.")



# Main

if __name__ == "__main__":
    import os

    base = "."   # simplest fix

    boards = [
        ("easy.txt",     "Easy board"),
        ("medium.txt",   "Medium board"),
        ("hard.txt",     "Hard board"),
        ("veryhard.txt", "Very Hard board"),
    ]

    for fname, label in boards:
        path = os.path.join(base, fname)
        solve(path, label)

