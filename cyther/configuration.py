
"""
This module holds the necessary definitions to make and find config files which
hold critical data about where different compile-critical directories exist.
"""

import os

from .files import path, USER
from .searcher import find
from .tools import read_dict_from_file, write_dict_to_file,\
    get_input, get_choice
from .definitions import CONFIG_FILE_NAME, VER, DOT_VER


class DirectoryError(Exception):
    """A custom error used to denote an error with a system of directories"""
    no_include = "No include directory found for this version of python"
    no_default = "There appears to be no default include directory; Cyther " \
                 "was not able to find a suitable directory to default to"

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
    return (VER in include_path) or (DOT_VER in include_path)


def _filter_include_dirs(include_dirs):
    filtered_dirs = []
    for include_path in include_dirs:
        if _check_include_dir_identity(include_path):
            filtered_dirs.append(include_path)
    return filtered_dirs


INCLUDE_PROMPT = "Choose the number of one of the listed include directories" \
                 " above, or enter 'default' to do what Cyther thinks is best"


def _make_include_dirs(*, guided):
    unfiltered_dirs = find(['include', 'Python.h'], content="Py_PYTHON_H")
    filtered_dirs = _filter_include_dirs(unfiltered_dirs)

    if not filtered_dirs:
        raise DirectoryError(DirectoryError.no_include)
    elif len(filtered_dirs) == 1:
        return filtered_dirs[0]
    elif not guided:
        # Be indecisive if multiple valid directories are found
        raise Exception()
    else:
        return get_choice(INCLUDE_PROMPT, filtered_dirs)


def _make_runtime_dirs(*, guided):
    runtime_filename = _make_full_runtime()
    runtime_dirs = find(runtime_filename)

    single_runtime = None
    for r in runtime_dirs:
        if not single_runtime:
            single_runtime = r
        else:
            if not guided:
                raise Exception()

    if guided:
        single_runtime = get_choice(runtime_dirs, single_runtime)
    else:
        if not single_runtime:
            raise DirectoryError(DirectoryError.none)

    return single_runtime


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


def make_config(guided=False):
    """
    Options: --auto, --guided, --manual
    Places for the file: --inplace, --user
    """
    config_path = _make_config_location(guided=guided)

    config_data = make_config_data(guided=guided)

    write_config_file(config_path, config_data)


def generate_configurations(*, guided=False, fresh_start=False, save=False):
    """
    Use 'get_config' to find a configuration file
    If not found, then generate it on the fly, and return it
    """
    loaded_status, loaded_data = get_config()
    if loaded_status != CONFIG_VALID:
        config_data = make_config_data(guided=guided)
    else:
        config_data = loaded_data

    return config_data


def test():
    #print(get_config())
    #print(generate_configurations(guided=False))
    print(get_choice('Yo', ['a', 'b', 'c']))
