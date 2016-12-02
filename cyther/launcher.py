
"""
This module contains definitions for launching sets of commands into a
subprocess and handling its output correctly and efficiently
"""

import subprocess
import traceback
import sys
import re


MORE_THAN_ONE_REGEX = "More than one pattern found for regex string: '{}'"


class Result:
    """
    A class to hold the results of a command call. Holds stderr and stdout
    Contains useful functions to process them
    """
    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return self.getOutput()

    def extract(self, pattern, *, only_one=True,
                allow_same=True, condense=True,
                none_error=False):
        """
        Given a regex string, it will find all of the occurences in the output
        """
        searcher = re.compile(pattern)
        output = searcher.findall(self.getOutput())
        if only_one and len(output) > 1:
            all_same = True
            compare = output[0]
            for item in output:
                if item != compare:
                    all_same = False

            if not (allow_same and all_same):
                raise ValueError(MORE_THAN_ONE_REGEX.format(pattern))
            else:
                if condense:
                    output = compare
        else:
            if condense:
                output = list(set(output))
                if len(output) == 1:
                    output = output[0]
        if not output:
            if none_error:
                raise LookupError("No matches for pattern '{}' could "
                                  "be found".format(pattern))
            else:
                output = None
        return output

    def extractVersion(self):
        """
        Extracts a three digit standard format version number
        """
        return self.extract(r'[0-9]\.[0-9]\.[0-9]', none_error=True)

    def getStdout(self):
        """
        Returns stdout
        """
        return self.stdout

    def getStderr(self):
        """
        Returns stderr
        """
        return self.stderr

    def getOutput(self):
        """
        Returns the combined output of stdout and stderr
        """
        output = self.stdout
        if self.stdout:
            output += '\r\n'
        output += self.stderr
        return output

    def extendInformation(self, response):
        """
        This extends the objects stdout and stderr by
        'response's stdout and stderr
        """
        if response.stdout:
            self.stdout += '\r\n' + response.stdout
        if response.stderr:
            self.stderr += '\r\n' + response.stderr


def _get_encodings():
    """
    Just a simple function to return the system encoding (defaults to utf-8)
    """
    stdout_encoding = sys.stdout.encoding if sys.stdout.encoding else 'utf-8'
    stderr_encoding = sys.stderr.encoding if sys.stderr.encoding else 'utf-8'
    return stdout_encoding, stderr_encoding


# TODO Make print_commands into an option instead of a function
def _print_commands(*several_commands):
    """
    Prints a list of commands given
    """
    for commands in several_commands:
        print(' '.join(commands).strip())


def _extract_output(process, print_result, raise_exception):
    stdout_bytes, stderr_bytes = process.communicate()
    stdout_encoding, stderr_encoding = _get_encodings()
    stdout = stdout_bytes.decode(stdout_encoding)
    stderr = stderr_bytes.decode(stderr_encoding)
    result = Result(process.returncode, stdout, stderr)

    if print_result and not raise_exception:
        if stdout:
            print(stdout, file=sys.stdout)
        if stderr:
            print(stderr, file=sys.stderr)
    return result


# TODO An option to raise a Exception as well? Is that useful?
def call(commands, *, print_result=False, raise_exception=False,
         print_commands=False):
    """
    Will call a set of commands and wrangle the output how you choose
    """
    if isinstance(commands, str):
        commands = commands.split()

    if not (isinstance(commands, tuple) or
            isinstance(commands, list)):
        raise ValueError("Function 'call' does not accept a 'commands'"
                         "argument of type '{}'".format(type(commands)))

    if raise_exception:
        print_result = False
    try:
        process = subprocess.Popen(commands,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        if print_commands:
            _print_commands(commands)

    except:
        output = traceback.format_exc()
        result = Result(1, stderr=output)
        if print_result and not raise_exception:
            print(output, file=sys.stderr)

    else:
        result = _extract_output(process, print_result, raise_exception)

    if raise_exception and (result.returncode == 1):
        message = "An error occurred in an external process:\n\n{}"
        raise Exception(message.format(result.getStderr()))
    return result


# TODO Should I pass on the argument 'raise_exception' to call?
def multiCall(*commands, dependent=True, bundle=False,
              print_result=False, print_commands=False):
    """
    Calls the function 'call' multiple times, given sets of commands
    """
    results = []
    dependent_failed = False

    for command in commands:
        if not dependent_failed:
            response = call(command, print_result=print_result,
                            print_commands=print_commands)
            # TODO Will an error ever return a code other than '1'?
            if (response.returncode == 1) and dependent:
                dependent_failed = True
        else:
            response = None
        results.append(response)

    if bundle:
        result = Result()
        for response in results:
            if not response:
                continue
            elif response.returncode == 1:
                result.returncode = 1

            result.extendInformation(response)
        processed_response = result
    else:
        processed_response = results

    return processed_response

