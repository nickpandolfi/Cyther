
"""
This module holds the necessary functions and object definitions to handle and
process basic instructions, whether they originate from an api usage or from
the terminal. This is where both functionalities merge. Serious error checking.
"""

from .files import File
from .parser import parseString


INCORRECT_INSTRUCTION_INIT = "Instruction doesn't accept arguments " \
                             "of type '{}', only string or individual " \
                             "parameter setting"
NO_INPUT_FILE = "Must have an input file specified for each instruction"


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
                self.input = ret['input_name']
                self.output = ret['output_name']
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
        The heart of the 'Instruction' object. This method will make sure that
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

    def setInput(self, input_name, **kwargs):
        self.input = File(input_name, **kwargs)

    def setOutput(self, output_name, **kwargs):
        self.output = File(output_name, **kwargs)



class InstructionManager:
    def parseInstruction(self, instruction):
        # This will parse a given string and automatically add an instruction!
        pass

    def parseInstructions(self, instructions):
        for instruction in instructions:
            self.parseInstruction(instruction)

    def to_file(self):
        pass

    def from_file(self):
        pass
