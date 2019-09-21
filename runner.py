# from seccomp import *
import os, sys
import time

from print_error import error
from runner_result import *


def run(config, command):
    ret = RunnerResult(SUCCESS)

    # Check root privileges
    # uid = os.getuid()
    uid = 0
    if uid != 0:
        error('Root required')
        ret.result = ROOT_REQUIRED
        return ret

    start = time.time()

    try:
        child = os.fork()
        if child < 0:
            ret.error = FORK_FAILED
            return ret
        elif child == 0:
            print('this is process 0', start)
        else:
            print('this is child process', start)
    except OSError as err:
        error(str(err))
        ret.error = FORK_FAILED
        return ret


