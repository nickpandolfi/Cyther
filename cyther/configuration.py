
"""
This module holds the necessary definitions to make and find config files which
hold critical data about where different compile-critical directories exist.
"""

import os

from .files import path, USER
from .tools import read_dict_from_file, write_dict_to_file, getResponse

CONFIG_FILE_NAME = '.cyther_config'

INCLUDE_DIRS_KEY = 'include_search_directory'
RUNTIME_DIRS_KEY = 'runtime_search_directory'
RUNTIME_KEY = 'runtime_libraries'


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


def check_exists(obj, check_function):
    if isinstance(obj, str):
        obj = (obj,)

    result = True
    for item in obj:
        if not check_function(item):
            result = False

    return result


KEY_MISSING = "Key '{}' is missing"


def check_keys_values(config_data, necessary_keys):
    keys = list(config_data.keys())
    problems = []
    is_valid = True

    for key in necessary_keys:
        keys.remove(key)
        if keys.count(key) != 1:
            is_valid = False
            problems.append((key, KEY_MISSING.format(key)))
        elif key == INCLUDE_DIRS_KEY:
            include_dirs_path = path(config_data[key])
            if not os.path.isdir(include_dirs_path):
                is_valid = False
                problems.append((key, "Dir"))
            # Check for Python.h and other main files
            pass
        elif key == RUNTIME_DIRS_KEY:
            # Check that it exists
            pass
        elif key == RUNTIME_KEY:
            # Check that the runtime pattern specified is in RUNTIME_DIRS
            pass
        else:
            pass

    if keys:
        problems.append(())

    return True


PYTHON_KEYS = (INCLUDE_DIRS_KEY, RUNTIME_DIRS_KEY, RUNTIME_KEY)


def check_config_fields(config_data):
    """
    Extracts the data in the config_data object passed in with a high level
    'prompt' argument. For example, 'python' will return all the data necessary
    to compile python, including the runtime and include directories. If prompt
    is not provided, then it will check for baseline minimum to work
    """

    necessary_keys = PYTHON_KEYS
    is_valid, problems = check_keys_values(config_data, necessary_keys)


def make_config_manual():
    """
    Ask for runtime directory
    Ask for runtime name
    Ask for include directory
    """
    return


def make_config():
    """
    Options: --auto, --guided, --manual
    Places for the file: --inplace, --user

    If get_config_file finds a file, what do we want to do?

    Print a message to display correct example usage
    """
    pass


CONFIG_NOT_FOUND = 'cnf'
CONFIG_NOT_VALID = 'cnv'
INVALID_OR_MISSING = "Invalid or missing data fields detected in config file"


def get_config():
    """
    Get the config data structure that is supposed to exist
    """
    config_path = find_config_file()
    if not config_path:
        return CONFIG_NOT_FOUND

    try:
        config_data = read_config_file(config_path)
    except Exception as error:
        return CONFIG_NOT_VALID, error

    valid = check_config_fields(config_data)
    if not valid:
        return CONFIG_NOT_VALID, INVALID_OR_MISSING

    return config_data
