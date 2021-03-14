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
        self.domain = self.set_domain()
        self.variables = self.set_variables() # array of nodes
        self.constraints = constraints
    
    def set_domain(self):
        domain = []
        for color in range(self.k):
            domain.append(color)
        return domain

    def set_variables(self):
        variables = []
        for key in range(self.n):
            node = Node(str(key), self.domain)
            variables.append(node)
        return variables

    def get_node(self, key):
        for node in self.variables:
            if (node.key == key):
                return node
        return False
    
    def get_neighbors(self, node):
        neighbors = []
        for constraint in self.constraints:
            if (node.key in constraint):
                neighbor_key = constraint[constraint.index(node.key)-1]
                neighbor_node = self.get_node(neighbor_key)
                neighbors.append(neighbor_node)
        return neighbors

# -------------------------------------------------------
### helpful funcitons ###

def get_unassigned(csp, assignment):
        unassigned = []
        for var in csp.variables:
            if (var.key not in assignment):
                unassigned.append(var)
        return unassigned

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
### DFS-B methods (for both) ###

def is_complete(assignment, csp): # assignment is the path taken
    if (len(assignment) != csp.n):
        return False    
    return True

def consistent(var, value, assignment, csp): # adjacent nodes cannot have the same color - check is consistent with the current assignments
    for neighbor in csp.get_neighbors(var):
        if ((neighbor.key in assignment) and assignment[neighbor.key] == value):
            return False
    return True

# -------------------------------------------------------
### Plain DFS-B ###

def plain_select_unassigned_variable(assignment, csp):
    # This default implementation just selects the first in the ordered list of variables provided by the CSP.
    unassigned = get_unassigned(csp, assignment)
    return unassigned[0]

def plain_order_domain_values(var, assignment, csp):
    # Primitive operation, ordering the domain values of the specified variable. 
    # This default implementation just takes the default order provided by the CSP.
    return var.domain

def plain_backtracking_search(csp):
    # plain DFS, traverse the node tree depth first order
    # if current node doesn't satisfy constraints, skip node and it's children
    return plain_recursive_backtracking({}, csp)

def plain_recursive_backtracking(assignment, csp): # returns solution or failure
    if is_complete(assignment, csp): # if assignment is complete, return assignment (like goal test)
        return assignment
    var = plain_select_unassigned_variable(assignment, csp) # var <- select_unassigned_variable(variables[csp],assignment,csp)
    for value in plain_order_domain_values(var, assignment, csp): # given the variable (var) that we have, explore all possible values that you can assign
        if consistent(var, value, assignment, csp): # if value is consistent with assignment given constraints[csp] then
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
# Constraint propagation (inference)
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
    unassigned = get_unassigned(csp, assignment)
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
    values_remain = {} # key = color, value = total number of values remaining for other variables

    # assume the value for the variable and 
    # use the constraint graph to check how many values remain for the other variables
    for value in var.domain:
        counter = 0 # amount of choices
        for neighbor in csp.get_neighbors(var): # neighbor (from constraint)
            if (value in neighbor.domain):
                counter += (len(neighbor.domain)-1)
            else:
                counter += len(neighbor.domain)
        values_remain[value] = counter

    ordered_domains = sorted(values_remain, key=values_remain.get)
    ordered_domains = ordered_domains[::-1] # greatest amount of choices to least
    return ordered_domains

def forward_checking(csp, var, value):
    # forward checking
    # when a variable is assigned a value
    # prune incompatible values from the domain of its neighbors
    # terminate when any variable has no legal values
    print("node is", var.key, "with value", value)
    for xj in csp.get_neighbors(var): # for all xj exsits in neighbors (of xi)
        # pruning xj when xi = a
        print("neighbor xj", xj.key, "domain is", xj.domain)
        for b in xj.domain: # for all b exists in domain (of xj)
            if (value == b): # xi = a AND xj = b is incompatible (according to constraint)
                # then remove b from domain (xj)
                xj.domain.remove(b)
                print("new xj domain", xj.domain)
                if (not xj.domain):
                    return False
    return csp

def ac3(csp):
    # arc consistency
    # prune domains of a variable whenever the domains of its neighbors change
    queue = [] # queue of arcs, initially all the arcs in csp

    return csp # returns ths csp, possible with reduced domains

def remove_inconsistent_values(xi, xj):
    print()

def inference(csp, var, value):
    # pruning domains (prune out values form the CSP)
    # use forward checking and use AC3
    print("inference")
    # forward checking
    forward_checking(csp,var,value)
    # constraint propagation
    # arc consistency
    
    # keep a queue of arcs tail(var) -> head(var)
    # until queue is empty:
        # pop an arc xi -> xj from queue
        # prune domain of xi based on xj's domain
        # if domain of xi was pruned
            # add all arcs xk -> xi to the queue
    
    # an arc xi -> xj is consistent if:
        # a exists domain (xi) 
        # b exists domain (xj)
        # such that: 
        # xi = 1 and xj = b is consistent with constraitns (CSP)

    print()

def improved_backtracking_search(csp):
    return improved_recursive_backtracking({}, csp)

def improved_recursive_backtracking(assignment, csp):
    if is_complete(assignment, csp): # if assignment is complete, return assignment (like goal test)
        return assignment
    var = improved_select_unassigned_variable(assignment, csp) # var <- select_unassigned_variable(variables[csp],assignment,csp)
    for value in improved_order_domain_values(var, assignment, csp): # given the variable (var) that we have, explore all possible values that you can assign
        if consistent(var, value, assignment, csp): # if value is consistent with assignment given constraints[csp] then
            assignment[var.key] = value # add {var = value} to assignment
            var.domain = [value] # set domain

            inferences = inference(csp, var, value)
            if inferences:
                # add inferences to the assignment
                print("TRUE")
                
            result = improved_recursive_backtracking(assignment, csp)
            if (result): # if result not equal failure then return result
                return result
            assignment.pop(var.key, None) # remove {var = value} from assignment
            var.domain = csp.domain # reset domain
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
    print("---")
    print(improved_backtracking_search(input_to_csp(input)))