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


def getParentDir(filename):
    """
    This will return just the name of the parent directory of
    the given file path
    """
    return os.path.basename(os.path.dirname(filename))


def injectCache(filename):
    """
    This will inject a '__cythercache__' into a file path before the filename
    and after the parent directory, essentially putting it in the cache
    """
    if getParentDir(filename) == '__cythercache__':
        raise FileExistsError("Can't put a cache in another cache")
    new_filename = os.path.join(os.path.dirname(filename),
                                '__cythercache__',
                                os.path.basename(filename))
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


def changeFileName(filename, new_name):
    """
    Changes the name of the file with the extension from the given path name
    """
    dirname = os.path.dirname(filename)
    old_basename = os.path.basename(filename)
    new_basename = joinExt(new_name, os.path.splitext(old_basename)[1])
    return os.path.join(dirname, new_basename)


def changeFileDir(filename, dirname):
    """
    Changes the parent directory of the given path name
    """
    return os.path.join(dirname, os.path.basename(filename))


def changeFileExt(filename, ext):
    """
    Changes the extension of the file to ext
    """
    return joinExt(os.path.splitext(filename)[0], ext)


# TODO detect if it is a file or directory fragment
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


def getFullPath(path=None, *, must_exist=True, error=True, root=None,
                absolute=False):
    """
    Gets the full absolute path of a given path
    """
    if path:
        if root:
            if absolute and not os.path.splitdrive(root)[DRIVE]:
                raise ValueError("Parameter 'root' must be a full path name")
            path = os.path.join(root, path)
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


def getExtension(path):
    """
    Fetch the extension of the path name 'path'
    """
    return os.path.splitext(path)[EXTENSION]


def getName(path):
    pass


def getFileName(path):
    pass


def getDirectory(path):
    if detectPath(path, isdir=True):
        directory = path
    else:
        directory = os.path.dirname(path)
    return directory

OVERWRITE_ERROR = "; cannot overwrite without explicit permission"


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
                new_name = joinExt(getJustName(name), ext)
            else:
                new_name = name
        else:
            if ext:
                new_name = joinExt(name, ext)
            else:
                new_name = getJustName(name)
    else:
        if detectPath(path, isfile=True):
            if ext:
                if not overwrite:
                    raise ValueError("Can't provide an extension with a full "
                                     "file name" + OVERWRITE_ERROR)
                new_name = joinExt(getJustName(name), ext)
            else:
                new_name = name
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

    abspath = os.path.join(new_directory, name)
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


"""
If inject
    NEW_DIRECTORY = NEW_DIRECTORY + inject

abspath = os.path.join(NEW_DIRECTORY, NEW_NAME)
if must_exist
    if abspath exists
        result = abspath
    else
        if exists_error
            ERROR (The path doesn't exist)
        else
            result = None
else
    result = abspath

return result
"""


"""
if name
    If path and path has a name
        if not overwrite
            ERROR (Path must be a directory)

    If name has an extension
        if ext is given
            if not overwrite:
                ERROR (cannot overwrite the name's extension, strip it first)
            NEW_NAME = name(w/o ext) + given_ext
        else
            NEW_NAME = name
    else
        if ext is given
            NEW_NAME = name + given_ext
        else
            NEW_NAME = name(w/o ext)
else
    if path is a file, extract file name
        if ext:
            if not overwrite:
                ERROR
            NEW_NAME = name(w/o ext) + given_ext
        else:
            NEW_NAME = name
    else
        ERROR (path is a directory, no name exists)
"""
"""
If root
    If root is not absolute
        ERROR (root must be an absolute directory if specified)
    if path is absolute
        ERROR (cannot add two absolute paths together...)

    If path
        NEW_DIRECTORY = root + dirname(path)
    else
        NEW_DIRECTORY = root
else
    If path
        path = getDirectory(path)
        If path is a directory
            NEW_DIRECTORY = abspath(path)
        else
            NEW_DIRECTORY = dirname(path)
    else
        NEW_DIRECTORY = cwd
"""


# TODO Add the getFullPath and convert functions together?
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
        return self.__file_exists

    def create(self, *, directory=None, name=None, extension=None):
        """
        Returns a different object with the specified changes applied to
        it. This object is not changed in the process.
        """
        path = self.getPath()
        if directory:
            new_directory = directory
        else:
            new_directory = os.path.dirname(path)

        if extension:
            new_extension = extension
        else:
            if name:
                new_extension = os.path.splitext(name)[EXTENSION]
            else:
                new_extension = os.path.splitext(path)[EXTENSION]

        if not new_extension:
            if not name:
                raise ValueError("You must provide an extension if "
                                 "one was not specified in the original "
                                 "'File' definition")
            else:
                raise ValueError("A name must include an extension with the "
                                 "file's base name")

        if new_extension[0] != '.':
            new_extension = '.' + new_extension

        # Now that we know there is an extension, that means basename == name
        # Name only exists if there is a file, else nope

        split = os.path.splitext(os.path.basename(path))
        if split[EXTENSION]:
            raw_name = split[NAME]
        else:
            raise ValueError("You cannot specify a different extension when "
                             "the original file path was a directory")

        filename = os.path.join(raw_name, new_extension)
        new_path = os.path.join(new_directory, filename)
        return File(new_path)

    def isOutDated(self, output_file):
        """
        Figures out if Cyther should compile the given FileInfo object by
        checking the both of the modified times
        """
        # TODO incorporate the getmtime method in here
        path = output_file.getPath()
        if os.path.exists(path):
            source_time = os.path.getmtime(self.getPath())
            output_time = os.path.getmtime(path)
            if source_time > output_time:
                return True
        else:
            return True
        return False

    def isUpdated(self, previous_modified_time):
        # TODO Why didn't I use abspath or normpath?
        """
        Figures out if the file had previously errored and hasn't
        been fixed since given a numerical time
        """
        modified_time = os.path.getmtime(self.getPath())
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
    new = file.create(extension='.p')
    print(new)
