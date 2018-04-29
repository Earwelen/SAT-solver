# #######################################################################################
#     Sylvain Riondet
#         e0267895@u.nus.edu / sylvainriondet@gmail.com
#         2018/05/12
#         National University of Singapore / SoC / CS4244 Kknowledge Based Systems
#         Professor Kuldeep S. Meel
#         Project : SAT solver
# #######################################################################################

# Classes for SAT solver. A Formula consists of Clauses, which themselves consist of Terms
from ui import tracer

TRACE_LVL = 2


class Formula:
    """ CNF Formula: list of clauses """
    terms_values = {}

    def __init__(self):
        self.nb_terms = 0
        self.nb_clauses = 0
        self.clauses = []
        self.terms = []
        self.solved = None

    def create_terms(self):
        self.terms = [Term(x) for x in range(1, self.nb_terms + 1)]

    def create_clauses(self):
        self.clauses = [Clause(x) for x in range(self.nb_clauses)]

    def satisfiable(self):
        clauses_satis = [x.satisfiable() for x in self.clauses]
        if False in clauses_satis:
            self.solved = False
        elif None in clauses_satis:
            self.solved = None
        else:
            tracer(f"Assume that if there's no False nor None in our formula, we only have True", TRACE_LVL, 4)
            tracer(f"So the clause are satisfiable? Here: {clauses_satis}", TRACE_LVL, 4)
            self.solved = True
        return self.solved

    def find_unique_terms(self):
        """
        Find the literals that have enough constrains to take a value.
        :return: List of x: True/False that are implied by the value of other literals
        """
        literals = []
        for clause in self.clauses:
            found_x = clause.unique_term()
            if found_x is not None:
                literals.append(found_x)
        if len(literals) >= 1:
            return literals
        else:
            return None

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
        """
        A Clause consists of Terms, stored in self.terms
        the masks enable to mask the terms that are already evaluating to true.
        if the whole Clause is satisfiable, the self.satisfied == True
        """
        self.index = Clause.nb_clauses_count
        self.terms = []
        self.literals_values = []
        self.satisfied = None
        self.nb_terms = None
        Clause.nb_clauses_count += 1

    def append_term(self, to_append):
        """ To have same number of terms and masks """
        self.terms.append(to_append)
        self.literals_values.append(None)
        self.nb_terms = len(self.terms)

    def satisfiable(self):
        """
        It is satisfiable if at least one Term is True
        self.literals_values compute the evaluation of each term, True / False or None if no value yet
        """
        self.literals_values = [x.assigned_val() for x in self.terms]
        if True in self.literals_values:
            clause_sat = True
        elif None in self.literals_values:
            clause_sat = None
        else:
            clause_sat = False
        self.satisfied = clause_sat

        tracer(f"Clause {str(self.index)} evaluates to {clause_sat}, details: {self.literals_values}, "
               f"{[x.short_str() for x in self.terms]}", TRACE_LVL, 4)
        return clause_sat

    def unique_term(self):
        """
        If there an unique term that is undefined, all others are False,
        only one value is possible to satisfy the Clause

        :return: TRue/False/None Return the only value that can be assigned to that x
        """
        if self.satisfied is None and self.literals_values.count(None) == 1:
            # so there is only one Term that is None, all others are False
            i_unique = self.literals_values.index(None)
            u_term = self.terms[i_unique]
            if u_term.neg is True:
                return {'x': u_term.x, 'val': True}
            else:
                return {'x': u_term.x, 'val': False}
        return None

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
        if x not in Term.values.keys():
            Term.tot_nb_terms += 1
        Term.values[x] = None
        self.x = x
        self.neg = neg
        self.val = Term.values[x]
        # todo: this previous assignment is not a pointer.  Therefore the value is stored and not updated

    def count_unassigned():
        unassigned_terms = 0
        for k in Term.values.keys():
            if Term.values[k] is None: unassigned_terms += 1
        return unassigned_terms

    def reassign_val(self):
        self.val = Term.values[self.x]

    def assigned_val(self):
        """ Compute the value when required, neg * val """
        # assert self.val is not None, f"One Term doesn't have any value: x{self.x}={self.val}"
        tracer(f"{str(self)}, neg={self.neg} val={self.val}", TRACE_LVL, 6)

        # make use of Python True==1 and False ==0, to apply the negation easily
        if self.val is None:    return None
        else:                   return self.neg == self.val

    def short_str(self):
        if self.neg == False:   return f"-x{self.x}"
        else:                   return f" x{self.x}"

    def __repr__(self):
        return f"Term {self.short_str()}, val={self.val}"


class Solutions:
    """
    DEPRECATED : using numpy instead

    Holds a set of solutions, the values of the terms.
    Used for the guess, trying random values

    self.satis: is this set of terms leading to a solutions or not
    self.chosen: terms that have been decided
    self.implied: terms which values are induced by the previous choices.
    self.values: combine both
    """

    def __init__(self, initial_values):
        """
        :param initial_values: should be the values that are constrained by the formula, without any guess \
                                same structure as Term.values = [{index: True/False/None} for all indexes]

        self.satis: is this set of terms leading to a solutions or not
        self.chosen: terms that have been decided
        self.implied: terms which values are induced by the previous choices.
        self.values: combine both
        """
        self.satis = None
        self.initial = initial_values
        self.chosen = {k: None for k in initial_values.keys()}
        self.implied = {k: None for k in initial_values.keys()}
        self.values = {}
        self.update_values()

    def update_values(self):
        for key in self.values.keys():
            chosen_k = self.chosen[key]
            implied_k = self.implied[key]
            initial = self.initial[key]

            # ensure that no contradiction exists
            assert not(True in (chosen_k, implied_k, initial) and False in (chosen_k, implied_k, initial)), \
                "Contradiction in chosen and implied terms values"

            # Then just take the value from any dic. None is the default if no value in any variable.
            self.values[key] = chosen_k or implied_k or initial



















