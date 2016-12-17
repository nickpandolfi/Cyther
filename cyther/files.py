
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

ISFILE = True
ISDIR = False

EXT = '.'

__all__ = ['identify', 'detect', 'get', 'path', 'exists', 'File']


class OverwriteError(Exception):
    """
    Denotes if the user tried to overwrite a part of a file without giving
    explicit permission
    """
    def __init__(self, *args, **kwargs):
        super(OverwriteError, self).__init__(*args, **kwargs)


OVERWRITE_ERROR = "; cannot overwrite without explicit permission"


def _join_ext(name, extension, ext=EXT):
    if extension[0] == ext:
        ret = name + extension
    else:
        ret = name + ext + extension
    return ret


def _sort_output(results):
    if not results:
        raise ValueError("Must specify at least one identifier")
    elif len(results) == 1:
        ret = results[0]
    else:
        ret = tuple(results)
    return ret

###########################################################################


def _isfile(path_name, override=None):
    return identify(path_name, override=override) == ISFILE


def _isdir(path_name, override=None):
    return identify(path_name, override=override) == ISDIR


def _has_ext(path_name, ext=EXT):
    return ext in os.path.basename(path_name)


def _has_dir(path_name):
    return bool(os.path.dirname(path_name))


def _get_drive(path_name):
    return os.path.splitdrive(os.path.normpath(path_name))[DRIVE]


def _get_dir(path_name, override=None):
    if _isdir(path_name, override):
        r = path_name
    else:
        r = os.path.dirname(path_name)
    return r


def _get_parent(path_name):
    return os.path.basename(os.path.dirname(path_name))


def _get_name(path_name, ext, identity=None):
    if identity == ISFILE or (identity is None and identify(path_name)):
        if ext:
            r = os.path.basename(path_name)
        else:
            r = os.path.splitext(os.path.basename(path_name))[NAME]
    else:
        r = ''
    return r


def _get_ext(path_name, ext=EXT):
    basename = os.path.basename(path_name)
    if _has_ext(basename):
        if basename[0] == ext:
            r = os.path.splitext(basename)[NAME]
        else:
            r = os.path.splitext(basename)[EXTENSION]
    else:
        r = ''
    return r

###########################################################################


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


def _process_existing_name(path_name, name, ext, overwrite, identity,
                           multi_ext):
    if path_name and identity == ISFILE:
        if not overwrite:
            raise OverwriteError("The path supplied must be a directory" +
                                 OVERWRITE_ERROR)

    if _has_ext(name):
        if ext:
            if not overwrite and not multi_ext:
                raise OverwriteError("The name supplied must not have an "
                                     "extension" + OVERWRITE_ERROR)
            new_name = _join_ext(_get_name(name, False), ext)
        else:
            new_name = name
    else:
        if ext:
            new_name = _join_ext(name, ext)
        else:
            new_name = _get_name(name, False)
    return new_name


def _process_non_existing_name(path_name, name, ext, overwrite, identity):
    if path_name:
        if identity == ISFILE:
            if ext:
                if not overwrite:
                    raise OverwriteError("Can't provide an extension with a "
                                         "full file name" + OVERWRITE_ERROR)
                new_name = _join_ext(_get_name(name, False), ext)
            else:
                new_name = _get_name(path_name, True, identity)
        else:
            raise ValueError("The path specified is a directory, and no name "
                             "was provided; therefore, no name exists to "
                             "construct off of")
    else:
        if ext:
            new_name = _join_ext('', ext)
        else:
            raise ValueError("There was no path specified, and thus no name "
                             "exists to construct file path from. Name was "
                             "not specified")
    return new_name


def _process_name(path_name, name, ext, overwrite, identity, multi_ext):
    if name:
        new_name = _process_existing_name(path_name, name, ext, overwrite,
                                          identity, multi_ext)
    else:
        new_name = _process_non_existing_name(path_name, name, ext, overwrite,
                                              identity)

    return new_name


def _process_directory(path_name, root, inject, override):
    if root:
        if not os.path.isabs(root):
            raise ValueError("The root must be an absolute directory "
                             "if specified")
        if path_name:
            if os.path.isabs(path_name):
                raise ValueError("The path cannot be absolute as well as the r"
                                 "oot; cannot add two absolute paths together")
            new_directory = os.path.join(root, _get_dir(path_name, override))
        else:
            new_directory = root
    else:
        cwd = os.getcwd()
        if path_name and _has_dir(path_name):
            dir_extension = _get_dir(path_name, override)
            if os.path.isabs(path_name):
                new_directory = dir_extension
            else:
                new_directory = os.path.join(cwd, dir_extension)
        else:
            new_directory = cwd

    if inject:
        if _isfile(inject):
            raise ValueError("Parameter 'inject' must be a directory")
        new_directory = os.path.join(new_directory, inject)

    return new_directory


def _format_path(path_name, root, relpath, reduce):
    if reduce:
        relpath = True

    if not relpath:
        result = path_name
    else:
        if isinstance(relpath, str):
            if not os.path.isabs(relpath):
                raise ValueError("If relpath is manually specified, it must "
                                 "be an absolute path")
            start = relpath
        elif root:
            start = root
        else:
            start = os.getcwd()

        if _get_drive(path_name) != _get_drive(start):
            raise ValueError("Calculating relpath requires that the "
                             "comparator path is of the same drive")

        new_path = os.path.relpath(path_name, start=start)

        if reduce and (len(new_path) >= len(path_name)):
            result = path_name
        else:
            result = new_path

    return result

###########################################################################


def identify(path_name, *, override=None, check_exists=True, default=ISDIR):
    """
    Identify the type of a given path name (file or directory)
    """
    if not path_name:
        if path_name is None:
            return None
        else:
            raise ValueError("The path name provided is empty")

    result = None
    head, tail = os.path.split(path_name)

    if check_exists and os.path.exists(path_name):
        if os.path.isfile(path_name):
            result = ISFILE
        elif os.path.isdir(path_name):
            result = ISDIR
        else:
            raise Exception("Path exists but isn't a file or a directory...")
    elif not tail:
        result = ISDIR
    elif _has_ext(tail):
        result = ISFILE

    if result is None:
        if override is not None:
            result = override
        else:
            result = default
    else:
        if override is not None:
            if result != override:
                raise ValueError("The path '{}' appears to be ")

    return result


def exists(path_name, istype=None):
    """
    Checks to make sure a path name exists within the file system given a path
    name, and an optional type for the path (file / dir)
    """
    if istype == ISFILE:
        result = os.path.isfile(path_name)
    elif istype == ISDIR:
        result = os.path.isdir(path_name)
    elif not istype:
        result = os.path.exists(path_name)
    else:
        raise ValueError("Incorrect 'istype' parameter: '{}'".format(istype))
    return result


def detect(path_name, *args, override=None):
    """
    Detects different things about the path in question
    """
    results = []
    for item in args:
        if item == 'isfile' or item == 'name':
            r = identify(path_name, override=override) == ISFILE
        elif item == 'isdir':
            r = identify(path_name, override=override) == ISDIR
        elif item == 'isabs':
            r = os.path.isabs(path_name)
        elif item == 'ext':
            r = _has_ext(path_name)
        elif item == 'dir':
            r = _has_dir(path_name)
        else:
            raise ValueError("Item '{}' not supported in function "
                             "detect".format(item))
        results.append(r)

    return _sort_output(results)


def get(path_name, *args, override=None):
    """
    This function will extract different portions of a path's name
    """
    results = []

    for item in args:
        if item == 'drive':
            r = _get_drive(path_name)
        elif item == '+dir':
            r = _get_dir(path_name, override)
        elif item == 'dir':
            r = os.path.dirname(path_name)
        elif item == 'parent':
            r = _get_parent(path_name)
        elif item == 'name.ext':
            r = _get_name(path_name, True, override)
        elif item == 'name':
            r = _get_name(path_name, False, override)
        elif item == 'ext':
            r = _get_ext(path_name)
        else:
            raise ValueError("Item '{}' not supported in "
                             "function get".format(item))

        results.append(r)

    return _sort_output(results)


def path(path_name=None, *, name=None, ext=None, inject=None, overwrite=False,
         relpath=None, reduce=False, override=None, root=None,
         multi_ext=True):
    """
    Path manipulation black magic
    """
    identity = identify(path_name, override=override)
    path_name, root = _expand_users(path_name, root)

    new_name = _process_name(path_name, name, ext, overwrite,
                             identity, multi_ext)
    new_directory = _process_directory(path_name, root, inject, identity)
    full_path = os.path.normpath(os.path.join(new_directory, new_name))
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
            return source_time > output_time
        else:
            return True

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
        return _get_name(self.getPath(), ext)

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
