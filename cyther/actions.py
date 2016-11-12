from .test_cyther import test_cyther
from .system import INFO
import argparse


def polymorphesizeArguments(*args, **kwargs):
    #Theyve been called as the default function by the parser
    if isinstance(args, argparse.Namespace):
        new_args = args

    #Theyve been called as functions
    else:
        new_args = argparse.Namespace()
        for key in kwargs:
            exec("new_args.{} = kwargs[key]".format(key))

    return new_args


def info(args):
    print(INFO)
    exit()


def configure(*args, **kwargs):
    args = polymorphesizeArguments(*args, **kwargs)
    print(args)


def test(args):
    test_cyther()


def setup(args):
    pass


def make(args):
    pass


def clean(args):
    pass


def purge(args):
    pass
