import sys
import random
from CSP import CSP
import datetime
from CSPGenerator import CSPGenerator
import math

# -------------------------------------------------------
# Sources used:
# Lecture slides
# http://pages.cs.wisc.edu/~bgibson/cs540/handouts/csp.pdf
# https://en.wikipedia.org/wiki/Min-conflicts_algorithm
# -------------------------------------------------------

# -------------------------------------------------------
### helpful funcitons ###

global steps
steps = 0
global steps_list
steps_list = []

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

# check if assignment is a valid
def check_assignment(assignment, csp): # adjacent nodes cannot have the same color
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

def copy(arr): # makes a deep copy of the array
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

# return conflicted variables
def conflicted_variables(assignment, csp): # adjacent nodes cannot have the same color
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

# returns ordered array of values and # of conflicts for each value
def conflicts(var, assignment, csp): # counts the number of conflicts for each value if assigned to the variable
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
    for i in range(max_steps): # for i ??? 1 to max_steps do
        global steps
        steps += 1
        if is_complete(current_state, csp): # if current_state is a solution of csp then
            print(steps)
            return current_state # return current_state
        conflicted = conflicted_variables(current_state, csp)
        # set var ??? a randomly chosen variable from the set of conflicted variables CONFLICTED[csp]
        var = random.choice(conflicted)            
        # set value ??? the value v for var that minimizes CONFLICTS(var,v,current_state,csp)
        value = conflicts(csp.get_node(var), current_state, csp)[0]
        # set var ??? value in current_state
        current_state[var] = value
    return False

# algorithm MIN-CONFLICTS is
#     input: csp, A constraint satisfaction problem.
#            max_steps, The number of steps allowed before giving up.
#            current_state, An initial assignment of values for the variables in the csp.
#     output: A solution set of values for the variable or failure.

#     for i ??? 1 to max_steps do
#         if current_state is a solution of csp then
#             return current_state
#         set var ??? a randomly chosen variable from the set of conflicted variables CONFLICTED[csp]
#         set value ??? the value v for var that minimizes CONFLICTS(var,v,current_state,csp)
#         set var ??? value in current_state

#     return failure

def min_conflicts_solver(csp):
    global steps
    trial = 0
    start = datetime.datetime.now()
    assignment = False
    expire = False
    while (not assignment or expire): # and time_elapsed < 60 seconds
        trial += 1
        print("trial", trial)
        assignment = min_conflicts(csp, 1000, random_state(csp))
        end = datetime.datetime.now()
        time_elapsed = (end - start)
        if time_elapsed > datetime.timedelta(seconds=60):
            print("around 60 seconds have past")
            expire = True
            return False
    if assignment:
        global steps_list
        steps_list.append(steps)
    return assignment

# -------------------------------------------------------

# writes the solution assignment to the output file
def write_output(assignment, file):
    if (assignment):
        f = open(file, "w")
        for i in sorted(assignment): 
            color = str(assignment[i])
            f.write(color)
            if not i == sorted(assignment)[-1]:
                f.write("\n")
        f.close()
        return True
    else:
        f = open(file, "w")
        f.write("No answer")
        f.close()
        return False

### Main class ###

if __name__ == '__main__':
    # python minconicts.py <INPUT FILE> <OUTPUT FILE>.
    
    # (sys.argv[0]) # minconicts.py
    input = (sys.argv[1]) # INPUT FILE PATH
    output = (sys.argv[2]) # OUTPUT FILE PATH

    start = datetime.datetime.now()

    csp = input_to_csp(input)
    assignment = []

    assignment = min_conflicts_solver(csp)

    # write to output file
    write_output(assignment, output)

    end = datetime.datetime.now()
    time_elapsed = (end - start)

    # print("constraints", csp.constraints)
    # print("result", assignment)
    print("time elapsed", time_elapsed)

    '''
    times = []

    for i in range(20):
        print("test", i)
        steps = 0
        # state = CSPGenerator(20, 100, 4, "parameter_set") # N M K
        # state = CSPGenerator(50, 625, 4, "parameter_set") # N M K
        # state = CSPGenerator(100, 2500, 4, "parameter_set") # N M K
        # state = CSPGenerator(200, 10000, 4, "parameter_set") # N M K
        state = CSPGenerator(400, 40000, 4, "parameter_set") # N M K
        start = datetime.datetime.now()
        csp = input_to_csp("parameter_set")
        assignment = []
        assignment = min_conflicts_solver(csp)
        write_output(assignment, "output")
        end = datetime.datetime.now()
        time_elapsed = (end - start) * 1000.0 # milliseconds
        print(time_elapsed)
        times.append(time_elapsed.total_seconds())
        print("---")
    print(steps_list)
    x = steps_list
    mean = sum(x) / len(x)
    print("mean states", mean)
    sd = math.sqrt(sum([(val - mean)**2 for val in x])/(len(x) - 1))
    print("sd states", sd)
    # print("times", times)
    x = times
    mean = sum(x) / len(x)
    print("mean times", mean)
    sd = math.sqrt(sum([(val - mean)**2 for val in x])/(len(x) - 1))
    print("sd times", sd)
    '''