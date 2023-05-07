import enum
import random

from program import Block
from cfg import CFG

from language import Language

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
    #NEXT_BIT        = 24

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

Arithmetic_Rules = {
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
        # (Sym.AND, [Sym.BOOL_EXP, Sym.BOOL_EXP]),
        # (Sym.OR, [Sym.BOOL_EXP, Sym.BOOL_EXP]),
        # (Sym.NEG_BOOL, [Sym.BOOL_EXP]),
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
        # (Sym.PLUS, [Sym.INT_EXP, Sym.INT_EXP]),
        # (Sym.MULT, [Sym.INT_EXP, Sym.INT_EXP]),
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

Arithmetic = CFG(Sym.EXEC, Arithmetic_Rules)

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

def a_sugar(block, abstract_syntax):
    if block.symbol in variable_symbols:
        return block.var.get_name()
    return abstract_syntax
    
def a_to_str(block):
    return Block.rec_block_printer(block, a_sugar)


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

def a_interpreter(block):
    if block.symbol == Sym.PASS:
        pass
    elif block.symbol == Sym.SEQ:
        for c in block.children:
            a_interpreter(c)
    elif block.symbol == Sym.GETS:
        a_interpreter(block.children[0])
    elif block.symbol == Sym.BOOL_BINDING:
        block.children[0].var.set(evaluate_bool(block.children[1]))
    elif block.symbol == Sym.INT_BINDING:
        block.children[0].var.set(evaluate_int(block.children[1]))
    elif block.symbol == Sym.IF_THEN_ELSE:
        if evaluate_bool(block.children[0]):
            a_interpreter(block.children[1])
        else:
            a_interpreter(block.children[2])
    elif block.symbol == Sym.WHILE:
        while evaluate_bool(block.children[0]):
            a_interpreter(block.children[1])
    else:
        pass 

Arithmetic_Language = Language(
    Arithmetic,
    variable_symbols,
    get_variable_options,
    a_interpreter,
    a_sugar,
)