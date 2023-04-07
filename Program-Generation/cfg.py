# TODO: Concisely specify a CFG
class CFG:
    def __init__(self, start, rules):
        # Start symbol
        self.start = start
        # A dictionary of rules.
        # A symbol maps to a list of symbols with their children
        # in abstract syntax.
        self.rules = rules