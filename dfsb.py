import sys

# -------------------------------------------------------
# Sources used:
# Lecture slides
# http://pages.cs.wisc.edu/~bgibson/cs540/handouts/csp.pdf
# https://en.wikipedia.org/wiki/Min-conflicts_algorithm
# -------------------------------------------------------

class CSP:
    def __init__(self, n, m, k, graph):
        self.n = int(n) # n variables
        self.m = int(m) # m constraints
        self.k = int(k) # k possible colors
        self.graph = graph # constraints
        self.variables = self.set_variables()
    
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
    graph = {} # adjacency list
    for line in f:
        line = line.strip('\n')
        constraint = line.split()
        if (constraint[0] not in graph):
            graph[constraint[0]] = []
        graph[constraint[0]].append(constraint[1])
    csp = CSP(n, m, k, graph)
    print(graph)
    return csp

def plain_select_unassigned_variable(variables, assignment, csp):
    # variables is unassigned items
    if (not assignment):
        print(variables)
        # return variables[0]
    # unassigned = []
    # for var in variables:
    #     if (var not in assignment):
    #         unassigned.append(var)
    # selected = unassigned[0]
    return False

def plain_order_domain_values(var, assignment, csp):
    return False

def plain_backtracking_search(csp):
    # plain DFS, traverse the node tree depth first order
    # if current node doesn't satisfy constraints, skip node and it's children
    return plain_recursive_backtracking({}, csp)

def plain_recursive_backtracking(assignment, csp): # returns solution or failure
    # if assignment is complete, return assignment
    if (is_complete(assignment, csp)): # like goal test
        return assignment
    # var <- select_unassigned_variable(variables[csp],assignment,csp)
    var = plain_select_unassigned_variable(csp.variables, assignment, csp)
    # for each value in order_domain_values(var,assignment,csp) do
    # given the variable (var) that we have, explore all possible values that you can assign
        # if value is consistent with assignment given constraints[csp] then
        # adjacent nodes cannot have the same color - check is consistent with the current assignments
            # add {var = value} to assignment
            # result <- recursive_backtracking(assignment,csp)
            # if result not equal failure then return result
            # remove {var = value} from assignment
    return False


'''
# writes the solution path array to the output file
def write_output(path, file):
    output = ",".join(path)
    f = open(file, "w")
    for ch in output:
        f.write(ch)
    f.close()
    return True

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)

class Node:
    def __init__(self, problem, parent=None, action=None):
        self.problem = problem
        self.parent = parent
        self.action = action
        self.state = problem.state
        # g(n)
        if (self.parent != None):
            # cost of parent's path + distance from between parent and node
            self.g = parent.g + 1 
        else:
            self.g = 0
        # f(n) = g(n) + h(n)

def reconstruct_path(node):
    solution = []
    ptr = node
    while(ptr.parent!=None):
        solution.insert(0, ptr.action)
        ptr = ptr.parent
    # print("Depth", len(solution))
    return solution

def a_star(problem, h):
    # frontier = priority_queue() # sort frontier on expected path cost
    frontier = queue.PriorityQueue()
    # frontier = frontier + make-node(start)
    start = Node(problem)
    frontier.put(PrioritizedItem(0, start))
    explored = []

    # f(n) = g(n) + h(n)
    # g(n) = cost of path from start to n so far (dist from root)
    # h(n) = estimated cost from n to G (end node)

    # start has no parent
    # start.g = 0
    start.h = h(start.state)
    start.f = start.g + start.h

    # while not frontier.isempty():
    while not frontier.empty():
        # current <- pop(frontier) # i.e., the top of the queue
        current = frontier.get().item
        # if goal-test(current) return success # goal test when node expands
        if problem.goal_test(current.state):
            # print("Number of states explored:", len(explored)+1, "ANSWER:", reconstruct_path(current))
            return reconstruct_path(current) 
        # if current not in explored:
        if not current in explored:
            # explored <- explored + current.state
            explored.append(current.state)
            # for each action in current.actions():
            for action in problem.state_actions(current.state): # neighbors/sucessors
                # new <- action(current.state)
                new = problem.change_state(current.state, action) # new problem
                # new-node <- make-node(new, current, action)
                new_node = Node(new, current, action) # neighbor
                # new_node.g = new_node.parent.g + 1 
                new_node.h = h(new_node.state)
                new_node.f = new_node.g + new_node.h
                
                if (not new_node.state in explored):
                    # frontier = frontier + new-node
                    frontier.put(PrioritizedItem(new_node.f, new_node))
    return False

counter = 1

def recursive_best_first_search(problem, h):
    global counter
    counter = 1
    # solution, fvalue <- rbfs(problem, node(problem.initial), inf, h)
    start = Node(problem)
    start.h = h(start.state)
    start.f = start.g + start.h
    solution = rbfs(problem, start, float("inf"), h)
    return solution

def rbfs(problem, node, f_limit, h):
    # returns solution or failure, and a new f-cost limit
    if (problem.goal_test(node.state)):
        return reconstruct_path(node)
    sucessors = []
    for action in problem.state_actions(node.state, node.action): # neighbors/sucessors
        # add child_node(problem, node, action) into sucessors
        new = problem.change_state(node.state, action) # new problem
        child_node = Node(new, node, action) # neighbor
        child_node.h = h(child_node.state)
        child_node.f = child_node.g + child_node.h
        sucessors.append(child_node)
    if (not sucessors): # if successors is empty
        # return failure, infinity
        return (False, float("inf"))
    for s in sucessors:
        # update f with value from previous search if any
        s.f = max(s.g + s.h, node.f)
    # loop do
    while True:
        # best <- lowest f-value in successors
        best = sucessors[0]
        alternative = best
        for s in sucessors:
            if (s.f <= best.f):
                alternative = best
                best = s
            elif (s.f <= alternative.f):
                alternative = s
        # if best.f > f-limit then return failure, best.f
        if (best.f > f_limit):
            return (False, best.f)
        # alternative <- the second lowest f-value among successors
        # result, best.f <- RBFS(problem, best, min(f-limit,alternative))
        global counter
        counter += 1
        result = rbfs(problem, best, min(f_limit, alternative.f), h)
        best.f = result[1]
        # if result not = failure then return result
        if (result[0]):
            return result
'''
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
    
    test = input_to_csp(input)
    print(plain_backtracking_search(test))