from typing import List, Dict, Tuple

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

# TODO: allow a list of discrete values
class CDT:
    def __init__(self, dists: List[List[float]], vals: List[str] = None):
        self.dists = dists
        if vals is None:
            vals = ["Val%d"%i for i in range(len(dists[0]))]
        self.vals = vals

#CDT = List[float]

def dict_to_CDT(readable: List[Tuple[Assignment, float]]) -> CDT:
    cdt = [0 for i in len(readable)]
    for assignment, probability in readable:
        cdt[indexify(assignment)] = probability

class Variable_Node:
    def __init__(self, parents : list, cdt: CDT, name=None): # TODO: list should be list[Variable_Node] ideally
        if name is None:
            name = next_name()
        self.parents = parents
        self.cdt = cdt
        self.name = name
        self.children = []
        for p in self.parents:
            p.children.append(self)

    def __repr__(self):
        string = "Node %s\n" % self.name
        string += "Parents: "
        for p in self.parents:
            string += "%s " % p.name
        string += "\nChildren: "
        for c in self.children:
            string += "%s " % c.name
        return string
        

    # TODO: dict is used instead of set because soon any discrete values
    # will be allowed.
    def fully_conditioned_dist(self, parent_vals: Dict[str, bool]):
        assignment = [parent_vals[p.name] for p in self.parents]
        return self.cdt.dists[indexify(assignment)]

    def get_value_names(self):
        return self.cdt.vals
    
def main():
    coinFlip = Variable_Node(
        parents=[],
        cdt=CDT([[0.5,0.5]], ["H","T"]),
        name="coin flip",
    )
    resultCalled = Variable_Node(
        parents=[coinFlip],
        cdt=CDT([[0.99,0.01],[0.01,0.99]], ["H","T"]),
        name="result called"
    )
    print(coinFlip)
    print(resultCalled)
    print("If %s comes up H" % (coinFlip.name))
    resultDist = resultCalled.fully_conditioned_dist({coinFlip.name:True})
    for i, name in enumerate(resultCalled.get_value_names()):
        print("%s is %s with probability %.2f" % (resultCalled.name, name, resultDist[i]))

if __name__ == "__main__":
    main()