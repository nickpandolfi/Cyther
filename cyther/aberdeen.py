
"""
A module that defines the different testing procedures to be used by test.py
"""


def test_path():
    """
    Tests createPath to make sure it's working correctly
    """

    import os
    from .files import path, exists, get, OverwriteError

    assert path('test.o') != 'test.o'
    assert path('test.o') == os.path.abspath('test.o')
    assert path('test.o') == path(name='test', ext='o')

    assert path('.tester') == os.path.abspath('.tester')
    assert path('.tester') == path(ext='tester')
    assert path('.tester') == path(ext='.tester')
    assert path('.tester') == path(name='.tester')
    assert path('.tester') != path(name='tester')

    assert path('parent/test.o') == path('test.o', inject='parent')

    test_path = os.path.abspath('test.o')
    assert path(test_path) == test_path
    assert path(test_path, relpath=True) != test_path

    # Fake path
    fake_file_name = 'abcd' * 3 + '.guyfieri'
    fake_path = os.path.abspath(fake_file_name)

    path1 = path(fake_path, name='is', ext='dumb',
                 inject='cyther', overwrite=True)
    path2 = path(name='is', ext='dumb', inject='cyther')
    assert path1 == path2

    try:
        path(fake_path, name='is', ext='dumb', inject='nick')
        raise AssertionError("This command shouldn't have worked")
    except OverwriteError:
        pass

    another_fake = os.path.abspath(os.path.join("nick", "says",
                                                "cyther", "is.dumb"))
    fake_root = get(path(another_fake), 'dir')
    faker_root = os.path.dirname(os.path.dirname(fake_root))

    assert path(os.path.join('says', 'cyther'),
                root=faker_root, name='is.dumb') == another_fake
    assert not exists(path(fake_path))
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
