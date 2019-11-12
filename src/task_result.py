from dataclasses import dataclass, field
from typing import List, Optional

from sandbox.result_code import ResultCode, ErrorCode
from sandbox.runner_result import RunnerResult


@dataclass
class CaseResult(RunnerResult):
    case_id: (str, int) = None

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.case_id, int):
            self.case_id = str(self.case_id)


@dataclass
class SubTaskResult:
    sub_task_id: (str, int)
    type: str
    score: int
    cases: List[CaseResult]

    def __post_init__(self):
        if isinstance(self.sub_task_id, int):
            self.sub_task_id = str(self.sub_task_id)


@dataclass
class RunResult:
    problem_id: str
    cpu_time: (float, int)
    real_time: (float, int)
    memory: int
    result: ResultCode
    score: int
    error: ErrorCode = ErrorCode.SUCCESS
    sub_tasks: List[SubTaskResult] = None
    message: Optional[str] = None


@dataclass
class TaskResult:
    task_id: str
    problem_id: str
    results: dict = field(default_factory=dict)
