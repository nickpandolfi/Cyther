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


__all__ = ['injectCache', 'detectPath', 'createPath', 'getFullPath', 'File']


def injectCache(path):
    """
    This will inject a '__cythercache__' into a file path before the filename
    and after the parent directory, essentially putting it in the cache
    """
    if os.path.basename(os.path.dirname(path)) == '__cythercache__':
        raise FileExistsError("Can't put a cache in another cache")
    new_filename = os.path.join(os.path.dirname(path),
                                '__cythercache__',
                                os.path.basename(path))
    return new_filename


# TODO Implement a must_exist parameter?
def detectPath(path, *, isfile=None, isdir=None):
    """
    Detect what the path represents. Must provide a single mutually exclusive
    keyword argument of either 'isdir' or 'isfile', depending on what you
    want to detect for.
    """
    if isfile and isdir:
        raise ValueError("Cannot specify both 'isfile' and 'isdir'")

    if isfile:
        exists = os.path.isfile(path)
        appears_like = bool(_get_ext(path))
    elif isdir:
        exists = os.path.isdir(path)
        appears_like = not bool(_get_ext(path))
    else:
        raise ValueError("Must specify 'isfile' or 'isdir'")

    if exists and not appears_like:
        raise ValueError("The path exists, but doesn't look like it should")

    result = exists or appears_like
    return result


###############################################################################

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
    if detectPath(path, isdir=True):
        directory = path
    else:
        directory = os.path.dirname(path)
    return directory


def _is_absolute(path):
    """
    Returns if the given path is an absolute path or not.
    """
    return os.path.abspath(path) == os.path.normpath(path)


def _process_name(path, name, ext, overwrite):
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


def _process_no_name(path, name, ext, overwrite):
    if path:
        if detectPath(path, isfile=True):
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


def _process_directory(path, root, inject):
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
        # TODO This if statement can probably be cleaned up a little bit
        if path:
            if _has_directory(path):
                new_directory = _get_directory(path)
            else:
                new_directory = os.getcwd()
        else:
            new_directory = os.getcwd()

    if inject:
        new_directory = os.path.join(new_directory, inject)

    return new_directory


def _process_path(path, must_exist, exists_error):
    if must_exist:
        if not os.path.exists(path):
            result = path
        else:
            if exists_error:
                raise ValueError("The path '{}' doesn't "
                                 "exist".format(path))
            else:
                result = None
    else:
        result = path

    return result


# TODO Make a overriding option to tell the function if path is a dir or file
# TODO even if it doesn't look like it (path_is_file=True, path_is_dir=False)
def createPath(path=None, *, name=None, ext=None, inject=None, root=None,
               overwrite=False, exists_error=True, must_exist=False):
    """
    Literally magic
    """
    if path.count('~') == 1:
        path = os.path.expanduser(path)

    if name:
        new_name = _process_name(path, name, ext, overwrite)
    else:
        new_name = _process_no_name(path, name, ext, overwrite)

    new_directory = _process_directory(path, root, inject)

    full_path = os.path.normpath(os.path.join(new_directory, new_name))

    result = _process_path(full_path, must_exist, exists_error)

    return result


def getFullPath(path=None, *, must_exist=True, error=True):
    """
    Gets the full absolute path of a given path
    """
    if path:
        abspath = os.path.abspath(path)
        if must_exist:
            if os.path.exists(abspath):
                full_path = abspath
            else:
                if error:
                    raise FileNotFoundError("The path '{}' does not "
                                            "exist".format(abspath))
                else:
                    full_path = None
        else:
            full_path = abspath
    else:
        full_path = os.getcwd()

    return full_path


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
        return self.getPath()

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
        return _get_name(self.__path, ext=ext)

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


if __name__ == '__main__':
    pass
    # FIXME createPath('poop.o', inject='cache.swag')
    print(createPath('~/poop.o'))
