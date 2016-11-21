import argparse

from .tools import getFullPath
from .system import *
from .arguments import parser


class InstructionManager:
    """
    An intelligent container for multiple instructions
    This contains methods for dependency resolution order
    """

    # TODO Is Instruction a better name than FileInfo?
    def parseInstruction(instruction):
        """
        Parses `example.pyx>example.c` into information and stores it in FileInfo
        """
        pass

    def parseInstruction(instructions):
        """
        for each instruction in the list of instructions, parse it
        return a collection of FileInfo objects
        """
        pass


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
        raise CytherError("Args must be a instance of str or argparse.Namespace, not '{}'".format(str(type(args))))

    if args['watch']:
        args['timestamp'] = True

    args['watch_stats'] = {'counter': 0, 'errors': 0, 'compiles': 0, 'polls': 0}
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
            file['include'] = INCLUDE_STRING + ''.join(['-I' + item for item in args['include']])
        else:
            file['include'] = INCLUDE_STRING

        file['file_path'] = getFullPath(filename)
        file['file_base_name'] = os.path.splitext(os.path.basename(file['file_path']))[0]
        file['no_extension'], file['extension'] = os.path.splitext(file['file_path'])
        if file['extension'] not in CYTHONIZABLE_FILE_EXTS:
            raise CytherError("The file '{}' is not a designated cython file".format(file['file_path']))
        base_path = os.path.dirname(file['file_path'])
        local_build = args['local']
        if not local_build:
            cache_name = os.path.join(base_path, '__cythercache__')
            os.makedirs(cache_name, exist_ok=True)
            file['c_name'] = os.path.join(cache_name, file['file_base_name']) + '.c'
        else:
            file['c_name'] = file['no_extension'] + '.c'
        file['object_file_name'] = os.path.splitext(file['c_name'])[0] + '.o'
        output_name = args['output_name']
        if args['watch']:
            file['output_name'] = file['no_extension'] + DEFAULT_OUTPUT_EXTENSION
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
                    raise CytherError('The directory specified to write the output file in does not exist')
        else:
            file['output_name'] = file['no_extension'] + DEFAULT_OUTPUT_EXTENSION

        file['stamp_if_error'] = 0
        to_process.append(file)
    return to_process


class FileInfo:
    def __init__(self, file_type):
        self.file_type = file_type
        """
        include
        c_name
        file_path
        object_file_name
        output_name
        """


"""
Each file gets read and information gets determined

Depencencies are determined

Dependencies are matched and a heirarchy is created

In order from lowest to highest, those commands get created

Put them into cytherize
"""


class CommandManager:
    def __init__(self, commands=None):
        self.__commands = commands

    def toFile(self, filename=None):
        if not filename:
            filename = 'cytherize'
        with open(filename, 'w+') as file:
            chars = file.write(self.__commands.join('\n'))
        return chars

    def fromFile(self, filename=None):
        if not filename:
            filename = 'cytherize'
        with open(filename, 'r') as file:
            lines = file.readlines()
        if self.__commands is not None:
            raise ValueError("The commands '{}' already exist, you cannot"
                             "overwrite them".format(self.__commands))
        self.__commands = eval(lines)

    def sortCommands(self):
        """ Intended to put the -l commands at the end """
        pass

    def getCommands(self):
        self.sortCommands()
        return self.__commands


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


