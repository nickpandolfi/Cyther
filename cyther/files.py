"""
This module holds the utilities necessary to process full path names and hold
their parsed information, so other tools can easily extract this information
(i.e. extension), and hold the information in a containers better designed
for it
"""

import os

# TODO Change all 'filename's to 'filepath's

DRIVE = 0
EXTENSION = 1
NAME = 0
OVERWRITE_ERROR = "; cannot overwrite without explicit permission"


def getParentDir(path):
    """
    This will return just the name of the parent directory of
    the given file path
    """
    return os.path.basename(os.path.dirname(path))


def injectCache(path):
    """
    This will inject a '__cythercache__' into a file path before the filename
    and after the parent directory, essentially putting it in the cache
    """
    if getParentDir(path) == '__cythercache__':
        raise FileExistsError("Can't put a cache in another cache")
    new_filename = os.path.join(os.path.dirname(path),
                                '__cythercache__',
                                os.path.basename(path))
    return new_filename


def joinExt(name, ext):
    """
    Similar to os.path.join, except it joins a file name and an extension
    """
    if ext[0] == '.':
        ret = name + ext
    else:
        ret = name + '.' + ext
    return ret


def changeFileName(path, new_name):
    """
    Changes the name of the file with the extension from the given path name
    """
    dirname = os.path.dirname(path)
    old_basename = os.path.basename(path)
    new_basename = joinExt(new_name, os.path.splitext(old_basename)[1])
    return os.path.join(dirname, new_basename)


def changeFileDir(path, dirname):
    """
    Changes the parent directory of the given path name
    """
    return os.path.join(dirname, os.path.basename(path))


def changeFileExt(path, ext):
    """
    Changes the extension of the file to ext
    """
    return joinExt(os.path.splitext(path)[0], ext)


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
        appears_like = bool(getExtension(path))
    elif isdir:
        exists = os.path.isdir(path)
        appears_like = not bool(getExtension(path))
    else:
        raise ValueError("Must specify 'isfile' or 'isdir'")

    if exists and not appears_like:
        raise ValueError("The path exists, but doesn't look like it should")

    result = exists or appears_like
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


###############################################################################


def hasExtension(fragment):
    """
    Returns a boolean value to denote if the path fragment 'fragment'
    has an extension
    """
    return bool(os.path.splitext(fragment)[EXTENSION])


def getExtension(fragment):
    """
    Fetch the extension of the partial path 'fragment'
    """
    return os.path.splitext(fragment)[EXTENSION]


def hasName(fragment):
    """
    Return a boolean value to denote if the path fragment 'fragment' has a
    name (test is done by seeing if the fragment has a extension)
    """
    return hasExtension(fragment)


def getName(fragment, *, ext=False):
    """
    Fetch the file name of the partial path 'fragment'
    """
    basename = os.path.basename(fragment)
    if ext:
        result = basename
    else:
        result = os.path.splitext(basename)[NAME]
    return result


def getDirectory(path):
    """
    Gets the directory part of the path provided
    """
    if detectPath(path, isdir=True):
        directory = path
    else:
        directory = os.path.dirname(path)
    return directory


def isAbsolute(path):
    """
    Returns if the given path is an absolute path or not.
    """

    return os.path.abspath(path) == os.path.normpath(path)


# TODO rename error to make more sense (it only blocks one kind of error)
def createPath(path=None, *, name=None, ext=None, inject=None, root=None,
               overwrite=False, exists_error=True, must_exist=False):
    """
    Literally magic
    """
    if name:
        if path and hasName(path):
            if not overwrite:
                raise ValueError("The path supplied must be a "
                                 "directory" + OVERWRITE_ERROR)

        if hasExtension(name):
            if ext:
                if not overwrite:
                    raise ValueError("The name supplied must not have "
                                     "an extension" + OVERWRITE_ERROR)
                new_name = joinExt(getName(name, ext=False), ext)
            else:
                new_name = name
        else:
            if ext:
                new_name = joinExt(name, ext)
            else:
                new_name = getName(name, ext=False)
    else:
        if detectPath(path, isfile=True):
            if ext:
                if not overwrite:
                    raise ValueError("Can't provide an extension with a full "
                                     "file name" + OVERWRITE_ERROR)
                new_name = joinExt(getName(name, ext=False), ext)
            else:
                new_name = getName(name, ext=True)
        else:
            raise ValueError("The path specified is a directory, and no name "
                             "was provided; therefore, no name exists "
                             "to construct off of")

    if root:
        if not isAbsolute(root):
            raise ValueError("The root must be an absolute directory "
                             "if specified")
        if isAbsolute(path):
            raise ValueError("The path cannot be absolute as well as the "
                             "root; cannot add two absolute paths together")

        if path:
            new_directory = os.path.join(root, os.path.dirname(path))
        else:
            new_directory = root
    else:
        if path:
            new_directory = getDirectory(path)
        else:
            new_directory = os.getcwd()

    if inject:
        new_directory = os.path.join(new_directory, inject)

    abspath = os.path.join(new_directory, new_name)
    if must_exist:
        if not os.path.exists(abspath):
            result = abspath
        else:
            if exists_error:
                raise ValueError("The path '{}' doesn't exist".format(abspath))
            else:
                result = None
    else:
        result = abspath
    return result


class File:
    """
    Holds all of the information and methods necessary to process full paths.
    Takes a path name and an optional constructor to build a file name on
    if it does not exist already.
    """

    def __init__(self, path=None, *, error=True, must_exist=True,
                 root=None, full_dir=False):
        full_path = getFullPath(path, must_exist=must_exist, error=error,
                                root=root, absolute=full_dir)
        self.__file_path = full_path
        self.__file_exists = os.path.exists(full_path)

        basename = os.path.basename(full_path)
        isdir = os.path.isdir(full_path)

        self.__file_name = str() if isdir else basename
        self.__file_type = os.path.splitext(full_path)[EXTENSION]
        self.__file_location = os.path.dirname(full_path)

    def __str__(self):
        return self.__file_path

    def __repr__(self):
        return self.__file_path

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

    def isUpdated(self, previous_modified_time):
        """
        Figures out if the file had previously errored and hasn't
        been fixed since given a numerical time
        """
        modified_time = self.getmtime()
        valid = modified_time > previous_modified_time
        return valid

    def getName(self):
        """
        Gets the name of the file as the parent directory sees it
        (ex. 'example.py')
        """
        return self.__file_name

    def getType(self):
        """
        Returns the type of the file (its extension) with the '.'
        """
        return self.__file_type

    def getLocation(self):
        """
        Returns the parent directory of the file
        """
        return self.__file_location

    def getPath(self):
        """
        Returns the full file path to the file, including the drive
        """
        return self.__file_path


if __name__ == '__main__':
    file = File()
    new = file.createPath(extension='.p')
    print(new)
