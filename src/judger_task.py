from dataclasses import dataclass
import os
import shutil
from typing import List

from config import JUDGER_WORKSPACE
from judger_error import JudgerError
from operation import Operation
from problem_info import ProblemInfo
from task_result import TaskResult


def create_file_tree(path=None, files=None):
    if not isinstance(files, dict):
        raise JudgerError('Files must be a dict()')
    for p, f in files.items():
        if not isinstance(p, str):
            raise JudgerError('Unexpected path name: ' + str(p))
        if '/' in p or '\\' in p:
            raise JudgerError('Path can only be single-depth relative path')
        if p.startswith('..'):
            raise JudgerError('Path cannot be parent path')
        if isinstance(f, str):
            try:
                with open(os.path.join(path, p), 'w') as fp:
                    fp.write(f)
            except IOError:
                raise JudgerError('Cannot write ' + p)
        elif isinstance(f, dict):
            try:
                real_path = os.path.join(path, p)
                os.makedirs(real_path)
                create_file_tree(real_path, f)
            except OSError:
                raise JudgerError('Cannot create path ' + p)
        else:
            raise JudgerError('Unexpected file entry: ' + str(p))


@dataclass
class Task:
    task_id: str
    problem_id: str
    runner_id: str
    runner_path: str
    files: dict
    operations: List[Operation]
    problem_info: ProblemInfo

    def write_files(self):
        try:
            os.makedirs(self.runner_path)
        except OSError as err:
            raise JudgerError('Cannot create runner dir: ' + str(err))
        create_file_tree(self.runner_path, self.files)

    def run(self):
        ret = TaskResult(task_id=self.task_id, problem_id=self.problem_id, results={})

        for operation in self.operations:
            res = operation.execute()
            if operation.name == 'compile':
                ret.results['compile'] = res
            elif operation.name == 'run':
                ret.results['run'] = res
            elif operation.name == 'lint':
                raise NotImplementedError()
            else:
                raise JudgerError('Unexpected operation: ' + operation.name)
            if not res.success:
                break
        return ret

    def clean_up(self):
        if not self.runner_path.startswith(JUDGER_WORKSPACE):
            return
        if os.path.exists(self.runner_path):
            try:
                shutil.rmtree(self.runner_path)
            except OSError as err:
                raise JudgerError('Cannot remove files: ' + str(err))
