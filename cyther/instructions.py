from .files import FileInfo

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


def check_flow_operator(string):
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
    output_name = None

    check_whitespace(string)

    there_are_dependencies = check_dependencies(string)
    if there_are_dependencies:
        buildable_dependencies, \
            given_dependencies, \
            string = parseDependencies(string)

    there_are_options = check_building_options(string)
    if there_are_options:
        output_directory, \
            output_format, \
            building_directory, string = parseBuildingOptions(string)

    if string[0] == '>':
        string = string[1:]
    if string[-1] == '>':
        string = string[:-1]

    is_a_flow_operator = check_flow_operator(string)
    if is_a_flow_operator:
        greater_than_location = string.index('>')
        output_name = string[greater_than_location + 1:]
        string = string[:greater_than_location]

    ret = {
        'input_name': string,
        'output_name': output_name,
        'buildable_dependencies': buildable_dependencies,
        'given_dependencies': given_dependencies,
        'output_format': output_format,
        'building_directory': building_directory,
        'output_directory': output_directory
    }
    return ret


class Instruction:
    def __init__(self, init=None):
        self.output_name = None
        self.output_name = None
        self.__progression = None
        # Is self.progression and starting point File objects?

        self.build_directory = None

        self.buildable_dependencies = []
        self.given_dependencies = []

        if init and isinstance(init, str):
            parseString(init)

    def processAndSetDefaults(self):
        return

    @staticmethod
    def fileify(string):
        return FileInfo(string)

    def setBuildableDependencies(self, dependencies):
        self.buildable_dependencies = dependencies

    def setGivenDependencies(self, dependencies):
        self.given_dependencies = dependencies

    def setBuildDirectory(self, directory):
        self.build_directory = directory

    def setInput(self, input_name):
        if isinstance(input_name, str):
            self.output_name = self.fileify(input_name)
        else:
            self.output_name = input_name

    def setOutput(self, output_name):
        if isinstance(output_name, str):
            self.output_name = self.fileify(output_name)
        else:
            self.output_name = output_name



class InstructionManager:
    def parseInstruction(self, instruction):
        # This will parse a given string and automatically add an instruction!
        pass

    def parseInstructions(self, instructions):
        for instruction in instructions:
            self.parseInstruction(instruction)
