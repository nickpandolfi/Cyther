
FINE = 0
ERROR_PASSOFF = 1
SKIPPED_COMPILATION = 1337
WAIT_FOR_FIX = 42

INTERVAL = .25

RESPONSES_ERROR = "Argument 'acceptableResponses' cannot be of type: '{}'"

WATCH_STATS_TEMPLATE = "\n...<iterations:{}, compiles:{}," \
                       "errors:{}, polls:{}>...\n"

SETUP_TEMPLATE = """
# high level importing to extract whats necessary from your '@cyther' code
import sys
sys.path.insert(0, '{0}')
import {1}

# bringing everything into your local namespace
extract = ', '.join([name for name in dir({1}) if not name.startswith('__')])
exec('from {1} import ' + extract)

# freshening up your namespace
del {1}
del sys.path[0]
del sys

# this is the end of the setup actions
"""

TIMER_TEMPLATE = """
import timeit

setup_string = '''{0}'''

code_string = '''{1}'''

repeat = {2}
number = {3}
precision = {4}

exec(setup_string)

timer_obj = timeit.Timer(code_string,
                         setup="from __main__ import {5}".format(extract))

try:
    result = min(timer_obj.repeat(repeat, number)) / number
    rounded = format(result, '.{5}e'.format(precision))
    print("{5} loops, best of {5}: ({5}) sec per loop".format(number, repeat,
                                                              rounded))
except:
    timer_obj.print_exc()

"""

MISSING_INCLUDE_DIRS = """
Cyther could not find any include directories that the
current Python installation was built off of.

This is eiher a bug or you don't have Python correctly installed.
"""

MISSING_RUNTIME_DIRS = """
Cyther could not find any runtime libraries that the
current Python installation was built off of.

This is eiher a bug or you don't have Python correctly installed.
"""

NOT_NEEDED_MESSAGE = "Module '{}' does not have to be included," \
                     "or has no .get_include() method"
