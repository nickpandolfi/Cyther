
"""
A module that defines the different testing procedures to be used by test.py
"""


def test_path():
    """
    Tests createPath to make sure it's working correctly
    """

    import os
    from .files import ISFILE, ISDIR, path, exists, get_dir, OverwriteError,\
        normalize

    cwd = os.getcwd()
    cwd_and_file = os.path.abspath('test.py')
    assert normalize(cwd) == (os.path.normpath(cwd), ISDIR)
    assert normalize(cwd_and_file) == (os.path.normpath(cwd_and_file), ISFILE)
    user_and_file = os.path.join('~', 'test.py')
    expanded_file = os.path.expanduser(user_and_file)
    assert normalize(user_and_file) == (expanded_file, ISFILE)

    example_path = os.path.abspath('test.o')
    assert path(example_path) == example_path
    assert path(example_path, relpath=True) != example_path

    assert path('test.o') != 'test.o'
    assert path('test.o') == os.path.abspath('test.o')
    assert path('test.o') == path(name='test', ext='o')

    assert path('.tester') == os.path.abspath('.tester')
    assert path('.tester') == path(ext='tester')
    assert path('.tester') == path(ext='.tester')
    assert path('.tester') == path(name='.tester')
    assert path('.tester') != path(name='tester')
    assert path('.config.yaml') == path(name='.config', ext='yaml')
    assert path(os.path.join('parent', 'test.o')) == path('test.o',
                                                          inject='parent')
    #assert path('a.config', ext='yml', overwrite=True)

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
    faker_root = os.path.dirname(os.path.dirname(get_dir(path(another_fake))))
    p1 = path(os.path.join('says', 'cyther'), root=faker_root, name='is.dumb')
    assert p1 == another_fake
    assert not exists(path(fake_path))

    assert path('test', ISFILE) == os.path.abspath('test')
    example_path = os.path.abspath(os.path.join('a.b.c', 'test.o'))
    calculated_path = path('a.b.c', ISDIR, name='test.o')
    assert calculated_path == example_path


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
