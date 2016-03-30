# coding=utf-8

import os, sys, subprocess
import argparse, platform
import time

from shutil import which


CYTHER_FAIL = 0
CYTHER_SUCCESS = 1
ERROR_PASSOFF = -3
INTERVAL = .25

CYTHONIZABLE_FILE_EXTS = ('.pyx', '.py')

PLEASE_ADD = ", please add it to the system's path"
NOT_NEEDED_MESSAGE = "Module '{}' does not have to be included, or has no .get_include() method"

LIB_A_MISSING_MESSAGE = '''
Currently, cyther does not support the automatic construction of 'libpython{0}.a',
so you will have to do it yourself. There are several tools that can help you with
this, including dlltool, gendef, pexport, reimp. All of which are a part of mingw32.

The general idea is to first look into the python{0}.dll and figure out all the
objects that belong to that file. Then, take the names of these objects, and put
them in a .def file. Take this file, and pass it to dll tool to tell it what to
extract from the python{0}.dll and inject into the libpython{0}.a static library.
'''


ASSUMPTIONS = """
Assumptions cyther makes about your system:
1) Cython and gcc are both installed, and accessible from the system console
2) Your environment path variable is able to be found by `shutil.which`
3) gcc can work with the option -l pythonXY (libpythonXY.a exists in your python libs directory)
4) Almost any gcc compiled C program will work on Windows
"""


class CytherError(Exception):
    """A helpful custom error to be called when a general python error just doesn't make sense in context"""
    def __init__(self, *args, **kwargs):
        super(CytherError, self).__init__(*args, **kwargs)


def where(cmd, mode=os.X_OK, path=None):
    """This function will wrap the shutil.which function to return the abspath every time, or a empty string"""
    raw_result = which(cmd, mode, path)
    if raw_result:
        return os.path.abspath(raw_result)
    else:
        return ''


def dealWithLibA(direc, message):
    """What to do if the libpythonXY.a is missing. Currently, it raises an error, and prints a helpful message"""
    raise CytherError("The file '{}' does not exist.\n\n{}".format(direc, message))


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
                print('dirname: {}'.format(dirname))
                if os.path.exists(dirname):
                    file['output_name'] = output_name
                else:
                    raise CytherError('The directory specified to write the output file in does not exist')
        else:
            file['output_name'] = file['no_extension'] + DEFAULT_OUTPUT_EXTENSION

        file['stamp_if_error'] = 0
        to_process.append(file)
    return to_process


def isOutDated(file):
    """Figures out if Cyther should compile the given file. For use with the -t option"""
    if os.path.exists(file['output_name']):
        source_time = os.path.getmtime(file['file_path'])
        output_time = os.path.getmtime(file['output_name'])
        if source_time > output_time:
            return True
    else:
        return True
    return False


def makeCommands(preset, file):
    """Given a high level preset, it will construct the basic args to pass over. 'ninja', 'beast', and 'minimal'"""
    if not preset:
        preset = 'ninja'

    if preset == 'ninja':
        cython_command = ['cython', '-a', '-p', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-shared', '-w', '-O3', '-I', INCLUDE_DIRECTORY, '-L', LIBS_DIRECTORY, '-o',
                       file['output_name'], file['c_name'],
                       '-l', LIB_A_NAME]
    elif preset == 'beast':
        cython_command = ['cython', '-a', '-l', '-p', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-shared', '-Wall', '-O3', '-I', INCLUDE_DIRECTORY, '-L', LIBS_DIRECTORY, '-o',
                       file['output_name'],
                       file['c_name'], '-l', LIB_A_NAME]
    elif preset == 'minimal':
        cython_command = ['cython', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-shared', '-I', INCLUDE_DIRECTORY, '-L', LIBS_DIRECTORY, '-o', file['output_name'],
                       file['c_name'], '-l', LIB_A_NAME]
    else:
        raise CytherError("The preset '{}' is not supported".format(preset))

    return cython_command, gcc_command


def printCommands(commands):
    """Simply prints all of the commands on screen for the user to see. Nice for debugging."""
    print(' '.join(commands).strip())


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


def callCompilers(args, commands, actions):
    """The function where the actual compilation takes place"""
    for command, action in zip(commands, actions):
        ret = subprocess.call(command)
        if ret:
            if ret != 1:
                string = str(ret)
            else:
                string = ''
            if args['watch']:
                print(string)
                return ERROR_PASSOFF
            else:
                raise CytherError(string)
    return CYTHER_SUCCESS


def cytherize(args, file, print_command):
    """Used by core to integrate all the pieces of information, and to make sure everything is good to go"""
    cython_commands, gcc_commands = makeCommands(args['preset'], file)

    cython_pass_off = convertToDashes(args['cython_args'])
    gcc_pass_off = convertToDashes(args['gcc_args'])

    filterCommands(cython_pass_off, cython_commands)
    filterCommands(gcc_pass_off, gcc_commands)

    dirs = getDirsToInclude(args['include'])
    gcc_commands.extend(dirs)

    if print_command:
        printCommands(cython_commands)
        printCommands(gcc_commands)

    response = callCompilers(args, (cython_commands, gcc_commands), ('cython', 'gcc'))
    return response


def convertArgs(args):
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
    return args


def core(args):
    """The heart of Cyther, this function controls the main loop"""
    args = convertArgs(args)

    numfiles = len(args['filenames'])
    interval = INTERVAL / numfiles
    files = processFiles(args)
    if not args['timestamp'] and args['watch']:
        args['timestamp'] = True
    counter = 1
    should_i_print = True
    while True:
        for file in files:
            if args['timestamp']:
                modified_time = os.path.getmtime(file['file_path'])
                no_error = modified_time > file['stamp_if_error']
                if isOutDated(file) and no_error:
                    if args['watch']:
                        if len(args['filenames']) > 1:
                            print("Compiling the file '{}'".format(file['file_path']))
                        else:
                            print('Compiling the file')
                    print('')
                    ret = cytherize(args, file, should_i_print)
                    should_i_print = False
                    if ret == ERROR_PASSOFF:
                        file['stamp_if_error'] = time.time()
                    if args['watch']:
                        print("\n...<count:{}>...\n".format(counter))
                        counter += 1
                else:
                    if not args['watch']:
                        if len(args['filenames']) > 1:
                            print("Skipping the file '{}'".format(file['file_path']))
                        else:
                            print('Skipping compilation')
                    else:
                        pass
                    continue
            else:
                cytherize(args, file, should_i_print)
        if not args['watch']:
            break
        else:
            time.sleep(interval)


INFO = str()

INFO += "\nSystem:"

OPERATING_SYSTEM = platform.platform().split('-')[0]
INFO += "\n\tOperating System: {}".format(OPERATING_SYSTEM)
IS_WINDOWS = OPERATING_SYSTEM == 'Windows'
INFO += "\n\t\tOS is Windows: {}".format(IS_WINDOWS)
DLL_EXTENSION = '.dll' if IS_WINDOWS else '.so'
INFO += "\n\tLinked Library Extension: {}".format(DLL_EXTENSION)
DEFAULT_OUTPUT_EXTENSION = '.pyd' if IS_WINDOWS else '.so'
INFO += "\n\tDefault Output Extension: {}".format(DEFAULT_OUTPUT_EXTENSION)

INFO += "\nPython:"

python_found = where('python')
if not python_found:
    raise CytherError("Python is not able to be called, please add it to the system's path")

VER = str(sys.version_info.major) + str(sys.version_info.minor)
INFO += "\n\tVersion: {}".format('.'.join(list(VER)))

LIB_A_MISSING_MESSAGE = LIB_A_MISSING_MESSAGE.format(VER)

PYTHON_DIRECTORY = sys.exec_prefix
PYTHON_DIRECTORY_EXISTS = os.path.exists(PYTHON_DIRECTORY)
if not PYTHON_DIRECTORY_EXISTS:
    raise CytherError("The Python main installation directory doesn't exist")
INFO += "\n\tInstallation Directory: {}".format(PYTHON_DIRECTORY)
INFO += "\n\t\tExists: {}".format(PYTHON_DIRECTORY_EXISTS)

LIBS_DIRECTORY = os.path.normpath(os.path.join(PYTHON_DIRECTORY, 'libs'))
LIBS_DIRECTORY_EXISTS = os.path.exists(LIBS_DIRECTORY)
if not LIBS_DIRECTORY_EXISTS:
    raise CytherError("The Python 'libs' directory doesn't exist")
INFO += "\n\tDirectory 'libs': {}".format(LIBS_DIRECTORY)
INFO += "\n\t\tExists: {}".format(LIBS_DIRECTORY_EXISTS)

INCLUDE_DIRECTORY = os.path.normpath(os.path.join(PYTHON_DIRECTORY, 'include'))
INCLUDE_DIRECTORY_EXISTS = os.path.exists(INCLUDE_DIRECTORY)
if not INCLUDE_DIRECTORY_EXISTS:
    raise CytherError("The Python 'include' directory doesn't exist")
INFO += "\n\tDirectory 'include': {}".format(INCLUDE_DIRECTORY)
INFO += "\n\t\tExists: {}".format(INCLUDE_DIRECTORY_EXISTS)

LIB_A_NAME = 'python' + VER
LIB_A = 'lib' + LIB_A_NAME + '.a'
LIB_A_DIRECTORY = os.path.normpath(os.path.join(LIBS_DIRECTORY, LIB_A))
LIB_A_DIRECTORY_EXISTS = os.path.exists(LIB_A_DIRECTORY)
if not LIB_A_DIRECTORY_EXISTS:
    dealWithLibA(LIB_A_DIRECTORY, LIB_A_MISSING_MESSAGE)
INFO += "\n\tLibrary '.a' Directory: {}".format(LIB_A_DIRECTORY)
INFO += "\n\t\tExists: {}".format(LIB_A_DIRECTORY_EXISTS)

DLL_NAME = LIB_A_NAME + DLL_EXTENSION
DLL_LOCATION = where(DLL_NAME)
DLL_EXISTS = os.path.exists(DLL_LOCATION)

DLL_DIRECTORY = os.path.normpath(DLL_LOCATION)
INFO += "\n\tPython '{}' Directory: {}".format(DLL_EXTENSION, DLL_LOCATION)
INFO += "\n\t\tExists: {}".format(DLL_EXISTS)

cython_found = where('cython')
if not cython_found:
    try:
        import cython
        raise CytherError("Cython exists and is able to be imported by Python, but is unable to be called" + PLEASE_ADD)
    except ImportError:
        raise CytherError("Cython is unable to be imported, and is probably not installed")

gcc_found = where('gcc')
if not gcc_found:
    raise CytherError("gcc is not able to be called" + PLEASE_ADD)

__cytherinfo__ = INFO

del INFO

help_filenames = 'The Cython source files'
help_preset = 'The preset options for using cython and gcc (ninja, verbose, beast)'
help_timestamp = 'If this flag is provided, cyther will not compile files that have a modified' \
                 'time before that of your compiled .pyd or .so files'
help_output_name = 'Change the name of the output file, default is basename plus .pyd'
help_include = 'The names of the python modules that have an include library that needs to be passed to gcc'
help_assumptions = 'Print the list of assumptions cyther makes about your system before running'
help_local = 'When not flagged, builds in __cythercache__, when flagged, it builds locally in the same directory'
help_watch = "When given, cyther will watch the directory with the 't' option implied and compile," \
             "when necessary, the files given"
help_cython = "Arguments to pass to Cython (use '_' or '__' instead of '-' or '--'"
help_gcc = "Arguments to pass to gcc (use '_' or '__' instead of '-' or '--'"

description_text = 'Auto compile and build .pyx files in place.\n{}\n{}'

parser = argparse.ArgumentParser(description=description_text.format(ASSUMPTIONS, __cytherinfo__),
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 usage='cyther [options] input_file')
parser.add_argument('filenames', action='store', nargs='+', help=help_filenames)
parser.add_argument('-p', '--preset', action='store', default='', help=help_preset)
parser.add_argument('-t', '--timestamp', action='store_true', default=False, help=help_timestamp)
parser.add_argument('-o', '--output_name', action='store', help=help_output_name)
parser.add_argument('-i', '--include', action='store', default='', help=help_include)
parser.add_argument('-l', '--local', action='store_true', dest='local', default=False, help=help_local)
parser.add_argument('-w', '--watch', action='store_true', dest='watch', default=False, help=help_watch)
parser.add_argument('-cython', action='store', nargs='+', dest='cython_args', default=[], help=help_cython)
parser.add_argument('-gcc', action='store', nargs='+', dest='gcc_args', default=[], help=help_gcc)


def runAsScript():
    args = parser.parse_args()
    core(args)


if __name__ == '__main__':
    raise CytherError('This module is not meant to be run as a script. See cytherize.py for this functionality')
