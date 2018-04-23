# #######################################################################################
#  Sylvain Riondet
# e0267895@u.nus.edu / sylvainriondet@gmail.com
# 2018/05/12
# National University of Singapore / SoC / CS4244 Kknowledge Based Systems
# Professor Kuldeep S. Meel
# Project : SAT solver
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
import ui


# #######################################################################################
# Variables & constants
PROFILER = False
TRACE_LVL = 5

# #######################################################################################
def solver(formula):
    print(format())




# ########################################################################################
# ##############################      main function     ##################################
if __name__ == '__main__':

    # Arguments for inline commands : https://docs.python.org/3/howto/argparse.html#id1
    cmd = argparse.ArgumentParser(
        "\n"
        "  Coded by Sylvain Riondet, @NUS/SoC \n"
        "  sylvainriondet@gmail.com \n"
        "  Course: CS4244 - Knowledge-Based Systems\n"
        "  Submission for 2018/05/12 \n"
        "\n")
    cmd.add_argument("input_formula", help="Input formula to test",)  # type=lambda x: fonction_call(cmd, x))
    args = cmd.parse_args()
    # Arguments
    input_formula = args.input_formula
    print("Hello, lets start ! Welcome to my SAT solver ! ... Sylvain")


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



















