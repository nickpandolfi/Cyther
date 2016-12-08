"""
This module holds the utilities necessary to process full path names and hold
their parsed information, so other tools can easily extract this information
(i.e. extension), and hold the information in a containers better designed
for it
"""

import os
import time

DRIVE = 0
EXTENSION = 1
NAME = 0
OVERWRITE_ERROR = "; cannot overwrite without explicit permission"


__all__ = ['createPath', 'getPath', 'File']


def _join_ext(name, ext):
    """
    Similar to os.path.join, except it joins a file name and an extension
    """
    if ext[0] == '.':
        ret = name + ext
    else:
        ret = name + '.' + ext
    return ret


def _has_ext(fragment):
    return bool(os.path.splitext(fragment)[EXTENSION])


def _get_ext(fragment):
    return os.path.splitext(fragment)[EXTENSION]


def _has_name(fragment):
    return _has_ext(fragment)


def _get_name(fragment, *, ext=False):
    basename = os.path.basename(fragment)
    if ext:
        result = basename
    else:
        result = os.path.splitext(basename)[NAME]
    return result


def _has_directory(fragment):
    if _has_ext(fragment):
        return bool(os.path.dirname(fragment))
    else:
        return bool(fragment)


def _get_directory(path):
    if not _isfile(path):
        directory = path
    else:
        directory = os.path.dirname(path)
    return directory


def _is_absolute(path):
    """
    Returns if the given path is an absolute path or not.
    """
    return os.path.abspath(path) == os.path.normpath(path)


def _isfile(path, override=None):
    if override is True:
        result = True
    elif override is False:
        if _isfile(path):
            raise ValueError("Path '{}' has an extension, cannot "
                             "override to a directory".format(path))
        result = False
    else:
        result = bool(_get_ext(path))

    return result


def _get_drive(path):
    return os.path.splitdrive(path)[DRIVE]


def _ensure_same_drives(path1, path2):
    if _get_drive(path1) != _get_drive(path2):
        return False
    return True


def _process_existing_name(path, name, ext, overwrite):
    if path and _has_name(path):
        if not overwrite:
            raise ValueError("The path supplied must be a "
                             "directory" + OVERWRITE_ERROR)

    if _has_ext(name):
        if ext:
            if not overwrite:
                raise ValueError("The name supplied must not have "
                                 "an extension" + OVERWRITE_ERROR)
            new_name = _join_ext(_get_name(name, ext=False), ext)
        else:
            new_name = name
    else:
        if ext:
            new_name = _join_ext(name, ext)
        else:
            new_name = _get_name(name, ext=False)
    return new_name


def _process_non_existing_name(path, name, ext, overwrite):
    if path:
        if _isfile(path):
            if ext:
                if not overwrite:
                    raise ValueError("Can't provide an extension with a "
                                     "full file name" + OVERWRITE_ERROR)
                new_name = _join_ext(_get_name(name, ext=False), ext)
            else:
                new_name = _get_name(path, ext=True)
        else:
            raise ValueError("The path specified is a directory, and no "
                             "name was provided; therefore, no name "
                             "exists to construct off of")
    else:
        raise ValueError("There was no path specified, and thus no name "
                         "exists to construct file path from. Name was "
                         "not specified")
    return new_name


def _expand_users(*args):
    expanded = []
    for arg in args:
        if arg:
            expanded.append(os.path.expanduser(arg))
        else:
            expanded.append(None)

    return expanded


def _process_name(path, name, ext, overwrite):
    if name:
        new_name = _process_existing_name(path, name, ext, overwrite)
    else:
        new_name = _process_non_existing_name(path, name, ext, overwrite)

    return new_name


def _process_directory(path, root, inject):
    # TODO What if path is absolute???
    if root:
        if not _is_absolute(root):
            raise ValueError("The root must be an absolute directory "
                             "if specified")

        if path:
            if _is_absolute(path):
                raise ValueError("The path cannot be absolute as well as the "
                                 "root; cannot add two absolute paths "
                                 "together")
            new_directory = os.path.join(root, _get_directory(path))
        else:
            new_directory = root
    else:
        cwd = os.getcwd()
        if path and _has_directory(path):
            if _is_absolute(path):
                new_directory = _get_directory(path)
            else:
                new_directory = os.path.join(cwd, _get_directory(path))
        else:
            new_directory = cwd

    if inject:
        if _isfile(inject):
            raise ValueError("Parameter 'inject' must be a directory")
        new_directory = os.path.join(new_directory, inject)

    return new_directory


def _construct_path(new_directory, new_name):
    path = os.path.normpath(os.path.join(new_directory, new_name))
    return path


def _format_path(path, root, relpath, reduce):
    if reduce:
        relpath = True

    if not relpath:
        result = path
    else:
        if isinstance(relpath, str):
            if not _is_absolute(relpath):
                raise ValueError("If relpath is manually specified, it "
                                 "must be an absolute path")
            start = relpath
        elif root:
            start = root
        else:
            start = os.getcwd()

        is_same_drive = _ensure_same_drives(path, start)

        if not is_same_drive:
            raise ValueError("Calculating relpath requires that the "
                             "comparator path is of the same drive")

        new_path = os.path.relpath(path, start=start)

        if reduce and (len(new_path) >= len(path)):
            result = path
        else:
            result = new_path

    return result


def _check_path(path, must_exist, exists_error, exists):
    if exists:
        exists_error = False
        must_exist = True

    if must_exist and not os.path.exists(path):
        if exists_error:
            raise ValueError("The path '{}' doesn't exist".format(path))
        else:
            result = False
    else:
        result = path

    return result


# TODO Make a overriding option to tell the function if path is a dir or file
def createPath(path=None, *, name=None, ext=None, inject=None, root=None,
               overwrite=False, exists_error=True, must_exist=False,
               relpath=None, reduce=False, exists=False):
    """
    Path manipulation black magic
    """
    path, root = _expand_users(path, root)
    new_name = _process_name(path, name, ext, overwrite)
    new_directory = _process_directory(path, root, inject)
    full_path = _construct_path(new_directory, new_name)
    final_path = _format_path(full_path, root, relpath, reduce)
    result = _check_path(final_path, must_exist, exists_error, exists)

    return result


class File:
    """
    Holds all of the information and methods necessary to process full paths.
    Takes a path name and an optional constructor to build a file name on
    if it does not exist already.
    """

    def __init__(self, path=None, **kwargs):
        self.__path = createPath(path, **kwargs)
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

    def createPath(self, **kwargs):
        """
        Returns a different object with the specified changes applied to
        it. This object is not changed in the process.
        """
        new_path = createPath(self.getPath(), **kwargs)
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
        return _get_name(self.getPath(), ext=ext)

    def getExtension(self):
        """
        Returns the type of the file (its extension) with the '.'
        """
        return _get_ext(self.getPath())

    def getDirectory(self):
        """
        Returns the parent directory of the file
        """
        return _get_directory(self.getPath())

    def getPath(self):
        """
        Returns the full file path to the file, including the drive
        """
        return self.__path


def test_createPath():
    """
    Tests createPath to make sure its working
    """
    assert createPath('test.o') != 'test.o'
    assert createPath('test.o') == createPath(name='test', ext='o')
    assert createPath('parent/test.o') == createPath('test.o', inject='parent')

    test_path = os.path.abspath('test.o')
    assert createPath(test_path) == test_path
    assert createPath(test_path, relpath=True) != test_path

if __name__ == '__main__':
    test_createPath()
