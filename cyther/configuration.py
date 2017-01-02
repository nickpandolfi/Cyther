
"""
This module holds the necessary definitions to make and find config files which
hold critical data about where different compile-critical directories exist.
"""

import os

from .pathway import path, USER
from .searcher import find
from .tools import read_dict_from_file, write_dict_to_file,\
    get_input, get_choice
from .definitions import CONFIG_FILE_NAME, VER, DOT_VER


class DirectoryError(Exception):
    """A custom error used to denote an error with a system of directories"""
    should_be_guided = "If this is the case, please DO run in guided mode so" \
                       " you can manually choose which one you wish to use"
    no_include_dirs = "No include directory found for this version of Python"
    multiple_include = "Multiple include directories were found for this " \
                       "version of Python. " + should_be_guided

    no_runtime_dirs = "No runtime library search directories were found for" \
                      " this version of Python"
    multiple_runtime_dirs = "Multiple runtime search directories were found " \
                            "for this version of Python. " + should_be_guided

    def __init__(self, *args, **kwargs):
        super(DirectoryError, self).__init__(*args, **kwargs)


INCLUDE_DIRS_KEY = 'include_search_directory'
RUNTIME_DIRS_KEY = 'runtime_search_directory'
RUNTIME_KEY = 'runtime_libraries'


# TODO What about the __file__ attribute
# TODO Make this automatic if 'numpy' is seen in the source code?
def getDirsToInclude(string):
    """
    Given a string of module names, it will return the 'include' directories
    essential to their compilation as long as the module has the conventional
    'get_include' function.
    """
    dirs = []
    a = string.strip()
    obj = a.split('-')

    if len(obj) == 1 and obj[0]:
        for module in obj:
            try:
                exec('import {}'.format(module))
            except ImportError:
                raise FileNotFoundError("The module '{}' does not"
                                        "exist".format(module))
            try:
                dirs.append('-I{}'.format(eval(module).get_include()))
            except AttributeError:
                print(NOT_NEEDED_MESSAGE.format(module))
    return dirs


def purge_configs():
    """
    These will delete any configs found in either the current directory or the
    user's home directory
    """
    user_config = path(CONFIG_FILE_NAME, root=USER)
    inplace_config = path(CONFIG_FILE_NAME)

    if os.path.isfile(user_config):
        os.remove(user_config)

    if os.path.isfile(inplace_config):
        os.remove(inplace_config)


def write_config_file(file_path, data):
    """
    Writes a config data structure (dict for now) to the file path specified
    """
    write_dict_to_file(file_path, data)


def read_config_file(file_path):
    """
    Reads a config data structure (dict for now) from the file path specified
    """
    return read_dict_from_file(file_path)


def find_config_file():
    """
    Returns the path to the config file if found in either the current working
    directory, or the user's home directory. If a config file is not found,
    the function will return None.
    """
    local_config_name = path(CONFIG_FILE_NAME)
    if os.path.isfile(local_config_name):
        return local_config_name
    else:
        user_config_name = path(CONFIG_FILE_NAME, root=USER)
        if os.path.isfile(user_config_name):
            return user_config_name
        else:
            return None


CONFIG_NOT_FOUND = 'cnf'
CONFIG_NOT_VALID = 'cnv'
CONFIG_VALID = 'cv'


def get_config():
    """
    Get the config data structure that is supposed to exist in the form:
        (Status, Data)
    """
    config_path = find_config_file()
    if not config_path:
        return CONFIG_NOT_FOUND, None

    try:
        config_data = read_config_file(config_path)
    except Exception as error:
        return CONFIG_NOT_VALID, error

    return CONFIG_VALID, config_data


BOTH_CONFIGS_EXIST = "Config files exist both in the current directory, and " \
                     "the user's directory. Specifying either would result " \
                     "in one being overwriten\n"

USER_CONFIG_EXISTS = "There is a config file in the user's directory, but " \
                     "not in the current directory; making a config in " \
                     "user's would overwrite the existing one\n"

INPLACE_CONFIG_EXISTS = "There is a config file in the current directory, " \
                        "but not in the user's directory; making a config " \
                        "inplace would overwrite the existing one\n"

NO_CONFIGS_EXIST = "No configs were found, it's safe " \
                   "to make the config file anywhere\n"

COMPLEX_PROMPT = "Where do you want to make the config file?"


def _complex_decision(*, guided):
    user = path(CONFIG_FILE_NAME, root=USER)
    inplace = path(CONFIG_FILE_NAME)

    if os.path.isfile(user):
        if os.path.isfile(inplace):
            code = 0
            default = inplace
        else:
            code = 1
            default = user
    else:
        if os.path.isfile(inplace):
            code = 2
            default = inplace
        else:
            code = 3
            default = user

    if guided:
        # Code used to preface the situation to the user on the command line
        if code == 0:
            print(BOTH_CONFIGS_EXIST)
        elif code == 1:
            print(USER_CONFIG_EXISTS)
        elif code == 2:
            print(INPLACE_CONFIG_EXISTS)
        else:
            print(NO_CONFIGS_EXIST)

        # Get the user's response to said situation ^
        response = get_input(COMPLEX_PROMPT,('user', 'inplace', 'default', ''))

        # Decide what to do based on the user's error checked response
        if response == 'user':
            result = user
        elif response == 'inplace':
            result = inplace
        elif response == 'default':
            result = default
        else:
            exit()
            return
    else:
        result = default

    return result, code


SIMPLE_PROMPT = "Do you want to overwrite '{}'?"


def _simple_decision(directory, *, guided):
    config_name = path(CONFIG_FILE_NAME, root=directory)
    if os.path.isfile(config_name):
        if guided:
            response = get_input(SIMPLE_PROMPT.format(config_name), ('y', 'n'))
            if response == 'n':
                exit()
    return config_name


def _make_config_location(*, guided):
    current = path(CONFIG_FILE_NAME)

    if os.path.isdir(path(USER)):
        if path() == path(USER):
            result = _simple_decision(current, guided=guided)
        else:
            result, code = _complex_decision(guided=guided)
    else:
        result = _simple_decision(current, guided=guided)

    return result


# TODO Check this condition... It may not be accurate
def _check_include_dir_identity(include_path):
    condition1 = (VER in include_path) or (DOT_VER in include_path)
    condition2 = 'include' in include_path
    return condition1 and condition2


def _filter_include_dirs(include_dirs):
    filtered_dirs = []
    for include_path in include_dirs:
        if _check_include_dir_identity(include_path):
            filtered_dirs.append(os.path.dirname(include_path))
    return filtered_dirs


INCLUDE_PROMPT = "Choose one of the listed include directories above (by " \
                 "entering the number), or enter nothing to exit the process"


def _make_include_dirs(*, guided):
    unfiltered_dirs = find('Python.h', content="Py_PYTHON_H")
    include_dirs = _filter_include_dirs(unfiltered_dirs)
    print("Filtered dirs: '{}'".format(include_dirs))

    if not include_dirs:
        raise DirectoryError(DirectoryError.no_include_dirs)
    elif len(include_dirs) == 1:
        return include_dirs[0]
    elif not guided:
        # Be indecisive if multiple valid directories are found
        raise DirectoryError(DirectoryError.multiple_include)
    else:
        return get_choice(INCLUDE_PROMPT, include_dirs)


def _filter_runtime_dirs(rumtime_dirs):
    filtered_dirs = []
    for include_path in rumtime_dirs:
        filtered_dirs.append(os.path.dirname(include_path))
    return filtered_dirs


RUNTIME_DIRS_PROMPT = "Choose one of the listed runtime search directories " \
                      "above (by entering the number), or enter nothing to " \
                      "exit the process"


def _make_runtime_dirs(*, guided):
    # Dont need to filter on this one
    unfiltered_dirs = find(_make_full_runtime())
    runtime_dirs = _filter_runtime_dirs(unfiltered_dirs)

    if not runtime_dirs:
        raise DirectoryError(DirectoryError.no_runtime_dirs)
    elif len(runtime_dirs) == 1:
        return runtime_dirs[0]
    elif not guided:
        # Be indecisive if multiple valid dirs are found
        raise DirectoryError(DirectoryError.multiple_runtime_dirs)
    else:
        return get_choice(RUNTIME_DIRS_PROMPT, runtime_dirs)


def _make_full_runtime():
    return 'lib' + _make_runtime() + '.a'


def _make_runtime():
    name = 'python' + VER
    return name


def make_config_data(*, guided):
    """
    Makes the data necessary to construct a functional config file
    """
    config_data = {}
    config_data[INCLUDE_DIRS_KEY] = _make_include_dirs(guided=guided)
    config_data[RUNTIME_DIRS_KEY] = _make_runtime_dirs(guided=guided)
    config_data[RUNTIME_KEY] = _make_runtime()

    return config_data


def make_config_file(guided=False):
    """
    Options: --auto, --guided, --manual
    Places for the file: --inplace, --user
    """
    config_path = _make_config_location(guided=guided)

    config_data = make_config_data(guided=guided)

    write_config_file(config_path, config_data)


# TODO Make errors cascade out to the outside (this is why travis !catching it)
def generate_configurations(*, guided=False, fresh_start=False, save=False):
    """
    If a config file is found in the standard locations, it will be loaded and
    the config data would be retuned. If not found, then generate the data on
    the fly, and return it
    """

    if fresh_start:
        purge_configs()

    loaded_status, loaded_data = get_config()
    if loaded_status != CONFIG_VALID:
        if save:
            make_config_file(guided=guided)
            status, config_data = get_config()
        else:
            config_data = make_config_data(guided=guided)
    else:
        config_data = loaded_data

    return config_data


def test():
    from pprint import pprint
    pprint(generate_configurations(fresh_start=True, guided=True, save=True))
