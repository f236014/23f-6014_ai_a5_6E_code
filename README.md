#  Sudoku Solver using CSP (AC-3 + Backtracking)

##  Overview
This project is a **Sudoku Solver** implemented using **Constraint Satisfaction Problem (CSP)** techniques.  
It combines:

- **AC-3 Algorithm (Arc Consistency)** for constraint propagation
- **Backtracking Search** for solving remaining variables
- **MRV Heuristic (Minimum Remaining Values)** for efficient variable selection

The solver reads Sudoku puzzles from text files and outputs the solved board along with performance statistics.

---

##  Features

- Solves Easy, Medium, Hard, and Very Hard Sudoku puzzles
- Uses **forward checking + AC-3 propagation**
- Implements **backtracking search with MRV heuristic**
- Tracks:
  - Number of recursive calls
  - Number of failures (backtracks)
- Clean formatted board output

---

##  Algorithms Used

### 1. AC-3 (Arc Consistency)
Ensures that every value in a cell has a valid support in its connected cells (row, column, or 3×3 box).  
It reduces the search space before backtracking starts.

### 2. Backtracking Search
Tries possible values for unassigned cells and recursively searches for a valid solution.

### 3. MRV Heuristic
Selects the variable (cell) with the **fewest possible values** to reduce branching.

---

##  Project Structure
.
├── sudoku_solver.py # Main solver code
├── easy.txt
├── medium.txt
├── hard.txt
├── veryhard.txt
└── README.md

---

##  Input Format

Each Sudoku puzzle is stored in a `.txt` file:

- 9 lines per file
- Each line has 9 digits (0–9)
- `0` represents an empty cell

Example:
530070000
600195000
098000060
800060003
400803001
700020006
060000280
000419005
000080079

---

##  How to Run

### 1. Install Python
Make sure Python 3 is installed.

### 2. Place files
Keep all `.txt` puzzle files in the same folder as the script.

### 3. Run the solver
bash
python sudoku_solver.py

##Example Output
=======================================================
  Solving: Easy board
=======================================================

Initial board:
5 3 . | . 7 . | . . .
6 . . | 1 9 5 | . . .
...

Solution:
5 3 4 | 6 7 8 | 9 1 2
...

BACKTRACK calls: 12
Failures: 3
Comment: Very few backtracks — AC-3 solved most cells directly.
