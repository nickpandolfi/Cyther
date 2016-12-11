
from .definitions import NOT_NEEDED_MESSAGE, RESPONSES_ERROR


class CytherError(Exception):
    """A custom error used to denote that an exception was Cyther related"""
    def __init__(self, *args, **kwargs):
        super(CytherError, self).__init__(*args, **kwargs)


def getResponse(message, acceptableResponses):
    """
    Ask the user to input something on the terminal level, check their response
    and ask again if they didn't answer correctly
    """
    if isinstance(acceptableResponses, str):
        acceptableResponses = (acceptableResponses,)
    else:
        if not isinstance(acceptableResponses, tuple):
            raise ValueError(RESPONSES_ERROR.format(type(acceptableResponses)))

    response = input(message)
    while response not in acceptableResponses:
        response = input(message)
    return response


# TODO What about the __file__ attribute
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
                raise FileNotFoundError("The module '{}' does not"
                                        "exist".format(module))
            try:
                dirs.append('-I{}'.format(eval(module).get_include()))
            except AttributeError:
                print(NOT_NEEDED_MESSAGE.format(module))
    return dirs


def removeGivensFromTasks(tasks, givens):
    for given in givens:
        if given in tasks:
            raise Exception("Task '{}' is not supposed to be a"
                            " given".format(given))
        for task in tasks:
            if given in tasks[task]:
                tasks[task].remove(given)


def generateBatches(tasks, givens):
    removeGivensFromTasks(tasks, givens)

    batches = []
    while tasks:
        batch = set()
        for task, dependencies in tasks.items():
            if not dependencies:
                batch.add(task)

        if not batch:
            batchErrorProcessing(tasks)

        for task in batch:
            del tasks[task]

        for task, dependencies in tasks.items():
            for item in batch:
                if item in dependencies:
                    tasks[task].remove(item)

        batches.append(batch)
    return batches


GIVENS_NOT_SPECIFIED = "The dependencies '{}' should be givens if not " \
                       "specified as tasks"


def batchErrorProcessing(tasks):
    should_be_givens = []
    total_deps = {dep for deps in tasks.values() for dep in deps}
    for dep in total_deps:
        if dep not in tasks:
            should_be_givens.append(dep)

    if should_be_givens:
        string = ', '.join(should_be_givens)
        message = GIVENS_NOT_SPECIFIED.format(string)
    else:
        message = "Circular dependency found:\n\t"
        msg = []
        for task, dependencies in tasks.items():
            for parent in dependencies:
                line = "{} -> {}".format(task, parent)
                msg.append(line)
        message += "\n\t".join(msg)

    raise ValueError(message)
