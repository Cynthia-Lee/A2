import sys
import random
from CSP import CSP

# -------------------------------------------------------
# Sources used:
# Lecture slides
# http://pages.cs.wisc.edu/~bgibson/cs540/handouts/csp.pdf
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

def check_assignment(assignment, csp):
    for constraint in csp.constraints:
        u = constraint[0]
        v = constraint[1]
        if (assignment[u] == assignment[v]):
            return False
    return True

def is_complete(assignment, csp): # assignment is the path taken
    if (len(assignment) != csp.n):
        return False    
    return check_assignment(assignment, csp)

def copy(arr):
    new = []
    for element in arr:
        new.append(element)
    return new

# -------------------------------------------------------
### min_conflicts ###

def random_state(csp):
    assignment = {}
    for node in csp.variables:
        assignment[node.key] = random.choice(csp.domain)
    return assignment

def conflicted_variables(assignment, csp):
    conflicted = []
    for constraint in csp.constraints:
        u = constraint[0]
        v = constraint[1]
        if (assignment[u] == assignment[v]):
            if (u not in conflicted):
                conflicted.append(u)
            if (v not in conflicted):
                conflicted.append(v)
    return conflicted

def conflicts(var, assignment, csp):
    ordered_conflicts = []
    values_remain = {} # key = color, value = total number of conflicts

    for value in var.domain:
        counter = 0 # amount of conflicts
        for constraint in csp.constraints:
            u = constraint[0]
            v = constraint[1]
            if (u == var.key):
                if (value == assignment[v]):
                    counter += 1
            elif (v == var.key):
                if (assignment[u] == value):
                    counter += 1
            else:
                if (assignment[u] == assignment[v]):
                    counter += 1
        values_remain[value] = counter
    
    ordered_conflicts = sorted(values_remain, key=values_remain.get)
    return ordered_conflicts

def min_conflicts(csp, max_steps, current_state):
    for i in range(max_steps): # for i ← 1 to max_steps do
        if is_complete(current_state, csp): # if current_state is a solution of csp then
            print("FINISH")
            return current_state # return current_state
        # set var ← a randomly chosen variable from the set of conflicted variables CONFLICTED[csp]
        var = random.choice(conflicted_variables(current_state, csp))
        # set value ← the value v for var that minimizes CONFLICTS(var,v,current_state,csp)
        conflicts(csp.get_node(var), current_state, csp)
        value = "b"
        # set var ← value in current_state
        var = "c" 

    return False

# algorithm MIN-CONFLICTS is
#     input: csp, A constraint satisfaction problem.
#            max_steps, The number of steps allowed before giving up.
#            current_state, An initial assignment of values for the variables in the csp.
#     output: A solution set of values for the variable or failure.

#     for i ← 1 to max_steps do
#         if current_state is a solution of csp then
#             return current_state
#         set var ← a randomly chosen variable from the set of conflicted variables CONFLICTED[csp]
#         set value ← the value v for var that minimizes CONFLICTS(var,v,current_state,csp)
#         set var ← value in current_state

#     return failure

# -------------------------------------------------------
### Main class ###

if __name__ == '__main__':
    # python minconicts.py <INPUT FILE> <OUTPUT FILE>.
    
    # (sys.argv[0]) # minconicts.py
    input = (sys.argv[1]) # INPUT FILE PATH
    output = (sys.argv[2]) # OUTPUT FILE PATH

    csp = input_to_csp(input)
    assignment = []

    state = random_state(csp)
    print("initial state", state)
    assignment = min_conflicts(csp, 1, state)

    # write to output file
    # write_output(assignment, output)

    print("constraints", csp.constraints)
    print("result", assignment)