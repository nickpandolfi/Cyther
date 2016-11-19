
import os
import re
import argparse


class CytherError(Exception):
    """A custom error used to denote that an exception was Cyther related"""
    def __init__(self, *args, **kwargs):
        super(CytherError, self).__init__(*args, **kwargs)

try:
    from shutil import which
except ImportError:
    raise CytherError("The current version of Python doesn't support the function 'which', normally located in shutil")


def getResponse(message, acceptableResponses):
    if isinstance(acceptableResponses, str):
        acceptableResponses = (acceptableResponses,)
    else:
        if not isinstance(acceptableResponses, tuple):
            raise ValueError("Argument 'acceptableResponses' cannot be of type: '{}'".format(type(acceptableResponses)))

    response = input(message)
    while response not in acceptableResponses:
        response = input(message)
    return response


def commandsFromFile(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    #to be updated with more functionality to mimic GNU's 'makefile' system
    return lines


def commandsToFile(filename, commands):
    with open(filename, 'w+') as file:
        chars = file.write(commands.join('\n'))
    #to be updated with more functionality to mimic GNU's 'makefile' system
    return chars


def where(cmd, path=None):
    """
    A function to wrap shutil.which for universal usage
    Args:
        cmd (str): The command wished to be traced back to its source
        path: A pathin which to limit the results to
    Returns:
        (CytherError): If could not find
        (str): The abspath of the executable found
    """
    raw_result = which(cmd, os.X_OK, path)
    if raw_result:
        return os.path.abspath(raw_result)
    else:
        raise CytherError("Could not find '{}' in the path".format(cmd))


def sift(obj):
    """
    Used to find the correct static lib name to pass to gcc
    Args:
        obj (list): The list of names of runtime directories to include

    Returns (str): The proper name of the argument passed into the '-l' option
    """
    string = [str(item) for name in obj for item in os.listdir(name)]
    s = set(re.findall('(?<=lib)(.+?)(?=\.so|\.a)', '\n'.join(string)))
    result = max(list(s), key=len)
    return result


POUND_EXTRACT = re.compile(r"(?:#\s*@\s?[Cc]yther\s+)(?P<content>.+?)(?:\s*)(?:\n|$)")
TRIPPLE_EXTRACT = re.compile(r"(?:(?:''')(?:(?:.|\n)+?)@[C|c]yther\s+)(?P<content>(?:.|\n)+?)(?:\s*)(?:''')")


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

