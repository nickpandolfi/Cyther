
"""
This module holds utilities to search for items, whether they be files or
textual patterns, that cyther will use for compilation. This module is
designed to be relatively easy to use and make a very complex task much less so
"""

import os
import re
import shutil

from .files import get_drive, path, ISDIR

MULTIPLE_FOUND = "More than one pattern found for regex pattern: '{}' " \
                 "for output:\n\t{}"
NONE_FOUND = "No matches for pattern '{}' could be found in output:\n\t{}"
ASSERT_ERROR = "The search result:\n\t{}\nIs not equivalent to the assert " \
               "test provided:\n\t{}"

RUNTIME_PATTERN = r"(?<=lib)(?P<content>.+?)(?=\.so|\.a)"
POUND_PATTERN = r"#\s*@\s?[Cc]yther +(?P<content>.+?)\s*?(\n|$)"
TRIPPLE_PATTERN = r"(?P<quote>'{3}|\"{3})(.|\n)+?@[Cc]yther\s+" \
                  r"(?P<content>(.|\n)+?)\s*(?P=quote)"
VERSION_PATTERN = r"[Vv]ersion:?\s+(?P<content>([0-9]+\.){1,}((dev)?[0-9]+))"


def where(cmd, path=None):
    """
    A function to wrap shutil.which for universal usage
    """
    raw_result = shutil.which(cmd, os.X_OK, path)
    if raw_result:
        return os.path.abspath(raw_result)
    else:
        raise ValueError("Could not find '{}' in the path".format(cmd))


def has_parent(path_name):
    """
    Takes in a file path, and will check that the path has a specific parent
    directory
    """
    target = os.path.normpath(path_name)
    base = os.path.basename(target)
    if target != base:
        # Target is NOT a single component
        parent_check = os.path.dirname(target)
    else:
        # Target is a single component
        parent_check = None


def find(target, start=None):
    """
    Finds a given 'target' (filename string) in the file system
    """
    if not target or not isinstance(target, str):
        raise TypeError("Parameter 'target' must be a filename string")

    if os.path.isabs(target):
        return os.path.isfile(target)
    else:
        dirname, basename = os.path.split(target)

    if not start:
        top = get_drive(os.getcwd())
    elif os.path.isdir(start):
        top = start
    else:
        raise ValueError("Parameter 'start' must be a directory if specified")

    results = []
    for (dirpath, dirnames, filenames) in os.walk(top):
        if target in filenames:
            results.append(path(dirpath, ISDIR, name=target))

    return process_output(results, condense=True)


def get_content(pattern, string):
    """
    Finds the 'content' tag from a 'pattern' in the provided 'string'
    """
    output = []
    for match in re.finditer(pattern, string):
        output.append(match.group('content'))
    return output


MULTIPLE = 'multiple'
NONE = 'none'


def process_output(output, *, condense=False, one=False, default=None,
                   default_if_multiple=True, default_if_none=True):
    """
    Taking a iterative container (list, tuple), this function will process its
    contents and condense if necessary. It also has functionality to try to
    assure that the output has only one item in it if desired. If this is not
    the case, then it will return a 'default' in place of the output, if
    specified.
    """
    if condense:
        output = list(set(output))

    if one:
        if len(output) > 1:
            if default and default_if_multiple:
                output = default
            else:
                return MULTIPLE
        elif len(output) == 1:
            output = output[0]
        else:
            if default and default_if_none:
                return default
            else:
                return NONE

    return output


def assert_output(output, assert_equal):
    """
    Check that two outputs have the same contents as one another, even if they
    aren't sorted yet
    """
    sorted_output = sorted(output)
    sorted_assert = sorted(assert_equal)
    if sorted_output != sorted_assert:
        raise ValueError(ASSERT_ERROR.format(sorted_output, sorted_assert))


def extract(pattern, string, *, assert_equal=False, one=False,
            condense=False, default=None, default_if_multiple=True,
            default_if_none=True):
    """
    Used to extract a given regex pattern from a string, given several options
    """

    output = get_content(pattern, string)

    output = process_output(output, condense=condense, default=default,
                            one=one,
                            default_if_multiple=default_if_multiple,
                            default_if_none=default_if_none)

    if assert_equal:
        assert_output(output, assert_equal)
    else:
        return output


def extractRuntime(runtime_dirs):
    """
    Used to find the correct static lib name to pass to gcc
    """
    names = [str(item) for name in runtime_dirs for item in os.listdir(name)]
    string = '\n'.join(names)
    result = extract(RUNTIME_PATTERN, string, condense=True)
    return result


def extractAtCyther(path_name):
    """
    Extracts the '@cyther' code to be run as a script after compilation
    """
    with open(path_name) as file:
        string = file.read()

    found_pound = extract(POUND_PATTERN, string)
    found_tripple = extract(TRIPPLE_PATTERN, string)
    all_found = found_pound + found_tripple
    code = '\n'.join([item for item in all_found])

    return code


def extractVersion(string, default='?'):
    """
    Extracts a three digit standard format version number
    """
    return extract(VERSION_PATTERN, string, condense=True, default=default,
                   one=True)
