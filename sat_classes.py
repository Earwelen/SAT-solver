# #######################################################################################
#     Sylvain Riondet
#         e0267895@u.nus.edu / sylvainriondet@gmail.com
#         2018/05/12
#         National University of Singapore / SoC / CS4244 Kknowledge Based Systems
#         Professor Kuldeep S. Meel
#         Project : SAT solver
# #######################################################################################


class Clause:
    """ List of terms in SAT """
    nb_clauses = 0

    def __init__(self, index, terms):
        self.index = index
        self.terms = terms


class Term:
    """ Term, with an id (x1, x2, ...) and a value (+1 or 0) """
    nb_terms = 0    # total nb of terms

    def __init__(self, x, val=None):
        self.x = x
        self.val = val
        Term.nb_terms += 1

    def __repr__(self):
        return f"Term x{self.x} = {self.val}"




