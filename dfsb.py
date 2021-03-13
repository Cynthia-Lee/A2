from os import unlink
import sys

# -------------------------------------------------------
# Sources used:
# Lecture slides
# http://pages.cs.wisc.edu/~bgibson/cs540/handouts/csp.pdf
# https://en.wikipedia.org/wiki/Min-conflicts_algorithm
# https://www.ics.uci.edu/~welling/teaching/271fall09/CSP271fall09.pdf
# http://aimacode.github.io/aima-java/aima3e/javadoc/aima-core/aima/core/search/csp/BacktrackingStrategy.html
# https://en.wikipedia.org/wiki/Min-conflicts_algorithm
# -------------------------------------------------------

class Node: 
    def __init__(self, key, domain):
        self.key = key
        self.domain = domain # set domains, one for each variable
        # domain is it's legal values

class CSP:
    def __init__(self, n, m, k, constraints):
        self.n = int(n) # n variables
        self.m = int(m) # m constraints
        self.k = int(k) # k possible colors
        self.variables = self.set_variables() # array of nodes
        self.constraints = constraints
    
    def set_variables(self):
        variables = []
        domain = []
        for color in range(self.k):
            domain.append(color)
        for key in range(self.n):
            node = Node(str(key), domain)
            variables.append(node)
        return variables

    def get_node(self, key):
        print("vars", self.variables)
        for node in self.variables:
            if (node.key == key):
                return node
        return False

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

# -------------------------------------------------------
### Plain DFS-B ###

def plain_select_unassigned_variable(assignment, csp):
    # variables is unassigned items
    # This default implementation just selects the first in the ordered list of variables provided by the CSP.
    for var in csp.variables:
        if (var.key not in assignment):
            return var
    return False

def plain_order_domain_values(var, assignment, csp):
    # Primitive operation, ordering the domain values of the specified variable. 
    # This default implementation just takes the default order provided by the CSP.
    return var.domain

def plain_consistent(var, value, assignment, csp): # adjacent nodes cannot have the same color - check is consistent with the current assignments
    for constraint in csp.constraints:
        if (var.key in constraint):
            neighbor = constraint[constraint.index(var.key)-1]
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
    var = plain_select_unassigned_variable(assignment, csp) # var <- select_unassigned_variable(variables[csp],assignment,csp)
    for value in plain_order_domain_values(var, assignment, csp): # given the variable (var) that we have, explore all possible values that you can assign
        if plain_consistent(var, value, assignment, csp): # if value is consistent with assignment given constraints[csp] then
            assignment[var.key] = value # add {var = value} to assignment
            result = plain_recursive_backtracking(assignment, csp)
            if (result): # if result not equal failure then return result
                return result
            assignment.pop(var.key, None) # remove {var = value} from assignment
    return False

# -------------------------------------------------------
### Improved DFS-B ###

# DFS-B with variable, value ordering + AC3 for constraint propagation

# Variable (select-unassigned-variable)
    # Most constrained variable, Minimum remaining values (MRV) heuristic 
# Value ordering (order-domain-values)
    # Least constraining value, (LCV) heuristic
# Constraint propagation (is-consistent) (inference)
    # AC3, arc consistency
    # Forward checking

def count_constraints(csp):
    count = {}
    for n in range(csp.n):
        count[str(n)] = 0
    for constraint in csp.constraints:
        u = constraint[0]
        v = constraint [1]
        count[u] += 1
        count[v] += 1
    return count

def improved_select_unassigned_variable(assignment, csp):
    # most constrained variable, use minimum remaining values (MRV) degree heuristic
    # choose the variable with the fewest legal values
    # choose the variable with the most constraints on remaining variables
    # In case of a tie, choose the variable that is involved in the most
    # constraints on remaining variables = degree heuristic
    unassigned = []
    for var in csp.variables:
        if (var.key not in assignment):
            unassigned.append(var)
    
    count = count_constraints(csp)
    
    min = unassigned[0]
    for var in unassigned[1:]: 
        var_values = len(var.domain) # possible remaining values for var
        min_values = len(min.domain) # possible remaining values for min
        if (var_values < min_values): # mvc heuristic
            min = var
        elif (var_values == min_values): # degree heuristic
            if (count[min.key] < count[var.key]): # most edges on the graph (constraints)
                min = var
    return min

def improved_order_domain_values(var, assignment, csp):
    # least constraining value, use LCV
    # the one that rules out the fewest values in the remaining variables
    # try to pick values best first
    ordered_domains = []
    values_remain = {}
    # assume the value for the variable and 
    # use the constraint graph to check how many values remain for the other variables
    print("var", var.key)
    for value in var.domain: # possible values for var
        counter = 0 # amount of choices
        print("---color", value)
        for constraint in csp.constraints:
            print("con", constraint)
            if (var.key in constraint):
                neighbor = constraint[constraint.index(var.key)-1]
                print("n", neighbor)
                neighbor_node = csp.get_node(neighbor)
                if (value in neighbor_node.domain):
                    counter += (len(neighbor_node.domain)-1)
                else:
                    counter += len(neighbor_node.domain)
        values_remain[value] = counter
    print(values_remain)
    print("go over this later")
    ordered_domains = sorted(values_remain, key=values_remain.get)
    ordered_domains = ordered_domains[::-1] # greatest amount of choices to least
    return ordered_domains

def improved_consistent(var, value, assignment, csp):
    # use AC3
    # use forward checking
    print("incomplete")
    return plain_consistent(var, value, assignment, csp)

def improved_backtracking_search(csp):
    return improved_recursive_backtracking({}, csp)

def improved_recursive_backtracking(assignment, csp):
    if (is_complete(assignment, csp)): # if assignment is complete, return assignment (like goal test)
        return assignment
    var = improved_select_unassigned_variable(assignment, csp) # var <- select_unassigned_variable(variables[csp],assignment,csp)
    for value in improved_order_domain_values(var, assignment, csp): # given the variable (var) that we have, explore all possible values that you can assign
        '''
        if improved_consistent(var, value, assignment, csp): # if value is consistent with assignment given constraints[csp] then
            assignment[var] = value # add {var = value} to assignment
            result = improved_recursive_backtracking(assignment, csp)
            if (result): # if result not equal failure then return result
                return result
            assignment.pop(var, None) # remove {var = value} from assignment
        '''
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
    
    # print(plain_backtracking_search(input_to_csp(input)))
    # print("---")
    print(improved_backtracking_search(input_to_csp(input)))