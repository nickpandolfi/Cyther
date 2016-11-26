# Cyther: The Cross-Platform Cython/Python/C Auto-Compiler

## Important
Cyther is currently under temporary renovation and this README does not apply just yet. It represents the future `0.8.0` version, offering true cross-platform compatibility and the new and improved intermediate `makefile` system. I am making the README first, then developing the code based around that. Why you ask? Because I have no idea what I'm doing. That's why.

[![Repository](https://badge.fury.io/py/cyther.svg)](https://pypi.python.org/pypi/Cyther)
[![Github](https://img.shields.io/github/stars/nickpandolfi/cyther.svg?style=social&label=Star)](https://github.com/nickpandolfi/Cyther)
[![Downloads](https://img.shields.io/github/downloads/nickpandolfi/Cyther/total.svg)](https://github.com/nickpandolfi/Cyther/releases)

[![Travis](https://secure.travis-ci.org/nickpandolfi/Cyther.png)](https://travis-ci.org/nickpandolfi/Cyther)
![Status](https://img.shields.io/badge/Status-Alpha-orange.svg?style=flat)
[![GPA](https://img.shields.io/codeclimate/github/nickpandolfi/Cyther.svg)](https://codeclimate.com/github/nickpandolfi/Cyther)
[![Issues](https://img.shields.io/codeclimate/issues/github/nickpandolfi/Cyther.svg)](https://codeclimate.com/github/nickpandolfi/Cyther/issues)

![Versions](https://img.shields.io/pypi/pyversions/cyther.svg?maxAge=2592000)
![Implementation](https://img.shields.io/pypi/implementation/cyther.svg?maxAge=2592000)
![License](https://img.shields.io/pypi/l/cyther.svg?maxAge=2592000)
![Format](https://img.shields.io/pypi/format/cyther.svg?maxAge=2592000)

## What is Cyther?

Cyther is a tool used to elegantly compile C and Cython *(and Python for that matter)*. Cyther is what I'd like to call an 'auto-compiler', because it makes the compilation process significantly easier and less cryptic than Python's standard `distutils.build_ext` does. Very similar to GNU's `make` utility, Cyther offers a three step system to compilation:

###1. Configuration
Cyther will guide you through the configuration of your own development environment. It will check to make sure that all of it's dependencies are installed correctly, and are *automatically* accessible.

###2. Initialization
Cyther will construct a single file that holds the commands that it will pass-off to the actual underlying compilers to handle. It is here where you can see what is happening to compile your source code. This can be used as an educational tool.

###3. Compilation
Cyther will then proceed to execute that exact set of commands. This phase also takes several very intelligent arguments to dynamically run and time the code as if the compiled code were 'interpretable'. This process is also extremely fast with very minimal overhead.

## A few reasons why you may want to use Cyther

1. Cyther's method for finding the 'include' and 'runtime' libraries is very sophisticated. Combining regex with a `which` like utility, Cyther will systematically search for the correct directories to use.
2. The commands used to set your project up and then compile your project are completely different, allowing for better bug fixing and quicker environment diagnostics.
3. All the errors ever produced by Cyther are helpful, tell you what to fix, and exactly how to do it.
4. Cyther is windows friendly
5. You do not have to use a full setup.py system to compile one file, or ten, or even a whole project.
6. You will never, *ever*, see the infamous `vcvarsall.bat not found` error. Not only is it cryptic, but it has many different underlying causes, meaning the user is very lucky if they've solved it.
7. Cyther can be used from the Python level, as it has a full API and can be imported.

### What Cyther is NOT

* Cyther is not a replacement for distutils' or setuptools' `build_ext` systems
* Cyther is not meant to be used in a setup.py script for developers to use it to install source files on a user's machine
* Cyther should not be used for important / critical pieces of software, ***yet***

## How to use

Cyther is extremely easy to use. One can call ``cyther`` from the command line, or import `cyther` and
call `cyther.core` from the module level.

    from cyther import core
    core('example_file.pyx')

same can be done with:

    $ cytherize example_file.pyx

And as expected, one can call `$ cyther -h` for all the argument help they need. See below.

### Raw examples (to be better explained later)

`$ cyther build example.pyx`
    Constructs an importable dll (pyd|so) of name `example.pyd` or `example.so`, depending on your machine

`$ cyther build example.pyx>{c}`
    Compiles `example.pyx` into the c file of the same name: `example.c`

`$ cyther build example.pyx>example.c`
    This does the same thing as the previous command, just more clear

`$ cyther build example.pyx>{@output_name}`
    Creates a dll and calls it `output_name.pyd`

`$ cyther build (example.o)big_program.py>{pyd} example.pyx>{o}`
    Compile `example.pyx` into an object file of name `example.o`
    Use this object file and link to big_program.o once you get there
    Then make dll by linking

`$ cyther build (?example.o)big_program.py>{pyd}`
If you were given the example.o file you would use this command

`$ cyther build example.pyx>example.o{^locally}`
`$ cyther build example.pyx>{o}{^locally}`
`$ cyther build example.pyx>{o,^locally}`
    These three commands do exactly the same thing
    The last one makes the most sense

Notes:

Dependent files can be in any position relative to the user:

>The structure of the {} operator:
>    {type,@name,^where,/directory}
>        where: local, cache, obfuscate
>        /directory could use both forward-slashes or backslashes

You can also write something like this to execute tests directly after the build procedure

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

The `@Cyther` line tells Cyther that it should extract the code after it in
the single quoted multi-line string and execute it if the build passed. One
can also tell Cyther to time the `@Cyther` code, returning an IPython-esque
timing message. Here are a few examples of how to use these features.

The wonderful `-x` option, and its output to `stdout`

	$ cytherize example_file.pyx -x
	0123456789

The `-t` option is also super helpful

	$ cytherize example_file.pyx -t
	10000 loops, best of 3: (2.94e-06) sec per loop

## The help text of Cyther

    $ cyther --help

### Assumptions Cyther makes about your system

Cyther, like everything else, isn't perfect. Currently for it to function
properly, it needs to make a few assumptions of your development environment.
All these quirks are listed below. I strongly recommend that you look them
over before using Cyther. In the near future I hope to make Cyther as polished
as possible, and bring the list of assumptions listed below to a minimum.
Future plans can be found in the to-do file I have included with the project.

1. gcc is installed, and accessible from the terminal
2. Your Python version supports `shutil.which`
3. Your environment path variable is able to be found by `shutil.which`
4. `distutils` is able to find the Python runtime static library
(usually `libpythonXY.a` or `libpythonXY.so`)
5. Windows will support gcc compiled C code

### The environment used to develop Cyther

1. Windows 10, 64 bit
2. I use the latest Python 3 version available
3. Linux platforms tested using Travis (cloud based)
4. Ubuntu platforms tested using a local Xubuntu machine
5. GCC version 4.9.3

### Miscellaneous

#### Backstory

Python's standard distutils library is weakly defined when it comes to it's
`build_ext` functionality *(big claim? Look at the code for yourself)*.
On windows specifically, there are many errors that never seem to be addressed
regarding finding and using Microsoft Visual C++ redistributables.
StackOverflow is littered with these kinds of errors, piling duplicate
question on duplicate question. In many instances, as I believe I had
mentioned before, there are many underlying causes to these errors, and the
individual errors tell you absolutely nothing about the problem. Getting to
the bottom of it was what inspired me to write Cyther.

Cyther is my humble attempt* at bridging this gap, and still offering a piece
of software that a beginner to Python can use. I intend for Cyther to be used
by people who simply want to compile a set of files for their own use. Cyther
explicitly avoids distutils' esoteric compilation system.
*(I know, I really live on the edge huh?)*

#### Contact + Reporting Info

If you notice any bugs or peculiarities, please report them to our bug
tracker, it will help us out a lot!

    https://github.com/nickpandolfi/Cyther/issues

If you have any questions or concerns, or even any suggestions,
don't hesitate to email me at:

    npandolfi@wpi.edu

*Happy compiling! - Nick*

###### *Choking hazard. Small parts. Not for children under 3 years of age.*