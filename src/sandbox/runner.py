import json
import time
import signal
import logging
from dataclasses import asdict

UNLIMITED = -1
from runner_result import *
from run_child import *
from timer import Timer
from result_code import ErrorCode


def run(config: RunnerConfig = None, command=()):
    logger = logging.getLogger(__name__)
    logger.debug(config.to_dict())
    logger.debug(command)
    ret = RunnerResult()

    ret.output = config.output_file
    # Check root privileges
    uid = 0
    # uid = os.getuid()
    if uid != 0:
        logger.error('Root required')
        ret.result = ErrorCode.ROOT_REQUIRED
    else:
        start = time.time()
        try:
            child = os.fork()
            if child < 0:
                ret.error = ErrorCode.FORK_FAILED
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
                        ret.result = ErrorCode.RESULT_SYSTEM_ERROR
                    else:
                        ret.exit_code = os.WEXITSTATUS(stop_status)
                        ret.cpu_time = resource_usage.ru_utime * 1000
                        ret.memory = resource_usage.ru_maxrss
                        ret.real_time = (end - start) * 1000
                        if ret.exit_code != 0:
                            ret.result = ResultCode.RUNTIME_ERROR
                        if ret.signal == signal.SIGSEGV:
                            if config.max_memory != UNLIMITED and ret.memory > config.max_memory:
                                ret.result = ResultCode.MEMORY_LIMIT_EXCEEDED
                            else:
                                ret.result = ResultCode.RUNTIME_ERROR
                        else:
                            if ret.signal != ErrorCode.SUCCESS:
                                ret.result = ResultCode.RUNTIME_ERROR
                            if config.max_memory != UNLIMITED and ret.memory > config.max_memory:
                                ret.result = ResultCode.MEMORY_LIMIT_EXCEEDED
                            if config.max_real_time != UNLIMITED and ret.real_time > config.max_real_time:
                                ret.result = ResultCode.REAL_TIME_LIMIT_EXCEEDED
                            if config.max_cpu_time != UNLIMITED and ret.cpu_time > config.max_cpu_time - 15:
                                ret.result = ResultCode.CPU_TIME_LIMIT_EXCEEDED
                except OSError as err:
                    logger.error('Wait failed')
                    logger.error(str(err))
                    ret.error = ErrorCode.WAIT_FAILED
        except OSError as err:
            logger.error('Fork failed')
            logger.error(str(err))
            ret.error = ErrorCode.FORK_FAILED
    logger.info(asdict(ret))
    print(json.dumps(asdict(ret)))
    sys.exit(0)


