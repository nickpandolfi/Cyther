

class CytherError(Exception):
    """A custom error used to denote that an exception was Cyther related"""
    def __init__(self, *args, **kwargs):
        super(CytherError, self).__init__(*args, **kwargs)


def isIterable(obj):
    """
    Returns a boolean denoting if the object passed in is iterable
    """
    try:
        _ = iter(obj)
    except TypeError:
        return False
    else:
        return True


MULTIPLE = 'multiple'
NONE = 'none'


def process_output(output, *, condense=False, one=False, default=None,
                   default_if_multiple=True, default_if_none=True):
    """
    Taking a iterative container (list, tuple), this function will process its
    contents and condense if necessary. It also has functionality to try to
    assure that the output has only one item in it if desired. If this is not
    the case, then it will return a 'default' in place of the output, if
    specified.
    """
    if condense:
        output = list(set(output))

    if one:
        if len(output) > 1:
            if default and default_if_multiple:
                output = default
            else:
                return MULTIPLE
        elif len(output) == 1:
            output = output[0]
        else:
            if default and default_if_none:
                return default
            else:
                return NONE

    return output


ASSERT_ERROR = "The search result:\n\t{}\nIs not equivalent to the assert " \
               "test provided:\n\t{}"


def assert_output(output, assert_equal):
    """
    Check that two outputs have the same contents as one another, even if they
    aren't sorted yet
    """
    sorted_output = sorted(output)
    sorted_assert = sorted(assert_equal)
    if sorted_output != sorted_assert:
        raise ValueError(ASSERT_ERROR.format(sorted_output, sorted_assert))


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
        key, value = line.split(':', maxsplit=1)
        obj[key] = eval(value)

    return obj


RESPONSES_ERROR = "Argument 'acceptableResponses' cannot be of type: '{}'"


def get_input(prompt, check, *, redo_prompt=None, repeat_prompt=False):
    """
    Ask the user to input something on the terminal level, check their response
    and ask again if they didn't answer correctly
    """
    if isinstance(check, str):
        check = (check,)

    to_join = []
    for item in check:
        if item:
            to_join.append(str(item))
        else:
            to_join.append("''")

    prompt += " [{}]: ".format('/'.join(to_join))

    if repeat_prompt:
        redo_prompt = prompt
    elif not redo_prompt:
        redo_prompt = "Incorrect input, please choose from {}: " \
                      "".format(str(check))

    if callable(check):
        def _checker(r): return check(r)
    elif isinstance(check, tuple):
        def _checker(r): return r in check
    else:
        raise ValueError(RESPONSES_ERROR.format(type(check)))

    response = input(prompt)
    while not _checker(response):
        print(response, type(response))
        response = input(redo_prompt if redo_prompt else prompt)
    return response


def get_choice(prompt, choices):
    """
    Asks for a single choice out of multiple items.
    Given those items, and a prompt to ask the user with
    """
    print()
    checker = []
    for offset, choice in enumerate(choices):
        number = offset + 1
        print("\t{}): '{}'\n".format(number, choice))
        checker.append(str(number))

    response = get_input(prompt, tuple(checker) + ('',))
    if not response:
        print("Exiting...")
        exit()

    offset = int(response) - 1
    selected = choices[offset]

    return selected


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
