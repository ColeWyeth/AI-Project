from base import *
import enum
import random

from typing import Dict, List

from program import Program, Block, Box, run_for_time
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
        (Sym.INT_OP, []),
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

def default_to(x, y):
    if len(x):
        return x
    else:
        return [y]

def get_variable_options(p, s : Sym):
    if s == Sym.LOCAL_INT:
        return default_to(p.int_locals, p.NO_INTS)
    elif s == Sym.LOCAL_BOOL:
        return default_to(p.bool_locals, p.NO_BOOLS)
    elif s == Sym.WINDOW_BOOL:
        return default_to(p.ins[bool] + p.outs[bool], p.NO_BOOLS)
    elif s == Sym.WINDOW_INT:
        return default_to(p.ins[int] + p.outs[int], p.NO_INTS)
    elif s == Sym.BOOL_LVAL:
        return default_to(p.bool_locals + p.outs[bool], p.NO_BOOLS)
    elif s == Sym.INT_LVAL:
        return default_to(p.int_locals + p.outs[int], p.NO_INTS)
    else:
        raise Exception("Variable symbol optionless")

def g_sugar(block, abstract_syntax):
    if block.symbol in variable_symbols:
        return block.var.get_name()
    return abstract_syntax
    
def g_to_str(block):
    return Block.rec_block_printer(block, g_sugar)


# The proper way to call an unbounded runtime block
# is to create a thread to run the interpreter and kill it 
# after some maximum runtime. 
def evaluate_int(block):
    if block.symbol == Sym.MULT:
        return evaluate_int(block.children[0])*evaluate_int(block.children[1])
    elif block.symbol == Sym.PLUS:
        return evaluate_int(block.children[0])+evaluate_int(block.children[1])
    elif block.symbol in variable_symbols:
        return block.var.get()
    elif block.symbol == Sym.ONE:
        return 1
    elif block.symbol == Sym.NEG_ONE:
        return -1
    elif block.symbol == Sym.RAND_INT:
        num = 0
        cont = random.choice([True, False])
        while cont:
            num += 1
            cont = random.choice([True, False])
        return num


def evaluate_bool(block):
    if block.symbol == Sym.LESS:
        return evaluate_int(block.children[0]) < evaluate_int(block.children[1])
    elif block.symbol == Sym.EQUAL:
        return evaluate_int(block.children[0]) == evaluate_int(block.children[1])
    elif block.symbol == Sym.AND:
        return evaluate_bool(block.children[0]) and evaluate_bool(block.children[1])
    elif block.symbol == Sym.OR:
        return evaluate_bool(block.children[0]) or evaluate_bool(block.children[1])
    elif block.symbol == Sym.NEG_BOOL:
        return not evaluate_bool(block.children[0])
    elif block.symbol == Sym.TRUE:
        return True
    elif block.symbol == Sym.FALSE:
        return False
    elif block.symbol in variable_symbols:
        return block.var.get()
    elif block.symbol == Sym.RAND_BOOL:
        return random.choice([True, False])

def g_interpreter(block):
    if block.symbol == Sym.PASS:
        pass
    elif block.symbol == Sym.SEQ:
        for c in block.children:
            g_interpreter(c)
    elif block.symbol == Sym.GETS:
        g_interpreter(block.children[0])
    elif block.symbol == Sym.BOOL_BINDING:
        block.children[0].var.set(evaluate_bool(block.children[1]))
    elif block.symbol == Sym.INT_BINDING:
        block.children[0].var.set(evaluate_int(block.children[1]))
    elif block.symbol == Sym.IF_THEN_ELSE:
        if evaluate_bool(block.children[0]):
            g_interpreter(block.children[1])
        else:
            g_interpreter(block.children[2])
    elif block.symbol == Sym.WHILE:
        while evaluate_bool(block.children[0]):
            g_interpreter(block.children[1])
    else:
        pass 


# The combination of CFG and interpreter should "plug in" to the program class. Ideally the search process 
# with also work for an arbitrary CFG and interpreter. 

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
        #s = cand_s
    b = Block(s)
    for c in children:
        # the children of a block should be blocks
        b.children.append(random_block_search(g, p, c))
    if b.symbol in variable_symbols:
        b.var = random.choice(get_variable_options(p, b.symbol))
    return b

def function_search(g : CFG, p: Program, s : Sym = -1):
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

def main():
    p = Program(
        {int: [Box(int, "X")], bool : [] },
        {int : [Box(int, "Y")], bool : []},
    )
    for i in range(2):
        p.add_int_local()
    for i in range(2):
        p.add_bool_local()
    def test(x, y):
        p.wipe_all_variables()
        p.set_input(int, "X", x)
        run_for_time(p, g_interpreter, 1)
        return p.get_output(int, "Y") == y
    for i in range(1000):
        try:
            p.block = function_search(Generative, p)
            passed = True
            for x,y in [(3,9), (4,16), (5,25)]:
                if not test(x,y):
                    passed = False
                    break
            if passed:
                print("Successful candidate!")
                break
        except RecursionError:
            print("Maximum recursion depth exceeded...")
    print(g_to_str(p.block))

if __name__ == "__main__":
    main()
