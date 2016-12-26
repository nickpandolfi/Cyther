
"""
The heart of Cyther
"""

from .system import INFO
from .project import purge_project, clean_project
import argparse

"""
Each function must have the parameter 'args', even if they do not use it.
This is because they can be called by the parser, and parser always passes a
'args' variable in.
"""


def polymorph(func):
    def wrapped(*args, **kwargs):
        if kwargs:
            args = argparse.Namespace()
            args.__dict__.update(kwargs)
        return func(args)
    return wrapped


def info(args):
    print(INFO)


@polymorph
def configure(args):
    """
    pass
    """
    pass


def setup(args):
    pass


def make(args):
    pass


@polymorph
def build(args):
    pass


@polymorph
def clean(args):
    clean_project()


@polymorph
def purge(args):
    purge_project()
