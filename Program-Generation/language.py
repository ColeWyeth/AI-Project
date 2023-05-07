from cfg import CFG
from program import Block, Program
import typing
import random

class Language:
    def __init__(
        self,
        cfg : CFG,
        variable_symbols,
        variable_semantics,
        interpreter,
        syntactic_sugar = None,
    ):
        self.cfg = cfg
        self.variable_symbols = variable_symbols
        self.variable_semantics = variable_semantics
        self.interpreter = interpreter
        self.sugar = syntactic_sugar
    def get_cfg(self):
        return self.cfg
    def get_variable_symbols(self):
        return self.variable_symbols
    def get_variable_options(self, program, symbol):
        return self.variable_semantics(program, symbol)
    def bind_semantics(self, p : Program, b : Block):
        if b.symbol in self.get_variable_symbols():
            b.var = random.choice(self.get_variable_options(p, b.symbol))
        for c in b.children:
            self.bind_semantics(p, c)
    def interpret(self, block):
        return self.interpreter(block)
    def print_block(self, block):
        print(Block.rec_block_printer(block, self.sugar))