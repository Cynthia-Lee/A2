import sys

# -------------------------------------------------------
# Sources used:
# Lecture slides
# http://pages.cs.wisc.edu/~bgibson/cs540/handouts/csp.pdf
# https://en.wikipedia.org/wiki/Min-conflicts_algorithm
# http://aimacode.github.io/aima-java/aima3e/javadoc/aima-core/aima/core/search/csp/BacktrackingStrategy.html
# -------------------------------------------------------

class CSP:
    def __init__(self, n, m, k, constraints):
        self.n = int(n) # n variables
        self.m = int(m) # m constraints
        self.k = int(k) # k possible colors
        self.constraints = constraints
        self.variables = self.set_variables() # unassigned variables
    
    def set_variables(self):
        variables = []
        for num in range(self.n):
            variables.append(str(num))
        return variables

def is_complete(assignment, csp): # assignment is the path taken
    if (len(assignment) != csp.n):
        return False    
    return True

# input file format
# N variables, numbered 0 to N-1
# M constraints connecting them
# K possible colors for each of variables
# then on each following line, give constraints one by one, U and V
def input_to_csp(file):
    f = open(file)
    line = f.readline().strip('\n')
    first = line.split()
    n = first[0]
    m = first[1]
    k = first[2]
    constraints = []
    for line in f:
        line = line.strip('\n')
        c = line.split()
        constraints.append((c[0], c[1]))
    csp = CSP(n, m, k, constraints)
    print("constraints", constraints)
    return csp

def plain_select_unassigned_variable(csp):
    # variables is unassigned items
    # This default implementation just selects the first in the ordered list of variables provided by the CSP.
    var = csp.variables[0]
    csp.variables.remove(var)
    return var

def plain_order_domain_values(var, assignment, csp):
    # Primitive operation, ordering the domain values of the specified variable. 
    # This default implementation just takes the default order provided by the CSP.
    domain_values = []
    for k in range(csp.k):
        domain_values.append(k)
    return domain_values

def consistent(var, value, assignment, csp): # adjacent nodes cannot have the same color - check is consistent with the current assignments
    for constraint in csp.constraints:
        if (var in constraint):
            neighbor = constraint[constraint.index(var)-1]
            # check that adjacent node does not have the same color
            if ((neighbor in assignment) and assignment[neighbor] == value):
                return False
    return True

def plain_backtracking_search(csp):
    # plain DFS, traverse the node tree depth first order
    # if current node doesn't satisfy constraints, skip node and it's children
    return plain_recursive_backtracking({}, csp)

def plain_recursive_backtracking(assignment, csp): # returns solution or failure
    if (is_complete(assignment, csp)): # if assignment is complete, return assignment (like goal test)
        return assignment
    var = plain_select_unassigned_variable(csp) # var <- select_unassigned_variable(variables[csp],assignment,csp)
    for value in plain_order_domain_values(var, assignment, csp): # given the variable (var) that we have, explore all possible values that you can assign
        if consistent(var, value, assignment, csp): # if value is consistent with assignment given constraints[csp] then
            assignment[var] = value # add {var = value} to assignment
            result = plain_recursive_backtracking(assignment, csp)
            if (result): # if result not equal failure then return result
                return result
            assignment.pop(var, None) # remove {var = value} from assignment
    return False

# -------------------------------------------------------
### Main class ###

if __name__ == '__main__':
    # dfsb.py - This should run in two modes. a) Plain DFS-B and 
    # b)DFS-B with variable, value ordering + AC3 for constraint propagation.
    # A sample execution of dfsb.py should be as below:
        # python dfsb.py <INPUT FILE> <OUTPUT FILE> <MODE FLAG>.
    # <MODE FLAG> can be either 0 (plain DFS-B) or 1 (improved DFS-B).
    
    # (sys.argv[0]) # dfsb.py
    input = (sys.argv[1]) # INPUT FILE PATH
    output = (sys.argv[2]) # OUTPUT FILE PATH
    mode = (sys.argv[3]) # MODE FLAG
    
    print(plain_backtracking_search(input_to_csp(input)))