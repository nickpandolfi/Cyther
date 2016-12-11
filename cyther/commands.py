
import argparse

from .system import *
from .arguments import parser


COMMAND_FILENAME = '.cyther'


class SimpleCommand:
    def __init__(self):
        self.runtime_names = []
        self.include_names = []
        self.cython_name = None
        self.python_name = None
        self.c_name = None
        self.o_name = None
        self.dll_name = None

    def getCythonFileName(self):
        return self.cython_name

    def setCythonFileName(self, obj):
        self.cython_name = obj

    def getPythonFileName(self):
        return self.python_name

    def setPythonFileName(self, obj):
        self.python_name = obj

    def getCName(self):
        return self.c_name

    def setCName(self, obj):
        self.c_name = obj

    def getOName(self):
        return self.o_name

    def setOName(self, obj):
        self.o_name = obj

    def getDLLName(self):
        return self.dll_name

    def setDLLName(self, obj):
        self.dll_name = obj

    def getRuntimeNames(self):
        return self.runtime_names

    def setRuntimeNames(self, obj):
        self.runtime_names = obj

    def getIncludeNames(self):
        return self.include_names

    def setIncludeNames(self, obj):
        self.include_names = obj



def furtherArgsProcessing(args):
    """
    Converts args, and deals with incongruities that argparse couldn't handle
    """
    if isinstance(args, str):
        unprocessed = args.strip().split(' ')
        if unprocessed[0] == 'cyther':
            del unprocessed[0]
        args = parser.parse_args(unprocessed).__dict__
    elif isinstance(args, argparse.Namespace):
        args = args.__dict__
    elif isinstance(args, dict):
        pass
    else:
        raise CytherError(
            "Args must be a instance of str or argparse.Namespace, not '{}'".format(
                str(type(args))))

    if args['watch']:
        args['timestamp'] = True

    args['watch_stats'] = {'counter': 0, 'errors': 0, 'compiles': 0,
                           'polls': 0}
    args['print_args'] = True

    return args


def processFiles(args):
    """
    Generates and error checks each file's information before the compilation actually starts
    """
    to_process = []

    for filename in args['filenames']:
        file = dict()

        if args['include']:
            file['include'] = INCLUDE_STRING + ''.join(
                ['-I' + item for item in args['include']])
        else:
            file['include'] = INCLUDE_STRING

        file['file_path'] = getPath(filename)
        file['file_base_name'] = \
        os.path.splitext(os.path.basename(file['file_path']))[0]
        file['no_extension'], file['extension'] = os.path.splitext(
            file['file_path'])
        if file['extension'] not in CYTHONIZABLE_FILE_EXTS:
            raise CytherError(
                "The file '{}' is not a designated cython file".format(
                    file['file_path']))
        base_path = os.path.dirname(file['file_path'])
        local_build = args['local']
        if not local_build:
            cache_name = os.path.join(base_path, '__cythercache__')
            os.makedirs(cache_name, exist_ok=True)
            file['c_name'] = os.path.join(cache_name,
                                          file['file_base_name']) + '.c'
        else:
            file['c_name'] = file['no_extension'] + '.c'
        file['object_file_name'] = os.path.splitext(file['c_name'])[0] + '.o'
        output_name = args['output_name']
        if args['watch']:
            file['output_name'] = file['no_extension']+DEFAULT_OUTPUT_EXTENSION
        elif output_name:
            if os.path.exists(output_name) and os.path.isfile(output_name):
                file['output_name'] = output_name
            else:
                dirname = os.path.dirname(output_name)
                if not dirname:
                    dirname = os.getcwd()
                if os.path.exists(dirname):
                    file['output_name'] = output_name
                else:
                    raise CytherError('The directory specified to write'
                                      'the output file in does not exist')
        else:
            file['output_name'] = file['no_extension']+DEFAULT_OUTPUT_EXTENSION

        file['stamp_if_error'] = 0
        to_process.append(file)
    return to_process


"""
Each file gets read and information gets determined
Depencencies are determined
Dependencies are matched and a heirarchy is created
In order from lowest to highest, those commands get created
Put them into cytherize
"""


class Commands:
    """
    Class to hold the data and methods for processing a manager of instructions
    into commands to execute in order to do what should be accomplished
    """
    def __init__(self):
        self.__unprocessed = []

    def toFile(self, filename=None):
        if not filename:
            filename = COMMAND_FILENAME

        commands = self.generateCommands()
        string = str()
        for command in commands:
            string += (' '.join(command) + '\n')

        # TODO What is the best file permission?
        with open(filename, 'w+') as file:
            chars = file.write(string)

        return chars

    @staticmethod
    def fromFile(filename=None):
        if not filename:
            filename = COMMAND_FILENAME

        with open(filename) as file:
            lines = file.readlines()

        output = []
        for line in lines:
            output.append(line.split())

        return output

    def generateCommands(self):
        """
        Generate a list of lists of commands from the internal manager object
        """
        # 1) Sort the commands
        # 2) Return the commands in the form of a list
        # 3) This does what makeCommands does right now
        pass


def makeCommands(file):
    """
    Given a high level preset, it will construct the basic args to pass over.
    'ninja', 'beast', 'minimal', 'swift'
    """
    commands = [['cython', '-a', '-p', '-o',
                 file['c_name'], file['file_path']],
                ['gcc', '-DNDEBUG', '-g', '-fwrapv', '-O3', '-Wall', '-Wextra',
                 '-pthread', '-fPIC', '-c', file['include'], '-o',
                 file['object_file_name'], file['c_name']],
                ['gcc', '-g', '-Wall', '-Wextra', '-pthread', '-shared',
                 RUNTIME_STRING, '-o', file['output_name'],
                 file['object_file_name'], L_OPTION]]

    return commands
