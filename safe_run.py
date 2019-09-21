import os, sys, getopt
import json
from print_error import error
from runner_errors import *
from runner_config import RunnerConfig, UNLIMITED
from runner import run


def version():
    print('Sandbox Runner v0.0.1')


def usage():
    print("Usage: python3 save_run.py [args] -- [commands]")


def main(argv=()):
    delimeter = argv.index('--')
    command = argv[delimeter + 1:]
    try:
        opts, args = getopt.getopt(argv[:delimeter],
                                   'hvVcfi:o:l:e:u:g:s:',
                                   ['help',
                                    'version',
                                    'max-cpu-time=',
                                    'max-real-time=',
                                    'max-memory=',
                                    'memory-check-only',
                                    'max-stack=',
                                    'max-output-size=',
                                    'max-process=',
                                    'input-file=',
                                    'output-file=',
                                    'log-file=',
                                    'file-io',
                                    'env=',
                                    'uid=',
                                    'gid=',
                                    'seccomp-rule='])
    except getopt.GetoptError as err:
        error(str(err))
        sys.exit(2)
    try:
        if len(opts) == 0:
            raise ArgumentError()
        if opts[0][0] in ('-h', '--help'):
            version()
            usage()
            sys.exit(0)
        if opts[0][0] in ('-v', '-V', '--version'):
            version()
            sys.exit(0)
    except RunnerException as err:
        error(str(err))
        sys.exit(2)
    try:
        config = RunnerConfig.build(opts)
    except ArgumentError as err:
        error(str(err))
        sys.exit(999)
    print(json.dumps(config.to_dict(), indent=2))
    run(config, command)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
    else:
        main(sys.argv[1:])
