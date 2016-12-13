
"""
A module that defines the different testing procedures to be used by test.py
"""


def test_createPath():
    """
    Tests createPath to make sure it's working correctly
    """

    import os
    from .files import createPath, OverwriteError

    # cwd tacking
    assert createPath('test.o') != 'test.o'

    # name building
    assert createPath('test.o') == createPath(name='test', ext='o')

    # name building using only an extension
    assert createPath('.tester') == createPath(ext='tester')

    # another only extension example by using 'name' parameter
    assert createPath('.tester') == createPath(name='.tester')

    # injection
    assert createPath('parent/test.o') == createPath('test.o', inject='parent')

    test_path = os.path.abspath('test.o')

    # creation of abspath, returning of same directory, unchanged
    assert createPath(test_path) == test_path

    # relpath is different from abspath
    assert createPath(test_path, relpath=True) != test_path

    # Fake path
    fake_file_name = 'abcd' * 3 + '.guyfieri'
    fake_path = os.path.join(os.getcwd(), fake_file_name)

    # Overloading overwriting call (tests many things)
    assert createPath(fake_path, name='is', ext='dumb', inject='cyther',
                      overwrite=True) == createPath(name='is', ext='dumb',
                                                    inject='cyther')

    # Make sure overwriting doesn't work without 'overwrite=' keyword
    try:
        createPath(fake_path, name='is', ext='dumb', inject='nick')
        raise AssertionError("This command shouldn't have worked")
    except OverwriteError:
        pass

    another_fake_dir = os.path.abspath("nick/says/cyther/is.dumb")
    fake_root = createPath(another_fake_dir, return_dir=True)
    faker_root = os.path.dirname(os.path.dirname(fake_root))

    # Another nifty overloading call
    assert createPath('says/cyther', root=faker_root,
                      name='is.dumb') == another_fake_dir

    # make sure non-existant name doesn't exist
    try:
        createPath(fake_path, must_exist=True)
    except FileNotFoundError:
        pass

    # Do the same but without exists_error
    assert not createPath(fake_path, must_exist=True, exists_error=False)

    # Test the 'exists' keyword (works like os.path.exists)
    assert not createPath(fake_path, exists=True)


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
