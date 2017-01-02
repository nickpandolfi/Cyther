
import os
import sys

import site
import distutils.sysconfig
import distutils.msvccompiler

from .tools import CytherError
from .definitions import DOT_VER

PLATFORM = sys.platform
BASENAME = "python" + DOT_VER


def get_direct_config():
    """
    Get the basic config data to compile python, by generating it directly
    """
    include_dirs, runtime_dirs = getIncludeAndRuntime()
    runtime = BASENAME
    return include_dirs, runtime_dirs, runtime


def dealWithMissingStaticLib(message):
    """
    Deal with the python missing static lib (.a|.so). Currently all this does
    is raises a helpful error...
    """
    raise CytherError(message)


def getIncludeAndRuntime():
    """
    A function from distutils' build_ext.py that was updated and changed
    to ACTUALLY WORK
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
            library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VS14',
                                             'win32release'))
        elif MSVC_VERSION == 9:
            suffix = '' if PLATFORM == 'win32' else PLATFORM[4:]
            new_lib = os.path.join(sys.exec_prefix, 'PCbuild')
            if suffix:
                new_lib = os.path.join(new_lib, suffix)
            library_dirs.append(new_lib)
        elif MSVC_VERSION == 8:
            library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VS8.0',
                                             'win32release'))
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
            library_dirs.append(os.path.join(sys.prefix, "lib", BASENAME,
                                             "config"))
        else:
            library_dirs.append(os.getcwd())

    if (is_linux or is_gnu or is_sunos) and is_shared:
        if sys.executable.startswith(os.path.join(sys.exec_prefix, "bin")):
            library_dirs.append(distutils.sysconfig.get_config_var('LIBDIR'))
        else:
            library_dirs.append(os.getcwd())

    user_include = os.path.join(site.USER_BASE, "include")
    user_lib = os.path.join(site.USER_BASE, "lib")
    if os.path.isdir(user_include):
        include_dirs.append(user_include)
    if os.path.isdir(user_lib):
        library_dirs.append(user_lib)

    ret_object = (include_dirs, library_dirs)
    _filter_non_existing_dirs(ret_object)

    return ret_object


def _filter_non_existing_dirs(ret_object):
    for x, obj in enumerate(ret_object):
        for y, item in enumerate(obj):
            if not os.path.isdir(item):
                del ret_object[x][y]
