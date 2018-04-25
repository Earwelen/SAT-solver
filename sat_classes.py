# #######################################################################################
#     Sylvain Riondet
#         e0267895@u.nus.edu / sylvainriondet@gmail.com
#         2018/05/12
#         National University of Singapore / SoC / CS4244 Kknowledge Based Systems
#         Professor Kuldeep S. Meel
#         Project : SAT solver
# #######################################################################################

# Classes for SAT solver. A Formula consists of Clauses, which themselves consist of Terms
from operator import mul
from functools import reduce
from ui import tracer

TRACE_LVL = 6


def prod(iterable):
    """ Return the product of all terms like sum() """
    return reduce(mul, iterable, 1)


class Formula:
    """ CNF Formula: list of clauses """
    terms_values = {}

    def __init__(self):
        self.nb_terms = 0
        self.nb_clauses = 0
        self.clauses = []
        self.terms = []

    def create_terms(self):
        self.terms = [Term(x) for x in range(1, self.nb_terms + 1)]

    def create_clauses(self):
        self.clauses = [Clause(x) for x in range(self.nb_clauses)]

    def satisfiable(self):
        return prod([x.satisfiable() for x in self.clauses])

    def reassign_terms_val(self):
        for clause in self.clauses:
            for term in clause.terms:
                term.reassign_val()

    def __repr__(self):
        return f"Formula consists of the following list of clauses: \n" + "\n".join([str(c) for c in self.clauses])


class Clause:
    """ List of terms in SAT
        starting index at 1
        self.terms should be [{sign: +/-1, val:Term}, {}]
    """
    nb_clauses_count = 0

    def __init__(self, ):
        self.index = Clause.nb_clauses_count
        self.terms = []
        Clause.nb_clauses_count += 1

    def satisfiable(self):
        """ It is satisfiable if at least one Term is True """
        is_satis = [x.assigned_val() for x in self.terms]
        clause_sat = sum(is_satis) >= 1
        tracer(f"Clause {str(self.index)} evaluates to  {clause_sat}, details: {is_satis}", TRACE_LVL, 3)
        return clause_sat

    def __repr__(self):
        return f"* Clause {self.index + 1} with Terms: \t(" + "\tv\t".join([t.short_str() for t in self.terms]) + ")"


class Term:
    """ Term, with an id (x1, x2, ...), neg T/F, and a value 0 or 1 """
    tot_nb_terms = 0    # total nb of terms
    nb_terms_count = 0
    values = {}

    def __init__(self, x, neg=True):
        """
        Create a Term
        :param x: x1, x2, x3 : id of the term
        :param neg: !! True if positive, False if need negation !!
        """
        Term.values[x] = None
        self.x = x
        self.neg = neg
        self.val = Term.values[x]
        Term.tot_nb_terms += 1

    def reassign_val(self):
        self.val = Term.values[self.x]

    def assigned_val(self):
        """ Compute the value when required, neg * val """
        assert self.val is not None, f"One Term doesn't have any value: x{self.x}={self.val}"
        # make use of Python True==1 and False ==0, to apply the negation easily
        tracer(f"Term: {str(self)}, neg={self.neg} val={self.val}", TRACE_LVL, 6)
        return self.neg == self.val

    def short_str(self):
        if self.neg == False:   return f"-x{self.x}"
        else:                   return f"x{self.x}"

    def __repr__(self):
        return f"Term {self.short_str()}, val={self.val}"




