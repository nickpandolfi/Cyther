
"""
A module that defines the different testing procedures to be used by test.py
"""

import os


def test_find():
    """
    Tests the all-powerful find function from cyther.searcher
    """

    from .searcher import find

    assert find('guy_fieri_headshots.png') == []


def test_extract():
    """
    Tests some extraction procedures to make sure they return the correct
    amounts of values, and nothing when appropriate
    """

    from .searcher import NONE, MULTIPLE, extract,\
        extractAtCyther, extractVersion

    string = \
        """
        test test test

        This is a word
        '''
        @cyther Hello
        '''
        #@Cyther import penguins
        version 3.4.5.100

        Hi
        """

    assert extract('(?P<content>test)', string) == ['test', 'test', 'test']
    assert extract('(?P<content>test)', string, one=True) == MULTIPLE
    a = extract('(?P<content>test)', string, one=True, condense=True)
    assert a == 'test'
    assert extract('(?P<content>flounder)', string, one=True) == NONE
    assert extract('(?P<content>word)', string, one=True) == 'word'
    assert extractVersion(string) == '3.4.5.100'

    string2 = \
        """
        Version 3.4
        """

    assert extractVersion(string2) == '3.4'
    string2 += "\nversion: 3.5\n"
    assert extractVersion(string2) == '?'

    a = extractAtCyther(string)
    assert a == 'import penguins\nHello'


def test_dict_file():
    """
    Tests 'write_dict_to_file' and 'read_dict_from_file' from tools.py
    """

    from .tools import write_dict_to_file, read_dict_from_file

    file_path = os.path.abspath('abcd_test_dbca.txt')
    dictionary = {'key1': 'value1',
                  'key2': ('value2', 'value3'),
                  'key3': 'value4'}
    write_dict_to_file(file_path, dictionary)
    extracted_dict = read_dict_from_file(file_path)
    assert dictionary == extracted_dict
    os.remove(file_path)


def test_path():
    """
    Tests 'path' function in 'files.py' to make sure it's working correctly
    """

    import os
    from .files import ISFILE, ISDIR, path, get_dir, OverwriteError, normalize

    cwd = os.getcwd()
    assert path() == os.getcwd()
    p1 = path(['one', 'two', 'three'])
    p2 = os.path.normpath(os.path.join(cwd, 'one', 'two', 'three'))
    assert p1 == p2

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
    assert path(os.path.join('p', 'test.o')) == path('test.o', inject='p')

    fake_file_name = 'abcd' * 3 + '.guyfieri'
    fake_path = os.path.abspath(fake_file_name)

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
