
import cyther
import subprocess


def test_cyther():
    #An info call to display helpful info in log
    cyther.info(None)
    cyther.core('cyther info')
    subprocess.call(['cyther', 'info'])

    #Do a core, command line, and function run
    #subprocess.call(['cyther', 'build', 'example_file.pyx'])

    print('<@test.py> All compilation tests have been passed')


def test_utilities():
    """
    This function is here to test cyther's utilities for operation, and not
    the actual compiling phases. It introduces crazy circumstances into the
    lower level operation of it
    """
    return


if __name__ == '__main__':
    test_cyther()
