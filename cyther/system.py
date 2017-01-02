
"""
This module holds most of the 'constants' dealing with information on the
user's system that doesn't change throughout the compilation process

Holds tons of important low level functions and info
"""

import platform
import sys
import os
import textwrap

from .tools import CytherError
from .searcher import where
from .launcher import call
from .definitions import MISSING_INCLUDE_DIRS, MISSING_RUNTIME_DIRS
from .direct import getIncludeAndRuntime


MAJOR = str(sys.version_info.major)
MINOR = str(sys.version_info.minor)
VER = MAJOR + MINOR

CYTHONIZABLE_FILE_EXTS = ('.pyx', '.py')

DRIVE, _ = os.path.splitdrive(sys.exec_prefix)
if not DRIVE:
    DRIVE = os.path.normpath(os.sep)

OPERATING_SYSTEM = platform.platform()

IS_WINDOWS = OPERATING_SYSTEM.lower().startswith('windows')

DEFAULT_OUTPUT_EXTENSION = '.pyd' if IS_WINDOWS else '.so'


PYTHON_EXECUTABLE = where('python')
'''
PYTHON_VERSION = call(['python', '--version'],
                      raise_exception=True).extractVersion()
'''
CYTHON_EXECUTABLE = where('cython')
GCC_EXECUTABLE = where('gcc')

gcc_output = call(['gcc', '-v'], raise_exception=True)
#print("gcc output: '{}'".format(gcc_output))
GCC_INFO = gcc_output.getOutput()
GCC_VERSION = gcc_output.extractVersion()

cython_output = call(['cython', '-V'], raise_exception=True)
#print("cython output: '{}'".format(cython_output))
CYTHON_OUTPUT = cython_output.getOutput()
CYTHON_VERSION = cython_output.extractVersion()

INFO = str()
INFO += "\nSystem:"

# TODO There must be a better way to do this...
INFO += "\n\tPython ({}):".format(PYTHON_EXECUTABLE)
INFO += "\n\t\tVersion: {}".format('.'.join(list(VER)))
INFO += "\n\t\tOperating System: {}".format(OPERATING_SYSTEM)
INFO += "\n\t\t\tOS is Windows: {}".format(IS_WINDOWS)
INFO += "\n\t\tDefault Output Extension: {}".format(DEFAULT_OUTPUT_EXTENSION)
INFO += "\n\t\tInstallation Directory: {}".format(sys.exec_prefix)
INFO += '\n'
INFO += "\n\tCython ({}) ({}):".format(CYTHON_VERSION, CYTHON_EXECUTABLE)
INFO += "\n\t{}".format(textwrap.indent(CYTHON_OUTPUT, '\t'))

INFO += "\n\tCyther:"
INFO += "\n\t\tIncludable Header Search Command: {}".format('')
INFO += "\n\t\tRuntime Library Search Command: {}".format('')
INFO += "\n\t\tRuntime Library Name(s): {}".format('')
INFO += "\n"
INFO += "\n\tGCC ({}) ({}):".format(GCC_VERSION, GCC_EXECUTABLE)

INFO += "\n{}".format(textwrap.indent(GCC_INFO.splitlines()[-1], '\t\t'))
INFO += "\n"
