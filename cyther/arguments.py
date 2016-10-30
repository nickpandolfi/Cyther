import argparse

from .system import INFO


help_filenames = 'The Cython source files'
help_concise = "Get cyther to NOT print what it is thinking. Only use if you like to live on the edge"
help_preset = 'The preset options for using cython and gcc (ninja, beast, minimal, swift)'
help_timestamp = 'If this flag is provided, cyther will not compile files that have a modified' \
                 'time before that of your compiled .pyd or .so files'
help_output_name = 'Change the name of the output file, default is basename plus .pyd'
help_include = 'The names of the python modules that have an include library that needs to be passed to gcc'
help_local = 'When not flagged, builds in __cythercache__, when flagged, it builds locally in the same directory'
help_watch = "When given, cyther will watch the directory with the 't' option implied and compile," \
             "when necessary, the files given"
help_error = "Raise a CytherError exception instead of printing out stderr when -w is not specified"
help_execute = "Run the @Cyther code in multi-line single quoted strings, and comments"
help_timer = "Time the @Cyther code in multi-line single quoted strings, and comments"
help_X = "A 'super flag' that implies the flags '-x', '-s', and '-w'"
help_T = "A 'super flag' that implies the flags '-t', '-s', and '-w'"
help_cython = "Arguments to pass to Cython"
help_gcc = "Arguments to pass to gcc"

description_text = 'Auto compile and build .pyx or .py files in place.'
description = description_text
epilog_text = "{}\nOther Info:\n\tUse '_' or '__' instead of '-' or '--' when passing args to gcc or Cython"
epilog_text += "\n\tThe ('-x', '-X') and ('-t', '-T') Boolean flags are mutually exclusive"
epilog = epilog_text.format(INFO)
formatter = argparse.RawDescriptionHelpFormatter

parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=formatter)
parser.add_argument('filenames', action='store', nargs='+', help=help_filenames)
parser.add_argument('-c', '--concise', action='store_true', help=help_concise)
parser.add_argument('-p', '--preset', action='store', default='', help=help_preset)
parser.add_argument('-s', '--timestamp', action='store_true', help=help_timestamp)
parser.add_argument('-o', '--output_name', action='store', help=help_output_name)
parser.add_argument('-i', '--include', action='store', default='', help=help_include)
parser.add_argument('-l', '--local', action='store_true', help=help_local)
parser.add_argument('-w', '--watch', action='store_true', help=help_watch)
parser.add_argument('-e', '--error', action='store_true', help=help_error)

execution_system = parser.add_mutually_exclusive_group()
execution_system.add_argument('-x', '--execute', action='store_true', dest='execute', default=False, help=help_execute)
execution_system.add_argument('-t', '--timeit', action='store_true', dest='timer', default=False, help=help_timer)

super_flags = parser.add_mutually_exclusive_group()
super_flags.add_argument('-X', action='store_true', dest='X', default=False, help=help_X)
super_flags.add_argument('-T', action='store_true', dest='T', default=False, help=help_T)

parser.add_argument('-cython', action='store', nargs='+', dest='cython_args', default=[], help=help_cython)
parser.add_argument('-gcc', action='store', nargs='+', dest='gcc_args', default=[], help=help_gcc)
