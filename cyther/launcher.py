import subprocess
import traceback
import sys


"""
This file contains definitions for launching sets of commands into a subprocess
and handling its output correctly and efficiently
"""


class Result:
    """
    A class to hold the results of a command call. Holds stderr and stdout
    Contains useful functions to process them
    """
    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def getStdout(self):
        return self.stdout

    def getStderr(self):
        return self.stderr

    def getOutput(self):
        output = self.stdout
        if self.stdout:
            output += '\r\n'
        output += self.stderr
        return output

    def extendInformation(self, response):
        if response.stdout:
            self.stdout += '\r\n' + response.stdout
        if response.stderr:
            self.stderr += '\r\n' + response.stderr


def getEncodings():
    """
    Just a simple function to return the system encoding (defaults to utf-8)
    """
    stdout_encoding = sys.stdout.encoding if sys.stdout.encoding else 'utf-8'
    stderr_encoding = sys.stderr.encoding if sys.stderr.encoding else 'utf-8'
    return stdout_encoding, stderr_encoding


# TODO Make print_commands into an option instead of a function
def printCommands(*several_commands):
    for commands in several_commands:
        print(' '.join(commands).strip())


# TODO An option to raise a Exception as well? Is that useful?
def call(commands, *, print_result=False, raise_exception=False):
    """
    Will call a set of commands and wrangle the output how you choose
    """
    if raise_exception:
        print_result = False
    try:
        process = subprocess.Popen(commands,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

    except:
        output = traceback.format_exc()
        result = Result(1, '', output)
        if print_result and not raise_exception:
            print(output, file=sys.stderr)

    else:
        stdout_bytes, stderr_bytes = process.communicate()
        stdout_encoding, stderr_encoding = getEncodings()
        stdout = stdout_bytes.decode(stdout_encoding)
        stderr = stderr_bytes.decode(stderr_encoding)
        result = Result(process.returncode, stdout, stderr)

        if print_result and not raise_exception:
            if stdout:
                print(stdout, file=sys.stdout)
            if stderr:
                print(stderr, file=sys.stderr)

    if raise_exception and (result.returncode == 1):
        message = "An error occurred in an external process:\n\n{}"
        raise Exception(message.format(result.getStderr()))
    return result


# TODO Fix this docstring
def multiCall(*commands, print_result=False, dependent=True, bundle=False):
    """
    Calls the function 'call' multiple times, given sets of commands
    """
    results = []
    dependent_failed = False

    for command in commands:
        if not dependent_failed:
            response = call(command, print_result=print_result)
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
