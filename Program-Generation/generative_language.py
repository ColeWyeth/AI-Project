from base import *
import enum
import random
from typing import Dict, List

class Sym(enum.Enum):
    EXEC            = 1

    IF_THEN_ELSE    = 2
    PASS            = 3
    WHILE           = 4
    SEQ             = 5
    GETS            = 6
    ASSIGN          = 7
    ASSIGN_INT      = 8
    ASSIGN_BOOL     = 9

    BOOL_EXP        = 10

    COMP            = 11
    LESS            = 12
    EQUAL           = 13

    BOOL_OP         = 14
    AND             = 15
    OR              = 16
    NEG_BOOL        = 17

    BOOL_BASIC      = 18
    TRUE            = 19
    FALSE           = 20
    LOCAL_BOOL      = 21
    WINDOW_BOOL     = 22
    RAND_BOOL       = 23
    NEXT_BIT        = 24

    INT_EXP         = 25

    INT_OP          = 33
    PLUS            = 34
    MULT            = 35
    # IND             = 36

    INT_BASIC       = 26
    ONE             = 27
    NEG_ONE         = 28
    # CONST           = 29
    RAND_INT        = 30
    LOCAL_INT       = 31
    WINDOW_INT      = 32


# TODO: Concisely specify a CFG
class CFG:
    def __init__(self, start, rules):
        self.start = start
        self.rules = rules

Generative_Rules = {
    Sym.EXEC: [
        (Sym.IF_THEN_ELSE, [Sym.BOOL_EXP, Sym.EXEC, Sym.EXEC]),
        (Sym.PASS, []),
        (Sym.WHILE, [Sym.BOOL_EXP, Sym.EXEC]),
        (Sym.SEQ, [Sym.EXEC, Sym.EXEC]),
        (Sym.GETS, [Sym.ASSIGN]),
    ],
    Sym.ASSIGN : [(Sym.ASSIGN_INT,[]), (Sym.ASSIGN_BOOL, [])],

    Sym.BOOL_EXP : [
        (Sym.COMP, []), # Note that this is empty because particular comps have children
        (Sym.BOOL_OP, []),
        (Sym.BOOL_BASIC, []),
    ],

    Sym.COMP : [
        (Sym.LESS, [Sym.INT_EXP, Sym.INT_EXP]),
        (Sym.EQUAL, [Sym.INT_EXP, Sym.INT_EXP]),
    ],

    Sym.BOOL_OP : [
        (Sym.AND, [Sym.BOOL_EXP, Sym.BOOL_EXP]),
        (Sym.OR, [Sym.BOOL_EXP, Sym.BOOL_EXP]),
        (Sym.NEG_BOOL, [Sym.BOOL_EXP]),
    ],

    Sym.BOOL_BASIC : [
        (Sym.TRUE, []),
        (Sym.FALSE, []),
        (Sym.LOCAL_BOOL, []),
        (Sym.WINDOW_BOOL, []),
        (Sym.RAND_BOOL, []),
    ],

    Sym.INT_EXP : [
        (Sym.INT_OP, [Sym.INT_EXP, Sym.INT_EXP]),
        (Sym.INT_BASIC, []),
    ],

    Sym.INT_OP : [
        (Sym.PLUS, [Sym.INT_EXP, Sym.INT_EXP]),
        (Sym.MULT, [Sym.INT_EXP, Sym.INT_EXP]),
    ],

    Sym.INT_BASIC : [
        (Sym.ONE, []),
        (Sym.NEG_ONE, []),
        (Sym.RAND_INT, []),
        (Sym.LOCAL_INT, []),
        (Sym.WINDOW_INT, []),
    ],

}
Generative = CFG(Sym.EXEC, Generative_Rules)


# TODO: Implement asynchronous window types
class Window:
    def __init__(self):
        pass 
    def set(self, val):
        pass
    def get(self):
        pass

# A Box is a type of window that can also be used to implement local variables
class Box(Window):
    def __init__(self, t: type, val=None):
        if val=None:
            self.val = t()
        else:
            self.val = val
    def get(self):
        return val
    def set(self, val):
        self.val = val

# class IntBox(Container):
#     def __init__(self, n=0):
#         self.val = n


# A program manages an environment, input and output memory locations
# (which may be anytime modifiable and readable) and a block.
# Searching over blocks is best handled externally to the program class; 
# a reference to program will be required by the search algorithm 
# for access to the relevant ins and outs and to set the block attribute.
class Program:
    def __init__(self, ins: Dict[type, List[Window]], outs: Dict[type, List[Window]]):
        self.ins = ins
        self.outs = outs
        self.block = None

    def get_block(self):
        return self.block

    def execute(self):
        self.block.run()

# A block is a partially constructed program module
class Block:
    def __init__(self, symbol : Sym):
        self.symbol = symbol
        self.children = []
    def __repr__(self):
        child_str = ""
        if self.children:
            child_str = '('
            for c in self.children:
                child_str += str(c) + ','
            child_str += ')'
        return self.symbol.name + child_str
    
# TODO: Blocks with pointers should be the only actual construct outside of the CFG definition.
# They will carry a symbol and sometimes indexing information for locals and windows, as well as
# an (often empty) list of child blocks. 

# TODO: Concisely specify an interpreter

# The combination of CFG and interpreter should "plug in" to the program class. Ideally the search process 
# with also work for an arbitrary CFG and interpreter. 

# class NewLocalInt:
#     def __init__(self):
#         Block.__init__(self)
#         self.sym = Sym.NEW_LOCAL_INT


# class IntBasic:
#     pass

# class IntExp(Block):
#     def __init__(self):
#         self.sym = Sym.INT_EXP
#         self.children = []
#         Block.__init__(self)
#     def replacements(self, program):
#         return [IntOp, IntBasic]
    
# class Pass(Block):
#     def __init__(self):
#         self.sym = Sym.PASS
#         self.children = []
#         Block.__init__(self)
#     def replacements(self, program):
#         return None
#     def execute(self):
#         pass

# L_EXECUTABLES = [
#     Pass,]
# #     While,
# #     Seq, 
# #     Gets,
# #     IfThenElse,
# # ]

# class Exec(Block):
#     def __init__(self):
#         self.sym = Sym.EXEC
#         super().__init__()
#     def replacements(self, program):
#         return L_EXECUTABLES 


# A symbol is an executable piece of a program
# class Symbol(Block):
#     def execute(self)

def baseline_random_search(g : CFG, p: Program, s : Sym = -1, int_regs : int = 2, bool_regs : int = 2):
    for i in range(int_regs):
        p.add_int_local()
    for i in range(bool_regs):
        p.add_bool_local()
    random_block_search(g, p, s)

def random_block_search(g : CFG, p : Program, s : Sym = -1):
    if s == -1:
        s = g.start
    nonterminals = g.rules.keys()
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
    b = Block(s)
    for c in children:
        # the children of a block should be blocks
        b.children.append(random_block_search(g, p, c))
    return b

def main():
    p = Program([],[])
    p.block = random_block_search(Generative, p)
    print(p.block)
    #p.block.execute()

if __name__ == "__main__":
    main()
