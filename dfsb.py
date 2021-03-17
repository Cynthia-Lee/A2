import sys
from CSP import CSP

# -------------------------------------------------------
# Sources used:
# Lecture slides
# http://pages.cs.wisc.edu/~bgibson/cs540/handouts/csp.pdf
# https://www.ics.uci.edu/~welling/teaching/271fall09/CSP271fall09.pdf
# http://aimacode.github.io/aima-java/aima3e/javadoc/aima-core/aima/core/search/csp/BacktrackingStrategy.html
# https://en.wikipedia.org/wiki/Min-conflicts_algorithm
# -------------------------------------------------------

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

def forward_checking(csp, var, value, assignment):
    # forward checking
    # when a variable is assigned a value
    # prune incompatible values from the domain of its neighbors
    # terminate when any variable has no legal values
    unassigned = get_unassigned(csp, assignment)
    for xj in csp.get_neighbors(var): # for all xj exsits in neighbors (of xi)
        if (xj in unassigned):
            # pruning xj when xi = a
            new_dom = copy(xj.domain)
            if value in xj.domain:
                new_dom.remove(value)
                xj.domain = new_dom       
            # for all b exists in domain (of xj)
                # xi = a AND xj = b is incompatible (according to constraint)
                    # xj.domain.remove(b) # then remove b from domain (xj)
            if (not xj.domain): # xj has no legal values
                return False   
    return csp

def copy(arr):
    new = []
    for element in arr:
        new.append(element)
    return new

def remove_inconsistent_values(xi, xj):
    # prune domain of xi based on xj
    removed = False
    for x in xi.domain: # for each x in Domain[xi] do
        # if no value y in Domain[xj] allows (x,y) to satisfy the constraint Xi <-> Xj
        if len(xj.domain) == 1 and x in xj.domain:
            # then delete x from Domain[xi]
            xi.domain.remove(x)
            removed = True
        # check = copy(xj.domain)
        # if x in check:
        #     check.remove(x)
        # if not check: # if arr is empty
        #     xi.domain.remove(x) # then delete x from Domain[xi]
        #     removed = True
    return removed

def ac3(csp):
    # arc consistency
    # prune domains of a variable whenever the domains of its neighbors change
    queue = []
    # queue of arcs, initially all the arcs in csp
    for constraint in csp.constraints:
        # constraint x<->y
        queue.append(constraint) # x->y
        queue.append(constraint[::-1]) # y->x

    while queue: # while queue is not empty
        arc = queue.pop(0) # (xi, xj) <- remove-first(queue)
        xi = csp.get_node(arc[0])
        xj = csp.get_node(arc[1])
        if remove_inconsistent_values(xi, xj): # remove-inconsistent-values(xi,xj) then
            for xk in csp.get_neighbors(xi): # for each xk in neighbors[xi] do
                queue.append((xk.key, xi.key))
    # if you remove anything from a variable, 
    # then add all arcs that go into that variable back into the queue

    # keep a queue of arcs tail(var) -> head(var)
    # until queue is empty:
        # pop an arc xi -> xj from queue
        # prune domain of xi based on xj's domain
        # if domain of xi was pruned
            # add all arcs xk -> xi to the queue
    
    # returns ths csp, possible with reduced domains
    return csp

    # an arc xi -> xj is consistent if:
        # a exists domain (xi) 
        # b exists domain (xj)
        # such that: 
        # xi = 1 and xj = b is consistent with constraitns (CSP)

        # for every value x at X there is some allowed y, i.e., there is at
        # least 1 value of Y that is consistent with x

    # X -> Y is consistent iff
        # for every value x at X there is some allowed y; if not, delete x
    
    # • If X loses a value, all neighbors of X need to be rechecked
    # • Arc consistency detects failure earlier than forward checking
    # • Can be run as a preprocessor or after each assignment

def inference(csp, var, value, assignment):
    # pruning domains (prune out values form the CSP) using forward checking and using AC3
    # forward checking
    # f_check = forward_checking(csp,var,value, assignment)
    f_check = True
    # constraint propagation
    # arc consistency
    a_check = ac3(csp)
    # a_check = True
    return f_check and a_check

def improved_backtracking_search(csp):
    colors = []
    for color in range(csp.k):
        colors.append(color)
    return improved_recursive_backtracking({}, csp, colors)

def improved_recursive_backtracking(assignment, csp, colors):
    if is_complete(assignment, csp): # if assignment is complete, return assignment (like goal test)
        return assignment
    var = improved_select_unassigned_variable(assignment, csp) # var <- select_unassigned_variable(variables[csp],assignment,csp)
    print("d", var.key, var.domain)
    for value in improved_order_domain_values(var, assignment, csp): # given the variable (var) that we have, explore all possible values that you can assign
        if consistent(var, value, assignment, csp): # if value is consistent with assignment given constraints[csp] then
            assignment[var.key] = value # add {var = value} to assignment
            var.domain = [value] # set domain

            print("og", assignment)
            restore_assignment = {}
            for a in assignment:
                restore_assignment[a] = assignment[a]

            inferences = inference(csp, var, value, assignment)
            if inferences:
                # add inferences to the assignment
                for inference_var in csp.variables:
                    if len(inference_var.domain) == 1:
                        assignment[inference_var.key] = inference_var.domain[0]

                result = improved_recursive_backtracking(assignment, csp, colors)
                if (result): # if result not equal failure then return result
                    return result

            # assignment fails
            # remove inferences from assignment (restore domains)
            for c in csp.variables:
                if (c.key in assignment) and (c.key not in restore_assignment):
                    assignment.pop(c.key, None)
            
            for node in get_unassigned(csp, assignment):
                node.domain = copy(colors)
            
            # remove {var = value} and inferences from assignment
            assignment.pop(var.key, None) 
            var.domain = copy(colors) # reset domain
            print("popped", var.key, assignment)
            print("fail global dom", var.domain, csp.domain)
    return False

# -------------------------------------------------------

# writes the solution assignment to the output file
def write_output(assignment, file):
    f = open(file, "w")
    for i in sorted(assignment): 
        color = str(assignment[i])
        f.write(color)
        if not i == sorted(assignment)[-1]:
            f.write("\n")
    f.close()
    return True

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
    csp = input_to_csp(input)
    assignment = []
    
    if (mode == '0'): # plain DFS-B
        assignment = plain_backtracking_search(csp)
    elif (mode == '1'): # improved DFS-B
        assignment = improved_backtracking_search(csp)
    
    # write to output file
    write_output(assignment, output)

    print("constraints", csp.constraints)
    print("result", assignment)
    
    # print(plain_backtracking_search(input_to_csp(input)))
    # print("---")
    # print(improved_backtracking_search(input_to_csp(input)))

    # print(improved_backtracking_search(input_to_csp("backtrack_easy")))
    # print("---")
    # print(improved_backtracking_search(input_to_csp("backtrack_hard")))