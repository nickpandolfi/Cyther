

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


def get_contents_between(string, opener, closer):
    opener_location = string.index(opener)
    closer_location = string.index(closer)
    content = string[opener_location + 1:closer_location]
    return content


###############################################################################


def check_whitespace(string):
    if string.count(' ') + string.count('\t') + string.count('\n') > 0:
        raise ValueError(INSTRUCTION_HAS_WHITESPACE)


def check_enclosing_characters(string, opener, closer):
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


def check_parameters(parameters, symbols):
    for param in parameters:
        if not param:
            raise ValueError(EMPTY_PARAMETER)
        elif (param[0] in symbols) and (not param[1:]):
            print(param)
            raise ValueError(EMPTY_KEYWORD_PARAMETER)


###############################################################################


def check_dependencies(string):
    opener, closer = '(', ')'
    check_enclosing_characters(string, opener, closer)
    if opener in string:
        if string[0] != opener:
            raise ValueError(DEPENDENCIES_NOT_FIRST)
        ret = True
    else:
        ret = False
    return ret


def check_building_options(string):
    opener, closer = '{', '}'
    check_enclosing_characters(string, opener, closer)
    if opener in string:
        if string[-1] != closer:
            raise ValueError(OPTIONS_NOT_LAST)
        ret = True
    else:
        ret = False
    return ret


###############################################################################


def parseDependencies(string):
    contents = get_contents_between(string, '(', ')')
    unsorted_dependencies = contents.split(',')
    check_parameters(unsorted_dependencies, ('?',))

    buildable_dependencies = []
    given_dependencies = []
    for dependency in unsorted_dependencies:
        if dependency[0] == '?':
            given_dependencies.append(dependency[1:])
        else:
            buildable_dependencies.append(dependency)

    string = string[string.index(')') + 1:]
    return buildable_dependencies, given_dependencies, string


def parseBuildingOptions(string):
    contents = get_contents_between(string, '{', '}')
    unsorted_options = contents.split(',')
    check_parameters(unsorted_options, ('@', '/', '\\', '^'))

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


def parseString(string):
    buildable_dependencies = []
    given_dependencies = []
    output_directory = None
    output_format = None
    building_directory = None

    check_whitespace(string)

    there_are_dependencies = check_dependencies(string)
    if there_are_dependencies:
        buildable_dependencies,\
            given_dependencies,\
            string = parseDependencies(string)

    there_are_options = check_building_options(string)
    if there_are_options:
        output_directory,\
            output_format,\
            building_directory, string = parseBuildingOptions(string)

    ret = {
        'task_name': string,
        'buildable_dependencies': buildable_dependencies,
        'given_dependencies': given_dependencies,
        'output_format': output_format,
        'building_directory': building_directory,
        'output_directory': output_directory
    }
    return ret
