Python Version: Python 3.7.5

Files: CSP.py, dfsb.py, minconflicts.py

Run in the command line: 

`python dfsb.py <INPUT FILE PATH> <OUTPUT FILE PATH> <MODE FLAG>`

<MODE FLAG> can be either 0 (plain DFS-B) or 1 (improved DFS-B)

`python minconflicts.py <INPUT FILE PATH> <OUTPUT FILE PATH>`

1. dfsb.py - runs in two modes. mode 0) plain DFS-B or mode 1) DFS-B with variable, value ordering + AC3 for constraint propagation.

2. minconflicts.py - runs the MinConflicts local search algorithm.

Input File Content:
N M K
v<sup>0</sup> u<sup>0</sup> (variables vo and uo should not have the same color)
v<sup>1</sup> u<sup>1</sup>
...
v<sup>m-1</sup> u<sup>m-1</sup>

Output File Content:
c<sup>0</sup>
c<sup>1</sup>
...
c<sup>n-1</sup>

After running either command, the solution will be written to the output file path.