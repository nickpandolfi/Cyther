
"""
The heart of Cyther
"""

from .system import INFO
from .tools import getResponse

import os
import argparse

"""
Each function must have the parameter 'args', even if they do not use it.
This is because they can be called by the parser, and parser always passes a
'args' variable in.
"""


def polymorph(func):
    def wrapped(*args, **kwargs):
        if kwargs:
            args = argparse.Namespace()
            args.__dict__.update(kwargs)
        return func(args)
    return wrapped


def info(args):
    print(INFO)



"""
CONFIG IS NEVER RUN AUTOMATICALLY, ITS ALWAYS RUN BY USER

get_config_file:
    Checks for the config file inplace
        If its non-existant, it looks in the users home directory

write_config_file:
    Open the config file path passed in and write the data structure to the
    file by first putting it in some sort of format

read_config_file:
    Open the config file passed in and parse the data into
    some sort of structure. Then take this and return it

check_config_info:
    Checks all the fields in the config file to make sure that they are valid
    paths that contain the correct data necessary to compile something

make_config_file:
    Options: --auto, --guided, --manual
    Places for the file: --inplace, --user

    If get_config_file finds a file,

    If the config file is found, then theres a problem

    Print a message to display correct example usage
"""


@polymorph
def configure(args):
    """
    pass
    """
    pass


def setup(args):
    pass


def make(args):
    pass


@polymorph
def build(args):
    pass


@polymorph
def clean(args):
    pass


@polymorph
def purge(args):
    print('Current Directory: {}'.format(os.getcwd()))
    directories = os.listdir(os.getcwd())
    if '__cythercache__' in directories:
        response = getResponse("Would you like to delete the cache and"
                               "everything in it? [y/n]: ", ('y', 'n'))
        if response == 'y':
            print("Listing local '__cythercache__':")
            cache_dir = os.path.join(os.getcwd(), "__cythercache__")
            to_delete = []
            contents = os.listdir(cache_dir)
            if contents:
                for filename in contents:
                    print('\t' + filename)
                    filepath = os.path.join(cache_dir, filename)
                    to_delete.append(filepath)
            else:
                print("\tNothing was found in the cache")

            check_response = getResponse("Delete all these files? (^)"
                                         "[y/n]: ", ('y', 'n'))
            if check_response == 'y':
                for filepath in to_delete:
                    os.remove(filepath)
                os.rmdir(cache_dir)
            else:
                print("Skipping the deletion... all files are fine!")
        else:
            print("Skipping deletion of the cache")
    else:
        print("Couldn't find a cache file ('__cythercache__')"
              "in this directory")
