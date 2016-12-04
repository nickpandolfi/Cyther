import os
import re
import shutil

from .tools import CytherError

MORE_THAN_ONE_REGEX = "More than one pattern found for regex pattern: '{}' " \
                      "for output:\n\t{}"


def where(cmd, path=None):
    """
    A function to wrap shutil.which for universal usage
    """
    raw_result = shutil.which(cmd, os.X_OK, path)
    if raw_result:
        return os.path.abspath(raw_result)
    else:
        raise CytherError("Could not find '{}' in the path".format(cmd))


def extract(pattern, string,
            allow_only_one=False, condense=False,
            error_if_none=False, default=None,
            assert_equal=None, message=None):
    """
    Used by extract to filter the entries in the searcher results
    """
    output = []
    for match in re.finditer(pattern, string):
        output.append(match.group('content'))

    if not output:
        if error_if_none:
            if not message:
                message = "No matches for pattern '{}' could be " \
                          "found in output:\n\t{}".format(pattern, output)
            raise LookupError(message)
        else:
            if default:
                output = default
            else:
                output = None
    else:
        if condense:
            output = list(set(output))

        if allow_only_one:
            if len(output) > 1:
                raise ValueError(MORE_THAN_ONE_REGEX.format(pattern,
                                                            output))
            output = output[0]

    if assert_equal:
        sorted_output = sorted(output)
        sorted_assert = sorted(assert_equal)
        if sorted_output != sorted_assert:
            if not message:
                message = "The search result:\n\t{}\nIs not equivalent " \
                          "to the assert test provided:" \
                          "\n\t{}".format(sorted_output, sorted_assert)
            raise ValueError(message)
    else:
        return output


def sift(obj):
    """
    Used to find the correct static lib name to pass to gcc
    """
    names = [str(item) for name in obj for item in os.listdir(name)]
    string = '\n'.join(names)
    filterMatches(condense=True)
    return result


RUNTIME_PATTERN = r"(?<=lib)(?P<content>.+?)(?=\.so|\.a)"
POUND_PATTERN = r"#\s*@\s?[Cc]yther +(?P<content>.+?)\s*?(\n|$)"
TRIPPLE_PATTERN = r"(?P<quote>'{3}|\"{3})(.|\n)+?@[Cc]yther\s+(?P<content>(.|\n)+?)\s*(?P=quote)"
VERSION_PATTERN = r"[Vv]ersion:?\s+(?P<content>([0-9]+\.){1,}((dev)?[0-9]+))"
