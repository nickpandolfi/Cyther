import argparse

from .tools import getFullPath
from .system import *
from .arguments import parser
from .definitions import NOT_NEEDED_MESSAGE


def furtherArgsProcessing(args):
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


def makeCommands(preset, file):
    """
    Given a high level preset, it will construct the basic args to pass over.
    'ninja', 'beast', 'minimal', 'swift'
    Args:
        preset (str): The high level preset
        file (dict): The file for which to generate these commands for
    Returns (tuple of lists): The commands in which to pass off to the underlying compilers
    """
    commands = [['cython', '-a', '-p', '-o', file['c_name'], file['file_path']],
                ['gcc', '-fPIC', '-c', file['include'], '-o', file['object_file_name'], file['c_name']],
                ['gcc', '-shared', RUNTIME_STRING, '-o', file['output_name'], file['object_file_name'], L_OPTION]]

    return commands


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