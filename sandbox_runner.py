import os, sys, getopt
import json
import logging

from print_error import error
from runner_errors import *
from runner_config import RunnerConfig, UNLIMITED
from runner import run


logging.basicConfig(level=logging.DEBUG)


def version():
    return 'Sandbox Runner v0.0.1'


def usage():
    print("Usage: python3 %s [args] -- [commands]" % sys.argv[0].split('/')[-1])


def main(argv=()):
    logger = logging.getLogger(__name__)
    logger.info(version())
    delimiter = argv.index('--')
    command = argv[delimiter + 1:]
    try:
        opts, args = getopt.getopt(argv[:delimiter],
                                   'hVcfi:o:l:e:v:u:g:s:',
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
                                    'err-file=',
                                    'log-file=',
                                    'file-io',
                                    'env=',
                                    'uid=',
                                    'gid=',
                                    'seccomp-rule='])
    except getopt.GetoptError as err:
        logger.error(str(err))
        sys.exit(2)
    try:
        if len(opts) == 0:
            raise ArgumentError()
        if opts[0][0] in ('-h', '--help'):
            print(version())
            usage()
            sys.exit(0)
        if opts[0][0] in ('-v', '-V', '--version'):
            print(version())
            sys.exit(0)
    except RunnerException as err:
        logger.error(str(err))
        sys.exit(2)
    try:
        config = RunnerConfig.build(opts)
    except ArgumentError as err:
        logger.error(str(err))
        sys.exit(999)
    # print(json.dumps(config.to_dict(), indent=2))
    run(config, command)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
    else:
        main(sys.argv[1:])
