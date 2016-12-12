
"""
This module contains the definitions necessary to parse sets of instructions in
string form and return a simple attribute object holding everything
"""


INSTRUCTION_HAS_WHITESPACE = "Cannot parse an instruction with whitespace"
INCOMPLETE_SET = "There must be one set of '{},{}' to finish " \
                 "the dependency definition"
INCORRECT_SET_CONSTITUENT = "There can only be one '{}' in a " \
                            "dependency definition"
MORE_THAN_ONE_SET = "An instruction can only have a maximum of one set of " \
                    "'{},{}', denoting the dependencies"
DEPENDENCIES_NOT_FIRST = "An instruction with dependencies must have " \
                         "them defined first"
OPTIONS_NOT_LAST = "An instruction with building options must have them " \
                   "defined last"
MULTIPLE_CONFLICTING_BUILD_OPTIONS = "There can only be one of each " \
                                     "building option per instruction"
EMPTY_PARAMETER = "Cannot have an empty parameter"
EMPTY_KEYWORD_PARAMETER = "Cannot have an empty keyword parameter"
MULTIPLE_FLOW_OPERATORS = "An instruction can only have one '>' in the " \
                          "task name"
FLOW_OPERATOR_ON_ENDS = "Greater than character (flow operator) must " \
                        "seperate filenames"


def _get_contents_between(string, opener, closer):
    """
    Get the contents of a string between two characters
    """
    opener_location = string.index(opener)
    closer_location = string.index(closer)
    content = string[opener_location + 1:closer_location]
    return content


def _check_whitespace(string):
    """
    Make sure thre is no whitespace in the given string. Will raise a
    ValueError if whitespace is detected
    """
    if string.count(' ') + string.count('\t') + string.count('\n') > 0:
        raise ValueError(INSTRUCTION_HAS_WHITESPACE)


def _check_enclosing_characters(string, opener, closer):
    """
    Makes sure that the enclosing characters for a definition set make sense
    1) There is only one set
    2) They are in the right order (opening, then closing)
    """
    opener_count = string.count(opener)
    closer_count = string.count(closer)
    total = opener_count + closer_count
    if total > 2:
        msg = MORE_THAN_ONE_SET.format(opener, closer)
        raise ValueError(msg)
    elif total == 1:
        msg = INCOMPLETE_SET.format(opener, closer)
        raise ValueError(msg)
    elif opener_count > 1:
        msg = INCORRECT_SET_CONSTITUENT.format(opener)
        raise ValueError(msg)
    elif closer_count > 1:
        msg = INCORRECT_SET_CONSTITUENT.format(closer)
        raise ValueError(msg)


def _check_parameters(parameters, symbols):
    """
    Checks that the parameters given are not empty. Ones with prefix symbols
    can be denoted by including the prefix in symbols
    """
    for param in parameters:
        if not param:
            raise ValueError(EMPTY_PARAMETER)
        elif (param[0] in symbols) and (not param[1:]):
            print(param)
            raise ValueError(EMPTY_KEYWORD_PARAMETER)


def _check_dependencies(string):
    """
    Checks the dependencies constructor. Looks to make sure that the
    dependencies are the first things defined
    """
    opener, closer = '(', ')'
    _check_enclosing_characters(string, opener, closer)
    if opener in string:
        if string[0] != opener:
            raise ValueError(DEPENDENCIES_NOT_FIRST)
        ret = True
    else:
        ret = False
    return ret


def _check_building_options(string):
    """
    Checks the building options to make sure that they are defined last,
    after the task name and the dependencies
    """
    opener, closer = '{', '}'
    _check_enclosing_characters(string, opener, closer)
    if opener in string:
        if string[-1] != closer:
            raise ValueError(OPTIONS_NOT_LAST)
        ret = True
    else:
        ret = False
    return ret


def _check_flow_operator(string):
    """
    Checks the flow operator ('>') to make sure that it:
    1) Is non empty
    2) There is only one of them
    """
    greater_than_count = string.count('>')
    if greater_than_count > 1:
        raise ValueError(MULTIPLE_FLOW_OPERATORS)
    elif (string[0] == '>') or (string[-1] == '>'):
        raise ValueError(FLOW_OPERATOR_ON_ENDS)
    else:
        if greater_than_count == 1:
            ret = True
        else:
            ret = False
    return ret


def _parse_dependencies(string):
    """
    This function actually parses the dependencies are sorts them into
    the buildable and given dependencies
    """
    contents = _get_contents_between(string, '(', ')')
    unsorted_dependencies = contents.split(',')
    _check_parameters(unsorted_dependencies, ('?',))

    buildable_dependencies = []
    given_dependencies = []
    for dependency in unsorted_dependencies:
        if dependency[0] == '?':
            given_dependencies.append(dependency[1:])
        else:
            buildable_dependencies.append(dependency)

    string = string[string.index(')') + 1:]
    return buildable_dependencies, given_dependencies, string


def _parse_building_options(string):
    """
    This will parse and sort the building options defined in the '{}'
    constructor. Will only allow one of each argument
    """
    contents = _get_contents_between(string, '{', '}')
    unsorted_options = contents.split(',')
    _check_parameters(unsorted_options, ('@', '/', '\\', '^'))

    output_directory = None
    output_format = None
    building_directory = None
    for option in unsorted_options:
        if option[0] == '@':
            if output_format:
                raise ValueError(MULTIPLE_CONFLICTING_BUILD_OPTIONS)
            output_format = option[1:]
        elif option[0] in ('/', '\\'):
            if output_directory:
                raise ValueError(MULTIPLE_CONFLICTING_BUILD_OPTIONS)
            output_directory = option[1:]
        elif option[0] == '^':
            if building_directory:
                raise ValueError(MULTIPLE_CONFLICTING_BUILD_OPTIONS)
            building_directory = option[1:]

    string = string[:string.index('{')]
    return output_directory, output_format, building_directory, string


"""
(example_file.o)[yolo.pyx]{^local} example_file.pyx{o}

Starting Point (task_name is the filename!)
    [Intermediate steps]
    Endpoint
"""


def parseString(string):
    """
    This function takes an entire instruction in the form of a string, and
    will parse the entire string and return a dictionary of the fields
    gathered from the parsing
    """
    buildable_dependencies = []
    given_dependencies = []
    output_directory = None
    output_format = None
    building_directory = None
    output_name = None

    _check_whitespace(string)

    there_are_dependencies = _check_dependencies(string)
    if there_are_dependencies:
        buildable_dependencies, \
            given_dependencies, \
            string = _parse_dependencies(string)

    there_are_options = _check_building_options(string)
    if there_are_options:
        output_directory, \
            output_format, \
            building_directory, string = _parse_building_options(string)

    if string[0] == '>':
        string = string[1:]
    if string[-1] == '>':
        string = string[:-1]

    is_a_flow_operator = _check_flow_operator(string)
    if is_a_flow_operator:
        greater_than_location = string.index('>')
        output_name = string[greater_than_location + 1:]
        string = string[:greater_than_location]

    ret = object()
    ret.input_name = string
    ret.output_name = output_name
    ret.buildable_dependencies = buildable_dependencies
    ret.given_dependencies = given_dependencies
    ret.output_format = output_format
    ret.building_directory = building_directory
    ret.output_directory = output_directory
    return ret
