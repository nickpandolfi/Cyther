
import os
import re
import sys
import traceback
import subprocess
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


def polymorph(func):
    def wrapped(*args, **kwargs):
        if kwargs:
            args = argparse.Namespace()
            args.__dict__.update(kwargs)
        return func(args)
    return wrapped


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


def printCommands(*several_commands):
    """
    Simply prints several commands given to it
    Args:
        *several_commands (list|tuple): Container of commands
    Returns: None
    """
    for commands in several_commands:
        print(' '.join(commands).strip())


def call(commands):
    """
    Super handy function to open another process
    Args:
        commands (list|tuple): The commands wished to open a new process with
    Returns (dict): The status of the call. Keys are 'returncode', and 'output'
    """
    try:
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        output = traceback.format_exc()
        return {'returncode': 1, 'output': output}

    stdout_bytes, stderr_bytes = process.communicate()
    stdout_encoding = sys.stdout.encoding if sys.stdout.encoding else 'utf-8'
    stderr_encoding = sys.stderr.encoding if sys.stderr.encoding else 'utf-8'
    stdout = stdout_bytes.decode(stdout_encoding)
    stderr = stderr_bytes.decode(stderr_encoding)
    code = process.returncode

    output = ''
    if stdout:
        output += stdout + '\r\n'
    output += stderr

    result = {'returncode': code, 'output': output}
    return result


def multiCall(*commands, dependent=True):
    """
    Calls 'call' multiple times, given sets of commands
    Args:
        *commands (list|tuple): The sets of commands to be called with
        dependent (bool): If one set fails, it forces the rest to fail, and return None
    Returns (dict): The combined results of the series of calls. Keys are same as 'call'
    """
    results = []
    dependent_failed = False

    for command in commands:
        if not dependent_failed:
            result = call(command)
            if (result['returncode'] == 1) and dependent:
                dependent_failed = True
        else:
            result = None
        results.append(result)

    obj = {'returncode': 0, 'output': ''}
    for result in results:
        if not result:
            continue
        elif result['returncode'] == 1:
            obj['returncode'] = 1
        obj['output'] += result['output']
    return obj
