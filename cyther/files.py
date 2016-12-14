
"""
This module holds the utilities necessary to process full path names and hold
their parsed information, so other tools can easily extract this information
(i.e. extension), and hold the information in a containers better designed
for it
"""

import os
import time

DRIVE = 0
REST = 1

NAME = 0
EXTENSION = 1


__all__ = ['detect', 'get', 'exists', 'path', 'File']


class OverwriteError(Exception):
    """
    Denotes if the user tried to overwrite a part of a file without giving
    explicit permission
    """
    def __init__(self, *args, **kwargs):
        super(OverwriteError, self).__init__(*args, **kwargs)


OVERWRITE_ERROR = "; cannot overwrite without explicit permission"
PATH_HAS_EXT = "Path '{}' has an extension, cannot override to a directory"
PATH_NOT_DIR = "The path supplied must be a directory"
NAME_HAS_EXT = "The name supplied must not have an extension"
FILE_NAME_AND_EXT = "Can't provide an extension with a full file name"
NO_NAME_PATH_IS_DIR = "The path specified is a directory, and no name was " \
                      "provided; therefore, no name exists to construct off of"
NO_NAME_NO_PATH = "There was no path specified, and thus no name exists to " \
                  "construct file path from. Name was not specified"
ROOT_NOT_ABS = "The root must be an absolute directory if specified"
PATH_AND_ROOT_ABS = "The path cannot be absolute as well as the root; " \
                    "cannot add two absolute paths together"
INJECT_IS_FILE = "Parameter 'inject' must be a directory"
RELPATH_NOT_ABS = "If relpath is manually specified, it must be an " \
                  "absolute path"
NOT_SAME_DRIVE = "Calculating relpath requires that the comparator path is " \
                 "of the same drive"
NOT_EXIST = "The path '{}' doesn't exist"
CANNOT_BE_FILE_AND_DIR = "The path specified cannot be both a file and a " \
                         "directory, please specify only one"
MULTIPLE_RETURNS = "Cannot specify multiple returns; One must be specified " \
                   "exclusively"
ITEM_NOT_SUPPORTED = "Item not supported: '{}'"


def _join_ext(name, ext):
    """
    Similar to os.path.join, except it joins a file name and an extension
    """
    if ext[0] == '.':
        ret = name + ext
    else:
        ret = name + '.' + ext
    return ret


def _process_existing_name(path_name, name, ext, overwrite, file_override):
    if path_name and detect(path_name, 'name', file_override=file_override):
        if not overwrite:
            raise OverwriteError(PATH_NOT_DIR + OVERWRITE_ERROR)

    if detect(name, 'ext'):
        if ext:
            if not overwrite:
                raise OverwriteError(NAME_HAS_EXT + OVERWRITE_ERROR)
            new_name = _join_ext(get(name, 'name'), ext)
        else:
            new_name = name
    else:
        if ext:
            new_name = _join_ext(name, ext)
        else:
            new_name = get(name, 'name')
    return new_name


def _process_non_existing_name(path_name, name, ext, overwrite, file_override):
    if path_name:
        if detect(path_name, 'isfile', file_override=file_override):
            if ext:
                if not overwrite:
                    raise OverwriteError(FILE_NAME_AND_EXT + OVERWRITE_ERROR)
                new_name = _join_ext(get(name, 'name'), ext)
            else:
                new_name = get(path_name, '*name')
        else:
            raise ValueError(NO_NAME_PATH_IS_DIR)
    else:
        if ext:
            new_name = _join_ext('', ext)
        else:
            raise ValueError(NO_NAME_NO_PATH)
    return new_name


def _expand_users(*args):
    expanded = []
    for arg in args:
        if arg:
            expanded.append(os.path.expanduser(arg))
        else:
            expanded.append(None)

    if len(expanded) == 1:
        expanded = expanded[0]
    return expanded


def _process_name(path_name, name, ext, overwrite, file_override):
    if name:
        new_name = _process_existing_name(path_name, name, ext, overwrite,
                                          file_override)
    else:
        new_name = _process_non_existing_name(path_name, name, ext, overwrite,
                                              file_override)

    return new_name


def _process_directory(path_name, root, inject, file_override):
    if root:
        if not os.path.isabs(root):
            raise ValueError(ROOT_NOT_ABS)
        if path_name:
            if os.path.isabs(path_name):
                raise ValueError(PATH_AND_ROOT_ABS)
            new_directory = os.path.join(root, get(path_name, '*dir'))
        else:
            new_directory = root
    else:
        cwd = os.getcwd()
        if path_name and detect(path_name, 'dir', file_override=file_override):
            if os.path.isabs(path_name):
                new_directory = get(path_name, '*dir')
            else:
                new_directory = os.path.join(cwd, get(path_name, '*dir'))
        else:
            new_directory = cwd

    if inject:
        if detect(inject, 'isfile'):
            raise ValueError(INJECT_IS_FILE)
        new_directory = os.path.join(new_directory, inject)

    return new_directory


def _construct_path(new_directory, new_name):
    path_name = os.path.normpath(os.path.join(new_directory, new_name))
    return path_name


def _format_path(path_name, root, relpath, reduce):
    if reduce:
        relpath = True

    if not relpath:
        result = path_name
    else:
        if isinstance(relpath, str):
            if not os.path.isabs(relpath):
                raise ValueError(RELPATH_NOT_ABS)
            start = relpath
        elif root:
            start = root
        else:
            start = os.getcwd()

        if get(path_name, 'drive') != get(start, 'drive'):
            raise ValueError(NOT_SAME_DRIVE)

        new_path = os.path.relpath(path_name, start=start)

        if reduce and (len(new_path) >= len(path_name)):
            result = path_name
        else:
            result = new_path

    return result


def _sort_output(results):
    if not results:
        raise ValueError("Must specify at least one identifier")
    elif len(results) == 1:
        ret = results[0]
    else:
        ret = tuple(results)

    return ret


def exists(path_name, istype=None):
    """
    Checks to make sure a path name exists within the file system given a path
    name, and an optional type for the path (file / dir)
    """
    if istype == 'isfile':
        result = os.path.isfile(path_name)
    elif istype == 'isdir':
        result = os.path.isdir(path_name)
    elif not istype:
        result = os.path.exists(path_name)
    else:
        raise ValueError("Incorrect 'istype' parameter: '{}'".format(istype))

    return result


def detect(path_name, *args, file_override=None):
    """
    Detects different things about the path in question
    """
    results = []
    for item in args:
        if item == 'isfile':
            has_ext = '.' in os.path.basename(path_name)
            looks_like_file = has_ext and not (file_override is False)
            r = looks_like_file or (file_override is True)
        elif item == 'isdir':
            not_has_ext = '.' not in os.path.basename(path_name)
            looks_like_dir = not_has_ext and not (file_override is True)
            r = looks_like_dir or (file_override is False)
        elif item == 'isabs':
            r = os.path.isabs(path_name)
        elif item == 'ext':
            r = '.' in os.path.basename(path_name)
        elif item == 'name':
            r = detect(path_name, 'isfile')
        elif item == 'dir':
            r = bool(os.path.dirname(path_name))
        else:
            raise ValueError(ITEM_NOT_SUPPORTED.format(item))
        results.append(r)

    return _sort_output(results)


def get(path_name, *args):
    """
    This function will extract different portions of a path's name
    """
    results = []

    for item in args:
        if item == 'drive':
            r = os.path.splitdrive(os.path.normpath(path_name))[DRIVE]
        elif item == '*dir':
            if detect(path_name, 'isdir'):
                r = path_name
            else:
                r = os.path.dirname(path_name)
        elif item == 'dir':
            r = os.path.dirname(path_name)
        elif item == 'parent':
            r = os.path.basename(os.path.dirname(path_name))
        elif item == '*name':
            if detect(path_name, 'isfile'):
                r = os.path.basename(path_name)
            else:
                r = ''
        elif item == 'name':
            if detect(path_name, 'isfile'):
                r = os.path.splitext(os.path.basename(path_name))[NAME]
            else:
                r = ''
        elif item == 'ext':
            basename = os.path.basename(path_name)
            if '.' in basename:
                if basename[0] == '.':
                    r = os.path.splitext(basename)[NAME]
                else:
                    r = os.path.splitext(basename)[EXTENSION]
            else:
                r = ''
        else:
            raise ValueError(ITEM_NOT_SUPPORTED.format(item))

        results.append(r)

    return _sort_output(results)


def path(path_name=None, *, name=None, ext=None, inject=None, root=None,
         relpath=None, reduce=False, file_override=None, overwrite=False):
    """
    Path manipulation black magic
    """
    path_name, root = _expand_users(path_name, root)
    new_name = _process_name(path_name, name, ext, overwrite, file_override)
    new_directory = _process_directory(path_name, root, inject, file_override)
    full_path = _construct_path(new_directory, new_name)
    final_path = _format_path(full_path, root, relpath, reduce)

    return final_path


class File:
    """
    Holds all of the information and methods necessary to process full paths.
    Takes a path name and an optional constructor to build a file name on
    if it does not exist already.
    """

    def __init__(self, path_name=None, **kwargs):
        self.__path = path(path_name, **kwargs)
        self.__stamp = None

    def __str__(self):
        return self.getPath()

    def __repr__(self):
        return "File('{}')".format(str(self))

    def getmtime(self):
        """
        Works the same as os.path.getmtime, but on the full internal path
        """
        return os.path.getmtime(self.getPath())

    def exists(self):
        """
        Method that works the same as os.path.exists, but on the internal path
        """
        return os.path.exists(self.getPath())

    def path(self, **kwargs):
        """
        Returns a different object with the specified changes applied to
        it. This object is not changed in the process.
        """
        new_path = path(self.getPath(), **kwargs)
        return File(new_path)

    def isOutDated(self, output_file):
        """
        Figures out if Cyther should compile the given FileInfo object by
        checking the both of the modified times
        """
        if output_file.exists():
            source_time = self.getmtime()
            output_time = output_file.getmtime()
            if source_time > output_time:
                return True
        else:
            return True
        return False

    def stampError(self):
        """
        Sets the current error point to the
        """
        self.__stamp = time.time()

    def isUpdated(self):
        """
        Figures out if the file had previously errored and hasn't
        been fixed since given a numerical time
        """
        modified_time = self.getmtime()
        valid = modified_time > self.__stamp
        return valid

    def getName(self, ext=True):
        """
        Gets the name of the file as the parent directory sees it
        (ex. 'example.py')
        """
        identifier = '*name' if ext else 'name'
        return get(self.getPath(), identifier)

    def getExtension(self):
        """
        Returns the type of the file (its extension) with the '.'
        """
        return get(self.getPath(), 'ext')

    def getDirectory(self):
        """
        Returns the parent directory of the file
        """
        return get(self.getPath(), 'dir')

    def getPath(self):
        """
        Returns the full file path to the file, including the drive
        """
        return self.__path
