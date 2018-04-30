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
import pandas as pd
from collections import OrderedDict
from pprint import pprint
from ui import tracer
from sat_classes import Term, Clause, Formula, set_tracing_lvl


# #######################################################################################
# Variables & constants
TRACE_LVL = 1

# formula Object with a list of Clauses composed of Terms
formula = Formula()
# Solutions.    Dimension 0: choice iteration nb,
#               Dim 1: [formula.solved] + x[1..n]
# todo This list of list of list will grow exponential. Might need to find a better solution here
sol = pd.DataFrame()    # TOOOOO BIG
"""
Sol Structure :

"""
explored = []
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
                int_list = [int(x) for x in striped_line.split()]
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
        tracer(f"satisfiability check iteration {iteration}: "
               f"Still {unassigned_terms} undefined out of {formula.nb_terms}", TRACE_LVL, 3)

        formula.satisfiable()       # recheck all the clauses satisfiability
        implied_x = formula.find_unique_terms()

        if implied_x is None:
            break

        # else:
        tracer(f"Found Term {implied_x} that has an unique possible value", TRACE_LVL, 3)
        for k_v in implied_x:
            Term.values[k_v['x']] = k_v['val']
            # todo add to implied_list as well

        formula.satisfiable()       # recheck all the clauses satisfiability
        tracer(f"Formula satisfiable: {formula.solved}. These values were updated: "
               f"{implied_x}", TRACE_LVL, 2)

        iteration += 1

    return implied_x


# #######################################################################################
# #################      check if set of values in solutions       ######################
def check_is_in_solutions():
    """
    Check if a set of values has already been checked by the sat solver.
    Look into the pandas solutions DataFrame
    :return:
    """
    # todo search if any row has the same True / False, don't care about None values
    # todo: might need that for save_solutions_pd to avoid duplicates

    assigned_terms = {f"x{k}": Term.values[k] for k in Term.values.keys() if Term.values[k] is not None}

    tracer(f"Current set of solutions", TRACE_LVL, 5)
    tracer(sol, TRACE_LVL, 5)
    query = " and ".join([f"{k} == {assigned_terms[k]}" for k in assigned_terms.keys()])
    tracer("Query is: " + query, TRACE_LVL, 7)

    queried = sol.query(query)
    tracer(queried, TRACE_LVL, 7)
    nb_occurrences = len(queried)

    tracer(f"This set of literals appears {nb_occurrences} times in the solutions", TRACE_LVL, 6)

    return True if nb_occurrences > 0 else False


# #######################################################################################
# #################      find all combinations of terms/values     ######################
def save_solution_pd():
    """
    Save (append) the solution into pandas DataFrame
    """
    global sol

    new_solution = OrderedDict({'solved': formula.solved})
    for k in Term.values.keys():
        new_solution[f"x{k}"] = Term.values[k]
    new_solution['nb_of_combinations'] = 2**Term.count_unassigned()
    sol = sol.append(new_solution, ignore_index=True)

    tracer(f"Appended solution {new_solution}", TRACE_LVL, 7)


# #######################################################################################
# #################      recursively choose values of terms     #########################
def rec_try_values(i_explored):
    """
    choose a value of an unconstrained term and check satisfiability of the formula.
    if still neither True or False, recursively choose more terms
    call function to save the computed values
    try to not recheck what has already been checked
    """
    global depth_n
    # tracer(f"=> Depth {depth_n}. Making a guess, i_explored={i_explored}", TRACE_LVL, 0)

    for x in Term.values.keys():
        # Save previous values to reset to previous state at the end
        previous_values = Term.values.copy()
        formula.reassign_terms_val()

        # Value already assigned, guess no need. Maybe need to record somehow ?
        if Term.values[x] is not None:
            tracer(f"Term x[{x}]={Term.values[x]}, continuing", TRACE_LVL, 6)
            continue
        # this x has already been decided in another previous loop
        if x in i_explored:
            continue

        tracer("="*(depth_n-1) + f"=> Depth {depth_n},\t x{x}. {len(sol)-1} solutions so far (True and False)", TRACE_LVL, 0)

        for true_false in (True, False):
            Term.values[x] = true_false
            formula.reassign_terms_val()
            tracer(f"Choosing x{x}={true_false}. Term.values = {Term.values}", TRACE_LVL, 1)

            # Check that we didn't already search this set of values
            already_checked = check_is_in_solutions()
            if already_checked:
                tracer(f"**** Has already been tried in previous loops {Term.values}", TRACE_LVL, 5)
                continue

            # Then alright, let's apply it
            implied_x = recursive_sat_check()
            if formula.solved in (True, False):
                tracer(f"*Solved={formula.solved}* -> adding solution n{len(sol)} if not redundant: "
                       f"Term.values = {Term.values}", TRACE_LVL, 2)
                # Add the solution to the global variable
                save_solution_pd()
            else:
                depth_n += 1
                tracer(f"Not Solved. Let's go to depth_n={depth_n}. Term.values = {Term.values}", TRACE_LVL, 3)
                rec_try_values([x] + i_explored)
                depth_n -= 1
                tracer(f"<- Coming back to one level above, depth={depth_n}", TRACE_LVL, 3)

        Term.values = previous_values
        formula.reassign_terms_val()


# #######################################################################################
# #############################      main function     ##################################
def solver(cnf_file, set_trace):
    """ Main function to solve the SAT pb. Most of the computation is into the objects """
    global sol
    global TRACE_LVL
    TRACE_LVL = set_trace

    # Read from CNF file and create the Formula object
    text_parse_to_formula(cnf_file)

    tracer(f"********************************************************************************\n"
           f"Here is our formula, freshly picked from the file {cnf_file} \n\n"
           f"********************************************************************************", TRACE_LVL, 0)
    tracer(formula, TRACE_LVL, 0)
    tracer(f"Let's start solving ! \n\n"
           f"********************************************************************************", TRACE_LVL, 0)

    # todo Simplify formula by identifying almost duplicates clauses

    # todo eliminate possibilities already stuck in
    # todo create choices_good, choices_bad

    # todo if need deep recursion
    if False:
        import sys
        sys.setrecursionlimit(5000)

    # Initial check for obvious solutions
    recursive_sat_check()

    # Initialize solutions
    first_solution = OrderedDict({'solved': [formula.solved]})
    for k in sorted(Term.values.keys()):
        first_solution[f"x{k}"] = [Term.values[k]]
    first_solution['nb_of_combinations'] = [2**Term.count_unassigned()]
    sol = pd.DataFrame(data=first_solution)

    # Launch the resolution
    rec_try_values([])

    # todo: Need to remove duplicates in the solutions
    #

    # End of the Solver
    # sort_sol()
    tracer(f"\n ********************************************************************************\n"
           f"\nEnd of the solving (hopefully). let's recap. The formula: ", TRACE_LVL, 0)
    tracer(f"\n{formula} \n", TRACE_LVL, 0)
    tracer(f"********************************************************************************", TRACE_LVL, 0)
    tracer(f"\nSolutions : \n", TRACE_LVL, 0)
    pprint(sol[sol.solved == True])
    formula_satisfiable = len(sol[sol.solved == True])
    if formula_satisfiable > 0:
        tracer(f"\nThe formula is satisfiable with AT LEAST {formula_satisfiable} solutions ", TRACE_LVL, 0)
    else:
        tracer(f"\nThe formula is NOT satisfiable", TRACE_LVL, 0)
    tracer(f"None values mean it can take either True or False without affecting the result. \n"
           f"There is currently duplicates because of that. The number of combinations doesn't \n"
           f"take these duplicates into account. Next merge :) ", TRACE_LVL, 0)
    tracer("\nThank you and hoping that I was useful ! :) \n", TRACE_LVL, 1)


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
    cmd.add_argument("-v", "--verbosity", help="Verbosity level, 0 (no comments), to 10 (lots of details)",
                     type=int, default=0, choices=[i for i in range(10+1)])
    args = cmd.parse_args()

    # Parse the text file to formula
    print("Hello, lets start ! Welcome to my SAT solver !")
    set_tracing_lvl(args.verbosity)

    #
    # #######################################################################################
    if args.profiler:
        # Checking processor time with cProfile lib#
        try:
            import cProfile
            import pstats
            cProfile.run("solver(args.input_file, args.verbosity)", "cProfileStats")
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
        solver(args.input_file, args.verbosity)

    # End
    print("Bye bye see you next time ! ~Sylvain \n")


















