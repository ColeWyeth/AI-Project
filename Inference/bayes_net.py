from typing import List, Dict, Tuple, Callable, Any

names_given = 0
def next_name():
    global names_given
    names_given += 1
    return "V%d" % names_given

Assignment = List[bool]

def indexify(assignment: Assignment) -> int:
    """Convert a tuple of bools into an index for the final column
    of the corresponding truth table, conventionally ordered.
    """
    index = 0
    # Start from the back of assignments,
    # which is indexed from (negative) one
    for i in range(1, len(assignment)+1):
        if assignment[-i]:
            index += 2**(i-1)
    # Remember Python lists are 0 indexed
    return index-1

# class CDT:
#     def __init__(self, dists: List[List[float]], vals: List[str] = None):
#         self.dists = dists
#         if vals is None:
#             vals = ["Val%d"%i for i in range(len(dists[0]))]
#         self.vals = vals

class Variable_Node: pass

Discrete_Dist = Dict[Any, float]

class Discrete_CDT:
    # TODO: if I made the second argument a dict, I could extract the third. But this may be less extensible. 
    def __init__(self, parents: List[Variable_Node], dists: Callable[[Tuple], Discrete_Dist], values: List):
        self.parents = parents
        self.dists = dists
        self.values = values

    def __call__(self, pvalues: Tuple) -> Discrete_Dist:
        return self.dists(pvalues)

    def __repr__(self):
        string = ""
        for p in self.parents:
            string += "%s " % (p.name)
        string += "| "
        for v in self.values:
            string += "%s " % (str(v))
        line_length = len(string)-1
        string += "\n"
        string += line_length*"-"
        string += "\n"
        def helper(first_ind):
            if not first_ind < len(self.parents):
                return [[]]
            conditions = []
            tail_assignments = helper(first_ind+1)
            for v in self.parents[first_ind].get_values():
                conditions.extend([[v]+l for l in tail_assignments])
            return conditions
        conditions = helper(0)
        for condition in conditions:
            for val in condition:
                string += "%s " % (str(val))
            string += "| "
            dist = self.dists(tuple(condition))
            print(dist)
            for val in self.values:
                string += "%.2f " % (dist[val])
            string += "\n"
        return string
    
    def getParents(self):
        return self.parents
    
    def evaluate_fully_conditioned(self):
        return self.dists(tuple([p.value for p in self.parents]))



#CDT = List[float]

# def dict_to_CDT(readable: List[Tuple[Assignment, float]]) -> CDT:
#     cdt = [0 for i in len(readable)]
#     for assignment, probability in readable:
#         cdt[indexify(assignment)] = probability


class Variable_Node:
    def __init__(self, cdt: Discrete_CDT, name=None): # TODO: continuous CDTs?
        if name is None:
            name = next_name()
        self.parents = cdt.getParents()
        self.cdt = cdt
        self.name = name
        self.children = []
        for p in self.parents:
            p.children.append(self)
        self.value = None

    def __repr__(self):
        string = "Node %s\n" % self.name
        string += "Parents: "
        for p in self.parents:
            string += "%s " % p.name
        string += "\nChildren: "
        for c in self.children:
            string += "%s " % c.name
        string += "\n"
        string += str(self.cdt)
        return string
    
    def get_fully_conditioned_dist(self):
        return self.cdt.evaluate_fully_conditioned()
    
    def get_values(self):
        return self.cdt.values
        

    # TODO: dict is used instead of set because soon any discrete values
    # will be allowed.
    # def fully_conditioned_dist(self, parent_vals: Dict[str, bool]):
    #     assignment = [parent_vals[p.name] for p in self.parents]
    #     return self.cdt.dists[indexify(assignment)]


    # TODO: Make the below implementable and implement it
    # def get_value_names(self):
    #     return self.cdt.vals

class Bayes_Net:
    def __init__(self, nodes: List[Variable_Node]):
        self.nodes = nodes

    def P(self, values: List[Any], cond=[]):
        for i, node in enumerate(self.nodes):
            node.value = values[i]
        p = 1
        for node in self.nodes:
            p *= node.get_fully_conditioned_dist()[node.value]
        # if cond:
        #     return p/self.P(values.extend(cond)) 
        return p
    
def main():
    coinFlip = Variable_Node(
        cdt=Discrete_CDT(
                [],
                lambda _: {"H":0.5, "T":0.5},
                values=["H","T"],
            ),
        name="coinFlip",
    )
    resultCalled = Variable_Node(
        cdt=Discrete_CDT(
                [coinFlip],
                lambda r: {"H":0.99, "T":0.01} if r[0]=="H" else {"H":0.01, "T":0.99},
                values=["H","T"],
            ),
        name="resultCalled",
    )
    print(coinFlip)
    print(resultCalled)
    coinFlip.value = "H"
    print("If %s comes up %s" % (coinFlip.name, coinFlip.value))
    resultDist = resultCalled.get_fully_conditioned_dist()
    for k in resultDist.keys():
        print("%s is %s with probability %.2f" % (resultCalled.name, k, resultDist[k]))
    bn = Bayes_Net([coinFlip, resultCalled])
    
    print("Probability of H flipped and reported: %.3f" % (bn.P(["H","H"])))
    print("Probability of H flipped but not reported: %.3f" % (bn.P(["H","T"])))
    #print("Probability of H flipped given H reported: %f", )

if __name__ == "__main__":
    main()