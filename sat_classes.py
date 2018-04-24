# #######################################################################################
#     Sylvain Riondet
#         e0267895@u.nus.edu / sylvainriondet@gmail.com
#         2018/05/12
#         National University of Singapore / SoC / CS4244 Kknowledge Based Systems
#         Professor Kuldeep S. Meel
#         Project : SAT solver
# #######################################################################################


class Formula:
    """ CNF Formula: list of clauses """

    def __init__(self):
        self.nb_terms = 0
        self.nb_clauses = 0
        self.clauses = []
        self.terms = []

    def create_terms(self):
        self.terms = [Term(x) for x in range(self.nb_terms)]

    def create_clauses(self):
        self.clauses = [Clause(x) for x in range(self.nb_clauses)]

    def __repr__(self):
        return f"Formula consists of the following list of clauses: \n" + "\n".join([str(c) for c in self.clauses])


class Clause:
    """ List of terms in SAT
        starting index at 1
        self.terms should be [{sign: +/-1, val:Term}, {}]
    """
    nb_clauses_count = 0

    def __init__(self, index):
        self.index = index
        self.terms = []
        self.nb_clauses_count += 1

    def __repr__(self):
        return f"* Clause {self.index + 1} with Terms: \n\t" + "\n\t".join([str(t) for t in self.terms])


class Term:
    """ Term, with an id (x1, x2, ...) and a sign (+1 or -1) """
    tot_nb_terms = 0    # total nb of terms
    nb_terms_count = 0
    values = []

    def __init__(self, x, sign=None):
        self.x = x
        self.sign = sign
        Term.tot_nb_terms += 1

    def __repr__(self):
        if self.sign == 1:
            return f"Term +{self.x}"
        elif self.sign == -1:
            return f"Term -{self.x}"
        else:
            return f"Term  {self.x}"




