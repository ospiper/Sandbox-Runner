import sys
import getopt
import logging

from .runner_errors import RunnerException, ArgumentError
from .runner_config import RunnerConfig
from .runner import run


def version():
    return 'Sandbox Runner v0.0.1'


def usage():
    print("Usage: python3 %s [args] -- [commands]" % sys.argv[0].split('/')[-1])


def main(argv=()):
    logger = logging.getLogger(__name__)
    delimiter = argv.index('--')
    command = argv[delimiter + 1:]
    try:
        opts, args = getopt.getopt(argv[:delimiter],
                                   'hdVcfi:o:l:e:v:u:g:s:',
                                   ['help',
                                    'version',
                                    'debug',
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
        if len(opts) > 0:
            if opts[0][0] in ('-h', '--help'):
                print(version())
                usage()
                sys.exit(0)
            if opts[0][0] in ('-v', '-V', '--version'):
                print(version())
                sys.exit(0)
    except RunnerException as err:
        logger.error(str(err))
        sys.exit(6)
    try:
        config = RunnerConfig.build(opts)
    except ArgumentError as err:
        logger.error(str(err))
        sys.exit(999)
    # print(json.dumps(config.to_dict(), indent=2))
    logging.info(version())
    run(config, command)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
    else:
        main(sys.argv[1:])
