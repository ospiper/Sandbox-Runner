from attr import dataclass


@dataclass
class RunnerConfig:
    root_dir: str = None
    command: str = None
    exe_name: str = None
    max_cpu_time: (str, int) = None
    max_real_time: (str, int) = None
    max_memory: (str, int) = None
    memory_check_only: bool = False
    max_stack: (str, int) = None
    max_output_size: (str, int) = None
    max_process: int = None
    seccomp_rule: str = None
    env: dict = None
    return_output: bool = False

    @staticmethod
    def build(args):
        if not isinstance(args, dict):
            raise ValueError('Compiler_config must be a dict()')
        ret = RunnerConfig(command=args['command'],
                           exe_name=args['exe_name'],
                           max_cpu_time=args['max_cpu_time'],
                           max_real_time=args['max_real_time'],
                           max_memory=args['max_memory'])
        if args.__contains__('memory_check_only'):
            ret.memory_check_only = args['memory_check_only']
        if args.__contains__('max_stack'):
            ret.max_stack = args['max_stack']
        if args.__contains__('max_output_size'):
            ret.max_output_size = args['max_output_size']
        if args.__contains__('max_process'):
            ret.max_process = args['max_process']
        if args.__contains__('seccomp_rule'):
            ret.seccomp_rule = args['seccomp_rule']
        if args.__contains__('env'):
            ret.env = args['env']
        else:
            ret.env = {}
        if args.__contains__('return_output'):
            ret.return_output = args['return_output']
        return ret
