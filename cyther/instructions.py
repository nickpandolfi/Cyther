
"""
This module holds the necessary functions and object definitions to handle and
process basic instructions, whether they originate from an api usage or from
the terminal. This is where both functionalities merge. Serious error checking.
"""

from .files import File

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
INCORRECT_INSTRUCTION_INIT = "Instruction doesn't accept arguments " \
                             "of type '{}', only string or individual " \
                             "parameter setting"
NO_INPUT_FILE = "Must have an input file specified for each instruction"


def get_contents_between(string, opener, closer):
    """
    Get the contents of a string between two characters
    """
    opener_location = string.index(opener)
    closer_location = string.index(closer)
    content = string[opener_location + 1:closer_location]
    return content


###############################################################################


def check_whitespace(string):
    """
    Make sure thre is no whitespace in the given string. Will raise a
    ValueError if whitespace is detected
    """
    if string.count(' ') + string.count('\t') + string.count('\n') > 0:
        raise ValueError(INSTRUCTION_HAS_WHITESPACE)


def check_enclosing_characters(string, opener, closer):
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


def check_parameters(parameters, symbols):
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


###############################################################################


def check_dependencies(string):
    """
    Checks the dependencies constructor. Looks to make sure that the
    dependencies are the first things defined
    """
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
    """
    Checks the building options to make sure that they are defined last,
    after the task name and the dependencies
    """
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
    """
    Checks the flow operator ('>') to mke sure that it:
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


###############################################################################


def parseDependencies(string):
    """
    This function actually parses the dependencies are sorts them into
    the buildable and given dependencies
    """
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
    """
    This will parse and sort the building options defined in the '{}'
    constructor. Will only allow one of each argument
    """
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


# TODO Privatize all of the attributes
class Instruction:
    """
    Holds the necessary information and utilities to process and default check
    the different fields. Provides a merging for the api and terminal
    functionality
    """
    def __init__(self, init=None):
        self.input = None
        # Steps inbetween the input and output need their own individual
        # instructions to be able to elaborate on them!
        self.output = None
        self.buildable_dependencies = []
        self.given_dependencies = []

        # Not critical information, information is obtained from ^ attributes
        # These attribs below are 'overwriters' in a sense
        self.output_format = None
        self.build_directory = None

        if init:
            if isinstance(init, str):
                ret = parseString(init)
                self.input = File(ret['input_name'])
                self.output = File(ret['output_name'])
                self.output_format = ret['output_format']
                self.buildable_dependencies = ret['buildable_dependencies']
                self.given_dependencies = ret['given_dependencies']
                self.building_directory = ret['building_directory']
                self.output_directory = ret['output_directory']
            else:
                raise ValueError(INCORRECT_INSTRUCTION_INIT.format(type(init)))
        else:
            pass  # If init is not specified, the user must use the methods!

    def processAndSetDefaults(self):
        """
        The heart of the Instruction object. This method will make sure that
        all fields not entered will be defaulted to a correct value. Also
        checks for incongruities in the data entered, if it was by the user.
        """
        # INPUT, OUTPUT, GIVEN + BUILDABLE DEPS
        if not self.input:
            raise ValueError(NO_INPUT_FILE)

        if not self.output:
            # Build directory must exist, right?
            if not self.build_directory:
                File()
            pass  # Can it be built? / reference self.output_format for this
        else:
            pass  # if it is not congruent with other info provided

        if not self.build_directory:
            pass  # Initialize it

        for dependency in self.given_dependencies:
            pass  # Check if the dependcy exists

        if self.output_format != self.output.getType():
            raise ValueError("")
        # Given dependencies must actually exist!
        # output_name must be at a lower extenion level than input_name
        # The build directory
        return

    def setBuildableDependencies(self, dependencies):
        self.buildable_dependencies = dependencies

    def setGivenDependencies(self, dependencies):
        self.given_dependencies = dependencies

    def setBuildDirectory(self, directory):
        self.build_directory = directory

    def setInput(self, input_name):
        if isinstance(input_name, str):
            self.input = File(input_name)
        else:
            self.input = input_name

    def setOutput(self, output_name):
        if isinstance(output_name, str):
            self.output = File(output_name)
        else:
            self.output = output_name



class InstructionManager:
    def parseInstruction(self, instruction):
        # This will parse a given string and automatically add an instruction!
        pass

    def parseInstructions(self, instructions):
        for instruction in instructions:
            self.parseInstruction(instruction)
