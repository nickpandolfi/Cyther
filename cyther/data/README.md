# Cyther: The Cross-Platform Cython/Python Compiler

![repo](https://badge.fury.io/py/cyther.svg)
![python](https://img.shields.io/pypi/pyversions/cyther.svg?maxAge=2592000)
![implementation](https://img.shields.io/pypi/implementation/cyther.svg?maxAge=2592000)
![status](https://img.shields.io/pypi/status/cyther.svg?maxAge=2592000)

![license](https://img.shields.io/pypi/l/cyther.svg?maxAge=2592000)
![format](https://img.shields.io/pypi/format/cyther.svg?maxAge=2592000)
![downloads](https://img.shields.io/pypi/dm/cyther.svg?maxAge=2592000)

![travis](https://secure.travis-ci.org/nickpandolfi/Cyther.png)
![codacy](https://api.codacy.com/project/badge/grade/a26189501a8e4086ac0eda51de5fd752)

#### We all know the beauties of Cython:

>1) Writing C extensions is just as easy as Python
>
>2) Almost any valid Python is valid Cython, as Cython is a super-set of Python
>
>3) It has the readability of Python, but the speed of C
>
>4) Minimal effort has to be taken in order to speed up some programs by two to four orders of magnitude

##### However, compiling is not always easy. There are a few places that disutils' `setup.py` can get tripped up.

>1) `vcvarsall.bat not found` error
>
>2) gcc: undefined reference to...
>
>3) Other errors basically referring to `compiler not found`

Cython may be almost as easy to write as Python, but sometimes nowhere near the level of easiness that it
takes to run Python. *This is where Cyther comes into play*. Cyther is an attempt at a cross platform compiler
that wields both the standard Cython compiler and gcc to *make sure that these errors don't happen*.

## How to use:

Cyther is extremely easy to use. One can call ``cytherize`` from the command line, or import `cyther` and
call `cyther.core` from the module level.

    from cyther import core
    core('example_file.pyx')

same can be done with:

    $ cytherize example_file.pyx

And as expected, one can call `$ cytherize -h` for all the argument help they need. See below.

### A few nifty examples:

###### Compile a Python file. This is the simplest usage of Cyther

    core('example_file.py')

###### Compile a Cython file while building the C files in-place (-l), and compiling only if the source file has been updated (-s)

    core('example_file.pyx -s -l')

###### Run an infinite loop, watching the given file(s) for changes, and automatically compile them (-w) when detected

    core('example_file.pyx -w')

###### And don't forget, this can also be done from the terminal!

	$ cytherize example_file.py
	$ cytherize example_file.pyx -s -l
	$ cytherize example_file.pyx -w

###### The command line interface of the `-w` option

    $ cytherize example_file.pyx -w

    cython -a -p -o X:\Cyther\__cythercache__\example_file.c X:\Cyther\example_file.pyx
    gcc -fPIC -shared -w -O3 -ID:\Python35\include -LD:\Python35\libs -o X:\Cyther\example_file.pyd X:\Cyther\__cythercache__\example_file.c -lpython35
    Compiled the file

    ...<iterations:1, compiles:1, errors:0, polls:12>...

    Compiled the file

    ...<iterations:2, compiles:2, errors:0, polls:19>...


    Error compiling Cython file:
    ------------------------------------------------------------
    ...

    def inverse_triangular(n):
        x = (sqrt(8 * n + 1) - 1) / 2
        n = int(x)
        if x - n > 0:
            return Flse
                      ^
    ------------------------------------------------------------

    example_file.pyx:15:19: undeclared name not builtin: Flse
    Cyther will wait for you to fix this error before it tries to compile again...

    ...<iterations:3, compiles:2, errors:1, polls:31>...


    Compiled the file

    ...<iterations:4, compiles:3, errors:1, polls:51>...

###### Compile these two files and pass in the Cython argument `-l` (_l) to the Cython compiler before using `gcc`

    $ cytherize example_file.pyx another_file.py -l -w -cython _l

###### You can also write something like this to execute tests directly after the build procedure

	# example_file.pyx
	from math import sqrt

	cdef int triangular(int n):
	    cdef:
	        double q
	        int r
	    q = (n * (n + 1)) / 2
	    r = int(q)
	    return r

	def inverse_triangular(n):
	    x = (sqrt(8 * n + 1) - 1) / 2
	    n = int(x)
	    if x - n > 0:
	        return False
	    return int(x)

	'''
	@Cyther
	a = ''.join([str(x) for x in range(10)])
	print(a)
	'''

The `@Cyther` line tells Cyther that it should extract the code after it in the single quoted multi-line string and execute it if the build passed. One can also tell Cyther to time the `@Cyther` code, returning an IPython-esque timing message. Here are a few examples of how to use these features.

###### The wonderful `-x` option, and its output to `stdout`

	$ cytherize example_file.pyx -x
	0123456789

###### The `-t` option is also super helpful

	$ cytherize example_file.pyx -t
	10000 loops, best of 3: (2.94e-06) sec per loop

### The help text of `cytherize`:

    $ cytherize -h

    usage: cytherize.py [-h] [-c] [-p PRESET] [-s] [-o OUTPUT_NAME] [-i INCLUDE]
                        [-l] [-w] [-e] [-x | -t] [-X | -T]
                        [-cython CYTHON_ARGS [CYTHON_ARGS ...]]
                        [-gcc GCC_ARGS [GCC_ARGS ...]]
                        filenames [filenames ...]

    Auto compile and build .pyx or .py files in place.

    positional arguments:
      filenames             The Cython source files

    optional arguments:
      -h, --help            show this help message and exit
      -c, --concise         Get cyther to NOT print what it is thinking. Only use
                            if you like to live on the edge
      -p PRESET, --preset PRESET
                            The preset options for using cython and gcc (ninja,
                            beast, minimal, swift)
      -s, --timestamp       If this flag is provided, cyther will not compile
                            files that have a modifiedtime before that of your
                            compiled .pyd or .so files
      -o OUTPUT_NAME, --output_name OUTPUT_NAME
                            Change the name of the output file, default is
                            basename plus .pyd
      -i INCLUDE, --include INCLUDE
                            The names of the python modules that have an include
                            library that needs to be passed to gcc
      -l, --local           When not flagged, builds in __cythercache__, when
                            flagged, it builds locally in the same directory
      -w, --watch           When given, cyther will watch the directory with the
                            't' option implied and compile,when necessary, the
                            files given
      -e, --error           Raise a CytherError exception instead of printing out
                            stderr when -w is not specified
      -x, --execute         Run the @Cyther code in multi-line single quoted
                            strings, and comments
      -t, --timeit          Time the @Cyther code in multi-line single quoted
                            strings, and comments
      -X                    A 'super flag' that implies these flags: '-x', '-s',
                            '-p swift'
      -T                    A 'super flag' that implies these flags: '-t', '-s',
                            '-p swift'
      -cython CYTHON_ARGS [CYTHON_ARGS ...]
                            Arguments to pass to Cython
      -gcc GCC_ARGS [GCC_ARGS ...]
                            Arguments to pass to gcc

    System:
            Python (D:\Python35\python.EXE):
                    Version: 3.5
                    Operating System: Windows-10-10.0.10586-SP0
                            OS is Windows: True
                    Default Output Extension: .pyd
                    Installation Directory: D:\Python35
            Cython (D:\Python35\Scripts\cython.EXE):
                    Nothing Here Yet
            GCC (D:\MinGW\bin\gcc.EXE):
                    Nothing Here Yet

    (Use '_' or '__' instead of '-' or '--' when passing args to gcc or Cython)
    (The '-x' and '-b' Boolean flags are mutually exclusive)

## Assumptions Cyther makes about your system:

Cyther isn't quite perfect yet, so all the incompatibilities and assumptions that Cyther makes are listed
below. We strongly recommend that you look them over before even considering usage. In the
near future I hope to make Cyther as polished as possible, and bring the list of assumptions listed below
to zero.

>1) Cython and gcc are both installed, and accessible from the terminal
>
>2) Your Python version supports `shutil.which`
>
>3) Your environment path variable is able to be found by `shutil.which`
>
>4) 'distutils' is able to find the Python runtime static library (usually `libpythonXY.a` or `libpythonXY.so`)
>
>5) Windows will support gcc compiled C code


Hey you! Yes you. If you notice any bugs or peculiarities, please report them to our bug tracker, it will
help us out a lot!

    https://github.com/nickpandolfi/Cyther/issues

If you have any questions or concerns, or even any suggestions, don't hesitate to email me at:

    npandolfi@wpi.edu

*Happy compiling! - Nick*

