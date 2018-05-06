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
# call prog with => python sat_solver.py "cnf_formulas/cnf-2.cnf"
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
import csv
from time import time
from pprint import pprint
from ui import tracer
from sat_classes import Term, Clause, Formula, set_tracing_lvl


# #######################################################################################
# Variables & constants
TRACE_LVL = 1

# formula Object with a list of Clauses composed of Terms
formula = Formula()
# todo describe this solutions holder
sol = [()]
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
        if formula.solved is False:
            return False

        implied_x = None
        # this might actually not help
        # implied_x = formula.find_unique_terms()

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

    assigned_terms = tuple(Term.values[k] for k in Term.values.keys())
    # assigned_terms = (formula.solved,) + assigned_terms + (None,)
    #  if Term.values[k] is not None

    nb_occurrences = 0

    for solution in sol[1:]:
        # compare the values (so excludes index 0 and -1) and check if the set of values already assigned exists in
        #  the solutions
        tracer(tuple((s, a, "s, a, and s==a ", s == a) for s, a in zip(solution[1:-1], assigned_terms) if s is not None), TRACE_LVL, 3)
        if all((s == a for s, a in zip(solution[1:-1], assigned_terms) if s is not None)):
            nb_occurrences += 1
            # if no need to count, then exit
            break
    # tracer(f"This set of literals appears {nb_occurrences} times in the solutions", TRACE_LVL, 6)

    tracer(f"Current set of solutions", TRACE_LVL, 5)
    tracer(sol, TRACE_LVL, 5)

    return True if nb_occurrences > 0 else False


# #######################################################################################
# #################      find all combinations of terms/values     ######################
def save_solution_list():
    """
    Save (append) the solution into pandas DataFrame
    """
    global sol

    # todo check if there is not a broader set of solution. merge with it.

    new_solution = [formula.solved, ]
    for k in Term.values.keys():
        new_solution.append(Term.values[k])
    new_solution.append(Term.count_unassigned())
    new_sol = tuple(new_solution)

    # Add only if not already in solution list
    for index, solution in enumerate(sol):
        if index == 0:
            continue

        # compare the values (so excludes index 0 and -1) and check if the set of values already assigned exists in
        #  the solutions
        tracer((solution, new_sol), TRACE_LVL, 6)

        # Exact solution already existing
        if all((s == n for s, n in zip(solution[1:-1], new_sol[1:-1]))):
            tracer(f"... Exact same solution already existing", TRACE_LVL, 3)
            return
        # Broader solution existing
        if all((s == n for s, n in zip(solution[1:-1], new_sol[1:-1]) if s is not None)):
            tracer(f"... Broader solution already existing", TRACE_LVL, 3)
            return
        # if the new solution is more general, replace the previous one
        if all((s == n for s, n in zip(solution[1:-1], new_sol[1:-1]) if n is not None)):
            tracer(f"... New solution is more broad", TRACE_LVL, 3)
            sol[index] = new_sol
            return

    sol.append(new_sol)

    tracer(f"Appended solution {sol[-1]}", TRACE_LVL, 2)


# #######################################################################################
# #################      recursively choose values of terms     #########################
def rec_try_values(find_all, val_keys):
    """
    choose a value of an unconstrained term and check satisfiability of the formula.
    if still neither True or False, recursively choose more terms
    call function to save the computed values
    try to not recheck what has already been checked
    """
    # todo remove i_explored, seems useless with the current implementation

    if val_keys is None:
        return

    global depth_n
    # tracer(f"=> Depth {depth_n}. Making a guess, i_explored={i_explored}", TRACE_LVL, 0)

    for x in val_keys:
        # Save previous values to reset to previous state at the end
        previous_values = Term.values.copy()
        formula.reassign_terms_val()

        # Value already assigned, guess no need. Maybe need to record somehow ?
        if Term.values[x] is not None:
            tracer(f"Term x[{x}]={Term.values[x]}, continuing", TRACE_LVL, 6)
            continue

        # Main tracer for all loops
        tracer("="*(depth_n-1) + f"=> Depth {depth_n},\t x{x}\t: {len(sol)-1} solutions so far (True and False)", TRACE_LVL, 0)

        for true_false in (True, False):
            previous_values_2 = Term.values.copy()
            Term.values[x] = true_false
            formula.reassign_terms_val()
            tracer(f"Choosing x{x}={true_false}. Term.values = {Term.values}", TRACE_LVL, 1)

            # Check that we didn't already search this set of values
            already_checked = check_is_in_solutions()
            if already_checked:
                tracer(f"**** Has already been tried in previous loops {Term.values}", TRACE_LVL, 5)
                Term.values = previous_values_2
                formula.reassign_terms_val()
                continue

            # Then alright, let's apply it
            recursive_sat_check()
            if formula.solved in (True, False):
                tracer(f"*Solved={formula.solved}* -> adding solution n{len(sol)} if not redundant: "
                       f"Term.values = {Term.values}", TRACE_LVL, 2)
                # Add the solution to the global variable
                save_solution_list()
                # if just want to have the first solution, stop here.
                if formula.solved is True and find_all is False:
                    return
            else:
                depth_n += 1
                tracer(f"Not Solved. Let's go to depth_n={depth_n}. Term.values = {Term.values}", TRACE_LVL, 3)
                next_val_keys = val_keys.copy()
                next_val_keys.remove(x)
                rec_try_values(find_all, next_val_keys)
                depth_n -= 1
                tracer(f"<- Coming back to one level above, depth={depth_n}", TRACE_LVL, 3)
                # if just want to have the first solution, stop here.
                if formula.solved is True and find_all is False:
                    return

            Term.values = previous_values_2
            formula.reassign_terms_val()

        Term.values = previous_values
        formula.reassign_terms_val()


# #######################################################################################
# #############################      main function     ##################################
def solver(cnf_file, find_all, set_trace):
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
    if True:
        import sys
        sys.setrecursionlimit(5000)

    # Initial check for obvious solutions
    recursive_sat_check()

    # Initialize solutions
    first_solution = [formula.solved,]
    for k in sorted(Term.values.keys()):
        first_solution.append(Term.values[k])
    first_solution.append(Term.count_unassigned())
    sol = [tuple(first_solution), ]

    # Launch the resolution
    rec_try_values(find_all, list(Term.values.keys()))

    # todo: Need to remove duplicates in the solutions

    # Save solutions
    # todo save sol.to_csv() every 5 seconds ?
    save_to = "cnf_formulas/Solutions/" + cnf_file.split('/')[-1].split('.')[0] + "-solved.csv"

    with open(save_to, 'w') as csv_file:
        csv_out = csv.writer(csv_file)
        csv_out.writerows(sol)

    tracer(f"\n*** Solutions save to {save_to} ***", TRACE_LVL, 0)

    # End of the Solver
    tracer(f"\n ********************************************************************************\n"
           f"\nEnd of the solving (hopefully). let's recap. The formula: ", TRACE_LVL, 0)
    tracer(f"\n{formula} \n", TRACE_LVL, 0)
    tracer(f"********************************************************************************", TRACE_LVL, 0)

    # Solutions
    true_sol = [s for s in sol if s[0] is True]
    tracer(f"\nSolutions : \n", TRACE_LVL, 0)
    pprint(true_sol)
    formula_satisfiable = len(true_sol)
    if formula_satisfiable > 0:
        tracer(f"\nThe formula is satisfiable with AT LEAST {formula_satisfiable} solutions ", TRACE_LVL, 0)
    else:
        tracer(f"\nThe formula is NOT satisfiable", TRACE_LVL, 0)
    if find_all is False and formula.solved is True:
        tracer(f"If you want to find ALL the solutions, rerun with the option -a / --all_solutions "
               f"(takes time if clauses/literals < 20 !)", TRACE_LVL, 0)
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
    cmd.add_argument("-a", "--all_solutions", help="Find all solutions. If more than 20 clauses/literals, "
                                                   "takes a LOT of time.", action='store_true', default=False)
    cmd.add_argument("-p", "--profiler", help="Activate the profiler", action='store_true', default=False)
    cmd.add_argument("-m", "--memory", help="Activate memory tracker", action='store_true', default=False)
    cmd.add_argument("-v", "--verbosity", help="Verbosity level, 0 (no comments), to 10 (lots of details)",
                     type=int, default=0, choices=[i for i in range(-1, 10)])
    args = cmd.parse_args()

    # Parse the text file to formula
    print("Hello, lets start ! Welcome to my SAT solver !")
    set_tracing_lvl(args.verbosity)

    if args.memory:
        from pympler import tracker
        tr = tracker.SummaryTracker()

    start_time = time()

    #
    # #######################################################################################
    if args.profiler:
        # Checking processor time with cProfile lib#
        try:
            import cProfile
            import pstats
            cProfile.run("solver(args.input_file, args.all_solutions, args.verbosity)", "cProfileStats")
            stats = pstats.Stats("cProfileStats")
            # Sort the stats and print the 10 first rows
            stats.sort_stats("cumtime")
            tracer(f"\n********************************************************************************", TRACE_LVL, 0)
            tracer(f"\tPROFILER", TRACE_LVL, 0)
            stats.print_stats(30)
        except:
            print("** Crashed, nothing saved ** \n"
                  "* Try without the profiler to have more details *")
        finally:
            os.remove("cProfileStats")

    else:
        solver(args.input_file, args.all_solutions, args.verbosity)

    tracer(f"\n********************************************************************************", TRACE_LVL, 0)
    tracer(f"\tTotal execution time:\t {round(time()-start_time, 3)} seconds", TRACE_LVL, 0)
    if args.memory:
        tracer(f"********************************************************************************", TRACE_LVL, 0)
        tracer(f"\tMEMORY USAGE", TRACE_LVL, 0)
        tr.print_diff()

    # End
    print("\nBye bye see you next time ! ~Sylvain \n")


















