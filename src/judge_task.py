from attr import dataclass


class JudgeTask:
    def __init__(self, task_type=None):
        self.task_type = task_type
        self.sub_tasks = []
    
    def to_dict(self):
        return {
            'task_type': self.task_type, 
            'sub_tasks': [sub_task.to_dict() for sub_task in self.sub_tasks]
        }


class JudgeSubTask:
    def __init__(self, sub_task_id, sub_task_type, score, cases=None):
        self.sub_task_id = sub_task_id
        self.sub_task_type = sub_task_type
        self.score = score
        if cases is not None:
            self.cases = cases
        else:
            self.cases = []

    def to_dict(self):
        return {
            'sub_task_id': self.sub_task_id,
            'sub_task_type': self.sub_task_type,
            'score': self.score,
            'cases': [case.to_dict() for case in self.cases]
        }


@dataclass
class JudgeCase:
    case_id: str = None
    input_size: int = None
    input_name: str = None
    output_size: int = None
    output_name: str = None
    output_md5: str = None

    def to_dict(self):
        return {
            'case_id': self.case_id,
            'input_size': self.input_size,
            'input_name': self.input_name,
            'output_size': self.output_size,
            'output_name': self.output_name,
            'output_md5': self.output_md5
        }