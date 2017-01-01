
"""
This module deals with operations regarding individual cyther projects
"""

import os

from .tools import get_input
from .pathway import path, ISDIR
from .definitions import CACHE_NAME


def assure_cache(project_path=None):
    """
    Assure that a project directory has a cache folder.
    If not, it will create it.
    """

    project_path = path(project_path, ISDIR)
    cache_path = os.path.join(project_path, CACHE_NAME)

    if not os.path.isdir(cache_path):
        os.mkdir(cache_path)


def clean_project():
    """
    Clean a project of anything cyther related that is not essential to a build
    """
    pass


def purge_project():
    """
    Purge a directory of anything cyther related
    """
    print('Current Directory: {}'.format(os.getcwd()))
    directories = os.listdir(os.getcwd())
    if CACHE_NAME in directories:
        response = get_input("Would you like to delete the cache and"
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

            check_response = get_input("Delete all these files? (^)"
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
        print("Couldn't find a cache file ('{}') in this "
              "directory".format(CACHE_NAME))
