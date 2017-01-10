
"""
This module provides tools to extract different patterns from raw text or files
"""

import os
import re

# Although NONE and MULTIPLE arent used here, they may be used BY THE USER
from .tools import process_output, assert_output, NONE, MULTIPLE


def get_content(pattern, string, tag='content'):
    """
    Finds the 'content' tag from a 'pattern' in the provided 'string'
    """
    output = []
    for match in re.finditer(pattern, string):
        output.append(match.group(tag))
    return output


def extract(pattern, string, *, assert_equal=False, one=False,
            condense=False, default=None, default_if_multiple=True,
            default_if_none=True):
    """
    Used to extract a given regex pattern from a string, given several options
    """

    if isinstance(pattern, str):
        output = get_content(pattern, string)
    else:
        # Must be a linear container
        output = []
        for p in pattern:
            output += get_content(p, string)

    output = process_output(output, one=one, condense=condense,
                            default=default,
                            default_if_multiple=default_if_multiple,
                            default_if_none=default_if_none)

    if assert_equal:
        assert_output(output, assert_equal)
    else:
        return output


RUNTIME_PATTERN = r"(?<=lib)(?P<content>.+?)(?=\.so|\.a)"


def extractRuntime(runtime_dirs):
    """
    Used to find the correct static lib name to pass to gcc
    """
    names = [str(item) for name in runtime_dirs for item in os.listdir(name)]
    string = '\n'.join(names)
    result = extract(RUNTIME_PATTERN, string, condense=True)
    return result


POUND_PATTERN = r"#\s*@\s?[Cc]yther +(?P<content>.+?)\s*?(\n|$)"
TRIPPLE_PATTERN = r"(?P<quote>'{3}|\"{3})(.|\n)+?@[Cc]yther\s+" \
                  r"(?P<content>(.|\n)+?)\s*(?P=quote)"


def extractAtCyther(string):
    """
    Extracts the '@cyther' code to be run as a script after compilation
    """
    if isinstance(string, str) and os.path.isfile(string):
        with open(string) as file:
            string = file.read()

    found_pound = extract(POUND_PATTERN, string)
    found_tripple = extract(TRIPPLE_PATTERN, string)
    all_found = found_pound + found_tripple
    code = '\n'.join([item for item in all_found])

    return code


VERSION_PATTERN = r"[Vv]ersion:?\s+(?P<content>([0-9]+\.){1,}((dev)?[0-9]+))"


def extractVersion(string, default='?'):
    """
    Extracts a three digit standard format version number
    """
    return extract(VERSION_PATTERN, string, condense=True, default=default,
                   one=True)
