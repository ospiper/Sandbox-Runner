import sys
from seccomp import *
import errno
import os

from runner_config import RunnerConfig


def load_seccomp_rule(config, command):
    if not isinstance(config, RunnerConfig) or len(command) <= 0:
        return
    if config is not None and config.seccomp_rule is not None:
        rule = config.seccomp_rule
        try:
            f = None
            # print('Loading seccomp rule:', config.seccomp_rule)
            if rule == 'general':
                f = SyscallFilter(defaction=ALLOW)
                forbidden_syscalls = [
                    'clone', 'fork', 'vfork', 'kill'
                ]
                for syscall in forbidden_syscalls:
                    f.add_rule(KILL, syscall)
                f.add_rule(ERRNO(errno.EACCES), 'socket')
                # f.add_rule(KILL, 'read', Arg(0, NE, sys.stdin.fileno()))
                # f.add_rule(KILL, 'write', Arg(0, NE, sys.stdout.fileno()))
                # f.add_rule(KILL, 'write', Arg(0, NE, sys.stderr.fileno()))
                if not config.file_io:
                    f.add_rule(KILL, 'open', Arg(1, MASKED_EQ, os.O_WRONLY, os.O_WRONLY))
                    f.add_rule(KILL, 'open', Arg(1, MASKED_EQ, os.O_RDWR, os.O_RDWR))
                    f.add_rule(KILL, 'openat', Arg(2, MASKED_EQ, os.O_WRONLY, os.O_WRONLY))
                    f.add_rule(KILL, 'openat', Arg(2, MASKED_EQ, os.O_RDWR, os.O_RDWR))
                # f.add_rule(KILL, "execve", Arg(1, NE, id(command)))
            if rule == 'c/c++':
                f = SyscallFilter(defaction=KILL)
                f.add_rule(ALLOW, 'read', Arg(0, EQ, sys.stdin.fileno()))
                f.add_rule(ALLOW, 'write', Arg(0, EQ, sys.stdout.fileno()))
                f.add_rule(ALLOW, 'write', Arg(0, EQ, sys.stderr.fileno()))
                f.add_rule(ALLOW, 'fstat')
                f.add_rule(ALLOW, 'ioctl')
                f.add_rule(ALLOW, 'sigaltstack')
                f.add_rule(ALLOW, 'rt_sigaction')
                f.add_rule(ALLOW, 'exit_group')
                if not config.file_io:
                    f.add_rule(KILL, 'open', Arg(1, MASKED_EQ, os.O_WRONLY | os.O_WRONLY, 0))
                    f.add_rule(KILL, 'open', Arg(1, MASKED_EQ, os.O_RDWR | os.O_RDWR, 0))
                    f.add_rule(KILL, 'openat', Arg(2, MASKED_EQ, os.O_WRONLY | os.O_WRONLY, 0))
                    f.add_rule(KILL, 'openat', Arg(2, MASKED_EQ, os.O_RDWR | os.O_RDWR, 0))
                allowed_syscalls = [
                    'mmap', 'mprotect', 'munmap', 'uname', 'arch_prctl', 'brk', 'access', 'close',
                    'readlink', 'sysinfo', 'writev', 'lseek', 'clock_gettime'
                ]
                for syscall in allowed_syscalls:
                    f.add_rule(ALLOW, syscall)
            if f is not None:
                f.load()
        except OSError as err:
            pass
