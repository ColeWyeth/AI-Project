from typing import Dict, List
# from generative_language import Sym

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
    def __init__(self, t : type, name : str ="NONAME", val=None):
        if val==None:
            self.val = t()
        else:
            self.val = val
        self.name = name
    def get_name(self):
        return self.name
    def get(self):
        return val
    def set(self, val):
        self.val = val


# A block is a partially constructed program module
class Block:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []
        self.var = None
    def rec_block_printer(block, sugar = None):
        child_str = ""
        if block.children:
            child_str = '('
            for c in block.children:
                child_str += Block.rec_block_printer(c,sugar) + ','
            child_str += ')'
        result = block.symbol.name + child_str
        if sugar:
            return sugar(block, result)
        return result
    def __repr__(self):
        return Block.rec_block_printer(self)
        # if self.symbol == Sym.LOCAL_BOOL or self.symbol == Sym.LOCAL_INT:
        #     return self.var.get_name()
        # child_str = ""
        # if self.children:
        #     child_str = '('
        #     for c in self.children:
        #         child_str += str(c) + ','
        #     child_str += ')'
        # return self.symbol.name + child_str
    
# TODO: Blocks with pointers should be the only actual construct outside of the CFG definition.
# They will carry a symbol and sometimes indexing information for locals and windows, as well as
# an (often empty) list of child blocks. 

# A program manages an environment, input and output memory locations
# (which may be anytime modifiable and readable) and a block.
# Searching over blocks is best handled externally to the program class; 
# a reference to program will be required by the search algorithm 
# for access to the relevant ins and outs and to set the block attribute.
class Program:
    def __init__(self, ins: Dict[type, List[Window]], outs: Dict[type, List[Window]]):
        self.ins = ins
        self.outs = outs
        # This is a bit of a kludge - I want (syntactically correct) programs to execute
        # even if their semantics is broken because there are no windows of the right type.
        # These are effectively similar to extra locals with restricted read/write
        # TODO: Fix this better
        if not self.ins[bool]:
            self.ins[bool].append(Box(bool, "NOBOOLS"))
        if not self.outs[bool]:
            self.outs[bool].append(Box(bool, "NOBOOLS"))
        if not self.ins[int]:
            self.ins[int].append(Box(int, "NOINTS"))
        if not self.outs[int]:
            self.outs[int].append(Box(int, "NOINTS"))
        self.block = None
        self.int_locals = []
        self.bool_locals = []

    def get_block(self):
        return self.block

    def execute(self):
        self.block.run()

    def add_int_local(self):
        self.int_locals.append(
            Box(int, "Li" + str(len(self.int_locals))),
        )

    def add_bool_local(self):
        self.bool_locals.append(
            Box(bool, "Lb" + str(len(self.bool_locals))),
        )