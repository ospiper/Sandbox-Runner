from dataclasses import dataclass
import json
import os
from typing import List, Optional

from dacite import from_dict

from judger_error import JudgerError
from config import TEST_CASE_DIR


@dataclass
class Case:
    case_id: (str, int)
    input_size: int
    input_name: str
    output_size: int
    output_name: str
    output_md5: str


@dataclass
class SubTask:
    sub_task_id: (str, int)
    type: str
    cases: List[Case]
    score: int = 0


@dataclass
class ProblemInfo:
    type: str
    sub_tasks: List[SubTask]
    problem_id: Optional[str] = None

    def fill_input_path(self):
        if self.problem_id is not None:
            for sub_task in self.sub_tasks:
                for case in sub_task.cases:
                    if case.input_name is not None:
                        case.input_name = os.path.join(TEST_CASE_DIR, self.problem_id, case.input_name)
                    if case.output_name is not None:
                        case.output_name = os.path.join(TEST_CASE_DIR, self.problem_id, case.output_name)
        return self

    @staticmethod
    def load(problem_id: str = None):
        if problem_id is None:
            return None
        ret = ProblemInfo.load_from_file(os.path.join(TEST_CASE_DIR, problem_id, 'tasks.json'))
        if ret.problem_id is None:
            ret.problem_id = problem_id
        return ret.fill_input_path()

    @staticmethod
    def load_from_file(path: str = None):
        if path is None:
            return None
        try:
            json_file = open(path, 'r')
            json_str = json_file.read()
            data = json.loads(json_str)
            json_file.close()
            if data['type'] not in ('io', 'file'):
                raise JudgerError('Unexpected problem type: ' + data['type'])
            return from_dict(data_class=ProblemInfo, data=data)
        except OSError as err:
            raise JudgerError(str(err))
        except ValueError as err:
            raise JudgerError(str(err))
