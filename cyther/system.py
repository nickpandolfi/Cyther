import platform
import sys
import os
import site

import textwrap
import distutils.sysconfig
import distutils.msvccompiler

from .tools import CytherError, where, call, sift
from .definitions import MISSING_INCLUDE_DIRS, MISSING_RUNTIME_DIRS


def dealWithMissingStaticLib(message):
    """
    Deal with the python missing static lib (.a|.so). Currently all this does is raises a helpful error...
    Args:
        message (str): What to pass to a CytherError
    Returns: CytherError
    """
    raise CytherError(message)


def getIncludeAndRuntime():
    """
    A function from distutils' build_ext.py that was updated and changed to ACTUALLY WORK
    Returns (tuple of list): The include and runtime directories Python needs (os dependant)
    """
    include_dirs, library_dirs = [], []

    py_include = distutils.sysconfig.get_python_inc()
    plat_py_include = distutils.sysconfig.get_python_inc(plat_specific=1)

    include_dirs.append(py_include)
    if plat_py_include != py_include:
        include_dirs.append(plat_py_include)

    if os.name == 'nt':
        library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))
        include_dirs.append(os.path.join(sys.exec_prefix, 'PC'))

        MSVC_VERSION = int(distutils.msvccompiler.get_build_version())
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


MAJOR = str(sys.version_info.major)
MINOR = str(sys.version_info.minor)
VER = MAJOR + MINOR

PLATFORM = sys.platform
BASENAME = "python" + distutils.sysconfig.get_python_version()

CYTHONIZABLE_FILE_EXTS = ('.pyx', '.py')

DRIVE, _ = os.path.splitdrive(sys.exec_prefix)
if not DRIVE:
    DRIVE = os.path.normpath('/')

CYTHER_CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.cyther')

INCLUDE_DIRS, RUNTIME_DIRS = getIncludeAndRuntime()

L_OPTION = '-l' + sift(RUNTIME_DIRS)

INCLUDE_STRING = ''
for directory in INCLUDE_DIRS:
    INCLUDE_STRING += '-I' + directory


RUNTIME_STRING = ''
for directory in RUNTIME_DIRS:
    RUNTIME_STRING += '-L' + directory


if not INCLUDE_DIRS:
    raise CytherError(MISSING_INCLUDE_DIRS)

if not RUNTIME_DIRS:
    dealWithMissingStaticLib(MISSING_RUNTIME_DIRS)


OPERATING_SYSTEM = platform.platform()

IS_WINDOWS = OPERATING_SYSTEM.lower().startswith('windows')

DEFAULT_OUTPUT_EXTENSION = '.pyd' if IS_WINDOWS else '.so'


PYTHON_EXECUTABLE = where('python')
CYTHON_EXECUTABLE = where('cython')
GCC_EXECUTABLE = where('gcc')
CYTHERIZE_SCRIPT = where('cytherize.py')

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

INFO += "\n\tCyther ({}):".format(CYTHERIZE_SCRIPT)
INFO += "\n\t\tIncludable Header Search Command: {}".format(INCLUDE_STRING)
INFO += "\n\t\tRuntime Library Search Command: {}".format(RUNTIME_STRING)
INFO += "\n\t\tRuntime Library Name: {}".format(L_OPTION)
INFO += "\n"
INFO += "\n\tGCC ({}):".format(GCC_EXECUTABLE)
INFO += "\n{}".format(textwrap.indent(call(['gcc', '-v'])['output'].splitlines()[-1], '\t\t'))
INFO += "\n"