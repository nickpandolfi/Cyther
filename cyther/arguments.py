
import argparse
from .core import info, configure, test, setup, make, clean, purge


help_info = "Prints the information regarding cyther's installation and " \
            "environment. Returns helpful info on the compilers used and" \
            "all the current build settings, then exits"
help_configure = "A very important command to run once in a while. This will" \
                 "trigger cyther's search for the compilers it will use on" \
                 "your system"
help_test = "Binary flag to run the included 'test.py' script"
help_setup = "Constructs the standard 'cytherize' file necessary to use" \
             "cyther. Takes an optional 'preset' argument to control the" \
             "style of commands generated and injected into the" \
             "'cytherize' file"
help_make = "Similar to GNU's 'make' command. Runs a file called" \
            "'cytherize' in your local directory. Optionally takes an" \
            "argument of a path to a specific 'cytherize' formatted file" \
            "that may not normally run."
help_clean = "Cleans the current directory of anything not in use. Will" \
             "ask explicit permission for anything to be deleted. Empties" \
             "the '__cythercache__' of independent files. This command is" \
             "similar to GNU's conventional '$make clean' for use with" \
             "makefiles"
help_purge = "Cleans the current directory of EVERYTHING cyther related." \
             "Will ask explicit permission for anything" \
             "to be deleted. Deletes the '__cythercache__'"

description_text = "Auto compile and build .pyx, .py, or .c files in-place"
formatter = argparse.RawDescriptionHelpFormatter

#Any others to use? Why did I choose this one?
parser = argparse.ArgumentParser(description=description_text,
                                 formatter_class=formatter)







commands = parser.add_subparsers()

# $$$$$$$$$$ COMMANDS FOR INFO $$$$$$$$$$
info_parser = commands.add_parser('info', help=help_info)
info_parser.set_defaults(func=info)
# Empty as of now




# $$$$$$$$$$ COMMANDS FOR CONFIGURE $$$$$$$$$$
configure_parser = commands.add_parser('configure', help=help_configure)
configure_parser.set_defaults(func=configure)
# Empty as of now




# $$$$$$$$$$ COMMANDS FOR TEST $$$$$$$$$$
test_parser = commands.add_parser('test', help=help_test)
test_parser.set_defaults(func=test)
# Empty as of now




# $$$$$$$$$$ COMMANDS FOR SETUP $$$$$$$$$$
setup_parser = commands.add_parser('setup', help=help_setup)
setup_parser.set_defaults(func=setup)
help_filenames = "The Cython source file(s)"
setup_parser.add_argument('filenames', action='store',
                          nargs='+', help=help_filenames)
help_preset = 'The preset options for using cython and' \
              'gcc (ninja, beast, minimal, swift)'
setup_parser.add_argument('--preset', action='store',
                          default='', help=help_preset)
help_output = 'Change the name of the output file,' \
              'default is basename plus .pyd'
setup_parser.add_argument('--output', action='store', help=help_output)
help_include = 'The names of the python modules that have an include' \
               'library that needs to be passed to gcc'
setup_parser.add_argument('--include', action='store',
                          default='', help=help_include)
help_gcc = "Arguments to pass to gcc"
setup_parser.add_argument('--gcc', action='store', nargs='+',
                          dest='gcc_args', default=[], help=help_gcc)
help_cython = "Arguments to pass to Cython"
setup_parser.add_argument('--cython', action='store', nargs='+',
                          dest='cython_args', default=[], help=help_cython)




# $$$$$$$$$$ COMMANDS FOR MAKE $$$$$$$$$$
make_parser = commands.add_parser('make', help=help_make)
make_parser.set_defaults(func=make)
help_concise = "Get cyther to NOT print what it is thinking. Only use if" \
               "you like to live on the edge"
make_parser.add_argument('--concise', action='store_true', help=help_concise)
help_local = 'When not flagged, builds in __cythercache__, when flagged,' \
             'it builds locally in the same directory'
make_parser.add_argument('--local', action='store_true', help=help_local)
help_watch = "When given, cyther will watch the directory with the 't'" \
             "option implied and compile, when necessary, the files given"
make_parser.add_argument('--watch', action='store_true', help=help_watch)
help_error = "Raise a CytherError exception instead of printing out stderr" \
             "when -w is not specified"
make_parser.add_argument('--error', action='store_true', help=help_error)
execution_system = make_parser.add_mutually_exclusive_group()
help_execute = "Run the @Cyther code in multi-line single quoted strings," \
               "and comments"
execution_system.add_argument('--execute', action='store_true',
                              dest='execute', help=help_execute)
help_timer = "Time the @Cyther code in multi-line single quoted strings," \
             "and comments"
execution_system.add_argument('--timeit', action='store_true',
                              dest='timer', help=help_timer)




# $$$$$$$$$$ COMMANDS FOR CLEAN $$$$$$$$$$
clean_parser = commands.add_parser('clean', help=help_clean)
clean_parser.set_defaults(func=clean)
# Empty as of now




# $$$$$$$$$$ COMMANDS FOR PURGE $$$$$$$$$$
purge_parser = commands.add_parser('purge', help=help_purge)
purge_parser.set_defaults(func=purge)
# Empty as of now


"""
Unsure:
help_timestamp = 'If this flag is provided, cyther will not compile files' \
                 'that have 'not been modified since last compile'
make_parser.add_argument('--timestamp', action='store_true',
                         help=help_timestamp)

"""
