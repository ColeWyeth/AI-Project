from base import *
import enum
import random

from typing import Dict, List

from program import Program, Block, Box
from cfg import CFG

class Sym(enum.Enum):
    EXEC            = 1

    IF_THEN_ELSE    = 2
    PASS            = 3
    WHILE           = 4
    SEQ             = 5
    GETS            = 6
    ASSIGN          = 7
    ASSIGN_INT      = 8
    INT_BINDING     = 42
    INT_LVAL        = 40
    ASSIGN_BOOL     = 9
    BOOL_BINDING    = 43
    BOOL_LVAL       = 41

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

Generative_Rules = {
    Sym.EXEC: [
        (Sym.IF_THEN_ELSE, [Sym.BOOL_EXP, Sym.EXEC, Sym.EXEC]),
        (Sym.PASS, []),
        (Sym.WHILE, [Sym.BOOL_EXP, Sym.EXEC]),
        (Sym.SEQ, [Sym.EXEC, Sym.EXEC]),
        (Sym.GETS, [Sym.ASSIGN]),
    ],

    Sym.ASSIGN : [(Sym.ASSIGN_INT,[]), (Sym.ASSIGN_BOOL, [])],

    Sym.ASSIGN_BOOL : [(Sym.BOOL_BINDING, [Sym.BOOL_LVAL, Sym.BOOL_EXP])],

    Sym.ASSIGN_INT : [(Sym.INT_BINDING, [Sym.INT_LVAL, Sym.INT_EXP])],

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

variable_symbols = [
    Sym.LOCAL_BOOL,
    Sym.LOCAL_INT,
    Sym.WINDOW_BOOL,
    Sym.WINDOW_INT,
    Sym.BOOL_LVAL,
    Sym.INT_LVAL,
]

def get_variable_options(p, s : Sym):
    if s == Sym.LOCAL_INT:
        return p.int_locals
    elif s == Sym.LOCAL_BOOL:
        return p.bool_locals
    elif s == Sym.WINDOW_BOOL:
        return p.ins[bool] + p.outs[bool]
    elif s == Sym.WINDOW_INT:
        return p.ins[int] + p.outs[int]
    elif s == Sym.BOOL_LVAL:
        return p.bool_locals + p.outs[bool]
    elif s == Sym.INT_LVAL:
        return p.int_locals + p.outs[int]
    else:
        raise Exception("Variable symbol optionless")

def g_sugar(block, abstract_syntax):
    if block.symbol in variable_symbols:
        return block.var.get_name()
    return abstract_syntax
    
def g_printer(block):
    return Block.rec_block_printer(block, g_sugar)

# The proper way to call an unbounded runtime block
# is to create a thread to run the interpreter and kill it 
# after some maximum runtime. 
def g_interpreter(block):
    pass

# The combination of CFG and interpreter should "plug in" to the program class. Ideally the search process 
# with also work for an arbitrary CFG and interpreter. 


def baseline_random_search(g : CFG, p: Program, s : Sym = -1, int_regs : int = 2, bool_regs : int = 2):
    for i in range(int_regs):
        p.add_int_local()
    for i in range(bool_regs):
        p.add_bool_local()
    return random_block_search(g, p, s)

def random_block_search(g : CFG, p : Program, s : Sym = -1):
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
    b = Block(s)
    for c in children:
        # the children of a block should be blocks
        b.children.append(random_block_search(g, p, c))
    if b.symbol in variable_symbols:
        b.var = random.choice(get_variable_options(p, b.symbol))
    return b

def main():
    p = Program(
        {int: [Box(int, "X")], bool : [] },
        {int : [Box(int, "Y")], bool : []},
    )
    p.ins[int][0].gets(1)
    p.block = baseline_random_search(Generative, p)
    print(g_printer(p.block))
    #p.block.execute()

if __name__ == "__main__":
    main()
