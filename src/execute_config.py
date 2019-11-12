import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExecuteConfig:
    root_dir: str
    command: (str, List[str])
    src_name: str
    exe_name: str
    src_path: Optional[str] = None
    exe_path: Optional[str] = None
    max_cpu_time: (str, int) = None
    max_real_time: (str, int) = None
    max_memory: (str, int) = None
    memory_check_only: bool = False
    max_stack: (str, int) = None
    max_output_size: (str, int) = '512m'
    max_process: int = None
    return_output: bool = False
    seccomp_rule: str = None
    env: dict = None

    def __post_init__(self):
        if self.env is None:
            self.env = dict()
        if not self.env.__contains__('PATH'):
            self.env['PATH'] = os.getenv('PATH')
        if self.src_path is None:
            self.src_path=os.path.join(self.root_dir, self.src_name)
        if self.exe_path is None:
            self.exe_path = os.path.join(self.root_dir, self.exe_name)
        if isinstance(self.command, str):
            self.command = self.command.format(src_path=self.src_path,
                                               src_name=self.src_name,
                                               src_dir=self.root_dir,
                                               exe_path=self.exe_path,
                                               exe_name=self.exe_name,
                                               exe_dir=self.root_dir).split(' ')
