
"""
This module holds the different functions for testing different aspects of
Cyther. It tets Cyther's main operation as well as the underlying utilities
Cyther uses.
"""

import os
import subprocess

import cyther
from .tools import generateBatches
from .files import createPath


def test_cyther():
    """
    Tests Cyther's entire core operation
    """
    cyther.info(None)
    cyther.core('cyther info')
    subprocess.call(['cyther', 'info'])

    print('<@test.py> All compilation tests have been passed')


def test_utilities():
    """
    A function to test cyther's internal compilation and helper tools
    """
    t = {
        'a': ['b'],
        'b': ['c'],
        'c': ['d', 'e', 'f', 'g'],
        'd': ['e', 'g', 'j'],
        'e': ['f'],
        'f': ['i', 'j'],
        'g': ['j'],
        'h': ['i'],
        'i': ['j'],
        'j': ['q'],
    }
    g = ['q']
    batches = generateBatches(t, g)
    assert batches == [{'j'}, {'i', 'g'}, {'f', 'h'}, {'e'},
                       {'d'}, {'c'}, {'b'}, {'a'}]
    path = 'C:/users/Nick/non-existing-file.pyx'
    assert os.path.normpath(path) == createPath(path)
    return


if __name__ == '__main__':
    test_cyther()
