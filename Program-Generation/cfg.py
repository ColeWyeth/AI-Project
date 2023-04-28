from typing import Dict, Any, Tuple, List
import math
import random
import numpy as np
import enum

# TODO: Concisely specify a CFG
class CFG:
    def __init__(self, start, rules : Dict[Any, Tuple[Any, List[Any]]]):
        # Start symbol
        self.start = start
        self.symbol_num = len(type(start))
        # A dictionary of rules.
        # A symbol maps to a list of symbols with their children
        # in abstract syntax.
        self.rules = rules
    def get_symbol_num(self):
        return self.symbol_num
    def get_symbols(self):
        return type(self.start)

class PCFG(CFG):
    def __init__(self, start, rules, probs):
        super().__init__(start, rules)
        self.probs = probs
    def sample_rule(self, symbol):
        if not symbol in self.rules.keys():
            return None
        else:
            return random.choices(
                self.rules[symbol],
                self.probs[symbol],
            )[0]
        
class Color(enum.Enum):
    WHITE = 0
    GRAY  = 1
    BLACK = 2
    ROOT  = 3

def solomonoff_masses(cfg : CFG, verbose=False):
    d = dict()
    for s in cfg.get_symbols():
        d[s] = [Color.WHITE, -1]
    solomonoff_visit(cfg.start, cfg, d, verbose)
    return d
        
def fill_downwards(symbol : Any, cfg : CFG, masses : Dict[Any, float], value : float):
    print("Filling " + symbol.name)
    print(masses[symbol])
    if not type(masses[symbol][1]) == np.poly1d:
        # We have reached the bottom of the path that needs to be filled
        return
    if masses[symbol][1].order == 0:
        # This is effectively a type cast
        masses[symbol][1] = masses[symbol][1][value]
        # We have reached the bottom of the path that needs to be filled
        return
    masses[symbol][1] = masses[symbol][1](value)
    if not symbol in cfg.rules.keys():
        return
    for next_sym, children in cfg.rules[symbol]:
        fill_downwards(next_sym, cfg, masses, value)
        for c in children:
            fill_downwards(c, cfg, masses, value)

# This implementation assumes that there are only local cycles
def solomonoff_visit(symbol : Any, cfg : CFG, masses : Dict[Any, float], verbose=False):
    if verbose:
        print(symbol)
    if masses[symbol][0] == Color.BLACK:
        if verbose:
            print("Already computed")
        return masses[symbol][1]
    # bits per symbol
    # only nonterminals need to be represented
    terminal_count = cfg.get_symbol_num() - len(cfg.rules.keys())
    s = math.floor(math.log2(terminal_count))+1
    if verbose:
        print(terminal_count)
    if not symbol in cfg.rules.keys():
        print("Terminal symbol")
        # This is a terminal symbol.
        # It is returned with probability 1,
        # and is length s,
        # so normalization is 2^(-s)
        masses[symbol] = [Color.BLACK, 2.0**(-s)]
        return masses[symbol][1]
    else:
        masses[symbol][0] = Color.GRAY
        N = np.poly1d([0])
        if verbose:
            print("Exploring each rule")
        for next_sym, children in cfg.rules[symbol]:
            if not children:
                if verbose:
                    print("Childless symbol " + next_sym.name)
                # We assume there is no self loop in this case,
                # because it would make the grammar ambiguous if
                # X -> X is a rule
                if not masses[next_sym][0] == Color.GRAY or masses[next_sym][0] == Color.ROOT:
                    N += solomonoff_visit(next_sym, cfg, masses, verbose)
                else:
                    # Back edge encountered. Will fill variable during a
                    # downward pass from up the recursion stack.
                    masses[next_sym][0] = Color.ROOT
                    N += np.poly1d([1,0])
                    if verbose:
                        print("Back edge to " + next_sym.name)
            else:
                if verbose:
                    print("Symbol with children " + next_sym.name)
                # If the derived symbol has attached children,
                # we need information about those children,
                # so we will calculate its normalization here.
                # Unrelated to operator norm in analysis
                op_norm = np.poly1d([1.0/2**s])
                for c in children:
                    if verbose:
                        print("Child " + c.name)
                    if masses[c][0] == Color.GRAY or masses[c][0] == Color.ROOT:
                        masses[c][0] = Color.ROOT
                        # Back edge encountered. Will fill variable during a
                        # downward pass from up the recursion stack.
                        op_norm *= np.poly1d([1, 0])
                    else:
                        # TODO: This currently leads to infinite recursion
                        # in Generative because for instance 
                        # INT_EXP -> INT_OP -> PLUS -> INT_EXP
                        op_norm *= solomonoff_visit(c, cfg, masses, verbose)
                masses[next_sym] = [Color.BLACK, op_norm]
                N += op_norm

        # This function assumes that all cycles are disjoint,
        # except possibly for a loop at the root. 
        # So if we have encountered a self loop, we should solve the resulting
        # quadratic here.
        if masses[symbol][0] == Color.ROOT:
            # Since N = p(N), the polynomial in N we've calculated,
            # The roots of p(N)-N = 0 are our candidate N values
            N_candidates = (N - np.poly1d([1, 0])).r
            if verbose:
                print("Candidates for " + symbol.name + " normalization: " + str(N_candidates))
            root = -1
            for cand in reversed(N_candidates):
                if np.isreal(cand) and cand > 0:
                    root = cand
                    break # Any overal solution uses the smallest roots in [0,1]
            # At this point if there is still no valid solution for root,
            # the universal a priori distribution has no PCFG.
            # However it is possible that only some roots can lead to 
            # global solutions (TODO)
            masses[symbol][1] = root
            # Go back and fill in the solution for N where it appears in
            # polynomial expressions for derivation normalizations
            for next_sym, children in cfg.rules[symbol]:
                fill_downwards(next_sym, cfg, masses, root)
                for c in children:
                    fill_downwards(c, cfg, masses, root)
        else:
            # N is either a polynomial we don't yet need to solve
            # or properly computed normalization.
            if type(N) == np.poly1d and N.order == 0:
                N = N[0]
            masses[symbol][1] = N
        masses[symbol][0] = Color.BLACK
            
        #for i, (next_sym, children) in enumerate(cfg.rules[symbol]):
            # Here we assume that the operators always occur
            # with the same number of arguments, so that we don't
            # need to maintain normalizations for every occurrence
            # masses[next_sym] = Ni[i](root)
        return masses[symbol][1]

def cfg_to_solomonoff_pcfg(cfg: CFG, verbose=False):
    """
    This function converts a cfg to a pcfg which generatives TM descriptions <T>
    according to probability proportional to 2^(-l(<T>)).
    This does not necessarily mean that programs p = <T,x> are generated with
    probability proportional to 2^(-l(p)), since the semantics of inputs are
    ignored, so is not identical to sampling from the universal a priori distribution.
    """
    masses = solomonoff_masses(cfg, verbose)
    # Everything should now be BLACK so drop color tags
    for k in masses.keys():
        masses[k] = masses[k][1]
        if type(masses[k]) == np.poly1d and masses[k].order == 0:
            masses[k] = masses[k][0]
    if verbose:
        print(masses)
    for k in masses.keys():
        if masses[k] < 0:
            raise Exception(k.name + " has a negative value!")
    rule_probs = dict()
    for s in masses.keys():
        if s in cfg.rules.keys():
            rule_probs[s] = [masses[desc]/masses[s] for desc, _ in cfg.rules[s]]
        else:
            # This number shouldn't actually be checked
            # I am not sure if 1 is the right thing to have here
            # for when that error is made TODO
            rule_probs[s] = 1
    return PCFG(cfg.start, cfg.rules, rule_probs)