import sys


def error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)