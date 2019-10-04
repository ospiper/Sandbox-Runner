from attr import dataclass

RESULT_ACCEPTED = 0
RESULT_WRONG_ANSWER = -1
RESULT_CPU_TIME_LIMIT_EXCEEDED = 1
RESULT_REAL_TIME_LIMIT_EXCEEDED = 2
RESULT_MEMORY_LIMIT_EXCEEDED = 3
RESULT_RUNTIME_ERROR = 4
RESULT_SYSTEM_ERROR = 5


class JudgeTaskResult:
    task_id = None
    task_type = None
    problem_id = None
    user_id = None
    cpu_time = 0
    real_time = 0
    peak_memory = 0
    result = RESULT_ACCEPTED
    score = 0
    error = None
    message = None
    sub_tasks = None

    def add_sub_task(self, sub_task=None):
        if sub_task is not None and isinstance(sub_task, JudgeSubTaskResult):
            if self.sub_tasks is None:
                self.sub_tasks = []
            self.sub_tasks.append(sub_task)
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'problem_id': self.problem_id,
            'user_id': self.user_id,
            'cpu_time': self.cpu_time,
            'real_time': self.real_time,
            'peak_memory': self.peak_memory,
            'result': self.result,
            'score': self.score,
            'error': self.error,
            'message': self.message,
            'sub_tasks': [sub_task.to_dict() for sub_task in self.sub_tasks]
        }


class JudgeSubTaskResult:
    sub_task_id = None
    sub_task_type = None
    score = 0
    cases = None

    def add_case(self, case=None):
        if case is not None and isinstance(case, JudgeCaseResult):
            if self.cases is None:
                self.cases = []
            self.cases.append(case)
    
    def to_dict(self):
        return {
            'sub_task_id': self.sub_task_id,
            'sub_task_type': self.sub_task_type,
            'score': self.score,
            'cases': [case.to_dict() for case in self.cases]
        }


@dataclass
class JudgeCaseResult:
    case_id: int = None
    cpu_time: int = None
    real_time: int = None
    memory: int = None
    signal: int = None
    exit_code: int = None
    result: int = None
    error: int = None
    output: str = None

    def to_dict(self, output=False):
        ret = {
            'case_id': self.case_id,
            'cpu_time': self.cpu_time,
            'real_time': self.real_time,
            'memory': self.memory,
            'signal': self.signal,
            'exit_code': self.exit_code,
            'result': self.result,
            'error': self.error
        }
        if output:
            ret['output'] = self.output
        return ret
