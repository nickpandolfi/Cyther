
import os
import re
import shutil

from .tools import CytherError


def where(cmd, path=None):
    """
    A function to wrap shutil.which for universal usage
    """
    raw_result = shutil.which(cmd, os.X_OK, path)
    if raw_result:
        return os.path.abspath(raw_result)
    else:
        raise CytherError("Could not find '{}' in the path".format(cmd))


def sift(obj):
    """
    Used to find the correct static lib name to pass to gcc
    """
    string = [str(item) for name in obj for item in os.listdir(name)]
    s = set(re.findall('(?<=lib)(.+?)(?=\.so|\.a)', '\n'.join(string)))
    result = max(list(s), key=len)
    return result


POUND_EXTRACT = re.compile(r"(?:#\s*@\s?[Cc]yther\s+)(?P<content>.+?)(?:\s*)(?:\n|$)")
TRIPPLE_EXTRACT = re.compile(r"(?:(?:''')(?:(?:.|\n)+?)@[C|c]yther\s+)(?P<content>(?:.|\n)+?)(?:\s*)(?:''')")