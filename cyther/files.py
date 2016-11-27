
"""
This module holds the utilities necessary to process full path names and hold
their parsed information, so other tools can easily extract this information
(i.e. extension), and hold the information in a containers better designed
for it
"""

import os

# TODO Change all 'filename's to 'filepath's

NULL_FILE_NAME = 'NULL.abc'


def getFullPath(filename, *, error=True):
    """
    Gets the full path of a filename relative to the drive it is on
    """
    cwd = os.getcwd()
    if os.path.exists(filename) and (filename not in os.listdir(cwd)):
        full_path = filename
    elif os.path.exists(os.path.join(cwd, filename)):
        full_path = os.path.join(cwd, filename)
    else:
        if error:
            raise FileNotFoundError("The file '{}' does not"
                                    " exist".format(filename))
        else:
            full_path = None
    return full_path


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


class File:
    """
    Holds all of the information and methods necessary to process full paths.
    Takes a path name and an optional constructor to build a file name on
    if it does not exist already.
    """
    def __init__(self, path=None, construction_dir=None):
        """If the path doesn't yet exist, it must be a FULL path!!"""
        if path:
            full_path = getFullPath(path, error=False)
            if not full_path:
                if not construction_dir:
                    construction_dir = os.getcwd()
                full_path = os.path.join(construction_dir, path)
        else:
            full_path = os.path.join(os.getcwd(), NULL_FILE_NAME)

        self.__file_name = os.path.basename(full_path)
        self.__file_type = os.path.splitext(full_path)[1]
        self.__file_location = os.path.dirname(full_path)
        self.__file_path = full_path

    def __str__(self):
        return self.__file_path

    def convertTo(self, *, directory=None, name=None, extension=None,
                  inject_cache=False):
        """
        Returns a different object with the specified changes applied to
        it. This object is not changed in the process.
        """
        path = self.getPath()
        if directory:
            path = changeFileDir(path, directory)
        if name:
            path = changeFileName(path, name)
        if extension:
            path = changeFileExt(path, extension)
        if inject_cache:
            path = injectCache(path)
        return File(path)

    def isOutDated(self, output_file):
        """
        Figures out if Cyther should compile the given FileInfo object by
        checking the both of the modified times
        """
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
    file = File('README.md')
    print(file.getType())
