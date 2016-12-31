import time

from .launcher import multiCall
from .commands import furtherArgsProcessing, processFiles, makeCommands
from .definitions import WAIT_FOR_FIX, SKIPPED_COMPILATION, INTERVAL, \
    ERROR_PASSOFF, FINE, WATCH_STATS_TEMPLATE, \
    SETUP_TEMPLATE, TIMER_TEMPLATE
from .searcher import extractAtCyther
from .system import *


def cueExtractAndRun(args, file):
    """
    Cues the @cyther code execution procedure
    """
    filename = file['file_path']
    if args['execute']:
        holla = run(filename)
    else:
        holla = run(filename, True)
    return holla


def initiateCompilation(args, file):
    """
    Starts the entire compilation procedure
    """
    ####commands = finalizeCommands(args, file)
    commands = makeCommands(0, file)
    if not args['concise'] and args['print_args']:
        print_commands = bool(args['watch'])
    response = multiCall(*commands, print_commands=print_commands)
    return response


def cytherize(args, file):
    """
    Used by core to integrate all the pieces of information, and to interface
    with the user. Compiles and cleans up.
    """
    if isOutDated(file):
        if isUpdated(file):
            response = initiateCompilation(args, file)
        else:
            response = {'returncode': WAIT_FOR_FIX, 'output': ''}
    else:
        if args['timestamp']:
            response = {'returncode': SKIPPED_COMPILATION, 'output': ''}
        else:
            response = initiateCompilation(args, file)

    ###########################################################################

    time.sleep(INTERVAL)
    if response['returncode'] == ERROR_PASSOFF:
        file['stamp_if_error'] = time.time()
        if args['watch']:
            if len(args['filenames']) > 1:
                output = "Error in file: '{}'; Cyther will wait until it is" \
                         "fixed...\n".format(file['file_path'])
            else:
                output = "Cyther will wait for you to fix this error before" \
                         "it tries to compile again...\n"
        else:
            output = "Error in source file, see above\n"

    elif response['returncode'] == SKIPPED_COMPILATION:
        if not args['watch']:
            output = 'Skipping compilation: source file not updated since' \
                     'last compile\n'
        else:
            output = ''

    elif response['returncode'] == WAIT_FOR_FIX:
        output = ''

    elif response['returncode'] == FINE:
        if args['watch']:
            if len(args['filenames']) > 1:
                output = "Compiled the file '{}'\n".format(file['file_path'])
            else:
                output = 'Compiled the file\n'
        else:
            if not args['concise']:
                output = 'Compilation complete\n'
            else:
                output = ''

    else:
        raise CytherError("Unrecognized return value '{}'"
                          "".format(response['returncode']))

    response['output'] += output

    ###########################################################################

    condition = response['returncode'] == SKIPPED_COMPILATION and not args[
        'watch']
    if (args['execute'] or args['timer']) and response[
        'returncode'] == FINE or condition:
        ret = cueExtractAndRun(args, file)
        response['output'] += ret['output']

    ###########################################################################

    if args['watch']:
        if response['returncode'] == FINE or response[
            'returncode'] == ERROR_PASSOFF:
            if response['returncode'] == FINE:
                args['watch_stats']['compiles'] += 1
            else:
                args['watch_stats']['errors'] += 1
            args['watch_stats']['counter'] += 1
            response['output'] += \
                WATCH_STATS_TEMPLATE.format(args['watch_stats']['counter'],
                                            args['watch_stats']['compiles'],
                                            args['watch_stats']['errors'],
                                            args['watch_stats']['polls'])
        else:
            args['watch_stats']['polls'] += 1

    ###########################################################################

    if args['watch']:
        if response['returncode'] == 1:
            print(response['output'] + '\n')
        else:
            if response['output']:
                print(response['output'])
    else:
        if response['returncode'] == 1:
            if args['error']:
                raise CytherError(response['output'])
            else:
                print(response['output'])
        else:
            print(response['output'])


def run(path, timer=False, repeat=3, number=10000, precision=2):
    """
    Extracts and runs the '@cyther' code from the given file 'path' name
    """
    code = extractAtCyther(path)
    if not code:
        output = "There was no '@cyther' code collected from the " \
                 "file '{}'\n".format(path)
        # TODO This should use a result, right?
        return {'returncode': 0, 'output': output}

    module_directory = os.path.dirname(path)
    module_name = os.path.splitext(os.path.basename(path))[0]
    setup_string = SETUP_TEMPLATE.format(module_directory, module_name, '{}')

    if timer:
        string = TIMER_TEMPLATE.format(setup_string, code, repeat,
                                       number, precision, '{}')
    else:
        string = setup_string + code

    script = os.path.join(os.path.dirname(__file__), 'script.py')
    with open(script, 'w+') as file:
        file.write(string)

    response = call(['python', script])
    return response


def core(args):
    """
    The heart of Cyther, this function controls the main loop, and can be
    used to perform any Cyther action. You can call if using Cyther
    from the module level
    """
    args = furtherArgsProcessing(args)

    numfiles = len(args['filenames'])
    interval = INTERVAL / numfiles
    files = processFiles(args)
    while True:
        for file in files:
            cytherize(args, file)
        if not args['watch']:
            break
        else:
            time.sleep(interval)


if __name__ == '__main__':
    raise CytherError('This module is not meant to be run as a script.'
                      'Try \'cyther make\' for this functionality')
