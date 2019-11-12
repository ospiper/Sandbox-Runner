import json
import os
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict

from dacite import from_dict

from execute_config import ExecuteConfig
from problem_info import SubTask, Case
from result_code import ResultCode, ErrorCode
from run_config import RunConfig
from run_utils import *
import sandbox
from runner_result import RunnerResult
from task_result import RunResult, CaseResult, SubTaskResult


@dataclass
class OperationResult:
    # info: dict = field(default_factory=dict)
    info: (RunResult, RunnerResult, dict)
    success: bool


@dataclass
class Operation:
    name: str
    config: ExecuteConfig

    def execute(self) -> OperationResult:
        # print(self.name)
        # print(asdict(self.config))
        if self.name == 'compile':
            ret = run_compile(self)
        elif self.name == 'run':
            ret = run(self)
        else:
            ret = None
        return ret
        # return RunnerResult()


def run_compile(op: Operation = None) -> OperationResult:
    # print(json.dumps(asdict(op), indent=2))
    if op is None:
        return OperationResult(success=False, info={'message': 'Empty operation'})
    config = op.config
    err_file = os.path.join(config.root_dir, 'compile.stderr.log')
    res = sandbox.run(command=config.command,
                      max_cpu_time=config.max_cpu_time,
                      max_real_time=config.max_real_time,
                      max_memory=config.max_memory,
                      memory_check_only=config.memory_check_only,
                      max_stack=config.max_stack,
                      max_output_size=config.max_output_size,
                      max_process=config.max_process,
                      input_file=None,
                      output_file=None,
                      err_file=err_file,
                      log_file='/dev/null',
                      file_io=None,
                      env=config.env,
                      uid=None,
                      gid=None,
                      seccomp_rule=config.seccomp_rule
                      )
    # print(res)
    # print(json.dumps(res, indent=2))
    with open(err_file, 'r') as err_fd:
        res['stderr'] = err_fd.read()
    if res.__contains__('result'):
        success = res['result'] == ResultCode.ACCEPTED
    else:
        success = False
    return OperationResult(success=success, info=from_dict(data_class=RunnerResult,
                                                           data=res))


def run(op: Operation = None) -> OperationResult:
    if op is None:
        return OperationResult(success=False, info={'message': 'Empty operation'})
    config = op.config
    if not isinstance(config, RunConfig):
        return OperationResult(success=False, info={'message': 'Invalid run config'})
    # print(json.dumps(asdict(config), indent=2))
    sub_tasks = config.problem_info.sub_tasks
    score = 0
    cpu_time = 0
    real_time = 0
    memory = None
    result = ResultCode.ACCEPTED
    error = ErrorCode.SUCCESS
    message = None
    sub_task_results = list()
    for sub_task in sub_tasks:
        sub_task_result = run_sub_task(config, sub_task)
        score += sub_task_result.score
        for case in sub_task_result.cases:
            cpu_time += case.cpu_time
            real_time += case.real_time
            if memory is None or case.memory > memory:
                memory = case.memory
            if case.error != ErrorCode.SUCCESS and error == ErrorCode.SUCCESS:
                error = case.error
            if case.result != ResultCode.ACCEPTED and result == ResultCode.ACCEPTED:
                result = case.result
            if case.output is not None and message is None:
                message = case.output
        sub_task_results.append(sub_task_result)
    run_result = RunResult(problem_id=config.problem_info.problem_id,
                           cpu_time=cpu_time,
                           real_time=real_time,
                           memory=memory,
                           result=result,
                           score=score,
                           error=error,
                           sub_tasks=sub_task_results,
                           message=message)
    return OperationResult(success=run_result.result not in (ResultCode.RUNTIME_ERROR,
                                                             ResultCode.SYSTEM_ERROR),
                           info=run_result)


def run_sub_task(config: RunConfig = None, sub_task: SubTask = None) -> SubTaskResult:
    sub_task_type = sub_task.type
    cases = list()
    score = 0
    ac_count = 0
    for case in sub_task.cases:
        case_result = run_case(config, case)
        if case_result.result == ResultCode.ACCEPTED:
            ac_count += 1
        cases.append(case_result)
    if sub_task_type == 'mul':
        if ac_count == len(sub_task.cases):
            score = sub_task.score
    elif sub_task_type == 'sum':
        score = int(sub_task.score * (ac_count / len(sub_task.cases)))
    return SubTaskResult(sub_task_id=sub_task.sub_task_id,
                         type=sub_task_type, score=score, cases=cases)


def run_case(config: RunConfig = None, case: Case = None) -> Optional[CaseResult]:
    if case is None or config is None:
        return None
    # print(case)
    err_file = os.path.join(config.root_dir, 'stderr')
    res = sandbox.run(command=config.command,
                      max_cpu_time=config.max_cpu_time,
                      max_real_time=config.max_real_time,
                      max_memory=config.max_memory,
                      memory_check_only=config.memory_check_only,
                      max_stack=config.max_stack,
                      max_output_size=config.max_output_size,
                      max_process=config.max_process,
                      input_file=case.input_name,
                      output_file=os.path.join(config.root_dir, 'stdout'),
                      err_file=err_file,
                      log_file=os.path.join(config.root_dir, 'log.log'),
                      file_io=False,
                      env=config.env,
                      uid=None,
                      gid=None,
                      seccomp_rule=config.seccomp_rule
                      )
    output_str = None
    res['result'] = ResultCode(res['result'])
    if res['result'] == ResultCode.ACCEPTED:
        if res['output'] is not None:
            with open(res['output'], 'r') as output_fd:
                output_str = output_fd.read()
            # print(md5(handle_output(output_str)))
            # print(case.output_md5)
            if not compare_output(handle_output(output_str), case.output_md5):
                res['result'] = ResultCode.WRONG_ANSWER
    elif res['result'] == ResultCode.RUNTIME_ERROR:
        with open(err_file) as err_fd:
            res['stderr'] = err_fd.read()
    res['output'] = output_str if config.return_output else None
    res['case_id'] = case.case_id
    return from_dict(data_class=CaseResult, data=res)


def run_lint(op: Operation = None) -> OperationResult:
    if op is None:
        return OperationResult(success=False)
    pass
