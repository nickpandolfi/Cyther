"""
This module holds utilities to search for items, whether they be files or
textual patterns, that cyther will use for compilation. This module is
designed to be relatively easy to use and make a very complex task much less so
"""

import os
import re
import shutil

# For testing purposes
from time import time

from .tools import isIterable, process_output
from .pathway import get_system_drives, has_suffix, disintegrate
from .launcher import distribute


def _is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


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


def _find_init(init, start):
    if not init:
        raise ValueError("Parameter 'init' must not be empty")
    elif isinstance(init, str):
        target = init
        suffix = None
    elif isIterable(init):
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


def breadth(dirs):
    """
    Crawl through directories like os.walk, but use a 'breadth first' approach
    (os.walk uses 'depth first')
    """
    while dirs:
        next_dirs = []
        print("Dirs: '{}'".format(dirs))
        for d in dirs:
            next_dirs = []
            try:
                for name in os.listdir(d):
                    p = os.path.join(d, name)
                    if os.path.isdir(p):
                        print(p)
                        next_dirs.append(p)
            except PermissionError as nallowed:
                print(nallowed)
        dirs = next_dirs
        if dirs:
            yield dirs


def _get_starting_points(base_start):
    return base_start, [], []


# TODO Make it possible to find multiple things at once (saves crazy time)
# TODO It turns out that process_args might not be necesssary at all... ('one')
def find(init, start=None, one=False, is_exec=False, content=None,
         parallelize=True, workers=None):
    """
    Finds a given 'target' (filename string) in the file system
    """
    base_start, target, suffix = _find_init(init, start)
    print(base_start)

    def _condition(file_path, dirpath, filenames):
        if target in filenames or is_exec and os.access(file_path, os.X_OK):
            if not suffix or has_suffix(dirpath, suffix):
                if not content or search_file(content, file_path):
                    return True
        return False

    starting_points, watch_dirs, excludes = _get_starting_points(base_start)
    disintegrated_excludes = [disintegrate(e) for e in excludes]

    def _filter(dirnames, dirpath):
        if disintegrate(dirpath) in watch_dirs:
            for e in disintegrated_excludes:
                if e[-1] in dirnames:
                    if disintegrate(dirpath) == e[:-1]:
                        dirnames.remove(e[-1])

    def _fetch(top):
        results = []
        for dirpath, dirnames, filenames in os.walk(top, topdown=True):
            # This if-statement is designed to save time
            _filter(dirnames, dirpath)

            file_path = os.path.normpath(os.path.join(dirpath, target))
            if _condition(file_path, dirpath, filenames):
                results.append(file_path)
        return results

    st = time()
    if parallelize:
        unzipped_results = distribute(_fetch, starting_points, workers=workers)
    else:
        unzipped_results = [_fetch(point) for point in base_start]
    et = time()
    print(et - st)

    zipped_results = [i for item in unzipped_results for i in item]
    processed_results = process_output(zipped_results, one=one)

    return processed_results


def bloop(p):
    start = time()
    i = find(['include', 'Python.h'], parallelize=p)
    end = time()
    return end - start


def test(prit=False):
    t1 = bloop(True)
    t2 = bloop(False)
    if prit:
        print("Time (parallelized): '{}'".format(t1))
        print("Time (not parallelized): '{}'".format(t2))
