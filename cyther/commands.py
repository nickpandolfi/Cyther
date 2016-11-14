from .test_cyther import test_cyther
from .system import INFO
from .tools import polymorph
import os

"""
Each function must have the parameter 'args', even if they do not use it. This is because they can be called
by the parser, and parser always passes a 'args' variable in.
"""


@polymorph
def info(args):
    print(INFO)
    exit()


@polymorph
def configure(args):
    print(args)


@polymorph
def test(args):
    test_cyther()


@polymorph
def setup(args):
    pass


@polymorph
def make(args):
    pass


@polymorph
def clean(args):
    pass


@polymorph
def purge(args):
    print('Current Directory: {}'.format(os.getcwd()))
