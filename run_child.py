from libseccomp import *
import os
import sys
import math
import resource
import logging

from runner_config import *
from print_error import error
from seccomp_loader import *


def run_child(config, command):
    logger = logging.getLogger(__name__)
    if not isinstance(config, RunnerConfig):
        logging.error('Invalid runner config')
        return
    if len(command) < 1:
        logging.error('Invalid command')
        return

    # Set resource limits
    try:
        if config.max_stack > 0:
            resource.setrlimit(resource.RLIMIT_STACK, (config.max_stack, config.max_stack))
        if config.max_output_size > 0:
            resource.setrlimit(resource.RLIMIT_FSIZE, (config.max_output_size, config.max_output_size))
        if config.max_process > 0:
            resource.setrlimit(resource.RLIMIT_NPROC, (config.max_process, config.max_process))
        if config.max_memory > 0 and not config.memory_check_only:
            resource.setrlimit(resource.RLIMIT_AS, (config.max_memory, config.max_memory))
        if config.max_cpu_time > 0:
            # Overtime resource limit
            cpu_over_time = int(math.ceil(config.max_cpu_time / 1000))
            # print('CPU Over time:', cpu_over_time)
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_over_time, cpu_over_time))
            # resource.setrlimit(resource.RLIMIT_RTTIME, (cpu_over_time, cpu_over_time))
    except ValueError as valErr:
        logger.error('Failed to parse resource limit')
        logger.error(str(valErr))
    except resource.error as err:
        logger.error('Failed to set resource limit')
        logger.error(str(err))

    # Handle input file
    input_fd = None
    output_fd = None
    err_fd = None
    try:
        if config.input_file is not None:
            input_fd = os.open(config.input_file, os.O_RDONLY)
            os.dup2(input_fd, sys.stdin.fileno())
        if config.output_file is not None:
            output_fd = os.open(config.output_file, os.O_CREAT | os.O_WRONLY)
            os.dup2(output_fd, sys.stdout.fileno())
        if config.err_file is not None:
            err_fd = os.open(config.err_file, os.O_CREAT | os.O_WRONLY)
            os.dup2(err_fd, sys.stderr.fileno())
    except OSError as err:
        logger.error('Failed to dup files')
        logger.error(str(err))

    try:
        if config.gid is not None:
            os.setgid(config.gid)
            os.setgroups((config.gid, ))
        if config.uid is not None:
            os.setuid(config.uid)
    except OSError as err:
        logger.error('Failed to set uid / gid')
        logger.error(err)

    try:
        load_seccomp_rule(config, command)
    except OSError as osErr:
        logger.error('Failed to load seccomp rule')
        logger.error(str(osErr))
    os.execve(command[0], command, config.env)
    logger.error('Execve failed')
