from attr import dataclass


@dataclass
class CompilerConfig:
    root_dir: str = None
    command: str = None
    src_name: str = None
    exe_name: str = None
    max_cpu_time: (str, int) = None
    max_real_time: (str, int) = None
    max_memory: (str, int) = None
    memory_check_only: bool = False
    max_stack: (str, int) = None
    max_output_size: (str, int) = None
    max_process: int = None

    @staticmethod
    def build(args):
        if not isinstance(args, dict):
            raise ValueError('Compiler_config must be a dict()')
        ret = CompilerConfig(command=args['command'],
                             src_name=args['src_name'],
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
        return ret