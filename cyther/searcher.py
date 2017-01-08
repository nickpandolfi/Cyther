
"""
This module holds utilities to search for items, whether they be files or
textual patterns, that cyther will use for compilation. This module is
designed to be relatively easy to use and make a very complex task much less so
"""

import os
import re
import shutil
import multiprocessing

from .pathway import get_system_drives, has_suffix, disintegrate


def where(cmd, path=None):
    """
    A function to wrap shutil.which for universal usage
    """
    raw_result = shutil.which(cmd, os.X_OK, path)
    if raw_result:
        return os.path.abspath(raw_result)
    else:
        raise ValueError("Could not find '{}' in the path".format(cmd))


def search_file(pattern, file_path):
    """
    Search a given file's contents for the regex pattern given as 'pattern'
    """
    try:
        with open(file_path) as file:
            string = file.read()
    except PermissionError:
        return []

    matches = re.findall(pattern, string)

    return matches


def get_content(pattern, string, tag='content'):
    """
    Finds the 'content' tag from a 'pattern' in the provided 'string'
    """
    output = []
    for match in re.finditer(pattern, string):
        output.append(match.group(tag))
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


ASSERT_ERROR = "The search result:\n\t{}\nIs not equivalent to the assert " \
               "test provided:\n\t{}"


def assert_output(output, assert_equal):
    """
    Check that two outputs have the same contents as one another, even if they
    aren't sorted yet
    """
    sorted_output = sorted(output)
    sorted_assert = sorted(assert_equal)
    if sorted_output != sorted_assert:
        raise ValueError(ASSERT_ERROR.format(sorted_output, sorted_assert))


def _find_init(init, start):
    if not init:
        raise ValueError("Parameter 'init' must not be empty")
    elif isinstance(init, str):
        target = init
        suffix = None
    elif isinstance(init, list):
        target = init.pop()
        if init:
            suffix = init
        else:
            suffix = None
    else:
        raise TypeError("Parameter 'init' cannot be type "
                        "'{}'".format(type(init)))

    if not start:
        start = get_system_drives()
    elif isinstance(start, str) and os.path.isdir(start):
        start = [start]
    else:
        raise TypeError("Parameter 'start' must be None, tuple, or list")

    return start, target, suffix


def _get_starting_points(base_start):
    return base_start


# TODO Make it possible to find multiple things at once (saves crazy time)
# TODO It turns out that process_args might not be necesssary at all... ('one')
def find(init, start=None, one=False, is_exec=False, content=None,
         workers=None):
    """
    Finds a given 'target' (filename string) in the file system
    """
    base_start, target, suffix = _find_init(init, start)

    def _condition(file_path, dirpath, dirnames, filenames):
        if target in filenames or is_exec and os.access(file_path, os.X_OK):
            if not suffix or has_suffix(dirpath, suffix):
                if not content or search_file(content, file_path):
                    return True
        return False

    def _fetch(top):
        disintegrated_excludes = disintegrate(excludes)
        results = []
        for dirpath, dirnames, filenames in os.walk(top, topdown=True):
            # This if-statement is designed to save time
            if disintegrate(dirpath) == watch_dirs:
                for e in disintegrated_excludes:
                    if e[-1] in dirnames:
                        if disintegrate(dirpath) == e[:-1]:
                            dirnames.remove(e[-1])

            file_path = os.path.normpath(os.path.join(dirpath, target))
            if _condition(file_path, dirpath, dirnames, filenames):
                results.append(file_path)
        return results

    starting_points, watch_dirs, excludes = _get_starting_points(base_start)

    with multiprocessing.Pool(workers) as pool:
        unzipped_results = pool.map(_fetch, starting_points)

    zipped_results = [i for item in unzipped_results for i in item]

    processed_results = process_output(zipped_results, one=one)

    return processed_results


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


def test():
    uzaz((('a', 'b'), ('c', 'd')))#print(find('Python.h'))

