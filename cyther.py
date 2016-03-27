# coding=utf-8
# auto defenestration is key

"""
Cyther: The Cross Platform Cython/Python Compiler

We all know the beauties of Cython:
    1) Writing C extensions is as easy as Python
    2) Almost any valid Python is valid Cython, as Cython is a superset of Python
    3) It has the readability of Python, but the speed of C
    4) Minimal effort has to be taken in order to speed up some programs by three to four orders of magnitude


However, compiling is not always easy. There are a few places that disutils' 'setup.py' can get tripped up.
    1) vcvarsall.bat not found error
    2) gcc: undefined reference to...
    3) Other errors basically referring to 'compiler not found'


Cython may be almost as easy to write as Python, but sometimes nowhere near the level of easiness that it
takes to run Python. This is where Cyther comes into play. Cyther is an attempt at a cross platform compiler
that wields both the standard cython compiler and gcc to make sure that these errors don't happen.


Cyther is extremely easy to use. One can call cyther.py from the command line, or import `core` on the
module level, then call that. Here are a few examples of Cyther's features:

        from cyther import core
        core('cython_file.pyx')

    same can be done with:

        C:/Python35> cyther cython_file.pyx

    Here are some neat little option examples:

        from cyther import core
        core('python_file.py -t -l')
        # -t means that cyther will not compile it if the source file is not older than the compiled file
        # -l means that cyther will build locally, if not given, it builds in __cythercache__

    Perhaps the most useful feature of Cyther:

        from cyther import core
        core('cython_file.pyx -w')

    This `-w` command means that cyther will keep looking at that file indefinitely and whenever it sees a change
    in the source code, it will automatically compile it without the user having to do anything. Here is the
    output of the -w option in the command line and stdout:

        Compiling the file 'D:\python\notes.py'

        cython -a -p -o D:\python\notes.c D:\python\notes.py -l

        gcc -shared -w -O3 -I D:\Python35\include -L D:\Python35\libs
            -o D:\python\notes.pyd D:\python\notes.c -l python35

        ...<count:1>...

        Compiling the file 'D:\python\test.pyx'

        ...<count:2>...

        Compiling the file 'D:\python\test.pyx'

        ...<count:3>...

        Compiling the file 'D:\python\test2.pyx'

        ...<count:4>...


    Keep in mind that anything that you pass to core, you can also pass to cyther from the command line. Now,
    try to meditate on this command:

        C:/Python35> cyther cython_file.pyx python_file.py test.pyx -w -l -o something -cython _l

    This command will compile these three files, then proceed to watch them continuously, and if they change,
    they will be recompiled. Also, their .c and .a files will be built in the same directory. Even further,
    we pass the option _l (-l) to cython, which will create listing files for the three files specified.
    Notice that we put a -o option, when in reality this makes no sense. Cyther knows this and will erase this
    option before it goes to compile, so the files will not be compiled under the same name. To get an idea
    of what Cyther is currently capable of, type `core('-h')` or `cyther -h` from the command line.


Cyther isn't quite perfect yet, so all the incompatabilities and assumptions that Cyther makes are listed
below. We strongly recommend that you look them over before even touching the download button. In the
near future we hope to make Cyther as polished as possible, and bring the list of assumptions listed below
to a minimum. There are even plans in the works to be able to automatically recompile shared object libraries
that are entirely missing on one's system; critical to Cython compilation.


Assumptions cyther makes about your system:
    1) Your environment path variable is able to be found by `shutil.which`
    2) gcc can work with the option -l pythonXY (libpythonXY.a exists in your libs directory)
    3) Almost any gcc compiled C program will work on Windows


Hey you! Yes you. If you notice any bugs or peculiarities, please report them to our bug tracker, it will
help us out a lot:
    <LINK FOR BUG TRACKING>

If you have any questions or concerns, or even any suggestions, don't hesitate to contact me at:
    npandolfi@wpi.edu

Happy compiling!!

Tags: Cyther, antibug, vcvarsall.bat, MinGW32, Python, Cython, Python 3.x, compiler, command-line, script
user-friendly, setup.py, gcc
"""

import os, sys, subprocess
import argparse, platform, errno
import time

from shutil import which

__author__ = 'Nicholas C. Pandolfi'

__version__ = '0.3.5'

__license__ = '''
Copyright (c) 2016 Nicholas C. Pandolfi ALL RIGHTS RESERVED (MIT)

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall
be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
'''


__all__ = ['CytherError', '_make_directory', 'core', 'where']


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
1) Your environment path variable is able to be found by `shutil.which`
2) gcc can work with the option -l pythonXY (libpythonXY.a exists in your libs directory)
3) Almost any gcc compiled C program will work on Windows
"""


class CytherError(Exception):
    """A helpful custom error to be called when a general python error just doesn't make sense in context"""
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def where(cmd, mode=os.X_OK, path=None):
    raw_result = which(cmd, mode, path)
    if raw_result:
        return os.path.abspath(raw_result)
    else:
        return ''


def deal_with_lib_a(direc, message):
    """What to do if the libpythonXY.a is missing. Currently, it raises an error, and prints a helpful message"""
    raise CytherError("The file '{}' does not exist.\n\n{}".format(direc, message))


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
    deal_with_lib_a(LIB_A_DIRECTORY, LIB_A_MISSING_MESSAGE)
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


def _make_directory(directory):
    """A attempt at a raceless make directory function. Should be as safe as possible"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise


def _get_full_path(filename):
    """This will get the full path of a path of a filename"""
    if os.path.exists(filename) and (filename not in os.listdir(os.getcwd())):
        ret = filename
    elif os.path.exists(os.path.join(os.getcwd(), filename)):
        ret = os.path.join(os.getcwd(), filename)
    else:
        raise CytherError("The file '{}' does not exist".format(filename))
    return ret


def _process_files(args):
    """Generates and error checks each file's information before the compilation actually starts"""
    to_process = []
    for filename in args['filenames']:
        file = dict()
        file['file_path'] = _get_full_path(filename)
        file['file_base_name'] = os.path.splitext(os.path.basename(file['file_path']))[0]
        file['no_extension'], file['extension'] = os.path.splitext(file['file_path'])
        if file['extension'] not in CYTHONIZABLE_FILE_EXTS:
            raise CytherError("The file '{}' is not a designated cython file".format(file['file_path']))
        base_path = os.path.dirname(file['file_path'])
        local_build = args['local']
        if not local_build:
            cache_name = os.path.join(base_path, '__cythercache__')
            _make_directory(cache_name)
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


def _should_compile(file):
    """Figures out if Cyther should compile the given file. For use with the -t option"""
    if os.path.exists(file['output_name']):
        source_time = os.path.getmtime(file['file_path'])
        output_time = os.path.getmtime(file['output_name'])
        if source_time > output_time:
            return True
    else:
        return True
    return False


def _commands_from_preset(preset, file):
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


def _print_commands(commands):
    """Simply prints all of the commands on screen for the user to see. Nice for debugging."""
    print(' '.join(commands).strip())


def _underscores_to_dashes(commands):
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


def _filter_passoff_commands(pass_off_commands, commands):
    """Puts items of pass_off_commands in commands if commands does not already have them"""
    if pass_off_commands:
        for item in pass_off_commands:
            if item[0] == '-':
                if item not in commands:
                    commands.append(item)


def _extract_inc_dirs(obj):
    """Used by _include_directories. Does some nice error checking and splitting and stripping. Cleans up."""
    results = []
    modules = obj.strip().split('-')
    for m in modules:
        try:
            exec('import {}'.format(m))
        except ImportError:
            raise CytherError("The module '{}' does not exist".format(m))
        try:
            results.append(eval(m).get_include())
        except AttributeError:
            print(NOT_NEEDED_MESSAGE.format(m))
    return results


def _include_directories(modules):
    """Given a string of module names, it will return the 'include' directories essential to their compilation"""
    dirs = []
    if modules:
        for path in _extract_inc_dirs(modules):
            dirs.append('-I {}'.format(path))
    return dirs


def _cytherize(args, commands, actions):
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


def _integrate(args, file, print_command):
    """Used by core to integrate all the pieces of information, and to make sure everything is good to go"""
    cython_commands, gcc_commands = _commands_from_preset(args['preset'], file)

    cython_pass_off = _underscores_to_dashes(args['cython_args'])
    gcc_pass_off = _underscores_to_dashes(args['gcc_args'])

    _filter_passoff_commands(cython_pass_off, cython_commands)
    _filter_passoff_commands(gcc_pass_off, gcc_commands)

    dirs = _include_directories(args['include'])
    gcc_commands.extend(dirs)

    if print_command:
        _print_commands(cython_commands)
        _print_commands(gcc_commands)

    response = _cytherize(args, (cython_commands, gcc_commands), ('cython', 'gcc'))
    return response


def _string_to_dictionary(string):
    """changes a command line string to a dictionary"""
    unprocessed = string.strip().split(' ')
    if unprocessed[0] == 'cyther':
        del unprocessed[0]
    namespace = parser.parse_args(unprocessed).__dict__
    return namespace


def core(args):
    """The heart of Cyther, this function controlls the main loop"""
    if isinstance(args, str):
        args = _string_to_dictionary(args)
    elif isinstance(args, argparse.Namespace):
        args = args.__dict__
    else:
        raise CytherError("Args must be a instance of str or argparse.Namespace, not '{}'".format(str(type(args))))

    numfiles = len(args['filenames'])
    interval = INTERVAL / numfiles
    files = _process_files(args)
    if not args['timestamp'] and args['watch']:
        args['timestamp'] = True
    counter = 1
    should_i_print = True
    while True:
        for file in files:
            if args['timestamp']:
                modified_time = os.path.getmtime(file['file_path'])
                no_error = modified_time > file['stamp_if_error']
                if _should_compile(file) and no_error:
                    if args['watch']:
                        if len(args['filenames']) > 1:
                            print("Compiling the file '{}'".format(file['file_path']))
                        else:
                            print('Compiling the file')
                    print('')
                    ret = _integrate(args, file, should_i_print)
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
                _integrate(args, file, should_i_print)
        if not args['watch']:
            break
        else:
            time.sleep(interval)

def test():
    core('test.pyx -w')


if __name__ == '__main__':
    command_line_args = parser.parse_args()
    core(command_line_args)
