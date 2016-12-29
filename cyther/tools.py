

class CytherError(Exception):
    """A custom error used to denote that an exception was Cyther related"""
    def __init__(self, *args, **kwargs):
        super(CytherError, self).__init__(*args, **kwargs)


def write_dict_to_file(file_path, obj):
    """
    Write a dictionary of string keys to a file
    """
    lines = []
    for key, value in obj.items():
        lines.append(key + ':' + repr(value) + '\n')

    with open(file_path, 'w+') as file:
        file.writelines(lines)

    return None


def read_dict_from_file(file_path):
    """
    Read a dictionary of strings from a file
    """
    with open(file_path) as file:
        lines = file.read().splitlines()

    obj = {}
    for line in lines:
        key, value = line.split(':')
        obj[key] = eval(value)

    return obj


RESPONSES_ERROR = "Argument 'acceptableResponses' cannot be of type: '{}'"


# TODO Make get_input take the 'check' parameter and inject it into the prompt
def get_input(prompt, check, *, redo_prompt=None):
    """
    Ask the user to input something on the terminal level, check their response
    and ask again if they didn't answer correctly
    """
    if isinstance(check, str):
        check = (check,)

    if callable(check):
        def checker(r): return check(r)
    elif isinstance(check, tuple):
        def checker(r): return r in check
    else:
        raise ValueError(RESPONSES_ERROR.format(type(check)))

    response = input(prompt)
    while not checker(response):
        response = input(redo_prompt if redo_prompt else prompt)
    return response


def _removeGivensFromTasks(tasks, givens):
    for given in givens:
        if given in tasks:
            raise Exception("Task '{}' is not supposed to be a"
                            " given".format(given))
        for task in tasks:
            if given in tasks[task]:
                tasks[task].remove(given)


def generateBatches(tasks, givens):
    """
    A function to generate a batch of commands to run in a specific order as to
    meet all the dependencies for each command. For example, the commands with
    no dependencies are run first, and the commands with the most deep
    dependencies are run last
    """
    _removeGivensFromTasks(tasks, givens)

    batches = []
    while tasks:
        batch = set()
        for task, dependencies in tasks.items():
            if not dependencies:
                batch.add(task)

        if not batch:
            _batchErrorProcessing(tasks)

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


def _batchErrorProcessing(tasks):
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
