
"""
This module holds the necessary definitions to make and find config files which
hold critical data about where different compile-critical directories exist.
"""

import os

from .files import path, USER
from .tools import read_dict_from_file, write_dict_to_file, get_input

CONFIG_FILE_NAME = '.cyther'

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

COMPLEX_PROMPT = "Where do you want to make the config file? " \
                 "[user/inplace/default/''=exit]: "

COMPLEX_REDO_PROMPT = "Incorrect response, must be 'user', 'inplace', " \
                      "'default', or '' (empty) to exit: "


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
        response = get_input(COMPLEX_PROMPT,
                             ('user', 'inplace', 'default', ''),
                             redo_prompt=COMPLEX_REDO_PROMPT)

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

    return result

SIMPLE_PROMPT = "Do you want to overwrite '{}'? [y/n]: "

SIMPLE_REDO_PROMPT = "Incorrect response, must be 'y' or 'n': "


def _simple_decision(directory, *, guided):
    config_name = path(CONFIG_FILE_NAME, root=directory)
    if os.path.isfile(config_name):
        if guided:
            response = get_input(SIMPLE_PROMPT.format(config_name), ('y', 'n'),
                                 redo_prompt=SIMPLE_REDO_PROMPT)
            if response == 'n':
                exit()
    return config_name


def _make_config_location(*, guided):
    current = path(CONFIG_FILE_NAME)

    if os.path.isdir(path(USER)):
        if path() == path(USER):
            result = _simple_decision(current, guided=guided)
        else:
            result = _complex_decision(guided=guided)
    else:
        result = _simple_decision(current, guided=guided)

    return result


def make_config(guided=False):
    """
    Options: --auto, --guided, --manual
    Places for the file: --inplace, --user
    """
    return _make_config_location(guided=guided)


def generate_configurations():
    """
    Use 'get_config' to find a configuration file
    If not found, then generate it on the fly, and return it
    """
    pass
