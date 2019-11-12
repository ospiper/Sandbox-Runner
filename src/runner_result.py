from dataclasses import dataclass
from enum import Enum
from typing import Optional

from result_code import ResultCode, ErrorCode


@dataclass
class RunnerResult:
    cpu_time: (float, int) = None
    real_time: (float, int) = None
    memory: int = None
    signal: int = 0
    exit_code: int = 0
    error: int = ErrorCode.SUCCESS
    result: int = ResultCode.ACCEPTED
    output: Optional[str] = None
    stderr: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.cpu_time, float):
            self.cpu_time = int(self.cpu_time)
        if isinstance(self.real_time, float):
            self.real_time = int(self.real_time)
