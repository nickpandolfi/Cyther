import argparse

from .tools import getFullPath
from .definitions import *
from .system import *
from .arguments import parser


def processArgs(args):
    """
    Converts args, and deals with incongruities that argparse couldn't handle
    Args:
        args (unknown): Args to be sorted
    Returns (dict): Filtered and processed arguments
    """
    if isinstance(args, str):
        unprocessed = args.strip().split(' ')
        if unprocessed[0] == 'cytherize' or unprocessed[0] == 'cyther':
            del unprocessed[0]
        args = parser.parse_args(unprocessed).__dict__
    elif isinstance(args, argparse.Namespace):
        args = args.__dict__
    elif isinstance(args, dict):
        pass
    else:
        raise CytherError("Args must be a instance of str or argparse.Namespace, not '{}'".format(str(type(args))))

    if args['X']:
        args['execute'] = True
        args['timestamp'] = True
        args['watch'] = True

    if args['T']:
        args['timer'] = True
        args['timestamp'] = True
        args['watch'] = True

    if args['watch']:
        args['timestamp'] = True

    args['watch_stats'] = {'counter': 0, 'errors': 0, 'compiles': 0, 'polls': 0}
    args['print_args'] = True

    return args


def processFiles(args):
    """
    Generates and error checks each file's information before the compilation actually starts
    Args:
        args (dict): The processed args to base 'file' off of
    Returns files
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


def makeCommands(preset, file):
    """
    Given a high level preset, it will construct the basic args to pass over.
    'ninja', 'beast', 'minimal', 'swift'
    Args:
        preset (str): The high level preset
        file (dict): The file for which to generate these commands for
    Returns (tuple of lists): The commands in which to pass off to the underlying compilers
    """
    if not preset:
        preset = 'ninja'

    if preset == 'ninja':
        cython_command = ['cython', '-a', '-p', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-fPIC', '-shared', '-w', '-O3', file['include'], RUNTIME_STRING, '-o',
                       file['output_name'], file['c_name'], L_OPTION]
    elif preset == 'beast':
        cython_command = ['cython', '-a', '-l', '-p', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-fPIC', '-shared', '-Wall', '-O3', file['include'], RUNTIME_STRING, '-o',
                       file['output_name'], file['c_name'], L_OPTION]
    elif preset == 'minimal':
        cython_command = ['cython', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-fPIC', '-shared', file['include'], RUNTIME_STRING, '-o', file['output_name'],
                       file['c_name'], L_OPTION]
    elif preset == 'swift':
        cython_command = ['cython', '-o', file['c_name'], file['file_path']]
        gcc_command = ['gcc', '-fPIC', '-shared', '-Os', file['include'], RUNTIME_STRING, '-o', file['output_name'],
                       file['c_name'], L_OPTION]
    else:
        raise CytherError("The preset '{}' is not supported".format(preset))
    return cython_command, gcc_command


def convertToDashes(commands):
    """
    Converts Cyther's pass off notation to the regular dash notation (_a becomes -a)
    Args:
        commands (list|tuple): The unprocessed commands
    Returns (list): The processed commands
    """
    processed = []
    for command in commands:
        if command[0] == '_':
            if command[1] == '_':
                command = '--' + command[2:]
            else:
                command = '-' + command[1:]
        processed.append(command)
    return processed


def filterCommands(pass_off_commands, commands):
    """
    Puts items of pass_off_commands in commands if commands does not already have them
    Args:
        pass_off_commands (list|tuple): Commands manually fed to be passed off
        commands (list): The automatically generate commands to be passed off
    Returns (list): The processed commands
    """
    if pass_off_commands:
        for item in pass_off_commands:
            if item[0] == '-':
                if item not in commands:
                    commands.append(item)


def finalizeCommands(args, file):
    """
    Combines a few functions to generate all the commands needed for a specific file
    Args:
        args (dict): The compilation wide arguments
        file (dict): The specific file dict to construct the commands for
    Returns (tuple of lists): The finalized cython and gcc commands
    """
    cython_commands, gcc_commands = makeCommands(args['preset'], file)

    cython_pass_off = convertToDashes(args['cython_args'])
    gcc_pass_off = convertToDashes(args['gcc_args'])

    filterCommands(cython_pass_off, cython_commands)
    filterCommands(gcc_pass_off, gcc_commands)

    return cython_commands, gcc_commands


def getDirsToInclude(string):
    """
    Given a string of module names, it will return the 'include' directories essential to their compilation
    Args:
        string (str): A continuous string of modules split by '-'
    Returns (list): Extra include directories to pass into gcc
    """
    dirs = []
    a = string.strip()
    obj = a.split('-')

    if len(obj) == 1 and obj[0]:
        for module in obj:
            try:
                exec('import {}'.format(module))
            except ImportError:
                raise CytherError("The module '{}' does not exist".format(module))
            try:
                dirs.append('-I {}'.format(eval(module).get_include()))
            except AttributeError:
                print(NOT_NEEDED_MESSAGE.format(module))
    return dirs