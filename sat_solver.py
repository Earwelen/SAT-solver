# #######################################################################################
#     Sylvain Riondet
#         e0267895@u.nus.edu / sylvainriondet@gmail.com
#         2018/05/12
#         National University of Singapore / SoC / CS4244 Kknowledge Based Systems
#         Professor Kuldeep S. Meel
#         Project : SAT solver
# #######################################################################################

# #######################################################################################
# todo TODO List
# todo check input
# todo check output
# todo do the sat solver
# #######################################################################################

# #######################################################################################
# imports
import argparse
import os
from ui import tracer
from sat_classes import Term, Clause


# #######################################################################################
# Variables & constants
PROFILER = False
TRACE_LVL = 5


# #######################################################################################
# #############################      parsing file      ##################################
def text_parse_to_formula(text_file):
    """ Parse .cnf file into terms and clauses """
    formula = []
    with open(text_file) as f:
        for line in f:

            formula.append()

    return formula


# #######################################################################################
# #############################      main function     ##################################
def solver(formula):
    tracer(formula(), TRACE_LVL, 1)


# ########################################################################################
# ##############################    Checking of args    ##################################
def is_valid_file(parser, file_path):
    if not os.path.isfile(file_path):
        parser.error(f'\n The file {file_path} does not exist!')
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
    args = cmd.parse_args()

    # Parse the text file to formula
    print("Hello, lets start ! Welcome to my SAT solver ! ... Sylvain")
    formula = text_parse_to_formula(args.input_file)

    #
    # #######################################################################################
    if PROFILER:
        # Checking processor time with cProfile lib#
        try:
            import cProfile
            import pstats
            cProfile.run("solver(input_formula)", "cProfileStats")
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
        solver(input_formula)



















