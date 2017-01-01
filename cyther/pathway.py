
"""
This module holds the utilities necessary to process full path names and hold
their parsed information, so other tools can easily extract this information
(i.e. extension), and hold the information in a containers better designed
for it
"""

import os
import time

APPEND_SEP_TO_DIRS = True

DRIVE = 0
REST = 1

NAME = 0
EXTENSION = 1

ISFILE = True
ISDIR = False

EXT = '.'
USER = '~'


class OverwriteError(Exception):
    """
    Denotes if the user tried to overwrite a part of a file without giving
    explicit permission
    """
    def __init__(self, *args, **kwargs):
        super(OverwriteError, self).__init__(*args, **kwargs)


def normalize(path_name, override=None):
    """
    Prepares a path name to be worked with. Path name must not be empty. This
    function will return the 'normpath'ed path and the identity of the path.
    This function takes an optional overriding argument for the identity.

    ONLY PROVIDE OVERRIDE IF:
        1) YOU AREWORKING WITH A FOLDER THAT HAS AN EXTENSION IN THE NAME
        2) YOU ARE MAKING A FILE WITH NO EXTENSION
    """

    identity = identify(path_name, override=override)
    new_path_name = os.path.normpath(os.path.expanduser(path_name))

    return new_path_name, identity


def identify(path_name, *, override=None, check_exists=True, default=ISDIR):
    """
    Identify the type of a given path name (file or directory). If check_exists
    is specified to be false, then the function will not set the identity based
    on the path existing or not. If override is specified as either ISDIR or
    ISFILE, then the function will try its best to over-ride the identity to be
    what you have specified. The 'default' parameter is what the function will
    default the identity to if 'override' is not specified, and the path looks
    like it could be both a directory and a file.
    """

    head, tail = os.path.split(path_name)

    if check_exists and os.path.exists(path_name):
        if os.path.isfile(path_name):
            if override == ISDIR:
                raise ValueError("Cannot override a path as a directory if it "
                                 "is a file that already exists")
            result = ISFILE
        elif os.path.isdir(path_name):
            if override == ISFILE:
                raise ValueError("Cannot override a path as a file if it is "
                                 "a directory that already exists")
            result = ISDIR
        else:
            raise Exception("Path exists but isn't a file or a directory...")
    elif not tail:
        if override == ISFILE:
            raise ValueError("Cannot interpret a path with a slash at the end "
                             "to be a file")
        result = ISDIR
    elif has_ext(tail, if_all_ext=True):
        if override is None:
            result = ISFILE
        else:
            result = override
    else:
        if override is None:
            result = default
        else:
            result = override

    return result


def join_ext(name, extension):
    """
    Joins a given name with an extension. If the extension doesn't have a '.'
    it will add it for you
    """
    if extension[0] == EXT:
        ret = name + extension
    else:
        ret = name + EXT + extension
    return ret


def get_drive(path_name):
    """
    Gets the part of the path that specified the drive. If this cannot be found
    it will return an empty string
    """
    return os.path.splitdrive(path_name)[DRIVE]


def has_ext(path_name, *, multiple=None, if_all_ext=False):
    """
    Determine if the given path name has an extension
    """
    base = os.path.basename(path_name)
    count = base.count(EXT)

    if not if_all_ext and base[0] == EXT and count != 0:
        count -= 1

    if multiple is None:
        return count >= 1
    elif multiple:
        return count > 1
    else:
        return count == 1


def get_ext(path_name, *, if_all_ext=False):
    """
    Get an extension from the given path name. If an extension cannot be found,
    it will return an empty string
    """
    if has_ext(path_name):
        return os.path.splitext(path_name)[EXTENSION]
    elif if_all_ext and has_ext(path_name, if_all_ext=True):
        return os.path.splitext(path_name)[NAME]
    else:
        return ''


def has_dir(path_name):
    """
    Determine if the given path name contains a directory part, even if the
    path refers to a file
    """
    return bool(os.path.dirname(path_name))


def get_dir(path_name, *, greedy=False, override=None, identity=None):
    """
    Gets the directory path of the given path name. If the argument 'greedy'
    is specified as True, then if the path name represents a directory itself,
    the function will return the whole path
    """
    if identity is None:
        identity = identify(path_name, override=override)

    path_name = os.path.normpath(path_name)

    if greedy and identity == ISDIR:
        return path_name
    else:
        return os.path.dirname(path_name)


def get_parent(path_name):
    """
    Gets the parent directory of the given path name
    """
    return os.path.basename(os.path.dirname(path_name))


def get_name(path_name, *, ext=True, override=None, identity=None):
    """
    Gets the name par of the path name given. By 'name' I mean the basename of
    a filename's path, such as 'test.o' in the path: 'C:/test/test.o'
    """
    if identity is None:
        identity = identify(path_name, override=override)

    if identity == ISFILE:
        if ext:
            r = os.path.basename(path_name)
        else:
            r = os.path.splitext(os.path.basename(path_name))[NAME]
    else:
        r = ''
    return r


def disintegrate(path_name):
    """
    Disintegrates the path name by splitting all of the components apart
    """
    return os.path.normpath(path_name).split(os.sep)


def get_system_drives():
    """
    Get the available drive names on the system. Always returns a list.
    """
    drives = []
    if os.name == 'nt':
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        letter = ord('A')
        while bitmask > 0:
            if bitmask & 1:
                name = chr(letter) + ':\\'
                if os.path.isdir(name):
                    drives.append(name)
            bitmask >>= 1
            letter += 1
    else:
        drives.append(get_drive(os.getcwd()))

    return drives


def has_suffix(path_name, suffix):
    """
    Determines if path_name has a suffix of at least 'suffix'
    """
    if isinstance(suffix, str):
        suffix = disintegrate(suffix)

    components = disintegrate(path_name)

    for i in range(-1, -(len(suffix) + 1), -1):
        if components[i] != suffix[i]:
            break
    else:
        return True
    return False

###########################################################################


def _initialize(path_name, override, root, inject):
    if path_name:
        if isinstance(path_name, list) or isinstance(path_name, tuple):
            path_name = os.path.join(*path_name)
        elif not isinstance(path_name, str):
            raise ValueError("Parameter 'path_name' must be of "
                             "type str, list, tuple, or NoneType, "
                             "not {}".format(type(path_name)))
        path_name, identity = normalize(path_name, override)
    else:
        identity = None

    if root:
        root, root_identity = normalize(root)
        if root_identity == ISFILE:
            raise ValueError("Parameter 'root' cannot be a file")
        elif not os.path.isabs(root):
            raise ValueError("The root must be an absolute directory if "
                             "specified")
        elif path_name and os.path.isabs(path_name):
            raise ValueError("The path cannot be absolute as well as the r"
                             "oot; cannot add two absolute paths together")

    if inject and identify(inject) == ISFILE:
        raise ValueError("Parameter 'inject' must be a directory")

    return path_name, identity, root


def _process_name(path_name, identity, name, ext):
    if name or ext or (identity == ISFILE):
        if identity == ISFILE:
            if name:
                raise OverwriteError("The path supplied must be a directory, "
                                     "if you provide a name")
            else:
                file_name = get_name(path_name, identity=ISFILE, ext=True)
                if ext:
                    new_name = join_ext(file_name, ext)
                else:
                    new_name = file_name
        else:
            if name:
                if ext:
                    new_name = join_ext(name, ext)
                else:
                    new_name = name
            else:
                new_name = join_ext('', ext)
    else:
        new_name = ''

    return new_name


def _process_directory(path_name, identity, root, inject):
    if root:
        if path_name:
            new_directory = os.path.join(root, get_dir(path_name,
                                                       identity=identity,
                                                       greedy=True))
        else:
            new_directory = root
    else:
        cwd = os.getcwd()
        if path_name and (has_dir(path_name) or identity == ISDIR):
            dir_extension = get_dir(path_name, identity=identity, greedy=True)
            if os.path.isabs(path_name):
                new_directory = dir_extension
            else:
                new_directory = os.path.join(cwd, dir_extension)
        else:
            new_directory = cwd

    if inject:
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

        if get_drive(path_name) != get_drive(start):
            raise ValueError("Calculating relpath requires that the "
                             "comparator path is of the same drive")

        new_path = os.path.relpath(path_name, start=start)

        if reduce and (len(new_path) >= len(path_name)):
            result = path_name
        else:
            result = new_path

    return result


# TODO Will '~' mean anything on a system with no user specified? Possible?
def path(path_name=None, override=None, *, root=None, name=None, ext=None,
         inject=None, relpath=None, reduce=False):
    """
    Path manipulation black magic
    """
    path_name, identity, root = _initialize(path_name, override, root, inject)
    new_name = _process_name(path_name, identity, name, ext)
    new_directory = _process_directory(path_name, identity, root, inject)
    full_path = os.path.normpath(os.path.join(new_directory, new_name))
    if APPEND_SEP_TO_DIRS and not new_name and full_path[-1] != os.sep:
        full_path += os.sep
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
        return get_name(self.getPath(), ext=ext)

    def getExtension(self):
        """
        Returns the type of the file (its extension) with the '.'
        """
        return get_ext(self.getPath())

    def getDirectory(self):
        """
        Returns the parent directory of the file
        """
        return get_dir(self.getPath())

    def getPath(self):
        """
        Returns the full file path to the file, including the drive
        """
        return self.__path
