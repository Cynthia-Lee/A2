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
        print("SCREAM")
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