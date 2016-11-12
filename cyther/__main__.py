import sys
from .arguments import parser


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser.parse_args(args)


if __name__ == '__main__':
    main()
