from threading import Thread
from time import sleep
from multiprocessing import Process, Manager
from typing import Dict, List
import enum
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
        self.type = t
    def get_name(self):
        return self.name
    def get(self):
        return self.val
    def set(self, val):
        self.val = val


# A block is a partially constructed program module
class Block:
    def __init__(self, symbol, children = None):
        self.symbol = symbol
        if children is None:
            self.children = []
        else:
            self.children = children
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
    def length(self):
        return 1 + sum([c.length() for c in self.children])
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

class Status(enum.Enum):
    NOTSTARTED = 0
    RUNNING    = 1
    STOPPED    = 2
    FINISHED   = 3

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
        # if not self.ins[bool]:
        #     self.ins[bool].append(Box(bool, "NOBOOLS"))
        # if not self.outs[bool]:
        #     self.outs[bool].append(Box(bool, "NOBOOLS"))
        # if not self.ins[int]:
        #     self.ins[int].append(Box(int, "NOINTS"))
        # if not self.outs[int]:
        #     self.outs[int].append(Box(int, "NOINTS"))
        self.NO_BOOLS = Box(bool, "NOBOOLS")
        self.NO_INTS = Box(int, "NOINTS")
        self.block = None
        self.int_locals = []
        self.bool_locals = []
        self.status = Status.NOTSTARTED

    def get_block(self):
        return self.block

    def add_int_local(self):
        self.int_locals.append(
            Box(int, "Li" + str(len(self.int_locals))),
        )

    def add_bool_local(self):
        self.bool_locals.append(
            Box(bool, "Lb" + str(len(self.bool_locals))),
        )

    def get_all_locals(self):
        return self.int_locals + self.bool_locals
    
    def get_all_windows(self):
        return self.ins[int] + self.ins[bool] + self.outs[int] + self.outs[bool] 
    
    def get_all_variables(self):
        return self.get_all_locals() + self.get_all_windows() + [self.NO_BOOLS] + [self.NO_INTS]
    
    def wipe_all_variables(self):
        vars = self.get_all_variables()
        for v in vars:
            v.set(v.type())

    def set_input(self, t : type, name : str, val):
        for x in self.ins[t]:
            if x.name == name:
                x.set(val)
                return
        raise Exception("Variable not found")

    def get_output(self, t : type, name : str):
        for y in self.outs[t]:
            if y.name == name:
                return y.get()
        raise Exception("Variable not found")


# Blocking, run program for some maximum time
def run_for_time(p : Program, interpreter, timeout : int):
    manager = Manager()
    return_dict = manager.dict()
    def task(return_dict):
        p.status = Status.RUNNING
        interpreter(p.block)
        try:
            return_dict["outputs"] = p.outs
        except RecursionError:
            print("Caught pickling error")
            p.status = Status.STOPPED
    process = Process(target=task, args=(return_dict,))
    #print("Starting process")
    process.start()
    process.join(timeout)
    sleep(0.01)
    if process.is_alive():
        print("Runtime limit exceeded, force terminating process")
        process.terminate()
        p.status = Status.STOPPED
    else:
        # Copy over return values from the process
        for t in [int, bool]:
            for i, y in enumerate(return_dict["outputs"][t]):
                p.outs[t][i].set(y.get()) 
        p.status = Status.FINISHED
