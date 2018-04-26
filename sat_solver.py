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

    found_x = True
    iteration = 0

    while found_x is not None:
        # todo might need to move the solution from Term.values to another variable

        unassigned_terms = Term.count_unassigned()
        tracer(f"=> Iteration {iteration}: Still {unassigned_terms} undefined out of {formula.nb_terms}", TRACE_LVL, 1)

        formula.reassign_terms_val()
        formula.satisfiable()       # recheck all the clauses satisfiability

        found_x = formula.find_unique_terms()
        if found_x is None: break

        tracer(f"Found Term {found_x} that has an unique possible value \n", TRACE_LVL, 2)
        Term.values[found_x['x']] = found_x['val']

        iteration += 1

    return formula.solved


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

    # todo Simplify formula by identifying almost duplicates

    # todo recursive checking of possibilities
    # todo find multiple solutions
    # todo eliminate possibilities already stuck in

    # todo create current_choice
    # todo create choices_good, choices_bad
    # todo still_unexplored_solutions()?
    # todo make_choice()
    # todo if formula == True / False / None => decide
    # todo while loop

    if False:
        for x in Term.values:
            for tf in (True, False):
                for again in Term.values:
                    print("until idk")

    # Simple solving if no need for guess or reduction
    satisfiable = recursive_sat_check()

    # End of the Solver
    tracer(f"\nTerms = {Term.values}", TRACE_LVL, 1)
    tracer(f"\nThe formula is satisfiable: {satisfiable}", TRACE_LVL, 0)
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


















