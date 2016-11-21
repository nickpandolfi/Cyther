
import os
from .definitions import NOT_NEEDED_MESSAGE


class CytherError(Exception):
    """A custom error used to denote that an exception was Cyther related"""
    def __init__(self, *args, **kwargs):
        super(CytherError, self).__init__(*args, **kwargs)


RESPONSES_ERROR = "Argument 'acceptableResponses' cannot be of type: '{}'"


def getResponse(message, acceptableResponses):
    if isinstance(acceptableResponses, str):
        acceptableResponses = (acceptableResponses,)
    else:
        if not isinstance(acceptableResponses, tuple):
            raise ValueError(RESPONSES_ERROR.format(type(acceptableResponses)))

    response = input(message)
    while response not in acceptableResponses:
        response = input(message)
    return response


def getFullPath(filename):
    """
    Gets the full path of a filename
    Args:
        filename (str): Name of the file to be absolutized
    Returns:
        (CytherError): If the filename doesn't exist
        (str): The full path of the location of the filename
    """
    if os.path.exists(filename) and (filename not in os.listdir(os.getcwd())):
        ret = filename
    elif os.path.exists(os.path.join(os.getcwd(), filename)):
        ret = os.path.join(os.getcwd(), filename)
    else:
        raise CytherError("The file '{}' does not exist".format(filename))
    return ret


# TODO Make this automatic if 'numpy' is seen in the source code?
def getDirsToInclude(string):
    """
    Given a string of module names, it will return the 'include' directories
    essential to their compilation as long as the module has the conventional
    'get_include' function.
    """
    dirs = []
    a = string.strip()
    obj = a.split('-')

    if len(obj) == 1 and obj[0]:
        for module in obj:
            try:
                exec('import {}'.format(module))
            except ImportError:
                raise CytherError("The module '{}' does not"
                                  "exist".format(module))
            try:
                dirs.append('-I{}'.format(eval(module).get_include()))
            except AttributeError:
                print(NOT_NEEDED_MESSAGE.format(module))
    return dirs

