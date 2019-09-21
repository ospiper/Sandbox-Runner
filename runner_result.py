SUCCESS = 0,
INVALID_CONFIG = -1
FORK_FAILED = -2
PTHREAD_FAILED = -3
WAIT_FAILED = -4
ROOT_REQUIRED = -5
LOAD_SECCOMP_FAILED = -6
SETRLIMIT_FAILED = -7
DUP2_FAILED = -8
SETUID_FAILED = -9
EXECVE_FAILED = -10
SPJ_ERROR = -11

RESULT_WRONG_ANSWER = -1
RESULT_CPU_TIME_LIMIT_EXCEEDED = 1
RESULT_REAL_TIME_LIMIT_EXCEEDED = 2
RESULT_MEMORY_LIMIT_EXCEEDED = 3
RESULT_RUNTIME_ERROR = 4
RESULT_SYSTEM_ERROR = 5


class RunnerResult:
    cpu_time = None
    real_time = None
    memory = None
    signal = None
    exit_code = None
    error = None
    result = None

    def __init__(self, result, cpu_time=None, real_time=None, memory=None, signal=None, exit_code=None, error=None):
        self.result = result
        self.cpu_time = cpu_time
        self.real_time = real_time
        self.memory = memory
        self.signal = signal
        self.exit_code = exit_code
        self.error = error

    def to_dict(self):
        return {
            'cpu_time': self.cpu_time,
            'real_time': self.real_time,
            'memory': self.memory,
            'signal': self.signal,
            'exit_code': self.exit_code,
            'error': self.error,
            'result': self.result
        }