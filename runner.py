import json
import time
import signal
import logging

from runner_result import *
from run_child import *
from timer import Timer


def run(config, command):
    logger = logging.getLogger(__name__)
    logger.debug(config.to_dict())
    logger.debug(command)
    ret = RunnerResult()

    # Check root privileges
    uid = 0
    # uid = os.getuid()
    if uid != 0:
        logger.error('Root required')
        ret.result = ROOT_REQUIRED
    else:
        start = time.time()
        try:
            child = os.fork()
            if child < 0:
                ret.error = FORK_FAILED
                logger.error('Fork failed')
            elif child == 0:
                run_child(config, command)
            else:
                try:
                    timer = None
                    if config.max_real_time != UNLIMITED:
                        timer = Timer(child, config.max_real_time)
                        timer.start()
                    child_id, stop_status, resource_usage = os.wait4(child, 0)
                    end = time.time()
                    if timer is not None:
                        timer.stop()
                    # Collect usage info
                    if os.WIFSIGNALED(stop_status):
                        ret.signal = os.WTERMSIG(stop_status)
                    if ret.signal == signal.SIGUSR1:
                        ret.result = RESULT_SYSTEM_ERROR
                    else:
                        ret.exit_code = os.WEXITSTATUS(stop_status)
                        ret.cpu_time = resource_usage.ru_utime * 1000
                        ret.memory = resource_usage.ru_maxrss
                        ret.real_time = (end - start) * 1000
                        if ret.exit_code != 0:
                            ret.result = RESULT_RUNTIME_ERROR
                        if ret.signal == signal.SIGSEGV:
                            if config.max_memory != UNLIMITED and ret.memory > config.max_memory:
                                ret.result = RESULT_MEMORY_LIMIT_EXCEEDED
                            else:
                                ret.result = RESULT_RUNTIME_ERROR
                        else:
                            if ret.signal != SUCCESS:
                                ret.result = RESULT_RUNTIME_ERROR
                            if config.max_memory != UNLIMITED and ret.memory > config.max_memory:
                                ret.result = RESULT_MEMORY_LIMIT_EXCEEDED
                            if config.max_real_time != UNLIMITED and ret.real_time > config.max_real_time:
                                ret.result = RESULT_REAL_TIME_LIMIT_EXCEEDED
                            if config.max_cpu_time != UNLIMITED and ret.cpu_time > config.max_cpu_time - 15:
                                ret.result = RESULT_CPU_TIME_LIMIT_EXCEEDED
                except OSError as err:
                    logger.error('Wait failed')
                    logger.error(str(err))
                    ret.error = WAIT_FAILED
        except OSError as err:
            logger.error('Fork failed')
            logger.error(str(err))
            ret.error = FORK_FAILED
    logger.debug(ret.to_dict().__str__())
    print(json.dumps(ret.to_dict()))
    sys.exit(0)


