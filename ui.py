# #######################################################################################
#  Sylvain Riondet
# e0267895@u.nus.edu / sylvainriondet@gmail.com
# 2018/05/12
# National University of Singapore / SoC / CS4244 Kknowledge Based Systems
# Professor Kuldeep S. Meel
# Project : SAT solver
# #######################################################################################


from pprint import pprint
from time import time as now
from os import getpid
from os import path as os_path
import sys
import csv
from threading import active_count as thread_active_count


def tracer(message, tracing_lvl=3, mess_priority=10, m_type="info", flush=False):
    """
    Print tracing message depending on their priority.
    Only message with priority inferior to the "tracing_lvl" will be displayed
    In case of error, print all previous messages and stops the script
    In case of warning, print at the end all warnings again

    :param flush: force flush
    :type flush: boolean
    :param message: message to print
    :type message: Union[str, List[str], Any]
    :param tracing_lvl: the parameter of messages details from the use (default is 3, max is 10)
    :type tracing_lvl: int
    :param mess_priority: the priority of This message
    :type mess_priority: int
    :param m_type: optional, can be either info, warning or error
    :type m_type: str
    :return: nothing
    :rtype: None
    """

    # An object message is created for each new message and added to the complete trace
    m = Message(message, mess_priority, m_type)

    # #################################################################################################################
    # Then prints the message is its priority is high than the desired
    if tracing_lvl is None or tracing_lvl < 0:
        tracing_lvl = 3
    if mess_priority <= tracing_lvl:
        if isinstance(m.msg, str):
            if Message.flush:
                print(m.log_name, str("  " * m.priority + m.msg), sep=": ")
            else:
                print(m.parser_id, str("  " * m.priority + m.msg), sep=": ")
        else:
            if Message.flush: print(m.log_name, ": ")
            else: print(m.parser_id, ": ")
            pprint(message)

    # #################################################################################################################
    # Then if it's a special message, special behavior can happen
    if m_type == "error":
        # In case of an error, stops the parser, display all messages and wait for exiting
        print("########             E R R O R    F O U N D          ######### ", flush=True)
        print("########  Last line should help you with this error  ######### ", flush=True)
        print("######## CSV file contains the report of the parsing ######### \n", flush=True)

        # write all messages in csv file
        m.to_csv()

        # Raise error for the parent process
        raise ChildProcessError(m.msg)

    # ##########################################################################################
    if m_type == "end" and thread_active_count() == 1:
        # At the end, if it is the last process (no "renaming pictures" thread still running),
        # print all the warnings if there were any
        warnings = [m for m in Message.all_msg if m.m_type == "warning"]
        if len(warnings) > 0:
            # First find the log name, so people can easily find which file had an issue.
            log_name = [i for i in Message.all_msg if i.m_type is "log_name"]
            print("\n\nWe had {} warnings during the parsing of : -> {} <-\n".format(len(warnings), log_name[0].msg))

            # Then print all messages
            for m in warnings:
                print("\t{}".format(m.msg))
            print("\n")
            # and write a csv with the messages
            m.to_csv()

        # Flush all messages
        sys.stdout.flush()
        print("", flush=True)
        # Delete all messages (in multiprocessing, to avoid multiple instances)
        Message.clean_msgs()

    # ##########################################################################################
    # if flush is desired, do it
    if m_type == "flush":
        Message.flush = True
    if Message.flush:
        sys.stdout.flush()

    # ##########################################################################################
    # if the output of the csv is specified, put it in the class variable
    if m_type == "csv_output":
        if os_path.isdir(os_path.dirname(message)):
            Message.csv_output = message

    # ##########################################################################################
    # Save the log file name
    if m_type == "log_name":
        Message.log_name = message
    # ##########################################################################################
    # save the directory of the log file
    if m_type == "log_dir":
        Message.log_dir = message

    # If flush option is enable, do it
    if flush: sys.stdout.flush()


class Message:
    """
    Messages writen during the script. They can be recalled if something goes wrong.
    Each message comes with an id, its priority, the message and the kind of message it is
    """
    msg_types = ("log_name", "log_dir", "info", "warning", "error", "end")
    time_first_msg = now()
    msg_count = 0
    all_msg = []
    flush = False
    csv_output = ""
    log_dir = ""
    log_name = ""

    def __init__(self, msg, priority, m_type="info", p_id=getpid()):
        self.msg = msg
        self.priority = priority
        self.m_type = m_type
        self.time = now() - Message.time_first_msg
        self.id = Message.msg_count
        self.parser_id = p_id
        Message.msg_count += 1
        Message.all_msg += [self]

    def __repr__(self):
        return "{}\t:{} ".format(self.log_name, self.msg)

    def verbose(self):
        return "{} : message n{:>5} at {:3.3}seconds, priority:{:>2}, {:7}: \n\t{} ".format(
            self.parser_id, self.id, self.time, self.priority, self.m_type, self.msg)

    # Clean all messages from previous process
    @classmethod
    def clean_msgs(cls):
        """ Remove all messages before the next log file """
        Message.time_first_msg = now()
        Message.msg_count = 0
        Message.all_msg = []
        Message.flush = False
        Message.csv_output = ""
        # default can be "//rt-x7270.de.bosch.com/share_data/APLM/Data_Streaming/Parser_messages/parser_messages.csv"
        Message.log_dir = ""
        Message.log_name = ""

    @classmethod
    def to_csv(cls):
        """Write all the message into a csv file. Default output file is inside the test folder.
            User can specify the output file."""

        if cls.csv_output == "":
            csv_name = [m.msg for m in cls.all_msg if m.m_type == "log_name"][0]
            csv_dir = [m.msg for m in cls.all_msg if m.m_type == "log_dir"][0]
            csv_file = os_path.join(csv_dir, "parsing_messages_" + os_path.splitext(csv_name)[0] + ".csv")
            opening_parameter = "w"
        else:
            csv_file = cls.csv_output
            opening_parameter = "a"

        try:
            # Check if the file already has the delimiter and headers
            flag_add_csv_headers = False
            if opening_parameter == "w":
                flag_add_csv_headers = True
            else:
                with open(csv_file, "r", newline="") as file:
                    csv_reader = csv.reader(file, delimiter=";")
                    if sum(1 for row in csv_reader) == 0:
                        flag_add_csv_headers = True

            with open(csv_file, opening_parameter, newline="") as file:
                # CSV writer
                spam_writer = csv.writer(file, delimiter=";")

                # if new file then add the delimiter and headers
                if flag_add_csv_headers:
                    spam_writer.writerow(("sep=;", ))
                    spam_writer.writerow(
                        ("process_id", "msg_type", "msg_id", "time", "msg_priority", "message", "log_dir", "log_name"))

                # Then write all the lines
                for m in cls.all_msg:
                    if m.priority <= 8:
                        time = "{0:.3f}".format(m.time).replace(".", ",")
                        spam_writer.writerow(
                            (m.parser_id, m.m_type, m.id, time, m.priority, m.msg, cls.log_dir, cls.log_name))
            print("CSV file with debug messages written at : " + csv_file + "\n\n", flush=True)
        except:
            print("CSV file not written, write access denied or wrong path \n", flush=True)




