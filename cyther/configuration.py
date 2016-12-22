
"""
This module holds the necessary definitions to make and find config files which
hold critical data about where different compile-critical directories exist.
"""

import os

from .files import path, USER
from .tools import read_dict_from_file, write_dict_to_file

CONFIG_FILE_NAME = '.cyther_config'
RUNTIME_DIR_KEY = 'runtime_search_directory'
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


def check_config_fields(config_data, prompt=None):
    """
    Extracts the data in the config_data object passed in with a high level
    'prompt' argument. For example, 'python' will return all the data necessary
    to compile python, including the runtime and include directories. If prompt
    is not provided, then it will check for baseline minimum to work
    """

    keys = list(config_data.keys())

    if not prompt:
        prompt = ('c', 'baseline')

    # TODO AFTER EACH CHECKING PROCEDURE, REMOVE FIELD JUST CHECKED
    if 'python' in prompt:
        # Include directories for python
        # Runtime library search dir
        # Runtime name(s)
        pass

    if 'c' in prompt:
        # Nothing should be required of just C (I think)
        pass

    if 'baseline' in prompt:
        # Executable directories
        pass


def generate_configuration(data, prompt):
    """
    Uses a prompt like 'python' to return an object with attributes that relate
    to that general mode of operation
    """
    pass


def make_config():
    """
    Options: --auto, --guided, --manual
    Places for the file: --inplace, --user

    If get_config_file finds a file,

    If the config file is found, then theres a problem

    Print a message to display correct example usage
    """
    pass


CONFIG_NOT_FOUND = 'cnf'
CONFIG_NOT_VALID = 'cnv'
INVALID_OR_MISSING = "Invalid or missing data fields detected in config file"


def get_config(prompt='all'):
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

    valid = check_config_fields(config_data, prompt=prompt)
    if not valid:
        return CONFIG_NOT_VALID, INVALID_OR_MISSING

    return config_data
