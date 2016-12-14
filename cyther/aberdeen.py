
"""
A module that defines the different testing procedures to be used by test.py
"""


def test_createPath():
    """
    Tests createPath to make sure it's working correctly
    """

    import os
    from .files import path, exists, get, OverwriteError

    # cwd tacking
    assert path('test.o') != 'test.o'

    # name building
    assert path('test.o') == path(name='test', ext='o')

    # name building using only an extension
    assert path('.tester') == path(ext='tester')

    # another only extension example by using 'name' parameter
    assert path('.tester') == path(name='.tester')

    # injection
    assert path('parent/test.o') == path('test.o', inject='parent')

    test_path = os.path.abspath('test.o')

    # creation of abspath, returning of same directory, unchanged
    assert path(test_path) == test_path

    # relpath is different from abspath
    assert path(test_path, relpath=True) != test_path

    # Fake path
    fake_file_name = 'abcd' * 3 + '.guyfieri'
    fake_path = os.path.abspath(fake_file_name)

    # Overloading overwriting call (tests many things)
    assert path(fake_path, name='is', ext='dumb', inject='cyther',
                overwrite=True) == path(name='is', ext='dumb', inject='cyther')

    # Make sure overwriting doesn't work without 'overwrite=' keyword
    try:
        path(fake_path, name='is', ext='dumb', inject='nick')
        raise AssertionError("This command shouldn't have worked")
    except OverwriteError:
        pass

    another_fake = os.path.abspath("nick/says/cyther/is.dumb")
    fake_root = get(path(another_fake), 'dir')
    faker_root = os.path.dirname(os.path.dirname(fake_root))

    # Another nifty overloading call
    assert path('says/cyther', root=faker_root, name='is.dumb') == another_fake

    # make sure non-existant name doesn't exist
    assert not exists(path(fake_path))

    # Create a fake executable (no extension)
    assert path('test', file_override=True) == os.path.abspath('test')


def test_generateBatches():
    """
    Tests functionality of the generateBatches function
    """

    from .tools import generateBatches

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
