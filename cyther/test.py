
"""
This module holds the different functions for testing different aspects of
Cyther. It tets Cyther's main operation as well as the underlying utilities
Cyther uses.
"""

from .aberdeen import test_generateBatches, test_path, test_dict_file


def test_all():
    """
    Tests everything
    """
    test_utilities()
    test_compiler()


def test_compiler():
    """
    Tests Cyther's entire core operation
    """
    import subprocess
    import cyther

    cyther.info(None)
    cyther.core('cyther info')
    subprocess.call(['cyther', 'info'])

    print('<@test.py> All compilation tests have been passed')


def test_utilities():
    """
    A function to test cyther's internal compilation and helper tools
    """

    test_generateBatches()
    test_path()
    test_dict_file()
    return None


if __name__ == '__main__':
    test_all()
