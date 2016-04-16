# Only those who risk going too far, can truly find out how far one can go

import site, textwrap

import distutils
import distutils.sysconfig
import distutils.msvccompiler

import os, sys, subprocess, platform
import re, collections, argparse
import time, traceback


class CytherError(Exception):
    def __init__(self, *args, **kwargs):
        super(CytherError, self).__init__(*args, **kwargs)


try:
    from shutil import which
except ImportError:
    raise CytherError("The current version of Python doesn't support the function 'which', normally located in shutil")


def dealWithMissingStaticLib(message):
    raise CytherError(message)


def getIncludeAndRuntime():
    include_dirs, library_dirs = [], []

    py_include = distutils.sysconfig.get_python_inc()
    plat_py_include = distutils.sysconfig.get_python_inc(plat_specific=1)

    include_dirs.append(py_include)
    if plat_py_include != py_include:
        include_dirs.append(plat_py_include)

    if os.name == 'nt':
        library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))
        include_dirs.append(os.path.join(sys.exec_prefix, 'PC'))

        if MSVC_VERSION == 14:
            library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VS14', 'win32release'))
        elif MSVC_VERSION == 9:
            suffix = '' if PLATFORM == 'win32' else PLATFORM[4:]
            new_lib = os.path.join(sys.exec_prefix, 'PCbuild')
            if suffix:
                new_lib = os.path.join(new_lib, suffix)
            library_dirs.append(new_lib)
        elif MSVC_VERSION == 8:
            library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VS8.0', 'win32release'))
        elif MSVC_VERSION == 7:
            library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VS7.1'))
        else:
            library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VC6'))

    if os.name == 'os2':
        library_dirs.append(os.path.join(sys.exec_prefix, 'Config'))

    is_cygwin = sys.platform[:6] == 'cygwin'
    is_atheos = sys.platform[:6] == 'atheos'
    is_shared = distutils.sysconfig.get_config_var('Py_ENABLE_SHARED')
    is_linux = sys.platform.startswith('linux')
    is_gnu = sys.platform.startswith('gnu')
    is_sunos = sys.platform.startswith('sunos')

    if is_cygwin or is_atheos:
        if sys.executable.startswith(os.path.join(sys.exec_prefix, "bin")):
            library_dirs.append(os.path.join(sys.prefix, "lib", BASENAME, "config"))
        else:
            library_dirs.append(os.getcwd())

    if (is_linux or is_gnu or is_sunos) and is_shared:
        if sys.executable.startswith(os.path.join(sys.exec_prefix, "bin")):
            library_dirs.append(distutils.sysconfig.get_config_var('LIBDIR'))
        else:
            library_dirs.append(os.getcwd())

    user = True
    if user:
        user_include = os.path.join(site.USER_BASE, "include")
        user_lib = os.path.join(site.USER_BASE, "lib")
        if os.path.isdir(user_include):
            include_dirs.append(user_include)
        if os.path.isdir(user_lib):
            library_dirs.append(user_lib)

    ret_object = (include_dirs, library_dirs)

    filter_that = True
    if filter_that:
        for x, obj in enumerate(ret_object):
            for y, item in enumerate(obj):
                if not os.path.isdir(item):
                    del ret_object[x][y]

    return ret_object

########################################################################################################################
########################################################################################################################

FINE = 0
ERROR_PASSOFF = 1
SKIPPED_COMPILATION = 1337
WAIT_FOR_FIX = 42

INTERVAL = .25

MAJOR = str(sys.version_info.major)
MINOR = str(sys.version_info.minor)

VER = MAJOR + MINOR

MSVC_VERSION = int(distutils.msvccompiler.get_build_version())
PLATFORM = sys.platform
BASENAME = "python" + distutils.sysconfig.get_python_version()

CYTHONIZABLE_FILE_EXTS = ('.pyx', '.py')

DRIVE, _ = os.path.splitdrive(sys.exec_prefix)
if not DRIVE:
    DRIVE = os.path.normpath('/')

CYTHER_CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.cyther')


def sift(obj):
    string = [str(item) for name in obj for item in os.listdir(name)]
    s = set(re.findall('(?<=lib)(.+?)(?=\.so|\.a)', '\n'.join(string)))
    result = max(list(s), key=len)
    return result


INCLUDE_DIRS, RUNTIME_DIRS = getIncludeAndRuntime()

L_OPTION = '-l' + sift(RUNTIME_DIRS)

INCLUDE_STRING = ''
for directory in INCLUDE_DIRS:
    INCLUDE_STRING += '-I' + directory


RUNTIME_STRING = ''
for directory in RUNTIME_DIRS:
    RUNTIME_STRING += '-L' + directory

EXPRESSIONS = collections.defaultdict()

MISSING_INCLUDE_DIRS = """
Cyther could not find any include directories that the current Python installation was built off of.
This is eiher a bug or you don't have Python correctly installed.
"""

MISSING_RUNTIME_DIRS = """
Cyther could not find any runtime libraries that the current Python installation was built off of.
This is eiher a bug or you don't have Python correctly installed.
"""

NOT_NEEDED_MESSAGE = "Module '{}' does not have to be included, or has no .get_include() method"

if not INCLUDE_DIRS:
    raise CytherError(MISSING_INCLUDE_DIRS)

if not RUNTIME_DIRS:
    dealWithMissingStaticLib(MISSING_RUNTIME_DIRS)


pound_extract = re.compile(r"(?:#\s*@\s?[Cc]yther\s+)(?P<content>.+?)(?:\s*)(?:\n|$)")
tripple_extract = re.compile(r"(?:(?:''')(?:(?:.|\n)+?)@[C|c]yther\s+)(?P<content>(?:.|\n)+?)(?:\s*)(?:''')")


setupTemplate = """
# high level importing to extract whats necessary from your '@cyther' code
import sys
sys.path.insert(0, '{0}')
import {1}

# bringing everything into your local namespace
extract_these = ', '.join([name for name in dir({1}) if not name.startswith('__')])
exec('from {1} import ' + extract_these)

# freshening up your namespace
del {1}
del sys.path[0]
del sys

# this is the end of the setup actions
"""

timerTemplate = """
import timeit

setup_string = '''{0}'''

code_string = '''{1}'''

repeat = {2}
number = {3}
precision = {4}

exec(setup_string)

timer_obj = timeit.Timer(code_string, setup="from __main__ import {5}".format(extract_these))

try:
    result = min(timer_obj.repeat(repeat, number)) / number
    rounded = format(result, '.{5}e'.format(precision))
    print("{5} loops, best of {5}: ({5}) sec per loop".format(number, repeat, rounded))
except:
    timer_obj.print_exc()

"""


########################################################################################################################
########################################################################################################################


def where(cmd, mode=os.X_OK, path=None):
    raw_result = which(cmd, mode, path)
    if raw_result:
        return os.path.abspath(raw_result)
    else:
        raise CytherError("Could not find '{}' in the path".format(cmd))


def getFullPath(filename):
    """This will get the full path of a path of a filename"""
    if os.path.exists(filename) and (filename not in os.listdir(os.getcwd())):
        ret = filename
    elif os.path.exists(os.path.join(os.getcwd(), filename)):
        ret = os.path.join(os.getcwd(), filename)
    else:
        raise CytherError("The file '{}' does not exist".format(filename))
    return ret


def processFiles(args):
    """Generates and error checks each file's information before the compilation actually starts"""
    to_process = []

    for filename in args['filenames']:
        file = dict()

        if args['include']:
            file['include'] = INCLUDE_STRING + ''.join(['-I' + item for item in args['include']])
        else:
            file['include'] = INCLUDE_STRING

        file['file_path'] = getFullPath(filename)
        file['file_base_name'] = os.path.splitext(os.path.basename(file['file_path']))[0]
        file['no_extension'], file['extension'] = os.path.splitext(file['file_path'])
        if file['extension'] not in CYTHONIZABLE_FILE_EXTS:
            raise CytherError("The file '{}' is not a designated cython file".format(file['file_path']))
        base_path = os.path.dirname(file['file_path'])
        local_build = args['local']
        if not local_build:
            cache_name = os.path.join(base_path, '__cythercache__')
            os.makedirs(cache_name, exist_ok=True)
            file['c_name'] = os.path.join(cache_name, file['file_base_name']) + '.c'
        else:
            file['c_name'] = file['no_extension'] + '.c'

        output_name = args['output_name']
        if args['watch']:
            file['output_name'] = file['no_extension'] + DEFAULT_OUTPUT_EXTENSION
        elif output_name:
            if os.path.exists(output_name) and os.path.isfile(output_name):
                file['output_name'] = output_name
            else:
                dirname = os.path.dirname(output_name)
                if not dirname:
                    dirname = os.getcwd()
                if os.path.exists(dirname):
                    file['output_name'] = output_name
                else:
                    raise CytherError('The directory specified to write the output file in does not exist')
        else:
            file['output_name'] = file['no_extension'] + DEFAULT_OUTPUT_EXTENSION

        file['stamp_if_error'] = 0
        to_process.append(file)
    return to_process


def isValid(file):
    modified_time = os.path.getmtime(file['file_path'])
    valid = modified_time > file['stamp_if_error']
    return valid


def isOutDated(file):
    """Figures out if Cyther should compile the given file. For use with the -s option"""
    if os.path.exists(file['output_name']):
        source_time = os.path.getmtime(file['file_path'])
        output_time = os.path.getmtime(file['output_name'])
        if source_time > output_time:
            return True
    else:
        return True
    return False


def printCommands(*several_commands):
    for commands in several_commands:
        print(' '.join(commands).strip())


def makeCommands(preset, file):
    """
    Given a high level preset, it will construct the basic args to pass over.
    'ninja', 'beast', 'minimal', 'swift'
    """
    if not preset:
        preset = 'ninja'

    if preset == 'ninja':
        cython_command = ['cython', '-a', '-p', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-fPIC', '-shared', '-w', '-O3', file['include'], RUNTIME_STRING, '-o',
                       file['output_name'], file['c_name'], L_OPTION]
    elif preset == 'beast':
        cython_command = ['cython', '-a', '-l', '-p', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-fPIC', '-shared', '-Wall', '-O3', file['include'], RUNTIME_STRING, '-o',
                       file['output_name'], file['c_name'], L_OPTION]
    elif preset == 'minimal':
        cython_command = ['cython', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-fPIC', '-shared', file['include'], RUNTIME_STRING, '-o', file['output_name'],
                       file['c_name'], L_OPTION]
    elif preset == 'swift':
        cython_command = ['cython', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-fPIC', '-shared', '-Os', file['include'], RUNTIME_STRING, '-o', file['output_name'],
                       file['c_name'], L_OPTION]
    else:
        raise CytherError("The preset '{}' is not supported".format(preset))
    return cython_command, gcc_command


def convertToDashes(commands):
    """Converts Cyther's pass off notation to the regular dash notation (_a becomes -a)"""
    processed = []
    for command in commands:
        if command[0] == '_':
            if command[1] == '_':
                command = '--' + command[2:]
            else:
                command = '-' + command[1:]
        processed.append(command)
    return processed


def filterCommands(pass_off_commands, commands):
    """Puts items of pass_off_commands in commands if commands does not already have them"""
    if pass_off_commands:
        for item in pass_off_commands:
            if item[0] == '-':
                if item not in commands:
                    commands.append(item)


def finalizeCommands(args, file):
    cython_commands, gcc_commands = makeCommands(args['preset'], file)

    cython_pass_off = convertToDashes(args['cython_args'])
    gcc_pass_off = convertToDashes(args['gcc_args'])

    filterCommands(cython_pass_off, cython_commands)
    filterCommands(gcc_pass_off, gcc_commands)

    return cython_commands, gcc_commands


def getDirsToInclude(string):
    """Given a string of module names, it will return the 'include' directories essential to their compilation"""
    dirs = []
    a = string.strip()
    obj = a.split('-')

    if len(obj) == 1 and obj[0]:
        for module in obj:
            try:
                exec('import {}'.format(module))
            except ImportError:
                raise CytherError("The module '{}' does not exist".format(module))
            try:
                dirs.append('-I {}'.format(eval(module).get_include()))
            except AttributeError:
                print(NOT_NEEDED_MESSAGE.format(module))
    return dirs


def processArgs(args):
    if isinstance(args, str):
        unprocessed = args.strip().split(' ')
        if unprocessed[0] == 'cytherize' or unprocessed[0] == 'cyther':
            del unprocessed[0]
        args = parser.parse_args(unprocessed).__dict__
    elif isinstance(args, argparse.Namespace):
        args = args.__dict__
    elif isinstance(args, dict):
        pass
    else:
        raise CytherError("Args must be a instance of str or argparse.Namespace, not '{}'".format(str(type(args))))

    if args['X']:
        args['execute'] = True
        args['timestamp'] = True
        args['watch'] = True

    if args['T']:
        args['timer'] = True
        args['timestamp'] = True
        args['watch'] = True

    if args['watch']:
        args['timestamp'] = True

    args['watch_stats'] = {'counter': 0, 'errors': 0, 'compiles': 0, 'polls': 0}
    args['print_args'] = True

    return args


def cueExtractAndRun(args, file):
    filename = file['file_path']
    if args['execute']:
        holla = run(filename)
    else:
        holla = run(filename, True, 3, 10000, 2)
    return holla


watch_stats_string = "\n...<iterations:{}, compiles:{}, errors:{}, polls:{}>...\n"


def call(commands):
    try:
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        output = traceback.format_exc()
        return {'returncode': 1, 'output': output}

    stdout_bytes, stderr_bytes = process.communicate()
    stdout = stdout_bytes.decode(sys.stdout.encoding)
    stderr = stderr_bytes.decode(sys.stderr.encoding)
    code = process.returncode

    output = ''
    if stdout:
        output += stdout + '\r\n'
    output += stderr

    result = {'returncode': code, 'output': output}
    return result


def multiCall(*commands, dependent=True):
    results = []
    dependent_failed = False

    for command in commands:
        if not dependent_failed:
            result = call(command)
            if (result['returncode'] == 1) and dependent:
                dependent_failed = True
        else:
            result = None
        results.append(result)

    obj = {'returncode': 0, 'output': ''}
    for result in results:
        if not result:
            continue
        elif result['returncode'] == 1:
            obj['returncode'] = 1
        obj['output'] += result['output']
    return obj


def initiateCompilation(args, file):
    commands = finalizeCommands(args, file)
    if not args['concise'] and args['print_args']:
        printCommands(*commands)
        if args['watch']:
            args['print_args'] = False
    response = multiCall(*commands)
    return response


def cytherize(args, file):
    """Used by core to integrate all the pieces of information, and to make sure everything is good to go"""
    if isOutDated(file):
        if isValid(file):
            response = initiateCompilation(args, file)
        else:
            response = {'returncode': WAIT_FOR_FIX, 'output': ''}
    else:
        if args['timestamp']:
            response = {'returncode': SKIPPED_COMPILATION, 'output': ''}
        else:
            response = initiateCompilation(args, file)

    ####################################################################################################################
    ####################################################################################################################

    time.sleep(INTERVAL)
    if response['returncode'] == ERROR_PASSOFF:
        file['stamp_if_error'] = time.time()
        if args['watch']:
            if len(args['filenames']) > 1:
                output = "Error in file: '{}'; Cyther will wait until it is fixed...\n".format(file['file_path'])
            else:
                output = "Cyther will wait for you to fix this error before it tries to compile again...\n"
        else:
            output = "Error in source file, see above\n"

    elif response['returncode'] == SKIPPED_COMPILATION:
        if not args['watch']:
            output = 'Skipping compilation: source file not updated since last compile\n'
        else:
            output = ''

    elif response['returncode'] == WAIT_FOR_FIX:
        output = ''

    elif response['returncode'] == FINE:
        if args['watch']:
            if len(args['filenames']) > 1:
                output = "Compiled the file '{}'\n".format(file['file_path'])
            else:
                output = 'Compiled the file\n'
        else:
            if not args['concise']:
                output = 'Compilation complete\n'
            else:
                output = ''

    else:
        raise CytherError("Unrecognized return value '{}'".format(response['returncode']))

    response['output'] += output

    ####################################################################################################################
    ####################################################################################################################

    condition = response['returncode'] == SKIPPED_COMPILATION and not args['watch']
    if (args['execute'] or args['timer']) and response['returncode'] == FINE or condition:
        ret = cueExtractAndRun(args, file)
        response['output'] += ret['output']

    ####################################################################################################################
    ####################################################################################################################

    if args['watch']:
        if response['returncode'] == FINE or response['returncode'] == ERROR_PASSOFF:
            if response['returncode'] == FINE:
                args['watch_stats']['compiles'] += 1
            else:
                args['watch_stats']['errors'] += 1
            args['watch_stats']['counter'] += 1
            response['output'] += watch_stats_string.format(args['watch_stats']['counter'],
                                                            args['watch_stats']['compiles'],
                                                            args['watch_stats']['errors'],
                                                            args['watch_stats']['polls'])
        else:
            args['watch_stats']['polls'] += 1

    ####################################################################################################################
    ####################################################################################################################

    if args['watch']:
        if response['returncode'] == 1:
            print(response['output'] + '\n')
        else:
            if response['output']:
                print(response['output'])
    else:
        if response['returncode'] == 1:
            if args['error']:
                raise CytherError(response['output'])
            else:
                print(response['output'])
        else:
            print(response['output'])


def core(args):
    """The heart of Cyther, this function controls the main loop"""
    args = processArgs(args)

    numfiles = len(args['filenames'])
    interval = INTERVAL / numfiles
    files = processFiles(args)
    while True:
        for file in files:
            cytherize(args, file)
        if not args['watch']:
            break
        else:
            time.sleep(interval)


def run(filename, timer=False, repeat=3, number=10000, precision=2):
    with open(filename, 'r') as file:
        string = file.read()

    obj = re.findall(pound_extract, string) + re.findall(tripple_extract, string)
    if not obj:
        output = "There was no '@cyther' code collected from the file '{}'\n".format(filename)
        return {'returncode': 0, 'output': output}

    code = ''.join([item + '\n' for item in obj])

    module_directory = os.path.dirname(filename)
    module_name = os.path.splitext(os.path.basename(filename))[0]
    setup_string = setupTemplate.format(module_directory, module_name, '{}')

    if timer:
        string = timerTemplate.format(setup_string, code, repeat, number, precision, '{}')
    else:
        string = setup_string + code

    script = os.path.join(os.path.dirname(__file__), 'script.py')
    with open(script, 'w+') as file:
        file.write(string)

    response = call(['python', script])
    return response


########################################################################################################################
########################################################################################################################

OPERATING_SYSTEM = platform.platform()

IS_WINDOWS = OPERATING_SYSTEM.lower().startswith('windows')

DEFAULT_OUTPUT_EXTENSION = '.pyd' if IS_WINDOWS else '.so'


PYTHON_EXECUTABLE = where('python')
CYTHON_EXECUTABLE = where('cython')
GCC_EXECUTABLE = where('gcc')

INFO = str()
INFO += "\nSystem:"

INFO += "\n\tPython ({}):".format(PYTHON_EXECUTABLE)
INFO += "\n\t\tVersion: {}".format('.'.join(list(VER)))
INFO += "\n\t\tOperating System: {}".format(OPERATING_SYSTEM)
INFO += "\n\t\t\tOS is Windows: {}".format(IS_WINDOWS)
INFO += "\n\t\tDefault Output Extension: {}".format(DEFAULT_OUTPUT_EXTENSION)
INFO += "\n\t\tInstallation Directory: {}".format(sys.exec_prefix)
INFO += '\n'
INFO += "\n\tCython ({}):".format(CYTHON_EXECUTABLE)
INFO += "\n\t{}".format(textwrap.indent(call(['cython', '-V'])['output'], '\t'))

INFO += "\n\tGCC ({}):".format(GCC_EXECUTABLE)
INFO += "\n{}".format(textwrap.indent(call(['gcc', '-v'])['output'], '\t\t'))

__cytherinfo__ = INFO

del INFO

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
epilog = epilog_text.format(__cytherinfo__)
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


def runAsScript():
    args = parser.parse_args()
    core(args)


if __name__ == '__main__':
    raise CytherError('This module is not meant to be run as a script. See cytherize.py for this functionality')
