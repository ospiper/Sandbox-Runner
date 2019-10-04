import subprocess
import json
from .runner_errors import ArgumentError
from .runner_config import UNLIMITED


def run(command=(),
        max_cpu_time=None,
        max_real_time=None,
        max_memory=None,
        memory_check_only=None,
        max_stack=None,
        max_output_size=None,
        max_process=None,
        input_file=None,
        output_file=None,
        err_file=None,
        log_file=None,
        file_io=None,
        env=None,
        uid=None,
        gid=None,
        seccomp_rule=None):
    if command is None or not isinstance(command, list) or len(command) < 1:
        raise ArgumentError('Command must be a list() and must not be empty')
    args = []
    if max_cpu_time is not None:
        args += ['--max-cpu-time', max_cpu_time]
    if max_real_time is not None:
        args += ['--max-real-time', max_real_time]
    if max_memory is not None:
        args += ['--max-memory', max_memory]
    if memory_check_only is not None and memory_check_only is True:
        args += ['--memory-check-only']
    if max_stack is not None:
        args += ['--max-stack', max_stack]
    if max_output_size is not None:
        args += ['--max-output-size', max_output_size]
    if max_process is not None:
        args += ['--max-process', max_process]
    if input_file is not None:
        args += ['--input-file', input_file]
    if output_file is not None:
        args += ['--output-file', output_file]
    if err_file is not None:
        args += ['--err-file', err_file]
    if log_file is not None:
        args += ['--log-file', log_file]
    if file_io is not None and file_io is True:
        args += ['--file-io']
    if env is not None and isinstance(env, dict):
        for key, value in env.items():
            args += ['--env', '%s=%s' % (str(key), str(value))]
    if uid is not None:
        args += ['--uid', uid]
    if gid is not None:
        args += ['--gid', gid]
    if seccomp_rule is not None:
        args += ['--seccomp-rule', seccomp_rule]
    sandbox_runner_args = ['/usr/bin/python3', 'sandbox_runner.py'] + args + ['--'] + command
    print(sandbox_runner_args)
    process = subprocess.Popen(sandbox_runner_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        raise ValueError(str(err))
    return json.loads(out.decode())