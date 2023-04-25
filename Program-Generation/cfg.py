from typing import Dict, Any, Tuple, List
import math
import random
import numpy as np

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

def a_priori_masses(cfg : CFG):
    d = dict()
    a_priori_visit(cfg.start, cfg, d)
    return d
        

# This implementation assumes that there are only local cycles
def a_priori_visit(symbol : Any, cfg : CFG, masses : Dict[Any, float]):
    print(symbol)
    if symbol in masses.keys():
        print("Already computed")
        return masses[symbol]
    # bits per symbol
    # only nonterminals need to be represented
    #s = math.floor(math.log2(cfg.get_symbol_num()))+1
    terminal_count = cfg.get_symbol_num() - len(cfg.rules.keys())
    s = math.floor(math.log2(terminal_count))+1
    print(terminal_count)
    if not symbol in cfg.rules.keys():
        print("Terminal symbol")
        # This is a terminal symbol.
        # It is returned with probability 1,
        # and is length s,
        # so normalization is 2^(-s)
        masses[symbol] = 2.0**(-s)
        return masses[symbol] 
    else:
        N = np.poly1d([0])
        Ni = []
        print("Exploring each rule")
        for next_sym, children in cfg.rules[symbol]:
            if not children:
                print("Childless symbol " + next_sym.name)
                # We assume there is no self loop in this case,
                # because it would make the grammar ambiguous if
                # X -> X is a rule
                Ni.append(
                    np.poly1d(
                        [a_priori_visit(next_sym, cfg, masses)],
                    ),
                )
            else:
                print("Symbol with children " + next_sym.name)
                # If the derived symbol has attached children,
                # we need information about those children,
                # so we will calculate its normalization here.
                Ni.append(np.poly1d([1.0/2**s]))
                for c in children:
                    print("Child " + c.name)
                    if c == symbol:
                        # A self loop - the value of the normalization
                        # depends on itself since the symbol can derive
                        # itself.
                        Ni[-1] *= np.poly1d([1, 0])
                    else:
                        # This can only be relied on to avoid infinite
                        # recursion if there are no later loops back to
                        # symbol (only self cycles!)
                        # TODO: This currently leads to infinite recursion
                        # in Generative because for instance 
                        # INT_EXP -> INT_OP -> PLUS -> INT_EXP
                        Ni[-1] *= np.poly1d(
                            [a_priori_visit(c, cfg, masses)],
                        )
        N = sum(Ni)
        # Since N = p(N), the polynomial in N we've calculated,
        # The roots of p(N)-N = 0 are our candidate N values
        N_candidates = (N - np.poly1d([1, 0])).r
        print("Candidates for " + symbol.name + " normalization: " + str(N_candidates))
        root = -1
        for cand in N_candidates:
            if np.isreal(cand) and cand > 0:
                root = cand
                # Removing the break happens to make this find a valid solution
                # for Generative (I guess smaller roots are better?)
                #break
        # At this point if there is still no valid solution for root,
        # the universal a priori distribution has no PCFG.
        # However it is possible that only some roots can lead to 
        # global solutions (TODO)
        masses[symbol] = root
        # Go back and fill in the solution for N where it appears in
        # polynomial expressions for derivation normalizations
        for i, (next_sym, children) in enumerate(cfg.rules[symbol]):
            # Here we assume that the operators always occur
            # with the same number of arguments, so that we don't
            # need to maintain normalizations for every occurrence
            masses[next_sym] = Ni[i](root)
        return masses[symbol]

def cfg_to_solomonoff_pcfg(cfg: CFG):
    masses = a_priori_masses(cfg)
    print(masses)
    for k in masses.keys():
        if masses[k] < 0:
            print(k.name + " has a negative value!")
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