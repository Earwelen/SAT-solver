# #######################################################################################
#     Sylvain Riondet
#         e0267895@u.nus.edu / sylvainriondet@gmail.com
#         2018/05/12
#         National University of Singapore / SoC / CS4244 Knowledge Based Systems
#         Professor Kuldeep S. Meel
#         Project : SAT solver
# #######################################################################################

# #######################################################################################
# todo TODO List
# todo brut force search
# todo check output
# todo do the sat solver
# todo general variable with values of terms, easy to change for all. In Formula or in Term class ?
#
# call prog with => python sat_solver.py "cnf_formulas/cnf-1.cnf"
#
# #######################################################################################
# ########################      Example of CNF Formula      #############################
# p cnf 3 2
# 1 -3 0
# 2 3 -1 0
# #######################################################################################

# #######################################################################################
# imports
import argparse
import os
from ui import tracer
from sat_classes import Term, Clause, Formula


# #######################################################################################
# Variables & constants
TRACE_LVL = 2

# formula Object with a list of Clauses composed of Terms
formula = Formula()
# Solutions.    Dimension 0: choice iteration nb,
#               Dim 1: 0-Choice/1-Implied/2-Final values,
#               Dim 2: [formula.solved] + x[1..n]
# todo This list of list of list will grow exponential. Might need to find a better solution here
sol = [[[]]]
depth_n = 1


# #######################################################################################
# #############################      parsing file      ##################################
def text_parse_to_formula(text_file):
    """ Parse .cnf file into terms and clauses """
    with open(text_file) as f:
        for line in f:
            if len(line) <= 1: continue
            striped_line = line.strip()

            # file name and empty line
            if striped_line[0] == 'c':
                tracer("don't care: " + striped_line, TRACE_LVL, 4)

            # "p cnf <nb of terms> <nb of clauses>
            elif striped_line[0] == 'p':
                index = 0
                for part in striped_line.split(" "):
                    if part.isdigit():
                        if index == 0:
                            formula.nb_terms = int(part)
                            formula.create_terms()
                            tracer(f"formula should have {formula.nb_terms} different terms", TRACE_LVL, 4)
                            tracer(formula.terms, TRACE_LVL, 7)
                            index += 1
                        elif index == 1:
                            formula.nb_clauses = int(part)
                            tracer(f"formula should have {formula.nb_clauses} clauses", TRACE_LVL, 4)
                            index += 1
                        else:
                            tracer("Error, there is a third number in the cnf file", TRACE_LVL, 0, m_type="error")

            # Real clause. Decompose it
            elif striped_line.split()[0].lstrip("-").isdigit():
                # have each int
                int_list = [int(x) for x in striped_line.split(" ")]
                if int_list[-1] == 0:
                    int_list = int_list[:-1]        # drop last '0'
                else:
                    tracer("No '0' found at the end, error", TRACE_LVL, 1, m_type="error")

                # now create each Term and pass into a clause
                clause = Clause()
                for x in int_list:
                    clause.append_term(Term(abs(x), True if x >= 0 else False))
                formula.clauses.append(clause)

            else:
                tracer(f"Hmmm {striped_line} was not recognized: {striped_line[0]}", TRACE_LVL, 1, m_type="warning")


# #######################################################################################
# #################      Recursive checking of satisfiability     #######################
def recursive_sat_check():
    """
    Recursively check if the formula is satisfiable, and auto assign terms that only have one possibility
    :return: Returns if the formula is satisfiable: True/False/None
    """

    implied_x = True
    iteration = 0

    while implied_x is not None:
        # todo might need to move the solution from Term.values to another variable

        unassigned_terms = Term.count_unassigned()
        tracer(f"=> Iteration {iteration}: Still {unassigned_terms} undefined out of {formula.nb_terms}", TRACE_LVL, 1)

        formula.reassign_terms_val()
        formula.satisfiable()       # recheck all the clauses satisfiability

        implied_x = formula.find_unique_terms()
        if implied_x is None: break
        # else:
        tracer(f"Found Term {implied_x} that has an unique possible value \n", TRACE_LVL, 2)
        for k_v in implied_x:
            Term.values[k_v['x']] = k_v['val']
            # todo add to implied_list as well

        iteration += 1

    return formula.solved


# #######################################################################################
# #################            choose a value to fix            #########################
def choose_term(depth_i):
    """

    :return:
    """
    values_proposition = sol[depth_i - 1][2]
    while values_proposition in sol[:][2]:

        values_proposition.index(None)
    x_index = 0
    return x_index


# #######################################################################################
# #################      recursively choose values of terms     #########################
def rec_try_values(n, i_explored):
    """
    choose a value of an unconstrained term and check satisfiability of the formula.
    if still neither True or False, recursively choose more terms
    """
    tracer(f"Iteration {depth_n}. Making a guess", TRACE_LVL, 0)

    for x in range():
        pass

    no_new_solution = False
    if no_new_solution:
        return
    else:
        print(f"potato {depth_n}")
        depth_n += 1

    # Choose a None term

    # Assign it

    # Recompute satisfiability
    formula.satisfiable()
    # Go deeper in choices
    if formula.solved is None:
        rec_try_values()
    else:
        add_solution()


# #######################################################################################
# #############################      main function     ##################################
def solver():
    """ Main function to solve the SAT pb. Most of the computation is into the objects """
    tracer(formula, TRACE_LVL, 1)

    # TEMPORARY Testing
    # 1 -3 0
    # 2 3 -1 0
    # values = {1: True, 2: False, 3: False}
    # Term.values = values

    # todo Simplify formula by identifying almost duplicates clauses

    # todo recursive checking of possibilities
    # todo find multiple solutions
    # todo eliminate possibilities already stuck in

    # todo create current_choice
    # todo create choices_good, choices_bad
    # todo still_unexplored_solutions()?
    # todo make_choice()
    # todo if formula == True / False / None => decide
    # todo while loop

    # todo if need deep recursion
    if False:
        import sys
        sys.setrecursionlimit(5000)

    if False:
        for x in Term.values:
            for tf in (True, False):
                for again in Term.values:
                    print("until idk")

    # Initial check for obvious solutions
    recursive_sat_check()
    # initial_terms = [formula.solved] + Term.values
    # sol[0] hold the initial values, those that can't be changed (too constrained)
    # sol.append([initial_terms, initial_terms, initial_terms])

    # rec_try_values()
    print(Term.tot_nb_terms)

    # End of the Solver
    tracer(f"\nTerms = {Term.values}", TRACE_LVL, 1)
    tracer(f"\nThe formula is satisfiable: {formula.solved}", TRACE_LVL, 0)
    tracer("\nEnd of main function\n", TRACE_LVL, 1)


# ########################################################################################
# ##############################    Checking of args    ##################################
def is_valid_file(parser, file_path):
    if not os.path.isfile(file_path) and (file_path.endswith(".cnf") or file_path.endswith(".txt")):
        parser.error(f'\n The file {file_path} does not exist or the extension is wrong(.cnf/.txt)!')
    else:
        # File exists so return the filename
        return file_path


# ########################################################################################
# ###########################      main call, cmd line     ###############################
if __name__ == '__main__':

    # Arguments for inline commands : https://docs.python.org/3/howto/argparse.html#id1
    cmd = argparse.ArgumentParser(
        "\n"
        "  Coded by Sylvain Riondet, @NUS/SoC \n"
        "  e0267895@u.nus.edu / sylvainriondet@gmail.com \n"
        "  Course: CS4244 - Knowledge-Based Systems\n"
        "  Submission for 2018/05/12 \n"
        "\n")
    cmd.add_argument("input_file", help="File with cnf formula",
                     type=lambda x: is_valid_file(cmd, x))  # type=lambda x: fonction_call(cmd, x))
    cmd.add_argument("-p", "--profiler", help="Activate the profiler", action='store_true', default=False)
    args = cmd.parse_args()

    # Parse the text file to formula
    print("Hello, lets start ! Welcome to my SAT solver ! ... Sylvain")
    text_parse_to_formula(args.input_file)

    #
    # #######################################################################################
    if args.profiler:
        # Checking processor time with cProfile lib#
        try:
            import cProfile
            import pstats
            cProfile.run("solver()", "cProfileStats")
            stats = pstats.Stats("cProfileStats")
            # Sort the stats and print the 10 first rows
            stats.sort_stats("tottime")
            stats.print_stats(10)
        except:
            print("** Crashed, nothing saved ** \n"
                  "* Try without the profiler to have more details *")
        finally:
            os.remove("cProfileStats")

    else:
        solver()

    # End
    print("Bye bye see you next time ! \n")


















