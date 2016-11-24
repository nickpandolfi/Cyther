import os

# TODO Change all 'filename's to 'filepath's

def isOutDated(file_path, output_name):
    """
    Figures out if Cyther should compile the given file by checking the source
    code and compiled object
    """
    if os.path.exists(output_name):
        source_time = os.path.getmtime(file_path)
        output_time = os.path.getmtime(output_name)
        if source_time > output_time:
            return True
    else:
        return True
    return False


def isUpdated(file_path, previous_modified_time):
    """
    Figures out if the file had previously errored and hasn't been fixed since
    """
    modified_time = os.path.getmtime(file_path)
    valid = modified_time > previous_modified_time
    return valid


# TODO Why didn't I use abspath or normpath?
def getFullPath(filename, *, error=True):
    """
    Gets the full path of a filename
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


def getParentDirectory(filename):
    return os.path.basename(os.path.dirname(filename))


def injectCache(filename):
    if getParentDirectory(filename) == '__cythercache__':
        raise FileExistsError("Can't put a cache in another cache")
    new_filename = os.path.join(os.path.dirname(filename),
                                '__cythercache__',
                                os.path.basename(filename))
    return new_filename


def joinExt(name, ext):
    if ext[0] == '.':
        ret = name + ext
    else:
        ret = name + '.' + ext
    return ret


def changeFileName(filename, new_name):
    dirname = os.path.dirname(filename)
    old_basename = os.path.basename(filename)
    new_basename = joinExt(new_name, os.path.splitext(old_basename)[1])
    return os.path.join(dirname, new_basename)


def changeFileDir(filename, dirname):
    return os.path.join(dirname, os.path.basename(filename))


def changeFileExt(filename, ext):
    return joinExt(os.path.splitext(filename)[0], ext)


class FileInfo:
    def __init__(self, file_name, file_type=None, file_location=None):
        """
        Exists location, [doesn't exist location],
        """
        path = getFullPath(file_name, error=False)
        if path:
            self.__file_name = os.path.basename(path)
            self.__file_type = os.path.splitext(path)[1]
            self.__file_location = os.path.dirname(path)
            self.__file_path = path
        else:
            if file_name and file_type and file_location:
                self.__file_name = file_name
                self.__file_type = file_type
                self.__file_location = file_location
                self.__file_path = os.path.join(self.__file_location,
                                                self.__file_name)
            else:
                raise ValueError("You must specify all parameters when the "
                                 "file '{}' cannot be found".format(file_name))

    def __str__(self):
        return self.__file_path

    def __repr__(self):
        return self.__file_path

    def getName(self):
        return self.__file_name

    def getType(self):
        return self.__file_type

    def getLocation(self):
        return self.__file_location

    def getPath(self):
        return self.__file_path

if __name__ == '__main__':
    file = FileInfo('README.md')
    print(file.getType())
