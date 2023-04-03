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

    INT_EXP         = 24

    INT_BASIC       = 25
    ONE             = 26
    NEG_ONE         = 27
    CONST           = 28
    RAND_INT        = 29
    LOCAL_INT       = 30
    WINDOW_INT      = 31

    INT_OP          = 32
    PLUS            = 33
    MULT            = 34
    IND             = 35


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



# A program manages an environment, input and output memory locations
# (which may be anytime modifiable and readable) and a block.
# Searching over blocks is best handled externally to the program class; 
# a reference to program will be required by the search algorithm 
# for access to the relevant ins and outs and to set the block attribute.
class Program:
    def __init__(self, ins: Dict[type, List[Window]], outs: Dict[type, List[Window]]):
        self.ins = ins
        self.outs = outs
        self.block = Exec()

    def get_block(self):
        return self.block

    def execute(self):
        self.block.run()

# A block is a partially constructed program module
class Block:
    def __init__(self):
        self.children = []
    def replacements(self):
        pass
    def execute(self):
        raise Exception("Not implemented")
    def __repr__(self):
        return self.sym.name
    
# TODO: Blocks with pointers should be the only actual construct outside of the CFG definition.
# They will carry a symbol and sometimes indexing information for locals and windows, as well as
# an (often empty) list of child blocks. 

# TODO: Concisely specify an interpreter

# The combination of CFG and interpreter should "plug in" to the program class. Ideally the search process 
# with also work for an arbitrary CFG and interpreter. 

class NewLocalInt:
    def __init__(self):
        Block.__init__(self)
        self.sym = Sym.NEW_LOCAL_INT


class IntBasic:
    pass

class IntExp(Block):
    def __init__(self):
        self.sym = Sym.INT_EXP
        self.children = []
        Block.__init__(self)
    def replacements(self, program):
        return [IntOp, IntBasic]
    
class Pass(Block):
    def __init__(self):
        self.sym = Sym.PASS
        self.children = []
        Block.__init__(self)
    def replacements(self, program):
        return None
    def execute(self):
        pass

L_EXECUTABLES = [
    Pass,]
#     While,
#     Seq, 
#     Gets,
#     IfThenElse,
# ]

class Exec(Block):
    def __init__(self):
        self.sym = Sym.EXEC
        super().__init__()
    def replacements(self, program):
        return L_EXECUTABLES 


# A symbol is an executable piece of a program
# class Symbol(Block):
#     def execute(self)

def random_search(b : Block, p : Program):
    if b.replacements(p) is None:
        return b
    else:
        nb = random.choice(b.replacements(p))()
        nb.children = [random_search(sb, p) for sb in nb.children]
        return nb

def main():
    p = Program([],[])
    p.block = random_search(p.get_block(), p)
    print(p.block)
    p.block.execute()

if __name__ == "__main__":
    main()
