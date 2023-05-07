from base import *
import random

from typing import Dict, List

from program import Program, Block, Box, run_for_time
from cfg import CFG, PCFG, cfg_to_solomonoff_pcfg

from language import Language

# For custom search and examples
from arithmetic_language import Sym, Arithmetic_Language

from matplotlib import pyplot as plt

# The combination of CFG and interpreter should "plug in" to the program class. Ideally the search process 
# with also work for an arbitrary CFG and interpreter. 

def random_block_search(l : Language, p : Program, s : Sym = -1):
    g = l.get_cfg()
    if s == -1:
        s = g.start
    nonterminals = g.rules.keys()
    children = []
    while s in nonterminals:
        cand_s, children = random.choice(g.rules[s])
        # Each length increase should have probability 1/2
        # Roughly speaking, this means a symbol with n children
        # should be 2^n times less likely. 
        undo = False
        for c in children:
            undo = undo or random.choice([True, False])
        if not undo:
            s = cand_s
        #s = cand_s
    b = Block(s)
    for c in children:
        # the children of a block should be blocks
        b.children.append(random_block_search(l, p, c))
    if b.symbol in l.get_variable_symbols():
        b.var = random.choice(l.get_variable_options(p, b.symbol))
    return b

def sample_pcfg(g : PCFG, s : Sym = -1):
    if s == -1:
        s = g.start
    nonterminals = g.rules.keys()
    children = []
    while s in nonterminals:
        s, children = g.sample_rule(s)
    b = Block(s)
    for c in children:
        # the children of a block should be blocks
        b.children.append(sample_pcfg(g, c))
    return b

def function_search(l : Language, p: Program, s : Sym = -1):
    """
        This search method imposes the requirement that after running some initial code,
        each output variable is assigned to.
    """
    b = Block(Sym.SEQ)
    b.children.append(random_block_search(g, p, s))
    assignments = None
    for int_output in p.outs[int]:
        y = Block(Sym.WINDOW_INT)
        y.var = int_output
        assign = Block(Sym.GETS, [Block(Sym.INT_BINDING, [y, random_block_search(g, p, Sym.INT_EXP)])])
        if assignments is None:
            assignments = assign 
        else:
            assignments = Block(Sym.SEQ, [assignments, assign])
    for bool_output in p.outs[bool]:
        y = Block(Sym.WINDOW_BOOL)
        y.var = bool_output
        assign = Block(Sym.GETS, [Block(Sym.BOOL_BINDING, [y, random_block_search(g, p, Sym.BOOL_EXP)])])
        if assignments is None:
            assignments = assign 
        else:
            assignments = Block(Sym.SEQ, [assignments, assign])
    b.children.append(assignments)
    return b

def function_sample(g : PCFG, p : Program, s : Sym = -1):
    """
        This search method imposes the requirement that after running some initial code,
        each output variable is assigned to.
    """
    b = Block(Sym.SEQ)
    b.children.append(sample_pcfg(g, s))
    assignments = None
    for int_output in p.outs[int]:
        y = Block(Sym.WINDOW_INT)
        y.var = int_output
        assign = Block(Sym.GETS, [Block(Sym.INT_BINDING, [y, sample_pcfg(g, Sym.INT_EXP)])])
        if assignments is None:
            assignments = assign 
        else:
            assignments = Block(Sym.SEQ, [assignments, assign])
    for bool_output in p.outs[bool]:
        y = Block(Sym.WINDOW_BOOL)
        y.var = bool_output
        assign = Block(Sym.GETS, [Block(Sym.BOOL_BINDING, [y, sample_pcfg(g, Sym.BOOL_EXP)])])
        if assignments is None:
            assignments = assign 
        else:
            assignments = Block(Sym.SEQ, [assignments, assign])
    b.children.append(assignments)
    return b

class Searcher:
    def __init__(self, l : Language, p : Program):
        self.l = l
        self.p = p
    def search(self):
        pass

class Solomonoff_sampler(Searcher):
    def __init__(self, l : Language, p : Program):
        super().__init__(l, p)
        self.pcfg = cfg_to_solomonoff_pcfg(l.get_cfg(), True)
    def search(self):
        b = sample_pcfg(self.pcfg)
        self.l.bind_semantics(self.p, b)
        return b

class Solomonoff_function_sampler(Solomonoff_sampler):
    def search(self):
        b = function_sample(self.pcfg, self.p)
        self.l.bind_semantics(self.p, b)
        return b 


def main():
    l = Arithmetic_Language
    #pcfg = cfg_to_solomonoff_pcfg(l.get_cfg(), True)
    p = Program(
        {int: [Box(int, "X")], bool : [] },
        {int : [Box(int, "Y")], bool : []},
    )
    ss = Solomonoff_sampler(l, p)
    sfs = Solomonoff_function_sampler(l, p)
    for i in range(2):
        p.add_int_local()
    for i in range(2):
        p.add_bool_local()
    def test(x, y):
        p.wipe_all_variables()
        p.set_input(int, "X", x)
        run_for_time(p, l.interpret, 1)
        return p.get_output(int, "Y") == y
    lengths = [0 for i in range(20)]
    for i in range(10000):
        try:
            #p.block = function_search(Generative, p)
            # Exponential decay is very sharp with 5 bits needed for each 
            # symbol. It would be much better to have less nonterminals. TODO
            # p.block = function_sample(pcfg, p)
            # l.bind_semantics(p, p.block)
            #p.block = ss.search()
            p.block = sfs.search()
            l.print_block(p.block)
            #print(p.block)
            lengths[p.block.length()] += 1
            passed = True
            easy_test = [(3,3), (4,4), (5,5)]
            hard_test = [(3,9), (4,16), (5,25)]
            for x,y in hard_test:
                if not test(x,y):
                    passed = False
                    break
            if passed:
                print("Successful candidate!")
                break
        except RecursionError:
            print("Maximum recursion depth exceeded...")
    print(lengths)
    plt.bar(range(len(lengths)), lengths)
    plt.show()
    l.print_block(p.block)

if __name__ == "__main__":
    main()
