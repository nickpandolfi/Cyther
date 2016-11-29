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


"""
1) Make a function to tell is something is a directory or a file
    This function could try to autodetect by doing isdir() or isfile()
2) Make something like dirname(), but it returns the entire directory part
    (Uses the previous function)
    Meaning that new_dirname('yolo/swag') would return: 'yolo/swag'

When combining the two functions, make it so that the following code is run if
the directory OR the name OR the extension is changed. Run this function,
then normalize the paths!

if name
    If path has a name already
        ERROR (It must be a directory)

    If name has an extension
        if ext is given
            ERROR (cannot overwrite the name's extension, strip it first)
        NEW_NAME == name
    else
        NEW_NAME == name + given_ext
else
    if path is a file, extract file name
        NEW_NAME
    else
        ERROR (path is a directory, no name exists)

If directory
    NEW_DIRECTORY = directory + dirname(path)
else
    If path is a directory
        NEW_DIRECTORY = path
    else
        split the directory off (NEW_DIRECTORY = split off directory)

File(NEW_DIRECTORY, NEW_NAME)
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
