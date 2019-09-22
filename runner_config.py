import os
import logging
from runner_errors import ArgumentError
UNLIMITED = -1


def parse_int(opt, s):
    try:
        return int(s)
    except ValueError as err:
        raise ArgumentError('%s: input "%s" is not a number' % (opt, s))


def parse_time(opt, s):
    """
    Parse a string / int to milliseconds
    Support times: ms, MS, s, S, m, M (minutes)
    :param opt: option name
    :param s: time str/int
    :return: time in ms
    """
    if isinstance(s, int):
        return s
    elif isinstance(s, str):
        if s.isnumeric():
            return parse_int(opt, s)
        elif s.endswith(('ms', 'MS')):  # Milliseconds
            return parse_int(opt, s[:-2])
        elif s.endswith(('s', 'S')):    # Seconds
            return parse_int(opt, s[:-1]) * 1000
        elif s.endswith(('m', 'M')):    # Minutes
            return parse_int(opt, s[:-1]) * 1000 * 60
        else:
            raise ArgumentError('%s: Time unit must be ms|s|m' % opt)

    else:
        raise ArgumentError("%s: Time must be an integer or a string" % opt)


def parse_size(opt, s):
    """
    Parse a string / int to bytes
    Supported sizes: b, B, k, K, m, M, g, G
    :param opt: option name
    :param s: size str/int
    :return: size in bytes
    """
    if isinstance(s, int):
        return s
    elif isinstance(s, str):
        if s.isnumeric():
            return parse_int(opt, s)
        elif s.endswith(('b', 'B')):
            return parse_int(opt, s[:-1])
        elif s.endswith(('k', 'K')):
            return parse_int(opt, s[:-1]) * 1024
        elif s.endswith(('m', 'M')):
            return parse_int(opt, s[:-1]) * 1024 * 1024
        elif s.endswith(('g', 'G')):
            return parse_int(opt, s[:-1]) * 1024 * 1024 * 1024
        else:
            raise ArgumentError('%s: Size unit must be b|k|m|g' % opt)
    else:
        raise ArgumentError("%s: Size must be an integer or a string" % opt)


class RunnerConfig:
    max_cpu_time = UNLIMITED
    max_real_time = UNLIMITED
    max_memory = UNLIMITED
    memory_check_only = False
    max_stack = UNLIMITED
    max_output_size = UNLIMITED
    max_process = UNLIMITED
    input_file = None
    output_file = None
    err_file = None
    log_file = None
    file_io = False
    env = {}
    uid = None
    gid = None
    seccomp_rule = None

    def to_dict(self):
        return {
            'max_cpu_time': self.max_cpu_time,
            'max_real_time': self.max_real_time,
            'max_memory': self.max_memory,
            'memory_check_only': self.memory_check_only,
            'max_stack': self.max_stack,
            'max_output_size': self.max_output_size,
            'max_process': self.max_process,
            'input_file': self.input_file,
            'output_file': self.output_file,
            'err_file': self.err_file,
            'log_file': self.log_file,
            'file_io': self.file_io,
            'env': self.env,
            'uid': self.uid,
            'gid': self.gid,
            'seccomp_rule': self.seccomp_rule
        }

    @staticmethod
    def build(opts=()):
        ret = RunnerConfig()
        log_level = logging.INFO
        for opt, arg in opts:
            if opt in ('--debug', '-d'):
                log_level = logging.DEBUG
            elif opt == '--max-cpu-time':
                ret.max_cpu_time = parse_time(opt, arg)
            elif opt == '--max-real-time':
                ret.max_real_time = parse_time(opt, arg)
            elif opt == '--max-memory':
                ret.max_memory = parse_size(opt, arg)
            elif opt in ('--memory-check-only', '-c'):
                ret.memory_check_only = True
            elif opt == '--max-stack':
                ret.max_stack = parse_size(opt, arg)
            elif opt == '--max-output-size':
                ret.max_output_size = parse_size(opt, arg)
            elif opt == '--max-process':
                ret.max_process = parse_int(opt, arg)
            elif opt in ('--input-file', '-i'):
                ret.input_file = arg
            elif opt in ('--output-file', '-o'):
                ret.output_file = arg
            elif opt in ('--err-file', '-e'):
                ret.err_file = arg
            elif opt in ('--log-file', '-l'):
                ret.log_file = arg
            elif opt in ('--file-io', '-f'):
                ret.file_io = True
            elif opt in ('--env', '-v'):
                env = arg.split('=')
                if len(arg) != 2:
                    raise ArgumentError('Environment variables must be like {Key}={Value}')
                ret.env[env[0]] = env[1]
            elif opt in ('--uid', '-u'):
                ret.uid = parse_int(opt, arg)
            elif opt in ('--gid', '-g'):
                ret.gid = parse_int(opt, arg)
            elif opt in ('--seccomp-rule', '-s'):
                ret.seccomp_rule = arg
            else:
                raise ArgumentError('Unexpected option: %s' % opt)
        if ret.log_file is not None:
            logging.basicConfig(filename=ret.log_file, level=log_level)
        else:
            logging.basicConfig(level=log_level)
        if ret.input_file is not None:
            if not os.path.exists(ret.input_file):
                raise ArgumentError('Input file %s does not exist' % ret.input_file)
        return ret
